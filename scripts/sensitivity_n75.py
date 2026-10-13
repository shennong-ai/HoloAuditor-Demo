# -*- coding: utf-8 -*-
"""n=75 sensitivity analysis: exclude the 25 coarse heat-pattern cases, recompute all headline tests."""
import io, sys, math, csv, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WS = r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_workspace"

def two_prop(x1, n1, x2, n2):
    p1, p2 = x1/n1, x2/n2
    pp = (x1+x2)/(n1+n2)
    se = math.sqrt(pp*(1-pp)*(1/n1+1/n2))
    z = (p1-p2)/se
    p = math.erfc(abs(z)/math.sqrt(2))
    return z, p

def binom_test_two_sided(x, n, p0):
    from math import comb
    def pmf(k):
        return comb(n, k) * p0**k * (1-p0)**(n-k)
    px = pmf(x)
    return min(1.0, sum(pmf(k) for k in range(n+1) if pmf(k) <= px + 1e-12))

def sign_test(wins, losses):
    n = wins + losses
    if n == 0:
        return float("nan")
    p = sum(math.comb(n, k) for k in range(0, min(wins, losses)+1)) / (2.0**n) * 2
    return min(p, 1.0)

# --- run 1 per-question ---
r1 = list(csv.DictReader(open(os.path.join(WS, "run1_per_question.csv"), encoding="utf-8-sig")))
# columns: idx,target,gemini_native(|joined),glm_native,gemini_guard_top1,guard_score
def top1(cands_field):
    return cands_field.split("|")[0].strip() if cands_field else ""

r1_rows = []
for r in r1:
    tgt = r["target"].strip()
    g = top1(r.get("gemini_native", ""))
    z = top1(r.get("glm_native", ""))
    gd = r.get("gemini_guard_top1", "").strip()
    r1_rows.append({"idx": int(r["idx"]), "target": tgt, "g_nat": g, "z_nat": z, "g_guard": gd})

# --- run 2 per-question ---
r2 = list(csv.DictReader(open(os.path.join(WS, "v71_trial_per_question.csv"), encoding="utf-8-sig")))
# columns: idx,target,native_top1,guard_top1,native_hit,guard_hit
r2_rows = {}
for r in r2:
    r2_rows[int(r["idx"])] = {"target": r["target"].strip(),
                              "native_hit": r["native_hit"] == "True",
                              "guard_hit": r["guard_hit"] == "True"}

# --- the 25 coarse heat-pattern indices (run 1: target == 热证) ---
heat_idx = {r["idx"] for r in r1_rows if r["target"] == "热证"}
print("heat-pattern cases (excluded):", len(heat_idx))

full = [r["idx"] for r in r1_rows]
eff75 = [i for i in full if i not in heat_idx]
print("effective n =", len(eff75))

def subset_hits(rows, idxs, model_nat):
    return sum(1 for r in rows if r["idx"] in set(idxs) and r[model_nat] and r[model_nat] == r["target"])

# 1. collapse on n=75: run1 gemini native vs run2 native
r1_g_hit75 = sum(1 for r in r1_rows if r["idx"] in eff75 and r["g_nat"] == r["target"])
r2_hit75 = sum(1 for i in eff75 if i in r2_rows and r2_rows[i]["native_hit"])
z, p = two_prop(r2_hit75, 75, r1_g_hit75, 75)
print("\n[collapse @n=75] 3.1 Pro %d/75 vs 2.5 Pro %d/75 | z=%.2f p=%.3e" % (r2_hit75, r1_g_hit75, z, p))

# 2. gemini sign test on n=75 (guarded top1 vs native top1 among non-heat, both present)
w = l = 0
for r in r1_rows:
    if r["idx"] in heat_idx or not r["g_guard"]:
        continue
    nat_ok = r["g_nat"] == r["target"]
    grd_ok = r["g_guard"] == r["target"]
    if grd_ok and not nat_ok: w += 1
    elif nat_ok and not grd_ok: l += 1
print("[gemini sign @n=75] rescued %d vs broken %d | p=%.4g" % (w, l, sign_test(w, l)))

# 3. GLM native on n=75 (guarded per-case unavailable without checkpoint)
z_nat = sum(1 for r in r1_rows if r["idx"] in eff75 and r["z_nat"] == r["target"])
print("[GLM native @n=75] %d/75 = %.1f%%" % (z_nat, 100.0*z_nat/75))

# 4. majority baseline @n=75 = 气虚 share (already known 53/75=70.7%)
q70 = sum(1 for r in r1_rows if r["idx"] in eff75 and r["target"] == "气虚")
print("[majority @n=75] %d/75 = %.1f%%" % (q70, 100.0*q70/75))

# 5. GLM guarded vs majority on n=75: GLM guarded total = 57 known, but per-case guarded not in csv.
#    Try checkpoint from G: (worked for golden earlier)
try:
    ck = json.load(open(r"G:\My Drive\shen2\Ablation_Exam_Results_Patient.json", encoding="utf-8"))
    print("\ncheckpoint READ OK:", len(ck), "records, keys:", list(ck[0].keys()))
    # GLM guarded per-case: GLM_V6.5[0] == 真实证型
    glm_guard75 = sum(1 for k, r in enumerate(ck) if (k+1) in eff75 and r.get("GLM_V6.5") and r["GLM_V6.5"][0] == r.get("真实证型"))
    glm_nat75 = sum(1 for k, r in enumerate(ck) if (k+1) in eff75 and r.get("GLM_LLM") and r["GLM_LLM"][0] == r.get("真实证型"))
    print("[GLM @n=75 from checkpoint] native %d/75, guarded %d/75" % (glm_nat75, glm_guard75))
    z, p = two_prop(glm_guard75, 75, glm_nat75, 75)
    print("[GLM guarded vs native @n=75] z=%.2f p=%.4g" % (z, p))
    z, p = two_prop(glm_guard75, 75, q70, 75)
    print("[GLM guarded vs majority @n=75] z=%.2f p=%.4g" % (z, p))
except Exception as e:
    print("checkpoint unavailable:", repr(e)[:100])

# -*- coding: utf-8 -*-
"""
Run-1 recompute v2 — fixed parser (call+return share one line in run-1 format).
Outputs: native H1/3/5 both models, per-target-class Hit@1 native vs guardrail
(Gemini guardrail top-1 is logged per question), majority baseline, rescue/break.
"""
import io, re, sys, json
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

LOG = r"C:\Users\admin\Documents\ShenNongAIAcademic\NatureMI4\HoloAuditor-demo\data_evidence\02_Ablation_GLM4_vs_Gemini2.5Pro.txt"
text = open(LOG, encoding="utf-8").read()

q_pat = re.compile(r"第\s*(\d+)/100 题\]\s*真实靶点:\s*【(.+?)】")
ret_pat = re.compile(r"(Gemini|GLM-4)\.\.\..*?返回:\s*(\[.*?\])")
cmp_pat = re.compile(r"诊断对比\]\s*Gemini 原生首选:\s*(.+?)\s*\|\s*护栏重排首选:\s*(.+?)\s*\(得分\s*([\d.]+)\)")

rows = []
cur = None
for line in text.splitlines():
    mq = q_pat.search(line)
    if mq:
        if cur: rows.append(cur)
        cur = {"idx": int(mq.group(1)), "target": mq.group(2).strip(), "gemini": [], "glm": [], "cmp": None}
        continue
    if cur is None: continue
    mr = ret_pat.search(line)
    if mr:
        who = "gemini" if mr.group(1) == "Gemini" else "glm"
        try:
            lst = json.loads(mr.group(2).replace("'", '"'))
        except Exception:
            lst = re.findall(r"'(.+?)'", mr.group(2))
        cur[who] = lst
        continue
    mc = cmp_pat.search(line)
    if mc:
        cur["cmp"] = {"native_top1": mc.group(1).strip(), "guard_top1": mc.group(2).strip(), "score": float(mc.group(3))}
if cur: rows.append(cur)

print("PARSED QUESTIONS: %d" % len(rows))
both = [r for r in rows if r["gemini"] and r["glm"]]
print("with both candidate lists: %d" % len(both))

def hits(rs, key, k):
    return sum(1 for r in rs if r["target"] in r[key][:k])

n = len(rows)
for key, label in [("gemini", "Gemini-2.5-Pro"), ("glm", "GLM-4-Flash")]:
    h = {k: hits(rows, key, k) for k in (1, 3, 5)}
    print("%-15s native: H1 %2d (%.0f%%)  H3 %2d (%.0f%%)  H5 %2d (%.0f%%)   [official 33/36/38 or 42/46/53]" % (
        label, h[1], 100.*h[1]/n, h[3], 100.*h[3]/n, h[5], 100.*h[5]/n))

# per-class native Hit@1 vs Gemini guardrail top-1 (logged), and GLM guardrail unknown
print("\nPER-CLASS Hit@1 (native), n by class:")
cls = defaultdict(lambda: {"n": 0, "g_nat": 0, "z_nat": 0, "g_guard": 0, "g_guard_logged": 0})
for r in rows:
    c = cls[r["target"]]
    c["n"] += 1
    if r["gemini"] and r["target"] in r["gemini"][:1]: c["g_nat"] += 1
    if r["glm"] and r["target"] in r["glm"][:1]: c["z_nat"] += 1
    if r["cmp"]:
        c["g_guard_logged"] += 1
        if r["cmp"]["guard_top1"] == r["target"]: c["g_guard"] += 1
print("%-8s %3s %10s %10s %18s" % ("class", "n", "GemNat", "GLMNat", "GemGuard(logged)"))
for name, c in sorted(cls.items(), key=lambda kv: -kv[1]["n"]):
    print("%-8s %3d %6.0f%% %8.0f%% %10.0f%% (of %d)" % (
        name, c["n"], 100.*c["g_nat"]/c["n"], 100.*c["z_nat"]/c["n"], 100.*c["g_guard"]/c["n"], c["g_guard_logged"]))

# macro average over classes with n>=1 (Gemini native)
macro_g = sum(c["g_nat"]/c["n"] for c in cls.values())/len(cls)
macro_z = sum(c["z_nat"]/c["n"] for c in cls.values())/len(cls)
print("\nMACRO Hit@1: Gemini native %.1f%%  GLM native %.1f%%  (classes=%d)" % (100*macro_g, 100*macro_z, len(cls)))

# guardrail effect on Gemini (rescued/broken/tied among logged)
win = tie = loss = 0
for r in rows:
    if not r["cmp"]: continue
    nat_ok = bool(r["gemini"]) and r["target"] in r["gemini"][:1]
    grd_ok = r["cmp"]["guard_top1"] == r["target"]
    if grd_ok and not nat_ok: win += 1
    elif nat_ok and not grd_ok: loss += 1
    elif nat_ok and grd_ok: tie += 1
print("GEMINI guardrail effect: rescued %d, broken %d, both-correct %d (of %d logged)" % (win, loss, tie, win+loss+tie))

# save parsed run-1 per-question table
import csv
with open(r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_workspace\run1_per_question.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["idx", "target", "gemini_native", "glm_native", "gemini_guard_top1", "guard_score"])
    for r in rows:
        w.writerow([r["idx"], r["target"], "|".join(r["gemini"]), "|".join(r["glm"]),
                    (r["cmp"] or {}).get("guard_top1", ""), (r["cmp"] or {}).get("score", "")])
print("WROTE run1_per_question.csv")

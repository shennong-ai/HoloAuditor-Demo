# -*- coding: utf-8 -*-
"""
OneButtonFire-style recompute of Hit@1/3/5 for the V7.1 trial
(gemini-3.1-pro-preview, 100 questions) purely from the captured exam log
01_Gemini_3.1Pro_ZeroShot_Collapse.txt — no hardcoded answers, everything
parsed from the logged per-question candidate list + per-candidate scores.

Log format per question:
    👉 [處理 N/100] 靶點: 【X】
        gemini-3.1-pro-preview 返回 (簡體歸一化): ['a', 'b', ...]
        [詳細評分 Debug]
           a: cooc_raw=..., topo=..., final=...
           b: ...
Guardrail ranking = candidates sorted by final score descending (stable sort,
matching sorted(..., key=...final, reverse=True) in the exam code).
Native ranking = the returned candidate order as-is.
"""
import io, re, sys, json
from collections import OrderedDict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

LOG = r"C:\Users\admin\Documents\ShenNongAIAcademic\NatureMI4\HoloAuditor-demo\data_evidence\01_Gemini_3.1Pro_ZeroShot_Collapse.txt"
text = open(LOG, encoding="utf-8").read()

# --- parse question blocks ---
q_pat = re.compile(r"👉\s*\[處理\s*(\d+)/100\]\s*靶點:\s*【(.+?)】")
ret_pat = re.compile(r"返回\s*\(簡體歸一化\):\s*(\[.*?\])")
score_pat = re.compile(r"^\s+(.+?):\s*cooc_raw=(-?[\d.]+),\s*topo=(-?[\d.]+),\s*final=(-?[\d.]+)\s*$")

questions = []
cur = None
for line in text.splitlines():
    mq = q_pat.search(line)
    if mq:
        if cur: questions.append(cur)
        cur = {"idx": int(mq.group(1)), "target": mq.group(2).strip(),
               "candidates": [], "scores": OrderedDict()}
        continue
    if cur is None: continue
    mr = ret_pat.search(line)
    if mr:
        try:
            cur["candidates"] = json.loads(mr.group(1).replace("'", '"'))
        except Exception:
            cur["candidates"] = re.findall(r"'(.+?)'", mr.group(1))
        continue
    ms = score_pat.match(line)
    if ms:
        cand = ms.group(1).strip()
        cur["scores"][cand] = {"cooc": float(ms.group(2)), "topo": float(ms.group(3)), "final": float(ms.group(4))}

if cur: questions.append(cur)

print("PARSED QUESTIONS: %d" % len(questions))

def norm(s):  # same normalization as log (already simplified there)
    return s.strip().replace("证", "").replace("症", "")

n_hits = {1: 0, 3: 0, 5: 0}
g_hits = {1: 0, 3: 0, 5: 0}
valid = 0
rows = []
for q in questions:
    tgt = norm(q["target"])
    cands = [norm(c) for c in q["candidates"] if c and len(c.strip()) >= 2]
    if not cands: continue
    valid += 1
    # guardrail rerank: sort by final desc (stable, like exam code)
    scored = [(c, q["scores"].get(c, {}).get("final", 0.0)) for c in cands]
    reranked = [c for c, _ in sorted(scored, key=lambda t: t[1], reverse=True)]
    row = {"idx": q["idx"], "target": tgt, "native_top1": cands[0],
           "guard_top1": reranked[0], "native_hit": None, "guard_hit": None}
    for k in (1, 3, 5):
        if tgt in cands[:k]: n_hits[k] += 1
        if tgt in reranked[:k]: g_hits[k] += 1
        if tgt in cands[:1]: row["native_hit"] = True
        if tgt in reranked[:1]: row["guard_hit"] = True
    rows.append(row)

print("VALID QUESTIONS: %d" % valid)
for k in (1, 3, 5):
    print("Hit@%d  native: %.1f%%  guardrail: %.1f%%" % (k, 100.0 * n_hits[k] / valid, 100.0 * g_hits[k] / valid))

# cross-check: native Hit@1 must match the logged stage stat (6.0%) and
# guardrail Hit@1 must match 24.0%
print("CROSS-CHECK vs logged final stage stat (expect native 6.0 / guardrail 24.0):")
print("  computed native Hit@1 = %.1f%%   guardrail Hit@1 = %.1f%%" % (
    100.0 * n_hits[1] / valid, 100.0 * g_hits[1] / valid))

# save per-question table for the paper appendix / audit
import csv
with open(r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_workspace\v71_trial_per_question.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["idx", "target", "native_top1", "guard_top1", "native_hit", "guard_hit"])
    w.writeheader()
    for r in rows: w.writerow(r)
print("WROTE v71_trial_per_question.csv")

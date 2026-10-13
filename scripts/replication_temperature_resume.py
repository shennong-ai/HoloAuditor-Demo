# -*- coding: utf-8 -*-
"""Resume the t=0.3 replication: remaining cases via Google API direct (gemini-3.1-pro-preview)."""
import io, sys, json, time, re, os, urllib.request, urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
KEY = open(os.path.expanduser("~") + r"\.zcode\secrets\gemini_key.txt", encoding="utf-8-sig").read().strip()
CASES = json.load(open(r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_workspace\replication_cases.json", encoding="utf-8"))["cases"]
OUT = r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_workspace\replication_t03_results.json"
LOG = r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_workspace\replication_t03_log.txt"
TOP_K = 15

def call_google(prompt, max_tokens=600):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key=%s" % KEY
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.3}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read().decode())
    cand = d["candidates"][0]
    parts = cand["content"].get("parts", [])
    return "".join(p.get("text", "") for p in parts if p.get("text"))

def parse_candidates(text, top_k):
    cleaned = re.sub(r"[\d\.\*]+", "", text)
    parts = re.split(r"[,，、\s\n]+", cleaned)
    out = []
    for p in parts:
        p = p.strip()
        if len(p) >= 2 and p not in out:
            out.append(p)
    return out[:top_k]

def log(msg):
    line = time.strftime("[%H:%M:%S] ") + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

PROMPT = ("你是一个资深中医研究专家助手，在协助我测试中医。请根据以下患者的综合症状：[{symptoms}]，"
          "推荐最相关的 {k} 个中医证型（如气虚、血瘀、湿热等）。只输出证型名称，用逗号分隔，严禁解释。")

results = json.load(open(OUT, encoding="utf-8"))
# only successfully-scored cases count as done; errored cases must be re-run
scored_idx = {r["idx"] for r in results if "hit1" in r}
remaining = [i for i in range(len(CASES)) if i not in scored_idx]
# drop old error records so the final file is clean
results = [r for r in results if "hit1" in r]
log("RESUME via Google API direct: %d remaining (successfully scored: %d)" % (len(remaining), len(scored_idx)))

for i in remaining:
    case = CASES[i]
    sym = "、".join(case["symptoms"])
    prompt = PROMPT.format(symptoms=sym, k=TOP_K)
    text, err = None, None
    for attempt in range(5):
        try:
            text = call_google(prompt)
            break
        except urllib.error.HTTPError as e:
            err = "HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:150])
            if e.code not in (429, 500, 502, 503, 504):
                break
        except Exception as e:
            err = repr(e)[:150]
        time.sleep(min(90, 10 * (2 ** attempt)))
    if text is None or not text.strip():
        log("case %d FAILED: %s" % (i, err))
        results.append({"idx": i, "target": case["target"], "error": err or "empty", "via": "google"})
    else:
        cands = parse_candidates(text, TOP_K)
        hit = 1 if (cands and cands[0] == case["target"]) else 0
        in3 = 1 if case["target"] in cands[:3] else 0
        results.append({"idx": i, "target": case["target"], "candidates": cands, "hit1": hit, "in3": in3, "via": "google"})
        log("case %d [%s] %s | top1=%s | hit1=%d" % (i, case["target"], "HIT " if hit else "MISS", (cands[0] if cands else "-")[:20], hit))
    json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(3)

scored = [r for r in results if "hit1" in r]
n = len(scored)
h1 = sum(r["hit1"] for r in scored)
google_scored = [r for r in scored if r.get("via") == "google"]
log("GRAND FINAL: n=%d scored (%d via google-direct), %d still errored | FULL Hit@1 = %d/%d = %.1f%%" % (
    n, len(google_scored), len([r for r in results if "error" in r or "hit1" not in r and "error" not in r]),
    h1, n, 100.0 * h1 / n))
g75 = [r for r in google_scored if r["idx"] not in set()]
if google_scored:
    gh = sum(r["hit1"] for r in google_scored)
    log("google-direct subset Hit@1 = %d/%d = %.1f%%" % (gh, len(google_scored), 100.0 * gh / len(google_scored)))
log("ALL DONE")

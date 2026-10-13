# -*- coding: utf-8 -*-
"""
Temperature-matched replication: gemini-3.1-pro-preview @ t=0.3 on the SAME
seed-42 100-case benchmark (Run-1 prompt, Run-1 scoring).
Run-1 reference points: Gemini 2.5 Pro @ t=0.3 = 33.0% Hit@1; 3.1 Pro @ t=0.1 = 6.0%.
"""
import io, sys, json, time, re, os, urllib.request, urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
KEY_PATH = os.path.join(os.path.expanduser("~"), ".zcode", "secrets", "openrouter_key.txt")
CASES = json.load(open(r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_workspace\replication_cases.json", encoding="utf-8"))["cases"]
OUT = r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_workspace\replication_t03_results.json"
LOG = r"C:\Users\admin\.zcode\workspace\default\paper-audit\cline_workspace\replication_t03_log.txt"

def load_key():
    with open(KEY_PATH, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                return line

MODEL = "google/gemini-3.1-pro-preview"
TEMP = 0.3
TOP_K = 15

def call(prompt, max_tokens=400):
    body = {"model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": TEMP}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers={"Authorization": "Bearer " + load_key(),
                                          "Content-Type": "application/json",
                                          "HTTP-Referer": "https://3token.org",
                                          "X-Title": "holoauditor-temp-replication"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"] or ""

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

results = []
if os.path.exists(OUT):
    results = json.load(open(OUT, encoding="utf-8"))
done_idx = {r["idx"] for r in results}
if done_idx:
    log("resuming with %d already done" % len(done_idx))
else:
    log("starting fresh: %d cases" % len(CASES))

for i, case in enumerate(CASES):
    if i in done_idx:
        continue
    sym = "、".join(case["symptoms"])
    prompt = PROMPT.format(symptoms=sym, k=TOP_K)
    text, err = None, None
    for attempt in range(4):
        try:
            text = call(prompt)
            break
        except urllib.error.HTTPError as e:
            err = "HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:150])
            if e.code not in (429, 500, 502, 503, 504):
                break
        except Exception as e:
            err = repr(e)[:150]
        time.sleep(min(60, 8 * (2 ** attempt)))
    if text is None:
        log("case %d FAILED: %s" % (i, err))
        results.append({"idx": i, "target": case["target"], "error": err})
    else:
        cands = parse_candidates(text, TOP_K)
        hit = 1 if (cands and cands[0] == case["target"]) else 0
        in3 = 1 if case["target"] in cands[:3] else 0
        results.append({"idx": i, "target": case["target"], "candidates": cands, "hit1": hit, "in3": in3})
        log("case %d [%s] %s | top1=%s | hit1=%d" % (i, case["target"], "HIT " if hit else "MISS", (cands[0] if cands else "-")[:20], hit))
    json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(2)

scored = [r for r in results if "hit1" in r]
errs = [r for r in results if "error" in r]
if scored:
    n = len(scored)
    h1 = sum(r["hit1"] for r in scored)
    i3 = sum(r["in3"] for r in scored)
    log("FINAL: n=%d scored, %d errored | Hit@1 = %d/%d = %.1f%% | in-Top3 = %.1f%%" % (n, len(errs), h1, n, 100.0*h1/n, 100.0*i3/n))
log("DONE")

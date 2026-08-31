#!/usr/bin/env python3
"""Score the world-legislature sample on the 8-axis DWEB character via the on-box 7B (:8301, temp 0).

Identical contract to parlamint/pm_score.py so scores are directly comparable to the held
ParlaMint + UNGD references. Resumable (key = legislature|i). Low worker count to SELF-QUEUE
politely behind other :8301 jobs.
"""
import os, re, json, threading
from concurrent.futures import ThreadPoolExecutor
import requests

TEACHER = os.environ.get("TEACHER_URL", "http://127.0.0.1:8301/v1/chat/completions")
MODEL = os.environ.get("TEACHER_MODEL", "qwen2.5-7b-atlas")
WORKERS = int(os.environ.get("WORKERS", "3"))
BODYMAX = int(os.environ.get("BODYMAX", "6000"))
BASE = "/mnt/nas/kronaxis/corpora/results/global_legislature_matrix"
INP = os.environ.get("INP", f"{BASE}/sample.jsonl")
OUT = os.environ.get("OUT", f"{BASE}/sample_scored.jsonl")
DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
CHAR_SYS = ("You analyse the VOICE a piece of writing projects, the character of the writing itself, not the "
            "author's personality and not the topic. Score each of eight axes as a DECIMAL between 0.0 and 1.0. "
            'Reply ONLY JSON: {"axes":{"rigour":0.5,"depth":0.5,"originality":0.5,"candour":0.5,"affect":0.5,'
            '"commercial_drive":0.5,"stance":0.5,"register":0.5}}')
CHAR_VOCAB = ("rigour: 0 unsourced -> 1 scholarly | depth: 0 superficial -> 1 expert | originality: 0 rehashed -> 1 "
              "primary source | candour: 0 opaque -> 1 transparent | affect: 0 neutral -> 1 sensational | "
              "commercial_drive: 0 reference -> 1 hard sell | stance: 0 balanced -> 1 polemical | register: 0 "
              "institutional -> 1 conversational")


def score(body):
    msgs = [{"role": "system", "content": CHAR_SYS},
            {"role": "user", "content": f"{CHAR_VOCAB}\n\nTEXT:\n{body[:BODYMAX]}"}]
    r = requests.post(TEACHER, json={"model": MODEL, "messages": msgs, "temperature": 0.0,
                                     "max_tokens": 220, "stream": False}, timeout=180)
    out = (r.json().get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
    m = re.search(r"\{[\s\S]*\}", out)
    ax = (json.loads(m.group(0)).get("axes") if m else None)
    return {k: float(ax[k]) for k in DWEB} if ax and all(k in ax for k in DWEB) else None


done = set()
if os.path.exists(OUT):
    for l in open(OUT):
        try:
            done.add(json.loads(l)["_k"])
        except Exception:
            pass
rows = [json.loads(l) for l in open(INP)]
jobs = [r for r in rows if f"{r['legislature']}|{r['i']}" not in done]
print(f"{len(rows)} rows, {len(jobs)} to score, {len(done)} already done", flush=True)
_wl = threading.Lock()
n = [0]


def do(r):
    ch = score(r["text"])
    if not ch:
        return
    rec = {k: r[k] for k in ("i", "legislature", "country", "lang", "n_chars")}
    rec["char"] = ch
    rec["_k"] = f"{r['legislature']}|{r['i']}"
    with _wl:
        open(OUT, "a").write(json.dumps(rec, ensure_ascii=False) + "\n")
        n[0] += 1
        if n[0] % 50 == 0:
            print(f"scored {n[0]}/{len(jobs)}", flush=True)


with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    list(ex.map(do, jobs))
print(f"DONE scored {n[0]} new", flush=True)

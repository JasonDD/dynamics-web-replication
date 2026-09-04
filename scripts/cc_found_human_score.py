#!/usr/bin/env python3
"""cc_found_human_score.py — score the 8-axis DWEB character of an input table for the FOUND-HUMAN triangulation.

Reads a JSONL of {id, text, outcome, kind} (from cc_found_human_prep.py) and writes a resumable JSONL of
{id, outcome, kind, char:{8 axes}} using the SAME free 7B, SAME system prompt, SAME vocab line and SAME
parse as the cross-site work (truthometer/scripts/cc_within_source_curated.py::score), so every scale matches.

Env: INPUT (jsonl in), OUT (jsonl out), WORKERS(12), BODYMAX(6000), TEACHER_URL, TEACHER_MODEL.
"""
import os, re, json, threading
from concurrent.futures import ThreadPoolExecutor
import requests

TEACHER = os.environ.get("TEACHER_URL", "an internal model endpoint")
MODEL = os.environ.get("TEACHER_MODEL", "an internal 7B instruct model")
WORKERS = int(os.environ.get("WORKERS", "12"))
BODYMAX = int(os.environ.get("BODYMAX", "6000"))
INPUT = os.environ["INPUT"]
OUT = os.environ["OUT"]

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
                                     "max_tokens": 220, "stream": False}, timeout=150)
    out = (r.json().get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
    m = re.search(r"\{[\s\S]*\}", out)
    ax = (json.loads(m.group(0)).get("axes") if m else None)
    return {k: float(ax[k]) for k in DWEB} if ax and all(k in ax for k in DWEB) else None

_wl = threading.Lock()
def emit(rec):
    with _wl:
        with open(OUT, "a") as f:
            f.write(json.dumps(rec) + "\n")

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "a").close()
    done = set()
    for l in open(OUT):
        try:
            done.add(json.loads(l)["id"])
        except Exception:
            pass
    jobs = []
    for l in open(INPUT):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r["id"] in done:
            continue
        jobs.append(r)
    print(f"to score: {len(jobs)} (already done {len(done)})", flush=True)
    n = [0]
    def work(r):
        try:
            ch = score(r["text"])
        except Exception:
            ch = None
        if ch:
            emit({"id": r["id"], "outcome": r["outcome"], "kind": r["kind"], "char": ch})
        n[0] += 1
        if n[0] % 200 == 0:
            print(f"  scored {n[0]}/{len(jobs)}", flush=True)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, jobs))
    print(f"done: {n[0]} attempted", flush=True)

if __name__ == "__main__":
    main()

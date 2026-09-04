#!/usr/bin/env python3
"""score_modality.py — score the 8-axis DWEB character of the modality/register corpora.

Identical instrument to the whole series: free 7B on , same system prompt, same vocab line, same
parse as truthometer/scripts/cc_found_human_score.py. Passes the input record through and adds `char`.
Resumable by id. Self-queues behind the running jobs via a modest worker count (polite on the shared GPU).

Scores every the internal corpus store/<name>/<name>.jsonl for the modality corpora into <name>_scored.jsonl.
Env: WORKERS(3), BODYMAX(6000), TEACHER_URL, TEACHER_MODEL, ONLY(comma names).
"""
import os, re, json, threading
from concurrent.futures import ThreadPoolExecutor
import requests

TEACHER = os.environ.get("TEACHER_URL", "an internal model endpoint")
MODEL = os.environ.get("TEACHER_MODEL", "an internal 7B instruct model")
WORKERS = int(os.environ.get("WORKERS", "3"))
BODYMAX = int(os.environ.get("BODYMAX", "6000"))
BASE = "the internal corpus store"

CORPORA = ["ted_talks_spoken", "scotus_oral_spoken", "podcast_spoken",
           "movie_dialogs_creative", "poetry_creative", "fiction_openings_creative",
           "arxiv_abstracts_technical", "pubmed_abstracts_technical", "contracts_cuad_technical",
           "patent_abstracts_technical", "job_postings_transactional",
           "product_descriptions_transactional", "complaints_transactional"]

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


def score_corpus(name):
    inp = os.path.join(BASE, name, f"{name}.jsonl")
    out = os.path.join(BASE, name, f"{name}_scored.jsonl")
    if not (os.path.exists(inp) and os.path.getsize(inp) > 0):
        print(f"SKIP {name}: no input", flush=True); return
    open(out, "a").close()
    done = set()
    for l in open(out):
        try:
            done.add(json.loads(l)["id"])
        except Exception:
            pass
    jobs = []
    for l in open(inp):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("id") in done:
            continue
        jobs.append(r)
    print(f"[{name}] to score: {len(jobs)} (done {len(done)})", flush=True)
    wl = threading.Lock()
    n = [0]

    def emit(rec):
        with wl:
            with open(out, "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def work(r):
        try:
            ch = score(r.get("text", ""))
        except Exception:
            ch = None
        if ch:
            rec = dict(r); rec["char"] = ch
            emit(rec)
        n[0] += 1
        if n[0] % 100 == 0:
            print(f"  [{name}] {n[0]}/{len(jobs)}", flush=True)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, jobs))
    print(f"[{name}] done: {n[0]} attempted, {sum(1 for _ in open(out))} scored total", flush=True)


if __name__ == "__main__":
    only = os.environ.get("ONLY", "").split(",") if os.environ.get("ONLY") else None
    for c in CORPORA:
        if only and c not in only:
            continue
        score_corpus(c)
    print("SCORE ALL DONE", flush=True)

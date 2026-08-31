#!/usr/bin/env python3
"""fetch_ted.py — TED prepared-monologue transcripts. opus_tedtalks stores text inside a translation dict
(the English side), so pull that; group consecutive segments per talk into a scorable passage."""
import os, json
BASE = "/mnt/nas/kronaxis/corpora"
n = "ted_talks_spoken"
d = os.path.join(BASE, n); os.makedirs(d, exist_ok=True)
p = os.path.join(d, f"{n}.jsonl")

def already(pp):
    try:
        return sum(1 for _ in open(pp)) if os.path.exists(pp) and os.path.getsize(pp) > 0 else 0
    except Exception:
        return 0

if already(p):
    print(f"STATUS|{n}|HELD|{already(p)}|{p}|exists"); raise SystemExit

from datasets import load_dataset

def pull_en(row):
    for k in ("translation", "en", "text", "transcript"):
        v = row.get(k)
        if isinstance(v, dict):
            for lk in ("en", "eng", "en-US"):
                if lk in v and isinstance(v[lk], str):
                    return v[lk]
        elif isinstance(v, str) and len(v) > 20:
            return v
    return None

recs = []
last = "unknown"
tried = [("Helsinki-NLP/opus_tedtalks", None, "train"),
         ("davidstap/ted_talks", None, "train")]
for repo, cfg, split in tried:
    try:
        ds = load_dataset(repo, cfg, split=split, streaming=True) if cfg else load_dataset(repo, split=split, streaming=True)
        buf = []
        for i, row in enumerate(ds):
            if i >= 40000:
                break
            s = pull_en(dict(row))
            if s:
                buf.append(s.strip())
            # every ~12 segments = one scorable spoken passage (~a talk section)
            if len(buf) >= 12:
                passage = " ".join(buf)
                if len(passage) >= 200:
                    recs.append({"id": f"{n}-{len(recs)}", "text": passage[:6000], "src": repo})
                buf = []
            if len(recs) >= 600:
                break
        if recs:
            with open(p, "w") as f:
                for r in recs:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"STATUS|{n}|FETCHED|{len(recs)}|{p}|{repo} EN segments grouped into passages")
            raise SystemExit
    except SystemExit:
        raise
    except Exception as e:
        last = f"{type(e).__name__}: {str(e)[:100]}"
print(f"STATUS|{n}|FAIL|0|{p}|{last}")

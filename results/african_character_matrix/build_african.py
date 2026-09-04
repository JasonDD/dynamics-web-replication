#!/usr/bin/env python3
"""build_african.py -- assemble score inputs for the AFRICAN LANGUAGES CHARACTER MATRIX.

Two panels, each an input JSONL of {id, text, outcome, kind} for cc_found_human_score.py:
  PANEL A (primary, genre = NEWS):  masakhanews, 16 languages, cap 600/lang.
     eng+fra are the European-language-news control (same MasakhaNEWS protocol);
     eng also stands as the scorer's high-resource ceiling reference.
  PANEL B (robustness, genre = SOCIAL/sentiment):  afrisenti tweets, 15 languages, cap 400/lang.

kind = ISO 639-3 config code (amh, hau, swa, ...). outcome unused here (set to genre tag).
"""
import os, json, random, collections
random.seed(1729)

OUT = "the internal corpus store/african_charmatrix"
os.makedirs(OUT, exist_ok=True)

MNEWS = "the internal corpus store/masakhanews/masakhanews.jsonl"
AFRIS = "the internal corpus store/afrisenti/afrisenti.jsonl"

def nwords(t): return len((t or "").split())

def build(src, textkey, cap, minwords, tag, outname):
    buckets = collections.defaultdict(list)
    for l in open(src, encoding="utf-8", errors="replace"):
        try: r = json.loads(l)
        except Exception: continue
        lang = r.get("_config")
        t = (r.get(textkey) or "").strip()
        if not lang or nwords(t) < minwords: continue
        buckets[lang].append(t)
    rows = []
    for lang in sorted(buckets):
        texts = buckets[lang]; random.shuffle(texts)
        k = min(cap, len(texts))
        for i, t in enumerate(texts[:k]):
            rows.append({"id": f"{tag}_{lang}_{i}", "text": t, "outcome": tag, "kind": lang})
        print(f"  {tag} {lang}: {k}/{len(texts)}", flush=True)
    random.shuffle(rows)
    p = os.path.join(OUT, outname)
    with open(p, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"WROTE {len(rows)} rows -> {p}\n", flush=True)

print("PANEL A masakhanews (news, cap 600, minwords 20):")
build(MNEWS, "text", 600, 20, "news", "score_input_news.jsonl")
print("PANEL B afrisenti (tweets, cap 400, minwords 3):")
build(AFRIS, "tweet", 400, 3, "tweet", "score_input_tweet.jsonl")

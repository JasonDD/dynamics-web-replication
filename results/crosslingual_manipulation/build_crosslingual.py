#!/usr/bin/env python3
"""build_crosslingual.py -- assemble the score input for the cross-lingual manipulation test.

Manipulation set: IRA (Internet Research Agency) troll tweets, bucketed by the dataset's own
`language` field. The same influence operation ran in many languages, so it is the cleanest
cross-lingual manipulation source we have.

Sincere baselines that still need scoring here:
  - Persian troll baseline: persian_daily_news (sincere Persian news).
Sincere baselines that are ALREADY scored and are folded in at analysis time (not rebuilt):
  - Europarl (de/fr/es/it/en) from europarl_multiway/scored.jsonl (professional parliamentary text).
  - English trolls from ira_troll/work/scored.jsonl.

Output row: {id, text, outcome, kind}
  outcome = "troll" | "sincere"      (role)
  kind    = ISO-ish language tag      (de,it,fr,es,ru,fa)
"""
import os, csv, json, random, collections

csv.field_size_limit(10**7)
random.seed(1729)
OUT = "the internal corpus store/crosslingual_manip"
os.makedirs(OUT, exist_ok=True)
INP = os.path.join(OUT, "score_input.jsonl")

IRA_CSVS = ["the internal corpus store/ira_troll/IRAhandle_tweets_1.csv",
            "the internal corpus store/ira_troll/IRAhandle_tweets_2.csv"]
PERSIAN = "the internal corpus store/persian_daily_news/persian_daily_news.jsonl"

# IRA language-field name -> our tag, with a per-language cap
LANGMAP = {"German": "de", "Italian": "it", "French": "fr", "Spanish": "es",
           "Russian": "ru", "Farsi (Persian)": "fa"}
CAP = {"de": 800, "it": 800, "fr": 900, "es": 900, "ru": 800, "fa": 400}
PERSIAN_CAP = 800

def nwords(t):
    return len((t or "").split())

# ---- collect IRA troll content per language ----
buckets = collections.defaultdict(list)
seen = collections.defaultdict(set)
for path in IRA_CSVS:
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            lang = LANGMAP.get(r.get("language", ""))
            if not lang:
                continue
            t = (r.get("content") or "").strip()
            if nwords(t) < 3:
                continue
            key = t[:120]
            if key in seen[lang]:
                continue
            seen[lang].add(key)
            buckets[lang].append(t)

rows = []
for lang, texts in buckets.items():
    random.shuffle(texts)
    k = min(CAP[lang], len(texts))
    for i, t in enumerate(texts[:k]):
        rows.append({"id": f"troll_{lang}_{i}", "text": t, "outcome": "troll", "kind": lang})
    print(f"IRA troll {lang}: {k}/{len(texts)} available", flush=True)

# ---- Persian sincere baseline (news) ----
pers = []
for l in open(PERSIAN, encoding="utf-8", errors="replace"):
    try:
        t = (json.loads(l).get("text") or "").strip()
    except Exception:
        continue
    if nwords(t) >= 3:
        pers.append(t)
random.shuffle(pers)
for i, t in enumerate(pers[:PERSIAN_CAP]):
    rows.append({"id": f"sincere_fa_{i}", "text": t, "outcome": "sincere", "kind": "fa"})
print(f"Persian sincere: {min(PERSIAN_CAP, len(pers))}/{len(pers)} available", flush=True)

random.shuffle(rows)
with open(INP, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"WROTE {len(rows)} rows -> {INP}", flush=True)

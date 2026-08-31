#!/usr/bin/env python3
"""prep_deception.py — build one {id,text,outcome,kind} JSONL for the manner-inflation
deception test, spanning matched honest/deceptive pairs in three genres that still need
scoring (phishing email, dark-pattern microcopy, LIAR political claims).

IRA (troll vs CMV sincere) is already scored elsewhere and is folded in at analysis time,
not here.

outcome is the honesty label per genre: a *_DECEPT value = deceptive, a *_HONEST value =
honest control. kind is the genre. Balanced, capped per class to keep the :8301 pass small.
"""
import os, csv, json, random, sys

random.seed(1729)
OUT = "/mnt/nas/kronaxis/corpora/manner_inflation/input.jsonl"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
CAP = {"phish": 700, "liar": 550, "dark": 100000}  # dark: take all (single clean source, cheap)

rows = []

def add(kind, outcome, text, i):
    text = (text or "").strip()
    if len(text.split()) < 2:      # drop empty / single-token junk
        return
    rows.append({"id": f"{kind}_{i}", "text": text, "outcome": outcome, "kind": kind})

# ---- PHISHING: Kaggle phishing-email set, "Email Text" + "Email Type" gold ----
phish, safe = [], []
for l in open("/mnt/nas/kronaxis/corpora/phishing_email/phishing_email.jsonl"):
    try:
        r = json.loads(l)
    except Exception:
        continue
    t = (r.get("Email Text") or "").strip()
    if not t or t.lower() == "empty":
        continue
    (phish if r.get("Email Type") == "Phishing Email" else safe).append(t)
random.shuffle(phish); random.shuffle(safe)
k = min(CAP["phish"], len(phish), len(safe))
for i, t in enumerate(phish[:k]):
    add("phish", "phish", t, f"d{i}")
for i, t in enumerate(safe[:k]):
    add("phish", "safe", t, f"h{i}")
print(f"phish: {k}/class (pool phish={len(phish)} safe={len(safe)})", flush=True)

# ---- DARK PATTERNS: RachitD set, target 1=dark microcopy 0=neutral UI/product copy ----
dk_d, dk_h = [], []
for fn in ("train.csv", "test.csv", "validation.csv"):
    p = f"/mnt/nas/kronaxis/corpora/dark_patterns/{fn}"
    if not os.path.exists(p):
        continue
    with open(p, newline="") as f:
        rd = csv.DictReader(f)
        for r in rd:
            t = (r.get("text") or "").strip()
            lab = str(r.get("target") or r.get("label") or "").strip()
            if not t:
                continue
            (dk_d if lab == "1" else dk_h).append(t)
# de-dup within class
dk_d = list(dict.fromkeys(dk_d)); dk_h = list(dict.fromkeys(dk_h))
for i, t in enumerate(dk_d):
    add("dark", "dark", t, f"d{i}")
for i, t in enumerate(dk_h):
    add("dark", "normal", t, f"h{i}")
print(f"dark: dark={len(dk_d)} normal={len(dk_h)}", flush=True)

# ---- LIAR: PolitiFact claims, deceptive = false/pants-fire, honest = true ----
li_d, li_h = [], []
for l in open("/mnt/nas/kronaxis/corpora/liar/train.tsv"):
    p = l.rstrip("\n").split("\t")
    if len(p) < 3:
        continue
    lab, stmt = p[1], p[2]
    if lab in ("false", "pants-fire"):
        li_d.append(stmt)
    elif lab == "true":
        li_h.append(stmt)
random.shuffle(li_d); random.shuffle(li_h)
k = min(CAP["liar"], len(li_d), len(li_h))
for i, t in enumerate(li_d[:k]):
    add("liar", "false", t, f"d{i}")
for i, t in enumerate(li_h[:k]):
    add("liar", "true", t, f"h{i}")
print(f"liar: {k}/class (pool false+pf={len(li_d)} true={len(li_h)})", flush=True)

# ---- MATHUR 2019 dark patterns WITH surface-form labels (per-category signature test) ----
# outcome = Pattern Category; a sidecar carries Type + Deceptive? + word count for the
# signature-by-surface-form analysis. Empty (visual/structural) strings are dropped.
META = "/mnt/nas/kronaxis/corpora/manner_inflation/mathur_meta.jsonl"
mcsv = "/mnt/nas/kronaxis/corpora/dark_patterns/mathur_dark_patterns.csv"
nm = 0
with open(mcsv, newline="") as f, open(META, "w") as mf:
    for i, r in enumerate(csv.DictReader(f)):
        s = (r.get("Pattern String") or "").strip()
        if len(s.split()) < 2:
            continue
        rid = f"darkm_{i}"
        cat = r.get("Pattern Category", "?")
        rows.append({"id": rid, "text": s, "outcome": cat, "kind": "darkm"})
        mf.write(json.dumps({"id": rid, "category": cat, "type": r.get("Pattern Type", "?"),
                             "deceptive": r.get("Deceptive?", "?"), "nwords": len(s.split()),
                             "text": s}) + "\n")
        nm += 1
print(f"mathur: {nm} labelled dark-pattern strings (sidecar {META})", flush=True)

random.shuffle(rows)
with open(OUT, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(f"WROTE {len(rows)} rows -> {OUT}", flush=True)

#!/usr/bin/env python3
"""Build a length-controlled, balanced sample of world legislature speeches for 8-axis scoring.

One record per speech: {legislature, country, lang, text, n_chars}. Metadata (heritage/region/
age) is joined in the analyser from LEG_META so this file stays a thin sampler.

Sampling rule (identical across every legislature, for a fair matter/manner comparison):
  - keep only speeches with CHAR_MIN <= len(text) <= CHAR_MAX  (length band control)
  - deterministic shuffle (seed) then take N_PER
Argentina is EXCLUDED: its corpus file is session metadata only (no speech text).
"""
import os, re, json, random, zipfile, csv, io, sys

random.seed(1729)
ROOT = "/mnt/nas/kronaxis/corpora"
OUT = "/mnt/nas/kronaxis/corpora/results/global_legislature_matrix/sample.jsonl"
CHAR_MIN = 400
CHAR_MAX = 6000
N_PER = 55

def clean(t):
    t = re.sub(r"\s+", " ", (t or "")).strip()
    return t

def banded(rows):
    """rows: list of (country, text). filter by length band, dedup, sample N_PER."""
    seen = set(); out = []
    for c, t in rows:
        t = clean(t)
        if not (CHAR_MIN <= len(t) <= CHAR_MAX):
            continue
        h = t[:80]
        if h in seen:
            continue
        seen.add(h)
        out.append((c, t))
    random.shuffle(out)
    return out[:N_PER]

def jsonl_iter(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except Exception:
                    pass

records = []  # (legislature, country, lang, text)

# ---- natparl (English-official African + Malaysia; Korean = Korea) ----
NATPARL = {
    "ghana":        ("Ghana_Parliament",   "Ghana",        "en"),
    "kenya":        ("Kenya_Parliament",   "Kenya",        "en"),
    "nigeria":      ("Nigeria_NASS",       "Nigeria",      "en"),
    "south_africa": ("SouthAfrica_NA",     "South Africa", "en"),
    "zambia":       ("Zambia_NA",          "Zambia",       "en"),
    "zimbabwe":     ("Zimbabwe_Parliament","Zimbabwe",     "en"),
    "malaysia":     ("Malaysia_DewanRakyat","Malaysia",    "en"),
    "korea":        ("Korea_NationalAssembly","South Korea","ko"),
}
for fn, (leg, country, lang) in NATPARL.items():
    p = f"{ROOT}/natparl/{fn}.jsonl"
    if not os.path.exists(p):
        print("MISS", p); continue
    rows = [(country, r.get("text", "")) for r in jsonl_iter(p)]
    for c, t in banded(rows):
        records.append((leg, country, lang, t))

# ---- japan_diet (JA, 'speech') ----
p = f"{ROOT}/japan_diet/japan_diet.jsonl"
rows = [("Japan", r.get("speech", "")) for r in jsonl_iter(p)]
for c, t in banded(rows):
    records.append(("Japan_Diet", "Japan", "ja", t))

# ---- pan_african_parliament (EN/FR mixed; giant hansard docs -> segment into paragraphs) ----
p = f"{ROOT}/pan_african_parliament/pap_hansard.jsonl"
segs = []
for r in jsonl_iter(p):
    txt = r.get("text", "")
    # docs are single ~1.5M-char strings separated by single newlines; split on newline,
    # then pack consecutive lines into ~1500-char windows so each scored unit is a real turn-sized chunk
    txt = clean(txt)
    buf = ""
    for sent in re.split(r"(?<=[.!?])\s+", txt):
        sent = sent.strip()
        if not sent:
            continue
        buf = (buf + " " + sent).strip()
        if len(buf) >= 1400:
            seg = clean(buf); buf = ""
            if CHAR_MIN <= len(seg) <= CHAR_MAX:
                segs.append(("Pan-Africa", seg))
random.shuffle(segs)
for c, t in banded(segs):
    records.append(("Pan_African_Parliament", "Pan-Africa", "en", t))

# ---- us_congress (hein-daily speeches_114.txt: 'speech_id|speech', EN) ----
zp = f"{ROOT}/us_congress/hein-daily.zip"
try:
    with zipfile.ZipFile(zp) as z:
        with z.open("hein-daily/speeches_114.txt") as fh:
            reader = io.TextIOWrapper(fh, encoding="latin-1", errors="ignore")
            us_rows = []
            first = True
            for line in reader:
                if first:
                    first = False
                    continue
                parts = line.split("|", 1)
                if len(parts) == 2:
                    us_rows.append(("United States", parts[1]))
                if len(us_rows) > 200000:
                    break
    for c, t in banded(us_rows):
        records.append(("US_Congress", "United States", "en", t))
except Exception as e:
    print("US ERR", e, file=sys.stderr)

# ---- SCOTUS (supreme convokit utterances; EN; JUDICIAL) ----
p = f"{ROOT}/supreme/supreme-corpus/utterances.jsonl"
scotus_rows = [("United States", r.get("text", "")) for r in jsonl_iter(p)]
for c, t in banded(scotus_rows):
    records.append(("SCOTUS", "United States", "en", t))

# ---- india_loksabha: EXCLUDED. Held xlsx are debate INDEXES only (title/metadata rows);
#      'contents'/'debateDesc' columns are null and Rajya Sabha carries only titles + PDF links.
#      No usable full-text speech in the snapshot. Flagged in RESULT.md alongside Argentina.
print("SKIP India_LokSabha: held corpus is metadata/index only (no speech text)")

# ---- brazil_chamber (discursos_sample.json -> dados[].transcricao, PT) ----
try:
    d = json.load(open(f"{ROOT}/brazil_chamber/discursos_sample.json", encoding="utf-8"))
    br_rows = []
    for page in d:
        for it in (page.get("dados") or []):
            br_rows.append(("Brazil", it.get("transcricao", "")))
    for c, t in banded(br_rows):
        records.append(("Brazil_Chamber", "Brazil", "pt", t))
except Exception as e:
    print("BRAZIL ERR", e, file=sys.stderr)

# ---- argentina: EXCLUDED (session metadata only, no speech text) ----

os.makedirs(os.path.dirname(OUT), exist_ok=True)
from collections import Counter
cnt = Counter()
with open(OUT, "w", encoding="utf-8") as f:
    for i, (leg, country, lang, text) in enumerate(records):
        rec = {"i": i, "legislature": leg, "country": country, "lang": lang,
               "n_chars": len(text), "text": text}
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        cnt[leg] += 1
print(f"WROTE {len(records)} speeches -> {OUT}")
for k in sorted(cnt):
    print(f"  {k:28s} {cnt[k]}")

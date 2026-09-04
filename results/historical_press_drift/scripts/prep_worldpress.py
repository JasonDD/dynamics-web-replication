#!/usr/bin/env python3
"""prep_worldpress.py — build WITHIN-TITLE deep-time press samples for FR + NO.

Discipline (carried from the EN within-source finding): measure drift WITHIN a title
(same newspaper) over decades, never across a changing archive composition. Restrict to
an OCR-quality floor and CARRY OCR quality as a covariate (OCR improves over time and can
masquerade as drift).

Output: INPUT jsonl for cc_found_human_score.py -> {id, text, outcome, kind}
  outcome = year (str)
  kind    = "COUNTRY|title|decade|ocr"   (parsed back at analysis; title sanitised of '|')
  id      = unique per issue
"""
import json, re, collections, os, random

BASE = "the internal corpus store"
OUT_DIR = "the internal corpus store/results/historical_press_drift"
os.makedirs(OUT_DIR, exist_ok=True)
random.seed(17)

def sanitise(t):
    return re.sub(r"\s+", " ", (t or "").replace("|", "/")).strip()

def load(p):
    for l in open(p):
        try: yield json.loads(l)
        except: pass

# ---------------- FRANCE: french_pd_news ----------------
# fields: title (with ':' subtitle), date YYYY-MM-DD, ocr (0-100 str), word_count, complete_text
def fr_base(t):
    return sanitise(re.split(r"\s*:\s*", t or "")[0]).lower()[:45]

fr = list(load(f"{BASE}/french_pd_news/french_pd_news.jsonl"))
fr_rows = []
for x in fr:
    d = str(x.get("date") or "")
    m = re.match(r"(\d{4})", d)
    if not m: continue
    year = int(m.group(1)); dec = year // 10 * 10
    t = fr_base(x.get("title"))
    ocr = int(x["ocr"]) if str(x.get("ocr", "")).isdigit() else -1
    wc = x.get("word_count") or 0
    txt = x.get("complete_text") or ""
    if not t or ocr < 0: continue
    fr_rows.append(dict(title=t, year=year, dec=dec, ocr=ocr, wc=wc, text=txt,
                        fid=x.get("file_id")))

# titles spanning >=3 decades
fr_decs = collections.defaultdict(set)
for r in fr_rows: fr_decs[r["title"]].add(r["dec"])
fr_keep_titles = {t for t, ds in fr_decs.items() if len(ds) >= 3}

# OCR floor 80, word floor 150, cap 4 issues per (title,decade) keeping highest OCR
FR_OCR_FLOOR = 80; CAP = 4
fr_cells = collections.defaultdict(list)
for r in fr_rows:
    if r["title"] in fr_keep_titles and r["ocr"] >= FR_OCR_FLOOR and (r["wc"] or 0) >= 150:
        fr_cells[(r["title"], r["dec"])].append(r)
fr_input = []
for (t, dc), rs in fr_cells.items():
    rs.sort(key=lambda r: -r["ocr"])
    for r in rs[:CAP]:
        fr_input.append(r)

# ---------------- NORWAY: ncc_norwegian ----------------
# fields: id (title prefix), doc_type, publish_year, lang_fasttext_conf, text
NO_STOP = {"maalfrid", "wikipedia", "wikipedia-no", "regjeringen", "lovdata"}
no = list(load(f"{BASE}/ncc_norwegian/ncc_norwegian.jsonl"))
no_rows = []
for x in no:
    if x.get("doc_type") != "newspaper_ocr": continue
    y = x.get("publish_year")
    if not y: continue
    year = int(y); dec = year // 10 * 10
    t = (x.get("id") or "").split("_")[0].lower()
    if not t or t in NO_STOP: continue
    conf = float(x.get("lang_fasttext_conf") or 0)
    txt = x.get("text") or ""
    if len(txt.split()) < 80: continue
    no_rows.append(dict(title=t, year=year, dec=dec, ocr=int(conf * 100), text=txt, fid=x.get("id")))

no_decs = collections.defaultdict(set)
for r in no_rows: no_decs[r["title"]].add(r["dec"])
no_keep = {t for t, ds in no_decs.items() if len(ds) >= 2}
NO_CONF_FLOOR = 50; NO_CAP = 8
no_cells = collections.defaultdict(list)
for r in no_rows:
    if r["title"] in no_keep and r["ocr"] >= NO_CONF_FLOOR:
        no_cells[(r["title"], r["dec"])].append(r)
no_input = []
for (t, dc), rs in no_cells.items():
    random.shuffle(rs)
    for r in rs[:NO_CAP]:
        no_input.append(r)

def write_input(rows, country, path):
    with open(path, "w") as f:
        for i, r in enumerate(rows):
            kind = f"{country}|{r['title']}|{r['dec']}|{r['ocr']}"
            f.write(json.dumps({"id": f"{country}_{i}_{r['fid']}",
                                "text": r["text"], "outcome": str(r["year"]),
                                "kind": kind}) + "\n")

write_input(fr_input, "FR", f"{OUT_DIR}/fr_input.jsonl")
write_input(no_input, "NO", f"{OUT_DIR}/no_input.jsonl")

def summ(rows, keep, name):
    cells = collections.Counter((r["title"], r["dec"]) for r in rows)
    titles = collections.Counter(r["title"] for r in rows)
    decs = collections.Counter(r["dec"] for r in rows)
    print(f"{name}: {len(rows)} issues | {len(keep)} titles span-kept | {len(titles)} titles present | "
          f"{len(cells)} (title,decade) cells")
    print(f"  decades: {dict(sorted(decs.items()))}")
    print(f"  top titles: {[(t, n) for t, n in titles.most_common(8)]}")

summ(fr_input, fr_keep_titles, "FR")
summ(no_input, no_keep, "NO")
print("wrote", f"{OUT_DIR}/fr_input.jsonl", f"{OUT_DIR}/no_input.jsonl")

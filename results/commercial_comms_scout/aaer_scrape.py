#!/usr/bin/env python3
"""Scrape SEC AAER archive pages 2015-2022 for release number, date, and named respondent.
The friactions archive lists rows: AAER-#### <date> <name> ... We keep all, tag likely-firm rows."""
import urllib.request, re, json, time, sys
UA="Kronaxis research jasond@kronaxis.co.uk"
def get(u):
    for _ in range(3):
        try:
            req=urllib.request.Request(u, headers={"User-Agent":UA})
            with urllib.request.urlopen(req, timeout=60) as r: return r.read().decode("utf-8","ignore")
        except Exception:
            time.sleep(1.5)
    return ""
rows=[]
MONTHS="Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
for yr in range(2015,2023):
    for ext in ("shtml","htm"):
        html=get(f"https://www.sec.gov/divisions/enforce/friactions/friactions{yr}.{ext}")
        if not html: continue
        t=re.sub(r"<[^>]+>"," ",html); t=re.sub(r"&#160;|&nbsp;"," ",t); t=re.sub(r"\s+"," ",t)
        # pattern: AAER-#### <Mon>. DD, YYYY <name up to 'Other'/'Release No'/next AAER>
        for m in re.finditer(r"AAER-(\d+)\s+((?:%s)[a-z]*\.?\s+\d{1,2},\s+\d{4})\s+(.+?)(?=\s+(?:Other|Civil|Admin|Release No\.?:|AAER-\d|$))" % MONTHS, t):
            num, date, name = m.group(1), m.group(2), m.group(3).strip()
            if len(name)>2:
                rows.append({"aaer":int(num),"date":date,"name":name,"year":yr})
        if rows: break  # got one extension for this year
# dedup by aaer number, keep first
seen={}; out=[]
for r in rows:
    if r["aaer"] in seen: continue
    seen[r["aaer"]]=1; out.append(r)
OUTP="/tmp/aaer_releases.jsonl"
with open(OUTP,"w") as f:
    for r in out: f.write(json.dumps(r)+"\n")
print(f"[aaer] scraped {len(out)} releases 2015-2022 -> {OUTP}")
for r in out[:8]: print("  ", r["aaer"], r["date"], "|", r["name"][:60])

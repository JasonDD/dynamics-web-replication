#!/usr/bin/env python3
"""culture-compass temporal validation: does a nation's WEB-CHARACTER drift track
its SURVEY-OPINION drift, nation by nation?

WEB side  (already computed upstream, NOT re-scored here): per-ccTLD within-domain
matter/manner PC1 drift 2020->2026, read from ../where_when.txt (4 Common Crawl
snapshots, same domains in 2020 & 2026, controls for crawl composition). Positive =
drift toward MATTER.

SURVEY side: Integrated Values Survey (EVS + WVS) per-country item time series,
machine-readable and login-free from Our World in Data (owid/*.csv). Multiple waves
per country; latest wave 2022. We compute an opinion drift per country per item over
the most recent decade-ish span ending at the latest wave.

We then correlate, across nations, the survey opinion drift (per item) against the
web character drift. Pearson + Spearman, honest read.
"""
import csv, os
from scipy import stats as _ss

HERE = os.path.dirname(os.path.abspath(__file__))
OWID = os.path.join(HERE, "owid")
WEB  = os.path.join(HERE, "..", "where_when.txt")

# ---- ccTLD (web side) -> ISO3 (OWID Code) -------------------------------------
CC2ISO = {
 "JP":"JPN","DK":"DNK","BE":"BEL","NL":"NLD","NZ":"NZL","HU":"HUN","NO":"NOR",
 "GB":"GBR","SE":"SWE","FR":"FRA","AU":"AUS","CZ":"CZE","IT":"ITA","DE":"DEU",
 "AT":"AUT","ES":"ESP","UA":"UKR","CH":"CHE","RU":"RUS","PL":"POL","CA":"CAN",
 "RO":"ROU","BR":"BRA","IE":"IRL","PT":"PRT","ZA":"ZAF","US":"USA","FI":"FIN",
 "KR":"KOR","TR":"TUR","CN":"CHN","IN":"IND","GR":"GRC",
}

# ---- WEB drift ----------------------------------------------------------------
def load_web():
    web = {}  # ISO3 -> (drift, baseline, n, cc)
    for line in open(WEB):
        p = line.split()
        # rows look like:  JP  1259  -0.912  +0.0476   (cc n baseline drift), '[anglo]' optional
        if len(p) >= 4 and len(p[0]) == 2 and p[0].isupper() and p[1].isdigit():
            cc = p[0]
            try:
                n = int(p[1]); base = float(p[2]); drift = float(p[3])
            except ValueError:
                continue
            iso = CC2ISO.get(cc)
            if iso:
                web[iso] = dict(cc=cc, n=n, baseline=base, web_drift=drift)
    return web

# ---- SURVEY items: (file, value column index, higher_means) --------------------
ITEMS = {
 "religion_very_important": ("how-important-religion-is-in-your-life.csv", 3,
                             "more religious (share saying religion very important, %)"),
 "trust_government":        ("trust-state-institutions-wvs.csv", 8,
                             "more trust in government (%)"),
 "confidence_un":           ("confidence-in-un-wvs.csv", 3,
                             "more confidence in the UN (%)"),
 "homosexuality_not_justifiable": ("share-of-people-who-think-homosexuality-is-never-justified.csv", 3,
                             "more traditional social values (% homosexuality never justifiable)"),
}

def load_series(fname, vidx):
    """ISO3 -> {year: value}"""
    d = {}
    path = os.path.join(OWID, fname)
    r = csv.reader(open(path))
    next(r)  # header
    for row in r:
        if len(row) <= max(2, vidx): continue
        iso = row[1].strip()
        if not iso: continue
        yr = row[2].strip()
        val = row[vidx].strip()
        if not yr.isdigit() or val == "": continue
        try: v = float(val)
        except ValueError: continue
        d.setdefault(iso, {})[int(yr)] = v
    return d

def survey_drift(series, iso):
    """Opinion drift over the most-recent decade-ish span ending at the latest wave.
       end = latest year available; start = year closest to (end-12), span >= 6 yr."""
    ys = series.get(iso)
    if not ys or len(ys) < 2: return None
    years = sorted(ys)
    end = years[-1]
    target = end - 12
    # candidate starts strictly before end
    cands = [y for y in years if y < end]
    start = min(cands, key=lambda y: abs(y - target))
    if end - start < 6: return None
    return dict(start=start, end=end, span=end-start,
                v_start=ys[start], v_end=ys[end], drift=ys[end]-ys[start])

# ---- stats --------------------------------------------------------------------
def pearson(xs, ys):
    n = len(xs)
    if n < 3: return None, None, n
    r, p = _ss.pearsonr(xs, ys)
    return float(r), float(p), n

def spearman(xs, ys):
    n = len(xs)
    if n < 3: return None, None, n
    r, p = _ss.spearmanr(xs, ys)
    return float(r), float(p), n

# ---- run ----------------------------------------------------------------------
def main():
    web = load_web()
    print(f"# culture-compass drift alignment")
    print(f"# WEB drift: within-domain matter/manner PC1 delta 2020->2026 per ccTLD (../where_when.txt)")
    print(f"# SURVEY drift: OWID Integrated Values Survey (EVS+WVS), recent decade-ish span ending latest wave")
    print(f"# web-drift countries available: {len(web)}\n")

    for item,(fname,vidx,higher) in ITEMS.items():
        series = load_series(fname, vidx)
        rows = []
        for iso, w in web.items():
            sd = survey_drift(series, iso)
            if sd is None: continue
            rows.append((iso, w["cc"], w["web_drift"], sd["drift"], sd["start"], sd["end"]))
        rows.sort(key=lambda r: r[3])
        print("="*78)
        print(f"ITEM: {item}   (higher = {higher})")
        print(f"joined nations: {len(rows)}")
        if len(rows) < 3:
            print("  too few nations to correlate\n"); continue
        print(f"  {'cc':3} {'iso':4} {'web_dPC1':>9} {'op_drift':>9}  {'span':>9}")
        for iso,cc,wd,od,s,e in rows:
            print(f"  {cc:3} {iso:4} {wd:+9.4f} {od:+9.3f}  {s}->{e}")
        xs = [r[2] for r in rows]; ys = [r[3] for r in rows]
        pr, pp, n = pearson(xs, ys)
        sr, sp, _ = spearman(xs, ys)
        print(f"  --> Pearson  r={pr:+.3f}  p={pp:.3f}  (n={n})")
        print(f"  --> Spearman r={sr:+.3f}  p={sp:.3f}")
        # sign-agreement (does the SIGN of opinion drift match sign of web drift?)
        agree = sum(1 for x,y in zip(xs,ys) if (x>0)==(y>0))
        print(f"  --> sign agreement (web>0 vs op>0): {agree}/{n} = {agree/n:.0%}\n")

if __name__ == "__main__":
    main()

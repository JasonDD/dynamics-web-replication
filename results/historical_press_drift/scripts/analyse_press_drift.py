#!/usr/bin/env python3
"""analyse_press_drift.py — HISTORICAL PRESS DRIFT MATRIX (country x decade), within-title.

Sources (same 8-axis 7B scorer, scales match):
  EN  histchar within_source_articles_only.jsonl   {series,year,decade,char}   (HELD)
  FR  scored.jsonl (kind=FR|title|decade|ocr)                                  (fresh)
  NO  scored.jsonl (kind=NO|title|decade|ocr)                                  (fresh)

DISCIPLINE:
  * WITHIN-TITLE drift only (same newspaper across decades); the archive-wide mean is a
    composition artefact and is NOT the test.
  * OCR floor already applied in prep; OCR carried as covariate here (FR/NO).
  * matter = rigour+depth ; manner = affect+stance+register.  M = matter_z - manner_z (+ = matter).
    z pooled GLOBALLY over all countries so cells sit on one ruler.
"""
import json, re, collections, numpy as np
from scipy import stats

DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
IX = {a:i for i,a in enumerate(DWEB)}
RES = "the internal corpus store/results/historical_press_drift"
EN_PATH = "the internal corpus store/histchar/within_source_articles_only.jsonl"

def as_vec(ch):
    if isinstance(ch, str):
        ch = json.loads(ch.replace("'", '"'))
    return np.array([float(ch[a]) for a in DWEB]) if all(a in ch for a in DWEB) else None

recs = []   # dict(country,title,year,decade,ocr,vec)

# EN (held)
for l in open(EN_PATH):
    try: r = json.loads(l)
    except: continue
    v = as_vec(r.get("char"))
    if v is None: continue
    y = int(r["year"])
    recs.append(dict(country="EN", title=r["series"], year=y, decade=y//10*10, ocr=None, vec=v))

# FR + NO (fresh)
for l in open(f"{RES}/scored.jsonl"):
    try: r = json.loads(l)
    except: continue
    v = as_vec(r.get("char"))
    if v is None: continue
    parts = r["kind"].split("|")
    country, title, dec, ocr = parts[0], parts[1], int(parts[2]), int(parts[3])
    y = int(r["outcome"])
    recs.append(dict(country=country, title=title, year=y, decade=y//10*10, ocr=ocr, vec=v))

print(f"loaded {len(recs)} scored issues: " +
      ", ".join(f"{c}={sum(1 for r in recs if r['country']==c)}" for c in ["EN","FR","NO"]))

# ---- global pooled z, matter/manner ruler ----
V = np.array([r["vec"] for r in recs])
MEAN, STD = V.mean(0), V.std(0)+1e-9
def z(v): return (v-MEAN)/STD
def matter_z(v): zz=z(v); return zz[IX["rigour"]]+zz[IX["depth"]]
def manner_z(v): zz=z(v); return zz[IX["affect"]]+zz[IX["stance"]]+zz[IX["register"]]
def M(v): return matter_z(v)-manner_z(v)          # + = toward matter
for r in recs:
    r["M"]=M(r["vec"]); r["affect"]=r["vec"][IX["affect"]]
    r["matter_raw"]=r["vec"][IX["rigour"]]+r["vec"][IX["depth"]]

# ============ 1. COUNTRY x DECADE MATRIX (title-balanced: mean of per-title decade means) ============
# each (country,title,decade) -> mean M ; then average those cell-means per (country,decade)
tcd = collections.defaultdict(list)
for r in recs: tcd[(r["country"],r["title"],r["decade"])].append(r["M"])
tcd_mean = {k:np.mean(v) for k,v in tcd.items()}
cd = collections.defaultdict(list)
cd_n = collections.defaultdict(int)
for (c,t,d),m in tcd_mean.items(): cd[(c,d)].append(m)
for r in recs: cd_n[(r["country"],r["decade"])]+=1
decades = sorted({d for (_,d) in cd})
countries = ["EN","FR","NO"]
print("\n=== COUNTRY x DECADE MATRIX — mean matter/manner M (+=matter), title-balanced ===")
print("    (cell = mean over titles of that title's mean M in the decade; n = issues)")
hdr = "  decade " + "".join(f"{c:>12}" for c in countries)
print(hdr)
for d in decades:
    row = f"  {d:>6} "
    for c in countries:
        if (c,d) in cd:
            row += f"{np.mean(cd[(c,d)]):>+8.2f}({cd_n[(c,d)]:>2})"
        else:
            row += f"{'--':>12}"
    print(row)

# ============ 2. WITHIN-TITLE DRIFT SLOPE per country (the honest test) ============
print("\n=== WITHIN-TITLE DRIFT: per-title slope of M vs year, then aggregated per country ===")
print("    (+ slope = title drifts toward MATTER over its life; - = toward MANNER)")
def within_title(country, min_iss=6, min_span=30):
    byt = collections.defaultdict(list)
    for r in recs:
        if r["country"]==country: byt[r["title"]].append(r)
    slopes=[]; rows=[]
    for t, rs in byt.items():
        yrs=[r["year"] for r in rs]
        if len(rs)<min_iss or (max(yrs)-min(yrs))<min_span: continue
        sl,ic,rr,pp,se = stats.linregress([r["year"] for r in rs],[r["M"] for r in rs])
        slopes.append(sl); rows.append((t,len(rs),min(yrs),max(yrs),sl,pp))
    return slopes, rows

for c in countries:
    slopes, rows = within_title(c)
    if len(slopes)<2:
        print(f"\n  {c}: only {len(slopes)} qualifying titles — underpowered, reported as thin.")
        for t,n,y0,y1,sl,pp in rows:
            print(f"     {t[:40]:<40} n={n:>3} {y0}-{y1} slope={sl:+.4f}/yr p={pp:.3f}")
        continue
    slopes=np.array(slopes)
    t,p = stats.ttest_1samp(slopes,0)
    npos=int((slopes>0).sum()); ntot=len(slopes)
    sign_p = stats.binomtest(npos, ntot, 0.5).pvalue if hasattr(stats,'binomtest') else stats.binom_test(npos,ntot,0.5)
    print(f"\n  {c}: {ntot} titles | mean within-title slope = {slopes.mean():+.4f}/yr "
          f"| one-sample t={t:+.2f} p={p:.4f} | toward-matter {npos}/{ntot} sign p={sign_p:.4f}")
    for t2,n,y0,y1,sl,pp in sorted(rows,key=lambda x:x[4]):
        print(f"     {t2[:40]:<40} n={n:>3} {y0}-{y1} slope={sl:+.4f}/yr p={pp:.3f}")

# ============ 3. PER-AXIS within-title drift (affect flat? matter rising/falling?) ============
print("\n=== PER-AXIS within-title mean slope per country (raw 0-1 axis vs year) ===")
axes_probe = ["rigour","depth","affect","stance","register","originality","candour","commercial_drive"]
print(f"  {'country':<8}" + "".join(f"{a[:8]:>10}" for a in axes_probe))
for c in countries:
    byt = collections.defaultdict(list)
    for r in recs:
        if r["country"]==c: byt[r["title"]].append(r)
    perax={a:[] for a in axes_probe}
    for t,rs in byt.items():
        yrs=[r["year"] for r in rs]
        if len(rs)<6 or (max(yrs)-min(yrs))<30: continue
        for a in axes_probe:
            sl,_,_,_,_ = stats.linregress([r["year"] for r in rs],[r["vec"][IX[a]] for r in rs])
            perax[a].append(sl)
    if not perax["affect"]:
        print(f"  {c:<8}  (thin)"); continue
    print(f"  {c:<8}" + "".join(f"{np.mean(perax[a])*100:>+10.3f}" for a in axes_probe) + "   (x100 /yr)")

# ============ 4. OCR CONFOUND CHECK (FR/NO) ============
print("\n=== OCR CONFOUND: is the drift explained by rising OCR quality? (FR/NO) ===")
for c in ["FR","NO"]:
    rr=[r for r in recs if r["country"]==c and r["ocr"] is not None]
    if len(rr)<20: print(f"  {c}: too few"); continue
    yr=np.array([r["year"] for r in rr]); oc=np.array([r["ocr"] for r in rr]); Mv=np.array([r["M"] for r in rr])
    r_oy = np.corrcoef(oc,yr)[0,1]; r_oM = np.corrcoef(oc,Mv)[0,1]
    # partial: regress M on year AND ocr
    Xd = np.column_stack([yr, oc, np.ones_like(yr)])
    beta,_,_,_ = np.linalg.lstsq(Xd, Mv, rcond=None)
    sl_raw,_,_,p_raw,_ = stats.linregress(yr, Mv)
    print(f"  {c}: corr(ocr,year)={r_oy:+.2f} corr(ocr,M)={r_oM:+.2f} | "
          f"pooled M~year slope={sl_raw:+.4f}/yr (p={p_raw:.3f}) | "
          f"M~year+ocr partial year-slope={beta[0]:+.4f}/yr, ocr-coef={beta[1]:+.4f}")
    # matched high-OCR band
    hi = oc>=np.percentile(oc,50)
    if hi.sum()>15:
        sl_hi,_,_,p_hi,_ = stats.linregress(yr[hi], Mv[hi])
        print(f"      high-OCR half (ocr>=p50={np.percentile(oc,50):.0f}): M~year slope={sl_hi:+.4f}/yr p={p_hi:.3f}")

# ============ 5. CROSS-COUNTRY CONSISTENCY ============
print("\n=== CROSS-COUNTRY CONSISTENCY of within-title drift direction ===")
dirs={}
for c in countries:
    slopes,_=within_title(c)
    if slopes: dirs[c]=(np.mean(slopes), len(slopes))
for c,(m,n) in dirs.items():
    print(f"  {c}: mean within-title slope {m:+.4f}/yr over {n} titles -> "
          f"{'toward MATTER' if m>0 else 'toward MANNER'}")
if len([c for c in dirs if dirs[c][1]>=3])>=2:
    sg=[c for c in dirs if dirs[c][1]>=3]
    same = len(set(np.sign(dirs[c][0]) for c in sg))==1
    print(f"  countries with >=3 titles: {sg} -> drift direction {'CONSISTENT' if same else 'DIVERGENT'}")

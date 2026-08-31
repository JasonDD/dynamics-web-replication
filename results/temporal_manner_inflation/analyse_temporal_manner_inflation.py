#!/usr/bin/env python3
"""analyse_temporal_manner_inflation.py — is the web getting MORE MANIPULATIVE over time?

The manipulation signature (from results/manner_inflation_deception/ + length_mechanism/) is
AFFECT inflated + MATTER starved. This asks whether the affect-heavy, matter-starved fraction of
the web is rising or falling across four Common Crawl snapshots (2020, 2022, 2024, 2026).

Pure read on ALREADY-SCORED data: cc_v3.domain_char8_cc{2020,2022,2024,2026} (8 axes/domain).
No new character scoring, no :8301, no :8288. Postgres :5432 only.

CRITICAL DISCIPLINE: the archive-wide mean is a COMPOSITION artefact (the crawl grows and its
domain mix changes). The primary test is WITHIN-DOMAIN: the same domains present across snapshots.

Axes: rigour, depth, originality, candour, affect, commercial_drive, stance, register.
  matter = rigour + depth ; manner = affect + stance + register (spec definition).
Standardisation: pooled z-scores over all four snapshots (matches the PC1 recipe).
  matter_z  = z(rigour) + z(depth)
  manner_z  = z(affect) + z(stance) + z(register)
  manner_inflation = manner_z - matter_z   (higher = more manner relative to matter)
Matter-starved (manipulation-signature) fraction: manner_z > 0 AND matter_z < 0, at the same
  fixed pooled thresholds every year (so the trend is composition-controlled when measured on a
  fixed domain set).
"""
import os, re, numpy as np, psycopg2
from scipy import stats

DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
IX = {a:i for i,a in enumerate(DWEB)}
SNAPS = {2020:"domain_char8_cc2020",2022:"domain_char8_cc2022",2024:"domain_char8_cc2024",2026:"domain_char8_cc2026"}
TLD = {"uk":"GB","ca":"CA","au":"AU","nz":"NZ","za":"ZA","ie":"IE","us":"US","de":"DE","fr":"FR","nl":"NL","it":"IT",
       "es":"ES","pl":"PL","jp":"JP","br":"BR","in":"IN","ru":"RU","se":"SE","no":"NO","dk":"DK"}
PW = [l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
c = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()

snap = {}
for yr,t in SNAPS.items():
    c.execute(f"SELECT domain,{','.join(DWEB)} FROM cc_v3.{t}")
    snap[yr] = {(r[0] or '').lower(): np.array([float(x) for x in r[1:]]) for r in c.fetchall()}
    print(f"[when] {yr}: {len(snap[yr]):,} domains")

yrs = sorted(SNAPS)
allv = np.array([v for d in snap.values() for v in d.values()])
MEAN = allv.mean(0); STD = allv.std(0) + 1e-9
def z(v): return (v - MEAN) / STD

# PC1 (matter/manner), oriented + = matter, for cross-check against when_drift.txt
_,_,Vt = np.linalg.svd(z(allv), full_matrices=False); PC1 = Vt[0]
if (PC1[IX["rigour"]] + PC1[IX["depth"]]) < 0: PC1 = -PC1
def pc1(v): return float(z(v) @ PC1)

def matter_z(v):  zz = z(v); return zz[IX["rigour"]] + zz[IX["depth"]]
def manner_z(v):  zz = z(v); return zz[IX["affect"]] + zz[IX["stance"]] + zz[IX["register"]]
def infl(v):      return manner_z(v) - matter_z(v)
def affect_raw(v):return v[IX["affect"]]
def starved(v):   return (manner_z(v) > 0) and (matter_z(v) < 0)          # manipulation signature
def starved_strict(v):
    zz = z(v)
    return (zz[IX["affect"]] > 0.5) and ((zz[IX["rigour"]] + zz[IX["depth"]]) < -0.5)

print("\n=== 1. per-snapshot MEANS (COMPOSITION-confounded — the crawl mix changes; read §2/§3 as primary) ===")
print(f"  {'yr':>6}{'n':>9}{'affect':>9}{'manner_z':>10}{'matter_z':>10}{'infl':>9}{'starved%':>10}{'strict%':>9}{'PC1':>9}")
for yr in yrs:
    V = list(snap[yr].values())
    aff = np.mean([affect_raw(v) for v in V]); mz = np.mean([manner_z(v) for v in V]); mtz = np.mean([matter_z(v) for v in V])
    inf = np.mean([infl(v) for v in V]); st = np.mean([starved(v) for v in V]); sts = np.mean([starved_strict(v) for v in V])
    p1 = np.mean([pc1(v) for v in V])
    print(f"  {yr:>6}{len(V):>9,}{aff:>9.3f}{mz:>10.3f}{mtz:>10.3f}{inf:>9.3f}{st*100:>9.1f}%{sts*100:>8.1f}%{p1:>9.3f}")

# ---- FIXED DOMAIN SET across ALL FOUR snapshots => composition held constant for the year trend ----
allfour = [d for d in snap[2020] if d in snap[2022] and d in snap[2024] and d in snap[2026]]
print(f"\n=== 2. FIXED-PANEL trend 2020->2026 (same {len(allfour):,} domains in ALL FOUR snapshots) ===")
print(f"  {'yr':>6}{'affect':>9}{'manner_z':>10}{'matter_z':>10}{'infl':>9}{'starved%':>10}{'strict%':>9}")
series = {"affect":[], "manner_z":[], "matter_z":[], "infl":[], "starved":[], "strict":[]}
for yr in yrs:
    aff = np.mean([affect_raw(snap[yr][d]) for d in allfour])
    mz  = np.mean([manner_z(snap[yr][d]) for d in allfour])
    mtz = np.mean([matter_z(snap[yr][d]) for d in allfour])
    inf = np.mean([infl(snap[yr][d]) for d in allfour])
    st  = np.mean([starved(snap[yr][d]) for d in allfour])
    sts = np.mean([starved_strict(snap[yr][d]) for d in allfour])
    for k,val in zip(series, [aff,mz,mtz,inf,st,sts]): series[k].append(val)
    print(f"  {yr:>6}{aff:>9.3f}{mz:>10.3f}{mtz:>10.3f}{inf:>9.3f}{st*100:>9.1f}%{sts*100:>8.1f}%")
print("\n  linear trend over the 4 years (fixed panel, composition-controlled):")
for k in ["affect","manner_z","matter_z","infl","starved","strict"]:
    sl,inter,r,p,se = stats.linregress(yrs, series[k])
    unit = "/yr" ; scale = 100 if k in ("starved","strict") else 1
    print(f"    {k:<10} slope {sl*scale:+.4f}{'%%' if scale==100 else ''}{unit}  r={r:+.2f}  p={p:.4g}")

# ---- PAIRED within-domain 2020 -> 2026 (endpoints; the headline within-source test) ----
both = [d for d in snap[2020] if d in snap[2026]]
print(f"\n=== 3. PAIRED within-domain 2020->2026 (same {len(both):,} domains, endpoints) ===")
def paired(fn, name, is_frac=False):
    a = np.array([fn(snap[2020][d]) for d in both]); b = np.array([fn(snap[2026][d]) for d in both])
    if is_frac:
        # McNemar-style: fraction change + paired t on the 0/1 indicator
        t,p = stats.ttest_rel(b.astype(float), a.astype(float))
        print(f"  {name:<16} {a.mean()*100:6.2f}% -> {b.mean()*100:6.2f}%  Δ={(b.mean()-a.mean())*100:+.2f}pp  paired t={t:+.2f} p={p:.4g}")
    else:
        t,p = stats.ttest_rel(b, a)
        print(f"  {name:<16} {a.mean():+7.3f} -> {b.mean():+7.3f}  Δ={b.mean()-a.mean():+.3f}  paired t={t:+.2f} p={p:.4g}")
paired(affect_raw, "affect (raw)")
paired(manner_z,   "manner_z")
paired(matter_z,   "matter_z")
paired(infl,       "manner_inflation")
paired(pc1,        "matter/manner PC1")
paired(starved,        "starved frac", is_frac=True)
paired(starved_strict, "starved strict", is_frac=True)

# ---- per-country manner-inflation drift (within-domain) ----
print(f"\n=== 4. within-domain Δ manner_inflation by ccTLD (2020->2026, + = MORE manner/manipulative) ===")
bycc = {}
for d in both:
    m = re.search(r"\.([a-z]{2,})$", d); cc = TLD.get(m.group(1)) if m else None
    if cc: bycc.setdefault(cc, []).append(infl(snap[2026][d]) - infl(snap[2020][d]))
print(f"  {'cc':<6}{'n':>7}{'Δinfl':>10}{'Δaffect':>10}")
byaff = {}
for d in both:
    m = re.search(r"\.([a-z]{2,})$", d); cc = TLD.get(m.group(1)) if m else None
    if cc: byaff.setdefault(cc, []).append(affect_raw(snap[2026][d]) - affect_raw(snap[2020][d]))
for cc in sorted(bycc, key=lambda k:-len(bycc[k])):
    if len(bycc[cc]) >= 30:
        print(f"  {cc:<6}{len(bycc[cc]):>7}{np.mean(bycc[cc]):>+10.3f}{np.mean(byaff[cc]):>+10.3f}")

print("\n[note] matter = rigour+depth, manner = affect+stance+register; z pooled over 4 snapshots.")
print("       §1 mean is composition-confounded; §2 (fixed 4-snapshot panel) and §3 (paired endpoints)")
print("       are the composition-controlled within-source tests. Positive infl/affect/starved = MORE manipulative.")

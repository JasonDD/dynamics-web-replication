#!/usr/bin/env python3
"""comms_b_analyse.py — Experiment B analysis. Credibility signature + trust-loss anchor (BoE autumn 2022)."""
import json, statistics as st, collections, math
D="the internal corpus store/comms_scout"
AXES=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]

def load(p):
    out=[]
    for l in open(p):
        try: out.append(json.loads(l))
        except Exception: pass
    return out

def mean(xs): return sum(xs)/len(xs) if xs else float("nan")
def sd(xs): return st.pstdev(xs) if len(xs)>1 else 0.0
def welch(a,b):
    if len(a)<2 or len(b)<2: return float("nan"), float("nan")
    ma,mb=mean(a),mean(b); va,vb=st.variance(a),st.variance(b); na,nb=len(a),len(b)
    se=math.sqrt(va/na+vb/nb)
    if se==0: return float("nan"), float("nan")
    t=(ma-mb)/se
    df=(va/na+vb/nb)**2/((va/na)**2/(na-1)+(vb/nb)**2/(nb-1))
    # two-sided p via normal approx of t for df>30 else rough
    from math import erf,sqrt
    p=2*(1-0.5*(1+erf(abs(t)/sqrt(2))))
    return t,p

sig=load(f"{D}/signature_scored.jsonl")
print("="*70); print(f"CREDIBILITY SIGNATURE  (n={len(sig)} central bank speeches, {len(set(r['bank'] for r in sig))} banks)"); print("="*70)
prof={}
for ax in AXES:
    xs=[r["axes"][ax] for r in sig]; prof[ax]=mean(xs)
    print(f"  {ax:16s} mean {mean(xs):.3f}  sd {sd(xs):.3f}")
print(f"\n  PREDICTION: high rigour, high candour, low affect.")
print(f"  rigour {prof['rigour']:.3f}, candour {prof['candour']:.3f}, affect {prof['affect']:.3f}, commercial_drive {prof['commercial_drive']:.3f}")
# credibility index vs manipulation pole (deceptive dir ~ affect+ candour- depth- commercial_drive+)
def cred(r): a=r["axes"]; return (a["candour"]+a["rigour"]+a["depth"]-a["affect"]-a["commercial_drive"])
ci=[cred(r) for r in sig]
print(f"  credibility index (candour+rigour+depth - affect - commercial_drive): mean {mean(ci):+.3f} sd {sd(ci):.3f}")
print("\n  per-bank profile (rigour / candour / affect / cred-index):")
for bank,g in sorted(((b,[r for r in sig if r['bank']==b]) for b in set(r['bank'] for r in sig)), key=lambda x:-len(x[1])):
    if len(g)<5: continue
    print(f"    {bank[:42]:42s} n={len(g):3d}  rig {mean([r['axes']['rigour'] for r in g]):.2f}  can {mean([r['axes']['candour'] for r in g]):.2f}  aff {mean([r['axes']['affect'] for r in g]):.2f}  CI {mean([cred(r) for r in g]):+.2f}")

# ---- BoE trust-loss anchor ----
boe=load(f"{D}/boe_scored.jsonl")
print("\n"+"="*70); print(f"TRUST-LOSS ANCHOR  Bank of England, t0 = autumn 2022 gilt/LDI episode  (n={len(boe)})"); print("="*70)
def ym(r): return r["year"]+ (r["month"] or 6)/12.0
boe=[r for r in boe if r.get("year")]
byyear=collections.defaultdict(list)
for r in boe: byyear[r["year"]].append(r)
print("  per-year BoE character:")
print(f"    {'year':4s} {'n':>3s}  {'rigour':>7s} {'candour':>7s} {'affect':>7s} {'comm':>6s} {'credIdx':>7s}")
for y in sorted(byyear):
    g=byyear[y]
    print(f"    {y:4d} {len(g):3d}  {mean([r['axes']['rigour'] for r in g]):7.3f} {mean([r['axes']['candour'] for r in g]):7.3f} {mean([r['axes']['affect'] for r in g]):7.3f} {mean([r['axes']['commercial_drive'] for r in g]):6.3f} {mean([cred(r) for r in g]):7.3f}")
# before vs the crisis year: baseline 2018-2021 vs 2022 (run-up/impact) and 2023 (after)
base=[r for r in boe if 2018<=r["year"]<=2021]
cris=[r for r in boe if r["year"]==2022]
after=[r for r in boe if r["year"]==2023]
print(f"\n  baseline 2018-2021 (n={len(base)}) vs 2022 (n={len(cris)}) vs 2023 (n={len(after)}):")
for ax in ["affect","candour","rigour","commercial_drive"]:
    b=[r["axes"][ax] for r in base]; c=[r["axes"][ax] for r in cris]; a=[r["axes"][ax] for r in after]
    t,p=welch(c,b)
    print(f"    {ax:16s} base {mean(b):.3f}  2022 {mean(c):.3f}  2023 {mean(a):.3f}   (2022 vs base: t={t:+.2f} p={p:.3f})")
cb=[cred(r) for r in base]; cc=[cred(r) for r in cris]
t,p=welch(cc,cb)
print(f"    cred_index       base {mean(cb):+.3f}  2022 {mean(cc):+.3f}   (t={t:+.2f} p={p:.3f})")
print("\n  NOTE: dataset date granularity is year+month (no day). Autumn 2022 = months 9-11.")
crun=[r for r in cris if (r['month'] or 0)>=6]
if crun:
    print(f"    2022 H2 only (n={len(crun)}): affect {mean([r['axes']['affect'] for r in crun]):.3f}  candour {mean([r['axes']['candour'] for r in crun]):.3f}  cred {mean([cred(r) for r in crun]):+.3f}")

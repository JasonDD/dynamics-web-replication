#!/usr/bin/env python3
"""Experiment A2 analysis: does the manipulation signature rise in earnings calls BEFORE fraud exposure?
Compares fraud_pre (calls in [t0-2y,t0)) vs fraud_base (same firm, earlier) vs control (same-SIC S&P500)."""
import json, statistics as st, math, collections
D="the internal corpus store/comms_scout"
AXES=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
def load(p):
    o=[]
    for l in open(p):
        try: o.append(json.loads(l))
        except Exception: pass
    return o
def mean(xs): return sum(xs)/len(xs) if xs else float("nan")
def sd(xs): return st.pstdev(xs) if len(xs)>1 else 0.0
def cohend(a,b):
    if len(a)<2 or len(b)<2: return float("nan")
    va,vb=st.variance(a),st.variance(b); na,nb=len(a),len(b)
    sp=math.sqrt(((na-1)*va+(nb-1)*vb)/max(1,na+nb-2)); return (mean(a)-mean(b))/sp if sp else float("nan")
def welch(a,b):
    if len(a)<2 or len(b)<2: return float("nan"),float("nan")
    ma,mb=mean(a),mean(b); va,vb=st.variance(a),st.variance(b); na,nb=len(a),len(b)
    se=math.sqrt(va/na+vb/nb)
    if se==0: return float("nan"),float("nan")
    t=(ma-mb)/se
    from math import erf,sqrt
    return t, 2*(1-0.5*(1+erf(abs(t)/sqrt(2))))
def cred(r): a=r["axes"]; return a["candour"]+a["rigour"]+a["depth"]-a["affect"]-a["commercial_drive"]

rows=load(f"{D}/a2_calls_scored.jsonl")
pre=[r for r in rows if r["window"]=="fraud_pre"]
base=[r for r in rows if r["window"]=="fraud_base"]
ctl=[r for r in rows if r["window"]=="control"]
print("="*70); print("EXPERIMENT A2 — manipulation signature in earnings CALLS before fraud exposure"); print("="*70)
print(f"  fraud pre-exposure calls {len(pre)} ({len(set(r['ticker'] for r in pre))} firms)")
print(f"  same-firm earlier baseline calls {len(base)} ({len(set(r['ticker'] for r in base))} firms)")
print(f"  sector-matched control calls {len(ctl)} ({len(set(r['ticker'] for r in ctl))} firms)")

print("\n  mean axis (fraud_pre / fraud_base / control):")
print(f"    {'axis':16s} {'pre':>7s} {'base':>7s} {'ctrl':>7s}  {'d(pre-ctl)':>10s} {'p':>6s}  {'d(pre-base)':>11s} {'p':>6s}")
for ax in AXES+["_cred"]:
    if ax=="_cred": p=[cred(r) for r in pre]; b=[cred(r) for r in base]; k=[cred(r) for r in ctl]; nm="cred_index"
    else: p=[r["axes"][ax] for r in pre]; b=[r["axes"][ax] for r in base]; k=[r["axes"][ax] for r in ctl]; nm=ax
    d1,pp1=cohend(p,k),welch(p,k)[1]; d2,pp2=cohend(p,b),welch(p,b)[1]
    print(f"    {nm:16s} {mean(p):7.3f} {mean(b):7.3f} {mean(k):7.3f}  {d1:10.2f} {pp1:6.3f}  {d2:11.2f} {pp2:6.3f}")

# within-firm paired: firms with both pre and base
byf=collections.defaultdict(lambda:{"pre":[],"base":[]})
for r in pre: byf[r["ticker"]]["pre"].append(r)
for r in base:
    if r["ticker"] in byf: byf[r["ticker"]]["base"].append(r)
paired=[(t,v) for t,v in byf.items() if v["pre"] and v["base"]]
print(f"\n  WITHIN-FIRM paired (pre vs own earlier baseline): n={len(paired)} firms")
for ax in ["affect","candour","commercial_drive","_cred"]:
    diffs=[]
    for t,v in paired:
        if ax=="_cred": pm=mean([cred(r) for r in v["pre"]]); bm=mean([cred(r) for r in v["base"]])
        else: pm=mean([r["axes"][ax] for r in v["pre"]]); bm=mean([r["axes"][ax] for r in v["base"]])
        diffs.append(pm-bm)
    predpos = ax in ("affect","commercial_drive")
    good=sum(1 for d in diffs if (d>0)==predpos)
    nm="cred_index" if ax=="_cred" else ax
    print(f"    {nm:16s} mean(pre-base) {mean(diffs):+.3f}   {good}/{len(diffs)} firms in predicted direction")
print("\n  Prediction: fraud_pre shows affect UP, candour DOWN, commercial_drive UP, cred_index DOWN.")
print("  Caveats: large-cap S&P500 respondents (localized restatements / some FCPA books-and-records),")
print("  a harder testbed than small-cap built-on-fraud firms; first 6000 chars (prepared remarks) scored.")

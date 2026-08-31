#!/usr/bin/env python3
"""comms_a_analyse.py — Experiment A analysis. Does the manipulation signature (affect up, candour down)
rise in fraud-active-year filings vs the same firms' clean years and vs control firms?"""
import json, statistics as st, math, collections
D="/mnt/nas/kronaxis/corpora/comms_scout"
AXES=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]

def load(p):
    out=[]
    for l in open(p):
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def mean(xs): return sum(xs)/len(xs) if xs else float("nan")
def sd(xs): return st.pstdev(xs) if len(xs)>1 else 0.0
def cohend(a,b):
    if len(a)<2 or len(b)<2: return float("nan")
    na,nb=len(a),len(b); va,vb=st.variance(a),st.variance(b)
    sp=math.sqrt(((na-1)*va+(nb-1)*vb)/max(1,na+nb-2))
    return (mean(a)-mean(b))/sp if sp else float("nan")
def welch(a,b):
    if len(a)<2 or len(b)<2: return float("nan"),float("nan")
    ma,mb=mean(a),mean(b); va,vb=st.variance(a),st.variance(b); na,nb=len(a),len(b)
    se=math.sqrt(va/na+vb/nb)
    if se==0: return float("nan"),float("nan")
    t=(ma-mb)/se
    from math import erf,sqrt
    p=2*(1-0.5*(1+erf(abs(t)/sqrt(2))))
    return t,p
def cred(r): a=r["axes"]; return (a["candour"]+a["rigour"]+a["depth"]-a["affect"]-a["commercial_drive"])

rows=load(f"{D}/a_filings_scored.jsonl")
fraud=[r for r in rows if r["label"]=="fraud"]
clean=[r for r in rows if r["label"]=="clean"]
ctrl =[r for r in rows if r["label"]=="control"]
print("="*70); print(f"EXPERIMENT A — fraud pre-signature in 10-K filings"); print("="*70)
print(f"  fraud-active filings {len(fraud)} | same-firm clean filings {len(clean)} | control-firm filings {len(ctrl)}")
print(f"  distinct fraud firms {len(set(r['cik'] for r in fraud))} | control firms {len(set(r['cik'] for r in ctrl))}")

print("\n  mean axis by group (fraud-active / same-firm clean / control):")
print(f"    {'axis':16s} {'fraud':>7s} {'clean':>7s} {'control':>7s}   {'d(fr-cl)':>8s} {'p':>6s}")
for ax in AXES+["_cred"]:
    if ax=="_cred":
        f=[cred(r) for r in fraud]; c=[cred(r) for r in clean]; k=[cred(r) for r in ctrl]; nm="cred_index"
    else:
        f=[r["axes"][ax] for r in fraud]; c=[r["axes"][ax] for r in clean]; k=[r["axes"][ax] for r in ctrl]; nm=ax
    d=cohend(f,c); t,p=welch(f,c)
    print(f"    {nm:16s} {mean(f):7.3f} {mean(c):7.3f} {mean(k):7.3f}   {d:8.2f} {p:6.3f}")

# within-firm paired: firms with both fraud and clean filings
byfirm=collections.defaultdict(lambda: {"fraud":[], "clean":[]})
for r in fraud: byfirm[r["cik"]]["fraud"].append(r)
for r in clean:
    if r["cik"] in byfirm: byfirm[r["cik"]]["clean"].append(r)
paired=[(c,v) for c,v in byfirm.items() if v["fraud"] and v["clean"]]
print(f"\n  WITHIN-FIRM paired (firms with both fraud and clean filings): n={len(paired)} firms")
for ax in ["affect","candour","commercial_drive","_cred"]:
    diffs=[]
    for cik,v in paired:
        if ax=="_cred":
            fm=mean([cred(r) for r in v["fraud"]]); cm=mean([cred(r) for r in v["clean"]])
        else:
            fm=mean([r["axes"][ax] for r in v["fraud"]]); cm=mean([r["axes"][ax] for r in v["clean"]])
        diffs.append(fm-cm)
    pos=sum(1 for d in diffs if d>0)
    t,p=welch(diffs,[0.0]*len(diffs)) if len(diffs)>1 else (float('nan'),float('nan'))
    nm="cred_index" if ax=="_cred" else ax
    print(f"    {nm:16s} mean(fraud-clean) {mean(diffs):+.3f}  {pos}/{len(diffs)} firms positive")
print("\n  Prediction: fraud filings show affect UP, candour DOWN, cred_index DOWN vs clean/control.")
print("  Caveat: 10-K prose is dry and boilerplate-heavy; affect range is compressed; n is feasibility-scale.")

#!/usr/bin/env python3
"""detector_analyse.py — within-institution event study around the 2021-2022 transitory-inflation walk-back.

For each institution the reversal month t0 is where its OWN credibility took the hit. We compute a signed
month distance d = (year-t0y)*12 + (month-t0m), bin speeches by d, and ask whether the credibility signature
(high rigour, high candour, low affect, low commercial_drive) DEGRADES in the bins BEFORE and AROUND t0
versus the institution's own earlier baseline. Candour falling or affect rising ahead of t0 would make
credibility drift a LEADING indicator of trust loss.

Reads detector_scored.jsonl (this run) + boe_scored.jsonl (reused from Experiment B) for a 5th institution.
"""
import json, statistics as st, collections, math

NAS="/mnt/nas/kronaxis/corpora/comms_scout"
AXES=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]

# t0 = reversal / own-credibility-loss month per institution
T0={
 "federal reserve":        (2021,11),   # Powell retires "transitory" 30 Nov 2021
 "european central bank":  (2022,7),    # first hike; Lagarde defended transitory into late 2021
 "reserve bank of australia":(2022,5),  # abandons "no hike until 2024" guidance; RBA Review follows
 "bank of england":        (2021,12),   # first hike; transitory framing walked back
}
def cred_index(a): return a["candour"]+a["rigour"]+a["depth"]-a["affect"]-a["commercial_drive"]

def load():
    recs=[]
    for l in open(f"{NAS}/detector_scored.jsonl"):
        try:
            r=json.loads(l)
            if "axes" in r and r.get("inst") in T0: recs.append(r)
        except Exception: pass
    # reuse BoE scored from Experiment B (has bank/year/month)
    try:
        for l in open(f"{NAS}/boe_scored.jsonl"):
            r=json.loads(l)
            if "axes" not in r: continue
            y=int(r.get("year",0)); m=int(r.get("month",0) or 0)
            if 2019<=y<=2023 and m>0:
                recs.append({"inst":"bank of england","year":y,"month":m,"axes":r["axes"]})
    except FileNotFoundError: pass
    return recs

def dist(r):
    ty,tm=T0[r["inst"]]; return (r["year"]-ty)*12+(int(r["month"] or 0)-tm)

# signed 6-month bins relative to t0
BINS=[(-30,-18,"pre  [-30,-18)"),(-18,-12,"pre  [-18,-12)"),(-12,-6,"run-up [-12,-6)"),
      (-6,0,"eve   [-6,0)"),(0,6,"break [0,+6)"),(6,12,"post  [+6,+12)"),(12,24,"post  [+12,+24)")]
def binlabel(d):
    for lo,hi,lab in BINS:
        if lo<=d<hi: return lab
    return None

def agg(rows):
    out={}
    for a in AXES+["cred"]:
        vals=[cred_index(r["axes"]) if a=="cred" else r["axes"][a] for r in rows]
        out[a]=(st.mean(vals), st.pstdev(vals) if len(vals)>1 else 0.0)
    return out

def welch(a,b):
    if len(a)<2 or len(b)<2: return float("nan"),float("nan")
    ma,mb=st.mean(a),st.mean(b); va,vb=st.variance(a),st.variance(b); na,nb=len(a),len(b)
    se=math.sqrt(va/na+vb/nb)
    if se==0: return 0.0,1.0
    t=(ma-mb)/se
    df=(va/na+vb/nb)**2/((va/na)**2/(na-1)+(vb/nb)**2/(nb-1))
    # two-sided p via survival of |t| under normal approx (df large enough here)
    z=abs(t); p=math.erfc(z/math.sqrt(2))
    return t,p

def main():
    recs=load()
    print("="*78); print("CREDIBILITY DETECTOR — re-anchored on the 2021-2022 transitory-inflation walk-back")
    print("="*78)
    byinst=collections.defaultdict(list)
    for r in recs: byinst[r["inst"]].append(r)
    for inst in ["federal reserve","european central bank","bank of england","reserve bank of australia"]:
        rows=byinst.get(inst,[])
        if not rows: continue
        ty,tm=T0[inst]
        print(f"\n{'-'*78}\n{inst.upper()}   t0 = {ty}-{tm:02d}   n={len(rows)}")
        binned=collections.defaultdict(list)
        for r in rows:
            lab=binlabel(dist(r))
            if lab: binned[lab].append(r)
        print(f"  {'bin':16s} {'n':>3} {'rigour':>7} {'candour':>7} {'affect':>7} {'comm':>6} {'credIdx':>8}")
        for lo,hi,lab in BINS:
            g=binned.get(lab,[])
            if not g: continue
            a=agg(g)
            print(f"  {lab:16s} {len(g):>3} {a['rigour'][0]:>7.3f} {a['candour'][0]:>7.3f} "
                  f"{a['affect'][0]:>7.3f} {a['commercial_drive'][0]:>6.3f} {a['cred'][0]:>8.3f}")
        # baseline = everything before -6 months; eve+break = [-6,+6); test degradation
        base=[r for r in rows if dist(r)<-6]
        eve =[r for r in rows if -6<=dist(r)<0]
        brk =[r for r in rows if 0<=dist(r)<6]
        both=[r for r in rows if -6<=dist(r)<6]
        if len(base)>=5 and len(both)>=5:
            print(f"  baseline (d<-6m) n={len(base)}  vs  eve+break [-6,+6) n={len(both)}:")
            for a in ["candour","affect","rigour","commercial_drive"]:
                bt=welch([r["axes"][a] for r in both],[r["axes"][a] for r in base])
                print(f"     {a:16s} base {st.mean([r['axes'][a] for r in base]):.3f}  "
                      f"window {st.mean([r['axes'][a] for r in both]):.3f}  t={bt[0]:+.2f} p={bt[1]:.3f}")
            ct=welch([cred_index(r["axes"]) for r in both],[cred_index(r["axes"]) for r in base])
            print(f"     {'cred_index':16s} base {st.mean([cred_index(r['axes']) for r in base]):+.3f}  "
                  f"window {st.mean([cred_index(r['axes']) for r in both]):+.3f}  t={ct[0]:+.2f} p={ct[1]:.3f}")

    # ---- POOLED within-institution event study (each institution centred on its own t0, z-scored to own baseline) ----
    print(f"\n{'='*78}\nPOOLED (each institution z-scored to its own d<-6m baseline, then stacked)\n{'='*78}")
    pooled=collections.defaultdict(list)
    for inst,rows in byinst.items():
        base=[r for r in rows if dist(r)<-6]
        if len(base)<5: continue
        mu={a:st.mean([r["axes"][a] for r in base]) for a in AXES}
        sd={a:(st.pstdev([r["axes"][a] for r in base]) or 1e-9) for a in AXES}
        muc=st.mean([cred_index(r["axes"]) for r in base]); sdc=st.pstdev([cred_index(r["axes"]) for r in base]) or 1e-9
        for r in rows:
            lab=binlabel(dist(r))
            if not lab: continue
            z={a:(r["axes"][a]-mu[a])/sd[a] for a in AXES}
            z["cred"]=(cred_index(r["axes"])-muc)/sdc
            pooled[lab].append(z)
    print(f"  {'bin':16s} {'n':>3} {'candour z':>9} {'affect z':>9} {'rigour z':>9} {'cred z':>8}")
    for lo,hi,lab in BINS:
        g=pooled.get(lab,[])
        if not g: continue
        print(f"  {lab:16s} {len(g):>3} {st.mean([x['candour'] for x in g]):>+9.3f} "
              f"{st.mean([x['affect'] for x in g]):>+9.3f} {st.mean([x['rigour'] for x in g]):>+9.3f} "
              f"{st.mean([x['cred'] for x in g]):>+8.3f}")
    # pooled test: eve+break vs baseline (baseline z==0 by construction, so test window bins vs 0)
    for lab in ["eve   [-6,0)","break [0,+6)"]:
        g=pooled.get(lab,[])
        if len(g)<5: continue
        for a in ["candour","affect","cred"]:
            vals=[x[a] for x in g]; m=st.mean(vals); se=(st.pstdev(vals) or 1e-9)/math.sqrt(len(vals))
            z=m/se; p=math.erfc(abs(z)/math.sqrt(2))
            print(f"  [{lab.strip()}] {a:10s} mean z {m:+.3f}  vs baseline 0  z={z:+.2f} p={p:.3f}")

if __name__=="__main__":
    main()

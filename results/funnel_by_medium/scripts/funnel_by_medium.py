#!/usr/bin/env python3
"""funnel_by_medium.py -- is the persuasion funnel a law of persuasion or a law of format?

The programme headline (Paper 4B) is "manner earns attention, matter earns conviction",
measured mostly on short form. Question tested here: on a LONG form medium, does matter
start earning attention too? If the attention/conviction split is conditional on text
LENGTH, the funnel is a law of FORMAT, not of persuasion.

PURE ANALYSIS on already-scored outcome corpora. No new character scoring. No :8301/:8288.

matter = mean(rigour, depth). manner = mean(affect, stance, register). (task definition)
Each corpus has an 8-axis character score, one real human outcome, and a word count.
Per corpus we standardise matter, manner and log10(word count), then model the outcome on
   matter + manner + len + matter*len + manner*len
with within-group demeaning to hold the topic/ask/persuadee fixed where the design gives it,
and cluster-robust standard errors by that group. y is standardised too, so every beta is in
"outcome SD per predictor SD" and is comparable across the five media.

Corpora (short -> long):
  upworthy  headline CTR (clicks/impressions), randomised A/B within a test   ATTENTION  SHORT
  petitions log10(1+signatures), UK gov petitions, within same-ask cluster    ATTENTION  short-mid
  cmv       delta won (0/1), Reddit ChangeMyView matched pairs by OP post      CONVICTION long
  se        accepted (0/1), StackExchange answers matched by question          CONVICTION long
  oldbailey guilty verdict (0/1), Old Bailey trial accounts                    CONVICTION very long
"""
import os, json, math
import numpy as np
from collections import defaultdict
from scipy import stats

AXES   = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
MATTER = ["rigour","depth"]
MANNER = ["affect","stance","register"]
NASC   = "/mnt/nas/kronaxis/corpora"
KCDW   = os.path.expanduser("~/kc-dwpaper")

def matter_of(ch):  return float(np.mean([ch[a] for a in MATTER]))
def manner_of(ch):  return float(np.mean([ch[a] for a in MANNER]))
def wc(t):          return len(t.split()) if isinstance(t,str) else 0

# ---------------------------------------------------------------- loaders
def load_upworthy():
    sc={}
    for f in (f"{KCDW}/upworthy_scores_full.jsonl", f"{KCDW}/upworthy_scores.jsonl"):
        if os.path.exists(f):
            for line in open(f):
                try:
                    r=json.loads(line); sc[r["headline"]]=r["scores"]
                except Exception: pass
    agg=defaultdict(lambda:[0.0,0.0])
    for line in open(f"{KCDW}/upworthy.jsonl"):
        try: r=json.loads(line)
        except Exception: continue
        h=r.get("headline")
        if h not in sc: continue
        a=agg[(r["test_id"],h)]; a[0]+=float(r.get("impressions",0)); a[1]+=float(r.get("clicks",0))
    rows=[]
    for (t,h),(imp,clk) in agg.items():
        if imp<=0: continue
        ch=sc[h]
        if not all(x in ch for x in AXES): continue
        rows.append(dict(group=t, y=clk/imp, matter=matter_of(ch), manner=manner_of(ch),
                         wc=max(1,wc(h)), w=imp))
    return rows

def load_paired(scores_path, utter_path):
    """cmv / se: matched pairs of arguments, success 0/1, group = root (the OP/question)."""
    txt={}
    for l in open(utter_path):
        try: r=json.loads(l)
        except Exception: continue
        i=r.get("id"); t=r.get("text")
        if i is not None and isinstance(t,str): txt[i]=wc(t)
    rows=[]
    for l in open(scores_path):
        try: r=json.loads(l)
        except Exception: continue
        if r.get("kind")!="arg" or r.get("skip"): continue
        ch=r.get("char")
        if not isinstance(ch,dict) or not all(a in ch for a in AXES): continue
        n=txt.get(r.get("id"))
        if not n or n<1: continue
        root=r.get("root")
        if root is None: continue
        rows.append(dict(group=root, y=float(r.get("success",0)), matter=matter_of(ch),
                         manner=manner_of(ch), wc=n, w=1.0))
    return rows

def load_petitions():
    txt={}
    for l in open(f"{NASC}/uk_petitions/petitions.jsonl"):
        try: r=json.loads(l)
        except Exception: continue
        i=r.get("id")
        if i is None: continue
        body=" ".join(str(r.get(k,"") or "") for k in ("action","background","additional_details"))
        yr=None
        ca=r.get("created_at")
        if isinstance(ca,str) and len(ca)>=4:
            try: yr=int(ca[:4])
            except Exception: yr=None
        txt[i]=(wc(body), yr)
    rows=[]
    for l in open(f"{NASC}/uk_petitions/cluster_members_scored.jsonl"):
        try: r=json.loads(l)
        except Exception: continue
        ch=r.get("char")
        if not isinstance(ch,dict) or not all(a in ch for a in AXES): continue
        if not r.get("opened_at"): continue                       # only petitions that opened for signing
        sig=r.get("signature_count")
        if sig is None: continue
        n,yr=txt.get(r.get("id"),(0,None))
        if n<1: continue
        rows.append(dict(group=r.get("cluster_id"), y=math.log10(1.0+float(sig)),
                         matter=matter_of(ch), manner=manner_of(ch), wc=n, w=1.0, year=yr))
    return rows

def load_oldbailey():
    rows=[]
    for l in open(f"{NASC}/oldbailey/oldbailey_scored.jsonl"):
        try: r=json.loads(l)
        except Exception: continue
        ch=r.get("char")
        if not isinstance(ch,dict) or not all(a in ch for a in AXES): continue
        n=r.get("nwords"); v=r.get("verdict")
        if not n or n<1 or v is None: continue
        rows.append(dict(group=r.get("offence","?"), y=float(v), matter=matter_of(ch),
                         manner=manner_of(ch), wc=int(n), w=1.0, offence=r.get("offence","?"),
                         npers=float(r.get("npers",0) or 0)))
    return rows

# ---------------------------------------------------------------- regression
def zc(a):
    a=np.asarray(a,float); s=a.std()
    return (a-a.mean())/s if s>1e-12 else a-a.mean()

def demean_within(vals, groups):
    vals=np.asarray(vals,float); out=vals.copy()
    idx=defaultdict(list)
    for i,g in enumerate(groups): idx[g].append(i)
    for g,ix in idx.items():
        ix=np.array(ix); out[ix]=vals[ix]-vals[ix].mean()
    return out

def cluster_robust(X, y, groups):
    XtXi=np.linalg.pinv(X.T@X); beta=XtXi@(X.T@y); u=y-X@beta
    K=X.shape[1]; N=X.shape[0]; meat=np.zeros((K,K))
    ug=np.unique(groups); G=len(ug)
    for g in ug:
        ix=np.where(groups==g)[0]; s=X[ix].T@u[ix]; meat+=np.outer(s,s)
    dof=(G/max(1,G-1))*((N-1)/max(1,N-K))
    V=dof*(XtXi@meat@XtXi); se=np.sqrt(np.clip(np.diag(V),0,None))
    t=beta/(se+1e-30); p=2*stats.t.sf(np.abs(t),df=max(1,G-1))
    return beta,se,t,p,G

def stars(p): return "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else ""

def analyse(name, rows, kind, use_group=True, extra_controls=()):
    """kind: 'attention' or 'conviction' (label only). Returns dict of results."""
    if len(rows)<40:
        print(f"\n[{name}] only {len(rows)} usable rows -- skip"); return None
    groups=np.array([r["group"] for r in rows])
    y   =np.array([r["y"] for r in rows],float)
    matter=np.array([r["matter"] for r in rows],float)
    manner=np.array([r["manner"] for r in rows],float)
    logwc =np.log10(np.array([r["wc"] for r in rows],float))
    wcv   =np.array([r["wc"] for r in rows],float)

    if use_group:
        matter=demean_within(matter,groups); manner=demean_within(manner,groups)
        logwc =demean_within(logwc,groups);  y=demean_within(y,groups)
    # extra numeric controls (residualise y AND predictors on them is overkill; add as regressors)
    ctrl_cols=[]
    for cname,arr in extra_controls:
        ctrl_cols.append((cname, zc(np.asarray(arr,float))))

    M=zc(matter); N=zc(manner); L=zc(logwc); Y=zc(y)
    ML=zc(M*L); NL=zc(N*L)

    # main-effects-only model (clean cross-corpus attention pull)
    Xm=np.column_stack([M,N,L]+[c for _,c in ctrl_cols])
    bm,sem,tm,pm,G=cluster_robust(Xm,Y,groups)
    main={"matter":(bm[0],pm[0]),"manner":(bm[1],pm[1]),"len":(bm[2],pm[2])}

    # full model with length interactions
    Xf=np.column_stack([M,N,L,ML,NL]+[c for _,c in ctrl_cols])
    bf,sef,tf,pf,G=cluster_robust(Xf,Y,groups)
    names=["matter","manner","len","matter_x_len","manner_x_len"]+[cn for cn,_ in ctrl_cols]
    full={names[i]:(bf[i],sef[i],pf[i]) for i in range(len(names))}

    medwc=float(np.median(wcv)); n=len(rows)
    print(f"\n{'='*82}\n{name}  ({kind})   n={n:,}  groups={G:,}  medianWC={medwc:.0f}  "
          f"[{np.percentile(wcv,10):.0f}..{np.percentile(wcv,90):.0f} p10-p90]")
    print(f"  MAIN-effects   matter beta={bm[0]:+.3f}{stars(pm[0]):3s}  manner beta={bm[1]:+.3f}{stars(pm[1]):3s}  len beta={bm[2]:+.3f}{stars(pm[2]):3s}")
    print(f"  FULL(+len int) matter={bf[0]:+.3f}{stars(pf[0]):3s} manner={bf[1]:+.3f}{stars(pf[1]):3s} "
          f"len={bf[2]:+.3f}{stars(pf[2]):3s}  matterXlen={bf[3]:+.3f}{stars(pf[3]):3s}  mannerXlen={bf[4]:+.3f}{stars(pf[4]):3s}")
    return dict(name=name,kind=kind,n=n,G=G,medwc=medwc,
                p10=float(np.percentile(wcv,10)),p90=float(np.percentile(wcv,90)),
                main=main,full=full)

def main():
    print("funnel_by_medium -- matter=mean(rigour,depth)  manner=mean(affect,stance,register)")
    print("all betas standardised: outcome SD per predictor SD; y & predictors within-group demeaned where a design group exists")
    res=[]
    up=load_upworthy();     res.append(analyse("upworthy",  up, "attention",  use_group=True))
    pe=load_petitions()
    yrs=[r.get("year") or 0 for r in pe]
    res.append(analyse("petitions", pe, "attention",  use_group=True,
                       extra_controls=[("year", yrs)]))
    cmv=load_paired(f"{NASC}/cmv_winning_args/cmv_scores.jsonl",
                    f"{NASC}/cmv_winning_args/winning-args-corpus/utterances.jsonl")
    res.append(analyse("cmv",       cmv,"conviction", use_group=True))
    se=load_paired(f"{NASC}/stackexchange_args/se_scores.jsonl",
                   f"{NASC}/stackexchange_args/combined/winning-args-corpus/utterances.jsonl")
    res.append(analyse("se",        se, "conviction", use_group=True))
    ob=load_oldbailey()
    npers=[r["npers"] for r in ob]
    res.append(analyse("oldbailey", ob, "conviction", use_group=True,
                       extra_controls=[("npers", npers)]))

    res=[r for r in res if r]
    res.sort(key=lambda r:r["medwc"])
    # ---- summary tables
    print(f"\n\n{'#'*82}\nSUMMARY -- corpora ordered short -> long\n{'#'*82}")
    print("\nMAIN EFFECTS (no interaction) -- does matter's pull on the outcome rise with medium length?")
    print(f"  {'corpus':10s}{'kind':11s}{'medWC':>7s}{'n':>8s}{'matter':>10s}{'manner':>10s}")
    for r in res:
        bm,pm=r["main"]["matter"]; bn,pn=r["main"]["manner"]
        print(f"  {r['name']:10s}{r['kind']:11s}{r['medwc']:7.0f}{r['n']:8,d}"
              f"{bm:+8.3f}{stars(pm):2s}{bn:+8.3f}{stars(pn):2s}")
    print("\nLENGTH INTERACTIONS (within corpus) -- matterXlen>0 & mannerXlen<0 => split is length-driven")
    print(f"  {'corpus':10s}{'medWC':>7s}{'matterXlen':>12s}{'mannerXlen':>12s}")
    for r in res:
        bm,_,pm=r["full"]["matter_x_len"]; bn,_,pn=r["full"]["manner_x_len"]
        print(f"  {r['name']:10s}{r['medwc']:7.0f}{bm:+10.3f}{stars(pm):2s}{bn:+10.3f}{stars(pn):2s}")

    import pickle
    with open(os.path.expanduser("~/funnel_by_medium_res.pkl"),"wb") as f: pickle.dump(res,f)
    print("\n[done]  results pickled to ~/funnel_by_medium_res.pkl")

if __name__=="__main__":
    main()

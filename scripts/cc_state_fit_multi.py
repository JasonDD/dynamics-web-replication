#!/usr/bin/env python3
"""cc_state_fit_multi.py — the EQUATION OF STATE, term by term.

Extends the genre location-vs-rotation test (cc_genre_state_fit.py) to the other state
variables (the Five Ws) on the cross-site corpus. For each state variable S we ask the
SAME question the genre test asked: does S enter the person->character coupling as a
LOCATION (an intercept offset, the field is affine in S) or as a ROTATION (it modulates
the disposition->character slope, a genuine interaction)?

Model comparison, held-out RMSE, folds STRATIFIED BY STATE GROUP (every group in training,
so B and A can diverge on held-out rows of known groups — the genre test's catch #4 fix):
  Null : C ~ P                         (coupling only, no state)
  B    : C ~ P + S_fixed_effects       (S shifts the LEVEL = location, affine)
  A    : C ~ P, slope varies by S       (S ROTATES the coupling = interaction)

P (disposition) = PERSON-mean plasticity (DeYoung Big-Two: sociability+novelty from D8),
computed per ident over that person's rows, so P is not read from the identical text as C
(reduces the shared-text circularity). C = per-row matter/manner PC1 (canonical ruler).
Aggregate, no keys, no names. INTERNAL HOLD corpus, analysis only, no scoring.
"""
import os, json, numpy as np, psycopg2
import statsmodels.formula.api as smf
import statsmodels.api as sm
import pandas as pd
from datetime import datetime

CHAR = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
PLAS = ["sociability","novelty"]
FLOOR = int(os.environ.get("FLOOR","300"))          # min rows per state group
CAP = int(os.environ.get("CAP","50000"))            # subsample rows per test (mixedlm tractability)
PW = [l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
DSN=f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"
def z(a): a=np.asarray(a,float); return (a-a.mean())/(a.std()+1e-9)
def obj(x): return x if isinstance(x,dict) else (json.loads(x) if x else None)

db=psycopg2.connect(DSN); cur=db.cursor()
cur.execute(f"SELECT {','.join(CHAR)} FROM the internal reference table")
allc=np.array([[float(v) for v in r] for r in cur.fetchall()],float)
MEAN=allc.mean(0); STD=allc.std(0)+1e-9
_,_,Vt=np.linalg.svd((allc-MEAN)/STD,full_matrices=False); PC1=Vt[0]
if (PC1[CHAR.index("rigour")]+PC1[CHAR.index("depth")])<0: PC1=-PC1
print(f"[fit] PC1 loadings: "+", ".join(f"{a}={l:+.2f}" for a,l in zip(CHAR,PC1)),flush=True)

def era_of(pd_str):
    if not pd_str: return None
    for fmt in ("%Y-%m-%d","%Y-%m-%dT%H:%M:%S","%Y/%m/%d","%Y"):
        try: return str(datetime.strptime(pd_str[:len(fmt)+2].strip(),fmt).year//5*5)
        except Exception: pass
    if len(pd_str)>=4 and pd_str[:4].isdigit(): return str(int(pd_str[:4])//5*5)
    return None

def host_tld(dom):
    if not dom: return None
    t=dom.rsplit(".",1)[-1].lower()
    return t if len(t)<=6 else None

print("[fit] pulling cross-site scored rows ...",flush=True)
cur.execute("""SELECT ident,domain,topic,post_date,lang,disp_d8,char_dweb
               FROM the internal cross site corpus
               WHERE disp_d8 IS NOT NULL AND char_dweb IS NOT NULL""")
recs=[]
for ident,dom,topic,pdate,lang,dd,cw in cur.fetchall():
    dd=obj(dd); cw=obj(cw)
    if not isinstance(dd,dict) or not isinstance(cw,dict): continue
    if any(a not in cw for a in CHAR) or any(k not in dd for k in PLAS): continue
    plas=sum(float(dd[k]) for k in PLAS)
    mm=float(((np.array([float(cw[a]) for a in CHAR])-MEAN)/STD)@PC1)
    recs.append((ident,dom,topic,era_of(pdate),lang,plas,mm))
df=pd.DataFrame(recs,columns=["ident","domain","topic","era","lang","plas","mm"])
print(f"[fit] {len(df):,} scored rows, {df['ident'].nunique():,} persons",flush=True)

# person-mean plasticity (disposition read separated from the row's own character)
pm=df.groupby("ident")["plas"].mean().rename("P"); df=df.join(pm,on="ident")
df["disp"]=z(df["P"]); df["c"]=z(df["mm"])
df["tld"]=df["domain"].map(host_tld)

def rmse(a,b): return float(np.sqrt(np.mean((np.asarray(a)-np.asarray(b))**2)))

def test_W(colname, label):
    print(f"[run] {label} ({colname}) starting ...",flush=True)
    d=df[df[colname].notna()].copy()
    vc=d[colname].value_counts(); keep=vc[vc>=FLOOR].index
    d=d[d[colname].isin(keep)].reset_index(drop=True)
    if len(d)>CAP:                                   # subsample for mixedlm tractability, keep every group
        d=d.groupby(colname,group_keys=False).apply(lambda g: g.sample(min(len(g),max(FLOOR,int(CAP*len(g)/len(d)))),random_state=7)).reset_index(drop=True)
    if d[colname].nunique()<3 or len(d)<3*FLOOR:
        print(f"\n=== {label} ({colname}) : SKIP — only {d[colname].nunique()} groups >= FLOOR, n={len(d)}",flush=True); return None
    # PERSON-GROUPED folds: every one of a person's rows shares a fold, so no person leaks
    # between train and test (disposition is a person-level quantity). Assigned by hashing ident,
    # so each state group, spanning many persons, still appears in every training fold.
    import hashlib
    idx=np.arange(len(d))
    fold=d["ident"].map(lambda x:int(hashlib.md5(str(x).encode()).hexdigest(),16)%5).values
    # guard: require every kept group present in >=4 of the 5 folds (else it cannot be held out fairly)
    gf=d.groupby(colname)["ident"].apply(lambda s:len(set(int(hashlib.md5(str(x).encode()).hexdigest(),16)%5 for x in s)))
    ok=set(gf[gf>=4].index); d=d[d[colname].isin(ok)].reset_index(drop=True)
    if d[colname].nunique()<3 or len(d)<3*FLOOR:
        print(f"[run] {label}: after person-fold guard only {d[colname].nunique()} groups, SKIP",flush=True); return None
    idx=np.arange(len(d))
    fold=d["ident"].map(lambda x:int(hashlib.md5(str(x).encode()).hexdigest(),16)%5).values
    y=d["c"].values
    groups=sorted(d[colname].unique())[1:]                         # drop-first dummy base
    D=np.column_stack([ (d[colname].values==g).astype(float) for g in groups ]) if groups else np.zeros((len(d),0))
    dispv=d["disp"].values.reshape(-1,1)
    Xn=np.column_stack([np.ones(len(d)),dispv])                     # Null: 1 + disp
    Xb=np.column_stack([Xn,D])                                      # B: + state FE (location)
    Xa=np.column_stack([Xb,D*dispv])                               # A: + disp x state (rotation)
    pN,pB,pA=np.zeros(len(d)),np.zeros(len(d)),np.zeros(len(d))
    for f in range(5):
        tr=fold!=f; te=fold==f
        for X,pred in ((Xn,pN),(Xb,pB),(Xa,pA)):
            beta,_,_,_=np.linalg.lstsq(X[tr],y[tr],rcond=None)
            pred[te]=X[te]@beta
    rN,rB,rA=rmse(pN,y),rmse(pB,y),rmse(pA,y)
    if rA<rB-0.002 and rB<rN-0.002: read="ROTATION (A<B<Null): S modulates the coupling"
    elif rB<rN-0.002 and abs(rA-rB)<=0.002: read="LOCATION (B<Null, A~B): affine offset, coupling invariant"
    elif abs(rB-rN)<=0.002: read="ABSORBED (A~B~Null): no state term needed"
    else: read="mixed"
    print(f"\n=== {label} ({colname}): {d[colname].nunique()} groups >=FLOOR, n={len(d):,} ===",flush=True)
    print(f"    held-out RMSE  Null={rN:.4f}  B(location)={rB:.4f}  A(rotation)={rA:.4f}  -> {read}",flush=True)
    return (label,d[colname].nunique(),len(d),rN,rB,rA,read)

out=[]
for col,lab in [("topic","WHAT / topic"),("tld","WHERE / site kind (tld)"),("era","WHEN / era (5yr)"),("lang","language")]:
    try:
        r=test_W(col,lab)
        if r: out.append(r)
    except Exception as e:
        import traceback; print(f"[ERROR] {lab}: {e}\n{traceback.format_exc()}",flush=True)

print("\n================= EQUATION OF STATE: per-W verdicts =================",flush=True)
print(f"  {'state var':24}{'groups':>7}{'n':>9}{'Null':>9}{'B loc':>9}{'A rot':>9}   read",flush=True)
for lab,ng,n,rN,rB,rA,read in out:
    print(f"  {lab:24}{ng:7d}{n:9d}{rN:9.4f}{rB:9.4f}{rA:9.4f}   {read.split(':')[0]}",flush=True)
print("  (genre, tested separately: LOCATION — affine, coupling invariant; weak rotation unresolved on the heavier model)",flush=True)
print("====================================================================",flush=True)

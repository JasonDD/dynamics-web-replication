#!/usr/bin/env python3
"""cc_state_who.py — the WHO (audience) state term for the equation of state.

A reply's audience is the author of the parent comment. So each reply carries the WRITER
disposition (P), the AUDIENCE disposition (A, the parent author's), and the produced
CHARACTER (C). We ask, as for the other state variables: does audience enter as a LOCATION
(an additive shift of C, a translation) or a ROTATION (it modulates the writer coupling)?

Audience A is continuous (the parent author's plasticity), so the three models are:
  Null : C ~ P
  B    : C ~ P + A          (audience shifts the level = location)
  Arot : C ~ P + A + P:A    (audience modulates the writer->character slope = rotation)
Person grouped cross validation by WRITER author (no writer leaks). Both P and A are
person-mean plasticity over an author's own posts, so neither is read from the reply's own
text. Also fits the audience displacement direction (regress the 8 axes on A) and its
alignment with matter/manner, to see if WHO adds a new rank direction or stays in plane.
Aggregate only, no names.
"""
import os, json, numpy as np, psycopg2, hashlib
CHAR=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
PLAS=["sociability","novelty"]
DISP="disp_d8_behav_27b"
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
db=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"); c=db.cursor()
def obj(x): return x if isinstance(x,dict) else (json.loads(x) if x else None)
c.execute(f"SELECT {','.join(CHAR)} FROM the internal reference table")
A0=np.array([[float(v) for v in r] for r in c.fetchall()],float); MEAN=A0.mean(0); STD=A0.std(0)+1e-9
_,_,Vt=np.linalg.svd((A0-MEAN)/STD,full_matrices=False); PC1=Vt[0]
if PC1[0]+PC1[1]<0: PC1=-PC1
print(f"[who] PC1 loaded",flush=True)

print("[who] pulling reddit_wide (id, author, parent_id, char, disp) ...",flush=True)
c.execute(f"SELECT id,author,parent_id,char,{DISP} FROM the internal Reddit corpus WHERE char IS NOT NULL AND {DISP} IS NOT NULL AND author IS NOT NULL")
rows=c.fetchall()
print(f"[who] {len(rows):,} scored comments",flush=True)
id2auth={}; auth_plas={}; auth_n={}; post=[]
for cid,auth,par,ch,dp in rows:
    ch=obj(ch); dp=obj(dp)
    if not ch or not dp or any(a not in ch for a in CHAR) or any(k not in dp for k in PLAS): continue
    pl=sum(float(dp[k]) for k in PLAS)
    mm=float(((np.array([float(ch[a]) for a in CHAR])-MEAN)/STD)@PC1)
    ch8=(np.array([float(ch[a]) for a in CHAR])-MEAN)/STD
    id2auth[cid]=auth; auth_plas[auth]=auth_plas.get(auth,0.0)+pl; auth_n[auth]=auth_n.get(auth,0)+1
    post.append((cid,auth,par,mm,ch8))
authmean={a:auth_plas[a]/auth_n[a] for a in auth_plas}            # per-author mean plasticity
print(f"[who] {len(post):,} usable, {len(authmean):,} authors",flush=True)

# build reply rows: audience = parent author's mean plasticity
P=[];A=[];C=[];CH=[];W=[]; matched=0
for cid,auth,par,mm,ch8 in post:
    if not par or not par.startswith("t1_"): continue                # only comment-parents have an author
    pauth=id2auth.get(par[3:])
    if pauth is None or pauth not in authmean or auth not in authmean: continue
    P.append(authmean[auth]); A.append(authmean[pauth]); C.append(mm); CH.append(ch8); W.append(auth); matched+=1
print(f"[who] {matched:,} replies whose parent comment is in-table (the audience join)",flush=True)
if matched<3000: print("[who] WARNING low coverage, result underpowered",flush=True)
P=np.array(P);A=np.array(A);C=np.array(C);CH=np.array(CH);W=np.array(W)
Pz=(P-P.mean())/(P.std()+1e-9); Az=(A-A.mean())/(A.std()+1e-9); Cz=(C-C.mean())/(C.std()+1e-9)

# person-grouped folds by WRITER
fold=np.array([int(hashlib.md5(w.encode()).hexdigest(),16)%5 for w in W])
def rmse(a,b): return float(np.sqrt(np.mean((a-b)**2)))
one=np.ones(len(Cz))
Xn=np.column_stack([one,Pz]); Xb=np.column_stack([one,Pz,Az]); Xr=np.column_stack([one,Pz,Az,Pz*Az])
pN,pB,pR=np.zeros(len(Cz)),np.zeros(len(Cz)),np.zeros(len(Cz))
for f in range(5):
    tr=fold!=f; te=fold==f
    for X,pr in ((Xn,pN),(Xb,pB),(Xr,pR)):
        be,_,_,_=np.linalg.lstsq(X[tr],Cz[tr],rcond=None); pr[te]=X[te]@be
rN,rB,rR=rmse(pN,Cz),rmse(pB,Cz),rmse(pR,Cz)
print(f"\n[who] held-out RMSE  Null(C~P)={rN:.4f}  B(+audience,location)={rB:.4f}  Arot(+P:A,rotation)={rR:.4f}",flush=True)
if rR<rB-0.002 and rB<rN-0.002: verdict="ROTATION: audience modulates the writer coupling"
elif rB<rN-0.002 and abs(rR-rB)<=0.002: verdict="LOCATION: audience is an affine offset, coupling invariant"
elif abs(rB-rN)<=0.002: verdict="ABSORBED / no detectable contribution"
else: verdict="mixed"
print(f"[who] VERDICT: {verdict}",flush=True)

# audience displacement direction: regress each of the 8 axes on Az (the WHO offset in char space)
beta=np.array([np.linalg.lstsq(np.column_stack([one,Az]),CH[:,k],rcond=None)[0][1] for k in range(8)])
bn=beta/ (np.linalg.norm(beta)+1e-12); cosPC1=abs(float(bn@PC1))
print(f"\n[who] audience displacement direction |.|matter/manner| = {cosPC1:.2f}   (near 1 => same plane as the other terms => rank likely holds ~2)",flush=True)
print(f"[who] direction: "+", ".join(f"{a}={bn[i]:+.2f}" for i,a in enumerate(CHAR)),flush=True)

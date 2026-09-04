#!/usr/bin/env python3
"""cc_state_closure.py — the CLOSURE probe (aggregate level).

At the community-aggregate regime where the person->content coupling is strong (~0.74),
fit the identified affine model C = g(P) + genre, then ask whether the between-community
RESIDUAL variance exceeds the independently estimated SAMPLING FLOOR (each community's own
within-variance divided by its post count). Residual ~ floor => no systematic structure left
beyond disposition + genre at this resolution (S closed at the tested support). Residual >>
floor => systematic structure remains, and the grouping that carries it names the next term.

Disjoint halves (seed 5, FLOOR 150) as in cc_genre_state_fit.py: P from half A, C from half B,
so disposition and character are not read from the same posts. Aggregate only, no keys/names.
"""
import os, json, numpy as np, psycopg2
CHAR=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
PLAS=["sociability","novelty"]
DISP_COL=os.environ.get("DISP_COL","disp_d8_behav_27b")
FLOOR=int(os.environ.get("FLOOR","150"))
GENRE_JSON=os.environ.get("GENRE_JSON","/home/jason/projects/kronaxis/truthometer/results/prereg_genre_PF-4B/genre_assign_400_FROZEN.json")
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
DSN=f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"
db=psycopg2.connect(DSN); c=db.cursor()
c.execute(f"SELECT {','.join(CHAR)} FROM the internal reference table")
allc=np.array([[float(x) for x in r] for r in c.fetchall()],float)
MEAN=allc.mean(0); STD=allc.std(0)+1e-9
_,_,Vt=np.linalg.svd((allc-MEAN)/STD,full_matrices=False); PC1=Vt[0]
if (PC1[CHAR.index("rigour")]+PC1[CHAR.index("depth")])<0: PC1=-PC1
print(f"[closure] PC1 rigour={PC1[0]:+.2f} depth={PC1[1]:+.2f} affect={PC1[4]:+.2f}",flush=True)

c.execute(f"SELECT subreddit,char,{DISP_COL} FROM the internal Reddit corpus WHERE char IS NOT NULL AND {DISP_COL} IS NOT NULL")
by={}
for sub,ch,dp in c.fetchall():
    ch=ch if isinstance(ch,dict) else json.loads(ch); dp=dp if isinstance(dp,dict) else json.loads(dp)
    by.setdefault(sub,[]).append(([float(ch[a]) for a in CHAR],sum(float(dp.get(k,0.5)) for k in PLAS)))
print(f"[closure] {len(by)} communities pulled",flush=True)
rng=np.random.default_rng(5)
sub=[];plas=[];cmean=[];cvar=[];nB=[]
for s,rr in by.items():
    if len(rr)<FLOOR: continue
    p=rng.permutation(len(rr)); h=len(rr)//2
    A=[rr[i] for i in p[:h]]; B=[rr[i] for i in p[h:]]
    pl=np.mean([x[1] for x in A])                                     # plasticity, half A
    mmB=np.array([float(((np.array(x[0])-MEAN)/STD)@PC1) for x in B]) # matter/manner per post, half B
    sub.append(s); plas.append(pl); cmean.append(mmB.mean()); cvar.append(mmB.var(ddof=1)); nB.append(len(mmB))
sub=np.array(sub); plas=np.array(plas); cmean=np.array(cmean); cvar=np.array(cvar); nB=np.array(nB,float)
gmap=json.load(open(GENRE_JSON)); genre=np.array([gmap.get(s) for s in sub])
keep=np.array([g is not None and g!="other_misc" for g in genre])
sub,plas,cmean,cvar,nB,genre=sub[keep],plas[keep],cmean[keep],cvar[keep],nB[keep],genre[keep]
print(f"[closure] {len(sub)} communities pass FLOOR={FLOOR}, {len(set(genre))} genres",flush=True)

# z-scale character to community SD so residual and floor share units
csd=cmean.std()+1e-9; C=(cmean-cmean.mean())/csd
disp=(plas-plas.mean())/(plas.std()+1e-9)
floor_c=cvar/(csd**2)/nB                                             # sampling variance of each community's C, in z units
FLOORv=float(floor_c.mean())

def fitrmse(X):
    beta,_,_,_=np.linalg.lstsq(X,C,rcond=None); resid=C-X@beta
    return beta,resid,float(resid.var(ddof=1))
one=np.ones(len(C))
_,rN,vN=fitrmse(np.column_stack([one,disp]))                        # g(P) only
G=np.array(sorted(set(genre)))[1:]; D=np.column_stack([(genre==g).astype(float) for g in G])
_,rM,vM=fitrmse(np.column_stack([one,disp,D]))                      # g(P) + genre
totvar=float(C.var(ddof=1))
print(f"\n[closure] between-community variance of C (z) = {totvar:.4f}")
print(f"[closure] residual var after g(P)          = {vN:.4f}   (coupling explains {100*(1-vN/totvar):.1f}%)")
print(f"[closure] residual var after g(P)+genre    = {vM:.4f}   (+genre explains a further {100*(vN-vM)/totvar:.1f}%)")
print(f"[closure] SAMPLING FLOOR (mean within/n, z) = {FLOORv:.4f}   [independently estimated]")
ratio=vM/FLOORv
print(f"\n[closure] CLOSURE RATIO = residual / floor = {vM:.4f} / {FLOORv:.4f} = {ratio:.1f}")
if ratio<=1.5: verdict="CLOSED at this resolution: residual ~ sampling floor, no systematic structure beyond g(P)+genre"
elif ratio<=4: verdict="MOSTLY CLOSED: residual modestly above floor, some structure remains"
else: verdict="OPEN: residual FAR above floor, strong systematic structure remains (a missing state term)"
print(f"[closure] VERDICT: {verdict}",flush=True)

# the search: does grouping the residual by a candidate (community size tier) overdisperse vs a random control?
size_tier=np.digitize(nB,np.quantile(nB,[0.33,0.66]))
def between_group_var(labels,resid):
    gs=[resid[labels==k] for k in np.unique(labels) if (labels==k).sum()>=5]
    gm=np.array([g.mean() for g in gs]); return float(gm.var(ddof=1))
rng2=np.random.default_rng(7); rand=rng2.integers(0,3,len(rM))
print(f"\n[search] between-group residual variance:  by SIZE tier = {between_group_var(size_tier,rM):.5f}   vs RANDOM control = {between_group_var(rand,rM):.5f}",flush=True)
print("[search] (a candidate grouping whose between-group variance exceeds the random control is a candidate missing state term)",flush=True)

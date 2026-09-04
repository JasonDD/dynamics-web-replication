#!/usr/bin/env python3
"""cc_ashlar_atlas.py -- the full Ashlar internal model: the 8x8 disposition to character coupling, surveyed.

Ashlar is the keystone, the map between a person's eight disposition axes (DYNAMICS-8) and the eight
character axes of the writing (DYNAMICS-WEB), two genuinely different objects that share only candour.
The recent equation of state work collapsed that map to a single matter against manner ruler; this
re-surveys the WHOLE internal model, every disposition axis against every character axis, so the trade secret is
measured cell by cell rather than represented by one principal slice.

Method, the same falsifiable core as the equation of state. Each person is aggregated within each room
(domain), so the room is fixed; persons in the same room are differenced, which cancels the room offset
exactly (dC = W dP, no intercept); W is the 8x8 coupling. A room block bootstrap gives a confidence
interval per cell, so the internal model reports which cells are real. Run on three reader legs to break
circularity: A both axes by the first reader, and the two cross legs where disposition and character are
read by DIFFERENT model families. The matter against manner and originality projection is reported
alongside so the internal model reconciles with the equation of state's 2x2. Aggregate, no keys, analysis only.
"""
import os, sys, json, time
import numpy as np, psycopg2
t0=time.time()
def log(*a): print(f"[{time.time()-t0:7.1f}s]", *a, flush=True)

CHAR=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
D8  =["discipline","yielding","novelty","acuity","mercuriality","impulsivity","candour","sociability"]
DISPCOL=os.environ.get("DISPCOL","disp_d8"); CHARCOL=os.environ.get("CHARCOL","char_dweb")
SAMPLE=os.environ.get("SAMPLE_TABLE",""); MINPERS=int(os.environ.get("MINPERS","5"))
PAIRCAP=int(os.environ.get("PAIRCAP","200")); NBOOT=int(os.environ.get("NBOOT","400"))
LEG=os.environ.get("LEG","A"); OUT=os.environ.get("OUT","/tmp/ashlar_atlas.json")
SEED=int(os.environ.get("SEED","20260903")); rng=np.random.default_rng(SEED)
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
db=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"); cur=db.cursor()
def obj(x): return x if isinstance(x,dict) else (json.loads(x) if x else None)

jt=f"JOIN {SAMPLE} s USING (id)" if SAMPLE else ""
log(f"pull leg={LEG} disp={DISPCOL} char={CHARCOL} sample={SAMPLE or 'full'}")
cur.execute(f"SELECT a.ident, a.domain, a.{DISPCOL}, a.{CHARCOL} FROM the internal cross site corpus a {jt} "
            f"WHERE a.{DISPCOL} IS NOT NULL AND a.{CHARCOL} IS NOT NULL")
idents,rooms,P,C=[],[],[],[]
for ident,dom,dd,cw in cur:
    dd=obj(dd); cw=obj(cw)
    if not isinstance(dd,dict) or not isinstance(cw,dict): continue
    if any(a not in cw for a in CHAR) or any(a not in dd for a in D8) or not ident or not dom: continue
    try: d=[float(dd[a]) for a in D8]; c=[float(cw[a]) for a in CHAR]
    except (TypeError,ValueError): continue
    idents.append(ident); rooms.append(dom); P.append(d); C.append(c)
db.close()
P=np.array(P,float); C=np.array(C,float); idents=np.array(idents,object); rooms=np.array(rooms,object)
log(f"rows={len(P):,} persons={len(set(idents)):,} rooms={len(set(rooms)):,}")

# person-room aggregation
key={}
for n,(i,r) in enumerate(zip(idents,rooms)): key.setdefault((i,r),[]).append(n)
rp,rr,rP,rC=[],[],[],[]
for (i,r),ix in key.items():
    ix=np.asarray(ix); rp.append(i); rr.append(r); rP.append(P[ix].mean(0)); rC.append(C[ix].mean(0))
rP=np.array(rP); rC=np.array(rC); rr=np.array(rr,object)
from collections import Counter
npc=Counter(rr); keep=np.array([npc[r]>=MINPERS for r in rr])
rP,rC,rr=rP[keep],rC[keep],rr[keep]
ROOMS=sorted(set(rr)); RC={r:k for k,r in enumerate(ROOMS)}; room=np.array([RC[r] for r in rr])
# standardise both sides to SD units so the 8x8 is comparable cell to cell
Pz=(rP-rP.mean(0))/(rP.std(0)+1e-9); Cz=(rC-rC.mean(0))/(rC.std(0)+1e-9)
log(f"rooms>= {MINPERS}: {len(ROOMS):,}  person-room records: {len(Pz):,}")

# within-room pairs (both orderings), capped per room
ridx={}
for n,r in enumerate(room): ridx.setdefault(r,[]).append(n)
def make_pairs(gen):
    A,B,RM=[],[],[]
    for r,mem in ridx.items():
        m=np.asarray(mem); k=len(m)
        if k<2: continue
        tot=k*(k-1)//2
        if tot<=PAIRCAP:
            ii,jj=np.triu_indices(k,1); a,b=m[ii],m[jj]
        else:
            aa=gen.integers(0,k,PAIRCAP*3); bb=gen.integers(0,k,PAIRCAP*3); ok=aa!=bb
            lo=np.minimum(aa[ok],bb[ok]); hi=np.maximum(aa[ok],bb[ok])
            u=np.unique(lo.astype(np.int64)*k+hi); gen.shuffle(u); u=u[:PAIRCAP]
            a=m[(u//k).astype(int)]; b=m[(u%k).astype(int)]
        A.append(np.concatenate([a,b])); B.append(np.concatenate([b,a])); RM.append(np.repeat(r,2*len(a)))
    return np.concatenate(A),np.concatenate(B),np.concatenate(RM)
A,B,RM=make_pairs(rng)
dP=Pz[A]-Pz[B]; dC=Cz[A]-Cz[B]
log(f"pairs={len(A):,}")
def fit(dp,dc):
    W,*_=np.linalg.lstsq(dp,dc,rcond=None); return W    # 8x8: rows D8, cols CHAR
W=fit(dP,dC)
# room block bootstrap for per-cell CI
urooms=np.unique(RM); byr={r:np.where(RM==r)[0] for r in urooms}
boot=np.zeros((NBOOT,len(D8),len(CHAR)))
g=np.random.default_rng(SEED+1)
for bk in range(NBOOT):
    pick=g.choice(urooms,len(urooms),replace=True)
    idx=np.concatenate([byr[r] for r in pick])
    boot[bk]=fit(dP[idx],dC[idx])
lo=np.percentile(boot,2.5,0); hi=np.percentile(boot,97.5,0); sd=boot.std(0)
sig=(lo>0)|(hi<0)
internal model={"leg":LEG,"disp_col":DISPCOL,"char_col":CHARCOL,"n_pairs":int(len(A)),"n_rooms":len(ROOMS),
       "n_person_rooms":int(len(Pz)),"D8":D8,"CHAR":CHAR,
       "W":W.tolist(),"lo":lo.tolist(),"hi":hi.tolist(),"sd":sd.tolist(),"sig":sig.astype(int).tolist()}
# reconcile with the equation of state 2x2 (plasticity/stability -> matter-manner PC1 / originality)
i8={a:k for k,a in enumerate(D8)}
plas=Pz[:,i8["novelty"]]+Pz[:,i8["sociability"]]; stab=Pz[:,i8["discipline"]]+Pz[:,i8["yielding"]]-Pz[:,i8["mercuriality"]]
# matter/manner PC1 on the char reference
cur2=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
cur2.execute(f"SELECT {','.join(CHAR)} FROM the internal reference table")
allc=np.array([[float(x) for x in r] for r in cur2.fetchall()],float); M=allc.mean(0); S=allc.std(0)+1e-9
_,_,Vt=np.linalg.svd((allc-M)/S,full_matrices=False); PC1=Vt[0]
if PC1[0]+PC1[1]<0: PC1=-PC1
MM=((rC-M)/S)@PC1; MMz=(MM-MM.mean())/(MM.std()+1e-9); ORIG=Cz[:,CHAR.index("originality")]
Pm=np.column_stack([plas,stab]); Cm=np.column_stack([MMz,ORIG])
dPm=Pm[A]-Pm[B]; dCm=Cm[A]-Cm[B]; Wm=fit(dPm,dCm)
internal model["metatrait_2x2"]={"rows":["plasticity","stability"],"cols":["matter_manner_PC1","originality"],"W":Wm.tolist()}
json.dump(internal model,open(OUT,"w"),indent=1)
# print the internal model
log("=== ASHLAR internal model: 8x8 within-room coupling W (rows=disposition, cols=character); * = CI excludes 0 ===")
print("               "+" ".join(f"{c[:6]:>7}" for c in CHAR),flush=True)
for i,d in enumerate(D8):
    cells=" ".join((f"{W[i,j]:+.2f}"+("*" if sig[i,j] else " ") for j in range(len(CHAR))))
    print(f"{d:<14} {cells}",flush=True)
nsig=int(sig.sum())
log(f"significant cells: {nsig} of 64")
# the strongest cells
flat=sorted(((abs(W[i,j]),D8[i],CHAR[j],W[i,j],bool(sig[i,j])) for i in range(8) for j in range(8)),reverse=True)[:10]
log("strongest cells: "+", ".join(f"{d}->{c} {w:+.2f}{'*' if s else ''}" for _,d,c,w,s in flat))
log(f"metatrait 2x2 (reconcile w/ equation of state): plas->MM {Wm[0,0]:+.3f} plas->orig {Wm[0,1]:+.3f} "
    f"stab->MM {Wm[1,0]:+.3f} stab->orig {Wm[1,1]:+.3f}")
log(f"wrote {OUT}")

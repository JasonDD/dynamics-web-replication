#!/usr/bin/env python3
"""analyse_27b.py — cross-lineage confirmation of the manipulation signature.

Reads the SAME 1350 items scored by two independent lineages:
  7B  = baseline_7b.jsonl   (an internal 7B instruct model, )
  27B = scored_27b.jsonl    (an internal model extract, , thinking disabled)

Groups: MANIP (ira POL) / SINCERE (cmv args) / SHORTPOL (liar). For each lineage it prints group
means (8 axis + matter/manner PC1 + residual), Cohen's d (MANIP vs SINCERE, MANIP vs SHORTPOL) and
classifier AUC, then the 7B-vs-27B agreement (per-axis d sign agreement + Pearson r of the d-vectors,
PC1 d, residual d). numpy only; PC1 basis from the web character reference (lineage-independent).
"""
import os, json, numpy as np, psycopg2
DWEB=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
MATTER=["rigour","depth"]; MANNER=["affect","stance","register"]
POL={"RightTroll","LeftTroll","Fearmonger"}
rng=np.random.default_rng(1729)
W="the internal corpus store/ira_troll/work"

# ---- PC1 (SVD on web character reference), oriented rigour+depth positive ----
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
c=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
c.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
allc=np.array([[float(x) for x in r] for r in c.fetchall()],float)
MEAN=allc.mean(0); STD=allc.std(0)+1e-9
_,_,Vt=np.linalg.svd((allc-MEAN)/STD,full_matrices=False); PC1=Vt[0]
if (PC1[DWEB.index("rigour")]+PC1[DWEB.index("depth")])<0: PC1=-PC1
def pc1(ch): return float(((np.array([ch[a] for a in DWEB],float)-MEAN)/STD)@PC1)

def has8(ch): return ch and all(a in ch for a in DWEB)
def load(p):
    out=[]
    for l in open(p):
        try: r=json.loads(l)
        except: continue
        if has8(r.get("char")): out.append(r)
    return out
def split(rows):
    manip=[r for r in rows if r.get("kind")=="ira" and r.get("outcome") in POL]
    sincere=[r for r in rows if r.get("kind")=="arg"]
    shortpol=[r for r in rows if r.get("kind")=="liar"]
    return manip,sincere,shortpol
def mat(rows): return np.array([[r["char"][a] for a in DWEB] for r in rows],float)
def matter(ch): return float(np.mean([ch[a] for a in MATTER]))
def manner(ch): return float(np.mean([ch[a] for a in MANNER]))
def resid(ch): return manner(ch)-matter(ch)
def cohend(A,B):
    A=np.asarray(A,float);B=np.asarray(B,float)
    na,nb=len(A),len(B)
    sp=np.sqrt(((na-1)*A.var(0,ddof=1)+(nb-1)*B.var(0,ddof=1))/(na+nb-2)+1e-12)
    return (A.mean(0)-B.mean(0))/sp
def auc(y,s):
    y=np.asarray(y);s=np.asarray(s,float)
    pos=(y==1).sum();neg=(y==0).sum()
    if pos==0 or neg==0: return float("nan")
    _,inv,cnt=np.unique(s,return_inverse=True,return_counts=True)
    csum=np.cumsum(cnt);avg=(csum-cnt+1+csum)/2.0;ranks=avg[inv]
    return (ranks[y==1].sum()-pos*(pos+1)/2.0)/(pos*neg)
def fit(X,y,it=600,lr=0.3,l2=1e-3):
    n,d=X.shape;w=np.zeros(d);b=0.0
    for _ in range(it):
        p=1/(1+np.exp(-(X@w+b)));g=p-y
        w-=lr*(X.T@g/n+l2*w);b-=lr*g.mean()
    return w,b
def cv_auc(A,B):
    XA=mat(A);XB=mat(B);k=min(len(XA),len(XB))
    ia=rng.permutation(len(XA))[:k];ib=rng.permutation(len(XB))[:k]
    X=np.vstack([XA[ia],XB[ib]]);y=np.hstack([np.ones(k),np.zeros(k)])
    pm=rng.permutation(len(y));X=X[pm];y=y[pm]
    folds=np.array_split(np.arange(len(y)),5);aucs=[]
    for f in range(5):
        te=folds[f];tr=np.hstack([folds[j] for j in range(5) if j!=f])
        mu=X[tr].mean(0);sd=X[tr].std(0)+1e-9
        w,b=fit((X[tr]-mu)/sd,y[tr])
        s=1/(1+np.exp(-(((X[te]-mu)/sd)@w+b)));aucs.append(auc(y[te],s))
    return float(np.nanmean(aucs)),float(np.nanstd(aucs))

def lineage(tag,path):
    rows=load(path); manip,sincere,shortpol=split(rows)
    print(f"\n{'='*86}\n{tag}: MANIP={len(manip)} SINCERE={len(sincere)} SHORTPOL={len(shortpol)}\n{'='*86}")
    print("  group means (8 axis + PC1 + matter/manner/resid)")
    print("  "+"group".ljust(20)+"".join(a[:5].rjust(7) for a in DWEB)+"    PC1 matter manner  resid")
    G={"MANIP":manip,"SINCERE":sincere,"SHORTPOL":shortpol}
    for n,g in G.items():
        M=mat(g);pm=np.mean([pc1(r["char"]) for r in g])
        mt=np.mean([matter(r["char"]) for r in g]);mn=np.mean([manner(r["char"]) for r in g])
        print("  "+n.ljust(20)+"".join(f"{v:7.3f}" for v in M.mean(0))+f"{pm:7.2f}{mt:7.3f}{mn:7.3f}{mn-mt:7.3f}")
    out={}
    for base,bn in ((sincere,"SINCERE"),(shortpol,"SHORTPOL")):
        d=cohend(mat(manip),mat(base))
        pd=cohend([pc1(r["char"]) for r in manip],[pc1(r["char"]) for r in base])
        rd=cohend([resid(r["char"]) for r in manip],[resid(r["char"]) for r in base])
        a,s=cv_auc(manip,base)
        out[bn]={"d8":d,"pc1":float(pd),"resid":float(rd),"auc":a,"aucsd":s}
        print(f"\n  Cohen's d  MANIP - {bn}  (+ = manipulation HIGHER)")
        for i,ax in enumerate(DWEB): print(f"    {ax:<18}{d[i]:+6.2f}")
        print(f"    {'matter/manner PC1':<18}{pd:+6.2f}    (negative => MANIP lower on matter pole)")
        print(f"    {'residual(mnr-mtr)':<18}{rd:+6.2f}    (positive => manner inflated past matter)")
        print(f"    classifier AUC MANIP vs {bn}: {a:.3f} +/- {s:.2f}")
    return out

o7=lineage("7B (an internal 7B instruct model)", f"{W}/baseline_7b.jsonl")
o27=lineage("27B (an internal model, thinking off)", f"{W}/scored_27b.jsonl")

print(f"\n{'='*86}\nAGREEMENT: 7B vs 27B\n{'='*86}")
for bn in ("SINCERE","SHORTPOL"):
    d7=o7[bn]["d8"];d27=o27[bn]["d8"]
    sign=np.mean(np.sign(d7)==np.sign(d27))
    r=np.corrcoef(d7,d27)[0,1]
    print(f"\n  MANIP vs {bn}")
    print(f"    per-axis Cohen's d, 7B vs 27B:")
    print("    "+"axis".ljust(18)+"   7B    27B   sign")
    for i,ax in enumerate(DWEB):
        print(f"    {ax:<18}{d7[i]:+6.2f}{d27[i]:+6.2f}   {'=' if np.sign(d7[i])==np.sign(d27[i]) else 'X'}")
    print(f"    PC1 d:      7B {o7[bn]['pc1']:+.2f}   27B {o27[bn]['pc1']:+.2f}")
    print(f"    residual d: 7B {o7[bn]['resid']:+.2f}   27B {o27[bn]['resid']:+.2f}")
    print(f"    AUC:        7B {o7[bn]['auc']:.3f}    27B {o27[bn]['auc']:.3f}")
    print(f"    => sign agreement on 8 axes = {sign*100:.0f}%   Pearson r(d7,d27) = {r:.2f}")

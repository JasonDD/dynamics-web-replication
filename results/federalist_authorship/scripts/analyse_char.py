#!/usr/bin/env python3
"""analyse_char.py — does the 8-axis CHARACTER instrument distinguish Hamilton from Madison,
and do the 12 disputed fall on the Madison side of character space? Compare to stylometry.

Reads papers_scored.jsonl (id, paper, label, char:{8 axes}).
Reports: per-axis Hamilton vs Madison (Cohen d, AUC); PC1 (matter/manner) separation;
a nearest-centroid character call on the disputed; leave-one-out character-classifier accuracy
on known authors (the honest ceiling: is character even separable here?).
"""
import json, os, math
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
SCORED=os.path.join(HERE,"..","papers_scored.jsonl")
AXES=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
def vec(r): return np.array([r["char"][a] for a in AXES],float)
def cohend(a,b):
    a,b=np.array(a),np.array(b); na,nb=len(a),len(b)
    if na<2 or nb<2: return float("nan")
    sp=math.sqrt(((na-1)*a.var(ddof=1)+(nb-1)*b.var(ddof=1))/(na+nb-2))
    return (a.mean()-b.mean())/sp if sp>0 else float("nan")
def auc(a,b):
    a,b=np.array(a),np.array(b)
    if len(a)==0 or len(b)==0: return float("nan")
    allv=np.concatenate([a,b]); order=allv.argsort()
    ranks=np.empty(len(allv)); ranks[order]=np.arange(1,len(allv)+1)
    R1=ranks[:len(a)].sum(); U1=R1-len(a)*(len(a)+1)/2
    return U1/(len(a)*len(b))
def main():
    recs=[json.loads(l) for l in open(SCORED)]
    ham=[r for r in recs if r["label"]=="HAMILTON"]
    mad=[r for r in recs if r["label"]=="MADISON"]
    disp=[r for r in recs if r["label"]=="DISPUTED"]
    print(f"scored: {len(recs)}  Hamilton {len(ham)}  Madison {len(mad)}  disputed {len(disp)}")
    # PC1 on all papers, oriented rigour+depth positive (matter/manner as in the series)
    X=np.array([vec(r) for r in recs]); Xc=X-X.mean(0)
    U,S,Vt=np.linalg.svd(Xc,full_matrices=False); pc1=Vt[0]
    if pc1[AXES.index("rigour")]+pc1[AXES.index("depth")]<0: pc1=-pc1
    var1=(S**2/ (S**2).sum())[0]
    for r in recs: r["pc1"]=float((vec(r)-X.mean(0))@pc1)
    print(f"PC1 variance explained: {var1:.1%}  loadings: "+", ".join(f"{a}={pc1[i]:+.2f}" for i,a in enumerate(AXES)))
    print("\n=== per-axis Hamilton vs Madison (known) ===")
    print(f"{'axis':16}{'H_mean':>8}{'M_mean':>8}{'cohen_d':>9}{'auc':>7}")
    per={}
    for a in AXES+["pc1"]:
        hv=[(r['char'][a] if a in AXES else r['pc1']) for r in ham]
        mv=[(r['char'][a] if a in AXES else r['pc1']) for r in mad]
        d=cohend(hv,mv); u=auc(hv,mv)
        print(f"{a:16}{np.mean(hv):8.3f}{np.mean(mv):8.3f}{d:9.2f}{u:7.3f}")
        per[a]={"h":float(np.mean(hv)),"m":float(np.mean(mv)),"d":None if math.isnan(d) else round(d,3),"auc":None if math.isnan(u) else round(u,3)}
    # nearest-centroid character call on disputed (z-scored on known)
    Xk=np.array([vec(r) for r in ham+mad]); mu=Xk.mean(0); sd=Xk.std(0); sd[sd==0]=1e-9
    hz=np.mean([(vec(r)-mu)/sd for r in ham],0); mz=np.mean([(vec(r)-mu)/sd for r in mad],0)
    def ccall(r):
        z=(vec(r)-mu)/sd
        dh=np.linalg.norm(z-hz); dm=np.linalg.norm(z-mz)
        return ("MADISON" if dm<dh else "HAMILTON"),dh,dm
    # LOO character-classifier accuracy on known (nearest centroid, z on the training fold)
    train=ham+mad; ytrue=["HAMILTON"]*len(ham)+["MADISON"]*len(mad); ok=0
    for i,r in enumerate(train):
        ph=[x for x in ham if x is not r]; pm=[x for x in mad if x is not r]
        Xt=np.array([vec(x) for x in ph+pm]); m2=Xt.mean(0); s2=Xt.std(0); s2[s2==0]=1e-9
        hz2=np.mean([(vec(x)-m2)/s2 for x in ph],0); mz2=np.mean([(vec(x)-m2)/s2 for x in pm],0)
        z=(vec(r)-m2)/s2
        pred="MADISON" if np.linalg.norm(z-mz2)<np.linalg.norm(z-hz2) else "HAMILTON"
        ok+=(pred==ytrue[i])
    print(f"\n[character] nearest-centroid LOO-CV accuracy on known: {ok}/{len(train)} = {ok/len(train):.3f}")
    print("(chance for this split by majority class = {:.3f})".format(max(len(ham),len(mad))/len(train)))
    print("\n=== disputed: character nearest-centroid call ===")
    print(f"{'No.':>4}{'call':>10}{'dist_H':>8}{'dist_M':>8}{'pc1':>8}")
    rows=[]; nmad=0
    for r in disp:
        call,dh,dm=ccall(r)
        print(f"{r['paper']:>4}{call:>10}{dh:8.2f}{dm:8.2f}{r['pc1']:8.3f}")
        nmad+=(call=="MADISON"); rows.append({"paper":r['paper'],"char_call":call,"dist_h":round(dh,3),"dist_m":round(dm,3),"pc1":round(r['pc1'],3)})
    print(f"\ndisputed called MADISON by character: {nmad}/12")
    print(f"mean PC1: Hamilton {np.mean([r['pc1'] for r in ham]):+.3f}  Madison {np.mean([r['pc1'] for r in mad]):+.3f}  disputed {np.mean([r['pc1'] for r in disp]):+.3f}")
    out={"n":len(recs),"pc1_var":float(var1),"per_axis":per,
         "char_loo_cv":ok/len(train),"char_chance":max(len(ham),len(mad))/len(train),
         "disputed_char_madison":nmad,"disputed":rows,
         "pc1_means":{"hamilton":float(np.mean([r['pc1'] for r in ham])),"madison":float(np.mean([r['pc1'] for r in mad])),"disputed":float(np.mean([r['pc1'] for r in disp]))}}
    json.dump(out,open(os.path.join(HERE,"..","character_result.json"),"w"),indent=2)
    print("\nwrote character_result.json")
if __name__=="__main__": main()

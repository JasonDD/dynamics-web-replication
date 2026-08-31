#!/usr/bin/env python3
"""analyse_multiway.py -- decompose the confound on the multi-way parallel Europarl set.

Reads scored.jsonl {id:"<item>__<lang>", char:{8 axes}}. Two questions:
 (A) Does character SURVIVE translation? -> per-item agreement across languages (ICC, mean cross-language r).
 (B) Content vs target-language split -> balanced two-way random-effects variance decomposition
     y_{item,lang} = mu + item + lang + resid  (one obs/cell; interaction = residual).
Uses the SAME matter/manner PC1 (SVD on cc_v3.domain_char8_expanded, rigour+depth positive) as the series.
"""
import os, json, numpy as np, psycopg2
from collections import defaultdict
from itertools import combinations
from scipy import stats

DWEB=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
LANGS=["en","de","fr","es","it","fi","pl","el"]
SCORED=os.environ.get("SCORED","/mnt/nas/kronaxis/corpora/europarl_multiway/scored.jsonl")

PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
c=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
c.execute(f"SELECT {','.join(DWEB)} FROM cc_v3.domain_char8_expanded")
allc=np.array([[float(x) for x in r] for r in c.fetchall()],float)
MEAN=allc.mean(0); STD=allc.std(0)+1e-9
_,_,Vt=np.linalg.svd((allc-MEAN)/STD,full_matrices=False); PC1=Vt[0]
if (PC1[DWEB.index("rigour")]+PC1[DWEB.index("depth")])<0: PC1=-PC1
def pc1(ch): return float(((np.array([ch[a] for a in DWEB],float)-MEAN)/STD)@PC1)

# load scores -> data[item][lang] = {axis:val, PC1:val}
data=defaultdict(dict)
for l in open(SCORED):
    try: r=json.loads(l)
    except Exception: continue
    if "char" not in r or "__" not in r["id"]: continue
    item,lang=r["id"].split("__",1)
    if lang not in LANGS: continue
    ch=r["char"]; d={a:float(ch[a]) for a in DWEB}; d["PC1"]=pc1(ch)
    data[item][lang]=d

# complete cases only (all 8 langs present)
items=[it for it in data if all(lang in data[it] for lang in LANGS)]
items.sort()
I=len(items); J=len(LANGS)
print(f"scored items with all {J} langs: {I}  (raw items seen {len(data)})")
AXES=DWEB+["PC1"]

def matrix(axis):
    return np.array([[data[it][lang][axis] for lang in LANGS] for it in items],float)  # I x J

def two_way_random(Y):
    # balanced two-way random effects, one obs per cell
    I,J=Y.shape
    gm=Y.mean(); ri=Y.mean(1); cj=Y.mean(0)
    SSitem=J*np.sum((ri-gm)**2); SSlang=I*np.sum((cj-gm)**2)
    resid=Y-ri[:,None]-cj[None,:]+gm; SSres=np.sum(resid**2)
    MSitem=SSitem/(I-1); MSlang=SSlang/(J-1); MSres=SSres/((I-1)*(J-1))
    v_item=max((MSitem-MSres)/J,0.0); v_lang=max((MSlang-MSres)/I,0.0); v_res=MSres
    tot=v_item+v_lang+v_res if (v_item+v_lang+v_res)>0 else 1.0
    Fi,pi=MSitem/MSres, stats.f.sf(MSitem/MSres,I-1,(I-1)*(J-1))
    Fl,pl=MSlang/MSres, stats.f.sf(MSlang/MSres,J-1,(I-1)*(J-1))
    return dict(v_item=v_item,v_lang=v_lang,v_res=v_res,
                pct_content=100*v_item/tot,pct_lang=100*v_lang/tot,pct_res=100*v_res/tot,
                Fi=Fi,pi=pi,Fl=Fl,pl=pl,MSitem=MSitem,MSlang=MSlang,MSres=MSres)

def survival(Y):
    # ICC(1) one-way (item as group across langs) + mean cross-language pairwise r + en-vs-mean-of-rest r
    I,J=Y.shape
    gm=Y.mean(); ri=Y.mean(1)
    MSb=J*np.sum((ri-gm)**2)/(I-1)
    MSw=np.sum((Y-ri[:,None])**2)/(I*(J-1))
    icc1=(MSb-MSw)/(MSb+(J-1)*MSw)
    rs=[stats.pearsonr(Y[:,a],Y[:,b])[0] for a,b in combinations(range(J),2)]
    en=LANGS.index("en"); rest=[j for j in range(J) if j!=en]
    r_en=stats.pearsonr(Y[:,en],Y[:,rest].mean(1))[0]
    return icc1,float(np.mean(rs)),r_en

print("\n=== (A) DOES CHARACTER SURVIVE TRANSLATION? (item = same content across 8 langs) ===")
print(f"{'axis':<17}{'ICC(item)':>10}{'meanXlangR':>12}{'en~transl':>11}")
surv={}
for ax in AXES:
    Y=matrix(ax); icc,mr,ren=survival(Y); surv[ax]=(icc,mr,ren)
    print(f"{ax:<17}{icc:>10.3f}{mr:>12.3f}{ren:>11.3f}")

print("\n=== (B) VARIANCE SPLIT: content(item) vs target-language vs residual ===")
print(f"{'axis':<17}{'content%':>9}{'lang%':>8}{'resid%':>8}{'p_item':>9}{'p_lang':>9}")
dec={}
for ax in AXES:
    d=two_way_random(matrix(ax)); dec[ax]=d
    print(f"{ax:<17}{d['pct_content']:>9.1f}{d['pct_lang']:>8.1f}{d['pct_res']:>8.1f}{d['pi']:>9.1e}{d['pl']:>9.1e}")

# content-vs-language split (renormalised, residual excluded) for the headline
print("\n=== headline content-vs-language split (residual/noise excluded, so content%+lang%=100) ===")
print(f"{'axis':<17}{'CONTENT%':>10}{'LANGUAGE%':>11}")
for ax in AXES:
    d=dec[ax]; s=d['v_item']+d['v_lang']
    cc_=100*d['v_item']/s if s>0 else float('nan'); ll_=100*d['v_lang']/s if s>0 else float('nan')
    print(f"{ax:<17}{cc_:>10.1f}{ll_:>11.1f}")

# per-language mean PC1 (the target-language norm, concretely)
print("\n=== target-language baselines: mean PC1 (matter/manner) per language ===")
YP=matrix("PC1")
for j,lang in enumerate(LANGS):
    print(f"  {lang}: mean PC1 = {YP[:,j].mean():+.3f}  sd={YP[:,j].std():.3f}")

# bootstrap CI on PC1 content/lang shares (resample items)
rng=np.random.default_rng(7)
Y=matrix("PC1"); B=1000; cs=[]; ls=[]
for _ in range(B):
    idx=rng.integers(0,I,I); d=two_way_random(Y[idx]); cs.append(d['pct_content']); ls.append(d['pct_lang'])
print(f"\nPC1 content% 95CI = [{np.percentile(cs,2.5):.1f}, {np.percentile(cs,97.5):.1f}]  "
      f"lang% 95CI = [{np.percentile(ls,2.5):.1f}, {np.percentile(ls,97.5):.1f}]  (bootstrap over items, B={B})")

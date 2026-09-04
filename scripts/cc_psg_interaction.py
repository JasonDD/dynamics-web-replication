#!/usr/bin/env python3
"""cc_psg_interaction.py -- the person by content INTERACTION test on PersuasionForGood.

Registered in results/person_content_interaction/PREREGISTRATION.md + MAPPING.md (frozen, tagged before this
run). Does the frozen person by content geometry predict WHICH persuadee was moved by WHICH persuader's
character, beyond persuadee personality alone, content alone, and a 768d modern embedding?

person (persuadee Big Five -> DeYoung Big Two metatraits, frozen loadings) x content (frozen char geometry
of the persuader turns) -> persuadee donation. Nested 5x5 CV ridge, incremental R2 of the interaction block
over baseline+embedding+content-main-effects. Persuadee-clustered bootstrap + a pairing permutation. Content
already scored (psg_scores.jsonl); embedding via local Ollama, cached. Analysis only, CPU.
"""
import os, re, json, math, time, urllib.request
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
import psycopg2

DWEB=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
BASE=os.environ.get("BASE","the internal corpus store/human_persuasion")
SCORES=os.path.join(BASE,"psg_scores.jsonl"); INPUT=os.path.join(BASE,"psg_input.jsonl")
INFO=os.path.join(BASE,"persuasionforgood/data/FullData/full_info.csv")
CACHE=os.environ.get("EMB_CACHE",os.path.join(BASE,"psg_nomic_emb.json"))
OLLAMA=os.environ.get("OLLAMA","http://127.0.0.1/api/embeddings"); EMB_MODEL=os.environ.get("EMB_MODEL","nomic-embed-text")
OUT=os.environ.get("OUT","/tmp/psg_interaction.json"); SEED=20260903
def log(*a): print(*a, flush=True)
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]

# ---- frozen content geometry (SVD on the domain reference, NOT on PSG) ----
c=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
c.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
allc=np.array([[float(x) for x in r] for r in c.fetchall()],float); MEAN=allc.mean(0); STD=allc.std(0)+1e-9
_,_,Vt=np.linalg.svd((allc-MEAN)/STD,full_matrices=False); PC1=Vt[0]
if PC1[0]+PC1[1]<0: PC1=-PC1
PC2=Vt[1]

# ---- content per dialogue (frozen) ----
char={}
for line in open(SCORES):
    d=json.loads(line); ch=d.get("char")
    if isinstance(ch,dict) and all(a in ch for a in DWEB):
        char[d["id"]]=np.array([float(ch[a]) for a in DWEB],float)
text={json.loads(l)["id"]: json.loads(l).get("text","") for l in open(INPUT)}

# ---- persuadee personality + donation (role B4==1), keyed psg_<B2> ----
info=pd.read_csv(INFO)
ee=info[info["B4"].round()==1].copy()
BF=["open.x","extrovert.x","conscientious.x","agreeable.x","neurotic.x"]
DS=["rational.x","intuitive.x"]; DEM=["age.x","sex.x","edu.x","income.x","ideology.x"]
for col in BF+DS+DEM+["B6"]:
    ee[col]=pd.to_numeric(ee[col],errors="coerce")
ee["id"]="psg_"+ee["B2"].astype(str)
ee=ee.dropna(subset=BF+DS+["B6"])
per={r["id"]:r for _,r in ee.iterrows()}

ids=[i for i in char if i in per and i in text and len(text[i])>=20]
log(f"joined {len(ids)} dialogues (content + persuadee personality + donation)")

# ---- embed persuader turns (cached) ----
emb={}
if os.path.exists(CACHE): emb={k:np.array(v,np.float32) for k,v in json.load(open(CACHE)).items()}
todo=[i for i in ids if i not in emb]
if todo:
    log(f"embedding {len(todo)} persuader texts via {EMB_MODEL} ...")
    for k,i in enumerate(todo,1):
        body=json.dumps({"model":EMB_MODEL,"prompt":"search_document: "+text[i][:2000]}).encode()
        for att in range(4):
            try:
                r=urllib.request.urlopen(urllib.request.Request(OLLAMA,data=body,headers={"Content-Type":"application/json"}),timeout=60)
                emb[i]=np.array(json.loads(r.read())["embedding"],np.float32); break
            except Exception:
                if att==3: raise
                time.sleep(2)
        if k%200==0: json.dump({kk:vv.tolist() for kk,vv in emb.items()},open(CACHE,"w")); log(f"  {k}/{len(todo)}")
    json.dump({kk:vv.tolist() for kk,vv in emb.items()},open(CACHE,"w"))
ids=[i for i in ids if i in emb]
log(f"embedded set: {len(ids)}")

# ---- assemble ----
def zc(a): a=np.asarray(a,float); return (a-a.mean())/(a.std()+1e-9)
CH=np.array([char[i] for i in ids]); CHz=(CH-MEAN)/STD
MM=CHz@PC1; OR2=CHz@PC2
# persuadee Big Five z within sample -> frozen DeYoung metatraits
zO=zc([per[i]["open.x"] for i in ids]); zE=zc([per[i]["extrovert.x"] for i in ids])
zC=zc([per[i]["conscientious.x"] for i in ids]); zA=zc([per[i]["agreeable.x"] for i in ids]); zN=zc([per[i]["neurotic.x"] for i in ids])
P_plas=zO+zE; P_stab=zC+zA-zN
PERSON=np.column_stack([zO,zE,zC,zA,zN,
                        zc([per[i]["rational.x"] for i in ids]),zc([per[i]["intuitive.x"] for i in ids])])
def zc_imp(a):
    a=np.asarray(a,float); fin=np.isfinite(a)
    if fin.sum()<100: return None
    m=a[fin].mean(); a=np.where(fin,a,m); sd=a.std()
    return (a-a.mean())/(sd+1e-9) if sd>1e-9 else None
demcols=[z for z in (zc_imp([per[i][d] for i in ids]) for d in DEM) if z is not None]
DEMz=np.column_stack(demcols) if demcols else np.zeros((len(ids),0))
log(f"demographic controls kept: {len(demcols)} of {len(DEM)}")
EMB_raw=np.array([emb[i] for i in ids],float)
# Amendment 2: top-50 PCs of the standardised embedding (nuisance control, tractable permutation)
EZ=(EMB_raw-EMB_raw.mean(0))/(EMB_raw.std(0)+1e-9)
_U,_S,_Vt=np.linalg.svd(EZ,full_matrices=False); EMB=EZ@_Vt[:50].T
# classical textual of persuader turns
WORD=re.compile(r"[a-z]+(?:'[a-z]+)?"); SENT=re.compile(r"[.!?]+"); VOW=re.compile(r"[aeiouy]+")
F2=set("i me my we us our you your".split()); EMO=set("love hate great awful terrible amazing best worst good bad wrong right must should".split())
INT=set("very really so totally completely absolutely extremely clearly obviously certainly".split()); PREP=set("of in to for with on at by from about as into than".split()); ART=set("the an".split())
def syll(w): n=len(VOW.findall(w)); return max(1,n-1 if w.endswith("e") else n)
def feats(t):
    tk=WORD.findall(t.lower()); n=max(len(tk),1); s=max(len([x for x in SENT.split(t) if x.strip()]),1)
    wps=n/s; syl=sum(syll(w) for w in tk); fk=0.39*wps+11.8*(syl/n)-15.59; mwl=float(np.mean([len(w) for w in tk])) if tk else 0
    first=sum(w in F2 for w in tk)/n; emo=sum(w in EMO for w in tk)/n; ints=sum(w in INT for w in tk)/n
    prep=sum(w in PREP for w in tk)/n; art=sum(w in ART for w in tk)/n; q=t.count("?")/s
    return [math.log(n),fk,mwl,wps,emo,ints,first,q,(mwl+8*prep+6*art)-(10*first+6*q+6*ints)]
CLASS=np.array([feats(text[i]) for i in ids])
# interaction block (frozen 2x2 person-metatrait x content-geometry)
def inter(pp,ps): return np.column_stack([pp*OR2, ps*MM, pp*MM, ps*OR2])
INTER=inter(P_plas,P_stab)

don=np.array([float(per[i]["B6"]) for i in ids])
Y_bin=(don>0).astype(float); Y_log=np.log1p(don)
log(f"donated>0 base rate {Y_bin.mean():.3f}   log-donation mean {Y_log.mean():.3f}")

def zx(X): return (X-X.mean(0))/(X.std(0)+1e-9)
def design(*p): return zx(np.column_stack([a for a in p if a.ndim==1 or a.shape[1]>0]))
def nested_r2(X,y,seed=SEED):
    outer=KFold(5,shuffle=True,random_state=seed); lams=[1,10,100,1000,10000,100000]; pred=np.zeros_like(y)
    for tr,te in outer.split(X):
        best=None
        for lam in lams:
            inner=KFold(5,shuffle=True,random_state=seed+1); se=0
            for itr,iva in inner.split(X[tr]):
                m=Ridge(alpha=lam).fit(X[tr][itr],y[tr][itr]); se+=((y[tr][iva]-m.predict(X[tr][iva]))**2).sum()
            if best is None or se<best[0]: best=(se,lam)
        pred[te]=Ridge(alpha=best[1]).fit(X[tr],y[tr]).predict(X[te])
    return 1-((y-pred)**2).sum()/((y-y.mean())**2).sum(), pred
def r2_of(p,y): return 1-((y-p)**2).sum()/((y-y.mean())**2).sum()

def run(y,tag):
    B_base=[PERSON,DEMz,CLASS]
    blocks={"baseline":design(*B_base),
            "+embedding":design(*B_base,EMB),
            "+content":design(*B_base,EMB,CHz),
            "+interaction":design(*B_base,EMB,CHz,INTER)}
    res={}; pr={}
    for k,X in blocks.items(): res[k],pr[k]=nested_r2(X,y); log(f"  [{tag}] {k:<14} R2 {res[k]:+.4f}")
    d=res["+interaction"]-res["+content"]
    p0,p1=pr["+content"],pr["+interaction"]
    g=np.random.default_rng(SEED+7); boot=[r2_of(p1[ix],y[ix])-r2_of(p0[ix],y[ix]) for ix in (g.integers(0,len(y),len(y)) for _ in range(1000))]
    lo,hi=np.percentile(boot,[2.5,97.5])
    gp=np.random.default_rng(SEED+9); perm=[]
    for _ in range(200):
        pi=gp.permutation(len(ids))
        Xp=design(*B_base,EMB,CHz,inter(P_plas[pi],P_stab[pi]))
        r2p,_=nested_r2(Xp,y); perm.append(r2p-res["+content"])
    perm=np.array(perm); pval=(np.sum(perm>=d)+1)/(len(perm)+1)
    verdict=("PASS: the frozen person x content interaction adds real predictive value" if (d>0.01 and lo>0 and pval<0.01)
             else "NULL: the interaction is redundant given person + content + embedding" if (d<=0.005 or lo<=0) else "WEAK: between")
    log(f"  [{tag}] INTERACTION delta R2 = {d:+.4f} [{lo:+.4f},{hi:+.4f}] perm p={pval}")
    log(f"  [{tag}] VERDICT: {verdict}")
    return {"blocks":{k:round(float(v),4) for k,v in res.items()},
            "interaction_delta":round(float(d),4),"boot_lo":round(float(lo),4),"boot_hi":round(float(hi),4),
            "perm_p":round(float(pval),4),"verdict":verdict}

out={"n":len(ids),"emb_dim":EMB.shape[1],"donated_base_rate":round(float(Y_bin.mean()),4),
     "primary_donated_binary":run(Y_bin,"bin"),"secondary_log_donation":run(Y_log,"log")}
json.dump(out,open(OUT,"w"),indent=1); log(f"wrote {OUT}")

#!/usr/bin/env python3
"""cc_ucsc_interaction.py -- person by content INTERACTION, leg 2: UCSC Persuasion and Personality.

The sharp leg PSG could not be: measured Big Five BEFORE exposure, an assigned persuasive argument (the
fact/feeling experiment, Lukin et al. EACL 2017), and actual belief change. Same frozen person side mapping
as PSG (DeYoung Big Two, no fit), same frozen content geometry directions, same preregistered 2x2 interaction,
same nested CV incremental-R2 ladder and pass rule. Content of the 100 arguments scored on the same 8 axes.

Cross-model scale note (Amendment): the reference geometry was built on a differently scored table, so the
content axes are standardised WITHIN this corpus before the FROZEN PC1/PC2 direction (the pre-committed
loading vector = which axes make matter/manner) is applied. The frozen object is the direction, not the
absolute scale. n is small at the person level (80 workers); the outcome varies within worker across 25
arguments each, and the bootstrap/CV are clustered by worker.
"""
import os, re, json, math
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
import psycopg2

DWEB=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
B="/mnt/nas/kronaxis/corpora/human_persuasion"; D=B+"/ucsc_persuasion_personality/"
OUT=os.environ.get("OUT","/tmp/ucsc_interaction.json"); SEED=20260903
def log(*a): print(*a, flush=True)
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]

# frozen PC1/PC2 DIRECTIONS from the domain reference (loading vectors only)
c=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
c.execute(f"SELECT {','.join(DWEB)} FROM cc_v3.domain_char8_expanded")
allc=np.array([[float(x) for x in r] for r in c.fetchall()],float)
_,_,Vt=np.linalg.svd((allc-allc.mean(0))/(allc.std(0)+1e-9),full_matrices=False)
PC1=Vt[0]; PC1=PC1 if PC1[0]+PC1[1]>=0 else -PC1; PC2=Vt[1]

# content scores per argument id (ucsc_<pg>_<q>)
char={json.loads(l)["id"]: np.array([float(json.loads(l)["char"][a]) for a in DWEB]) for l in open(B+"/ucsc_arg_scores.jsonl")}

# responses: person Big Five + change + before + ffvalue, join arg by page_qnum -> ucsc_<pg>_<q>
resp=pd.read_csv(D+"ffpage_anon_responses.csv")
def aid(pq):
    s=str(pq).split("_"); return f"ucsc_{s[0]}_{s[1]}" if len(s)==2 else None
resp["aid"]=resp["page_qnum"].map(aid)
BF={"o":"o_raw","c":"c_raw","e":"e_raw","a":"a_raw","n":"n_raw"}
need=list(BF.values())+["change_znorm","before_znorm","ffvalue","WorkerId","aid"]
for col in list(BF.values())+["change_znorm","before_znorm","ffvalue"]:
    resp[col]=pd.to_numeric(resp[col],errors="coerce")
resp=resp.dropna(subset=need)
resp=resp[resp["aid"].isin(char.keys())].reset_index(drop=True)
log(f"joined rows {len(resp)}  workers {resp.WorkerId.nunique()}  arguments {resp.aid.nunique()}")

CH=np.array([char[a] for a in resp["aid"]])
CHz=(CH-CH.mean(0))/(CH.std(0)+1e-9)          # within-corpus standardise, then frozen direction
MM=CHz@PC1; OR2=CHz@PC2
def z(x): x=np.asarray(x,float); return (x-x.mean())/(x.std()+1e-9)
zO=z(resp[BF["o"]]); zE=z(resp[BF["e"]]); zC=z(resp[BF["c"]]); zA=z(resp[BF["a"]]); zN=z(resp[BF["n"]])
P_plas=zO+zE; P_stab=zC+zA-zN                  # frozen DeYoung metatraits (identical to PSG mapping)
before=z(resp["before_znorm"]); ff=z(resp["ffvalue"])
PERSON=np.column_stack([zO,zE,zC,zA,zN])
Y=resp["change_znorm"].to_numpy(float)
groups=resp["WorkerId"].to_numpy()

WORD=re.compile(r"[a-z]+(?:'[a-z]+)?"); SENT=re.compile(r"[.!?]+"); VOW=re.compile(r"[aeiouy]+")
F2=set("i me my we us our you your".split()); EMO=set("love hate great awful terrible amazing best worst good bad wrong right must should".split())
INT=set("very really so totally completely absolutely extremely clearly obviously certainly".split()); PREP=set("of in to for with on at by from about as into than".split()); ART=set("the a an".split())
argtext={}  # for classical + embedding: r_text per aid
ff2=pd.read_csv(D+"ffpage.csv")
for _,r in ff2.iterrows(): argtext[f"ucsc_{int(r.pg_id)}_{int(r.q_num)}"]=str(r.r_text)
def syll(w): n=len(VOW.findall(w)); return max(1,n-1 if w.endswith("e") else n)
def feats(t):
    tk=WORD.findall(t.lower()); n=max(len(tk),1); s=max(len([x for x in SENT.split(t) if x.strip()]),1)
    wps=n/s; syl=sum(syll(w) for w in tk); fk=0.39*wps+11.8*(syl/n)-15.59; mwl=float(np.mean([len(w) for w in tk])) if tk else 0
    first=sum(w in F2 for w in tk)/n; emo=sum(w in EMO for w in tk)/n; ints=sum(w in INT for w in tk)/n
    prep=sum(w in PREP for w in tk)/n; art=sum(w in ART for w in tk)/n; q=t.count("?")/s
    return [math.log(n),fk,mwl,wps,emo,ints,first,q,(mwl+8*prep+6*art)-(10*first+6*q+6*ints)]
CLASS=np.array([feats(argtext.get(a,"")) for a in resp["aid"]])
# embedding block (Amendment 2 carried over): nomic per unique arg, top PCs, mapped per row
import urllib.request
ecache=B+"/ucsc_arg_nomic.json"
try: eall={k:np.array(v,np.float32) for k,v in json.load(open(ecache)).items()}
except Exception: eall={}
for a in set(resp["aid"]):
    if a in eall: continue
    bd=json.dumps({"model":"nomic-embed-text","prompt":"search_document: "+argtext.get(a,"")[:2000]}).encode()
    r=urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:11434/api/embeddings",data=bd,headers={"Content-Type":"application/json"}),timeout=60)
    eall[a]=np.array(json.loads(r.read())["embedding"],np.float32)
json.dump({k:v.tolist() for k,v in eall.items()},open(ecache,"w"))
EMBraw=np.array([eall[a] for a in resp["aid"]],float)
EZ=(EMBraw-EMBraw.mean(0))/(EMBraw.std(0)+1e-9)
_u,_sv,_vt=np.linalg.svd(EZ,full_matrices=False); EMB=EZ@_vt[:min(50,_vt.shape[0])].T

def inter(pp,ps): return np.column_stack([pp*OR2, ps*MM, pp*MM, ps*OR2])
INTER=inter(P_plas,P_stab)

def zx(X): return (X-X.mean(0))/(X.std(0)+1e-9)
def design(*p): return zx(np.column_stack([a for a in p if a.ndim>1 and a.shape[1]>0 or a.ndim==1]))
def nested_r2(X,y,seed=SEED):
    gk=GroupKFold(5); lams=[1,10,100,1000,10000]; pred=np.zeros_like(y)
    for tr,te in gk.split(X,y,groups):
        best=None
        gtr=groups[tr]
        for lam in lams:
            gi=GroupKFold(5); se=0
            for itr,iva in gi.split(X[tr],y[tr],gtr):
                m=Ridge(alpha=lam).fit(X[tr][itr],y[tr][itr]); se+=((y[tr][iva]-m.predict(X[tr][iva]))**2).sum()
            if best is None or se<best[0]: best=(se,lam)
        pred[te]=Ridge(alpha=best[1]).fit(X[tr],y[tr]).predict(X[te])
    return 1-((y-pred)**2).sum()/((y-y.mean())**2).sum(), pred
def r2_of(p,y): return 1-((y-p)**2).sum()/((y-y.mean())**2).sum()

# baseline: person main effects + prior belief + fact/feeling label + classical text
BASE=[PERSON, before.reshape(-1,1), ff.reshape(-1,1), CLASS]
blocks={"baseline":design(*BASE),
        "+embedding":design(*BASE,EMB),
        "+content":design(*BASE,EMB,CHz),
        "+interaction":design(*BASE,EMB,CHz,INTER)}
res={}; pr={}
for k,X in blocks.items(): res[k],pr[k]=nested_r2(X,Y); log(f"  {k:<14} R2 {res[k]:+.4f}")
d=res["+interaction"]-res["+content"]
p0,p1=pr["+content"],pr["+interaction"]
# worker-clustered bootstrap
uw=np.unique(groups); byw={w:np.where(groups==w)[0] for w in uw}
g=np.random.default_rng(SEED+7); boot=[]
for _ in range(1000):
    pick=g.choice(uw,len(uw),replace=True); ix=np.concatenate([byw[w] for w in pick])
    boot.append(r2_of(p1[ix],Y[ix])-r2_of(p0[ix],Y[ix]))
lo,hi=np.percentile(boot,[2.5,97.5])
# permutation: shuffle person metatraits ACROSS workers (person<->content pairing), holding margins
gp=np.random.default_rng(SEED+9); perm=[]
wlist=list(uw)
for _ in range(200):
    wp=gp.permutation(wlist); wmap={w:wp[i] for i,w in enumerate(wlist)}
    # map each row's worker to a permuted worker, reassign that worker's metatrait
    pmeta={w:(P_plas[byw[w]][0],P_stab[byw[w]][0]) for w in uw}  # worker-constant? metatraits vary by row? Big5 is per-worker -> constant
    pp=np.array([pmeta[wmap[w]][0] for w in groups]); ps=np.array([pmeta[wmap[w]][1] for w in groups])
    Xp=design(*BASE,EMB,CHz,inter(pp,ps)); r2p,_=nested_r2(Xp,Y); perm.append(r2p-res["+content"])
perm=np.array(perm); pval=(np.sum(perm>=d)+1)/(len(perm)+1)
# POSITIVE CONTROL: does the paper's OWN interaction (Big Five x fact/feeling label) surface in this pipeline?
INTER_ctrl=np.column_stack([zC*ff, zO*ff, zA*ff, zE*ff, zN*ff])
Xc=design(*BASE,EMB,CHz,INTER_ctrl); r2c,prc=nested_r2(Xc,Y); dctrl=r2c-res["+content"]
gpc=np.random.default_rng(SEED+11); permc=[]
for _ in range(200):
    wp=gpc.permutation(wlist); wmap={w:wp[i] for i,w in enumerate(wlist)}
    pC={w:(zC[byw[w]][0],zO[byw[w]][0],zA[byw[w]][0],zE[byw[w]][0],zN[byw[w]][0]) for w in uw}
    cc_=np.array([[pC[wmap[w]][j] for w in groups] for j in range(5)])
    Xcp=design(*BASE,EMB,CHz,np.column_stack([cc_[0]*ff,cc_[1]*ff,cc_[2]*ff,cc_[3]*ff,cc_[4]*ff]))
    r2cp,_=nested_r2(Xcp,Y); permc.append(r2cp-res["+content"])
permc=np.array(permc); pctrl=(np.sum(permc>=dctrl)+1)/(len(permc)+1)
log(f"POSITIVE CONTROL (Big Five x fact/feeling): delta R2 = {dctrl:+.4f} perm p={pctrl:.4f}  R2 {r2c:+.4f}")
CONTROL={"delta":round(float(dctrl),4),"perm_p":round(float(pctrl),4),"r2":round(float(r2c),4)}
verdict=("PASS: the frozen person x content interaction adds real predictive value under assigned content" if (d>0.01 and lo>0 and pval<0.01)
         else "NULL: the interaction is redundant given person + content" if (d<=0.005 or lo<=0) else "WEAK: between")
out={"n":len(resp),"workers":int(resp.WorkerId.nunique()),"arguments":int(resp.aid.nunique()),
     "blocks":{k:round(float(v),4) for k,v in res.items()},
     "interaction_delta":round(float(d),4),"boot_lo":round(float(lo),4),"boot_hi":round(float(hi),4),"perm_p":round(float(pval),4),
     "verdict":verdict,"positive_control_bigfive_x_ff":CONTROL}
json.dump(out,open(OUT,"w"),indent=1)
log(f"INTERACTION delta R2 = {d:+.4f} [{lo:+.4f},{hi:+.4f}] perm p={pval}")
log("VERDICT: "+verdict); log(f"wrote {OUT}")

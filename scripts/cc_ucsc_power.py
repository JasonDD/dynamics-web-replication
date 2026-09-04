#!/usr/bin/env python3
"""cc_ucsc_power.py -- assay sensitivity for the UCSC person by content interaction.

Answers the advisor's question: was this hammer capable of breaking the theory? Three steps.
(A) Conventional IN-SAMPLE reproduction of the corpus's own reference interaction (Big Five x fact/feeling)
    and of our frozen DYNAMICS interaction, as the original paper would (OLS incremental R2 + F test). If the
    reference does not reproduce even in sample, the mismatch is upstream.
(B) The SAME reference interaction under the held-out worker-clustered nested CV (already known to vanish).
(C) POWER INJECTION: inject a known population interaction of size tau (in the exact frozen direction,
    P_plas*OR2 + P_stab*MM) into the real UCSC design + worker structure, run it through the EXACT held-out
    pipeline, and estimate detection power at each tau. Compare the detection curve to the frozen 0.01 pass
    threshold and to the observed +0.0004. CPU only, content already scored.
"""
import os, re, json, math
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
import psycopg2
try:
    import statsmodels.api as sm; HAVE_SM=True
except Exception: HAVE_SM=False

DWEB=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
B="/mnt/nas/kronaxis/corpora/human_persuasion"; D=B+"/ucsc_persuasion_personality/"
OUT=os.environ.get("OUT","/tmp/ucsc_power.json"); SEED=20260903
def log(*a): print(*a, flush=True)
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
c=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
c.execute(f"SELECT {','.join(DWEB)} FROM cc_v3.domain_char8_expanded")
allc=np.array([[float(x) for x in r] for r in c.fetchall()],float)
_,_,Vt=np.linalg.svd((allc-allc.mean(0))/(allc.std(0)+1e-9),full_matrices=False)
PC1=Vt[0]; PC1=PC1 if PC1[0]+PC1[1]>=0 else -PC1; PC2=Vt[1]
char={json.loads(l)["id"]: np.array([float(json.loads(l)["char"][a]) for a in DWEB]) for l in open(B+"/ucsc_arg_scores.jsonl")}
resp=pd.read_csv(D+"ffpage_anon_responses.csv")
def aid(pq):
    s=str(pq).split("_"); return f"ucsc_{s[0]}_{s[1]}" if len(s)==2 else None
resp["aid"]=resp["page_qnum"].map(aid)
BF={"o":"o_raw","c":"c_raw","e":"e_raw","a":"a_raw","n":"n_raw"}
need=list(BF.values())+["change_znorm","before_znorm","ffvalue","WorkerId","aid"]
for col in list(BF.values())+["change_znorm","before_znorm","ffvalue"]: resp[col]=pd.to_numeric(resp[col],errors="coerce")
resp=resp.dropna(subset=need); resp=resp[resp["aid"].isin(char.keys())].reset_index(drop=True)
CH=np.array([char[a] for a in resp["aid"]]); CHz=(CH-CH.mean(0))/(CH.std(0)+1e-9)
MM=CHz@PC1; OR2=CHz@PC2
def z(x): x=np.asarray(x,float); return (x-x.mean())/(x.std()+1e-9)
zO=z(resp[BF["o"]]);zE=z(resp[BF["e"]]);zC=z(resp[BF["c"]]);zA=z(resp[BF["a"]]);zN=z(resp[BF["n"]])
P_plas=zO+zE; P_stab=zC+zA-zN; before=z(resp["before_znorm"]); ff=z(resp["ffvalue"])
PERSON=np.column_stack([zO,zE,zC,zA,zN]); Y=resp["change_znorm"].to_numpy(float); groups=resp["WorkerId"].to_numpy()
def zx(X): return (X-X.mean(0))/(X.std(0)+1e-9)
def design(*p): return zx(np.column_stack(p))
BASE=[PERSON, before.reshape(-1,1), ff.reshape(-1,1)]
INT_dyn=np.column_stack([P_plas*OR2,P_stab*MM,P_plas*MM,P_stab*OR2])
INT_ref=np.column_stack([zC*ff,zO*ff,zA*ff,zE*ff,zN*ff])

# ---------- (A) conventional in-sample OLS incremental R2 + F ----------
def insample_incr(Xbase,Xadd):
    Xb=sm.add_constant(zx(Xbase)); Xf=sm.add_constant(zx(np.column_stack([Xbase,Xadd])))
    rb=sm.OLS(Y,Xb).fit(); rf=sm.OLS(Y,Xf).fit()
    from scipy.stats import f as fdist
    q=Xadd.shape[1] if Xadd.ndim>1 else 1; n=len(Y); k=Xf.shape[1]
    F=((rf.rsquared-rb.rsquared)/q)/((1-rf.rsquared)/(n-k)); p=1-fdist.cdf(F,q,n-k)
    return round(rb.rsquared,4),round(rf.rsquared,4),round(rf.rsquared-rb.rsquared,4),round(float(F),3),round(float(p),5)
A={}
if HAVE_SM:
    base_simple=np.column_stack([PERSON,before,ff])          # faithful to the paper (no our-content control)
    base_full=np.column_stack([PERSON,before,ff,CHz])        # demanding (controls our content)
    A["reference_bigfive_x_ff_simple_baseline"]=dict(zip(["r2_base","r2_full","incr","F","p"],insample_incr(base_simple,INT_ref)))
    A["reference_bigfive_x_ff_full_baseline"]=dict(zip(["r2_base","r2_full","incr","F","p"],insample_incr(base_full,INT_ref)))
    A["dynamics_interaction_full_baseline"]=dict(zip(["r2_base","r2_full","incr","F","p"],insample_incr(base_full,INT_dyn)))
    log("[A] in-sample reference Big5xff (simple baseline):",A["reference_bigfive_x_ff_simple_baseline"])
    log("[A] in-sample reference Big5xff (full baseline)  :",A["reference_bigfive_x_ff_full_baseline"])
    log("[A] in-sample DYNAMICS 2x2 (full baseline)       :",A["dynamics_interaction_full_baseline"])

# ---------- held-out nested CV helper ----------
def nested_r2(X,y,seed=SEED):
    gk=GroupKFold(5); lams=[1,10,100,1000,10000]; pred=np.zeros_like(y)
    for tr,te in gk.split(X,y,groups):
        best=None; gtr=groups[tr]
        for lam in lams:
            gi=GroupKFold(5); se=0
            for itr,iva in gi.split(X[tr],y[tr],gtr):
                m=Ridge(alpha=lam).fit(X[tr][itr],y[tr][itr]); se+=((y[tr][iva]-m.predict(X[tr][iva]))**2).sum()
            if best is None or se<best[0]: best=(se,lam)
        pred[te]=Ridge(alpha=best[1]).fit(X[tr],y[tr]).predict(X[te])
    return 1-((y-pred)**2).sum()/((y-y.mean())**2).sum(), pred
def r2_of(p,y): return 1-((y-p)**2).sum()/((y-y.mean())**2).sum()
uw=np.unique(groups); byw={w:np.where(groups==w)[0] for w in uw}
def detect(y, INT, nboot=400, rng=None):
    Xc=design(*BASE,CHz); Xi=design(*BASE,CHz,INT)
    r2c,pc=nested_r2(Xc,y); r2i,pi=nested_r2(Xi,y); d=r2i-r2c
    g=rng or np.random.default_rng(0)
    boot=[]
    for _ in range(nboot):
        pick=g.choice(uw,len(uw),replace=True); ix=np.concatenate([byw[w] for w in pick])
        boot.append(r2_of(pi[ix],y[ix])-r2_of(pc[ix],y[ix]))
    lo=np.percentile(boot,2.5)
    return d, lo

# ---------- (B) reference under held-out CV ----------
dref,loref=detect(Y,INT_ref,nboot=400,rng=np.random.default_rng(SEED+1))
B_={"reference_heldout_delta":round(float(dref),4),"reference_heldout_boot_lo":round(float(loref),4)}
log("[B] held-out reference Big5xff delta",B_["reference_heldout_delta"],"boot_lo",B_["reference_heldout_boot_lo"])

# ---------- (C) power injection through the exact pipeline ----------
# THREE injection shapes (advisor): the preregistered frozen coupling is the adjudicator; the other two
# guard against proving sensitivity to an easy synthetic effect the real hypothesis would not share.
i_aff=DWEB.index("affect")
shapes={
 "frozen_coupling": z(P_plas*OR2+P_stab*MM),                                  # the preregistered form (ADJUDICATOR)
 "sparse_single_axis": z(zC*CHz[:,i_aff]),                                    # conscientiousness x affect (paper-like)
 "balanced_dense": z(sum((PERSON[:,j]*CHz[:,k]) for j in range(5) for k in range(8))),  # dense linear interaction
}
# detection uses the DYNAMICS interaction block (what the real test uses) as the fitted feature set
base_sig=z(design(*BASE,CHz)@np.linalg.lstsq(design(*BASE,CHz),Y,rcond=None)[0])
R2_BASE=0.05; REPS=int(os.environ.get("REPS","120")); PASS=0.01
taus=[0.0,0.005,0.008,0.01,0.015,0.02,0.03]
rng=np.random.default_rng(SEED+5)
C={}
for sname,s_int in shapes.items():
    curve={}
    for tau in taus:
        hits=0; dhat=[]
        for _ in range(REPS):
            noise=rng.standard_normal(len(Y))
            y=math.sqrt(R2_BASE)*base_sig + math.sqrt(tau)*s_int + math.sqrt(max(1e-9,1-R2_BASE-tau))*z(noise)
            d,lo=detect(y,INT_dyn,nboot=250,rng=rng)
            dhat.append(d)
            if d>PASS and lo>0: hits+=1
        curve[str(tau)]={"power":round(hits/REPS,3),"mean_delta_hat":round(float(np.mean(dhat)),4)}
        log(f"[C:{sname}] tau={tau:<5} power={curve[str(tau)]['power']:.2f}  mean_dhat={curve[str(tau)]['mean_delta_hat']:+.4f}")
    C[sname]=curve
adj=C["frozen_coupling"]["0.01"]["power"]
out={"n":len(resp),"workers":int(resp.WorkerId.nunique()),
     "A_insample":A,"B_reference_heldout":B_,
     "C_power_curves":C,"pass_threshold":PASS,"observed_dynamics_delta":0.0004,
     "ADJUDICATOR_power_frozen_form_at_0.01":adj,
     "adjudicator_sentence":f"At the frozen +0.01 substantive threshold, the exact UCSC pipeline had {adj*100:.0f}% probability of detecting an injected interaction of the preregistered (frozen coupling) form."}
json.dump(out,open(OUT,"w"),indent=1)
log("ADJUDICATOR:",out["adjudicator_sentence"])
log(f"wrote {OUT}")

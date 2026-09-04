#!/usr/bin/env python3
"""cc_experiment_power_design.py -- simulation-first power for the Ashlar severe test.

Simulates the PLANNED randomised experiment through the EXACT frozen detection pipeline and finds the minimum
N that detects an injected Ashlar-shaped interaction of delta R2 = 0.01 at 80/90/95% power. Shows the
repeated-measures economics: between-subjects (K=1) vs repeated propositions per participant (K>1). The
simulation sets N; N sets the cost. No real data; pure design tool.

Model per simulated experiment: each participant has frozen metatraits (plasticity, stability) ~ N(0,1) plus
nuisance covariates; each of K items is randomised to one of A arms whose target sits on a geometry-spanning
grid (between-arm SD = SPREAD) with within-arm scoring noise; message content = (matter/manner, originality).
Frozen coupling = plasticity*originality + stability*matter_manner. Outcome = person main + content main +
tau*coupling + noise, tau fixed so the population interaction share = 0.01. Detection = exact pipeline:
baseline (person + content main + arm dummies) vs +frozen 2x2 interaction, GroupKFold(5) by participant,
held-out incremental R2 > 0.01 AND participant-clustered bootstrap lower bound > 0.
"""
import os, json, math
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold

TAU=0.01; PASS=0.01; SEED=20260904
REPS=int(os.environ.get("REPS","50")); SPREAD=float(os.environ.get("SPREAD","0.8"))
R2P=0.06; R2C=0.04; WITHIN=0.3; A=int(os.environ.get("ARMS","5"))
OUT=os.environ.get("OUT","/tmp/experiment_power.json")
def log(*a): print(*a, flush=True)
def z(x): x=np.asarray(x,float); return (x-x.mean())/(x.std()+1e-9)

# arm target coordinates spanning a 2D geometry grid, scaled by SPREAD
grid=np.array([[-1,-1],[-1,1],[1,-1],[1,1],[0,0],[-1,0],[1,0],[0,-1],[0,1]],float)[:A]
grid=grid/ (grid.std()+1e-9) * SPREAD

def simulate(N,K,rng):
    plas=rng.standard_normal(N); stab=rng.standard_normal(N)
    nu=rng.standard_normal((N,3))
    pid=np.repeat(np.arange(N),K)
    plas_r=plas[pid]; stab_r=stab[pid]; nu_r=nu[pid]
    arm=rng.integers(0,A,N*K)
    mm=grid[arm,0]+rng.normal(0,WITHIN,N*K); orr=grid[arm,1]+rng.normal(0,WITHIN,N*K)
    mmz=z(mm); orz=z(orr)
    coup=z(plas_r*orz+stab_r*mmz)
    Sp=z(0.7*plas_r+0.5*stab_r+0.4*nu_r[:,0]+0.3*nu_r[:,1])
    Sc=z(0.8*mmz+0.5*orz)
    noise=rng.standard_normal(N*K)
    Y=math.sqrt(R2P)*Sp+math.sqrt(R2C)*Sc+math.sqrt(TAU)*coup+math.sqrt(max(1e-9,1-R2P-R2C-TAU))*z(noise)
    armd=np.zeros((N*K,A-1));
    for a in range(1,A): armd[:,a-1]=(arm==a)
    BASE=np.column_stack([plas_r,stab_r,nu_r,mmz,orz,armd])
    INT=np.column_stack([plas_r*orz,stab_r*mmz,plas_r*mmz,stab_r*orz])
    return Y,BASE,INT,pid
def zx(X): return (X-X.mean(0))/(X.std(0)+1e-9)
def nested_r2(X,y,groups):
    gk=GroupKFold(5); lams=[30,300,3000]; pred=np.zeros_like(y)
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
def detect(N,K,rng):
    Y,BASE,INT,pid=simulate(N,K,rng)
    Xb=zx(BASE); Xi=zx(np.column_stack([BASE,INT]))
    r2b,pb=nested_r2(Xb,Y,pid); r2i,pi=nested_r2(Xi,Y,pid); d=r2i-r2b
    uw=np.unique(pid); byw={w:np.where(pid==w)[0] for w in uw}
    boot=[]
    for _ in range(150):
        pick=rng.choice(uw,len(uw),replace=True); ix=np.concatenate([byw[w] for w in pick])
        boot.append(r2_of(pi[ix],Y[ix])-r2_of(pb[ix],Y[ix]))
    return d, np.percentile(boot,2.5)
def power_at(N,K):
    rng=np.random.default_rng(SEED+N*7+K)
    hits=0
    for _ in range(REPS):
        d,lo=detect(N,K,rng)
        if d>PASS and lo>0: hits+=1
    return hits/REPS
def find_N(K,grid_N):
    curve={}
    for N in grid_N:
        p=power_at(N,K); curve[N]=round(p,3); log(f"  K={K} N={N:<5} power={p:.2f}")
    return curve
def crossings(curve,targets=(0.8,0.9,0.95)):
    xs=sorted(curve); out={}
    for t in targets:
        Nc=None
        for i in range(len(xs)-1):
            a,b=xs[i],xs[i+1]
            if curve[a]<t<=curve[b] or curve[a]>=t:
                if curve[a]>=t: Nc=a; break
                Nc=int(a+(b-a)*(t-curve[a])/(curve[b]-curve[a]+1e-9)); break
        out[str(t)]=Nc if Nc else (xs[-1] if curve[xs[-1]]>=t else None)
    return out
res={"tau":TAU,"pass":PASS,"arms":A,"spread":SPREAD,"reps":REPS,"designs":{}}
log(f"=== SPREAD={SPREAD} ARMS={A} REPS={REPS} tau={TAU} ===")
for K,gridN in [(1,[600,1200,2400,4000,6000]),(6,[150,300,500,800,1200])]:
    log(f"--- K={K} ({'between-subjects' if K==1 else 'repeated-measures'}) ---")
    curve=find_N(K,gridN); cx=crossings(curve)
    res["designs"][f"K{K}"]={"curve":curve,"N_for_power":cx}
    log(f"  N for 80/90/95%: {cx}")
json.dump(res,open(OUT,"w"),indent=1); log(f"wrote {OUT}")

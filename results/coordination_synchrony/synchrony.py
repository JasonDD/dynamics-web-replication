#!/usr/bin/env python3
"""Character SYNCHRONY as a coordinated-inauthentic-behaviour (CIB) signal.

Coordinated pool : IRA political troll tweets (known state operation, many accounts, timestamps).
Organic baseline : Reddit ChangeMyView winning-args comments (thousands of independent authors,
                   threaded = shared-topic units, timestamps).

Pure analysis on already-scored 8-axis character. No new scoring. numpy only.

Three synchrony ideas, honest about the house-style confound:
  A. ACCOUNT-IDENTITY INDEX (flagship, domain-internal permutation control):
     within a pool, are the accounts statistically INTERCHANGEABLE (coordinated) or do they
     carry individual character identity (organic)? I = observed between-account dispersion /
     dispersion under a within-pool post->account shuffle. I~1 => interchangeable (coordinated).
     I>>1 => distinct individuals. Each pool is compared to its OWN shuffle, so platform / length /
     mean-location all cancel -> this sidesteps the Twitter-vs-Reddit domain confound.
  B. CROSS-POOL clustering tightness with matched posts-per-account + matched pool size
     (bootstrap null of organic pools). Effect size = z of IRA vs organic-pool null.
  C. TOPIC/TIME-CONDITIONED cross-account variance: on a shared context (IRA day / CMV thread),
     is cross-account character variance abnormally low? Distribution + Cohen's d + unit AUC.
"""
import os, json, csv, collections, datetime as dt, numpy as np

DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
rng = np.random.default_rng(1729)
IRA = "the internal corpus store/ira_troll"
CMV = "the internal corpus store/cmv_winning_args"

def vec(ch): return np.array([ch[a] for a in DWEB], float)

# ---------- load IRA (coordinated) ----------
scored = [json.loads(l) for l in open(f"{IRA}/work/scored.jsonl")]
ira_sc = {r["id"].split("ira_")[1]: r for r in scored if r.get("kind")=="ira"}
ira = []  # (account, day, category, vec)
for f in ["IRAhandle_tweets_1.csv","IRAhandle_tweets_2.csv"]:
    with open(f"{IRA}/{f}", newline="") as fh:
        for row in csv.DictReader(fh):
            tid = row["tweet_id"]
            if tid not in ira_sc: continue
            try: d = dt.datetime.strptime(row["publish_date"],"%m/%d/%Y %H:%M").date()
            except Exception: d = None
            ira.append((row["author"], d, row["account_category"], vec(ira_sc[tid]["char"])))

# ---------- load CMV (organic) ----------
utt = {}
for l in open(f"{CMV}/winning-args-corpus/utterances.jsonl"):
    dd = json.loads(l); utt[dd["id"]] = dd
cmv = []  # (author, day, thread, vec)
for l in open(f"{CMV}/cmv_scores.jsonl"):
    r = json.loads(l); u = utt.get(r["id"])
    if not u or "char" not in r or not all(a in r["char"] for a in DWEB): continue
    a = u.get("user")
    if not a or a == "[deleted]": continue
    ts = u.get("timestamp"); day = dt.datetime.utcfromtimestamp(ts).date() if ts else None
    cmv.append((a, day, u.get("root"), vec(r["char"])))

print(f"IRA posts {len(ira)}  accounts {len({r[0] for r in ira})}")
print(f"CMV posts {len(cmv)}  authors  {len({r[0] for r in cmv})}")

# ---------- z-scoring + PC1 from the union of scored points (self-contained) ----------
allv = np.array([r[3] for r in ira] + [r[3] for r in cmv], float)
MEAN, STD = allv.mean(0), allv.std(0) + 1e-9
_,_,Vt = np.linalg.svd((allv-MEAN)/STD, full_matrices=False); PC1 = Vt[0]
if (PC1[DWEB.index("rigour")]+PC1[DWEB.index("depth")]) < 0: PC1 = -PC1
def z(v): return (v-MEAN)/STD
def pc1(v): return float(z(v) @ PC1)
AFF = DWEB.index("affect")

def by_account(rows):
    d = collections.defaultdict(list)
    for a,day,top,v in rows: d[a].append(z(v))
    return {a: np.array(vs) for a,vs in d.items()}

ira_acc = by_account(ira)   # account -> (n,8) z-scored
cmv_acc = by_account(cmv)

# ================= METRIC A: ACCOUNT-IDENTITY INDEX (within-pool permutation) =================
def identity_index(acc, k, nperm=500, npoolsamp=40):
    """accounts with >=k posts, each subsampled to exactly k. Between-account dispersion =
    mean ||account_centroid - pool_centroid||. Permutation null: reshuffle post->account labels.
    Returns I = obs/perm_mean, p, per-axis variance ratio (obs_between_var/perm_between_var)."""
    keep = {a: v for a,v in acc.items() if len(v) >= k}
    accounts = list(keep)
    obs_D=[]; obs_axis=[]
    for _ in range(npoolsamp):
        cent=[];
        for a in accounts:
            v = keep[a]; idx = rng.choice(len(v), k, replace=False); cent.append(v[idx].mean(0))
        cent = np.array(cent)
        obs_D.append(np.linalg.norm(cent - cent.mean(0), axis=1).mean())
        obs_axis.append(cent.var(0))              # between-account variance per axis
    obs_D = np.mean(obs_D); obs_axis = np.mean(obs_axis,0)
    # permutation: pool all k*Naccts posts, randomly re-partition into accounts of size k
    perm_D=[]; perm_axis=[]
    for _ in range(nperm):
        pool = np.array([keep[a][rng.choice(len(keep[a]),k,replace=False)] for a in accounts]).reshape(-1,8)
        rng.shuffle(pool)
        cent = pool.reshape(len(accounts),k,8).mean(1)
        perm_D.append(np.linalg.norm(cent-cent.mean(0),axis=1).mean())
        perm_axis.append(cent.var(0))
    perm_D=np.array(perm_D); perm_axis=np.array(perm_axis).mean(0)
    I = obs_D/perm_D.mean()
    p = float((perm_D >= obs_D).mean())          # organic: obs high -> p small
    return dict(naccts=len(accounts), k=k, obs_D=obs_D, perm_D=perm_D.mean(),
                I=I, p=p, axis_ratio=obs_axis/(perm_axis+1e-12))

print("\n================= METRIC A: ACCOUNT-IDENTITY INDEX =================")
print("I = between-account dispersion / within-pool-shuffle dispersion.  I~1 => interchangeable accounts (coordinated).  I>>1 => individual identities (organic).")
A={}
for k in (5,10):
    for name,acc in (("IRA",ira_acc),("CMV",cmv_acc)):
        r=identity_index(acc,k); A[(name,k)]=r
        print(f"  {name:3} k={k:2}  accts={r['naccts']:4}  obsD={r['obs_D']:.3f}  permD={r['perm_D']:.3f}  I={r['I']:.3f}  p(perm>=obs)={r['p']:.3f}")
print("  per-axis obs/perm between-account variance ratio (k=5): 1=interchangeable, >1=individual")
for name in ("IRA","CMV"):
    ar=A[(name,5)]["axis_ratio"]
    print(f"    {name}: "+"  ".join(f"{ax}={ar[i]:.2f}" for i,ax in enumerate(DWEB)))

# ================= METRIC B: CROSS-POOL clustering tightness (matched k, matched N, bootstrap) =================
print("\n================= METRIC B: CROSS-POOL clustering tightness =================")
def pool_dispersion(acc, accounts, k):
    cent = np.array([acc[a][rng.choice(len(acc[a]),k,replace=False)].mean(0) for a in accounts])
    return np.linalg.norm(cent-cent.mean(0),axis=1).mean()
for k in (5,10):
    ira_ok=[a for a,v in ira_acc.items() if len(v)>=k]
    cmv_ok=[a for a,v in cmv_acc.items() if len(v)>=k]
    N=len(ira_ok)
    ira_D=np.mean([pool_dispersion(ira_acc,ira_ok,k) for _ in range(40)])
    null=np.array([pool_dispersion(cmv_acc, list(rng.choice(cmv_ok,N,replace=False)), k) for _ in range(1000)])
    zsc=(ira_D-null.mean())/null.std(); pct=float((null<=ira_D).mean())
    print(f"  k={k:2}  IRA pool N={N}  IRA_D={ira_D:.3f}  organic-null D={null.mean():.3f}+-{null.std():.3f}  z={zsc:.2f}  IRA percentile={pct*100:.1f}%")

# ================= METRIC C: TOPIC / TIME conditioned cross-account variance =================
print("\n================= METRIC C: TOPIC/TIME-conditioned cross-account synchrony =================")
def context_units(rows, ctx_idx, min_accts=5):
    """group rows by context (day or thread); per context, per-account mean; cross-account SD
    of affect and of PC1. Returns arrays."""
    g = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        ctx = r[ctx_idx]
        if ctx is None: continue
        g[ctx][r[0]].append(r[3])
    aff=[]; p1=[]
    for ctx,accs in g.items():
        if len(accs) < min_accts: continue
        ameans=np.array([z(np.mean(vs,0)) for vs in accs.values()])
        aff.append(ameans[:,AFF].std())
        p1.append(np.array([ameans[i]@PC1 for i in range(len(ameans))]).std())
    return np.array(aff), np.array(p1)

ira_day_aff, ira_day_p1 = context_units(ira, 1)          # IRA grouped by DAY
cmv_thr_aff, cmv_thr_p1 = context_units(cmv, 2)          # CMV grouped by THREAD (shared topic)
cmv_day_aff, cmv_day_p1 = context_units(cmv, 1)          # CMV grouped by DAY (alt matched unit)

def cohend(a,b):
    s=np.sqrt(((len(a)-1)*a.var()+(len(b)-1)*b.var())/(len(a)+len(b)-2)); return (a.mean()-b.mean())/s
def auc(pos,neg):  # AUC that a unit's LOW variance flags it as coordinated -> use -SD as score
    s=np.concatenate([-pos,-neg]); y=np.r_[np.ones(len(pos)),np.zeros(len(neg))]
    o=np.argsort(s); r=np.empty(len(s)); r[o]=np.arange(1,len(s)+1)
    return (r[y==1].sum()-len(pos)*(len(pos)+1)/2)/(len(pos)*len(neg))

for nm,ip,cn,ca in (("affect",ira_day_aff,cmv_thr_aff,cmv_day_aff),("PC1",ira_day_p1,cmv_thr_p1,cmv_day_p1)):
    print(f"  [{nm}] cross-account SD within a shared context:")
    print(f"     IRA/day (n={len(ip)}) median={np.median(ip):.3f}   CMV/thread (n={len(cn)}) median={np.median(cn):.3f}   CMV/day (n={len(ca)}) median={np.median(ca):.3f}")
    print(f"     Cohen d IRA-day vs CMV-thread = {cohend(ip,cn):+.2f}   AUC(low-SD=>coordinated, IRA-day vs CMV-thread) = {auc(ip,cn):.3f}")
    print(f"     Cohen d IRA-day vs CMV-day    = {cohend(ip,ca):+.2f}   AUC(IRA-day vs CMV-day) = {auc(ip,ca):.3f}")

# temporal co-movement snapshot: IRA days with many accounts singing one tune (low SD, extreme mean)
print("\n  temporal co-movement: IRA high-activity days ranked by LOW cross-account affect SD (many accounts, same affect):")
g=collections.defaultdict(list)
for a,day,top,v in ira:
    if day is not None: g[day].append((a,z(v)))
rowsd=[]
for day,items in g.items():
    accs=collections.defaultdict(list)
    for a,zv in items: accs[a].append(zv)
    if len(accs)<10: continue
    am=np.array([np.mean(v,0) for v in accs.values()])
    rowsd.append((day,len(accs),am[:,AFF].mean(),am[:,AFF].std()))
rowsd.sort(key=lambda r:r[3])
for day,n,m,s in rowsd[:6]:
    print(f"     {day}  accounts={n:3}  mean affect(z)={m:+.2f}  cross-account SD={s:.3f}")

# ---- convergent-spike test: are 'many accounts, high affect, low spread' days distinctively IRA? ----
def day_stats(rows, min_accts=10):
    g=collections.defaultdict(lambda: collections.defaultdict(list))
    for a,day,top,v in rows:
        if day is not None: g[day][a].append(z(v))
    out=[]
    for day,accs in g.items():
        if len(accs)<min_accts: continue
        am=np.array([np.mean(v,0) for v in accs.values()])
        out.append((am[:,AFF].mean(), am[:,AFF].std()))
    return np.array(out)
ird=day_stats(ira); cmd=day_stats([(a,d,t,v) for a,d,t,v in cmv])
# organic thresholds
hi=np.percentile(cmd[:,0],90); lo=np.percentile(cmd[:,1],10)
def frac_spike(d): return float(((d[:,0]>=hi)&(d[:,1]<=lo)).mean())
print(f"\n  convergent-spike day test (>=10 accts; spike = mean affect >= organic P90 [{hi:+.2f}] AND cross-acct SD <= organic P10 [{lo:.3f}]):")
print(f"     IRA busy-days n={len(ird)}  spike-fraction={frac_spike(ird)*100:.1f}%")
print(f"     CMV busy-days n={len(cmd)}  spike-fraction={frac_spike(cmd)*100:.1f}%  (organic self-reference ~ few %)")
print(f"     IRA busy-day mean affect(z)={ird[:,0].mean():+.2f} vs CMV={cmd[:,0].mean():+.2f}; IRA affect-SD median={np.median(ird[:,1]):.3f} vs CMV={np.median(cmd[:,1]):.3f}")

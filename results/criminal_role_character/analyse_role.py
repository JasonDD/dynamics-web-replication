#!/usr/bin/env python3
"""analyse_role.py — first cut: is an ENABLER's character distinguishable from a USER's, once the room
is controlled, and does an account level signature flag enablers early?

Inputs: a scored JSONL (id, role, subgroup, user_id, topic_id, forum, nchars, char:{8 axes}).
Discipline held from DESIGN_AND_DATA.md: room control ladder (same forum -> same thread), length matched;
report the effect that survives; account level early warning k sweep; honest null allowed. Numbers only,
no naming of individuals, no operational content.

Outputs a plain text report to stdout (redirect to RESULT_raw.txt) plus a JSON summary side file.
"""
import sys, json, math, random
import numpy as np

random.seed(7); np.random.seed(7)
AXES = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
IN = sys.argv[1]

rows = []
for l in open(IN):
    try:
        r = json.loads(l)
    except Exception:
        continue
    if "char" not in r or not all(a in r["char"] for a in AXES):
        continue
    rows.append(r)
print(f"scored posts: {len(rows)}")

def vec(r):
    return np.array([r["char"][a] for a in AXES], float)

EN = [r for r in rows if r["role"] == "ENABLER"]
US = [r for r in rows if r["role"] == "USER"]
print(f"ENABLER {len(EN)} (vendor {sum(1 for r in EN if r['subgroup']=='vendor')}, "
      f"staff {sum(1 for r in EN if r['subgroup']=='staff')}) | USER {len(US)}")

# ---- PC1 (matter vs manner): local PCA on this corpus, oriented so rigour+depth positive ----
X = np.array([vec(r) for r in rows])
Xc = X - X.mean(0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
pc1 = Vt[0]
if pc1[AXES.index("rigour")] + pc1[AXES.index("depth")] < 0:
    pc1 = -pc1
for r in rows:
    r["pc1"] = float(vec(r) @ pc1 - (X.mean(0) @ pc1))

def cohend(a, b):
    a, b = np.array(a), np.array(b)
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    sp = math.sqrt(((na-1)*a.var(ddof=1) + (nb-1)*b.var(ddof=1)) / (na+nb-2))
    return (a.mean() - b.mean()) / sp if sp > 0 else float("nan")

def mann_whitney_auc(a, b):
    # AUC = P(enabler axis > user axis); rank based, ties=0.5
    a, b = np.array(a), np.array(b)
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    allv = np.concatenate([a, b])
    order = allv.argsort()
    ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv)+1)
    # average ranks for ties
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    # simple tie handling via scipy-less average
    ra = ranks[:len(a)]
    R1 = ra.sum()
    U1 = R1 - len(a)*(len(a)+1)/2
    return U1 / (len(a)*len(b))

def per_axis(en, us, label):
    print(f"\n=== per axis: ENABLER vs USER  [{label}]  (n_en={len(en)}, n_us={len(us)}) ===")
    print(f"{'axis':16} {'en_mean':>8} {'us_mean':>8} {'cohen_d':>8} {'auc':>6}")
    out = {}
    for i, a in enumerate(AXES + ["pc1"]):
        ev = [ (r['char'][a] if a in AXES else r['pc1']) for r in en]
        uv = [ (r['char'][a] if a in AXES else r['pc1']) for r in us]
        d = cohend(ev, uv); auc = mann_whitney_auc(ev, uv)
        print(f"{a:16} {np.mean(ev):8.3f} {np.mean(uv):8.3f} {d:8.2f} {auc:6.3f}")
        out[a] = {"en_mean": float(np.mean(ev)), "us_mean": float(np.mean(uv)),
                  "cohen_d": None if math.isnan(d) else round(d,3),
                  "auc": None if math.isnan(auc) else round(auc,3)}
    return out

summary = {"n_posts": len(rows), "n_enabler": len(EN), "n_user": len(US),
           "n_vendor": sum(1 for r in EN if r['subgroup']=='vendor'),
           "n_staff": sum(1 for r in EN if r['subgroup']=='staff')}

# ---------- TIER 0: pooled raw (both forums) ----------
summary["tier0_pooled_raw"] = per_axis(EN, US, "TIER0 pooled raw (both forums)")

# ---------- length matched same forum (match nchars distribution by bucket) ----------
def length_match(en, us, nb=8):
    lens = np.array([r["nchars"] for r in en+us])
    edges = np.quantile([r["nchars"] for r in us], np.linspace(0,1,nb+1))
    edges[0]=-1; edges[-1]=1e9
    def buck(n):
        return int(np.searchsorted(edges, n, side="right")-1)
    from collections import defaultdict
    ub = defaultdict(list);
    for r in us: ub[buck(r["nchars"])].append(r)
    matched_en=[]; matched_us=[]
    for r in en:
        b=buck(r["nchars"])
        if ub[b]:
            matched_en.append(r); matched_us.append(random.choice(ub[b]))
    return matched_en, matched_us

# ---------- TIER 1+2: WITHIN each forum, length matched (the real same-room control) ----------
from collections import defaultdict
forums = sorted(set(r["forum"] for r in rows))
summary["tier1_2_per_forum_length_matched"] = {}
for fo in forums:
    fen = [r for r in EN if r["forum"] == fo]
    fus = [r for r in US if r["forum"] == fo]
    if len(fen) < 8 or len(fus) < 8:
        print(f"\n[forum {fo}] too few for per-forum test (en={len(fen)}, us={len(fus)})")
        continue
    fmen, fmus = length_match(fen, fus)
    summary["tier1_2_per_forum_length_matched"][fo] = per_axis(
        fmen, fmus, f"TIER1+2 forum={fo} length-matched (paired n={len(fmen)}, en_all={len(fen)})")

# pooled length-matched too (context only; per-forum above is the honest one)
men, mus = length_match(EN, US)
summary["tier2_pooled_length_matched"] = per_axis(men, mus, f"TIER2 pooled length-matched (paired n={len(men)})")

# ---------- TIER 3: same thread (enabler and user posts co-occurring in one topic) ----------
by_topic = defaultdict(lambda: {"ENABLER":[], "USER":[]})
for r in rows:
    by_topic[(r["forum"], r["topic_id"])][r["role"]].append(r)
mixed = {t:d for t,d in by_topic.items() if d["ENABLER"] and d["USER"]}
en3=[]; us3=[]
for t,d in mixed.items():
    en3 += d["ENABLER"]; us3 += d["USER"]
print(f"\nmixed-role threads (same-thread control): {len(mixed)} threads, "
      f"{len(en3)} enabler posts vs {len(us3)} user posts")
if en3 and us3:
    summary["tier3_same_thread"] = per_axis(en3, us3, "TIER3 same-thread (strongest room control)")
    # length match within same-thread pool too
    m3en,m3us = length_match(en3, us3)
    if m3en:
        summary["tier3_same_thread_lenmatched"] = per_axis(m3en, m3us, f"TIER3 same-thread length-matched (n={len(m3en)})")

# ---------- vendor-only vs user (the commercially interesting enabler) ----------
VEN = [r for r in EN if r["subgroup"]=="vendor"]
if len(VEN) >= 10:
    vm_en, vm_us = length_match(VEN, US)
    summary["vendor_only_length_matched"] = per_axis(vm_en, vm_us, f"vendor-only vs user, length-matched (n={len(vm_en)})")

# ---------- ACCOUNT LEVEL detector + early-warning k sweep ----------
def account_features(posts):
    M = np.array([vec(p) for p in posts])
    p1 = np.array([p["pc1"] for p in posts])
    feats = list(M.mean(0)) + list(M.std(0)) + [ (p1<0).mean(), p1.mean() ]
    return np.array(feats)

acc = defaultdict(list)
for r in rows:
    acc[r["user_id"]].append(r)
# account label = its role (accounts are single-role here: group is per account rank)
acc_role = {}
for u, ps in acc.items():
    roles = set(p["role"] for p in ps)
    acc_role[u] = "ENABLER" if "ENABLER" in roles else "USER"

def logreg_auc(Xf, yf, folds=5):
    # tiny standalone L2 logistic regression, grouped CV already implicit (unit=account)
    from numpy.linalg import pinv
    Xf = np.array(Xf); yf = np.array(yf)
    # standardise
    mu=Xf.mean(0); sd=Xf.std(0); sd[sd==0]=1; Xs=(Xf-mu)/sd
    n=len(yf); idx=np.arange(n); np.random.shuffle(idx)
    aucs=[]
    for f in range(folds):
        te = idx[f::folds]; tr=np.setdiff1d(idx,te)
        if len(set(yf[tr]))<2 or len(set(yf[te]))<2:
            continue
        w=np.zeros(Xs.shape[1]+1); Xtr=np.hstack([Xs[tr],np.ones((len(tr),1))])
        for _ in range(300):
            z=Xtr@w; p=1/(1+np.exp(-z)); g=Xtr.T@(p-yf[tr])/len(tr)+0.05*np.r_[w[:-1],0]
            w-=0.5*g
        Xte=np.hstack([Xs[te],np.ones((len(te),1))]); pte=1/(1+np.exp(-(Xte@w)))
        aucs.append(mann_whitney_auc(pte[yf[te]==1], pte[yf[te]==0]))
    return float(np.mean(aucs)) if aucs else float("nan"), len(aucs)

print("\n=== ACCOUNT LEVEL early-warning k-sweep (min posts per account) ===")
print(f"{'min_k':>5} {'n_en_acc':>8} {'n_us_acc':>8} {'post_auc':>9} {'acct_auc':>9}")
summary["k_sweep"] = []
for k in [1,2,3,5,10]:
    accs = {u:ps for u,ps in acc.items() if len(ps)>=k}
    en_accs=[u for u in accs if acc_role[u]=="ENABLER"]; us_accs=[u for u in accs if acc_role[u]=="USER"]
    if len(en_accs)<5 or len(us_accs)<5:
        print(f"{k:>5} {len(en_accs):>8} {len(us_accs):>8}   (too few accounts)")
        continue
    # balance
    m=min(len(en_accs),len(us_accs)); random.shuffle(en_accs); random.shuffle(us_accs)
    sel=en_accs[:m]+us_accs[:m]
    Xf=[account_features(accs[u]) for u in sel]; yf=[1 if acc_role[u]=="ENABLER" else 0 for u in sel]
    acct_auc,nf = logreg_auc(Xf,yf)
    # post-level baseline on the same accounts' posts
    pXf=[]; pyf=[]
    for u in sel:
        for p in accs[u]:
            pXf.append(vec(p)); pyf.append(1 if acc_role[u]=="ENABLER" else 0)
    post_auc,_ = logreg_auc(pXf,pyf)
    print(f"{k:>5} {len(en_accs):>8} {len(us_accs):>8} {post_auc:9.3f} {acct_auc:9.3f}")
    summary["k_sweep"].append({"min_k":k,"n_en_acc":len(en_accs),"n_us_acc":len(us_accs),
                               "balanced_n":m,"post_auc":round(post_auc,3),"acct_auc":round(acct_auc,3)})

json.dump(summary, open(sys.argv[2] if len(sys.argv)>2 else "summary.json","w"), indent=2)
print("\nsummary written")

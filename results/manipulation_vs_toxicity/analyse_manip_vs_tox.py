#!/usr/bin/env python3
"""analyse_manip_vs_tox.py — head to head: our 8-axis manipulation detector vs the
incumbent toxicity tools (Detoxify original / unitary toxic-bert = the Jigsaw/Perspective
reproduction; s-nlp roberta toxicity = cross-family comparator), tested BOTH ways.

OUR detector: logistic on the 8 DYNAMICS-WEB axes, trained on IRA political trolls (manip=1)
vs Change My View sincere winning arguments (manip=0). Applied OUT OF DOMAIN to dark patterns,
phishing and the toxicity corpus (none in training, so no leakage on those).

Tasks:
  1. MANIPULATION task (dark: dark vs normal; phish: phish vs safe; pooled): AUC of ours vs
     each toxicity tool. Plus the miss rate: fraction of manipulation content the toxicity
     tools rate below their 0.5 flag threshold.
  2. TOXICITY task (civil_comments gold labels): AUC of the toxicity tools vs ours.
  3. Orthogonality: corr(our manip prob, toxicity) on the combined pool + 2x2 quadrant sizes,
     the low-toxicity + high-manipulation quadrant being the product gap.
"""
import os, json, numpy as np

internal store = "the internal corpus store"
DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
rng = np.random.default_rng(1729)

def load_jsonl(p):
    out = []
    for l in open(p):
        try:
            out.append(json.loads(l))
        except Exception:
            pass
    return out

def has_char(r):
    return "char" in r and all(a in r["char"] for a in DWEB)

# ---------- 8-axis char per corpus ----------
POL = {"RightTroll", "LeftTroll", "Fearmonger"}
ira_all = load_jsonl(f"{internal store}/ira_troll/work/scored.jsonl")
ira = [r for r in ira_all if r.get("kind") == "ira" and r.get("outcome") in POL and has_char(r)]
cmv = [r for r in load_jsonl(f"{internal store}/cmv_winning_args/cmv_scores.jsonl") if has_char(r)]

mi = [r for r in load_jsonl(f"{internal store}/manner_inflation/scored.jsonl") if has_char(r)]
dark = [r for r in mi if r.get("kind") == "dark"]
phish = [r for r in mi if r.get("kind") == "phish"]

tox_char = {r["id"]: r for r in load_jsonl(f"{internal store}/toxicity_civilcomments/scored.jsonl") if has_char(r)}
tox_gold = {r["id"]: r["gold"] for r in load_jsonl(f"{internal store}/toxicity_civilcomments/input.jsonl")}

def X(rows):
    return np.array([[r["char"][a] for a in DWEB] for r in rows], float)

# ---------- our manipulation detector: logistic on the 8 axes ----------
# The product detector is trained on manipulation (positive) vs honest (negative) across
# domains. Manipulation-task AUCs are LEAVE-ONE-DOMAIN-OUT (train on the other domains, test
# the held-out one) so a domain's number never comes from a model that saw it.
def fit_logistic(Xs, y, iters=2000, lr=0.3, l2=1e-3):
    n, d = Xs.shape
    w = np.zeros(d); b = 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(Xs @ w + b)))
        g = p - y
        w -= lr * (Xs.T @ g / n + l2 * w)
        b -= lr * g.mean()
    return w, b

# domain -> (manipulation rows, honest rows)
dark_pos = [r for r in dark if r["outcome"] == "dark"]; dark_neg = [r for r in dark if r["outcome"] == "normal"]
phish_pos = [r for r in phish if r["outcome"] == "phish"]; phish_neg = [r for r in phish if r["outcome"] == "safe"]
DOMAINS = {"ira": (ira, cmv), "dark": (dark_pos, dark_neg), "phish": (phish_pos, phish_neg)}

def make_model(pos_rows, neg_rows):
    Xt = np.vstack([X(pos_rows), X(neg_rows)])
    y = np.hstack([np.ones(len(pos_rows)), np.zeros(len(neg_rows))])
    mu = Xt.mean(0); sd = Xt.std(0) + 1e-9
    w, b = fit_logistic((Xt - mu) / sd, y)
    return mu, sd, w, b

def apply_model(model, rows):
    if len(rows) == 0:
        return np.array([])
    mu, sd, w, b = model
    Z = (X(rows) - mu) / sd
    return 1.0 / (1.0 + np.exp(-(Z @ w + b)))

# leave-one-domain-out models (for each domain, train on the other two domains' pools)
LODO = {}
for d in DOMAINS:
    pos = sum((DOMAINS[o][0] for o in DOMAINS if o != d), [])
    neg = sum((DOMAINS[o][1] for o in DOMAINS if o != d), [])
    LODO[d] = make_model(pos, neg)

# full product model (all three domains) — used out of domain on the toxicity corpus
ALLPOS = sum((v[0] for v in DOMAINS.values()), []); ALLNEG = sum((v[1] for v in DOMAINS.values()), [])
FULL = make_model(ALLPOS, ALLNEG)

# IRA-only flagship model (the published AUC 0.925 detector) — for the transfer note
IRAONLY = make_model(ira, cmv)

def cv_auc(pos_rows, neg_rows, k=5):
    """balanced 5-fold CV AUC, in-domain (numpy logistic)."""
    XP = X(pos_rows); XN = X(neg_rows)
    n = min(len(XP), len(XN))
    ip = rng.permutation(len(XP))[:n]; iN = rng.permutation(len(XN))[:n]
    Xa = np.vstack([XP[ip], XN[iN]]); ya = np.hstack([np.ones(n), np.zeros(n)])
    pm = rng.permutation(len(ya)); Xa = Xa[pm]; ya = ya[pm]
    folds = np.array_split(np.arange(len(ya)), k); aucs = []
    for f in range(k):
        te = folds[f]; tr = np.hstack([folds[j] for j in range(k) if j != f])
        mu = Xa[tr].mean(0); sd = Xa[tr].std(0) + 1e-9
        w, b = fit_logistic((Xa[tr] - mu) / sd, ya[tr])
        s = 1.0 / (1.0 + np.exp(-(((Xa[te] - mu) / sd) @ w + b)))
        aucs.append(auc(ya[te], s))
    return float(np.mean(aucs)), float(np.std(aucs))

def manip_prob(rows):
    """Default = full product model (used for the toxicity corpus, out of domain)."""
    return apply_model(FULL, rows)

def auc(y, s):
    y = np.asarray(y); s = np.asarray(s, float)
    pos = (y == 1); neg = (y == 0)
    if pos.sum() == 0 or neg.sum() == 0:
        return float("nan")
    order = np.argsort(s, kind="mergesort")
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt); ranks = ((csum - cnt + 1) + csum) / 2.0
    r = ranks[inv]
    return (r[pos].sum() - pos.sum() * (pos.sum() + 1) / 2.0) / (pos.sum() * neg.sum())

# ---------- toxicity tool scores, joined by id ----------
detox = {r["id"]: r for r in load_jsonl(f"{internal store}/manip_vs_tox/detox_scores.jsonl")}

def join_scores(rows, model=None):
    """Return (manip_prob, detox_tox, snlp_tox, kept rows) for rows that have all three.
    model overrides the default full product model (used to pass a leave-one-out model)."""
    mp = apply_model(model, rows) if model is not None else manip_prob(rows)
    out_m, out_d, out_s, keep = [], [], [], []
    for i, r in enumerate(rows):
        d = detox.get(r["id"])
        if d is None:
            continue
        out_m.append(mp[i]); out_d.append(d["detox_tox"]); out_s.append(d["snlp_tox"]); keep.append(r)
    return np.array(out_m), np.array(out_d), np.array(out_s), keep

print("=== corpus sizes (8-axis scored) ===")
print(f"  IRA political (train+)   n={len(ira)}")
print(f"  CMV sincere  (train-)    n={len(cmv)}")
print(f"  dark patterns            n={len(dark)}  (dark={sum(r['outcome']=='dark' for r in dark)}, normal={sum(r['outcome']=='normal' for r in dark)})")
print(f"  phishing                 n={len(phish)} (phish={sum(r['outcome']=='phish' for r in phish)}, safe={sum(r['outcome']=='safe' for r in phish)})")
print(f"  toxicity (civil comments) n={len(tox_char)} (gold toxic={sum(tox_gold.get(i,0)==1 for i in tox_char)})")

# ================= TASK 1: MANIPULATION =================
print("\n" + "=" * 70)
print("TASK 1 — MANIPULATION DETECTION (deceptive vs matched honest control)")
print("=" * 70)
print("OURS = leave-one-domain-out product detector (trained on the OTHER manipulation domains)")
print(f"{'domain':<22}{'n':>7}{'OURS':>9}{'Detoxify':>10}{'s-nlp':>9}")

def manip_domain(rows, pos_label, neg_label, name, model):
    m, d, s, keep = join_scores(rows, model=model)
    y = np.array([1 if r["outcome"] == pos_label else (0 if r["outcome"] == neg_label else -1) for r in keep])
    mask = y >= 0
    y = y[mask]; m = m[mask]; d = d[mask]; s = s[mask]
    a_ours, a_det, a_snlp = auc(y, m), auc(y, d), auc(y, s)
    print(f"{name:<22}{len(y):>7}{a_ours:>9.3f}{a_det:>10.3f}{a_snlp:>9.3f}")
    return y, m, d, s, a_ours, a_det, a_snlp

d_y, d_m, d_d, d_s, *_ = manip_domain(dark, "dark", "normal", "dark patterns", LODO["dark"])
p_y, p_m, p_d, p_s, *_ = manip_domain(phish, "phish", "safe", "phishing", LODO["phish"])
# pooled dark+phish
pool_y = np.hstack([d_y, p_y]); pool_m = np.hstack([d_m, p_m]); pool_d = np.hstack([d_d, p_d]); pool_s = np.hstack([d_s, p_s])
print(f"{'POOLED dark+phish':<22}{len(pool_y):>7}{auc(pool_y,pool_m):>9.3f}{auc(pool_y,pool_d):>10.3f}{auc(pool_y,pool_s):>9.3f}")

# IRA (flagship): leave-one-out model (trained on dark+phish) vs toxicity, political trolls with detox
im, idd, iss, ikeep = join_scores(ira[:4000], model=LODO["ira"])
print(f"\nIRA political trolls (flagship manipulation), n={len(ikeep)} with toxicity scores:")
print(f"  mean OUR manip prob = {im.mean():.3f} | mean Detoxify = {idd.mean():.3f} | mean s-nlp = {iss.mean():.3f}")

# IRA in-domain flagship AUC (self-contained reproduction of the published number)
ira_cv_m, ira_cv_s = cv_auc(ira, cmv)
print(f"\nIRA in-domain flagship (5-fold CV, IRA vs CMV sincere): AUC = {ira_cv_m:.3f} +/- {ira_cv_s:.3f}")

# transfer note: the published IRA-only flagship detector applied to the other domains
print("--- transfer of the IRA-only flagship detector (cross-domain, target domain unseen) ---")
for nm, pos_rows, neg_rows in [("dark vs normal", dark_pos, dark_neg), ("phish vs safe", phish_pos, phish_neg)]:
    yy = np.hstack([np.ones(len(pos_rows)), np.zeros(len(neg_rows))])
    ss = np.hstack([apply_model(IRAONLY, pos_rows), apply_model(IRAONLY, neg_rows)])
    print(f"  IRA-only model on {nm:<16} AUC = {auc(yy, ss):.3f}")

# ---- the miss rate: manipulation content below the toxicity flag threshold (0.5) ----
print("\n--- incumbent MISS RATE: fraction of manipulation content below toxicity flag 0.5 ---")
def miss(name, det, snl):
    print(f"  {name:<26} Detoxify<0.5: {(det<0.5).mean()*100:5.1f}%   s-nlp<0.5: {(snl<0.5).mean()*100:5.1f}%   (n={len(det)})")
miss("dark patterns (dark)", d_d[d_y==1], d_s[d_y==1])
miss("phishing (phish)", p_d[p_y==1], p_s[p_y==1])
miss("IRA political trolls", idd, iss)
allmanip_d = np.hstack([d_d[d_y==1], p_d[p_y==1], idd]); allmanip_s = np.hstack([d_s[d_y==1], p_s[p_y==1], iss])
miss("ALL manipulation pooled", allmanip_d, allmanip_s)

# ================= TASK 2: TOXICITY =================
print("\n" + "=" * 70)
print("TASK 2 — TOXICITY DETECTION (civil_comments gold labels) — their home turf")
print("=" * 70)
tox_rows = list(tox_char.values())
tm, td, ts, tkeep = join_scores(tox_rows)
tg = np.array([tox_gold.get(r["id"], 0) for r in tkeep])
print(f"{'tool':<26}{'AUC':>9}")
print(f"{'OURS (manip prob)':<26}{auc(tg,tm):>9.3f}")
print(f"{'Detoxify':<26}{auc(tg,td):>9.3f}")
print(f"{'s-nlp roberta':<26}{auc(tg,ts):>9.3f}")
print(f"  (n={len(tg)}, gold toxic={int(tg.sum())})")

# ================= TASK 3: ORTHOGONALITY / 2x2 =================
print("\n" + "=" * 70)
print("TASK 3 — ORTHOGONALITY (our manipulation axis vs their toxicity axis)")
print("=" * 70)
# The 2x2 and correlation describe the DEPLOYED detector: the full product model (trained on
# all three manipulation domains), in-sample on the manipulation domains and out of sample on
# the toxicity corpus. The leakage-free generalisation evidence is the AUC table above; here we
# characterise how the shipped tool's flags land against the toxicity tools' flags.
fd_m, fd_d, fd_s, fd_keep = join_scores(dark, model=FULL)
fp_m, fp_d, fp_s, fp_keep = join_scores(phish, model=FULL)
fi_m, fi_d, fi_s, fi_keep = join_scores(ira[:4000], model=FULL)
fd_y = np.array([1 if r["outcome"] == "dark" else 0 for r in fd_keep])
fp_y = np.array([1 if r["outcome"] == "phish" else 0 for r in fp_keep])
# combined pool: all rows with both scores (full model manip prob)
allm = np.hstack([fd_m, fp_m, fi_m, tm]); alld = np.hstack([fd_d, fp_d, fi_d, td]); alls = np.hstack([fd_s, fp_s, fi_s, ts])

def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])
def pearson(a, b):
    return float(np.corrcoef(a, b)[0, 1])
print(f"combined pool n={len(allm)}")
print(f"  Pearson  corr(OUR manip, Detoxify) = {pearson(allm,alld):+.3f} | corr(OUR manip, s-nlp) = {pearson(allm,alls):+.3f}")
print(f"  Spearman corr(OUR manip, Detoxify) = {spearman(allm,alld):+.3f} | corr(OUR manip, s-nlp) = {spearman(allm,alls):+.3f}")

# 2x2 quadrants at thresholds: toxicity 0.5 (standard); ours at 0.5 (logistic boundary)
def quad(manip, tox, mt=0.5, tt=0.5):
    hm = manip >= mt; ht = tox >= tt
    n = len(manip)
    q = {"lowT_lowM": int((~ht & ~hm).sum()), "lowT_highM": int((~ht & hm).sum()),
         "highT_lowM": int((ht & ~hm).sum()), "highT_highM": int((ht & hm).sum())}
    return q, n
print("\n2x2 on the COMBINED pool (toxicity>=0.5 = flagged toxic; our manip prob>=0.5 = flagged manipulative):")
for tool, tox in [("Detoxify", alld), ("s-nlp", alls)]:
    q, n = quad(allm, tox)
    print(f"  {tool}: low-tox/low-manip {q['lowT_lowM']} ({q['lowT_lowM']/n*100:.1f}%) | "
          f"LOW-TOX/HIGH-MANIP {q['lowT_highM']} ({q['lowT_highM']/n*100:.1f}%) [the gap only we catch] | "
          f"high-tox/low-manip {q['highT_lowM']} ({q['highT_lowM']/n*100:.1f}%) | "
          f"high-tox/high-manip {q['highT_highM']} ({q['highT_highM']/n*100:.1f}%)")

# 2x2 restricted to the MANIPULATION corpora only (the commercial signal), full deployed model
print("\n2x2 restricted to MANIPULATION content (dark+phish deceptive + IRA), the product surface:")
mm = np.hstack([fd_m[fd_y==1], fp_m[fp_y==1], fi_m]); mdx = np.hstack([fd_d[fd_y==1], fp_d[fp_y==1], fi_d]); msx = np.hstack([fd_s[fd_y==1], fp_s[fp_y==1], fi_s])
for tool, tox in [("Detoxify", mdx), ("s-nlp", msx)]:
    q, n = quad(mm, tox)
    print(f"  {tool}: LOW-TOX/HIGH-MANIP {q['lowT_highM']} of {n} = {q['lowT_highM']/n*100:.1f}% caught by us + missed by them | "
          f"both flag {q['highT_highM']} ({q['highT_highM']/n*100:.1f}%) | "
          f"we miss too (low-manip) {q['lowT_lowM']+q['highT_lowM']} ({(q['lowT_lowM']+q['highT_lowM'])/n*100:.1f}%)")

# ---- mean scores per corpus (descriptive) ----
print("\n=== mean scores per corpus (0-1) ===")
print(f"{'corpus':<26}{'OUR manip':>11}{'Detoxify':>10}{'s-nlp':>9}")
def meanrow(name, m, d, s):
    print(f"{name:<26}{m.mean():>11.3f}{d.mean():>10.3f}{s.mean():>9.3f}")
meanrow("dark patterns (dark)", d_m[d_y==1], d_d[d_y==1], d_s[d_y==1])
meanrow("normal microcopy", d_m[d_y==0], d_d[d_y==0], d_s[d_y==0])
meanrow("phishing (phish)", p_m[p_y==1], p_d[p_y==1], p_s[p_y==1])
meanrow("safe email", p_m[p_y==0], p_d[p_y==0], p_s[p_y==0])
meanrow("IRA political trolls", im, idd, iss)
meanrow("toxicity: toxic (gold)", tm[tg==1], td[tg==1], ts[tg==1])
meanrow("toxicity: clean (gold)", tm[tg==0], td[tg==0], ts[tg==0])

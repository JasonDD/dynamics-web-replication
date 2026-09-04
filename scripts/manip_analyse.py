#!/usr/bin/env python3
"""manip_analyse.py — state-sponsored manipulation vs sincere argument on the 8-axis
character instrument (DYNAMICS-WEB).

Groups:
  MANIP     = IRA political trolls (RightTroll/LeftTroll/Fearmonger), English, original content
  IRA_OTHER = IRA NewsFeed/Commercial/HashtagGamer (within-IRA heterogeneity, context only)
  SINCERE   = Reddit Change My View winning args (cmv_scores.jsonl)  -- sincere persuasion
  SHORTPOL  = LIAR PolitiFact statements                            -- length-matched short political

Outputs: mean 8-axis + matter/manner PC1 per group; Cohen's d (MANIP vs each baseline);
logistic classifier (numpy, 5-fold CV, balanced) AUC + accuracy for MANIP-vs-SINCERE and
MANIP-vs-SHORTPOL; per-axis standardised coefficients and univariate AUCs (which axes give
manipulation away).

No sklearn: logistic regression, k-fold CV and AUC are implemented in numpy here.
"""
import os, json, numpy as np, psycopg2

DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
W = "the internal corpus store/ira_troll/work"
CMV = "the internal corpus store/cmv_winning_args/cmv_scores.jsonl"
POL = {"RightTroll", "LeftTroll", "Fearmonger"}
OTHER = {"NewsFeed", "Commercial", "HashtagGamer"}
rng = np.random.default_rng(1729)

# ---- matter/manner PC1 (SVD on the web character reference), oriented rigour+depth positive
PW = [l.split("=", 1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
c = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
c.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
allc = np.array([[float(x) for x in r] for r in c.fetchall()], float)
MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
_, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False); PC1 = Vt[0]
if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0:
    PC1 = -PC1
def pc1(ch):
    return float(((np.array([ch[a] for a in DWEB], float) - MEAN) / STD) @ PC1)

def load(path, want=None):
    out = []
    for l in open(path):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if "char" not in r:
            continue
        if not all(a in r["char"] for a in DWEB):
            continue
        if want and not want(r):
            continue
        out.append(r)
    return out

scored = load(f"{W}/scored.jsonl")
manip = [r for r in scored if r.get("kind") == "ira" and r.get("outcome") in POL]
iraother = [r for r in scored if r.get("kind") == "ira" and r.get("outcome") in OTHER]
shortpol = [r for r in scored if r.get("kind") == "liar"]
sincere = load(CMV)

def mat(rows):
    return np.array([[r["char"][a] for a in DWEB] for r in rows], float)

def summ(name, rows):
    if not rows:
        return name, 0, None, None, None, None
    M = mat(rows)
    p = np.array([pc1(r["char"]) for r in rows])
    return name, len(rows), M.mean(0), M.std(0), p.mean(), p.std()

groups = [summ("MANIP (IRA political)", manip),
          summ("SINCERE (CMV args)", sincere),
          summ("SHORTPOL (LIAR)", shortpol),
          summ("IRA_OTHER (news/comm/hashtag)", iraother)]

print("=== group sizes ===")
for n, k, *_ in groups:
    print(f"  {n:<32} n={k}")

print("\n=== mean 8-axis character per group ===")
print("  " + "group".ljust(32) + "".join(a[:5].rjust(8) for a in DWEB) + "     PC1")
for n, k, m, s, pm, ps in groups:
    if k == 0:
        print("  " + n.ljust(32) + "  (empty group — skipped)")
        continue
    print("  " + n.ljust(32) + "".join(f"{v:8.3f}" for v in m) + f"{pm:8.3f}")

def cohend(A, B):
    ma, mb = A.mean(0), B.mean(0)
    va, vb = A.var(0, ddof=1), B.var(0, ddof=1)
    na, nb = len(A), len(B)
    sp = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2) + 1e-12)
    return (ma - mb) / sp

def cohend_1d(a, b):
    va, vb = a.var(ddof=1), b.var(ddof=1)
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2) + 1e-12)
    return (a.mean() - b.mean()) / sp

Amanip = mat(manip); Asin = mat(sincere); Asp = mat(shortpol)
Pman = np.array([pc1(r["char"]) for r in manip])
Psin = np.array([pc1(r["char"]) for r in sincere])
Psp = np.array([pc1(r["char"]) for r in shortpol])

if len(manip) == 0:
    print("\n[abort] MANIP group is empty — scoring has not produced any IRA political rows yet.")
    raise SystemExit(0)

print("\n=== Cohen's d, MANIP minus baseline (positive = manipulation scores HIGHER) ===")
print("  " + "axis".ljust(18) + "vs SINCERE(CMV)".rjust(18) + "vs SHORTPOL(LIAR)".rjust(20))
have_sin = len(sincere) > 0
have_sp = len(shortpol) > 0
dsin = cohend(Amanip, Asin) if have_sin else None
dsp = cohend(Amanip, Asp) if have_sp else None
for i, a in enumerate(DWEB):
    cs = f"{dsin[i]:18.2f}" if have_sin else " " * 14 + "  n/a"
    cp = f"{dsp[i]:20.2f}" if have_sp else " " * 16 + "  n/a"
    print("  " + a.ljust(18) + cs + cp)
cs = f"{cohend_1d(Pman,Psin):18.2f}" if have_sin else " " * 14 + "  n/a"
cp = f"{cohend_1d(Pman,Psp):20.2f}" if have_sp else " " * 16 + "  n/a"
print("  " + "matter/manner PC1".ljust(18) + cs + cp)

# ---------- numpy logistic regression + 5-fold CV + AUC ----------
def auc(y, s):
    pos = s[y == 1]; neg = s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
    # average ranks for ties
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt); start = csum - cnt + 1
    avg = (start + csum) / 2.0
    ranks = avg[inv]
    rp = ranks[y == 1].sum()
    return (rp - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg))

def fit_logistic(X, y, iters=500, lr=0.3, l2=1e-3):
    n, d = X.shape
    w = np.zeros(d); b = 0.0
    for _ in range(iters):
        z = X @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        g = p - y
        gw = X.T @ g / n + l2 * w
        gb = g.mean()
        w -= lr * gw; b -= lr * gb
    return w, b

def cv_classify(rowsA, rowsB, label):
    XA = mat(rowsA); XB = mat(rowsB)
    nA, nB = len(XA), len(XB)
    k = min(nA, nB)
    ia = rng.permutation(nA)[:k]; ib = rng.permutation(nB)[:k]
    X = np.vstack([XA[ia], XB[ib]])
    y = np.hstack([np.ones(k), np.zeros(k)])
    perm = rng.permutation(len(y)); X = X[perm]; y = y[perm]
    folds = np.array_split(np.arange(len(y)), 5)
    aucs, accs, coefs = [], [], []
    for f in range(5):
        te = folds[f]; tr = np.hstack([folds[j] for j in range(5) if j != f])
        mu = X[tr].mean(0); sd = X[tr].std(0) + 1e-9
        Xtr = (X[tr] - mu) / sd; Xte = (X[te] - mu) / sd
        w, b = fit_logistic(Xtr, y[tr])
        s = 1.0 / (1.0 + np.exp(-(Xte @ w + b)))
        aucs.append(auc(y[te], s))
        accs.append(((s > 0.5).astype(float) == y[te]).mean())
        coefs.append(w)
    coefs = np.array(coefs).mean(0)
    print(f"\n=== classifier {label} (balanced n={k}/class, 5-fold CV) ===")
    print(f"  AUC = {np.mean(aucs):.3f} +/- {np.std(aucs):.3f}   accuracy = {np.mean(accs):.3f} +/- {np.std(accs):.3f}")
    print("  standardised logistic coefficients (|large| = axis drives the split; + => higher in MANIP):")
    order = np.argsort(-np.abs(coefs))
    for i in order:
        print(f"    {DWEB[i]:<18} {coefs[i]:+.2f}")
    # univariate AUC per axis (single-axis separability, MANIP=1)
    print("  univariate AUC per axis (0.5 = no separation):")
    ua = []
    for i, a in enumerate(DWEB):
        s = np.hstack([XA[ia][:, i], XB[ib][:, i]])
        yy = np.hstack([np.ones(k), np.zeros(k)])
        au = auc(yy, s); au = max(au, 1 - au)
        ua.append((a, au))
    for a, au in sorted(ua, key=lambda x: -x[1]):
        print(f"    {a:<18} {au:.3f}")
    return np.mean(aucs), np.std(aucs), np.mean(accs)

if len(sincere) > 0:
    cv_classify(manip, sincere, "MANIP vs SINCERE (CMV)")
else:
    print("\n[skip] MANIP vs SINCERE — SINCERE (CMV) group empty")
if len(shortpol) > 0:
    cv_classify(manip, shortpol, "MANIP vs SHORTPOL (LIAR)")
else:
    print("\n[skip] MANIP vs SHORTPOL — SHORTPOL (LIAR) group empty (length control unavailable)")

print("\n[note] one actor (IRA), one era (2015-2018), one platform (Twitter), English only.")
print("       CMV baseline is longer-form Reddit (length confound); LIAR is length-matched")
print("       short political but is politician claims not social posts; scorer is web-tuned 7B.")

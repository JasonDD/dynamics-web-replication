#!/usr/bin/env python3
"""analyse_manner_inflation.py — is deception a domain-independent character signature, and
are dark patterns its purest form?

Hypothesis under test (manner-inflation): deception inflates MANNER (affect+stance+register)
past what the genre's MATTER (rigour+depth) earns. Metric per text:
    residual        = mean(manner axes) - mean(matter axes)
    residual_bs     = residual - (mean residual of the matched HONEST control in that genre)

Domains (deceptive vs matched honest control):
    ira    IRA political trolls          vs  CMV winning arguments (sincere persuasion)
    phish  phishing emails               vs  legitimate ('safe') emails
    dark   dark-pattern UI microcopy     vs  neutral UI / product microcopy
    liar   PolitiFact false/pants-fire   vs  PolitiFact true statements

Outputs: per-domain manner-inflation table; within-domain classifier AUC (8-axis logistic,
and residual-only); cross-domain AUC matrix (train one domain, test the others); pooled
leave-one-domain-out AUC; a length ranking to test the 'dark patterns are shortest' claim.
numpy only (logistic regression, k-fold CV, AUC implemented here).
"""
import os, json, csv, numpy as np, psycopg2

DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
MATTER = ["rigour", "depth"]
MANNER = ["affect", "stance", "register"]
rng = np.random.default_rng(1729)

SCORED = "/mnt/nas/kronaxis/corpora/manner_inflation/scored.jsonl"
INPUT = "/mnt/nas/kronaxis/corpora/manner_inflation/input.jsonl"
IRA = "/mnt/nas/kronaxis/corpora/ira_troll/work/scored.jsonl"
CMV = "/mnt/nas/kronaxis/corpora/cmv_winning_args/cmv_scores.jsonl"
IRA_RAW = "/mnt/nas/kronaxis/corpora/ira_troll/IRAhandle_tweets_1.csv"
POL = {"RightTroll", "LeftTroll", "Fearmonger"}
CMV_CAP = 2000

# ---- web-reference matter/manner PC1 (continuity with manip_analyse.py) ----
def load_pc1():
    PW = [l.split("=", 1)[1].strip().strip('"').strip("'")
          for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
    c = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
    c.execute(f"SELECT {','.join(DWEB)} FROM cc_v3.domain_char8_expanded")
    allc = np.array([[float(x) for x in r] for r in c.fetchall()], float)
    MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
    _, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False); PC1 = Vt[0]
    if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0:
        PC1 = -PC1
    return MEAN, STD, PC1

def vec(ch):
    return np.array([ch[a] for a in DWEB], float)

def matter(ch):
    return float(np.mean([ch[a] for a in MATTER]))

def manner(ch):
    return float(np.mean([ch[a] for a in MANNER]))

def residual(ch):
    return manner(ch) - matter(ch)

def affect(ch):
    return float(ch["affect"])

def affect_gap(ch):
    # the PRECISE predicted form: affect inflated past matter (not generic manner)
    return affect(ch) - matter(ch)

# ---- assemble domains: label 1 = deceptive, 0 = honest ----
def load_jsonl(p):
    out = []
    for l in open(p):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if "char" in r and all(a in r["char"] for a in DWEB):
            out.append(r)
    return out

sc = load_jsonl(SCORED)
by_kind = {}
for r in sc:
    by_kind.setdefault(r["kind"], []).append(r)

DECEPT_LABELS = {"phish": {"phish"}, "dark": {"dark"}, "liar": {"false", "pants-fire"}}
domains = {}  # name -> list of (char, label)
for k in ("phish", "dark", "liar"):
    rows = by_kind.get(k, [])
    d = DECEPT_LABELS[k]
    domains[k] = [(r["char"], 1 if r["outcome"] in d else 0) for r in rows]

# IRA (deceptive) vs CMV (honest)
ira = [(r["char"], 1) for r in load_jsonl(IRA) if r.get("kind") == "ira" and r.get("outcome") in POL]
cmv = load_jsonl(CMV)
rng.shuffle(cmv)
cmv = [(r["char"], 0) for r in cmv[:CMV_CAP]]
domains["ira"] = ira + cmv

DOM_ORDER = ["ira", "phish", "dark", "liar"]
DOM_NAME = {"ira": "IRA trolls vs CMV", "phish": "phishing vs safe email",
            "dark": "dark patterns vs neutral UI", "liar": "LIAR false vs true"}

# ---- helpers ----
def cohend(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2) + 1e-12)
    return (a.mean() - b.mean()) / sp

def auc(y, s):
    y = np.asarray(y); s = np.asarray(s, float)
    pos = (y == 1).sum(); neg = (y == 0).sum()
    if pos == 0 or neg == 0:
        return float("nan")
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt); avg = (csum - cnt + 1 + csum) / 2.0
    ranks = avg[inv]
    return (ranks[y == 1].sum() - pos * (pos + 1) / 2.0) / (pos * neg)

def fit_logistic(X, y, iters=800, lr=0.3, l2=1e-3):
    n, d = X.shape
    w = np.zeros(d); b = 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(X @ w + b)))
        g = p - y
        w -= lr * (X.T @ g / n + l2 * w)
        b -= lr * g.mean()
    return w, b

def balance(rows):
    pos = [r for r in rows if r[1] == 1]; neg = [r for r in rows if r[1] == 0]
    k = min(len(pos), len(neg))
    ip = rng.permutation(len(pos))[:k]; ineg = rng.permutation(len(neg))[:k]
    sel = [pos[i] for i in ip] + [neg[i] for i in ineg]
    X = np.array([vec(c) for c, _ in sel]); y = np.array([l for _, l in sel], float)
    return X, y

print("=" * 78)
print("MANNER-INFLATION DECEPTION TEST  —  8-axis DWEB character scorer (qwen2.5-7b-atlas)")
print("=" * 78)
print("\n=== domain sizes (deceptive / honest) ===")
for k in DOM_ORDER:
    d = domains[k]
    print(f"  {DOM_NAME[k]:<32} deceptive={sum(l for _,l in d):5d}  honest={sum(1-l for _,l in d):5d}")

# ---- per-domain manner-inflation table ----
print("\n=== per-domain matter / manner / affect / residual / affect_gap (mean) ===")
hdr = f"  {'domain':<30}{'grp':<6}{'matter':>7}{'manner':>7}{'affect':>7}{'resid':>7}{'aff_gap':>8}"
print(hdr)
dom_stats = {}
for k in DOM_ORDER:
    d = domains[k]
    dec = [c for c, l in d if l == 1]; hon = [c for c, l in d if l == 0]
    for name, grp in (("deceptive", dec), ("honest", hon)):
        mt = np.mean([matter(c) for c in grp]); mn = np.mean([manner(c) for c in grp])
        af = np.mean([affect(c) for c in grp]); rs = np.mean([residual(c) for c in grp])
        ag = np.mean([affect_gap(c) for c in grp])
        print(f"  {DOM_NAME[k]:<30}{name:<6}{mt:7.3f}{mn:7.3f}{af:7.3f}{rs:7.3f}{ag:8.3f}")
    dr = [residual(c) for c in dec]; hr = [residual(c) for c in hon]
    da = [affect_gap(c) for c in dec]; ha = [affect_gap(c) for c in hon]
    dom_stats[k] = (cohend(dr, hr), np.mean(dr) - np.mean(hr),
                    cohend(da, ha), np.mean(da) - np.mean(ha))
print("\n  matter=mean(rigour,depth)  manner=mean(affect,stance,register)")
print("  resid=manner-matter   aff_gap=affect-matter  (the precise 'high affect + starved matter' form)")
print("\n=== deception gap (deceptive minus honest): residual vs affect_gap ===")
print(f"  {'domain':<32}{'resid d':>9}{'resid gap':>11}{'affgap d':>10}{'affgap gap':>12}")
for k in DOM_ORDER:
    rd_, rg_, ad_, ag_ = dom_stats[k]
    print(f"  {DOM_NAME[k]:<32}{rd_:+9.2f}{rg_:+11.3f}{ad_:+10.2f}{ag_:+12.3f}")

# ---- within-domain classifiers (5-fold CV) ----
def cv_within(rows, use_residual=False):
    X0, y = balance(rows)
    if use_residual:
        X = np.array([[manner(dict(zip(DWEB, x))) - matter(dict(zip(DWEB, x)))] for x in X0])
    else:
        X = X0
    perm = rng.permutation(len(y)); X = X[perm]; y = y[perm]
    folds = np.array_split(np.arange(len(y)), 5)
    aucs = []
    for f in range(5):
        te = folds[f]; tr = np.hstack([folds[j] for j in range(5) if j != f])
        mu = X[tr].mean(0); sd = X[tr].std(0) + 1e-9
        w, b = fit_logistic((X[tr] - mu) / sd, y[tr])
        s = 1.0 / (1.0 + np.exp(-(((X[te] - mu) / sd) @ w + b)))
        aucs.append(auc(y[te], s))
    return np.nanmean(aucs), np.nanstd(aucs)

print("\n=== within-domain AUC (balanced, 5-fold CV) ===")
print(f"  {'domain':<32}{'8-axis':>10}{'residual-only':>16}")
for k in DOM_ORDER:
    a8, s8 = cv_within(domains[k], False)
    ar, sr = cv_within(domains[k], True)
    print(f"  {DOM_NAME[k]:<32}{a8:6.3f}+-{s8:.2f}{ar:10.3f}+-{sr:.2f}")

# ---- cross-domain AUC matrix (train on one, test on others) ----
def train_dom(rows):
    X, y = balance(rows)
    mu = X.mean(0); sd = X.std(0) + 1e-9
    w, b = fit_logistic((X - mu) / sd, y)
    return mu, sd, w, b

def test_dom(model, rows):
    mu, sd, w, b = model
    X, y = balance(rows)
    s = 1.0 / (1.0 + np.exp(-(((X - mu) / sd) @ w + b)))
    return auc(y, s)

print("\n=== cross-domain AUC matrix (row=train domain, col=test domain), 8-axis logistic ===")
models = {k: train_dom(domains[k]) for k in DOM_ORDER}
print("  " + "train\\test".ljust(14) + "".join(k.rjust(9) for k in DOM_ORDER))
for tr in DOM_ORDER:
    row = "  " + tr.ljust(14)
    for te in DOM_ORDER:
        row += f"{test_dom(models[tr], domains[te]):9.3f}"
    print(row)

# residual-only cross-domain (single feature)
def train_res(rows):
    X, y = balance(rows)
    r = (X[:, [DWEB.index(a) for a in MANNER]].mean(1) - X[:, [DWEB.index(a) for a in MATTER]].mean(1))
    return r, y  # threshold-free: use raw residual as score
print("\n=== cross-domain AUC, RESIDUAL-ONLY score (manner-matter), no training ===")
print("  (residual used directly as deception score; same sign across all domains)")
for te in DOM_ORDER:
    X, y = balance(domains[te])
    r = (X[:, [DWEB.index(a) for a in MANNER]].mean(1) - X[:, [DWEB.index(a) for a in MATTER]].mean(1))
    print(f"  {DOM_NAME[te]:<32} AUC={auc(y, r):.3f}")

# ---- pooled leave-one-domain-out ----
print("\n=== leave-one-domain-out: train on other 3 domains (pooled), test on held-out ===")
for held in DOM_ORDER:
    tr_rows = []
    for k in DOM_ORDER:
        if k == held:
            continue
        Xk, yk = balance(domains[k])
        tr_rows += list(zip([tuple(x) for x in Xk], yk))
    Xtr = np.array([list(x) for x, _ in tr_rows]); ytr = np.array([l for _, l in tr_rows], float)
    mu = Xtr.mean(0); sd = Xtr.std(0) + 1e-9
    w, b = fit_logistic((Xtr - mu) / sd, ytr)
    Xte, yte = balance(domains[held])
    s = 1.0 / (1.0 + np.exp(-(((Xte - mu) / sd) @ w + b)))
    print(f"  held-out {DOM_NAME[held]:<32} AUC={auc(yte, s):.3f}")

# ---- PCAA gate: block rate at fixed false-positive on matched honest control ----
# Detector = pooled leave-one-domain-out 8-axis logistic (so the block rate on a domain
# comes from a model that never saw that domain — the honest cross-domain capability).
print("\n=== PCAA gate: block rate on deceptive at 5%/10% false-positive on honest control ===")
print("  (score = pooled model trained on the OTHER 3 domains; threshold set on that domain's honest)")
print(f"  {'domain':<32}{'block@5%FPR':>13}{'block@10%FPR':>14}")
def scores_for(held):
    tr_rows = []
    for k in DOM_ORDER:
        if k == held:
            continue
        Xk, yk = balance(domains[k])
        tr_rows += list(zip([tuple(x) for x in Xk], yk))
    Xtr = np.array([list(x) for x, _ in tr_rows]); ytr = np.array([l for _, l in tr_rows], float)
    mu = Xtr.mean(0); sd = Xtr.std(0) + 1e-9
    w, b = fit_logistic((Xtr - mu) / sd, ytr)
    Xte, yte = balance(domains[held])
    s = 1.0 / (1.0 + np.exp(-(((Xte - mu) / sd) @ w + b)))
    return s, yte
for k in DOM_ORDER:
    s, y = scores_for(k)
    dec_s = s[y == 1]; hon_s = s[y == 0]
    br = {}
    for fpr in (0.05, 0.10):
        thr = np.quantile(hon_s, 1 - fpr)
        br[fpr] = (dec_s >= thr).mean()
    print(f"  {DOM_NAME[k]:<32}{br[0.05]:12.1%}{br[0.10]:13.1%}")

# ---- MATHUR per-surface-form signature (the signature-by-target-trait test) ----
print("\n" + "=" * 78)
print("MATHUR 2019 per-surface-form signature  (does each pattern carry the predicted form?)")
print("=" * 78)
meta = {r["id"]: r for r in (json.loads(l) for l in open("/mnt/nas/kronaxis/corpora/manner_inflation/mathur_meta.jsonl"))}
dm = [r for r in sc if r["kind"] == "darkm" and r["id"] in meta]
for r in dm:
    r["_m"] = meta[r["id"]]
# neutral-UI baseline (dark-domain honest control) to define 'starved/inflated PAST genre'
neutral = [c for c, l in domains["dark"] if l == 0]
base_matter = np.mean([matter(c) for c in neutral]) if neutral else 0.0
base_affect = np.mean([affect(c) for c in neutral]) if neutral else 0.0
print(f"\n  neutral-UI baseline: matter={base_matter:.3f}  affect={base_affect:.3f}  (n={len(neutral)})")
print(f"\n  {'surface type':<28}{'n':>5}{'wrd':>5}{'matter':>8}{'affect':>8}{'aff-mat':>8}{'vs base: aff':>13}{'mat':>7}")
by_type = {}
for r in dm:
    by_type.setdefault(r["_m"]["type"], []).append(r)
def keyf(kv):
    return -np.mean([affect_gap(r["char"]) for r in kv[1]])
for t, rows_t in sorted(by_type.items(), key=keyf):
    if len(rows_t) < 5:
        continue
    mt = np.mean([matter(r["char"]) for r in rows_t]); af = np.mean([affect(r["char"]) for r in rows_t])
    ag = af - mt; nw = np.median([r["_m"]["nwords"] for r in rows_t])
    print(f"  {t:<28}{len(rows_t):5d}{nw:5.0f}{mt:8.3f}{af:8.3f}{ag:8.3f}{af-base_affect:+13.3f}{mt-base_matter:+7.3f}")
print("\n  PREDICTION: urgency/scarcity/social-proof types => affect inflated, matter starved (aff-mat high).")
print("  EXCEPTION (illusion-of-control analog): types that FAKE rigour — Hidden Costs (fabricated")
print("  itemised totals), Testimonials (fake authority) — should read HIGHER matter, LOWER affect.")
# explicit exception check
faked = [r for r in dm if r["_m"]["type"] in ("Hidden Costs", "Testimonials of Uncertain Origin", "Pressured Selling")]
affy = [r for r in dm if r["_m"]["type"] in ("Countdown Timer", "Low-stock Message", "Limited-time Message", "High-demand Message")]
if faked and affy:
    print(f"\n  faked-matter types  (Hidden Costs/Testimonials/Pressured): matter={np.mean([matter(r['char']) for r in faked]):.3f}  affect={np.mean([affect(r['char']) for r in faked]):.3f}  n={len(faked)}")
    print(f"  affect-weapon types (Countdown/Low-stock/Limited/High-demand): matter={np.mean([matter(r['char']) for r in affy]):.3f}  affect={np.mean([affect(r['char']) for r in affy]):.3f}  n={len(affy)}")

# ---- length ranking (dark patterns shortest?) ----
print("\n=== text length by domain (median words), deceptive class ===")
# phish/dark/liar from input.jsonl; ira from raw tweet sample
txt = {}
for l in open(INPUT):
    try:
        r = json.loads(l)
    except Exception:
        continue
    txt.setdefault(r["kind"], {}).setdefault("dec" if r["outcome"] in DECEPT_LABELS.get(r["kind"], set()) else "hon", []).append(len(r["text"].split()))
for k in ("dark", "liar", "phish"):
    if k in txt:
        d = np.median(txt[k].get("dec", [0])); h = np.median(txt[k].get("hon", [0]))
        print(f"  {DOM_NAME[k]:<32} deceptive median={d:6.0f} w   honest median={h:6.0f} w")
# ira raw tweets
try:
    import io
    lens = []
    with open(IRA_RAW, encoding="utf-8", errors="ignore") as f:
        rd = csv.DictReader(f)
        for i, r in enumerate(rd):
            if i > 20000:
                break
            cat = r.get("account_category", "")
            if cat in POL:
                lens.append(len((r.get("content") or "").split()))
    if lens:
        print(f"  {'IRA trolls (raw tweets)':<32} deceptive median={np.median(lens):6.0f} w   (sample n={len(lens)})")
except Exception as e:
    print(f"  [ira length skipped: {e}]")

print("\n[caveats] one 7B scorer; IRA control is cross-genre (CMV long-form) so its gap is")
print("          confounded by length; LIAR 'deception' = fact-check falsity, not intent to")
print("          manipulate; dark/phish/liar honest controls are same-genre and same-source.")

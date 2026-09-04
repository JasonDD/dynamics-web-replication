#!/usr/bin/env python3
"""analyse_crosslingual.py -- is the manipulation signature language-agnostic?

Claim under test: manipulation inflates MANNER (affect+stance+register) past what the genre's
MATTER (rigour+depth) earns. If this signature is affect-heavy manner inflation and manner
survives translation, it should separate troll from sincere in EVERY language, and a detector
trained on ENGLISH deception should transfer to non-English troll-vs-sincere.

Per text metrics:
    matter    = mean(rigour, depth)
    manner    = mean(affect, stance, register)
    residual  = manner - matter
    aff_gap   = affect - matter          (the precise predicted form)

Manipulation set (all languages): IRA troll tweets, bucketed by the dataset language field.
Sincere baselines:
    en/de/fr/es/it : Europarl parliamentary text (europarl_multiway/scored.jsonl) -- one genre,
                     held constant across languages so cross-language CONSISTENCY is meaningful.
    fa             : Persian daily news (scored in crosslingual_manip/scored.jsonl).
    ru             : no matched baseline -> descriptive only (honest gap).

Genre caveat: troll = short social post, Europarl/news baseline = long formal text. The genre
gap is held CONSTANT across the Europarl-baselined languages, so equal effect sizes across
languages is the invariance evidence even if the absolute magnitude is genre-inflated. The
length_mechanism result argues short text is forced into the affect channel, so length is part
of the manipulation mechanism, not only a nuisance.

numpy only.
"""
import os, json, numpy as np

DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
MATTER = ["rigour", "depth"]
MANNER = ["affect", "stance", "register"]
rng = np.random.default_rng(1729)

CL = "the internal corpus store/crosslingual_manip/scored.jsonl"
EUP = "the internal corpus store/europarl_multiway/scored.jsonl"
IRA_EN = "the internal corpus store/ira_troll/work/scored.jsonl"
POL = {"RightTroll", "LeftTroll", "Fearmonger"}

def load(p):
    out = []
    for l in open(p, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if isinstance(r.get("char"), dict) and all(a in r["char"] for a in DWEB):
            out.append(r)
    return out

def vec(ch):    return np.array([ch[a] for a in DWEB], float)
def matter(ch): return float(np.mean([ch[a] for a in MATTER]))
def manner(ch): return float(np.mean([ch[a] for a in MANNER]))
def resid(ch):  return manner(ch) - matter(ch)
def affgap(ch): return float(ch["affect"]) - matter(ch)

def cohend(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2) + 1e-12)
    return (a.mean() - b.mean()) / sp

def auc(y, s):
    y = np.asarray(y); s = np.asarray(s, float)
    pos = int((y == 1).sum()); neg = int((y == 0).sum())
    if pos == 0 or neg == 0:
        return float("nan")
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt); avgr = (csum - cnt + 1 + csum) / 2.0
    ranks = avgr[inv]
    return (ranks[y == 1].sum() - pos * (pos + 1) / 2.0) / (pos * neg)

def fit_logistic(X, y, iters=1200, lr=0.3, l2=1e-3):
    n, d = X.shape
    w = np.zeros(d); b = 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(X @ w + b)))
        g = p - y
        w -= lr * (X.T @ g / n + l2 * w)
        b -= lr * g.mean()
    return w, b

def predict(w, b, X):
    return 1.0 / (1.0 + np.exp(-(X @ w + b)))

# ---- assemble troll / sincere character vectors per language ----
cl = load(CL)
troll = {}   # lang -> list[char]
for r in cl:
    if r.get("outcome") == "troll":
        troll.setdefault(r["kind"], []).append(r["char"])
# English trolls from the existing IRA scoring (political categories = the established anchor)
troll["en"] = [r["char"] for r in load(IRA_EN) if r.get("kind") == "ira" and r.get("outcome") in POL]

sincere = {}  # lang -> list[char]
for r in load(EUP):            # Europarl per-language sincere baseline
    sincere.setdefault(r["kind"], []).append(r["char"])
sincere["fa"] = [r["char"] for r in cl if r.get("outcome") == "sincere" and r.get("kind") == "fa"]

LANGNAME = {"en": "English", "de": "German", "it": "Italian", "fr": "French",
            "es": "Spanish", "fa": "Persian", "ru": "Russian"}
BASELINE = {"en": "Europarl", "de": "Europarl", "it": "Europarl", "fr": "Europarl",
            "es": "Europarl", "fa": "Persian news", "ru": "(none)"}

print("=" * 92)
print("CROSS-LINGUAL MANIPULATION SIGNATURE  -  8-axis DWEB character (an internal 7B instruct model )")
print("=" * 92)
print(f"\n{'lang':10s} {'baseline':13s} {'n_troll':>8s} {'n_sinc':>8s}")
for lg in ["en", "de", "it", "fr", "es", "fa", "ru"]:
    nt = len(troll.get(lg, [])); ns = len(sincere.get(lg, []))
    print(f"{LANGNAME[lg]:10s} {BASELINE[lg]:13s} {nt:8d} {ns:8d}")

# ---- per-language signature: Cohen's d + AUC for aff_gap, residual, and 8-axis logistic ----
print("\n" + "-" * 92)
print("PER-LANGUAGE SIGNATURE  (troll vs sincere; d>0 and AUC>0.5 = troll more manner-inflated)")
print("-" * 92)
print(f"{'lang':10s} {'d(aff_gap)':>11s} {'AUC(aff_gap)':>13s} {'d(resid)':>10s} {'AUC(resid)':>11s} {'AUC(8ax cv)':>12s}")
CLEAN = ["en", "de", "it", "fr", "es", "fa"]
per_lang = {}
for lg in CLEAN:
    T = troll.get(lg, []); S = sincere.get(lg, [])
    if len(T) < 20 or len(S) < 20:
        print(f"{LANGNAME[lg]:10s}  too few samples (troll={len(T)} sinc={len(S)})")
        continue
    ag_t = [affgap(c) for c in T]; ag_s = [affgap(c) for c in S]
    rs_t = [resid(c) for c in T];  rs_s = [resid(c) for c in S]
    d_ag = cohend(ag_t, ag_s); a_ag = auc([1]*len(ag_t)+[0]*len(ag_s), ag_t+ag_s)
    d_rs = cohend(rs_t, rs_s); a_rs = auc([1]*len(rs_t)+[0]*len(rs_s), rs_t+rs_s)
    # balanced 8-axis logistic, 5-fold CV
    k = min(len(T), len(S))
    Tsel = [T[i] for i in rng.permutation(len(T))[:k]]
    Ssel = [S[i] for i in rng.permutation(len(S))[:k]]
    X = np.array([vec(c) for c in Tsel] + [vec(c) for c in Ssel])
    y = np.array([1.0]*k + [0.0]*k)
    idx = rng.permutation(len(y)); X, y = X[idx], y[idx]
    folds = np.array_split(np.arange(len(y)), 5)
    scores = np.zeros(len(y))
    mu = X.mean(0); sd = X.std(0) + 1e-9
    for f in range(5):
        te = folds[f]; tr = np.setdiff1d(np.arange(len(y)), te)
        w, b = fit_logistic((X[tr]-mu)/sd, y[tr])
        scores[te] = predict(w, b, (X[te]-mu)/sd)
    a_8 = auc(y, scores)
    print(f"{LANGNAME[lg]:10s} {d_ag:11.2f} {a_ag:13.3f} {d_rs:10.2f} {a_rs:11.3f} {a_8:12.3f}")
    per_lang[lg] = dict(d_ag=d_ag, a_ag=a_ag, d_rs=d_rs, a_rs=a_rs, a_8=a_8,
                        n_t=len(T), n_s=len(S))

# ---- Russian descriptive (no matched baseline) ----
print("\n" + "-" * 92)
print("RUSSIAN (descriptive; no matched Russian sincere baseline on hand)")
print("-" * 92)
if troll.get("ru"):
    ru_ag = [affgap(c) for c in troll["ru"]]
    ru_rs = [resid(c) for c in troll["ru"]]
    # pooled non-English sincere baseline mean (Europarl de/fr/es/it) for a rough placement
    pooled = [affgap(c) for lg in ["de","fr","es","it"] for c in sincere.get(lg, [])]
    print(f"Russian troll aff_gap: mean={np.mean(ru_ag):.3f} sd={np.std(ru_ag):.3f}  "
          f"residual mean={np.mean(ru_rs):.3f}  (n={len(ru_ag)})")
    print(f"pooled Europarl sincere aff_gap mean={np.mean(pooled):.3f}  "
          f"-> gap={np.mean(ru_ag)-np.mean(pooled):+.3f}")

# ---- ENGLISH->OTHER TRANSFER: train 8-axis logistic on English, test each non-English ----
print("\n" + "=" * 92)
print("TRANSFER: detector trained on ENGLISH deception, tested on NON-ENGLISH troll vs sincere")
print("=" * 92)
Ten = troll["en"]; Sen = sincere["en"]
ke = min(len(Ten), len(Sen))
Tw = [Ten[i] for i in rng.permutation(len(Ten))[:ke]]
Sw = [Sen[i] for i in rng.permutation(len(Sen))[:ke]]
Xen = np.array([vec(c) for c in Tw] + [vec(c) for c in Sw])
yen = np.array([1.0]*ke + [0.0]*ke)
mu_en = Xen.mean(0); sd_en = Xen.std(0) + 1e-9
w_en, b_en = fit_logistic((Xen-mu_en)/sd_en, yen)
print(f"trained on English: {ke} troll + {ke} sincere")
print(f"English self-AUC (train=test, optimistic): "
      f"{auc(yen, predict(w_en,b_en,(Xen-mu_en)/sd_en)):.3f}\n")
print(f"{'target lang':12s} {'n_troll':>8s} {'n_sinc':>8s} {'transfer AUC(8ax)':>18s} {'AUC(aff_gap)':>13s}")
transfer = {}
for lg in ["de", "it", "fr", "es", "fa"]:
    T = troll.get(lg, []); S = sincere.get(lg, [])
    if len(T) < 20 or len(S) < 20:
        continue
    X = np.array([vec(c) for c in T] + [vec(c) for c in S])
    y = np.array([1.0]*len(T) + [0.0]*len(S))
    p = predict(w_en, b_en, (X-mu_en)/sd_en)
    a_tr = auc(y, p)
    a_ag = auc(y, np.array([affgap(c) for c in T] + [affgap(c) for c in S]))
    print(f"{LANGNAME[lg]:12s} {len(T):8d} {len(S):8d} {a_tr:18.3f} {a_ag:13.3f}")
    transfer[lg] = dict(a_tr=a_tr, a_ag=a_ag, n_t=len(T), n_s=len(S))

# ---- dump machine-readable summary ----
summary = {"per_lang": per_lang, "transfer": transfer,
           "en_self_auc": float(auc(yen, predict(w_en,b_en,(Xen-mu_en)/sd_en))),
           "en_weights": {a: float(w) for a, w in zip(DWEB, w_en)}}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ".",
                       "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("\nWROTE summary.json")

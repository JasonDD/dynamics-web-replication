#!/usr/bin/env python3
"""biber_reduction.py — DYNAMICS-WEB unification reduction test (PUBLIC track).

Does our matter/manner PC1 (projected-voice scoring) reduce onto Biber (1988)
Dimension 1, "Involved versus Informational production" (grammatical feature
factor analysis)? Two unrelated methods, same documents. Analysis only: reuse
held 8-axis char scores (the internal Reddit corpus), compute Biber D1 from text, no
model, no scoring service.

Biber D1 here is the classic standardised-additive dimension score: z-score each
feature rate across documents, sum the involved features, subtract the
informational features. Involved features are all closed-class (pronouns,
private verbs, contractions, hedges, amplifiers, discourse particles, emphatics,
demonstratives, analytic negation, possibility modals, wh-words, questions) so
they are exact without a POS tagger. The informational pole (nouns, attributive
adjectives, present-vs-past) needs a tagger we do not have offline, so it is
carried by Biber's own taggerless informational features — mean word length,
type-token ratio, preposition rate — plus nominalisation-suffix and definite-
article density as noun-style proxies. This is stated as the honest bound.
"""
import os, re, json, numpy as np, psycopg2

DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
OUT = os.path.expanduser("~/biber_reduction_out")
os.makedirs(OUT, exist_ok=True)

PW = [l.split("=", 1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
conn = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs")
c = conn.cursor()

# ---- matter/manner PC1 reference (same recipe as truthometer/scripts/manip_analyse.py)
c.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
allc = np.array([[float(x) for x in r] for r in c.fetchall()], float)
MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
_, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False)
PC1 = Vt[0]
if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0:
    PC1 = -PC1
print("PC1 loadings (rigour+depth oriented positive):")
for a, w in sorted(zip(DWEB, PC1), key=lambda t: -t[1]):
    print(f"  {a:<18} {w:+.3f}")

def pc1_of(ch):
    v = (np.array([ch[a] for a in DWEB], float) - MEAN) / STD
    return float(v @ PC1)

# ---- pull held reddit_wide docs: text + char + subreddit
c.execute("""
  SELECT id, subreddit, body, char
  FROM the internal Reddit corpus
  WHERE char IS NOT NULL AND char ? 'rigour' AND length(body) >= 200
""")
rows = c.fetchall()
print(f"\nfetched {len(rows)} scored reddit_wide docs (body >= 200 chars)")

# ================= Biber Dimension 1 feature extraction =================
FIRST = set("i me my mine myself we us our ours ourselves".split())
SECOND = set("you your yours yourself yourselves".split())
PRIVATE = set(("think thinks thought feel feels felt believe believes believed know knows knew "
    "guess guessed suppose supposed assume assumed doubt doubted hope hoped imagine imagined "
    "realize realise realized realised wonder wondered seem seems seemed understand understood "
    "mean meant want wants wanted wish wished remember remembered forget forgot notice noticed "
    "decide decided consider considered expect expected figure reckon agree agreed concern "
    "concerned believe recall assume").split())
DEMON = set("this that these those".split())
EMPH = set("just really so real most more such sure".split())
AMPL = set("very extremely totally completely absolutely highly entirely strongly fully quite too".split())
HEDGE1 = set("maybe perhaps somewhat probably possibly kinda sorta".split())
DISC = set("well now anyway anyhow".split())
CAUSE = set("because cause cuz bc".split())
WH = set("what where when why how who whom whose which".split())
POSS = set("can could may might will would shall should".split())
PREP = set(("of in to for with on at by from as into about over under between through during "
    "before after above below against among around upon within without toward towards than "
    "onto off per via across behind beside beyond near").split())
ARTICLE = set("the an".split())
NOMSUF = ("tion", "sion", "ment", "ness", "ity", "ance", "ence", "ism", "ation")

WORD = re.compile(r"[a-zA-Z]+(?:'[a-z]+)?")
ALPHA = re.compile(r"[a-zA-Z]+")
CONTR = re.compile(r"\b\w+'(t|s|re|ve|ll|d|m)\b", re.I)
NT = re.compile(r"n't\b", re.I)

INV_NAMES = ["first_person","second_person","private_verbs","contractions","present_bedohave",
    "demonstratives","emphatics","amplifiers","hedges","discourse_particles","neg_not",
    "causative","wh_words","possibility_modals","questions"]
INF_NAMES = ["mean_word_len","type_token_ratio","prepositions","nominalisations","article_density"]

def features(text):
    t = text.lower()
    toks = WORD.findall(t)
    n = len(toks)
    if n < 30:
        return None
    alpha = ALPHA.findall(t)
    def rate(cnt):
        return 100.0 * cnt / n
    fp = sum(w in FIRST for w in toks)
    sp = sum(w in SECOND for w in toks)
    pv = sum(w in PRIVATE for w in toks)
    contr = len(CONTR.findall(text)) + len(NT.findall(text))
    presentbe = sum(w in {"am","is","are","'s","'re","'m","do","does","have","has"} for w in toks)
    dem = sum(w in DEMON for w in toks)
    emph = sum(w in EMPH for w in toks)
    ampl = sum(w in AMPL for w in toks)
    hedge = sum(w in HEDGE1 for w in toks) + t.count("sort of") + t.count("kind of") + t.count("i think") + t.count("i guess")
    disc = sum(w in DISC for w in toks) + t.count("you know")
    neg = sum(w == "not" for w in toks) + len(NT.findall(text))
    caus = sum(w in CAUSE for w in toks)
    wh = sum(w in WH for w in toks)
    poss = sum(w in POSS for w in toks)
    q = text.count("?")

    prep = sum(w in PREP for w in toks)
    art = sum(w in ARTICLE for w in toks)
    nom = sum(any(w.endswith(s) and len(w) > len(s) + 2 for s in NOMSUF) for w in alpha)
    mwl = float(np.mean([len(w) for w in alpha])) if alpha else 0.0
    window = toks[:100]
    ttr = len(set(window)) / len(window) if window else 0.0

    inv = [rate(fp), rate(sp), rate(pv), rate(contr), rate(presentbe), rate(dem), rate(emph),
           rate(ampl), rate(hedge), rate(disc), rate(neg), rate(caus), rate(wh), rate(poss), rate(q)]
    inf = [mwl, ttr, rate(prep), rate(nom), rate(art)]
    return inv, inf

ids, subs, PCv, INV, INF, CHrows = [], [], [], [], [], []
skipped = 0
for _id, sub, body, ch in rows:
    f = features(body)
    if f is None:
        skipped += 1
        continue
    ids.append(_id); subs.append(sub)
    PCv.append(pc1_of(ch))
    INV.append(f[0]); INF.append(f[1])
    CHrows.append([float(ch[a]) for a in DWEB])

PCv = np.array(PCv)
INV = np.array(INV, float); INF = np.array(INF, float)
CH = np.array(CHrows, float)
print(f"usable docs after >=30-word floor: {len(PCv)} (skipped {skipped} short)")

def z(M):
    return (M - M.mean(0)) / (M.std(0) + 1e-12)

zinv = z(INV); zinf = z(INF)
# Biber standardised-additive D1: sum involved z, minus informational z (mean so counts balance)
D1 = zinv.mean(1) - zinf.mean(1)

def pearson(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d else float("nan")

def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return pearson(ra.astype(float), rb.astype(float))

r_p = pearson(PCv, D1)
r_s = spearman(PCv, D1)
print(f"\n=== PC1 vs Biber D1 ===  n={len(PCv)}")
print(f"  Pearson  r = {r_p:+.3f}")
print(f"  Spearman r = {r_s:+.3f}")

# per-axis alignment with D1 (raw axis vs involved-positive D1)
print("\n=== per-axis Pearson vs Biber D1 (positive = axis rises with INVOLVED) ===")
axis_r = {}
for i, a in enumerate(DWEB):
    rr = pearson(CH[:, i], D1)
    axis_r[a] = rr
for a, rr in sorted(axis_r.items(), key=lambda t: t[1]):
    print(f"  {a:<18} {rr:+.3f}")

# which raw Biber features drive D1's link to PC1 (corr of each feature vs PC1)
print("\n=== Biber feature vs PC1 (sign shows matter/manner side) ===")
feat_r = {}
for i, nm in enumerate(INV_NAMES):
    feat_r["INV:"+nm] = pearson(INV[:, i], PCv)
for i, nm in enumerate(INF_NAMES):
    feat_r["INF:"+nm] = pearson(INF[:, i], PCv)
for nm, rr in sorted(feat_r.items(), key=lambda t: t[1]):
    print(f"  {nm:<26} {rr:+.3f}")

# within-subreddit correlation (control for genre clustering)
from collections import defaultdict
by = defaultdict(list)
for s, p, d in zip(subs, PCv, D1):
    by[s].append((p, d))
wr = []
for s, lst in by.items():
    if len(lst) >= 50:
        p = np.array([x[0] for x in lst]); d = np.array([x[1] for x in lst])
        wr.append((s, len(lst), pearson(p, d)))
wr_vals = np.array([x[2] for x in wr])
wr_w = np.array([x[1] for x in wr], float)
print(f"\n=== within-subreddit PC1-vs-D1 ({len(wr)} subreddits n>=50) ===")
print(f"  mean r          = {wr_vals.mean():+.3f}")
print(f"  weighted mean r = {float((wr_vals*wr_w).sum()/wr_w.sum()):+.3f}")
print(f"  median r        = {np.median(wr_vals):+.3f}")
print(f"  frac r<0        = {float((wr_vals<0).mean()):.2f}")

# between-subreddit centroids: Biber derived D1 at the GENRE level (factor analysis of
# genre feature profiles), so subreddit-mean PC1 vs subreddit-mean D1 is the most faithful
# unit-matched comparison, and tests whether the weak item-level r is within-genre noise.
cent = []
for s, lst in by.items():
    if len(lst) >= 50:
        p = np.array([x[0] for x in lst]); d = np.array([x[1] for x in lst])
        cent.append((p.mean(), d.mean(), len(lst)))
cp = np.array([x[0] for x in cent]); cd = np.array([x[1] for x in cent])
r_cent_p = pearson(cp, cd); r_cent_s = spearman(cp, cd)
print(f"\n=== between-subreddit centroids ({len(cent)} subreddits, Biber's own unit) ===")
print(f"  Pearson  r = {r_cent_p:+.3f}")
print(f"  Spearman r = {r_cent_s:+.3f}")

summary = {
    "n_docs": int(len(PCv)),
    "between_subreddit_centroid": {
        "n_subreddits": len(cent),
        "pearson_r": r_cent_p,
        "spearman_r": r_cent_s,
    },
    "n_reference_domains": int(len(allc)),
    "pc1_loadings": {a: float(w) for a, w in zip(DWEB, PC1)},
    "pearson_pc1_d1": r_p,
    "spearman_pc1_d1": r_s,
    "per_axis_vs_d1": axis_r,
    "biber_feature_vs_pc1": feat_r,
    "within_subreddit": {
        "n_subreddits": len(wr),
        "mean_r": float(wr_vals.mean()),
        "weighted_mean_r": float((wr_vals*wr_w).sum()/wr_w.sum()),
        "median_r": float(np.median(wr_vals)),
        "frac_negative": float((wr_vals < 0).mean()),
    },
    "involved_features": INV_NAMES,
    "informational_features": INF_NAMES,
}
json.dump(summary, open(f"{OUT}/summary.json", "w"), indent=2)
print(f"\nwrote {OUT}/summary.json")

#!/usr/bin/env python3
"""biber_crossmodel.py — second-lineage re-score of the BIBER reduction on cc_v3.reddit_wide.

Same documents, same taggerless Biber Dimension 1 feature code as
../reduction_biber/biber_reduction.py, but PC1 is built by SVD on an INDEPENDENT
FRONTIER MODEL FAMILY's own 8-axis projected-voice scores (not the 7B's held
scores, and not the domain reference matrix). Tests whether the matter/manner
PC1 <-> Biber D1 alignment survives a change of scorer lineage.

Inputs (JSONL, no DB needed for the cross-model scores):
  SCORES = {id, c:[8 in DWEB order]}   the second lineage's scores
  TEXT   = {id, subreddit, body}       the scored sample
7B baselines to beat: genre-centroid -0.60, item-level -0.14.
"""
import os, re, json
import numpy as np

DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
SCORES = os.environ["SCORES"]
TEXT = os.environ["TEXT"]
OUT = os.environ.get("OUT", os.path.dirname(SCORES))

# ================= Biber Dimension 1 feature extraction (verbatim from biber_reduction.py) =====
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
ARTICLE = set("the a an".split())
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


def pearson(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d else float("nan")


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return pearson(ra.astype(float), rb.astype(float))


def main():
    ch = {}
    for l in open(SCORES):
        r = json.loads(l)
        ch[r["id"]] = {a: float(r["c"][i]) for i, a in enumerate(DWEB)}

    docs = []
    for l in open(TEXT):
        r = json.loads(l)
        if r["id"] in ch and len(r["body"]) >= 200:
            docs.append((r["id"], r["subreddit"], r["body"]))

    # ---- PC1 built by SVD on the SECOND LINEAGE's own 8-axis scores (rigour+depth oriented +)
    allc = np.array([[ch[i][a] for a in DWEB] for i, _, _ in docs], float)
    MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
    _, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False)
    PC1 = Vt[0]
    if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0:
        PC1 = -PC1
    print("PC1 loadings on second-lineage scores (rigour+depth oriented positive):")
    for a, w in sorted(zip(DWEB, PC1), key=lambda t: -t[1]):
        print(f"  {a:<18} {w:+.3f}")

    def pc1_of(c):
        v = (np.array([c[a] for a in DWEB], float) - MEAN) / STD
        return float(v @ PC1)

    ids, subs, PCv, INV, INF, CHrows = [], [], [], [], [], []
    skipped = 0
    for _id, sub, body in docs:
        f = features(body)
        if f is None:
            skipped += 1
            continue
        ids.append(_id); subs.append(sub)
        PCv.append(pc1_of(ch[_id]))
        INV.append(f[0]); INF.append(f[1])
        CHrows.append([ch[_id][a] for a in DWEB])

    PCv = np.array(PCv); INV = np.array(INV, float); INF = np.array(INF, float); CH = np.array(CHrows, float)
    print(f"\nusable docs after >=30-word floor: {len(PCv)} (skipped {skipped} short)")

    def z(M):
        return (M - M.mean(0)) / (M.std(0) + 1e-12)

    zinv = z(INV); zinf = z(INF)
    D1 = zinv.mean(1) - zinf.mean(1)

    r_p = pearson(PCv, D1); r_s = spearman(PCv, D1)
    print(f"\n=== ITEM-LEVEL PC1 vs Biber D1 ===  n={len(PCv)}")
    print(f"  Pearson  r = {r_p:+.3f}")
    print(f"  Spearman r = {r_s:+.3f}")

    print("\n=== per-axis Pearson vs Biber D1 (positive = axis rises with INVOLVED) ===")
    axis_r = {}
    for i, a in enumerate(DWEB):
        axis_r[a] = pearson(CH[:, i], D1)
    for a, rr in sorted(axis_r.items(), key=lambda t: t[1]):
        print(f"  {a:<18} {rr:+.3f}")

    print("\n=== Biber feature vs PC1 (sign shows matter/manner side) ===")
    feat_r = {}
    for i, nm in enumerate(INV_NAMES):
        feat_r["INV:" + nm] = pearson(INV[:, i], PCv)
    for i, nm in enumerate(INF_NAMES):
        feat_r["INF:" + nm] = pearson(INF[:, i], PCv)
    for nm, rr in sorted(feat_r.items(), key=lambda t: t[1]):
        print(f"  {nm:<26} {rr:+.3f}")

    from collections import defaultdict
    by = defaultdict(list)
    for s, p, d in zip(subs, PCv, D1):
        by[s].append((p, d))

    # within-subreddit (control genre clustering) — floor 20 given 25/sub
    wr = []
    for s, lst in by.items():
        if len(lst) >= 20:
            p = np.array([x[0] for x in lst]); d = np.array([x[1] for x in lst])
            wr.append((s, len(lst), pearson(p, d)))
    wr_vals = np.array([x[2] for x in wr]); wr_w = np.array([x[1] for x in wr], float)
    print(f"\n=== within-subreddit PC1-vs-D1 ({len(wr)} subreddits n>=20) ===")
    print(f"  mean r          = {wr_vals.mean():+.3f}")
    print(f"  weighted mean r = {float((wr_vals*wr_w).sum()/wr_w.sum()):+.3f}")
    print(f"  median r        = {np.median(wr_vals):+.3f}")
    print(f"  frac r<0        = {float((wr_vals<0).mean()):.2f}")

    # between-subreddit centroids: Biber's own genre unit
    cent = []
    for s, lst in by.items():
        if len(lst) >= 20:
            p = np.array([x[0] for x in lst]); d = np.array([x[1] for x in lst])
            cent.append((p.mean(), d.mean(), len(lst)))
    cp = np.array([x[0] for x in cent]); cd = np.array([x[1] for x in cent])
    r_cent_p = pearson(cp, cd); r_cent_s = spearman(cp, cd)
    print(f"\n=== between-subreddit centroids ({len(cent)} subreddits, Biber's own unit) ===")
    print(f"  Pearson  r = {r_cent_p:+.3f}")
    print(f"  Spearman r = {r_cent_s:+.3f}")
    print(f"\n7B baselines: genre-centroid Pearson -0.60, item-level Pearson -0.14")

    summary = {
        "scorer": "independent frontier model family (second lineage)",
        "n_docs": int(len(PCv)),
        "item_level": {"pearson_r": r_p, "spearman_r": r_s},
        "between_subreddit_centroid": {"n_subreddits": len(cent), "pearson_r": r_cent_p, "spearman_r": r_cent_s},
        "within_subreddit": {"n_subreddits": len(wr), "mean_r": float(wr_vals.mean()),
                             "weighted_mean_r": float((wr_vals*wr_w).sum()/wr_w.sum()),
                             "median_r": float(np.median(wr_vals)), "frac_negative": float((wr_vals < 0).mean())},
        "pc1_loadings": {a: float(w) for a, w in zip(DWEB, PC1)},
        "per_axis_vs_d1": axis_r,
        "biber_feature_vs_pc1": feat_r,
        "qwen7b_genre_centroid_pearson": -0.60,
        "qwen7b_item_pearson": -0.14,
    }
    json.dump(summary, open(os.path.join(OUT, "biber_crossmodel_summary.json"), "w"), indent=2)
    print(f"\nwrote biber_crossmodel_summary.json")


if __name__ == "__main__":
    main()

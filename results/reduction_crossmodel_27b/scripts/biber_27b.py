#!/usr/bin/env python3
"""biber_27b.py — Biber reduction on the 27B re-score of reddit_wide. SAME feature extractor and D1 recipe as
reduction_biber/biber_reduction.py; only the char scoring model changed (7B -> 27B). Per the cross-model brief,
PC1 is rebuilt by SVD ON THE 27B CHAR SCORES OF THE SAMPLED DOCS THEMSELVES (oriented rigour+depth positive),
so the ruler is the model's own, not the 7B domain reference. 7B headline to beat: between-subreddit-centroid
Pearson = -0.60 (correctly signed), item-level -0.14.

Reads WD/biber_scored.jsonl {id, subreddit, axes} and WD/biber_input.jsonl {id, text(body), subreddit}.
"""
import os, re, json, numpy as np
from collections import defaultdict

DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
WD = os.environ.get("WD", "the internal storecrossmodel_27b")
SCORED = os.path.join(WD, "biber_scored.jsonl")
INPUT  = os.path.join(WD, "biber_input.jsonl")
MINSUB = int(os.environ.get("MINSUB", "20"))     # min docs for a subreddit to enter the centroid test

# ---------- Biber Dimension 1 feature extraction (verbatim from biber_reduction.py) ----------
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
    t = text.lower(); toks = WORD.findall(t); n = len(toks)
    if n < 30:
        return None
    alpha = ALPHA.findall(t)
    def rate(cnt): return 100.0 * cnt / n
    fp = sum(w in FIRST for w in toks); sp = sum(w in SECOND for w in toks)
    pv = sum(w in PRIVATE for w in toks)
    contr = len(CONTR.findall(text)) + len(NT.findall(text))
    presentbe = sum(w in {"am","is","are","'s","'re","'m","do","does","have","has"} for w in toks)
    dem = sum(w in DEMON for w in toks); emph = sum(w in EMPH for w in toks)
    ampl = sum(w in AMPL for w in toks)
    hedge = sum(w in HEDGE1 for w in toks) + t.count("sort of") + t.count("kind of") + t.count("i think") + t.count("i guess")
    disc = sum(w in DISC for w in toks) + t.count("you know")
    neg = sum(w == "not" for w in toks) + len(NT.findall(text))
    caus = sum(w in CAUSE for w in toks); wh = sum(w in WH for w in toks)
    poss = sum(w in POSS for w in toks); q = text.count("?")
    prep = sum(w in PREP for w in toks); art = sum(w in ARTICLE for w in toks)
    nom = sum(any(w.endswith(s) and len(w) > len(s) + 2 for s in NOMSUF) for w in alpha)
    mwl = float(np.mean([len(w) for w in alpha])) if alpha else 0.0
    window = toks[:100]; ttr = len(set(window)) / len(window) if window else 0.0
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
    body_of = {}; sub_of = {}
    for l in open(INPUT):
        r = json.loads(l); body_of[r["id"]] = r["text"]; sub_of[r["id"]] = r["subreddit"]
    ids, subs, CH = [], [], []
    for l in open(SCORED):
        r = json.loads(l); ch = r.get("axes")
        if not ch or not all(a in ch for a in DWEB) or r["id"] not in body_of:
            continue
        ids.append(r["id"]); subs.append(r.get("subreddit") or sub_of[r["id"]])
        CH.append([float(ch[a]) for a in DWEB])
    CH = np.array(CH, float)
    print(f"scored 27B reddit_wide docs: {len(ids)}", flush=True)

    # PC1 by SVD on the 27B char scores of the sampled docs themselves, rigour+depth oriented positive
    MEAN = CH.mean(0); STD = CH.std(0) + 1e-9
    _, _, Vt = np.linalg.svd((CH - MEAN) / STD, full_matrices=False); PC1 = Vt[0]
    if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0:
        PC1 = -PC1
    print("PC1 loadings (27B self, rigour+depth oriented positive):")
    for a, w in sorted(zip(DWEB, PC1), key=lambda t: -t[1]):
        print(f"  {a:<18} {w:+.3f}")
    PCv = ((CH - MEAN) / STD) @ PC1

    INV, INF, keep = [], [], []
    for i, _id in enumerate(ids):
        f = features(body_of[_id])
        if f is None:
            continue
        keep.append(i); INV.append(f[0]); INF.append(f[1])
    keep = np.array(keep)
    PCv = PCv[keep]; subs = [subs[i] for i in keep]
    INV = np.array(INV, float); INF = np.array(INF, float)
    print(f"usable docs after >=30-word floor: {len(PCv)}", flush=True)

    def z(M): return (M - M.mean(0)) / (M.std(0) + 1e-12)
    D1 = z(INV).mean(1) - z(INF).mean(1)     # Biber standardised-additive D1

    r_p = pearson(PCv, D1); r_s = spearman(PCv, D1)
    print(f"\n=== item-level PC1 vs Biber D1 ===  n={len(PCv)}")
    print(f"  Pearson  r = {r_p:+.3f}\n  Spearman r = {r_s:+.3f}")

    by = defaultdict(list)
    for s, p, d in zip(subs, PCv, D1):
        by[s].append((p, d))
    cent = []
    for s, lst in by.items():
        if len(lst) >= MINSUB:
            p = np.array([x[0] for x in lst]); d = np.array([x[1] for x in lst])
            cent.append((p.mean(), d.mean(), len(lst)))
    cp = np.array([x[0] for x in cent]); cd = np.array([x[1] for x in cent])
    r_cent_p = pearson(cp, cd); r_cent_s = spearman(cp, cd)
    print(f"\n=== between-subreddit centroids ({len(cent)} subreddits, n>={MINSUB}, Biber's own genre unit) ===")
    print(f"  Pearson  r = {r_cent_p:+.3f}\n  Spearman r = {r_cent_s:+.3f}")

    summary = {
        "n_docs": int(len(PCv)),
        "item_level": {"pearson_r": r_p, "spearman_r": r_s},
        "between_subreddit_centroid": {"n_subreddits": len(cent),
                                       "pearson_r": r_cent_p, "spearman_r": r_cent_s},
        "pc1_loadings": {a: float(w) for a, w in zip(DWEB, PC1)},
    }
    json.dump(summary, open(os.path.join(WD, "biber_27b_summary.json"), "w"), indent=2)
    print(f"\nwrote {os.path.join(WD, 'biber_27b_summary.json')}", flush=True)


if __name__ == "__main__":
    main()

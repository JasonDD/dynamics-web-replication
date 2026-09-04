#!/usr/bin/env python3
"""analyse_modality.py — place the new modality/register corpora on the character map.

Builds a reference frame from held scored corpora (same 8-axis instrument), computes the mean character of
each NEW register, then places it: matter/manner (PC1 proxy), the affect-to-matter contrast, an empirical
PCA-PC1 over all corpus means, and the nearest held anchor + distance. Reports which registers land in a
sparse region (far from every held anchor) = genuinely new map territory.

Reads scored jsonl on the internal store; writes a compact analysis block to stdout (captured into RESULT.md).
"""
import os, json, math
import numpy as np

BASE = "the internal corpus store"
AXES = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
MATTER = ["rigour", "depth", "originality"]   # substance
MANNER = ["affect", "stance", "register"]      # heat / delivery
NMAX = 600

# Held anchor corpora: (label, relative path, register descriptor)
ANCHORS = [
    ("cmv_web_argument", "cmv_winning_args/cmv_scores.jsonl", "web argument (Reddit CMV)"),
    ("oldbailey_court", "oldbailey/oldbailey_scored.jsonl", "court trial (historical)"),
    ("ungd_diplomatic", "ungd/ungd_char8.jsonl", "diplomatic speech (UN)"),
    ("parlamint_parliament", "parlamint/sample_scored.jsonl", "parliament (EU)"),
    ("darwin_private_letters", "darwin_letters/bioarc_scored.jsonl", "private letters"),
    ("sacred_text", "sacred_secular/sacred_scored.jsonl", "sacred text"),
    ("echr_ruling", "legal_matrix/echr_scored.jsonl", "court ruling (ECHR)"),
    ("financial_filings", "comms_scout/a_filings_scored.jsonl", "corporate/financial filings"),
    ("dark_forum_criminal", "dnm_archives/scored_andromeda.jsonl", "illicit forum"),
    ("boe_central_bank", "comms_scout/boe_scored.jsonl", "central-bank communication"),
    ("knesset_parliament", "knesset_corpus/knesset_attribute_scored.jsonl", "parliament (Israel)"),
    ("toxic_web_comments", "toxicity_civilcomments/scored.jsonl", "toxic web comments"),
    ("histchar_periodicals", "histchar/histchar.jsonl", "historical periodicals"),
    ("upworthy_headlines", "causal/causal_char.jsonl", "clickbait headlines (A/B)"),
    ("uk_petitions", "uk_petitions/cluster_members_scored.jsonl", "petitions"),
    ("bible_multilingual", "bible_multilingual/fingerprint_scored.jsonl", "scripture (multilingual)"),
]

NEW = [
    ("scotus_oral_spoken", "spoken: US Supreme Court oral argument"),
    ("ted_talks_spoken", "spoken: TED prepared monologue"),
    ("podcast_spoken", "spoken: podcast conversation"),
    ("movie_dialogs_creative", "creative: film/TV dialogue"),
    ("poetry_creative", "creative: public-domain verse"),
    ("fiction_openings_creative", "creative: narrative fiction"),
    ("arxiv_abstracts_technical", "technical: arXiv abstracts"),
    ("pubmed_abstracts_technical", "technical: PubMed abstracts"),
    ("contracts_cuad_technical", "technical: legal contracts (CUAD)"),
    ("patent_abstracts_technical", "technical: patent abstracts"),
    ("job_postings_transactional", "transactional: job postings"),
    ("product_descriptions_transactional", "transactional: product descriptions"),
    ("complaints_transactional", "transactional: customer complaints"),
]


def extract_char(rec):
    for key in ("char", "axes"):
        c = rec.get(key)
        if isinstance(c, dict) and all(k in c for k in AXES):
            try:
                return [float(c[k]) for k in AXES]
            except Exception:
                pass
    if all(k in rec for k in AXES):
        try:
            return [float(rec[k]) for k in AXES]
        except Exception:
            return None
    return None


def load_means(relpath):
    p = relpath if os.path.isabs(relpath) else os.path.join(BASE, relpath)
    if not (os.path.exists(p) and os.path.getsize(p) > 0):
        return None, 0
    vecs = []
    for l in open(p):
        try:
            r = json.loads(l)
        except Exception:
            continue
        v = extract_char(r)
        if v:
            vecs.append(v)
        if len(vecs) >= NMAX:
            break
    if not vecs:
        return None, 0
    return np.array(vecs).mean(axis=0), len(vecs)


def matter_manner(mean_vec):
    idx = {a: i for i, a in enumerate(AXES)}
    matter = float(np.mean([mean_vec[idx[a]] for a in MATTER]))
    manner = float(np.mean([mean_vec[idx[a]] for a in MANNER]))
    return matter, manner


def main():
    # ---- load anchors
    anchor_rows = []
    for label, rel, desc in ANCHORS:
        m, n = load_means(rel)
        if m is not None:
            anchor_rows.append((label, desc, m, n))
    # ---- load new corpora
    new_rows = []
    for name, desc in NEW:
        m, n = load_means(os.path.join(name, f"{name}_scored.jsonl"))
        if m is not None:
            new_rows.append((name, desc, m, n))

    A = np.array([r[2] for r in anchor_rows])
    N = np.array([r[2] for r in new_rows]) if new_rows else np.zeros((0, 8))
    allM = np.vstack([A, N]) if len(new_rows) else A

    # ---- empirical PCA-PC1 over ALL corpus means (anchors + new)
    mu = allM.mean(axis=0)
    Xc = allM - mu
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    pc1 = Vt[0]
    # orient PC1 so + = matter (rigour+depth+originality loading positive)
    idx = {a: i for i, a in enumerate(AXES)}
    matter_load = sum(pc1[idx[a]] for a in MATTER) - sum(pc1[idx[a]] for a in MANNER)
    if matter_load < 0:
        pc1 = -pc1
    pc2 = Vt[1]
    var = (S ** 2) / (S ** 2).sum()

    def proj(v):
        return float((v - mu) @ pc1), float((v - mu) @ pc2)

    print("# analysis stamp")
    print(f"anchors_loaded={len(anchor_rows)} new_loaded={len(new_rows)}")
    print(f"pc1_var={var[0]:.3f} pc2_var={var[1]:.3f}")
    print("pc1_loadings=" + ", ".join(f"{a}:{pc1[i]:+.2f}" for i, a in enumerate(AXES)))
    print()

    print("## ANCHOR FRAME (held corpora)")
    print("label | desc | n | " + " ".join(AXES) + " | matter manner | pc1 pc2")
    for label, desc, m, n in sorted(anchor_rows, key=lambda r: proj(r[2])[0]):
        mt, mn = matter_manner(m)
        p1, p2 = proj(m)
        print(f"{label} | {desc} | {n} | " + " ".join(f"{x:.2f}" for x in m) +
              f" | {mt:.2f} {mn:.2f} | {p1:+.2f} {p2:+.2f}")
    print()

    # sparsity threshold from anchor-to-anchor nearest-neighbour distances
    def nn_dist(v, pool):
        return sorted((float(np.linalg.norm(v - p[2])), p[0]) for p in pool)

    anchor_nn = []
    for i, r in enumerate(anchor_rows):
        others = anchor_rows[:i] + anchor_rows[i + 1:]
        anchor_nn.append(nn_dist(r[2], others)[0][0])
    anchor_nn = np.array(anchor_nn)
    med_nn = float(np.median(anchor_nn))
    thr = float(np.percentile(anchor_nn, 90))
    print(f"anchor_nn_median={med_nn:.3f} anchor_nn_p90(threshold)={thr:.3f}")
    print()

    print("## NEW REGISTERS placed")
    print("name | desc | n | " + " ".join(AXES) + " | matter manner | pc1 pc2 | nearest_anchor(dist) | NEW_REGION")
    verdicts = []
    for name, desc, m, n in new_rows:
        mt, mn = matter_manner(m)
        p1, p2 = proj(m)
        nn = nn_dist(m, anchor_rows)
        nearest, nd = nn[0][1], nn[0][0]
        new_region = nd > thr
        verdicts.append((name, desc, nd, nearest, new_region, mt, mn, p1))
        print(f"{name} | {desc} | {n} | " + " ".join(f"{x:.2f}" for x in m) +
              f" | {mt:.2f} {mn:.2f} | {p1:+.2f} {p2:+.2f} | {nearest}({nd:.2f}) | {'YES' if new_region else 'no'}")
    print()
    print("## VERDICT — new territory (nearest-anchor distance > anchor p90)")
    for name, desc, nd, nearest, nr, mt, mn, p1 in sorted(verdicts, key=lambda x: -x[2]):
        tag = "NEW REGION" if nr else "within known space"
        print(f"{name}: dist_to_nearest_held={nd:.2f} (nearest={nearest}) -> {tag}")


if __name__ == "__main__":
    main()

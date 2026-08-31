#!/usr/bin/env python3
"""analyse_bioarc.py — the biographical-arc regression.

Question: does an individual's WRITING CHARACTER drift monotonically over a whole life,
or is the person a fixed point while only the room (correspondent, topic, length) changes?

For Charles Darwin (453 dated, editor-cleaned letters, 1828-1882, age 19-73):
  - regress each of the 8 DWEB axes, the matter/manner PC1, and a fixed matter-minus-manner
    contrast on the author's AGE at writing;
  - CONTROL for length (letters lengthen/shorten over a life and matter needs bandwidth):
    partial the age slope on log(word count);
  - hold the correspondent fixed (Hooker n=131, Lyell n=72) and re-run;
  - check the age slope survives an editorial-density (ed_frac) covariate.

A significant, consistent age slope after the length control = the person drifts.
A flat slope = the person is a fixed point and earlier context findings were all room.
"""
import os, json, math
import numpy as np
import statsmodels.api as sm

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXES = ["rigour", "depth", "originality", "candour", "affect",
        "commercial_drive", "stance", "register"]
MATTER = ["rigour", "depth", "originality"]
MANNER = ["affect", "commercial_drive", "stance", "register"]
ALPHA_BONF = 0.05 / len(AXES)  # 8 axes


def load():
    meta = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(D, "meta_clean.jsonl"))}
    rows = []
    for l in open(os.path.join(D, "bioarc_scored.jsonl")):
        r = json.loads(l)
        m = meta.get(r["id"])
        if not m or not r.get("char"):
            continue
        rec = {"id": r["id"], "age": m["age"], "year": m["year"],
               "recipient": r["kind"], "wc": m["wordcount_clean"],
               "ed_frac": m.get("ed_frac", 0.0), "log_wc": math.log(m["wordcount_clean"])}
        rec.update({a: float(r["char"][a]) for a in AXES})
        rec["matter"] = np.mean([rec[a] for a in MATTER])
        rec["manner"] = np.mean([rec[a] for a in MANNER])
        rec["mm"] = rec["matter"] - rec["manner"]
        rows.append(rec)
    return rows


def pca_pc1(rows):
    X = np.array([[r[a] for a in AXES] for r in rows], float)
    Xz = (X - X.mean(0)) / X.std(0)
    U, S, Vt = np.linalg.svd(Xz - Xz.mean(0), full_matrices=False)
    load = Vt[0]
    # orient so the matter pole (rigour+depth+originality) is positive
    mi = [AXES.index(a) for a in MATTER]
    if load[mi].mean() < 0:
        load = -load
    pc1 = Xz @ load
    var_expl = (S[0] ** 2) / (S ** 2).sum()
    for i, r in enumerate(rows):
        r["pc1"] = float(pc1[i])
    return dict(zip(AXES, [round(float(x), 3) for x in load])), round(float(var_expl), 3)


def slope(rows, y, covars):
    """OLS y ~ age + covars. Return (coef_age_per_decade, p_age, r2, n) and covar coefs."""
    yv = np.array([r[y] for r in rows], float)
    cols = ["age"] + covars
    Xd = np.column_stack([[r[c] for r in rows] for c in cols]).astype(float)
    Xd = sm.add_constant(Xd)
    m = sm.OLS(yv, Xd).fit()
    idx = 1  # age is first after const
    return {"age_per_decade": round(float(m.params[idx]) * 10, 4),
            "p_age": float(m.pvalues[idx]),
            "r2": round(float(m.rsquared), 3),
            "n": int(m.nobs),
            "covar_coefs": {c: round(float(m.params[i + 1]), 4) for i, c in enumerate(cols) if c != "age"}}


def block(rows, label):
    print(f"\n===== {label} (n={len(rows)}) =====")
    # confound: does length track age?
    a = np.array([r["age"] for r in rows]); w = np.array([r["log_wc"] for r in rows])
    rc = np.corrcoef(a, w)[0, 1]
    print(f"corr(age, log_wc) = {rc:.3f}  (length-vs-age confound structure)")
    out = {"n": len(rows), "corr_age_logwc": round(float(rc), 3), "targets": {}}
    print(f"{'target':<16}{'raw/decade':>12}{'p_raw':>10}{'lenctl/decade':>15}{'p_lenctl':>11}{'verdict':>10}")
    for y in AXES + ["mm", "pc1"]:
        raw = slope(rows, y, [])
        ctl = slope(rows, y, ["log_wc"])
        sig = "DRIFT" if ctl["p_age"] < ALPHA_BONF else ("weak" if ctl["p_age"] < 0.05 else "flat")
        print(f"{y:<16}{raw['age_per_decade']:>12.4f}{raw['p_age']:>10.4f}"
              f"{ctl['age_per_decade']:>15.4f}{ctl['p_age']:>11.4f}{sig:>10}")
        out["targets"][y] = {"raw": raw, "len_ctl": ctl, "verdict": sig}
    return out


def main():
    rows = load()
    if len(rows) < 30:
        print(f"only {len(rows)} scored so far — wait for the run to finish"); return
    load_pc1, var = pca_pc1(rows)
    print(f"letters scored: {len(rows)}")
    print(f"PC1 loadings (oriented matter-positive): {load_pc1}")
    print(f"PC1 variance explained: {var}")
    result = {"n_total": len(rows), "pc1_loadings": load_pc1, "pc1_var_explained": var,
              "alpha_bonferroni": round(ALPHA_BONF, 5),
              "age_range": [min(r['age'] for r in rows), max(r['age'] for r in rows)],
              "blocks": {}}
    result["blocks"]["all"] = block(rows, "ALL LETTERS")
    for corr in ["J.D. HOOKER", "C. LYELL"]:
        sub = [r for r in rows if r["recipient"] == corr]
        if len(sub) >= 30:
            result["blocks"][corr] = block(sub, f"FIXED CORRESPONDENT = {corr}")
    # editorial covariate check on PC1 and rigour (all letters)
    print("\n===== editorial-density robustness (all letters) =====")
    edchk = {}
    for y in ["pc1", "rigour", "mm"]:
        c = slope(rows, y, ["log_wc", "ed_frac"])
        print(f"{y:<10} age/decade (len+ed ctl) = {c['age_per_decade']:+.4f}  p={c['p_age']:.4f}")
        edchk[y] = c
    result["editorial_ctl"] = edchk
    json.dump(result, open(os.path.join(D, "stats.json"), "w"), indent=2)
    print(f"\nwrote {os.path.join(D, 'stats.json')}")


if __name__ == "__main__":
    main()

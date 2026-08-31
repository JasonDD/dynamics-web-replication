#!/usr/bin/env python3
"""bioarc_supplement.py — nail the composition mechanism behind the pooled age drift.

If the pooled 'drift over a life' is really a change in WHO Darwin wrote to (the room),
then adding a correspondent fixed effect should collapse the age slope toward zero, and
between correspondents the mean writing-age should track the mean matter score.

Also emits the descriptive per-decade trajectory for the write-up.
"""
import os, json, math
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXES = ["rigour", "depth", "originality", "candour", "affect",
        "commercial_drive", "stance", "register"]
MATTER = ["rigour", "depth", "originality"]
MANNER = ["affect", "commercial_drive", "stance", "register"]


def load():
    meta = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(D, "meta_clean.jsonl"))}
    rows = []
    for l in open(os.path.join(D, "bioarc_scored.jsonl")):
        r = json.loads(l)
        m = meta.get(r["id"])
        if not m or not r.get("char"):
            continue
        d = {"age": m["age"], "year": m["year"], "recipient": r["kind"],
             "log_wc": math.log(m["wordcount_clean"])}
        d.update({a: float(r["char"][a]) for a in AXES})
        d["matter"] = np.mean([d[a] for a in MATTER])
        d["manner"] = np.mean([d[a] for a in MANNER])
        d["mm"] = d["matter"] - d["manner"]
        rows.append(d)
    df = pd.DataFrame(rows)
    # PC1 (matter-oriented) to match the main analyser
    X = df[AXES].values
    Xz = (X - X.mean(0)) / X.std(0)
    U, S, Vt = np.linalg.svd(Xz - Xz.mean(0), full_matrices=False)
    load = Vt[0]
    if load[[AXES.index(a) for a in MATTER]].mean() < 0:
        load = -load
    df["pc1"] = Xz @ load
    return df


def fe_test(df, y):
    """pooled age slope vs correspondent fixed-effect age slope (recurrent correspondents)."""
    pooled = smf.ols(f"{y} ~ age + log_wc", data=df).fit()
    rec = df["recipient"].value_counts()
    keep = rec[rec >= 8].index
    sub = df[df["recipient"].isin(keep)].copy()
    fe = smf.ols(f"{y} ~ age + log_wc + C(recipient)", data=sub).fit()
    return {
        "pooled_age_per_decade": round(pooled.params["age"] * 10, 4),
        "pooled_p": float(pooled.pvalues["age"]),
        "fe_age_per_decade": round(fe.params["age"] * 10, 4),
        "fe_p": float(fe.pvalues["age"]),
        "n_pooled": int(pooled.nobs), "n_fe": int(fe.nobs),
        "n_correspondents_fe": int(len(keep)),
    }


def main():
    df = load()
    out = {}
    print("=== composition test: does a correspondent fixed effect kill the age slope? ===")
    print(f"{'target':<8}{'pooled/dec':>12}{'p':>9}{'FE/dec':>10}{'p':>9}   interpretation")
    for y in ["pc1", "mm", "rigour", "depth", "affect", "register"]:
        r = fe_test(df, y)
        out[y] = r
        shrink = "COMPOSITION (age slope collapses under FE)" if (r["pooled_p"] < 0.05 and r["fe_p"] > 0.05) \
            else ("within-person (survives FE)" if r["fe_p"] < 0.05 else "flat both")
        print(f"{y:<8}{r['pooled_age_per_decade']:>12.4f}{r['pooled_p']:>9.4f}"
              f"{r['fe_age_per_decade']:>10.4f}{r['fe_p']:>9.4f}   {shrink}")

    print("\n=== between-correspondent: mean writing-age vs mean matter (top correspondents n>=8) ===")
    rec = df["recipient"].value_counts()
    top = rec[rec >= 8].index
    btab = []
    for c in top:
        s = df[df["recipient"] == c]
        btab.append((c, len(s), round(s["age"].mean(), 1), round(s["mm"].mean(), 3),
                     round(s["pc1"].mean(), 3)))
    btab.sort(key=lambda x: x[2])  # by mean age
    print(f"{'correspondent':<18}{'n':>4}{'mean_age':>9}{'mean_mm':>9}{'mean_pc1':>9}")
    for c, n, a, mm, p in btab:
        print(f"{c:<18}{n:>4}{a:>9}{mm:>9}{p:>9}")
    ages = np.array([b[2] for b in btab]); mms = np.array([b[3] for b in btab])
    pcs = np.array([b[4] for b in btab])
    r_mm = np.corrcoef(ages, mms)[0, 1]
    r_pc = np.corrcoef(ages, pcs)[0, 1]
    print(f"\nbetween-correspondent corr(mean_age, mean_mm)  = {r_mm:.3f}")
    print(f"between-correspondent corr(mean_age, mean_pc1) = {r_pc:.3f}")
    out["between_correspondent"] = {"corr_age_mm": round(float(r_mm), 3),
                                    "corr_age_pc1": round(float(r_pc), 3),
                                    "table": [{"recipient": c, "n": n, "mean_age": a,
                                               "mean_mm": mm, "mean_pc1": p} for c, n, a, mm, p in btab]}

    print("\n=== descriptive per-decade-of-age trajectory (pooled) ===")
    df["decade"] = (df["age"] // 10 * 10).astype(int)
    traj = []
    print(f"{'age band':<10}{'n':>4}" + "".join(f"{a[:6]:>8}" for a in ["rigour", "depth", "affect", "register", "mm", "pc1"]))
    for d in sorted(df["decade"].unique()):
        s = df[df["decade"] == d]
        row = {"age_band": f"{d}s", "n": int(len(s))}
        for a in ["rigour", "depth", "affect", "register", "mm", "pc1"]:
            row[a] = round(float(s[a].mean()), 3)
        traj.append(row)
        print(f"{d}s (age)".ljust(10) + f"{len(s):>4}" +
              "".join(f"{row[a]:>8.3f}" for a in ["rigour", "depth", "affect", "register", "mm", "pc1"]))
    out["decade_trajectory"] = traj

    json.dump(out, open(os.path.join(D, "supplement.json"), "w"), indent=2)
    print(f"\nwrote {os.path.join(D, 'supplement.json')}")


if __name__ == "__main__":
    main()

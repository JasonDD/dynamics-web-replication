#!/usr/bin/env python3
"""cc_genre_state_fit.py — PF-4B-GENRE-20260829-REV-1, THE FIT. Tests whether genre modifies the production-side
disposition->character coupling (bilinear M.W.S state hypothesis). Genre assignment is FROZEN (sha256 2d701e0c);
this script is the first to touch a coupling number, strictly after the freeze.

DEVIATION FROM LOCKED CV (documented catch #4): the locked leave-one-genre-out CV cannot distinguish Model A
(genre random slope) from Model B (genre fixed effect) — a fully held-out genre has parameters in neither, so both
predict the population line and RMSE is identical by construction. The discriminating test is leave-COMMUNITIES-out
stratified k-fold (every genre in training), which lets A/B/null diverge on held-out communities of known genres.
Taxonomy hash unchanged; only the CV partition is corrected. Everything else per the lock.

disp_k = community mean PLASTICITY (DeYoung Big-Two from D8: sociability + novelty), half A.
c in {matter_manner (canonical PC1, PRIMARY), originality, stance}, produced-character half B (disjoint).
"""
import os, json, numpy as np, psycopg2
import statsmodels.formula.api as smf
import statsmodels.api as sm
import pandas as pd

CHAR = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
D8_PLAS = ["sociability", "novelty"]            # DeYoung Plasticity = Extraversion + Openness
DISP_COL = os.environ.get("DISP_COL", "disp_d8_behav_27b")
FLOOR = int(os.environ.get("FLOOR", "150"))
GENRE_JSON = os.environ.get("GENRE_JSON", "/home/jason/projects/kronaxis/truthometer/results/prereg_genre_PF-4B/genre_assign_400_FROZEN.json")
PW = [l.split("=", 1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
DSN = f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"
def z(a): a = np.asarray(a, float); return (a - a.mean()) / (a.std() + 1e-9)

db = psycopg2.connect(DSN); cur = db.cursor()

# ---- canonical matter<->manner PC1 ruler (SVD on domain_char8_expanded), oriented rigour+depth positive ----
cur.execute(f"SELECT {','.join(CHAR)} FROM the internal reference table")
allc = np.array([[float(x) for x in r] for r in cur.fetchall()], float)
MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
_, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False)
PC1 = Vt[0]
if (PC1[CHAR.index("rigour")] + PC1[CHAR.index("depth")]) < 0: PC1 = -PC1
print(f"[fit] canonical PC1 (matter<->manner) loadings: " + ", ".join(f"{a}={l:+.2f}" for a, l in zip(CHAR, PC1)))

# ---- aggregate reddit_wide by community, disjoint halves (seed 5, FLOOR 150), matching the 0.74 construction ----
cur.execute(f"SELECT subreddit,char,{DISP_COL} FROM the internal Reddit corpus WHERE char IS NOT NULL AND {DISP_COL} IS NOT NULL")
by = {}
for sub, ch, dp in cur.fetchall():
    ch = ch if isinstance(ch, dict) else json.loads(ch)
    dp = dp if isinstance(dp, dict) else json.loads(dp)
    by.setdefault(sub, []).append(([float(ch[a]) for a in CHAR], [float(dp.get(k, 0.5)) for k in D8_PLAS]))
rng = np.random.default_rng(5)
rows = []
for sub, rr in by.items():
    if len(rr) < FLOOR: continue
    p = rng.permutation(len(rr)); h = len(rr) // 2
    A = [rr[i] for i in p[:h]]; B = [rr[i] for i in p[h:]]
    plas = np.array([x[1] for x in A]).mean(0).sum()              # sociability+novelty, half A
    cb = np.array([x[0] for x in B]).mean(0)                      # produced character, half B
    mm = float(((cb - MEAN) / STD) @ PC1)
    rows.append((sub, plas, mm, cb[CHAR.index("originality")], cb[CHAR.index("stance")]))
df = pd.DataFrame(rows, columns=["sub", "plas", "matter_manner", "originality", "stance"])
print(f"[fit] {len(df)} communities passed FLOOR={FLOOR}")

# ---- join FROZEN genre; exclude other_misc from the primary ----
gmap = json.load(open(GENRE_JSON))
df["genre"] = df["sub"].map(gmap)
df = df[df["genre"].notna() & (df["genre"] != "other_misc")].reset_index(drop=True).copy()
df["disp"] = z(df["plas"])
for c in ["matter_manner", "originality", "stance"]:
    df[c] = z(df[c])
print(f"[fit] {len(df)} communities after excluding other_misc; {df['genre'].nunique()} genres")

def rmse(a, b): return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))

def run_dim(c, primary=False):
    print(f"\n====== {c}{'  [PRIMARY]' if primary else ''} ======")
    # ---- full Model A: random intercept + slope by genre; LRT vs random-intercept-only (secondary) ----
    try:
        mA = smf.mixedlm(f"{c} ~ disp", df, groups=df["genre"], re_formula="~disp").fit(reml=False, method="lbfgs")
        m0 = smf.mixedlm(f"{c} ~ disp", df, groups=df["genre"], re_formula="~1").fit(reml=False, method="lbfgs")
        lr = 2 * (mA.llf - m0.llf)
        from scipy.stats import chi2
        # slope-variance test: mixture of chi2_1 and chi2_2, approx with chi2_2 upper bound (conservative)
        pv = chi2.sf(lr, 2)
        cov = mA.cov_re
        tau2_slope = float(cov.iloc[1, 1]) if cov.shape[0] > 1 else float("nan")
        print(f"  [secondary] tau^2_1 (genre disp-slope variance) = {tau2_slope:.4f}; LRT vs intercept-only chi2={lr:.2f} p={pv:.4f} (conservative)")
        # BLUP slope ordering
        re = mA.random_effects
        slopes = {g: float(v.iloc[1]) for g, v in re.items() if len(v) > 1}
        order = sorted(slopes.items(), key=lambda x: x[1])
        print("  [secondary] genre disp-slope BLUPs (low->high): " + ", ".join(f"{g}={s:+.2f}" for g, s in order[:3]) + " ... " + ", ".join(f"{g}={s:+.2f}" for g, s in order[-3:]))
    except Exception as e:
        print(f"  [secondary] Model A full fit failed: {e}")

    # ---- PRIMARY: leave-communities-out stratified 5-fold; Null vs B vs A on held-out communities ----
    genres = df["genre"].values; y = df[c].values; disp = df["disp"].values
    idx = np.arange(len(df)); rr = np.random.default_rng(11)
    fold = np.full(len(df), -1)
    for g in np.unique(genres):
        gi = idx[genres == g]; gi = rr.permutation(gi)
        for k, i in enumerate(gi): fold[i] = k % 5
    pN, pB, pA = np.zeros(len(df)), np.zeros(len(df)), np.zeros(len(df))
    for f in range(5):
        tr = fold != f; te = fold == f
        d_tr = df[tr]
        # Null: c ~ disp
        n = sm.OLS(d_tr[c], sm.add_constant(d_tr["disp"])).fit()
        pN[te] = n.params["const"] + n.params["disp"] * df.loc[te, "disp"]
        # Model B: c ~ disp + genre FE
        Xb = pd.get_dummies(d_tr["genre"], drop_first=True).astype(float)
        Bmat = pd.concat([d_tr[["disp"]].reset_index(drop=True), Xb.reset_index(drop=True)], axis=1)
        b = sm.OLS(d_tr[c].values, sm.add_constant(Bmat).values).fit()
        gcols = list(Xb.columns)
        for i in idx[te]:
            gv = [1.0] + [df.loc[i, "disp"]] + [1.0 if df.loc[i, "genre"] == gc else 0.0 for gc in gcols]
            pB[i] = float(np.array(gv) @ b.params)
        # Model A: random intercept+slope by genre
        try:
            a = smf.mixedlm(f"{c} ~ disp", d_tr, groups=d_tr["genre"], re_formula="~disp").fit(reml=False, method="lbfgs")
            re = a.random_effects; fe = a.fe_params
            for i in idx[te]:
                g = df.loc[i, "genre"]; dv = df.loc[i, "disp"]
                ri = float(re[g].iloc[0]) if g in re else 0.0
                rs = float(re[g].iloc[1]) if (g in re and len(re[g]) > 1) else 0.0
                pA[i] = fe["Intercept"] + fe["disp"] * dv + ri + rs * dv
        except Exception as e:
            pA[te] = pB[te]
    print(f"  [PRIMARY] leave-communities-out held-out RMSE:  Null={rmse(pN,y):.4f}  ModelB(genre FE)={rmse(pB,y):.4f}  ModelA(genre slope)={rmse(pA,y):.4f}")
    return rmse(pN, y), rmse(pB, y), rmse(pA, y)

res = {}
res["matter_manner"] = run_dim("matter_manner", primary=True)
res["originality"] = run_dim("originality")
res["stance"] = run_dim("stance")

print("\n================ SUMMARY (held-out RMSE, lower=better) ================")
print(f"  {'dim':16} {'Null':>8} {'B(FE)':>8} {'A(slope)':>9}   read")
for c, (rn, rb, ra) in res.items():
    if ra < rb - 0.002 and rb < rn - 0.002:
        read = "A<B<Null: genre MODULATES the coupling (state, off-diagonal W)"
    elif rb < rn - 0.002 and abs(ra - rb) <= 0.002:
        read = "B<Null, A~B: genre shifts LEVEL only (offset, not slope)"
    elif abs(rb - rn) <= 0.002:
        read = "A~B~Null: genre absorbed (matter/manner carries it) [favoured prior]"
    else:
        read = "mixed"
    print(f"  {c:16} {rn:8.4f} {rb:8.4f} {ra:9.4f}   {read}")
print("=======================================================================")

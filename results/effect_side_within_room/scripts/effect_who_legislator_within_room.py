#!/usr/bin/env python3
"""effect_who_legislator_within_room.py -- WITHIN ROOM test of the EFFECT side WHO clause.

Paper 4B grounds the WHO clause ("the reader's disposition individuates the winning
coordinate") on the European legislator link: across roughly fourteen hundred legislators a
speaker's left to right position correlates with their character, the left leaning matter and
the right leaning manner. The published number is a POOLED Pearson correlation over 26
countries with no country control (truthometer/scripts/cc_parlamint_analyse.py):

    corr(lr, matter/manner PC1) = -0.109  p=0.000  n=1395

The production side has just been shown (memo #20180/#20181, commit 2759e8472) to have had a
large part of a person level coupling turn out to be WHO GATHERS WHERE. The same confound is
available here: the countries differ enormously in character (between country mean distance
3.81 standardised) AND in the left right composition of who speaks. This script asks whether
the WHO link survives when legislators are compared INSIDE the same country.

Room = country (which also holds language fixed, the confound the original run named).
Person = speaker. Disposition P = lr (left to right, party level). Character C = the canonical
matter against manner ruler, PC1 of the eight axes built on cc_v3.domain_char8_expanded, the
same ruler the rest of the series uses. Secondary outcomes: stance, affect.

Traps carried, matching the production side test:
  PERSON LEAKAGE   -- every speaker sits in exactly one country, verified not assumed, so a
                      speaker cannot be split across a between and a within contrast. Repeated
                      speeches are collapsed to one speaker record before any contrast.
  NONLINEARITY     -- a per room LINEAR slope differs between rooms with different lr RANGES
                      even with no true modulation. The pair design carries an antisymmetric
                      curvature term dP x centred mean P, so the no intercept algebra holds.
  WILD BOOTSTRAP   -- the null fixes each room's own lr design and residual scale and flips
                      residual signs at the cluster level. A record permutation null would
                      wrongly blame rooms with a narrow lr spread.
  ATTENUATION      -- reliability of the speaker character mean is MEASURED from the scatter of
                      that speaker's own speeches, not assumed. Raw and corrected side by side.
  CLUSTERING       -- lr is a PARTY level attribute. A speech level standard error treats 1,675
                      speeches as 1,675 independent draws of lr when there are only a couple of
                      hundred distinct party values. Reported at every level.
"""
import os, json, math, time
from collections import defaultdict, Counter
import numpy as np
import psycopg2
from scipy import stats

t0 = time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

CHAR = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
SRC = os.environ.get("SRC", "/mnt/nas/kronaxis/corpora/parlamint/sample_scored.jsonl")
OUT = os.environ.get("OUT", "/home/jason/effect_confound/who_legislator.json")
NBOOT = int(os.environ.get("NBOOT", "4000"))
SEED = int(os.environ.get("SEED", "20260903"))
PAIRCAP = int(os.environ.get("PAIRCAP", "400"))
rng = np.random.default_rng(SEED)
RES = {}

# ------------------------------------------------------------------ the canonical ruler
PW = [l.split("=", 1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
db = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs")
cur = db.cursor()
log("building the canonical matter against manner ruler ...")
cur.execute(f"SELECT {','.join(CHAR)} FROM cc_v3.domain_char8_expanded")
allc = np.array([[float(v) for v in r] for r in cur.fetchall()], float)
MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
_, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False); PC1 = Vt[0]
if (PC1[CHAR.index("rigour")] + PC1[CHAR.index("depth")]) < 0: PC1 = -PC1
db.close()
log(f"ruler rows={len(allc):,}  PC1: " + ", ".join(f"{a}={l:+.2f}" for a, l in zip(CHAR, PC1)))
RES["ruler"] = dict(rows=int(len(allc)), pc1=dict(zip(CHAR, [round(float(x), 3) for x in PC1])))

def pc1_of(ch):
    return float(((np.array([ch[a] for a in CHAR], float) - MEAN) / STD) @ PC1)

# ------------------------------------------------------------------ load
rows = []
for line in open(SRC):
    try: r = json.loads(line)
    except Exception: continue
    if "char" not in r: continue
    try: lr = float(r.get("lr", "") if r.get("lr", "") != "" else "nan")
    except (TypeError, ValueError): lr = float("nan")
    rows.append(dict(country=r["country"], speaker=r.get("speaker") or "", party=r.get("party") or "",
                     lr=lr, pc1=pc1_of(r["char"]),
                     stance=float(r["char"]["stance"]), affect=float(r["char"]["affect"]),
                     n_words=float(r.get("n_words") or 0)))
log(f"speeches loaded={len(rows):,}  countries={len({r['country'] for r in rows})}  "
    f"speakers={len({r['speaker'] for r in rows})}")

use = [r for r in rows if r["lr"] == r["lr"] and r["speaker"]]
log(f"speeches with a usable lr and speaker id = {len(use):,}")

# ------------------------------------------------------------------ 0. person leakage check
spk_countries = defaultdict(set); spk_parties = defaultdict(set)
for r in use:
    spk_countries[r["speaker"]].add(r["country"]); spk_parties[r["speaker"]].add(r["party"])
cross = [s for s, c in spk_countries.items() if len(c) > 1]
log(f"PERSON LEAKAGE CHECK: speakers appearing in more than one country = {len(cross)} "
    f"(of {len(spk_countries):,}) -> {'CLEAN' if not cross else 'LEAKAGE PRESENT'}")
RES["leakage"] = dict(speakers=len(spk_countries), cross_country=len(cross),
                      multi_party=len([s for s, p in spk_parties.items() if len(p) > 1]))

# ------------------------------------------------------------------ 0b. where does lr actually vary?
# lr is coded per party. Decompose its variance: between country, between party within country,
# within party. If the last is zero, the finest room in which the WHO claim can be posed AT ALL
# is the country, and the effective sample size is parties, not speeches.
lrv = np.array([r["lr"] for r in use], float)
cc = np.array([r["country"] for r in use], dtype=object)
pp = np.array([r["country"] + "|" + r["party"] for r in use], dtype=object)
def ss_between(values, groups):
    g = defaultdict(list)
    for v, k in zip(values, groups): g[k].append(v)
    gm = {k: np.mean(v) for k, v in g.items()}
    grand = values.mean()
    return float(sum(len(v) * (gm[k] - grand) ** 2 for k, v in g.items())), gm
sst = float(((lrv - lrv.mean()) ** 2).sum())
ss_c, _ = ss_between(lrv, cc)
ss_p, party_mean = ss_between(lrv, pp)
log(f"lr variance decomposition (total SS={sst:.1f}): between country {100*ss_c/sst:.1f}%   "
    f"between party (nested) {100*(ss_p-ss_c)/sst:.1f}%   within party {100*(sst-ss_p)/sst:.1f}%")
log(f"distinct country-party cells = {len(set(pp))}   distinct countries = {len(set(cc))}")
RES["lr_variance"] = dict(total_ss=sst, pct_between_country=100 * ss_c / sst,
                          pct_between_party_within_country=100 * (ss_p - ss_c) / sst,
                          pct_within_party=100 * (sst - ss_p) / sst,
                          country_party_cells=len(set(pp)), countries=len(set(cc)))

# ------------------------------------------------------------------ helpers
def cluster_se(x, y, groups, add_const=True):
    """OLS slope of y on x with a cluster robust (CR0) standard error."""
    X = np.column_stack([np.ones(len(x)), x]) if add_const else x.reshape(-1, 1)
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ (X.T @ y)
    u = y - X @ b
    gidx = defaultdict(list)
    for i, g in enumerate(groups): gidx[g].append(i)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for ix in gidx.values():
        ix = np.asarray(ix)
        s = X[ix].T @ u[ix]
        meat += np.outer(s, s)
    G = len(gidx); n = len(y); k = X.shape[1]
    adj = (G / max(G - 1, 1)) * ((n - 1) / max(n - k, 1))
    V = XtX_inv @ (adj * meat) @ XtX_inv
    slope = float(b[-1]); se = float(np.sqrt(max(V[-1, -1], 0)))
    tstat = slope / se if se > 0 else float("nan")
    p = 2 * stats.t.sf(abs(tstat), max(G - 1, 1))
    return slope, se, tstat, float(p), G

def demean(values, groups):
    g = defaultdict(list)
    for i, k in enumerate(groups): g[k].append(i)
    out = np.array(values, float).copy()
    for ix in g.values():
        ix = np.asarray(ix); out[ix] -= out[ix].mean()
    return out

# ------------------------------------------------------------------ 1. replicate the published number
RES["published_replication"] = {}
for name, key in [("matter/manner PC1", "pc1"), ("stance", "stance"), ("affect", "affect")]:
    y = np.array([r[key] for r in use], float)
    r_, p_ = stats.pearsonr(lrv, y)
    log(f"POOLED (as published, speech level, no country control): corr(lr, {name}) = {r_:+.4f} p={p_:.3g} n={len(y)}")
    RES["published_replication"][key] = dict(r=float(r_), p=float(p_), n=int(len(y)))

# ------------------------------------------------------------------ 2. speaker level records (person unit)
key = defaultdict(list)
for i, r in enumerate(use): key[(r["speaker"], r["country"], r["party"])].append(i)
sp_country, sp_party, sp_lr, sp_n = [], [], [], []
sp_y = {k: [] for k in ("pc1", "stance", "affect")}
within_ss = {k: 0.0 for k in sp_y}; within_df = 0
for (s, c, pa), ix in key.items():
    sp_country.append(c); sp_party.append(c + "|" + pa); sp_lr.append(use[ix[0]]["lr"]); sp_n.append(len(ix))
    for k in sp_y:
        v = np.array([use[i][k] for i in ix], float)
        sp_y[k].append(float(v.mean()))
        if len(v) >= 2: within_ss[k] += float(((v - v.mean()) ** 2).sum())
    if len(ix) >= 2: within_df += len(ix) - 1
sp_country = np.array(sp_country, dtype=object); sp_party = np.array(sp_party, dtype=object)
sp_lr = np.array(sp_lr, float); sp_n = np.array(sp_n, int)
for k in sp_y: sp_y[k] = np.array(sp_y[k], float)
log(f"speaker records={len(sp_lr):,}  countries={len(set(sp_country))}  parties={len(set(sp_party))}  "
    f"repeat speech df for the reliability estimate={within_df:,}")
RES["speaker_records"] = dict(n=int(len(sp_lr)), countries=len(set(sp_country)),
                              country_party=len(set(sp_party)), within_df=int(within_df))

# ------------------------------------------------------------------ 3. reliability, MEASURED
# sigma2_e = mean square of a single speech about its speaker's own mean.
# reliability of the speaker mean lambda = sigma2_true / (sigma2_true + sigma2_e / nbar)
REL = {}
for k in sp_y:
    if within_df < 20: REL[k] = None; continue
    s2e = within_ss[k] / within_df
    total = float(sp_y[k].var(ddof=1))
    nbar = float(np.mean(sp_n))
    s2true = max(total - s2e / nbar, 1e-12)
    lam = s2true / (s2true + s2e / nbar)
    REL[k] = dict(sigma2_within_speech=s2e, var_speaker_mean=total, nbar=nbar,
                  sigma2_true=s2true, reliability=float(lam))
    log(f"reliability of the speaker mean, {k}: lambda={lam:.3f} "
        f"(single speech noise {s2e:.4f}, speaker mean variance {total:.4f}, mean speeches per speaker {nbar:.2f})")
RES["reliability"] = REL

# ------------------------------------------------------------------ 4. BETWEEN room vs WITHIN room
RES["between_within"] = {}
for k in sp_y:
    y = sp_y[k]
    # BETWEEN: one point per country, its mean lr against its mean outcome
    g = defaultdict(list)
    for i, c in enumerate(sp_country): g[c].append(i)
    bx, by, bw = [], [], []
    for c, ix in g.items():
        ix = np.asarray(ix)
        bx.append(sp_lr[ix].mean()); by.append(y[ix].mean()); bw.append(len(ix))
    bx = np.array(bx); by = np.array(by); bw = np.array(bw, float)
    sl_b, ic_b, r_b, p_b, se_b = stats.linregress(bx, by)
    # standardised slope so between and within are on one scale
    zb = sl_b * bx.std(ddof=1) / (by.std(ddof=1) + 1e-12)

    # WITHIN: country demeaned, speaker level, clustered three ways
    xw = demean(sp_lr, sp_country); yw = demean(y, sp_country)
    sd_x = xw.std(ddof=1) + 1e-12; sd_y = yw.std(ddof=1) + 1e-12
    sl_naive, se_n, t_n, p_n, _ = cluster_se(xw, yw, np.arange(len(xw)))
    sl_pty, se_p, t_p, p_p, G_p = cluster_se(xw, yw, sp_party)
    sl_cty, se_c, t_c, p_c, G_c = cluster_se(xw, yw, sp_country)
    zw = sl_pty * sd_x / sd_y
    r_w = float(np.corrcoef(xw, yw)[0, 1])

    lam = REL[k]["reliability"] if REL.get(k) else float("nan")
    r_w_corr = r_w / math.sqrt(lam) if lam == lam and lam > 0 else float("nan")

    log(f"\n--- {k} ---")
    log(f"  BETWEEN room (26 countries): slope={sl_b:+.4f} r={r_b:+.3f} p={p_b:.3g}  standardised={zb:+.4f}")
    log(f"  WITHIN  room (country demeaned, {len(xw)} speakers): slope={sl_pty:+.4f} standardised={zw:+.4f} r={r_w:+.4f}")
    log(f"     SE by speaker (naive)      : {se_n:.4f}  t={t_n:+.2f} p={p_n:.3g}")
    log(f"     SE clustered on party      : {se_p:.4f}  t={t_p:+.2f} p={p_p:.3g}  ({G_p} clusters)")
    log(f"     SE clustered on country    : {se_c:.4f}  t={t_c:+.2f} p={p_c:.3g}  ({G_c} clusters)")
    log(f"     within r corrected for measurement noise (lambda={lam:.3f}) = {r_w_corr:+.4f}")
    log(f"  BETWEEN / WITHIN standardised ratio = "
        f"{(zb/zw if abs(zw)>1e-9 else float('inf')):+.2f}")
    RES["between_within"][k] = dict(
        between=dict(slope=float(sl_b), r=float(r_b), p=float(p_b), std_slope=float(zb), n_rooms=int(len(bx))),
        within=dict(slope=float(sl_pty), std_slope=float(zw), r=float(r_w), r_corrected=float(r_w_corr),
                    se_naive=float(se_n), p_naive=float(p_n),
                    se_party=float(se_p), p_party=float(p_p), n_party_clusters=int(G_p),
                    se_country=float(se_c), p_country=float(p_c), n_country_clusters=int(G_c),
                    n=int(len(xw))),
        ratio_between_over_within=float(zb / zw) if abs(zw) > 1e-9 else None)

# ------------------------------------------------------------------ 5. wild cluster bootstrap for the within slope
# H0: within room slope = 0. Restricted residuals, Rademacher weights drawn ONCE PER COUNTRY, so
# each room keeps its own lr design and its own residual scale. This is the null the production
# side test used; a record permutation null would blame rooms with a narrow lr spread.
log("\nwild cluster bootstrap (Rademacher, weights per country, restricted null) ...")
RES["wild_bootstrap"] = {}
for k in sp_y:
    y = sp_y[k]
    xw = demean(sp_lr, sp_country); yw = demean(y, sp_country)
    sl_obs, se_obs, t_obs, _, _ = cluster_se(xw, yw, sp_country)
    # restricted fit: slope forced to 0, so residual = yw itself (yw already country demeaned)
    u0 = yw.copy()
    countries = sorted(set(sp_country))
    cidx = {c: np.flatnonzero(sp_country == c) for c in countries}
    tb = np.empty(NBOOT)
    for b in range(NBOOT):
        w = rng.choice([-1.0, 1.0], size=len(countries))
        ystar = np.empty_like(yw)
        for wi, c in zip(w, countries): ystar[cidx[c]] = u0[cidx[c]] * wi
        ystar = demean(ystar, sp_country)
        s, se, t, _, _ = cluster_se(xw, ystar, sp_country)
        tb[b] = t
    p_wild = float((np.sum(np.abs(tb) >= abs(t_obs)) + 1) / (NBOOT + 1))
    log(f"  {k}: observed within t (country clustered) = {t_obs:+.2f}   wild bootstrap p = {p_wild:.4f}")
    RES["wild_bootstrap"][k] = dict(t_obs=float(t_obs), p=p_wild, nboot=NBOOT)

# ------------------------------------------------------------------ 6. pair differencing, with the curvature trap
# Inside a country, take ordered pairs of speakers. dC = w dP with no intercept under the claim.
# Curvature control: the antisymmetric term dP x (mean lr of the pair, centred on the room mean).
# If g is curved, a per room LINEAR w differs between rooms with different lr RANGES with no true
# modulation at all, so this term must be fitted before any modulation is claimed.
log("\npair differencing inside each country (both orderings kept, no intercept) ...")
room_members = defaultdict(list)
for i, c in enumerate(sp_country): room_members[c].append(i)
lr_roommean = np.zeros(len(sp_lr))
for c, ix in room_members.items():
    ix = np.asarray(ix); lr_roommean[ix] = sp_lr[ix].mean()

A, B, RM = [], [], []
for c, mem in room_members.items():
    mem = np.asarray(mem)
    m = len(mem)
    if m < 2: continue
    ii, jj = np.triu_indices(m, 1)
    if len(ii) > PAIRCAP:
        pick = rng.choice(len(ii), PAIRCAP, replace=False); ii, jj = ii[pick], jj[pick]
    a, b = mem[ii], mem[jj]
    A.append(np.concatenate([a, b])); B.append(np.concatenate([b, a]))
    RM.append(np.repeat(c, 2 * len(a)))
A = np.concatenate(A); B = np.concatenate(B); RM = np.concatenate(RM)
dP = sp_lr[A] - sp_lr[B]
Pbar = (sp_lr[A] + sp_lr[B]) / 2.0 - lr_roommean[A]
log(f"  ordered pairs={len(dP):,} across {len(set(RM))} countries (cap {PAIRCAP} unordered per country)")
RES["pairs"] = dict(ordered=int(len(dP)), rooms=int(len(set(RM))), cap=PAIRCAP)
RES["pair_fit"] = {}
for k in sp_y:
    y = sp_y[k]; dC = y[A] - y[B]
    X1 = dP.reshape(-1, 1)
    w1 = float(np.linalg.lstsq(X1, dC, rcond=None)[0][0])
    r1 = dC - X1 @ np.array([w1])
    X2 = np.column_stack([dP, dP * Pbar])
    w2 = np.linalg.lstsq(X2, dC, rcond=None)[0]
    r2 = dC - X2 @ w2
    # cluster bootstrap over countries for both
    cs = sorted(set(RM)); ridx = {c: np.flatnonzero(RM == c) for c in cs}
    b1, b2 = [], []
    for _ in range(400):
        pick = rng.integers(0, len(cs), len(cs))
        ix = np.concatenate([ridx[cs[j]] for j in pick])
        b1.append(float(np.linalg.lstsq(dP[ix].reshape(-1, 1), dC[ix], rcond=None)[0][0]))
        b2.append(np.linalg.lstsq(np.column_stack([dP[ix], dP[ix] * Pbar[ix]]), dC[ix], rcond=None)[0])
    b1 = np.array(b1); b2 = np.array(b2)
    r2_lin = 1 - float((r1 ** 2).sum() / (dC ** 2).sum())
    r2_curv = 1 - float((r2 ** 2).sum() / (dC ** 2).sum())
    log(f"  {k}: linear w={w1:+.4f} (se {b1.std(ddof=1):.4f})   "
        f"with curvature w={w2[0]:+.4f} (se {b2[:,0].std(ddof=1):.4f}), curvature term={w2[1]:+.4f} "
        f"(se {b2[:,1].std(ddof=1):.4f})   R2 {r2_lin:.5f} -> {r2_curv:.5f}")
    RES["pair_fit"][k] = dict(w_linear=w1, se_linear=float(b1.std(ddof=1)),
                              w_curv=float(w2[0]), se_w_curv=float(b2[:, 0].std(ddof=1)),
                              curvature=float(w2[1]), se_curvature=float(b2[:, 1].std(ddof=1)),
                              r2_linear=r2_lin, r2_curv=r2_curv)

# ------------------------------------------------------------------ 7. does the WHO slope itself differ by room?
# The effect side analogue of the production side rotation test: is the lr -> character slope a
# constant, or does it turn from country to country? Null = wild bootstrap fixing each country's
# own lr design and residual scale, so a narrow lr spread cannot pose as real heterogeneity.
log("\nper country WHO slope heterogeneity against a wild bootstrap null ...")
RES["slope_heterogeneity"] = {}
MINSPK = 8
for k in sp_y:
    y = sp_y[k]
    slopes, cs = [], []
    for c, ix in room_members.items():
        ix = np.asarray(ix)
        if len(ix) < MINSPK: continue
        x = sp_lr[ix]
        if x.std() < 1e-9: continue
        sl = np.polyfit(x, y[ix], 1)[0]
        slopes.append(sl); cs.append(c)
    if len(slopes) < 6:
        RES["slope_heterogeneity"][k] = None; continue
    slopes = np.array(slopes)
    obs_sd = float(slopes.std(ddof=1))
    # pooled within slope as the null truth
    xw = demean(sp_lr, sp_country); yw = demean(y, sp_country)
    w0 = float(np.polyfit(xw, yw, 1)[0])
    nullsd = []
    for _ in range(600):
        sl2 = []
        for c in cs:
            ix = np.asarray(room_members[c]); x = sp_lr[ix]
            fit = w0 * (x - x.mean())
            resid = (y[ix] - y[ix].mean()) - fit
            ystar = fit + resid * rng.choice([-1.0, 1.0], size=len(ix))
            sl2.append(np.polyfit(x, ystar, 1)[0])
        nullsd.append(np.std(sl2, ddof=1))
    nullsd = np.array(nullsd)
    p = float((np.sum(nullsd >= obs_sd) + 1) / (len(nullsd) + 1))
    log(f"  {k}: {len(slopes)} countries with >={MINSPK} speakers, observed slope sd={obs_sd:.4f} "
        f"vs wild bootstrap null {nullsd.mean():.4f} (95th {np.percentile(nullsd,95):.4f})  p={p:.4f}")
    RES["slope_heterogeneity"][k] = dict(n_rooms=int(len(slopes)), obs_sd=obs_sd,
                                         null_mean=float(nullsd.mean()),
                                         null_p95=float(np.percentile(nullsd, 95)), p=p,
                                         pooled_within_slope=w0)

json.dump(RES, open(OUT, "w"), indent=1)
log(f"\nwrote {OUT}")

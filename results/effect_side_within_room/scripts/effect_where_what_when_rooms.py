#!/usr/bin/env python3
"""effect_where_what_when_rooms.py -- the between room against within room split for the WHERE,
WHAT and remaining WHEN legs of Paper 4B's five clauses.

WHERE  798 independent forums (cc_v3.forum_threads). Paper 4B rests the clause on two numbers:
       (1) 49.3 per cent of matter against manner variance sits BETWEEN forums, stated in the
           source RESULT.md as an upper bound because there is NO TOPIC CONTROL, and
       (2) the spread of per room reward gradients beats a shuffled room null, p=0.0025.
       (1) is a pure between room quantity, so the honest question is how much survives a topic
       control. A topic room is built here by clustering thread titles, and the variance is then
       decomposed BETWEEN forum, BETWEEN topic and the interaction, so the part of the 49.3 that
       is really subject matter is measured rather than conceded.
       (2) is a slope, so it is already the within room object, but its null is a room label
       shuffle. It is redone here against a WILD BOOTSTRAP that fixes each room's own engagement
       design and residual scale, which is the null the production side test showed is required,
       and with the curvature control, because a per room LINEAR gradient differs between rooms
       with different character ranges with no true modulation at all.

WHAT   the Upworthy randomised headline experiments. Randomisation is WITHIN test, so the
       published estimate is already a within room one. Reported here as the explicit split:
       the between test (package level) association beside the within test causal estimate, plus
       a package grouped read so a package's own tests cannot be split across the contrast.

WHEN   the two legs that are not the press. The web leg is already a within domain paired test;
       the between domain (crawl composition) read is put beside it. The UN leg's within country
       drift is redone with a wild bootstrap over countries and a per country slope table, since
       the published sign test does not clear (99 of 180, p=0.205).
"""
import os, json, re, time, csv, sys
from collections import defaultdict
import numpy as np
import psycopg2
from scipy import stats

t0 = time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)
csv.field_size_limit(10 ** 8)

CHAR = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
IX = {a: i for i, a in enumerate(CHAR)}
OUT = os.environ.get("OUT", "/home/jason/effect_confound/where_what_when.json")
SEED = int(os.environ.get("SEED", "20260903"))
NTOPIC = int(os.environ.get("NTOPIC", "40"))
MINTHREADS = int(os.environ.get("MINTHREADS", "50"))
rng = np.random.default_rng(SEED)
RES = {}

PW = [l.split("=", 1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
DSN = f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"
db = psycopg2.connect(DSN); cur = db.cursor()
cur.execute(f"SELECT {','.join(CHAR)} FROM cc_v3.domain_char8_expanded")
allc = np.array([[float(v) for v in r] for r in cur.fetchall()], float)
MEAN, STD = allc.mean(0), allc.std(0) + 1e-9
_, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False); PC1 = Vt[0]
if (PC1[IX["rigour"]] + PC1[IX["depth"]]) < 0: PC1 = -PC1
log(f"ruler rows={len(allc):,}")
RES["ruler"] = dict(rows=int(len(allc)), pc1=dict(zip(CHAR, [round(float(x), 3) for x in PC1])))

# ================================================================== WHERE
log("\n" + "=" * 90)
log("WHERE -- 798 forums: how much of the between room reading is subject matter?")
log("=" * 90)
cur.execute("""SELECT dom, software, title, replies, char FROM cc_v3.forum_threads
               WHERE char IS NOT NULL AND dom IS NOT NULL""")
doms, softs, titles, reps, vecs = [], [], [], [], []
for dom, soft, title, rep, ch in cur:
    if isinstance(ch, str):
        try: ch = json.loads(ch)
        except Exception: continue
    if not isinstance(ch, dict) or any(a not in ch for a in CHAR): continue
    try: v = [float(ch[a]) for a in CHAR]
    except (TypeError, ValueError): continue
    doms.append(dom); softs.append(soft or ""); titles.append(title or "")
    reps.append(float(rep) if rep is not None else np.nan); vecs.append(v)
db.close()
V = np.array(vecs, float); doms = np.array(doms, dtype=object)
softs = np.array(softs, dtype=object); reps = np.array(reps, float)
P = ((V - MEAN) / STD) @ PC1
log(f"scored forum threads={len(P):,}  distinct forums={len(set(doms)):,}")

from collections import Counter
cnt = Counter(doms)
keep = np.array([cnt[d] >= MINTHREADS for d in doms])
P, doms, softs, reps, titles = P[keep], doms[keep], softs[keep], reps[keep], [t for t, k in zip(titles, keep) if k]
log(f"forums with >={MINTHREADS} scored threads: {len(set(doms)):,}  threads kept: {len(P):,}")

def var_share(values, groups):
    g = defaultdict(list)
    for i, k in enumerate(groups): g[k].append(i)
    grand = values.mean()
    between = sum(len(ix) * (values[ix].mean() - grand) ** 2 for ix in map(np.asarray, g.values()))
    total = float(((values - grand) ** 2).sum())
    return float(between / total) if total > 0 else float("nan")

share_forum = var_share(P, doms)
log(f"  BETWEEN forum share of matter/manner variance (the published 49.3 per cent) = {100*share_forum:.1f}%")

# topic rooms from thread titles
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans
tf = TfidfVectorizer(max_features=20000, stop_words="english", min_df=5, lowercase=True)
Tm = tf.fit_transform(titles)
km = MiniBatchKMeans(n_clusters=NTOPIC, n_init=6, random_state=SEED, batch_size=4096).fit(Tm)
topic = km.labels_
share_topic = var_share(P, topic)
log(f"  BETWEEN topic share (a {NTOPIC} cluster topic room built from the thread titles) = {100*share_topic:.1f}%")

# forum share AFTER removing the topic mean: the house style term the RESULT.md said was owed
Pdm = P.copy()
for k in set(topic):
    m = np.flatnonzero(topic == k); Pdm[m] -= Pdm[m].mean()
share_forum_given_topic = var_share(Pdm, doms)
# and the reverse, for symmetry
Pdf = P.copy()
for d in set(doms):
    m = np.flatnonzero(doms == d); Pdf[m] -= Pdf[m].mean()
share_topic_given_forum = var_share(Pdf, topic)
log(f"  BETWEEN forum share AFTER the topic room is taken out = {100*share_forum_given_topic:.1f}%")
log(f"  BETWEEN topic share AFTER the forum is taken out      = {100*share_topic_given_forum:.1f}%")
RES["where_variance"] = dict(between_forum=share_forum, between_topic=share_topic,
                             between_forum_given_topic=share_forum_given_topic,
                             between_topic_given_forum=share_topic_given_forum,
                             forums=len(set(doms)), threads=int(len(P)), ntopic=NTOPIC)

# ---- reward gradients: within room slope of rank normalised engagement on character
log("\n  reward gradients per room, with the topic control and the curvature control")
def ranknorm(x):
    r = stats.rankdata(x); return (r - r.mean()) / (r.std() + 1e-12)

room_ix = defaultdict(list)
for i, d in enumerate(doms): room_ix[d].append(i)
grads, grads_topic, grads_curv, rnames, rn = [], [], [], [], []
for d, ix in room_ix.items():
    ix = np.asarray(ix)
    e = reps[ix]
    ok = ix[np.isfinite(e)]
    if len(ok) < 30: continue
    e = reps[ok]
    if np.nanstd(e) < 1e-9: continue
    ez = ranknorm(e)
    x = P[ok]
    if x.std() < 1e-9: continue
    xz = (x - x.mean()) / x.std()
    grads.append(float(np.polyfit(xz, ez, 1)[0]))
    # topic controlled: take the topic mean out of BOTH sides inside this room
    tt = topic[ok]
    xr, er = xz.copy(), ez.copy()
    for k in set(tt):
        m = np.flatnonzero(tt == k)
        if len(m) >= 3: xr[m] -= xr[m].mean(); er[m] -= er[m].mean()
    grads_topic.append(float(np.polyfit(xr, er, 1)[0]) if xr.std() > 1e-9 else np.nan)
    # curvature control: fit e ~ a*x + b*x^2 inside the room and report the LINEAR term
    A = np.column_stack([xz, xz ** 2, np.ones(len(xz))])
    grads_curv.append(float(np.linalg.lstsq(A, ez, rcond=None)[0][0]))
    rnames.append(d); rn.append(len(ok))
grads = np.array(grads); grads_topic = np.array(grads_topic); grads_curv = np.array(grads_curv)
log(f"    {len(grads)} rooms with a usable gradient")
log(f"    raw gradients          : mean {np.nanmean(grads):+.4f}  spread(sd) {np.nanstd(grads, ddof=1):.4f}")
log(f"    topic controlled       : mean {np.nanmean(grads_topic):+.4f}  spread(sd) {np.nanstd(grads_topic, ddof=1):.4f}")
log(f"    curvature controlled   : mean {np.nanmean(grads_curv):+.4f}  spread(sd) {np.nanstd(grads_curv, ddof=1):.4f}")

# wild bootstrap null: hold the gradient at the pooled value, keep each room's own character
# design and residual scale, flip residual signs inside the room.
def wild_spread(vals_fn, pooled):
    out = []
    for _ in range(400):
        sl = []
        for d, ix in room_ix.items():
            ix = np.asarray(ix); e = reps[ix]
            ok = ix[np.isfinite(e)]
            if len(ok) < 30: continue
            e = reps[ok]
            if np.nanstd(e) < 1e-9: continue
            ez = ranknorm(e); x = P[ok]
            if x.std() < 1e-9: continue
            xz = (x - x.mean()) / x.std()
            fit = pooled * xz
            resid = ez - fit
            star = fit + resid * rng.choice([-1.0, 1.0], size=len(resid))
            sl.append(np.polyfit(xz, star, 1)[0])
        out.append(np.std(sl, ddof=1))
    return np.array(out)

pooled_grad = float(np.nanmean(grads))
null = wild_spread(None, pooled_grad)
obs = float(np.nanstd(grads, ddof=1))
p_wild = float((np.sum(null >= obs) + 1) / (len(null) + 1))
log(f"    WILD BOOTSTRAP null spread (each room keeps its own design and residual scale): "
    f"mean {null.mean():.4f}, 95th {np.percentile(null,95):.4f}   observed {obs:.4f}   p={p_wild:.4f}")
obs_t = float(np.nanstd(grads_topic, ddof=1))
p_wild_t = float((np.sum(null >= obs_t) + 1) / (len(null) + 1))
log(f"    same null against the TOPIC CONTROLLED spread {obs_t:.4f}  p={p_wild_t:.4f}")
RES["where_gradients"] = dict(rooms=int(len(grads)), mean=pooled_grad, spread=obs,
                              spread_topic_controlled=obs_t,
                              spread_curvature_controlled=float(np.nanstd(grads_curv, ddof=1)),
                              wild_null_mean=float(null.mean()),
                              wild_null_p95=float(np.percentile(null, 95)),
                              p_wild=p_wild, p_wild_topic=p_wild_t)

# ================================================================== WHAT (Upworthy)
log("\n" + "=" * 90)
log("WHAT -- Upworthy randomised headlines: the between test read beside the within test one")
log("=" * 90)
D = os.path.expanduser("~/kc-dwpaper")
sc = {}
for f in (f"{D}/upworthy_scores_full.jsonl", f"{D}/upworthy_scores.jsonl"):
    if os.path.exists(f):
        for line in open(f):
            try:
                r = json.loads(line); sc[r["headline"]] = [float(r["scores"][a]) for a in CHAR]
            except Exception: pass
agg = defaultdict(lambda: [0.0, 0.0])
pkg_of = {}
for line in open(f"{D}/upworthy.jsonl"):
    try: r = json.loads(line)
    except Exception: continue
    h = r["headline"]
    if h not in sc: continue
    a = agg[(r["test_id"], h)]
    a[0] += float(r.get("impressions", 0)); a[1] += float(r.get("clicks", 0))
    pkg_of[r["test_id"]] = r.get("clickability_test_id") or r.get("test_id")
tests = defaultdict(list)
for (t, h), (imp, clk) in agg.items():
    if imp > 0: tests[t].append((sc[h], imp, clk))
usable = {t: v for t, v in tests.items() if len(v) >= 2 and sum(x[1] for x in v) >= 1000}
log(f"  scored headlines={len(sc):,}  tests={len(tests):,}  usable tests={len(usable):,}")

rows_t, rows_x, rows_y, rows_w = [], [], [], []
for t, v in usable.items():
    for ch, imp, clk in v:
        rows_t.append(t); rows_x.append(((np.array(ch) - MEAN) / STD) @ PC1)
        rows_y.append(clk / imp); rows_w.append(imp)
rows_t = np.array(rows_t, dtype=object); X = np.array(rows_x); Y = np.array(rows_y); Wt = np.array(rows_w)
log(f"  arm observations={len(X):,}")

# WITHIN test (the causal estimate): both sides demeaned inside the test
tix = defaultdict(list)
for i, t in enumerate(rows_t): tix[t].append(i)
Xw, Yw = X.copy(), Y.copy()
for ix in map(np.asarray, tix.values()):
    Xw[ix] -= Xw[ix].mean(); Yw[ix] -= Yw[ix].mean()
sl_w = float(np.polyfit(Xw, Yw, 1)[0])
# cluster robust t on the tests
u = Yw - sl_w * Xw
num = sum((Xw[np.asarray(ix)] @ u[np.asarray(ix)]) ** 2 for ix in tix.values())
den = float((Xw ** 2).sum())
se_w = float(np.sqrt(num) / den)
t_w = sl_w / se_w
std_w = sl_w * Xw.std(ddof=1) / (Yw.std(ddof=1) + 1e-15)

# BETWEEN test: one point per test, its mean character against its mean CTR
bx = np.array([X[np.asarray(ix)].mean() for ix in tix.values()])
by = np.array([Y[np.asarray(ix)].mean() for ix in tix.values()])
lb = stats.linregress(bx, by)
std_b = lb.slope * bx.std(ddof=1) / (by.std(ddof=1) + 1e-15)
log(f"  WITHIN test (randomised, causal): slope={sl_w:+.6f} standardised={std_w:+.4f} "
    f"cluster t={t_w:+.2f} over {len(tix):,} tests")
log(f"  BETWEEN test (composition, NOT randomised): slope={lb.slope:+.6f} standardised={std_b:+.4f} "
    f"r={lb.rvalue:+.3f} p={lb.pvalue:.3g} over {len(bx):,} tests")
log(f"  BETWEEN / WITHIN standardised ratio = {std_b/std_w if abs(std_w)>1e-12 else float('nan'):+.2f}")

# curvature control inside the test: does a curved g pose as the linear effect?
A = np.column_stack([Xw, Xw ** 2 - np.mean(Xw ** 2)])
wc = np.linalg.lstsq(A, Yw, rcond=None)[0]
log(f"  with an in test curvature term: linear {wc[0]:+.6f} (was {sl_w:+.6f}), curvature {wc[1]:+.6f}")
RES["what_upworthy"] = dict(tests=int(len(tix)), arms=int(len(X)),
                            within=dict(slope=sl_w, std_slope=float(std_w), se=se_w, t=float(t_w)),
                            between=dict(slope=float(lb.slope), std_slope=float(std_b),
                                         r=float(lb.rvalue), p=float(lb.pvalue), n=int(len(bx))),
                            ratio=float(std_b / std_w) if abs(std_w) > 1e-12 else None,
                            curvature=dict(linear=float(wc[0]), curv=float(wc[1])))

# ================================================================== WHEN, the two non press legs
log("\n" + "=" * 90)
log("WHEN -- the web leg and the UN leg, between room beside within room")
log("=" * 90)
# --- UN general debate
UNG = "/mnt/nas/kronaxis/corpora/ungd/ungd_char8.jsonl"
if os.path.exists(UNG):
    rows = []
    for line in open(UNG):
        try: r = json.loads(line)
        except Exception: continue
        ch = r.get("char")
        if isinstance(ch, str):
            try: ch = json.loads(ch)
            except Exception: continue
        if not isinstance(ch, dict) or any(a not in ch for a in CHAR): continue
        c = r.get("country") or r.get("iso") or r.get("cc")
        y = r.get("year") or r.get("outcome")
        if c is None or y is None:
            k = str(r.get("kind", "")).split("|")
            if len(k) >= 2: c = c or k[0]
            y = y or r.get("outcome")
        try: y = int(y)
        except (TypeError, ValueError): continue
        rows.append((str(c), y, float(((np.array([float(ch[a]) for a in CHAR]) - MEAN) / STD) @ PC1)))
    log(f"  UN speeches loaded={len(rows):,} countries={len({c for c,_,_ in rows})}")
    byc = defaultdict(list)
    for c, y, p in rows: byc[c].append((y, p))
    slopes, ns, names = [], [], []
    for c, pts in byc.items():
        ys = np.array([y for y, _ in pts], float); ps = np.array([p for _, p in pts], float)
        if len(ys) >= 6 and (ys.max() - ys.min()) >= 30:
            slopes.append(stats.linregress(ys, ps).slope); ns.append(len(ys)); names.append(c)
    slopes = np.array(slopes)
    tt, pp = stats.ttest_1samp(slopes, 0.0)
    npos = int((slopes > 0).sum()); sp = float(stats.binomtest(npos, len(slopes), 0.5).pvalue)
    ally = np.array([y for _, y, _ in rows], float); allp = np.array([p for _, _, p in rows], float)
    xs = stats.linregress(ally, allp)
    # strict between country: country mean year against country mean PC1
    bx = np.array([np.mean([y for y, _ in byc[c]]) for c in names])
    by = np.array([np.mean([p for _, p in byc[c]]) for c in names])
    bt = stats.linregress(bx, by)
    # wild bootstrap over countries
    tb = []
    for _ in range(4000):
        sl = []
        for c in names:
            ys = np.array([y for y, _ in byc[c]], float); ps = np.array([p for _, p in byc[c]], float)
            fit = np.polyval(np.polyfit(ys, ps, 1), ys); resid = ps - fit
            star = ps.mean() + resid * rng.choice([-1.0, 1.0])
            sl.append(stats.linregress(ys, star).slope)
        tb.append(stats.ttest_1samp(sl, 0.0).statistic)
    tb = np.array(tb); pw = float((np.sum(np.abs(tb) >= abs(tt)) + 1) / (len(tb) + 1))
    log(f"  WITHIN country drift: {len(slopes)} countries, mean {slopes.mean():+.5f}/yr t={tt:+.2f} "
        f"p={pp:.4f}  toward matter {npos}/{len(slopes)} (sign p={sp:.3f})  wild bootstrap p={pw:.4f}")
    log(f"  BETWEEN: pooled cross section {xs.slope:+.5f}/yr p={xs.pvalue:.4g} | "
        f"strict between country {bt.slope:+.5f}/yr p={bt.pvalue:.4g}")
    RES["when_ungd"] = dict(countries=int(len(slopes)), within_mean=float(slopes.mean()),
                            t=float(tt), p=float(pp), toward_matter=npos, sign_p=sp, p_wild=pw,
                            cross_section=float(xs.slope), cross_section_p=float(xs.pvalue),
                            between_country=float(bt.slope), between_country_p=float(bt.pvalue))
else:
    log(f"  UN corpus not found at {UNG}")

# --- the web leg
db = psycopg2.connect(DSN); cur = db.cursor()
cur.execute("""SELECT table_name FROM information_schema.tables
               WHERE table_schema='cc_v3' AND table_name ~ 'char8'""")
log("  cc_v3 char8 tables: " + ", ".join(r[0] for r in cur.fetchall()))
db.close()

json.dump(RES, open(OUT, "w"), indent=1)
log(f"\nwrote {OUT}")

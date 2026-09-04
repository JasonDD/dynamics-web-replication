#!/usr/bin/env python3
"""effect_when_press_ruler.py -- resolve the three way disagreement in the WHEN clause's press leg.

Paper 4B says the temporal term is read "in the web, in the deep history of the periodical press,
and in diplomacy, all three pointing the same way" (toward matter). The multiplicity audit (memo
#20174) found the press leg does not say that, and that the three press artefacts disagree with
EACH OTHER on the same sixteen English titles:

  results/within_source_proof.txt           636 issues, 17 titles: mean -0.0237/yr p=0.0122,  5/17 toward matter
  results/within_source_articles_proof.txt  454 issues, 16 titles: mean -0.0236/yr p=0.0133,  1/16 toward matter
  results/historical_press_drift/RESULT.md  454 issues, 16 titles: mean -0.0062/yr p=0.18,    6/16 toward matter

The last two run on the SAME held file. The RESULT.md attributes the gap to "a ruler standardised
on the English archive alone", which is not what the earlier script does. This settles it by
recomputing every ruler on one set of rows.

A ruler here has TWO parts and the two artefacts differ in BOTH:
  AXIS SET       -- cc_within_source_analyse.py projects all eight axes on the web PC1;
                    analyse_press_drift.py uses a five axis hand contrast,
                    M = (rigour+depth)_z - (affect+stance+register)_z.
  STANDARDISATION-- the first standardises on the 2.65M domain web corpus; the second on the
                    1,717 issue EN+FR+NO press corpus itself.
Crossing the two gives a 2x2 that says which half of the ruler moves the answer, plus the EN only
standardisation the RESULT.md claims was used.

Then the honest WHEN read: the within title design IS the within room design, so this doubles as
the WHEN clause's composition test. Between title (archive wide cross section) is reported beside
within title for every ruler, and the per title slopes are put against a wild bootstrap null that
fixes each title's own year design and residual scale.
"""
import os, json, time
from collections import defaultdict
import numpy as np
import psycopg2
from scipy import stats

t0 = time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

CHAR = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
IX = {a: i for i, a in enumerate(CHAR)}
EN_PATH = "the internal corpus store/histchar/within_source_articles_only.jsonl"
EN_ALL = "the internal corpus store/histchar/within_source_curated.jsonl"
PRESS = "the internal corpus store/results/historical_press_drift/scored.jsonl"
OUT = os.environ.get("OUT", "/home/jason/effect_confound/when_press_ruler.json")
SEED = int(os.environ.get("SEED", "20260903"))
rng = np.random.default_rng(SEED)
RES = {}

def as_vec(ch):
    if isinstance(ch, str):
        ch = json.loads(ch.replace("'", '"'))
    if not isinstance(ch, dict) or any(a not in ch for a in CHAR): return None
    try: return np.array([float(ch[a]) for a in CHAR], float)
    except (TypeError, ValueError): return None

# ------------------------------------------------------------------ rows
en_art, en_all, press = [], [], []
for line in open(EN_PATH):
    try: r = json.loads(line)
    except Exception: continue
    v = as_vec(r.get("char"))
    if v is None: continue
    en_art.append(dict(country="EN", title=r["series"], year=int(r["year"]), vec=v))
for line in open(EN_ALL):
    try: r = json.loads(line)
    except Exception: continue
    v = as_vec(r.get("char"))
    if v is None: continue
    en_all.append(dict(country="EN", title=r["series"], year=int(r["year"]), vec=v))
for line in open(PRESS):
    try: r = json.loads(line)
    except Exception: continue
    v = as_vec(r.get("char"))
    if v is None: continue
    p = r["kind"].split("|")
    press.append(dict(country=p[0], title=p[1], year=int(r["outcome"]), vec=v))
log(f"EN articles only={len(en_art)} ({len({r['title'] for r in en_art})} titles)   "
    f"EN all issue types={len(en_all)} ({len({r['title'] for r in en_all})} titles)   "
    f"FR+NO fresh={len(press)}")
RES["rows"] = dict(en_articles=len(en_art), en_all=len(en_all), fr_no=len(press),
                   en_articles_titles=len({r["title"] for r in en_art}),
                   en_all_titles=len({r["title"] for r in en_all}))

# ------------------------------------------------------------------ the standardisation bases
PW = [l.split("=", 1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
db = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs")
cur = db.cursor()
log("pulling the web character corpus for the web standardisation and the web PC1 ...")
cur.execute(f"SELECT {','.join(CHAR)} FROM the internal reference table")
allc = np.array([[float(v) for v in r] for r in cur.fetchall()], float)
db.close()
WEB_MEAN, WEB_STD = allc.mean(0), allc.std(0) + 1e-9
_, _, Vt = np.linalg.svd((allc - WEB_MEAN) / WEB_STD, full_matrices=False)
WEB_PC1 = Vt[0]
if (WEB_PC1[IX["rigour"]] + WEB_PC1[IX["depth"]]) < 0: WEB_PC1 = -WEB_PC1
log(f"web corpus rows={len(allc):,}  PC1: " + ", ".join(f"{a}={l:+.2f}" for a, l in zip(CHAR, WEB_PC1)))

press_pool = np.array([r["vec"] for r in (en_art + press)], float)
PRESS_MEAN, PRESS_STD = press_pool.mean(0), press_pool.std(0) + 1e-9
en_pool = np.array([r["vec"] for r in en_art], float)
EN_MEAN, EN_STD = en_pool.mean(0), en_pool.std(0) + 1e-9
log(f"press pooled standardisation base = {len(press_pool)} issues (EN articles + FR + NO); "
    f"EN only base = {len(en_pool)} issues")

# the five axis hand contrast used by analyse_press_drift.py
HAND = np.zeros(8)
HAND[IX["rigour"]] = 1; HAND[IX["depth"]] = 1
HAND[IX["affect"]] = -1; HAND[IX["stance"]] = -1; HAND[IX["register"]] = -1

RULERS = {
    "R1_webPC1_webZ":     ("web PC1 weights, web standardisation  (cc_within_source_analyse.py, the series ruler)", WEB_PC1, WEB_MEAN, WEB_STD),
    "R2_handM_pressZ":    ("five axis hand contrast, press pooled standardisation  (analyse_press_drift.py)",       HAND,    PRESS_MEAN, PRESS_STD),
    "R3_handM_webZ":      ("five axis hand contrast, web standardisation  (isolates the standardisation base)",     HAND,    WEB_MEAN, WEB_STD),
    "R4_webPC1_pressZ":   ("web PC1 weights, press pooled standardisation  (isolates the axis set)",                WEB_PC1, PRESS_MEAN, PRESS_STD),
    "R5_handM_enZ":       ("five axis hand contrast, ENGLISH ONLY standardisation  (what the RESULT.md claims)",     HAND,    EN_MEAN, EN_STD),
    "R6_webPC1_enZ":      ("web PC1 weights, ENGLISH ONLY standardisation",                                          WEB_PC1, EN_MEAN, EN_STD),
}

def project(recs, w, mean, sd):
    V = np.array([r["vec"] for r in recs], float)
    return ((V - mean) / sd) @ w

# ------------------------------------------------------------------ within title vs between title
def within_between(recs, vals, min_iss, min_span, label):
    byt = defaultdict(list)
    for r, v in zip(recs, vals): byt[r["title"]].append((r["year"], v))
    slopes, names, ns = [], [], []
    for t, pts in byt.items():
        ys = np.array([y for y, _ in pts], float); ms = np.array([m for _, m in pts], float)
        if len(ys) < min_iss or (ys.max() - ys.min()) < min_span: continue
        sl = stats.linregress(ys, ms).slope
        slopes.append(sl); names.append(t); ns.append(len(ys))
    slopes = np.array(slopes)
    if len(slopes) < 3: return None
    tt, pp = stats.ttest_1samp(slopes, 0.0)
    npos = int((slopes > 0).sum())
    sign_p = float(stats.binomtest(npos, len(slopes), 0.5).pvalue)
    # BETWEEN title: the archive wide cross section, which is the composition read
    ally = np.array([r["year"] for r in recs], float); allv = np.array(vals, float)
    xs = stats.linregress(ally, allv)
    # BETWEEN title in the strict sense: title mean value against title mean year
    tm = defaultdict(list)
    for r, v in zip(recs, vals): tm[r["title"]].append((r["year"], v))
    bx = np.array([np.mean([y for y, _ in p]) for p in tm.values()])
    by = np.array([np.mean([m for _, m in p]) for p in tm.values()])
    bt = stats.linregress(bx, by)
    return dict(label=label, n_titles=int(len(slopes)), mean_slope=float(slopes.mean()),
                t=float(tt), p=float(pp), toward_matter=npos, sign_p=sign_p,
                cross_section_slope=float(xs.slope), cross_section_p=float(xs.pvalue),
                between_title_slope=float(bt.slope), between_title_p=float(bt.pvalue),
                per_title=sorted(zip(names, ns, [float(s) for s in slopes]), key=lambda z: z[2]))

RES["rulers"] = {}
log("\n" + "=" * 100)
log("THE SAME 454 ENGLISH ARTICLE ISSUES / 16 TITLES, READ UNDER SIX RULERS")
log("filter: >=6 issues and >=30 year span (the historical_press_drift filter); "
    "the earlier artefacts used >=4 issues and >=40 years, both reported below")
log("=" * 100)
for rk, (desc, w, mean, sd) in RULERS.items():
    vals = project(en_art, w, mean, sd)
    a = within_between(en_art, vals, 6, 30, desc)     # press drift filter
    b = within_between(en_art, vals, 4, 40, desc)     # earlier artefact filter
    log(f"\n{rk}: {desc}")
    if a: log(f"   filter >=6 issues / >=30y : {a['n_titles']:>2} titles  mean {a['mean_slope']:+.4f}/yr  "
              f"t={a['t']:+.2f} p={a['p']:.4f}  toward matter {a['toward_matter']}/{a['n_titles']} (sign p={a['sign_p']:.4g})")
    if b: log(f"   filter >=4 issues / >=40y : {b['n_titles']:>2} titles  mean {b['mean_slope']:+.4f}/yr  "
              f"t={b['t']:+.2f} p={b['p']:.4f}  toward matter {b['toward_matter']}/{b['n_titles']} (sign p={b['sign_p']:.4g})")
    if a: log(f"   BETWEEN title (archive cross section) slope {a['cross_section_slope']:+.4f}/yr p={a['cross_section_p']:.4g}   "
              f"| strict between title (title means) {a['between_title_slope']:+.4f}/yr p={a['between_title_p']:.4g}")
    RES["rulers"][rk] = dict(desc=desc, filter_6_30=a, filter_4_40=b)

# the older 636 issue / 17 title file under the series ruler, for the third artefact
vals_all = project(en_all, WEB_PC1, WEB_MEAN, WEB_STD)
c = within_between(en_all, vals_all, 4, 40, "web PC1, web z, ALL issue types (within_source_proof.txt)")
log(f"\nwithin_source_proof.txt reproduction (all issue types, {len(en_all)} issues, filter >=4/>=40y): "
    f"{c['n_titles']} titles mean {c['mean_slope']:+.4f}/yr t={c['t']:+.2f} p={c['p']:.4f} "
    f"toward matter {c['toward_matter']}/{c['n_titles']}")
RES["all_issue_types_seriesruler"] = c

# ------------------------------------------------------------------ how different are the rulers?
log("\ncorrelation between the ruler readings on the same 454 issues:")
proj = {rk: project(en_art, w, m, s) for rk, (d, w, m, s) in RULERS.items()}
keys = list(proj)
RES["ruler_correlations"] = {}
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        r_ = float(np.corrcoef(proj[keys[i]], proj[keys[j]])[0, 1])
        RES["ruler_correlations"][f"{keys[i]}|{keys[j]}"] = r_
        log(f"   {keys[i]:<20} vs {keys[j]:<20} r={r_:+.4f}")

# ------------------------------------------------------------------ wild bootstrap on the per title slopes
# Null: no within title drift. Each title keeps its own year design and residual scale; residual
# signs flipped per title. Tests the mean slope, not a record permutation.
log("\nwild bootstrap for the mean within title slope (per title sign flips, "
    "each title keeps its own year design and residual scale) ...")
RES["wild"] = {}
for rk in ("R1_webPC1_webZ", "R2_handM_pressZ"):
    w, mean, sd = RULERS[rk][1], RULERS[rk][2], RULERS[rk][3]
    vals = project(en_art, w, mean, sd)
    byt = defaultdict(list)
    for r, v in zip(en_art, vals): byt[r["title"]].append((r["year"], v))
    qual = {t: p for t, p in byt.items()
            if len(p) >= 6 and (max(y for y, _ in p) - min(y for y, _ in p)) >= 30}
    obs = np.array([stats.linregress([y for y, _ in p], [m for _, m in p]).slope for p in qual.values()])
    tobs = float(stats.ttest_1samp(obs, 0.0).statistic)
    tb = []
    for _ in range(4000):
        sl = []
        for p in qual.values():
            ys = np.array([y for y, _ in p], float); ms = np.array([m for _, m in p], float)
            fit = np.polyval(np.polyfit(ys, ms, 1), ys)
            resid = ms - fit
            base = ms.mean()                                   # restricted: slope zero
            star = base + resid * rng.choice([-1.0, 1.0])
            sl.append(stats.linregress(ys, star).slope)
        tb.append(stats.ttest_1samp(sl, 0.0).statistic)
    tb = np.array(tb)
    p = float((np.sum(np.abs(tb) >= abs(tobs)) + 1) / (len(tb) + 1))
    log(f"   {rk}: observed t={tobs:+.2f}  wild bootstrap p={p:.4f}  ({len(qual)} titles)")
    RES["wild"][rk] = dict(t=tobs, p=p, n_titles=len(qual))

json.dump(RES, open(OUT, "w"), indent=1)
log(f"\nwrote {OUT}")

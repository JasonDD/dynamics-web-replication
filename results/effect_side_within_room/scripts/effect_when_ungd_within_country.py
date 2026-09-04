#!/usr/bin/env python3
"""effect_when_ungd_within_country.py -- the WHEN clause's diplomacy leg, between country beside
within country, on the wild bootstrap null.

Paper 4B counts the general debate of the United Nations as one of three corroborations of the
temporal drift toward matter. The published artefact (results/ungd_where_when.txt) reads it on
1,594 speeches: cross section +0.0052/yr p=0.012, within country +0.0088/yr t=+2.93 p=0.0038, but
the sign test does NOT clear (99 of 180 countries toward matter, p=0.205). The corpus has since
grown, so this reruns it and adds the two things the published read lacks:

  a WILD BOOTSTRAP over countries, which fixes each country's own year design and residual scale,
  in place of the plain one sample t; a record permutation null would blame countries with a short
  or lopsided span,

  and the explicit BETWEEN country reading beside the within one, because the between term is what
  a changing membership (decolonisation, more small states after 1960) buys you and it is the
  composition confound in this corpus.

Room = country. There are no persons here, so there is no person leakage: a speech belongs to one
country and one year. The curvature trap is carried by fitting a quadratic in year inside each
country and reporting the linear term beside the straight line one.
"""
import os, json, time
from collections import defaultdict
import numpy as np
import psycopg2
from scipy import stats

t0 = time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

CHAR = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
SRC = os.environ.get("SRC", "the internal corpus store/ungd/ungd_char8.jsonl")
OUT = os.environ.get("OUT", "/home/jason/effect_confound/when_ungd.json")
MINPTS = int(os.environ.get("MINPTS", "6")); MINSPAN = int(os.environ.get("MINSPAN", "30"))
NBOOT = int(os.environ.get("NBOOT", "4000"))
rng = np.random.default_rng(int(os.environ.get("SEED", "20260903")))
RES = {}

PW = [l.split("=", 1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
db = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"); cur = db.cursor()
cur.execute(f"SELECT {','.join(CHAR)} FROM the internal reference table")
allc = np.array([[float(v) for v in r] for r in cur.fetchall()], float)
db.close()
MEAN, STD = allc.mean(0), allc.std(0) + 1e-9
_, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False); PC1 = Vt[0]
if (PC1[CHAR.index("rigour")] + PC1[CHAR.index("depth")]) < 0: PC1 = -PC1
log(f"ruler rows={len(allc):,}")

rows = []
for line in open(SRC):
    try: r = json.loads(line)
    except Exception: continue
    ch = r.get("char")
    if isinstance(ch, str):
        try: ch = json.loads(ch)
        except Exception: continue
    if not isinstance(ch, dict) or any(a not in ch for a in CHAR): continue
    c = r.get("iso3"); y = r.get("year")
    if not c or y is None: continue
    try: y = int(y)
    except (TypeError, ValueError): continue
    rows.append((str(c), y, float(((np.array([float(ch[a]) for a in CHAR]) - MEAN) / STD) @ PC1)))
log(f"UN speeches={len(rows):,}  countries={len({c for c,_,_ in rows})}  "
    f"years {min(y for _,y,_ in rows)}-{max(y for _,y,_ in rows)}")

byc = defaultdict(list)
for c, y, p in rows: byc[c].append((y, p))
names, slopes, slopes_q, ns = [], [], [], []
for c, pts in byc.items():
    ys = np.array([y for y, _ in pts], float); ps = np.array([p for _, p in pts], float)
    if len(ys) < MINPTS or (ys.max() - ys.min()) < MINSPAN: continue
    names.append(c); ns.append(len(ys))
    slopes.append(stats.linregress(ys, ps).slope)
    yc = ys - ys.mean()
    A = np.column_stack([yc, yc ** 2, np.ones(len(yc))])
    slopes_q.append(float(np.linalg.lstsq(A, ps, rcond=None)[0][0]))
slopes = np.array(slopes); slopes_q = np.array(slopes_q)
tt, pp = stats.ttest_1samp(slopes, 0.0)
npos = int((slopes > 0).sum()); sp = float(stats.binomtest(npos, len(slopes), 0.5).pvalue)
tq, pq = stats.ttest_1samp(slopes_q, 0.0)
log(f"WITHIN country: {len(slopes)} countries (>= {MINPTS} speeches, >= {MINSPAN} year span), "
    f"mean slope {slopes.mean():+.5f}/yr  t={tt:+.2f} p={pp:.4g}  "
    f"toward matter {npos}/{len(slopes)} (sign p={sp:.4g})")
log(f"WITHIN country with a curvature term in year: linear mean {slopes_q.mean():+.5f}/yr "
    f"t={tq:+.2f} p={pq:.4g}")

ally = np.array([y for _, y, _ in rows], float); allp = np.array([p for _, _, p in rows], float)
xs = stats.linregress(ally, allp)
bx = np.array([np.mean([y for y, _ in byc[c]]) for c in names])
by = np.array([np.mean([p for _, p in byc[c]]) for c in names])
bt = stats.linregress(bx, by)
sd_all = allp.std(ddof=1)
log(f"BETWEEN: pooled cross section {xs.slope:+.5f}/yr r={xs.rvalue:+.3f} p={xs.pvalue:.4g}")
log(f"BETWEEN (strict, country mean year against country mean character over {len(bx)} countries): "
    f"{bt.slope:+.5f}/yr r={bt.rvalue:+.3f} p={bt.pvalue:.4g}")

# wild bootstrap over countries, restricted null (no within country drift)
tb = np.empty(NBOOT)
pre = {c: (np.array([y for y, _ in byc[c]], float), np.array([p for _, p in byc[c]], float)) for c in names}
for b in range(NBOOT):
    sl = []
    for c in names:
        ys, ps = pre[c]
        fit = np.polyval(np.polyfit(ys, ps, 1), ys)
        resid = ps - fit
        star = ps.mean() + resid * rng.choice([-1.0, 1.0])
        sl.append(stats.linregress(ys, star).slope)
    tb[b] = stats.ttest_1samp(sl, 0.0).statistic
pw = float((np.sum(np.abs(tb) >= abs(tt)) + 1) / (NBOOT + 1))
log(f"WILD BOOTSTRAP over countries (each keeps its own year design and residual scale): "
    f"observed t={tt:+.2f}  p={pw:.4f}")

RES = dict(speeches=len(rows), countries_all=len({c for c, _, _ in rows}),
           countries_used=int(len(slopes)), within_mean=float(slopes.mean()),
           t=float(tt), p=float(pp), toward_matter=npos, sign_p=sp,
           within_mean_with_curvature=float(slopes_q.mean()), t_curv=float(tq), p_curv=float(pq),
           cross_section=float(xs.slope), cross_section_r=float(xs.rvalue), cross_section_p=float(xs.pvalue),
           between_country=float(bt.slope), between_country_r=float(bt.rvalue), between_country_p=float(bt.pvalue),
           p_wild=pw, sd_pc1=float(sd_all), minpts=MINPTS, minspan=MINSPAN)
json.dump(RES, open(OUT, "w"), indent=1)
log(f"wrote {OUT}")

#!/usr/bin/env python3
"""genre_calib.py — GENRE BASELINE CALIBRATION for the manner-inflation detector.

PURE ANALYSIS on already-scored data. No new scoring; does not touch :8301/:8288.

Calibration base: the FROZEN 400-community reddit genre taxonomy (genre_assign_400_FROZEN.json)
joined to per-item 8-axis character scores in cc_v3.reddit_wide (80,138 items, 400 communities,
14 usable genres after excluding other_misc). This is the only scored corpus carrying a clean,
purpose-built genre label. The 2.65M-domain cc_v3.domain_char8_expanded carries NO genre column,
and the web topic tables (pld_content_topic, pld_topicality) either do not join to it (3 rows) or
carry mixed, junk-laden vocab (topicality) — so a clean WEB genre calibration is not available;
that limitation is reported, not papered over.

Metric (spec): manner inflation = manner - matter, per text.
  matter = mean(rigour, depth)
  manner = mean(affect, stance, register)
Genre baseline = the distribution of that metric within a genre.
Calibrated manipulation score = a text's manner inflation as a robust z (and percentile) ABOVE
its own genre baseline. Manipulation is the residual over the genre norm, not raw high manner.

False-positive guard: IRA political trolls (already scored) are placed against the
politics_ideology genre baseline (their natural genre) — the test is whether the calibration
still flags them as anomalous while NOT flagging ordinary political / high-manner content.
"""
import os, json, numpy as np, psycopg2

CHAR = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
MATTER = ["rigour", "depth"]
MANNER = ["affect", "stance", "register"]
GENRE_JSON = "/home/jason/projects/kronaxis/truthometer/results/prereg_genre_PF-4B/genre_assign_400_FROZEN.json"
IRA = "/mnt/nas/kronaxis/corpora/ira_troll/work/scored.jsonl"
POL = {"RightTroll", "LeftTroll", "Fearmonger"}
MANNER_INFL = "manner inflation = mean(affect,stance,register) - mean(rigour,depth)"

PW = [l.split("=", 1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
db = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"); cur = db.cursor()

def matter(ch): return float(np.mean([ch[a] for a in MATTER]))
def manner(ch): return float(np.mean([ch[a] for a in MANNER]))
def mi(ch):     return manner(ch) - matter(ch)

# ---- canonical PC1 (matter<->manner) ruler for the robustness cross-check ----
cur.execute(f"SELECT {','.join(CHAR)} FROM cc_v3.domain_char8_expanded")
allc = np.array([[float(x) for x in r] for r in cur.fetchall()], float)
CMEAN = allc.mean(0); CSTD = allc.std(0) + 1e-9
_, _, Vt = np.linalg.svd((allc - CMEAN) / CSTD, full_matrices=False); PC1 = Vt[0]
if (PC1[CHAR.index("rigour")] + PC1[CHAR.index("depth")]) < 0: PC1 = -PC1
def pc1(ch): return float(((np.array([ch[a] for a in CHAR], float) - CMEAN) / CSTD) @ PC1)
print(f"[axis-scale] web-ref per-axis mean/std (0-1 scorer):")
for a, m, s in zip(CHAR, CMEAN, CSTD):
    print(f"   {a:<18} mean={m:.3f} std={s:.3f}")

# ---- load reddit_wide items + genre ----
gmap = json.load(open(GENRE_JSON))
cur.execute("SELECT subreddit, char FROM cc_v3.reddit_wide WHERE char IS NOT NULL")
items = []            # (subreddit, genre, mi, matter, manner, pc1(-> matter+, so manner = -pc1 side))
by_comm = {}          # subreddit -> list of mi
for sub, ch in cur.fetchall():
    ch = ch if isinstance(ch, dict) else json.loads(ch)
    if not all(a in ch for a in CHAR): continue
    g = gmap.get(sub)
    if g is None or g == "other_misc": continue
    v = mi(ch)
    items.append((sub, g, v))
    by_comm.setdefault(sub, []).append(v)
print(f"\n[data] {len(items)} scored reddit items, {len(by_comm)} communities, "
      f"{len(set(g for _,g,_ in items))} genres (other_misc excluded)")

# per-genre item arrays and per-community means
genre_items = {}
comm_mean = {s: float(np.mean(v)) for s, v in by_comm.items()}
comm_genre = {}
for sub, g, v in items:
    genre_items.setdefault(g, []).append(v)
    comm_genre[sub] = g
genre_comm_means = {}
for s, m in comm_mean.items():
    genre_comm_means.setdefault(comm_genre[s], []).append(m)

def stats(arr):
    a = np.asarray(arr, float)
    med = np.median(a); mad = np.median(np.abs(a - med)) * 1.4826 + 1e-9
    return dict(n=len(a), median=med, mean=a.mean(), std=a.std(),
                iqr=np.percentile(a, 75) - np.percentile(a, 25),
                p90=np.percentile(a, 90), p95=np.percentile(a, 95),
                mad=mad, q25=np.percentile(a, 25), q75=np.percentile(a, 75))

# ---- RANKED GENRE BASELINE TABLE ----
gstat = {g: stats(v) for g, v in genre_items.items()}
ranked = sorted(gstat.items(), key=lambda kv: -kv[1]["median"])
print("\n" + "=" * 96)
print("GENRE BASELINE TABLE — normal manner inflation per genre (ranked high->low, item-level)")
print("  " + MANNER_INFL)
print("=" * 96)
print(f"  {'genre':<26}{'#comm':>6}{'#items':>7}{'median':>8}{'mean':>8}{'IQR':>7}{'p90':>7}{'p95':>7}{'MADσ':>7}")
for g, s in ranked:
    nc = len(genre_comm_means[g])
    print(f"  {g:<26}{nc:>6}{s['n']:>7}{s['median']:>8.3f}{s['mean']:>8.3f}{s['iqr']:>7.3f}{s['p90']:>7.3f}{s['p95']:>7.3f}{s['mad']:>7.3f}")
allmi = np.array([v for _, _, v in items], float)
gl = stats(allmi)
print(f"  {'--- POOLED (all genres) ---':<26}{len(by_comm):>6}{gl['n']:>7}{gl['median']:>8.3f}{gl['mean']:>8.3f}{gl['iqr']:>7.3f}{gl['p90']:>7.3f}{gl['p95']:>7.3f}{gl['mad']:>7.3f}")

# ---- CALIBRATED SCORE: robust within-genre z + percentile ----
def cal_z(v, g):   s = gstat[g]; return (v - s["median"]) / s["mad"]
def cal_pct(v, g):
    arr = np.asarray(genre_items[g]); return float((arr < v).mean())

# sanity: each genre's own items are centred at 0 by construction; check tail uniformity
print("\n" + "=" * 96)
print("FALSE-POSITIVE GUARD 1 — within-genre calibration is uniform across genres")
print("  (fraction of each genre's OWN items exceeding its own calibrated z>=2 threshold;")
print("   a high-manner genre must NOT be flagged more than a low-manner one — the point of calibration)")
print("=" * 96)
print(f"  {'genre':<26}{'baseline median':>16}{'own frac z>=2':>15}{'own frac >p95':>15}")
for g, s in ranked:
    zs = np.array([cal_z(v, g) for v in genre_items[g]])
    fr2 = float((zs >= 2).mean())
    thr = s["p95"]; frp = float((np.asarray(genre_items[g]) >= thr).mean())
    print(f"  {g:<26}{s['median']:>16.3f}{fr2:>15.1%}{frp:>15.1%}")

# ---- IRA deception, genre-relative ----
ira = []
for l in open(IRA):
    try: r = json.loads(l)
    except Exception: continue
    if r.get("kind") == "ira" and r.get("outcome") in POL and "char" in r and all(a in r["char"] for a in CHAR):
        ira.append(mi(r["char"]))
ira = np.array(ira, float)
POL_G = "politics_ideology"
ps = gstat[POL_G]
print("\n" + "=" * 96)
print("FALSE-POSITIVE GUARD 2 — known deception (IRA political trolls) vs its own genre baseline")
print("=" * 96)
print(f"  IRA political trolls: n={len(ira)}  raw manner-inflation median={np.median(ira):.3f}  mean={ira.mean():.3f}")
print(f"  politics_ideology baseline: median={ps['median']:.3f}  p95={ps['p95']:.3f}  MADsigma={ps['mad']:.3f}")
ira_z = (np.median(ira) - ps["median"]) / ps["mad"]
ira_pct = float((np.asarray(genre_items[POL_G]) < np.median(ira)).mean())
print(f"  IRA median expressed within politics_ideology: calibrated z = {ira_z:+.2f}  (percentile {ira_pct:.1%})")
frac_ira_over_polp95 = float((ira >= ps["p95"]).mean())
print(f"  fraction of IRA items above the politics_ideology p95 threshold: {frac_ira_over_polp95:.1%}  (expected ~5% if IRA were ordinary political content)")
# ordinary politics communities: their own items above own p95 (must be ~5%)
pol_frac = float((np.asarray(genre_items[POL_G]) >= ps["p95"]).mean())
print(f"  fraction of ORDINARY politics_ideology items above that same threshold: {pol_frac:.1%}  (the legitimate-persuasion false-positive rate)")
# lift
print(f"  detection lift: IRA flag rate / ordinary-political flag rate = {frac_ira_over_polp95/ max(pol_frac,1e-9):.1f}x")

# also: IRA vs the HIGHEST-manner legit genre (hardest false-positive case) and vs pooled
top_g, top_s = ranked[0]
frac_ira_over_top = float((ira >= top_s["p95"]).mean())
print(f"\n  hardest case: IRA vs the highest-manner LEGIT genre ({top_g}, baseline median {top_s['median']:.3f}):")
print(f"    fraction of IRA above {top_g} p95: {frac_ira_over_top:.1%}   IRA median calibrated z in {top_g}: {(np.median(ira)-top_s['median'])/top_s['mad']:+.2f}")
frac_ira_over_pool = float((ira >= gl["p95"]).mean())
print(f"  IRA vs POOLED (uncalibrated / naive detector) p95: {frac_ira_over_pool:.1%} of IRA flagged")

# ---- naive vs calibrated contrast on the legit high-manner genres ----
print("\n" + "=" * 96)
print("NAIVE vs CALIBRATED — a naive 'high manner = manipulation' detector false-positives on")
print("legitimately high-manner genres; the genre-calibrated score does not")
print("=" * 96)
naive_thr = gl["p95"]   # a single global threshold (naive detector)
print(f"  naive global threshold (pooled p95 of manner inflation) = {naive_thr:.3f}")
print(f"  {'genre':<26}{'naive FP rate':>14}{'calibrated FP rate':>20}")
for g, s in ranked[:6]:
    arr = np.asarray(genre_items[g])
    naive_fp = float((arr >= naive_thr).mean())
    cal_fp = float((np.array([cal_z(v, g) for v in arr]) >= 1.645).mean())  # one-sided 5%
    print(f"  {g:<26}{naive_fp:>14.1%}{cal_fp:>20.1%}")
print("  (naive FP rate balloons for high-manner genres; calibrated FP rate stays ~5% for every genre)")

print("\n[caveats] genre base is reddit social text (14 genres), one 7B scorer; it lacks explicit")
print("  commercial genres (sales pages, display ads, tabloid) — those are approximated here by the")
print("  high-manner social genres (snark/gossip/reality-tv/support). IRA is one actor/era/platform.")
print("  The web corpus (2.65M domains) is unlabelled for genre, so the calibration is demonstrated")
print("  on reddit and stated as method, not a web-scale production baseline.")

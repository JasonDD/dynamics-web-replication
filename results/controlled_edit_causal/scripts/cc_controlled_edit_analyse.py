#!/usr/bin/env python3
"""cc_controlled_edit_analyse.py — the causal read of the controlled-edit test.

Reads the scored variants (cc_found_human_score.py output, id="<base>__<variant>") and reports, PAIRED
within each base text:
  1. per-axis mean shift (variant - base) with bootstrap 95% CIs, for each variant
  2. PC1 shift (same SVD basis as length_mechanism.py: the internal reference table, standardised, oriented
     rigour+depth positive) -- the falsification kill-test axis
  3. the LENGTH control contrast: matter_insert vs placebo_insert on the MATTER axes (is it the marker or
     just the added words?)
  4. the ASYMMETRY: zero-added-word affect_rewrite moves affect while zero-added-word matter_rewrite fails
     to move rigour/depth (matter needs bandwidth, manner is instant)

Emits a JSON stats blob + a human table to stdout.
"""
import os, json, numpy as np, psycopg2

SCORED = os.environ.get("SCORED", "the internal corpus store/controlled_edit/scored.jsonl")
STATS_OUT = os.environ.get("STATS_OUT", "the internal corpus store/controlled_edit/stats.json")
NBOOT = int(os.environ.get("NBOOT", "5000"))

DWEB   = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
MATTER = ["rigour","depth"]
MANNER = ["affect","stance","register"]
VARIANTS = ["matter_insert","placebo_insert","affect_insert","affect_rewrite","matter_rewrite"]

# ---- PC1 basis (identical construction to length_mechanism.py)
PW = [l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
c = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
c.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
allc = np.array([[float(x) for x in r] for r in c.fetchall()], float)
MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
_,_,Vt = np.linalg.svd((allc-MEAN)/STD, full_matrices=False); PC1 = Vt[0]
if (PC1[DWEB.index("rigour")]+PC1[DWEB.index("depth")]) < 0:
    PC1 = -PC1
def pc1(ch):
    return float(((np.array([ch[a] for a in DWEB],float)-MEAN)/STD) @ PC1)
print(f"[pc1] reference n={len(allc)}  loadings: " + ", ".join(f"{a}={PC1[i]:+.2f}" for i,a in enumerate(DWEB)))

# ---- load scored, index by base id
rows = {}
for l in open(SCORED):
    try:
        r = json.loads(l)
    except Exception:
        continue
    ch = r.get("char")
    if not isinstance(ch, dict) or not all(a in ch for a in DWEB):
        continue
    rid = r["id"]
    if "__" not in rid:
        continue
    bid, var = rid.rsplit("__", 1)
    rows.setdefault(bid, {})[var] = ch

# keep only bases that have base + every variant (complete cases -> clean pairing)
need = set(["base"] + VARIANTS)
complete = {b: v for b, v in rows.items() if need.issubset(v.keys())}
print(f"bases scored: {len(rows)}  complete (all 6 cells): {len(complete)}")

def feat(ch):
    d = {a: ch[a] for a in DWEB}
    d["MATTER"] = np.mean([ch[a] for a in MATTER])
    d["MANNER"] = np.mean([ch[a] for a in MANNER])
    d["PC1"] = pc1(ch)
    return d

AXES = DWEB + ["MATTER","MANNER","PC1"]
bases = sorted(complete)
base_f = {b: feat(complete[b]["base"]) for b in bases}
var_f  = {v: {b: feat(complete[b][v]) for b in bases} for v in VARIANTS}

rng = np.random.default_rng(1729)
def boot_ci(deltas):
    d = np.asarray(deltas, float)
    n = len(d)
    idx = rng.integers(0, n, size=(NBOOT, n))
    means = d[idx].mean(1)
    return float(d.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))

# ---- paired shift table (variant - base) per axis
stats = {"n_bases": len(bases), "pc1_loadings": {a: float(PC1[i]) for i,a in enumerate(DWEB)}, "shifts": {}}
print("\n" + "="*100)
print("PAIRED MEAN SHIFT (variant - base), 95% bootstrap CI  [* = CI excludes 0]")
print("="*100)
hdr = "axis".ljust(16) + "".join(v[:13].rjust(15) for v in VARIANTS)
print(hdr)
for ax in AXES:
    stats["shifts"][ax] = {}
    cells = []
    for v in VARIANTS:
        deltas = [var_f[v][b][ax] - base_f[b][ax] for b in bases]
        m, lo, hi = boot_ci(deltas)
        sig = "*" if (lo > 0 or hi < 0) else " "
        stats["shifts"][ax][v] = {"mean": m, "lo": lo, "hi": hi, "sig": (lo > 0 or hi < 0)}
        cells.append(f"{m:+.3f}{sig}".rjust(15))
    print(ax.ljust(16) + "".join(cells))

# ---- contrast 1: matter marker vs length-matched placebo, on MATTER axes + PC1
print("\n" + "="*100)
print("LENGTH CONTROL: matter_insert vs placebo_insert  (both add ~equal words) -> is it MARKER or LENGTH?")
print("="*100)
stats["contrast_matter_vs_placebo"] = {}
for ax in MATTER + ["MATTER","depth","PC1","rigour"]:
    if ax in stats["contrast_matter_vs_placebo"]:
        continue
    diff = [var_f["matter_insert"][b][ax] - var_f["placebo_insert"][b][ax] for b in bases]
    m, lo, hi = boot_ci(diff)
    sig = "*" if (lo > 0 or hi < 0) else " "
    stats["contrast_matter_vs_placebo"][ax] = {"mean": m, "lo": lo, "hi": hi, "sig": (lo > 0 or hi < 0)}
    print(f"  {ax.ljust(14)} matter - placebo = {m:+.3f}{sig}  CI[{lo:+.3f},{hi:+.3f}]")

# ---- contrast 2: the asymmetry at ZERO added words
print("\n" + "="*100)
print("ASYMMETRY (zero added words): affect_rewrite moves AFFECT while matter_rewrite fails to move MATTER?")
print("="*100)
stats["asymmetry_zero_length"] = {}
pairs = [("affect_rewrite","affect"), ("affect_rewrite","MANNER"),
         ("matter_rewrite","rigour"), ("matter_rewrite","depth"),
         ("matter_rewrite","MATTER"), ("matter_rewrite","register"),
         ("matter_rewrite","PC1"), ("affect_rewrite","PC1")]
for v, ax in pairs:
    deltas = [var_f[v][b][ax] - base_f[b][ax] for b in bases]
    m, lo, hi = boot_ci(deltas)
    sig = "*" if (lo > 0 or hi < 0) else " "
    stats["asymmetry_zero_length"][f"{v}:{ax}"] = {"mean": m, "lo": lo, "hi": hi, "sig": (lo > 0 or hi < 0)}
    print(f"  {v:14s} -> {ax.ljust(8)} shift = {m:+.3f}{sig}  CI[{lo:+.3f},{hi:+.3f}]")

# ---- length-conditioned: can matter_insert move MATTER in SHORT vs LONG bases equally? (matter needs bandwidth)
# recover base word count from the scored input if available; otherwise skip gracefully.
INPUT = os.environ.get("INPUT", "the internal corpus store/controlled_edit/score_input.jsonl")
basewc = {}
if os.path.exists(INPUT):
    for l in open(INPUT):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("outcome") == "base":
            bid = r["id"].rsplit("__",1)[0]
            basewc[bid] = len(r["text"].split())
if basewc:
    print("\n" + "="*100)
    print("MATTER-NEEDS-BANDWIDTH: matter_insert MATTER-shift by BASE length (short bases have less room)")
    print("="*100)
    stats["matter_shift_by_baselen"] = {}
    med = np.median([basewc[b] for b in bases if b in basewc])
    for label, keep in [("short (<=median base wc)", lambda b: basewc.get(b,0) <= med),
                        ("long  (> median base wc)", lambda b: basewc.get(b,0) >  med)]:
        sub = [b for b in bases if b in basewc and keep(b)]
        if len(sub) < 10:
            continue
        for v, ax in [("matter_insert","MATTER"), ("matter_rewrite","MATTER"),
                      ("affect_insert","affect"), ("affect_rewrite","affect")]:
            deltas = [var_f[v][b][ax] - base_f[b][ax] for b in sub]
            m, lo, hi = boot_ci(deltas)
            sig = "*" if (lo > 0 or hi < 0) else " "
            stats["matter_shift_by_baselen"][f"{label}|{v}:{ax}"] = {"mean": m, "lo": lo, "hi": hi, "n": len(sub)}
            print(f"  {label:26s} n={len(sub):3d}  {v:14s}->{ax.ljust(7)} {m:+.3f}{sig} CI[{lo:+.3f},{hi:+.3f}]")

os.makedirs(os.path.dirname(STATS_OUT), exist_ok=True)
json.dump(stats, open(STATS_OUT, "w"), indent=2)
print(f"\nwrote {STATS_OUT}")

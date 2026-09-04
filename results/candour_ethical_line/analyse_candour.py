#!/usr/bin/env python3
"""analyse_candour.py — is CANDOUR the ethical line between legitimate persuasion and
manipulation on the 8 axis DYNAMICS-WEB character instrument?

Hypothesis: legitimate persuasion is open about its intent (a charity says "please donate",
an advert says "buy this") -> HIGH candour. Manipulation hides its intent (a dark pattern
disguises the ask, a troll hides who it is, a phish impersonates) -> LOW candour.

Test: pool legit persuasion vs pool manipulation, and ask which single axis separates them
most cleanly. The three competitors named in the brief are candour, manner inflation
(the residual manner - matter) and affect. Report each one's univariate AUC on the SAME
contrast, plus the full 8 axis classifier as the ceiling, plus per manipulation domain
candour AUC, a candour threshold sweep, and the plane coordinates for plotting.

No sklearn: logistic regression, k fold CV and AUC are numpy here (same as manip_analyse.py).
"""
import os, json, numpy as np, psycopg2

DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
rng = np.random.default_rng(1729)

# ---- matter/manner PC1 (SVD on the web character reference), oriented rigour+depth positive.
# Needs the tfs DB (the internal host local); if unreachable, PC1 degrades to NaN and the candour verdict,
# which does not depend on PC1, still stands.
PC1 = None; MEAN = STD = None
try:
    PW = [l.split("=", 1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
    dbhost = os.environ.get("PGHOST", "127.0.0.1")
    c = psycopg2.connect(f"host={dbhost} port=5432 user=titan password={PW} dbname=tfs").cursor()
    c.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
    allc = np.array([[float(x) for x in r] for r in c.fetchall()], float)
    MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
    _, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False); PC1 = Vt[0]
    if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0:
        PC1 = -PC1
    print("[PC1] loaded matter/manner reference from the internal reference table", flush=True)
except Exception as e:
    print(f"[PC1] DB unreachable ({e}); PC1 columns will be NaN (candour verdict unaffected)", flush=True)
def pc1(ch):
    if PC1 is None:
        return float("nan")
    return float(((np.array([ch[a] for a in DWEB], float) - MEAN) / STD) @ PC1)

def load(path, kind=None, outcomes=None, cap=None):
    out = []
    for l in open(path):
        try:
            r = json.loads(l)
        except Exception:
            continue
        ch = r.get("char")
        if not ch or not all(a in ch for a in DWEB):
            continue
        if kind is not None and r.get("kind") != kind:
            continue
        if outcomes is not None and r.get("outcome") not in outcomes:
            continue
        out.append(r)
    if cap and len(out) > cap:
        idx = rng.permutation(len(out))[:cap]
        out = [out[i] for i in idx]
    return out

C = "the internal corpus store"
# ----- LEGITIMATE PERSUASION (open about intent -> predicted HIGH candour) -----
psg     = load(f"{C}/human_persuasion/psg_scores.jsonl", kind="psg")                 # charity donation dialogue
donors  = load(f"{C}/candour_line/scored.jsonl", kind="donorschoose")                # charity funding appeals
kick    = load(f"{C}/human_persuasion/kickstarter_scores.jsonl", kind="ks", cap=6000)# commercial crowdfunding (hard sell)
amazon  = load(f"{C}/candour_line/scored.jsonl", kind="amazon")                      # commercial product reviews
cmv     = load(f"{C}/cmv_winning_args/cmv_scores.jsonl", kind="arg", cap=6000)       # sincere reasoning anchor
# ----- MANIPULATION (hides intent -> predicted LOW candour) -----
ira     = load(f"{C}/ira_troll/work/scored.jsonl", kind="ira", outcomes={"RightTroll", "LeftTroll", "Fearmonger"})
dark    = load(f"{C}/manner_inflation/scored.jsonl", kind="dark", outcomes={"dark"})
darkm   = load(f"{C}/manner_inflation/scored.jsonl", kind="darkm")                   # Mathur labelled dark patterns
phish   = load(f"{C}/manner_inflation/scored.jsonl", kind="phish", outcomes={"phish"})
liar_f  = load(f"{C}/ira_troll/work/scored.jsonl", kind="liar", outcomes={"false", "pants-fire"})
# ----- HONEST CONTROLS (matched genre, for the plane only) -----
dark_ok = load(f"{C}/manner_inflation/scored.jsonl", kind="dark", outcomes={"normal"})
phish_ok= load(f"{C}/manner_inflation/scored.jsonl", kind="phish", outcomes={"safe"})
liar_t  = load(f"{C}/ira_troll/work/scored.jsonl", kind="liar", outcomes={"true", "mostly-true"})

LEGIT = [("psg (charity dialogue)", psg), ("donorschoose (charity appeal)", donors),
         ("kickstarter (crowdfund sell)", kick), ("amazon (product review)", amazon),
         ("CMV (sincere reasoning)", cmv)]
MANIP = [("IRA (state troll)", ira), ("dark pattern (RachitD)", dark),
         ("dark pattern (Mathur)", darkm), ("phishing", phish), ("LIAR false claim", liar_f)]
CTRL  = [("dark normal (control)", dark_ok), ("phish safe (control)", phish_ok),
         ("LIAR true (control)", liar_t)]

def feats(rows):
    M = np.array([[r["char"][a] for a in DWEB] for r in rows], float)
    cand = M[:, DWEB.index("candour")]
    aff = M[:, DWEB.index("affect")]
    matter = M[:, [DWEB.index("rigour"), DWEB.index("depth")]].mean(1)
    manner = M[:, [DWEB.index("affect"), DWEB.index("stance"), DWEB.index("register")]].mean(1)
    mi = manner - matter
    p = np.array([pc1(r["char"]) for r in rows])
    return M, cand, aff, mi, p

def auc(y, s):
    pos = (y == 1); neg = (y == 0)
    if pos.sum() == 0 or neg.sum() == 0:
        return float("nan")
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt); avg = (csum - cnt + 1 + csum) / 2.0
    ranks = avg[inv]
    rp = ranks[pos].sum()
    return (rp - pos.sum() * (pos.sum() + 1) / 2.0) / (pos.sum() * neg.sum())

print("=== group sizes ===")
for n, g in LEGIT + MANIP + CTRL:
    print(f"  {n:<32} n={len(g)}")

print("\n=== mean 8 axis + candour/affect/manner-inflation/PC1 per group ===")
hdr = "  " + "group".ljust(32) + "".join(a[:5].rjust(7) for a in DWEB) + "   MI".rjust(8) + "   PC1".rjust(8)
print(hdr)
def line(name, rows):
    if not rows:
        print("  " + name.ljust(32) + " (empty)"); return None
    M, cand, aff, mi, p = feats(rows)
    print("  " + name.ljust(32) + "".join(f"{v:7.3f}" for v in M.mean(0)) + f"{mi.mean():8.3f}{p.mean():8.3f}")
    return dict(name=name, n=len(rows), mean=M.mean(0).tolist(),
                candour=float(cand.mean()), candour_sd=float(cand.std()),
                affect=float(aff.mean()), affect_sd=float(aff.std()),
                mi=float(mi.mean()), mi_sd=float(mi.std()), pc1=float(p.mean()))
print("  -- LEGITIMATE PERSUASION --")
plane = {"legit": [line(n, g) for n, g in LEGIT],
         "manip": [], "ctrl": []}
print("  -- MANIPULATION --")
plane["manip"] = [line(n, g) for n, g in MANIP]
print("  -- HONEST CONTROLS --")
plane["ctrl"] = [line(n, g) for n, g in CTRL]

# ---------------- pooled legit vs manip: single axis separating power ----------------
legit_rows = [r for _, g in LEGIT for r in g]
manip_rows = [r for _, g in MANIP for r in g]
Ml, cand_l, aff_l, mi_l, p_l = feats(legit_rows)
Mm, cand_m, aff_m, mi_m, p_m = feats(manip_rows)

def balanced_idx(nA, nB):
    k = min(nA, nB)
    return rng.permutation(nA)[:k], rng.permutation(nB)[:k], k

ia, ib, k = balanced_idx(len(legit_rows), len(manip_rows))
print(f"\n=== pooled LEGIT vs MANIP, balanced n={k}/side ===")
print("  univariate AUC (legit=1). >0.5 => axis is HIGHER in legit; magnitude = separating power")
def uni(name, vl, vm):
    s = np.hstack([vl[ia], vm[ib]]); y = np.hstack([np.ones(k), np.zeros(k)])
    a = auc(y, s)
    return name, a, max(a, 1 - a)
rows_uni = []
for i, a in enumerate(DWEB):
    rows_uni.append(uni(a, Ml[:, i], Mm[:, i]))
rows_uni.append(uni("manner_inflation", mi_l, mi_m))
rows_uni.append(uni("matter/manner PC1", p_l, p_m))
for name, a, mag in sorted(rows_uni, key=lambda x: -x[2]):
    hi = "legit" if a > 0.5 else "manip"
    print(f"    {name:<20} AUC={a:.3f}  separating_power={mag:.3f}  (higher in {hi})")

# the three named competitors, side by side
print("\n  === THE HEADLINE: candour vs manner-inflation vs affect (separating power) ===")
for name, vl, vm in [("candour", cand_l, cand_m), ("manner_inflation", mi_l, mi_m), ("affect", aff_l, aff_m)]:
    s = np.hstack([vl[ia], vm[ib]]); y = np.hstack([np.ones(k), np.zeros(k)])
    a = auc(y, s)
    print(f"    {name:<18} AUC={a:.3f}  separating_power={max(a,1-a):.3f}")

# ---------------- per manipulation domain: candour AUC (legit pool vs each domain) ----------------
print("\n=== candour AUC: full legit pool vs EACH manipulation domain (candour higher in legit=1) ===")
print("  also affect & manner-inflation for the same per-domain contrast")
for name, g in MANIP:
    if not g:
        continue
    _, cand_d, aff_d, mi_d, _ = feats(g)
    kk = min(len(legit_rows), len(g))
    la = rng.permutation(len(legit_rows))[:kk]; da = rng.permutation(len(g))[:kk]
    y = np.hstack([np.ones(kk), np.zeros(kk)])
    ac = auc(y, np.hstack([cand_l[la], cand_d[da]]))
    aa = auc(y, np.hstack([aff_l[la], aff_d[da]]))
    am = auc(y, np.hstack([mi_l[la], mi_d[da]]))
    print(f"    {name:<26} candour={ac:.3f}  affect={1-aa:.3f}(manip-high)  manner_infl={1-am:.3f}(manip-high)  n={kk}/side")

# ---------------- candour threshold sweep ----------------
print("\n=== candour threshold sweep (pooled legit vs manip, balanced) ===")
cl = cand_l[ia]; cm = cand_m[ib]
best = None
for thr in np.round(np.arange(0.50, 0.96, 0.01), 2):
    tpr = (cl >= thr).mean()          # legit correctly kept (candour high)
    fpr = (cm >= thr).mean()          # manip wrongly spared
    youden = tpr - fpr
    if best is None or youden > best[3]:
        best = (thr, tpr, fpr, youden)
print(f"  legit candour: median={np.median(cl):.3f} p10={np.percentile(cl,10):.3f} p25={np.percentile(cl,25):.3f}")
print(f"  manip candour: median={np.median(cm):.3f} p75={np.percentile(cm,75):.3f} p90={np.percentile(cm,90):.3f}")
print(f"  best Youden threshold t={best[0]:.2f}: keeps {best[1]*100:.1f}% legit, spares(FPR) {best[2]*100:.1f}% manip, J={best[3]:.3f}")
# overlap coefficient at the coarse grid
lo, hi = 0.0, 1.0
grid = np.round(np.arange(lo, hi + 1e-6, 1/60.0), 4)
hl, _ = np.histogram(cl, bins=np.append(grid, 1.0001), density=True)
hm, _ = np.histogram(cm, bins=np.append(grid, 1.0001), density=True)
ov = np.minimum(hl, hm).sum() / max(hl.sum(), 1)
print(f"  histogram overlap coefficient (candour, legit vs manip) = {ov:.3f}  (0=disjoint, 1=identical)")

# ---------------- full 8 axis classifier (ceiling) ----------------
def fit_logistic(X, y, iters=600, lr=0.3, l2=1e-3):
    n, d = X.shape; w = np.zeros(d); b = 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(X @ w + b))); g = p - y
        w -= lr * (X.T @ g / n + l2 * w); b -= lr * g.mean()
    return w, b
X = np.vstack([Ml[ia], Mm[ib]]); y = np.hstack([np.ones(k), np.zeros(k)])
perm = rng.permutation(len(y)); X = X[perm]; y = y[perm]
folds = np.array_split(np.arange(len(y)), 5); aucs = []; coefs = []
for f in range(5):
    te = folds[f]; tr = np.hstack([folds[j] for j in range(5) if j != f])
    mu = X[tr].mean(0); sd = X[tr].std(0) + 1e-9
    w, b = fit_logistic((X[tr] - mu) / sd, y[tr])
    s = 1 / (1 + np.exp(-(((X[te] - mu) / sd) @ w + b)))
    aucs.append(auc(y[te], s)); coefs.append(w)
coefs = np.array(coefs).mean(0)
print(f"\n=== full 8 axis classifier (ceiling), legit vs manip, 5 fold CV ===")
print(f"  AUC = {np.mean(aucs):.3f} +/- {np.std(aucs):.3f}")
print("  standardised coefficients (+ => higher in legit):")
for i in np.argsort(-np.abs(coefs)):
    print(f"    {DWEB[i]:<18} {coefs[i]:+.2f}")

# dump plane coordinates as JSON for the RESULT tables/plot
with open(os.path.join(os.path.dirname(__file__), "plane_data.json"), "w") as f:
    json.dump(plane, f, indent=2)
print("\n[wrote] plane_data.json")
print("\n[note] one scorer lineage (7B an internal 7B instruct model). Manipulation groups are IRA (one actor,")
print("       one era, Twitter), dark patterns and phishing (English). Legit persuasion spans")
print("       charity, crowdfunding, reviews and sincere reasoning. Candour is the scorer's read")
print("       of transparency (0 opaque -> 1 transparent), not a ground truth intent label.")

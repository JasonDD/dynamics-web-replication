#!/usr/bin/env python3
"""biber_within_unit.py -- the Biber reduction WITHIN the unit, with measured reliability.

The first run reported item r = -0.14, within subreddit mean r = -0.08, between subreddit centroids r = -0.60.
A between unit correlation can be inflated by composition (the same comparison inflated a coupling slope
six fold elsewhere today), so this run (1) reports the POOLED within subreddit correlation with both
variables demeaned by room, (2) measures the reliability of each single comment read of Biber D1 by split
half (alternate sentences, Spearman Brown), (3) takes the reliability of a single comment PC1 read from the
two reader agreement on the cross site rows (both readers, same text), and (4) reports the within unit
correlation corrected for both, with a permutation null (D1 shuffled within room). Built on the original
script so features and PC1 are identical. Analysis only.
"""
import os, re, json, numpy as np, psycopg2

DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
OUT = os.path.expanduser("~/biber_within_out")
os.makedirs(OUT, exist_ok=True)

PW = [l.split("=", 1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
conn = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs")
c = conn.cursor()

# ---- matter/manner PC1 reference (same recipe as truthometer/scripts/manip_analyse.py)
c.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
allc = np.array([[float(x) for x in r] for r in c.fetchall()], float)
MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
_, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False)
PC1 = Vt[0]
if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0:
    PC1 = -PC1
print("PC1 loadings (rigour+depth oriented positive):")
for a, w in sorted(zip(DWEB, PC1), key=lambda t: -t[1]):
    print(f"  {a:<18} {w:+.3f}")

def pc1_of(ch):
    v = (np.array([ch[a] for a in DWEB], float) - MEAN) / STD
    return float(v @ PC1)

# ---- pull held reddit_wide docs: text + char + subreddit
c.execute("""
  SELECT id, subreddit, body, char
  FROM the internal Reddit corpus
  WHERE char IS NOT NULL AND char ? 'rigour' AND length(body) >= 200
""")
rows = c.fetchall()
print(f"\nfetched {len(rows)} scored reddit_wide docs (body >= 200 chars)")

# ================= Biber Dimension 1 feature extraction =================
FIRST = set("i me my mine myself we us our ours ourselves".split())
SECOND = set("you your yours yourself yourselves".split())
PRIVATE = set(("think thinks thought feel feels felt believe believes believed know knows knew "
    "guess guessed suppose supposed assume assumed doubt doubted hope hoped imagine imagined "
    "realize realise realized realised wonder wondered seem seems seemed understand understood "
    "mean meant want wants wanted wish wished remember remembered forget forgot notice noticed "
    "decide decided consider considered expect expected figure reckon agree agreed concern "
    "concerned believe recall assume").split())
DEMON = set("this that these those".split())
EMPH = set("just really so real most more such sure".split())
AMPL = set("very extremely totally completely absolutely highly entirely strongly fully quite too".split())
HEDGE1 = set("maybe perhaps somewhat probably possibly kinda sorta".split())
DISC = set("well now anyway anyhow".split())
CAUSE = set("because cause cuz bc".split())
WH = set("what where when why how who whom whose which".split())
POSS = set("can could may might will would shall should".split())
PREP = set(("of in to for with on at by from as into about over under between through during "
    "before after above below against among around upon within without toward towards than "
    "onto off per via across behind beside beyond near").split())
ARTICLE = set("the an".split())
NOMSUF = ("tion", "sion", "ment", "ness", "ity", "ance", "ence", "ism", "ation")

WORD = re.compile(r"[a-zA-Z]+(?:'[a-z]+)?")
ALPHA = re.compile(r"[a-zA-Z]+")
CONTR = re.compile(r"\b\w+'(t|s|re|ve|ll|d|m)\b", re.I)
NT = re.compile(r"n't\b", re.I)

INV_NAMES = ["first_person","second_person","private_verbs","contractions","present_bedohave",
    "demonstratives","emphatics","amplifiers","hedges","discourse_particles","neg_not",
    "causative","wh_words","possibility_modals","questions"]
INF_NAMES = ["mean_word_len","type_token_ratio","prepositions","nominalisations","article_density"]

def features(text):
    t = text.lower()
    toks = WORD.findall(t)
    n = len(toks)
    if n < 30:
        return None
    alpha = ALPHA.findall(t)
    def rate(cnt):
        return 100.0 * cnt / n
    fp = sum(w in FIRST for w in toks)
    sp = sum(w in SECOND for w in toks)
    pv = sum(w in PRIVATE for w in toks)
    contr = len(CONTR.findall(text)) + len(NT.findall(text))
    presentbe = sum(w in {"am","is","are","'s","'re","'m","do","does","have","has"} for w in toks)
    dem = sum(w in DEMON for w in toks)
    emph = sum(w in EMPH for w in toks)
    ampl = sum(w in AMPL for w in toks)
    hedge = sum(w in HEDGE1 for w in toks) + t.count("sort of") + t.count("kind of") + t.count("i think") + t.count("i guess")
    disc = sum(w in DISC for w in toks) + t.count("you know")
    neg = sum(w == "not" for w in toks) + len(NT.findall(text))
    caus = sum(w in CAUSE for w in toks)
    wh = sum(w in WH for w in toks)
    poss = sum(w in POSS for w in toks)
    q = text.count("?")

    prep = sum(w in PREP for w in toks)
    art = sum(w in ARTICLE for w in toks)
    nom = sum(any(w.endswith(s) and len(w) > len(s) + 2 for s in NOMSUF) for w in alpha)
    mwl = float(np.mean([len(w) for w in alpha])) if alpha else 0.0
    window = toks[:100]
    ttr = len(set(window)) / len(window) if window else 0.0

    inv = [rate(fp), rate(sp), rate(pv), rate(contr), rate(presentbe), rate(dem), rate(emph),
           rate(ampl), rate(hedge), rate(disc), rate(neg), rate(caus), rate(wh), rate(poss), rate(q)]
    inf = [mwl, ttr, rate(prep), rate(nom), rate(art)]
    return inv, inf

ids, subs, PCv, INV, INF, CHrows = [], [], [], [], [], []
skipped = 0
for _id, sub, body, ch in rows:
    f = features(body)
    if f is None:
        skipped += 1
        continue
    ids.append(_id); subs.append(sub)
    PCv.append(pc1_of(ch))
    INV.append(f[0]); INF.append(f[1])
    CHrows.append([float(ch[a]) for a in DWEB])

PCv = np.array(PCv)
INV = np.array(INV, float); INF = np.array(INF, float)
CH = np.array(CHrows, float)
print(f"usable docs after >=30-word floor: {len(PCv)} (skipped {skipped} short)")

def z(M):
    return (M - M.mean(0)) / (M.std(0) + 1e-12)

zinv = z(INV); zinf = z(INF)
# Biber standardised-additive D1: sum involved z, minus informational z (mean so counts balance)
D1 = zinv.mean(1) - zinf.mean(1)

def pearson(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d else float("nan")

def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return pearson(ra.astype(float), rb.astype(float))

r_p = pearson(PCv, D1)
r_s = spearman(PCv, D1)
print(f"\n=== PC1 vs Biber D1 ===  n={len(PCv)}")
print(f"  Pearson  r = {r_p:+.3f}")
print(f"  Spearman r = {r_s:+.3f}")

# per-axis alignment with D1 (raw axis vs involved-positive D1)
print("\n=== per-axis Pearson vs Biber D1 (positive = axis rises with INVOLVED) ===")
axis_r = {}
for i, a in enumerate(DWEB):
    rr = pearson(CH[:, i], D1)
    axis_r[a] = rr
for a, rr in sorted(axis_r.items(), key=lambda t: t[1]):
    print(f"  {a:<18} {rr:+.3f}")

# which raw Biber features drive D1's link to PC1 (corr of each feature vs PC1)
print("\n=== Biber feature vs PC1 (sign shows matter/manner side) ===")
feat_r = {}
for i, nm in enumerate(INV_NAMES):
    feat_r["INV:"+nm] = pearson(INV[:, i], PCv)
for i, nm in enumerate(INF_NAMES):
    feat_r["INF:"+nm] = pearson(INF[:, i], PCv)
for nm, rr in sorted(feat_r.items(), key=lambda t: t[1]):
    print(f"  {nm:<26} {rr:+.3f}")


# ================= WITHIN UNIT, PROPERLY =================
from collections import defaultdict
subs_arr = np.array(subs); D1 = np.asarray(D1); PCv = np.asarray(PCv)
cnt = defaultdict(int)
for s_ in subs_arr: cnt[s_] += 1
keep = np.array([cnt[s_] >= 50 for s_ in subs_arr])
S = subs_arr[keep]; P = PCv[keep]; D = D1[keep]; body_keep = [rows[i][2] for i in range(len(rows))]  # placeholder, rebuilt below
rooms_ = sorted(set(S)); rc = {r_: k for k, r_ in enumerate(rooms_)}; ridx = np.array([rc[s_] for s_ in S])
def demean(x, g, R_):
    m = np.zeros(R_); n = np.zeros(R_); np.add.at(m, g, x); np.add.at(n, g, 1); return x - (m/np.maximum(n,1))[g]
Pd = demean(P, ridx, len(rooms_)); Dd = demean(D, ridx, len(rooms_))
r_within_pooled = pearson(Pd, Dd)
print(f"\n=== POOLED within subreddit r (both demeaned by room; {len(rooms_)} rooms, {len(P)} comments) = {r_within_pooled:+.4f}")

# permutation null: D1 shuffled within room
rng = np.random.default_rng(20260903); null = []
for _ in range(200):
    Ds = Dd.copy()
    for k in range(len(rooms_)):
        ix = np.where(ridx == k)[0]; Ds[ix] = Dd[ix][rng.permutation(len(ix))]
    null.append(pearson(Pd, Ds))
null = np.array(null)
print(f"  permutation null: mean {null.mean():+.4f} sd {null.std():.4f}  (real {r_within_pooled:+.4f}, |real| beyond null in {int((np.abs(null) >= abs(r_within_pooled)).sum())}/200)")

# split half reliability of a single comment read of D1: alternate sentences
SENT = re.compile(r"(?<=[.!?])\s+")
# rebuild the kept bodies in the same order as PCv (ids/subs were appended in row order after the >=30 word floor)
kept_bodies = []
kk = 0
for _id, sub, body, ch in rows:
    f = features(body)
    if f is None: continue
    if keep[kk]: kept_bodies.append(body)
    kk += 1
assert len(kept_bodies) == len(P)
Da, Db, ok = [], [], []
for body in kept_bodies:
    sents = SENT.split(body.strip())
    if len(sents) < 4:
        w = body.split(); a_ = " ".join(w[0::2]); b_ = " ".join(w[1::2])
    else:
        a_ = " ".join(sents[0::2]); b_ = " ".join(sents[1::2])
    fa, fb = features(a_), features(b_)
    if fa is None or fb is None: ok.append(False); Da.append(0); Db.append(0); continue
    ok.append(True); Da.append(fa); Db.append(fb)
ok = np.array(ok)
def d1_of(feats):
    inv = np.array([f_[0] for f_ in feats], float); inf = np.array([f_[1] for f_ in feats], float)
    return z(inv).mean(1) - z(inf).mean(1)
Fa = [Da[i] for i in np.where(ok)[0]]; Fb = [Db[i] for i in np.where(ok)[0]]
d1a, d1b = d1_of(Fa), d1_of(Fb)
ga = ridx[ok]
r_half = pearson(demean(d1a, ga, len(rooms_)), demean(d1b, ga, len(rooms_)))
rel_D1 = 2*r_half/(1+r_half) if r_half > 0 else float("nan")
print(f"  D1 split half (alternate sentences, within room): r_half {r_half:+.3f} -> Spearman Brown reliability {rel_D1:.3f}  (n={int(ok.sum())})")

# PC1 reliability from the two reader agreement on the cross site rows (same text, two readers)
conn = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"); c = conn.cursor()   # fresh connection: the first one idles past the server timeout
c.execute("""SELECT a.char_dweb, a.char_dweb_mist, a.domain FROM the internal cross site corpus a
             JOIN an internal table s USING (id)
             WHERE a.char_dweb IS NOT NULL AND a.char_dweb_mist IS NOT NULL""")
xa, xb, xd = [], [], []
for a_, b_, d_ in c.fetchall():
    a_ = a_ if isinstance(a_, dict) else json.loads(a_); b_ = b_ if isinstance(b_, dict) else json.loads(b_)
    if all(k in a_ for k in DWEB) and all(k in b_ for k in DWEB):
        try: xa.append(pc1_of({k: float(a_[k]) for k in DWEB})); xb.append(pc1_of({k: float(b_[k]) for k in DWEB})); xd.append(d_)
        except Exception: pass
xa, xb = np.array(xa), np.array(xb); xd = np.array(xd)
xr = sorted(set(xd)); xc = {r_: k for k, r_ in enumerate(xr)}; xg = np.array([xc[d_] for d_ in xd])
rel_PC1_raw = pearson(xa, xb); rel_PC1_within = pearson(demean(xa, xg, len(xr)), demean(xb, xg, len(xr)))
print(f"  PC1 two reader agreement on {len(xa)} cross site rows: raw r {rel_PC1_raw:+.3f}, within domain {rel_PC1_within:+.3f} (used as the single read reliability, a lower bound)")

rel_PC1 = rel_PC1_within
r_corr = r_within_pooled / np.sqrt(rel_D1 * rel_PC1) if rel_D1 > 0 and rel_PC1 > 0 else float("nan")
print(f"\n=== WITHIN UNIT, DISATTENUATED: {r_within_pooled:+.4f} / sqrt({rel_D1:.3f} x {rel_PC1:.3f}) = {r_corr:+.3f}")

# item level and centroid level, disattenuated the same way, for the record
r_item = pearson(P, D)
cent_p = np.zeros(len(rooms_)); cent_d = np.zeros(len(rooms_)); n_ = np.zeros(len(rooms_))
np.add.at(cent_p, ridx, P); np.add.at(cent_d, ridx, D); np.add.at(n_, ridx, 1)
r_cent = pearson(cent_p/n_, cent_d/n_)
summary = dict(n_comments=int(len(P)), n_rooms=len(rooms_), r_item=r_item, r_within_pooled=r_within_pooled,
               perm_null_mean=float(null.mean()), perm_null_sd=float(null.std()),
               d1_split_half_r=r_half, d1_reliability=rel_D1, pc1_two_reader_r_raw=rel_PC1_raw, pc1_two_reader_r_within=rel_PC1_within,
               r_within_disattenuated=r_corr, r_item_disattenuated=r_item/np.sqrt(rel_D1*rel_PC1), r_centroid=r_cent,
               reading="the reduction as it holds inside a room, one comment against one comment, corrected for the noise of a single read on both sides")
json.dump(summary, open(f"{OUT}/within_unit.json", "w"), indent=2)
print(json.dumps(summary, indent=1)); print(f"wrote {OUT}/within_unit.json")

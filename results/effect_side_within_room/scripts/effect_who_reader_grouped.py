#!/usr/bin/env python3
"""effect_who_reader_grouped.py -- person grouped and topic grouped retest of the two READER side
legs of the WHO clause.

Paper 4B's WHO clause is the reader's disposition individuating which character moves them. Two
pieces of evidence carry it on the reader side (the legislator result is a WRITER side proxy and is
tested separately in effect_who_legislator_within_room.py):

  LEG 1  the ChangeMyView coupling fork (results/cmv_arbiter.txt, test C): a ridge fitted on the
         OP's disposition predicts that thread's winning character direction out of sample,
         held out r=+0.050, permutation p=0.0199, n=3,044 OPs. The published run uses a PLAIN
         five fold split over threads, so the SAME OP can sit in training and in test, and there
         is no topic control at all. Both are the composition confound in its usual clothes.
         Retested here under: (a) person grouped folds, every thread of an OP kept together,
         (b) topic grouped folds on a clustering of the thread titles, (c) topic demeaned
         outcomes, which is the within room contrast, (d) all three at once.

  LEG 2  the authored manipulation panel (results/causal_claude.txt): the manner advantage differs
         by the reader's disposition. Room = view, person = persona. Reported here as the between
         person and within person split, with the structural point stated plainly: disposition is
         constant inside a persona, so the interaction is a BETWEEN person contrast by
         construction and its effective sample size is the number of personas, not the number of
         judgements. Wild bootstrap over views, which fixes each view's own design.

Traps carried: person leakage is the whole point of (a); a wild bootstrap over rooms rather than a
record permutation; and the reliability of the outcome measured from the repeated judgements.
"""
import os, json, re, time
from collections import defaultdict
import numpy as np
import psycopg2
from scipy import stats

t0 = time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
D8 = ["discipline", "yielding", "novelty", "acuity", "mercuriality", "impulsivity", "candour", "sociability"]
SCORES = "the internal corpus store/cmv_winning_args/cmv_scores.jsonl"
CDIR = "the internal corpus store/cmv_winning_args/winning-args-corpus"
CAUSAL = "the internal corpus store/causal"
OUT = os.environ.get("OUT", "/home/jason/effect_confound/who_reader_grouped.json")
FOLDS = int(os.environ.get("FOLDS", "5"))
NPERM = int(os.environ.get("NPERM", "600"))
NTOPIC = int(os.environ.get("NTOPIC", "24"))
SEED = int(os.environ.get("SEED", "20260903"))
rng = np.random.default_rng(SEED)
RES = {}

# ------------------------------------------------------------------ ruler (the CMV published ruler)
PW = [l.split("=", 1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
db = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs")
cur = db.cursor()
cur.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
allc = np.array([[float(v) for v in r] for r in cur.fetchall()], float)
db.close()
CMEAN, CSTD = allc.mean(0), allc.std(0) + 1e-9
_, _, Vt = np.linalg.svd((allc - CMEAN) / CSTD, full_matrices=False); PC1 = Vt[0]
if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0: PC1 = -PC1
log(f"ruler rows={len(allc):,}")

# ================================================================== LEG 1: CMV
conv = json.load(open(f"{CDIR}/conversations.json"))
op_user = {cid: (m.get("op-userID") or "") for cid, m in conv.items()}
op_title = {cid: (m.get("op-title") or "") for cid, m in conv.items()}

args, ops = {}, {}
for line in open(SCORES):
    try: r = json.loads(line)
    except Exception: continue
    if r.get("kind") == "op" and "disp" in r: ops[r["id"]] = r["disp"]
    elif r.get("kind") == "arg" and "char" in r: args[r["id"]] = r
strata = defaultdict(lambda: {0: [], 1: []})
for a in args.values():
    for pid in (a.get("pair_ids") or []): strata[pid][a["success"]].append(a)
usable = {p: g for p, g in strata.items() if g[0] and g[1]}
log(f"CMV: scored args={len(args):,} scored OPs={len(ops):,} usable strata={len(usable):,}")

def cvec(a): return (np.array([a["char"][k] for k in DWEB], float) - CMEAN) / CSTD
def dvec(g): return np.mean([cvec(a) for a in g[1]], 0) - np.mean([cvec(a) for a in g[0]], 0)

thr_vecs = defaultdict(list)
for p, g in usable.items():
    root = next(iter({a.get("root") for a in g[1] + g[0]}))
    thr_vecs[root].append(dvec(g))
thr_dir = {t: np.mean(v, 0) for t, v in thr_vecs.items()}
thr_nstrata = {t: len(v) for t, v in thr_vecs.items()}

X, y, users, titles, threads, nstr = [], [], [], [], [], []
for t, vd in thr_dir.items():
    if t not in ops: continue
    u = op_user.get(t, "")
    X.append([ops[t][k] for k in D8]); y.append(float(vd @ PC1))
    users.append(u if u and u != "[deleted]" else f"__anon_{t}")
    titles.append(op_title.get(t, "")); threads.append(t); nstr.append(thr_nstrata[t])
X = np.array(X, float); y = np.array(y, float)
users = np.array(users, dtype=object); threads = np.array(threads, dtype=object)
nstr = np.array(nstr, int)
log(f"CMV modelling set: threads={len(y):,}  distinct OP users={len(set(users)):,}  "
    f"(threads whose OP appears more than once = {sum(1 for u in set(users) for _ in [0] if np.sum(users==u)>1 and not u.startswith('__anon_'))})")

# a topic room: TF-IDF over the CMV thread titles, k means
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
clean = [re.sub(r"^\s*cmv[:\s-]*", "", s, flags=re.I) for s in titles]
tf = TfidfVectorizer(max_features=4000, stop_words="english", min_df=3)
Tm = tf.fit_transform(clean)
km = KMeans(n_clusters=NTOPIC, n_init=8, random_state=SEED).fit(Tm)
topic = km.labels_
log(f"CMV topic rooms: {NTOPIC} clusters over {Tm.shape[0]} thread titles "
    f"(sizes {np.bincount(topic).min()}..{np.bincount(topic).max()})")

def ridge_oos(Xf, yf, groups, folds=FOLDS, lam=1.0, gen=None):
    """out of sample pearson r, folds formed over GROUPS so no group is split."""
    gen = gen or rng
    gs = np.array(sorted(set(groups)), dtype=object)
    gen.shuffle(gs)
    assign = {g: i % folds for i, g in enumerate(gs)}
    fold = np.array([assign[g] for g in groups])
    pred = np.zeros(len(yf))
    for f in range(folds):
        te = np.flatnonzero(fold == f); tr = np.flatnonzero(fold != f)
        if len(te) == 0 or len(tr) < 20: continue
        Xt = np.c_[np.ones(len(tr)), Xf[tr]]
        w = np.linalg.solve(Xt.T @ Xt + lam * np.eye(Xt.shape[1]), Xt.T @ yf[tr])
        pred[te] = np.c_[np.ones(len(te)), Xf[te]] @ w
    ok = pred != 0
    if ok.sum() < 50: return float("nan")
    return float(stats.pearsonr(pred[ok], yf[ok])[0])

def perm_p(Xf, yf, groups, shuffle_within=None):
    """null: permute the DISPOSITION rows, keeping the fold structure, so the null shares the
       grouping. If shuffle_within is given, permute only inside that block (a within room null)."""
    obs = ridge_oos(Xf, yf, groups)
    null = np.empty(NPERM)
    for b in range(NPERM):
        idx = np.arange(len(yf))
        if shuffle_within is None:
            idx = rng.permutation(idx)
        else:
            for blk in set(shuffle_within):
                m = np.flatnonzero(shuffle_within == blk)
                idx[m] = rng.permutation(m)
        null[b] = ridge_oos(Xf[idx], yf, groups)
    p = float((np.sum(null >= obs) + 1) / (NPERM + 1))
    return obs, float(np.nanmean(null)), p

RES["cmv"] = dict(threads=int(len(y)), op_users=int(len(set(users))), topics=NTOPIC)
log("\n--- CMV leg: does the OP's disposition predict the thread's winning character? ---")

# (0) the published design: plain folds over threads, no grouping, no topic control
obs0, n0, p0 = perm_p(X, y, np.array(threads, dtype=object))
log(f"  (0) PUBLISHED design, plain folds over threads      : held out r={obs0:+.4f}  null {n0:+.4f}  p={p0:.4f}")

# (1) PERSON grouped: every thread of an OP kept in one fold
obs1, n1, p1 = perm_p(X, y, users)
log(f"  (1) PERSON grouped folds (no OP split across folds) : held out r={obs1:+.4f}  null {n1:+.4f}  p={p1:.4f}")

# (2) TOPIC grouped: whole topic clusters held out
obs2, n2, p2 = perm_p(X, y, topic.astype(object))
log(f"  (2) TOPIC grouped folds (whole topic rooms held out): held out r={obs2:+.4f}  null {n2:+.4f}  p={p2:.4f}")

# (3) WITHIN ROOM: outcome demeaned inside its topic room, person grouped folds
ydm = y.copy()
for k in set(topic):
    m = np.flatnonzero(topic == k); ydm[m] -= ydm[m].mean()
obs3, n3, p3 = perm_p(X, ydm, users)
log(f"  (3) WITHIN topic room (outcome demeaned) + person grouped: held out r={obs3:+.4f}  null {n3:+.4f}  p={p3:.4f}")

# (4) BETWEEN room: how much of the raw signal is the topic room level?
tm_y = np.array([y[topic == k].mean() for k in range(NTOPIC)])
tm_X = np.array([X[topic == k].mean(0) for k in range(NTOPIC)])
between_share = float(sum((topic == k).sum() * (tm_y[k] - y.mean()) ** 2 for k in range(NTOPIC))
                      / max(((y - y.mean()) ** 2).sum(), 1e-12))
log(f"  (4) share of the winning direction variance that is BETWEEN topic rooms = {100*between_share:.1f}%")
RES["cmv"]["designs"] = dict(published=dict(r=obs0, null=n0, p=p0),
                             person_grouped=dict(r=obs1, null=n1, p=p1),
                             topic_grouped=dict(r=obs2, null=n2, p=p2),
                             within_topic_person_grouped=dict(r=obs3, null=n3, p=p3),
                             between_topic_share=between_share)

# repeat the whole thing over several random fold draws so the answer is not one lucky split
log("  stability over 20 random fold draws (person grouped):")
reps = [ridge_oos(X, y, users, gen=np.random.default_rng(SEED + i)) for i in range(20)]
reps3 = [ridge_oos(X, ydm, users, gen=np.random.default_rng(SEED + i)) for i in range(20)]
log(f"     raw outcome        r = {np.mean(reps):+.4f}  (sd {np.std(reps):.4f}, min {np.min(reps):+.4f}, max {np.max(reps):+.4f})")
log(f"     topic demeaned     r = {np.mean(reps3):+.4f}  (sd {np.std(reps3):.4f}, min {np.min(reps3):+.4f}, max {np.max(reps3):+.4f})")
RES["cmv"]["stability"] = dict(raw_mean=float(np.mean(reps)), raw_sd=float(np.std(reps)),
                               dm_mean=float(np.mean(reps3)), dm_sd=float(np.std(reps3)))

# ================================================================== LEG 2: the authored panel
log("\n--- panel leg: does the manner advantage depend on the reader's disposition? ---")
RES["panel"] = {}
for src, name in [(f"{CAUSAL}/causal_persuade.jsonl", "7B panel"),
                  (f"{CAUSAL}/claude_persuade.jsonl", "frontier panel")]:
    if not os.path.exists(src): continue
    rows = [json.loads(l) for l in open(src) if l.strip()]
    views = sorted({r["view_id"] for r in rows}); personas = sorted({r["persona"] for r in rows})
    log(f"  {name}: {len(rows)} judgements, {len(views)} views, {len(personas)} personas")
    # cell means
    cell = defaultdict(list)
    for r in rows: cell[(r["view_id"], r["persona"], r["variant"])].append(float(r["persuaded"]))
    cell = {k: float(np.mean(v)) for k, v in cell.items()}
    # manner advantage per (view, persona): mean(C,D) - mean(A,B)
    adv = {}
    for v in views:
        for p in personas:
            m = [cell.get((v, p, x)) for x in ("C", "D")]
            mt = [cell.get((v, p, x)) for x in ("A", "B")]
            if None in m or None in mt: continue
            adv[(v, p)] = float(np.mean(m) - np.mean(mt))
    stabhi = [p for p in personas if p.startswith("stabHi")]
    stablo = [p for p in personas if p.startswith("stabLo")]
    plashi = [p for p in personas if p.endswith("plasHi")]
    plaslo = [p for p in personas if p.endswith("plasLo")]
    def contrast(hi, lo):
        d = []
        for v in views:
            a = [adv[(v, p)] for p in hi if (v, p) in adv]
            b = [adv[(v, p)] for p in lo if (v, p) in adv]
            if a and b: d.append(np.mean(a) - np.mean(b))
        return np.array(d, float)
    out = {}
    for lbl, (hi, lo) in [("stability", (stabhi, stablo)), ("plasticity", (plashi, plaslo))]:
        d = contrast(hi, lo)
        if len(d) < 3: continue
        t, p = stats.ttest_1samp(d, 0.0)
        # wild bootstrap over VIEWS: each view keeps its own scale, sign flipped
        tb = []
        for _ in range(4000):
            s = d - d.mean()                       # restricted null: no interaction
            star = s * rng.choice([-1.0, 1.0], size=len(d))
            tb.append(stats.ttest_1samp(star, 0.0).statistic)
        tb = np.array(tb)
        pw = float((np.sum(np.abs(tb) >= abs(t)) + 1) / (len(tb) + 1))
        log(f"    {lbl} interaction on the manner advantage: per view mean {d.mean():+.4f} "
            f"(view paired t={t:+.2f} p={p:.4f}, wild bootstrap over {len(d)} views p={pw:.4f})")
        out[lbl] = dict(mean=float(d.mean()), t=float(t), p=float(p), p_wild=pw, n_views=int(len(d)),
                        n_persona_clusters_hi=len(hi), n_persona_clusters_lo=len(lo))
    # the balance main effect for comparison, view paired AND within persona
    bal = {}
    for v in views:
        for p in personas:
            b = [cell.get((v, p, x)) for x in ("A", "C")]
            q = [cell.get((v, p, x)) for x in ("B", "D")]
            if None in b or None in q: continue
            bal[(v, p)] = float(np.mean(b) - np.mean(q))
    bv = np.array([np.mean([bal[(v, p)] for p in personas if (v, p) in bal]) for v in views], float)
    tb_, pb_ = stats.ttest_1samp(bv, 0.0)
    # within persona: each persona is its own room, does balance still win inside it?
    per_persona = {p: np.array([bal[(v, p)] for v in views if (v, p) in bal], float) for p in personas}
    wp = {p: (float(a.mean()), int(len(a)), float(stats.ttest_1samp(a, 0.0).pvalue) if len(a) > 2 else float("nan"))
          for p, a in per_persona.items() if len(a) >= 3}
    log(f"    balance advantage, view paired across personas: {bv.mean():+.4f} t={tb_:+.2f} p={pb_:.4f}")
    for p, (m, n, pv) in sorted(wp.items()):
        log(f"       within persona {p:<16} balance advantage {m:+.4f} (n={n} views, p={pv:.4f})")
    out["balance_main"] = dict(mean=float(bv.mean()), t=float(tb_), p=float(pb_),
                               within_persona={k: dict(mean=v[0], n=v[1], p=v[2]) for k, v in wp.items()})
    out["structure"] = dict(judgements=len(rows), views=len(views), personas=len(personas),
                            note="disposition is constant inside a persona, so the WHO interaction "
                                 "is a between person contrast by construction; the effective sample "
                                 "size for it is the persona count, not the judgement count")
    RES["panel"][name] = out

json.dump(RES, open(OUT, "w"), indent=1)
log(f"\nwrote {OUT}")

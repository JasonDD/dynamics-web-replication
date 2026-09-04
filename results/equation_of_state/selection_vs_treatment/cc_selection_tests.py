#!/usr/bin/env python3
"""cc_selection_tests.py -- SELECTION against TREATMENT for the room term, on the three part model's held out residuals.

B1 within person across rooms: selection cancels within a person, a room treatment does not.
B4 does the state tail beyond the plane predict which rooms a person is in (homophily on the tail = selection).
Built from the competitor test's data path so folds, records and models are identical. (original header follows)

cc_competitor_test.py -- the COMPETITOR TEST for the unification claim (Paper 4).

Question. Does an assumption free, high capacity model find MORE structure in how disposition (P)
and room (S) produce character (C) than the constrained architecture the series settled on, once
it is judged on persons it has never seen? If it does, the "unified geometry" is a story told
about a fit. If the constrained model matches it with a small fraction of the moving parts, that
is the evidence unification needs. A draw is a win for the constrained model.

The fair fight. The constrained model here is the UPDATED architecture, not the old straight line
same everywhere one which today's tests already showed to be incomplete:
    C_ir = g(P_i) W  +  P_i D_r  +  s_r  +  e
    g     curved (quadratic) disposition map, pooled over rooms
    D_r   room specific slope deviation, ridge shrunk toward zero (the rotation, blend weight
          chosen by inner cross validation on training persons only)
    s_r   room state shift, constrained to a rank two subspace across rooms
Everything is fitted on eight standardised character axes so that "rank two" means something.

Competitors, all judged on the same held out persons:
    M0  room mean only (the null every P model has to beat)
    M1  invariant linear     C = P W + s_r          (the old architecture, for the record)
    M1c invariant curved     C = g(P) W + s_r
    M2  updated (ours)       as above, rank two state        <- the model under test
    M2f updated, full rank state (ablation of the rank two constraint)
    M3  separate             unshrunk per room slope and intercept (the overfit pole)
    M4  flexible gradient boosted trees on [P, room profile from TRAINING persons only]
    M5  flexible multilayer perceptron on the same inputs
    M6  the same perceptron given room identity as a one hot block

Held out design. Persons are assigned to K folds (person grouped: a person appears in exactly one
fold across every room, so no person leakage). Every room appears in training and test with
different persons, which is what lets every model learn room parameters and lets the flexible
models learn arbitrary P x room interactions. Test records whose room has fewer than ROOMMIN_TRAIN
training persons are dropped for every model alike.

Criterion, fixed before the run (see PREREGISTRATION.md next to the results):
    gain(M) = 1 - SSE_M / SSE_M0   pooled over the eight axes, on held out persons
    Delta   = gain(M4 or M5, whichever is larger) - gain(M2)
    Room block bootstrap over test rooms for the confidence interval on Delta.
Power calibration by injection: an unmodelled per room P1*P2 interaction of size TAU (SD units of
C) is added to C and the whole thing rerun; the flexible model must show it (Delta rises) or the
verdict is "uninformative", not "pass".

Aggregate, no keys, no names, analysis only.
"""
import os, sys, json, time
import numpy as np
import scipy.sparse as sp
import psycopg2
from collections import Counter

t0 = time.time()
def log(*a):
    print(f"[{time.time()-t0:7.1f}s]", *a, flush=True)

CHAR = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
D8   = ["discipline","yielding","novelty","acuity","mercuriality","impulsivity","candour","sociability"]

TABLE     = os.environ.get("TABLE", "crosssite_authorship")
PERSONCOL = os.environ.get("PERSONCOL", "ident")
ROOMCOL   = os.environ.get("ROOMCOL", "domain")
DISPCOL   = os.environ.get("DISPCOL", "disp_d8")
CHARCOL   = os.environ.get("CHARCOL", "char_dweb")
MINPERS   = int(os.environ.get("MINPERS", "10"))       # persons a room needs to enter at all
ROOMMIN_TRAIN = int(os.environ.get("ROOMMIN_TRAIN", "5"))  # training persons a room needs for its test rows to count
K         = int(os.environ.get("KFOLD", "5"))
NBOOT     = int(os.environ.get("NBOOT", "500"))
TAUS      = [float(x) for x in os.environ.get("TAUS", "0,0.06,0.15").split(",")]
LAMBDAS   = [float(x) for x in os.environ.get("LAMBDAS", "0.3,1,3,10,30,100,1e9").split(",")]
STATE_RANK= int(os.environ.get("STATE_RANK", "2"))
SEED      = int(os.environ.get("SEED", "20260903"))
OUT       = os.environ.get("OUT", "/tmp/cc_selection_tests.json")
LAMBDA    = float(os.environ.get("LAMBDA", "30"))
NPERM     = int(os.environ.get("NPERM", "200"))
INJECT    = os.environ.get("INJECT", "profile")  # profile: sign from the room mean disposition (visible to a
                                                  # profile fed model); room: random sign per room (needs identity)
THREADS   = int(os.environ.get("THREADS", "16"))
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, str(THREADS))   # small batch MLP fits thrash above ~16 BLAS threads

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.neural_network import MLPRegressor

rng = np.random.default_rng(SEED)

PW = [l.split("=",1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
DSN = f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"

def obj(x):
    return x if isinstance(x, dict) else (json.loads(x) if x else None)

# ------------------------------------------------------------------ pull
db = psycopg2.connect(DSN); cur = db.cursor()
log(f"pulling rows (table={TABLE} person={PERSONCOL} room={ROOMCOL} disp={DISPCOL} char={CHARCOL}) ...")
cur.execute(f"""SELECT {PERSONCOL}, {ROOMCOL}, {DISPCOL}, {CHARCOL}
                FROM the internal schema.{TABLE}
                WHERE {DISPCOL} IS NOT NULL AND {CHARCOL} IS NOT NULL
                ORDER BY {PERSONCOL}, {ROOMCOL}, id""")
i_d8 = {a: k for k, a in enumerate(D8)}
persons, rooms, P_row, C_row = [], [], [], []
for ident, room, dd, cw in cur:
    dd = obj(dd); cw = obj(cw)
    if not isinstance(dd, dict) or not isinstance(cw, dict): continue
    if any(a not in cw for a in CHAR) or any(a not in dd for a in D8): continue
    if not ident or not room: continue
    try:
        d = np.array([float(dd[a]) for a in D8], float)
        c = np.array([float(cw[a]) for a in CHAR], float)
    except (TypeError, ValueError):
        continue
    plas = d[i_d8["novelty"]] + d[i_d8["sociability"]]
    stab = d[i_d8["discipline"]] + d[i_d8["yielding"]] - d[i_d8["mercuriality"]]
    persons.append(ident); rooms.append(room); P_row.append((plas, stab)); C_row.append(c)
db.close()
P_row = np.array(P_row, float); C_row = np.array(C_row, float)
log(f"usable rows={len(P_row):,}  persons={len(set(persons)):,}  rooms={len(set(rooms)):,}")

# ------------------------------------------------------------------ person room records
key = {}
for n, (i, r) in enumerate(zip(persons, rooms)):
    key.setdefault((i, r), []).append(n)
rec_person, rec_room, recP, recC, rec_n = [], [], [], [], []
for (i, r), ix in key.items():
    ix = np.asarray(ix)
    rec_person.append(i); rec_room.append(r); rec_n.append(len(ix))
    recP.append(P_row[ix].mean(0)); recC.append(C_row[ix].mean(0))
recP = np.array(recP, float); recC = np.array(recC, float); rec_n = np.array(rec_n, int)
rec_person = np.array(rec_person, dtype=object); rec_room = np.array(rec_room, dtype=object)
npers = Counter(rec_room)
keep = np.array([npers[r] >= MINPERS for r in rec_room])
recP, recC, rec_n = recP[keep], recC[keep], rec_n[keep]
rec_person, rec_room = rec_person[keep], rec_room[keep]
ROOMS = sorted(set(rec_room)); RCODE = {r: k for k, r in enumerate(ROOMS)}
room = np.array([RCODE[r] for r in rec_room], int)
PERS = sorted(set(rec_person)); PCODE = {p: k for k, p in enumerate(PERS)}
pers = np.array([PCODE[p] for p in rec_person], int)
N, R, NP = len(recP), len(ROOMS), len(PERS)
log(f"rooms with >={MINPERS} persons: {R:,}   person room records: {N:,}   distinct persons: {NP:,}"
    f"   median persons per room {int(np.median(list(Counter(room).values())))}")

Z = (recP - recP.mean(0)) / (recP.std(0) + 1e-12)          # P in SD units
C0 = (recC - recC.mean(0)) / (recC.std(0) + 1e-12)         # C in SD units, eight axes
Q = C0.shape[1]

def gfeat(Zx):
    """curved disposition map: linear + quadratic + cross, standardised on the full sample."""
    return np.column_stack([Zx[:,0], Zx[:,1], Zx[:,0]**2, Zx[:,1]**2, Zx[:,0]*Zx[:,1]])
G = gfeat(Z); Gmu, Gsd = G.mean(0), G.std(0) + 1e-12; G = (G - Gmu) / Gsd

# person grouped folds
perm = rng.permutation(NP); fold_of_person = np.empty(NP, int); fold_of_person[perm] = np.arange(NP) % K
fold = fold_of_person[pers]

# ------------------------------------------------------------------ helpers
def room_means(vals, rm, R, min_n=1):
    s = np.zeros((R, vals.shape[1])); n = np.zeros(R)
    np.add.at(s, rm, vals); np.add.at(n, rm, 1)
    m = s / np.maximum(n, 1)[:, None]
    return m, n

def fit_fe(X, Y, rm, R):
    """within room OLS: demean X and Y by room, least squares, returns W and room intercepts."""
    Xm, n = room_means(X, rm, R); Ym, _ = room_means(Y, rm, R)
    Xd = X - Xm[rm]; Yd = Y - Ym[rm]
    W, *_ = np.linalg.lstsq(Xd, Yd, rcond=None)
    s = Ym - Xm @ W
    return W, s, n

def truncate_rank(S, n, rank):
    """rank constrained room state: weighted SVD of the R x Q state matrix, keep `rank` directions."""
    if rank <= 0 or rank >= S.shape[1]: return S
    w = np.sqrt(np.maximum(n, 1))[:, None]
    mu = (S * w**2).sum(0) / (w**2).sum()
    U, sv, Vt = np.linalg.svd((S - mu) * w, full_matrices=False)
    return mu + ((U[:, :rank] * sv[:rank]) @ Vt[:rank]) / w

def room_dev_ridge(Xd, Rd, rm, R, lam):
    """per room ridge slope deviation on within room demeaned design/residual."""
    p, q = Xd.shape[1], Rd.shape[1]
    D = np.zeros((R, p, q))
    order = np.argsort(rm, kind="stable"); rm_s = rm[order]
    bounds = np.searchsorted(rm_s, np.arange(R + 1))
    I = np.eye(p)
    for r in range(R):
        ix = order[bounds[r]:bounds[r+1]]
        if len(ix) < 2: continue
        x = Xd[ix]; y = Rd[ix]
        D[r] = np.linalg.solve(x.T @ x + lam * I, x.T @ y)
    return D

class Updated:
    """g(P) W + P D_r + s_r with ridge shrunk D_r and rank constrained s_r."""
    def __init__(self, curved=True, lam=None, rank=0, lambdas=LAMBDAS):
        self.curved, self.lam, self.rank, self.lambdas = curved, lam, rank, lambdas
    def _X(self, i): return G[i] if self.curved else Z[i]
    def _fit_core(self, i, Y, lam):
        X = self._X(i); rm = room[i]
        W, s, n = fit_fe(X, Y, rm, R)
        Xm, _ = room_means(X, rm, R); Ym, _ = room_means(Y, rm, R)
        Zd = Z[i] - room_means(Z[i], rm, R)[0][rm]
        Rd = (Y - Ym[rm]) - (X - Xm[rm]) @ W
        D = room_dev_ridge(Zd, Rd, rm, R, lam) if lam < 1e8 else np.zeros((R, 2, Y.shape[1]))
        # state: room mean of what is left once the pooled map and the deviation are in
        Zm, _ = room_means(Z[i], rm, R)
        s = Ym - Xm @ W - np.einsum("rp,rpq->rq", Zm, D)
        s = truncate_rank(s, n, self.rank)
        return dict(W=W, D=D, s=s, n=n, Zm=Zm)
    def fit(self, i, Y):
        if self.lam is None:                       # inner CV over persons in the training set
            inner = fold_of_person[pers[i]] ; best = None
            for lam in self.lambdas:
                sse = 0.0
                for f in range(K):
                    tr, te = i[inner != f], i[inner == f]
                    m = self._fit_core(tr, Y[inner != f], lam)
                    ok = m["n"][room[te]] >= ROOMMIN_TRAIN
                    sse += float(((Y[inner == f][ok] - self._pred(m, te[ok]))**2).sum())
                if best is None or sse < best[0]: best = (sse, lam)
            self.lam_ = best[1]
        else:
            self.lam_ = self.lam
        self.m_ = self._fit_core(i, Y, self.lam_)
        self.k_ = self.m_["W"].size + (R * 2 * Y.shape[1] if self.lam_ < 1e8 else 0) + R * Y.shape[1]
        return self
    def _pred(self, m, i):
        X = self._X(i); rm = room[i]
        return X @ m["W"] + np.einsum("np,npq->nq", Z[i], m["D"][rm]) + m["s"][rm]
    def predict(self, i): return self._pred(self.m_, i)
    def train_n(self): return self.m_["n"]

class RoomMean:
    def fit(self, i, Y):
        self.s_, self.n_ = room_means(Y, room[i], R); self.k_ = R * Y.shape[1]; return self
    def predict(self, i): return self.s_[room[i]]
    def train_n(self): return self.n_

def room_profile(i_train, Y_train, i_query, loo):
    """features a flexible model may use about the room: mean C and mean P of TRAINING persons,
       leave one out for training rows so a row never sees its own target, plus log room size."""
    rm_t = room[i_train]
    sC = np.zeros((R, Q)); sP = np.zeros((R, 2)); n = np.zeros(R)
    np.add.at(sC, rm_t, Y_train); np.add.at(sP, rm_t, Z[i_train]); np.add.at(n, rm_t, 1)
    rq = room[i_query]
    if loo:
        nn = np.maximum(n[rq] - 1, 1)[:, None]
        mC = (sC[rq] - Y_train) / nn; mP = (sP[rq] - Z[i_query]) / nn
    else:
        nn = np.maximum(n[rq], 1)[:, None]
        mC = sC[rq] / nn; mP = sP[rq] / nn
    return np.column_stack([Z[i_query], G[i_query][:, 2:], mC, mP, np.log1p(n[rq])])

def room_onehot(i):
    """room identity as a one hot block, so a flexible model can learn anything tied to the room itself."""
    return sp.csr_matrix((np.ones(len(i), np.float32), (np.arange(len(i)), room[i])), shape=(len(i), R))

class Flexible:
    def __init__(self, kind): self.kind = kind
    def fit(self, i, Y):
        X = room_profile(i, Y, i, loo=True)
        self.i_, self.Y_ = i, Y
        self.mu_, self.sd_ = X.mean(0), X.std(0) + 1e-9
        if self.kind == "mlp_room":
            Xs = sp.hstack([sp.csr_matrix((X - self.mu_)/self.sd_), room_onehot(i)]).tocsr()
            self.models_ = [MLPRegressor(hidden_layer_sizes=(64, 64), alpha=1e-3, max_iter=300,
                                early_stopping=True, validation_fraction=0.15, n_iter_no_change=15,
                                random_state=SEED).fit(Xs, Y)]
            self.k_ = int(sum(c.size for c in self.models_[0].coefs_))
            self.n_ = room_means(Y, room[i], R)[1]
            return self
        if self.kind == "gbm":
            self.models_ = [HistGradientBoostingRegressor(max_iter=600, learning_rate=0.05,
                                max_leaf_nodes=31, min_samples_leaf=20, l2_regularization=1.0,
                                early_stopping=True, validation_fraction=0.15, n_iter_no_change=30,
                                random_state=SEED).fit(X, Y[:, q]) for q in range(Q)]
            self.k_ = int(sum(m.n_iter_ * 31 for m in self.models_))
        else:
            self.models_ = [MLPRegressor(hidden_layer_sizes=(64, 64), alpha=1e-3, max_iter=300,
                                early_stopping=True, validation_fraction=0.15, n_iter_no_change=15,
                                random_state=SEED).fit((X - self.mu_)/self.sd_, Y)]
            self.k_ = int(sum(c.size for c in self.models_[0].coefs_))
        self.n_ = room_means(Y, room[i], R)[1]
        return self
    def predict(self, i):
        X = room_profile(self.i_, self.Y_, i, loo=False)
        if self.kind == "mlp_room": X = sp.hstack([sp.csr_matrix((X - self.mu_)/self.sd_), room_onehot(i)]).tocsr()
        if self.kind == "gbm":
            return np.column_stack([m.predict(X) for m in self.models_])
        if self.kind == "mlp_room":
            return self.models_[0].predict(X)
        return self.models_[0].predict((X - self.mu_)/self.sd_)
    def train_n(self): return self.n_


# ------------------------------------------------------------------ held out residuals of the three part model
log("fitting the three part model per fold, collecting held out residuals and per fold room states ...")
E = np.full((N, Q), np.nan); S_fold = np.zeros((K, R, Q)); n_fold = np.zeros((K, R)); OKREC = np.zeros(N, bool)
for f in range(K):
    tr, te = np.where(fold != f)[0], np.where(fold == f)[0]
    m = Updated(curved=True, lam=LAMBDA, rank=0).fit(tr, C0[tr])
    ok = m.train_n()[room[te]] >= ROOMMIN_TRAIN; te = te[ok]
    E[te] = C0[te] - m.predict(te); OKREC[te] = True
    S_fold[f] = m.m_["s"]; n_fold[f] = m.m_["n"]
    log(f"  fold {f}: {len(te):,} held out records")
results = dict(table=TABLE, rooms=R, records=N, persons=NP, kfold=K, seed=SEED, lam=LAMBDA)

# ------------------------------------------------------------------ B1: within person, across rooms
byp = {}
for n in np.where(OKREC)[0]: byp.setdefault(pers[n], []).append(n)
multi = {p_: v for p_, v in byp.items() if len(v) >= 2}
pa, pb, pp = [], [], []
for p_, recs in multi.items():
    for x in recs:
        for y in recs:
            if x != y: pa.append(x); pb.append(y); pp.append(p_)
pa, pb, pp = np.array(pa), np.array(pb), np.array(pp)
D = E[pa] - E[pb]
log(f"B1: {len(multi):,} persons in 2+ rooms, {len(pa):,} ordered room pairs")

# residual variance components: person against room against remainder (one way ICCs on the held out residual)
def icc(groups, X):
    """share of variance between groups, pooled over axes (one way, unbalanced, plain moments)."""
    tot = X.var(0).sum()
    gm = {}; 
    for gid in np.unique(groups): gm[gid] = X[groups == gid].mean(0)
    between = np.array([gm[gid] for gid in groups]).var(0).sum()
    return float(between / tot) if tot > 0 else float("nan")
rec = np.where(OKREC)[0]
results["B1_residual_variance_shares"] = dict(
    person_share=icc(pers[rec], E[rec]), room_share=icc(room[rec], E[rec]),
    person_share_multiroom_only=icc(pers[np.isin(pers, list(multi))&OKREC], E[np.isin(pers, list(multi))&OKREC]),
    note="room share is near zero by construction (the shift is fitted per room); person share is the unobserved person component that selection would carry")

def ridge_fe_heldout(A, B, target, groups, lam=None, nperm=0, seed=0):
    """target ~ v[A] - v[B] (antisymmetric room design) by the normal equations built from pair counts,
       ridge, person grouped folds, lam by inner grid. Null: the target rows permuted with a random sign,
       which breaks the link between a pair's rooms and its difference while keeping the design."""
    gid = np.unique(groups); gp = np.random.default_rng(seed).permutation(len(gid)); gf = {g_: k % K for k, g_ in zip(gp, gid)}
    gfold = np.array([gf[g_] for g_ in groups])
    def solve(a, b, y, lam_):
        # X'X = diag(deg) - counts(a,b) - counts(b,a);  X'y = sum_{+a} y - sum_{-b} y
        XtX = np.zeros((R, R)); deg = np.bincount(a, minlength=R) + np.bincount(b, minlength=R)
        np.add.at(XtX, (a, b), -1.0); np.add.at(XtX, (b, a), -1.0); XtX[np.arange(R), np.arange(R)] += deg + lam_
        Xty = np.zeros((R, y.shape[1])); np.add.at(Xty, a, y); np.add.at(Xty, b, -y)
        return np.linalg.solve(XtX, Xty)
    def run(a, b, y, lam_):
        sse = sst = 0.0
        for f in range(K):
            tr, te = gfold != f, gfold == f
            W = solve(a[tr], b[tr], y[tr], lam_); pred = W[a[te]] - W[b[te]]
            sse += float(((y[te] - pred)**2).sum()); sst += float((y[te]**2).sum())
        return float(1 - sse/sst)
    if lam is None:
        grid = [1.0, 10.0, 100.0, 1000.0]; lam = max(grid, key=lambda l_: run(A, B, target, l_))
    real = run(A, B, target, lam); null = []
    g = np.random.default_rng(seed + 1)
    for _ in range(nperm):
        pm = g.permutation(len(target)); sg = g.choice([-1.0, 1.0], size=len(target))[:, None]
        null.append(run(A, B, target[pm]*sg, lam))
    return real, null, lam
r2, null, lam_b1 = ridge_fe_heldout(room[pa], room[pb], D, pp, lam=None, nperm=min(NPERM, 50), seed=SEED)
results["B1_room_pair_predicts_within_person_difference"] = dict(
    heldout_r2=r2, lam=lam_b1, null_mean=float(np.mean(null)) if null else None, null_p95=float(np.percentile(null, 95)) if null else None,
    p=float((np.sum(np.array(null) >= r2) + 1) / (len(null) + 1)) if null else None,
    reading="treatment: the room pair predicts how the same person's residual differs between rooms (r2 above the null); selection: it does not (r2 at the null), because a person level unobserved cancels within the person")
log(f"B1 room pair -> within person residual difference: held out r2 {r2:+.4f}  null mean {np.mean(null):+.4f} p95 {np.percentile(null,95):+.4f}")
json.dump(results, open(OUT, "w"), indent=1)

# ------------------------------------------------------------------ B4: the tail predicts membership?
log("B4: does a person's residual on the state tail predict the tail coordinate of the rooms they are in ...")
xs_tail, ys_tail, xs_plane, ys_plane, grp = [], [], [], [], []
for f in range(K):
    S = S_fold[f]; w = np.sqrt(np.maximum(n_fold[f], 1))[:, None]; mu = (S*w**2).sum(0)/(w**2).sum()
    U, sv, Vt = np.linalg.svd((S - mu)*w, full_matrices=False)
    U2, Ut = Vt[:2].T, Vt[2:].T                       # plane (8x2) and tail (8x6)
    T_plane, T_tail = (S - mu) @ U2, (S - mu) @ Ut    # room coordinates
    sel = (fold[pa] == f)                              # pairs whose person is held out in this fold
    a, b, p_ = pa[sel], pb[sel], pp[sel]
    xs_tail.append(E[a] @ Ut); ys_tail.append(T_tail[room[b]])
    xs_plane.append(E[a] @ U2); ys_plane.append(T_plane[room[b]]); grp.append(p_)
Xt, Yt, Xp, Yp, Gp = map(np.concatenate, (xs_tail, ys_tail, xs_plane, ys_plane, grp))
def cv_r2(X, Y, groups, lam=1.0, seed=0):
    gid = np.unique(groups); gp = np.random.default_rng(seed).permutation(len(gid)); gf = {g: k % K for k, g in zip(gp, gid)}
    gfold = np.array([gf[g] for g in groups]); sse = sst = 0.0
    for f in range(K):
        tr, te = gfold != f, gfold == f
        Xtr = np.column_stack([np.ones(tr.sum()), X[tr]]); W = np.linalg.solve(Xtr.T @ Xtr + lam*np.eye(Xtr.shape[1]), Xtr.T @ Y[tr])
        pred = np.column_stack([np.ones(te.sum()), X[te]]) @ W
        sse += float(((Y[te] - pred)**2).sum()); sst += float(((Y[te] - Y[tr].mean(0))**2).sum())
    return float(1 - sse/sst)
def perm_null(X, Y, groups, nperm, seed):
    g = np.random.default_rng(seed); out = []
    for _ in range(nperm):
        # permute the room coordinate across ROOMS (not records) so room size structure is kept
        out.append(cv_r2(X, Y[g.permutation(len(Y))], groups, seed=seed))
    return out
r2_tail = cv_r2(Xt, Yt, Gp, seed=SEED); null_tail = perm_null(Xt, Yt, Gp, min(NPERM, 100), SEED + 3)
r2_plane = cv_r2(Xp, Yp, Gp, seed=SEED); null_plane = perm_null(Xp, Yp, Gp, min(NPERM, 100), SEED + 4)
results["B4_tail_predicts_membership"] = dict(
    pairs=int(len(Xt)), tail_heldout_r2=r2_tail, tail_null_mean=float(np.mean(null_tail)), tail_null_p95=float(np.percentile(null_tail, 95)),
    tail_p=float((np.sum(np.array(null_tail) >= r2_tail) + 1)/(len(null_tail)+1)),
    plane_heldout_r2=r2_plane, plane_null_mean=float(np.mean(null_plane)), plane_null_p95=float(np.percentile(null_plane, 95)),
    plane_p=float((np.sum(np.array(null_plane) >= r2_plane) + 1)/(len(null_plane)+1)),
    reading="a person's residual on the tail in one room predicting the tail coordinate of their OTHER rooms is homophily on the tail: the tail carries who a room selects. The plane row is the comparison on the dominant axes.")
log(f"B4 tail: held out r2 {r2_tail:+.4f} null {np.mean(null_tail):+.4f} (p95 {np.percentile(null_tail,95):+.4f}) p={results['B4_tail_predicts_membership']['tail_p']:.3f}")
log(f"B4 plane: held out r2 {r2_plane:+.4f} null {np.mean(null_plane):+.4f} (p95 {np.percentile(null_plane,95):+.4f}) p={results['B4_tail_predicts_membership']['plane_p']:.3f}")
json.dump(results, open(OUT, "w"), indent=1)
log(f"written {OUT}")

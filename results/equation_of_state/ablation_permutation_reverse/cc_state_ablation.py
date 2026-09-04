#!/usr/bin/env python3
"""cc_state_ablation.py -- PERMUTATION NULL, ABLATION and REVERSE PREDICTION for the three part model.

Built from the competitor test's data path so the folds, records and models are identical.
(original header follows)

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
OUT       = os.environ.get("OUT", "/tmp/cc_state_ablation.json")
NPERM     = int(os.environ.get("NPERM", "20"))
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


# ------------------------------------------------------------------ the three tests
def heldout_gain(model_fn, Y, Xsel=None):
    """person grouped K fold; gain over the room mean pooled over axes; also per fold."""
    sse_m = 0.0; sse_0 = 0.0
    for f in range(K):
        tr, te = np.where(fold != f)[0], np.where(fold == f)[0]
        m0 = RoomMean().fit(tr, Y[tr]); ok = m0.train_n()[room[te]] >= ROOMMIN_TRAIN; te = te[ok]
        m = model_fn().fit(tr, Y[tr])
        sse_m += float(((Y[te] - m.predict(te))**2).sum()); sse_0 += float(((Y[te] - m0.predict(te))**2).sum())
    return float(1 - sse_m/sse_0)

results = dict(table=TABLE, rooms=R, records=N, persons=NP, kfold=K, seed=SEED)
three_part = lambda: Updated(curved=True, lam=None, rank=0)      # the secondary model of amendment 2

# 1. ABLATION: what each named part earns, held out, against the room mean
log("=== ablation ===")
abl = {}
abl["room_mean_only"] = 0.0
abl["map_only_no_room"] = None   # a pooled curved map with NO room term: predict from g(P) alone
class MapOnly:
    def fit(self, i, Y):
        X = np.column_stack([np.ones(len(i)), G[i]]); self.W_, *_ = np.linalg.lstsq(X, Y, rcond=None); return self
    def predict(self, i): return np.column_stack([np.ones(len(i)), G[i]]) @ self.W_
abl["map_only_no_room"] = heldout_gain(lambda: MapOnly(), C0)
abl["shift_only_linear_map"] = heldout_gain(lambda: Updated(curved=False, lam=1e9, rank=0), C0)
abl["shift_curved_map"] = heldout_gain(lambda: Updated(curved=True, lam=1e9, rank=0), C0)
abl["shift_curved_map_bend"] = heldout_gain(three_part, C0)
abl["shift_curved_map_bend_rank2"] = heldout_gain(lambda: Updated(curved=True, lam=None, rank=2), C0)
results["ablation"] = abl
for k, v in abl.items(): log(f"  {k:32s} gain={v:+.4f}")
json.dump(results, open(OUT, "w"), indent=1)

# 2. PERMUTATION NULL: shuffle disposition among persons WITHIN each room, refit the three part model.
#    The coupling must vanish; whatever gain survives is what the machinery extracts from nothing.
log("=== permutation null (disposition shuffled within room) ===")
Z_true, G_true = Z.copy(), G.copy()
perm_gains = []
g = np.random.default_rng(SEED + 17)
for p_ in range(NPERM):
    Zp = Z_true.copy()
    for r_ in range(R):
        ix = np.where(room == r_)[0]
        Zp[ix] = Z_true[ix][g.permutation(len(ix))]
    Z[:] = Zp; G[:] = (gfeat(Zp) - Gmu) / Gsd
    perm_gains.append(heldout_gain(three_part, C0))
    log(f"  perm {p_+1}/{NPERM}: gain={perm_gains[-1]:+.4f}")
Z[:] = Z_true; G[:] = G_true
results["permutation_null"] = dict(gains=perm_gains, mean=float(np.mean(perm_gains)), sd=float(np.std(perm_gains)),
                                   p95=float(np.percentile(perm_gains, 95)), real=abl["shift_curved_map_bend"])
log(f"  null mean {np.mean(perm_gains):+.4f} sd {np.std(perm_gains):.4f} p95 {np.percentile(perm_gains,95):+.4f}  real {abl['shift_curved_map_bend']:+.4f}")
json.dump(results, open(OUT, "w"), indent=1)

# 3. REVERSE PREDICTION: predict disposition from character with the same folds and room terms.
#    A leakage check: if the reader reads both from the same text, C -> P should be as easy as P -> C.
log("=== reverse prediction (character -> disposition) ===")
Cz = C0.copy(); Yrev = Z_true.copy()
class RevShift:
    def fit(self, i, Y):
        W, s, n = fit_fe(Cz[i], Y, room[i], R); self.W_, self.s_ = W, s; return self
    def predict(self, i): return Cz[i] @ self.W_ + self.s_[room[i]]
def heldout_gain_rev(model_fn, Y):
    sse_m = sse_0 = 0.0
    for f in range(K):
        tr, te = np.where(fold != f)[0], np.where(fold == f)[0]
        m0 = RoomMean().fit(tr, Y[tr]); ok = m0.train_n()[room[te]] >= ROOMMIN_TRAIN; te = te[ok]
        m = model_fn().fit(tr, Y[tr])
        sse_m += float(((Y[te] - m.predict(te))**2).sum()); sse_0 += float(((Y[te] - m0.predict(te))**2).sum())
    return float(1 - sse_m/sse_0)
rev = heldout_gain_rev(lambda: RevShift(), Yrev)
fwd_lin = abl["shift_only_linear_map"]
results["reverse_prediction"] = dict(gain_C_to_P=rev, gain_P_to_C_linear=fwd_lin,
    note="both are within room linear maps with a room shift; C has 8 inputs, P has 2, so equal gains are not expected; a C to P gain far above P to C flags the reader reading both from the same text")
log(f"  C -> P gain {rev:+.4f}   P -> C (linear, shift) {fwd_lin:+.4f}")
json.dump(results, open(OUT, "w"), indent=1)
log(f"written {OUT}")

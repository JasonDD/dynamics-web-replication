#!/usr/bin/env python3
"""char_propagate_2hop.py — the CORRECTED character propagation, rebuilt after the deep
propagation in scripts/fullgraph_propagate.py failed its held out test (fabric #20195:
r = 0.10, R2 against the predict the mean baseline = -10.2, calibration slope 0.124).

TWO FAULTS ARE FIXED HERE. Both were read out of the production code, not guessed.

  FAULT 1  UNKNOWN WAS TREATED AS ZERO.
           phase_char builds acc as the weighted sum of neighbour values but divides by norm,
           the TOTAL inbound edge weight over every neighbour, including the ~97.4 percent of
           vertices that never carried a value and contributed nothing to the numerator. Every
           estimate was therefore a real quantity over an inflated denominator, dragged toward
           zero by a factor that varies node by node. That is the mean shift (predicted 0.241
           against a true 0.451) and the flat calibration slope.
           FIX: divide by the inbound weight that ACTUALLY CARRIED A VALUE.

  FAULT 2  IT RAN PAST THE CORRELATION LENGTH.
           The programme's own measured character correlation length is about two hops. The
           production run took fifteen rounds, so it averaged in domains at distance five and
           beyond, where there is far more graph and no relationship. The depth curve shows it:
           mean r goes 0.36 at one hop to 0.09 at fifteen.
           FIX: stop at the correlation length. One hop and two hop estimates only.

  AND THREE THINGS THE ORIGINAL DID NOT DO AT ALL:
    3  NULL WHERE THERE IS NO EVIDENCE. A vertex with no valued neighbour inside the horizon
       gets no number, rather than a confident looking zero. Coverage is reported, not hidden.
    4  CALIBRATION. A linear map from prediction to truth is fitted on one half of the held out
       slice and reported on the other, so the output is correctly SCALED and not merely
       correlated. This is the difference between beating the mean baseline on error and not.
    5  PER DOMAIN CONFIDENCE. The seeded inbound weight and the seeded neighbour count travel
       with every row, so a domain inferred from fifty read neighbours is distinguishable from
       one inferred from a single link.

DIRECTION VARIANTS. `in` reproduces the production geometry: a vertex inherits from what links
TO it, each source weighted by 1/outdegree so a hub that links to everything counts for little.
`both` additionally uses what the vertex links to, each target weighted by 1/indegree, the exact
symmetric statement. Direction is a geometry choice, not one of the two faults, so `in` is the
primary graded configuration and `both` is reported alongside it.

WRITE SAFETY. This script NEVER touches the internal reference table, domain_char8_full,
domain_char8_scored, domain_indegree_full, domain_ranks_cc or domain_char8_holdout. Its only
write targets are the internal reference table (mode full) and the checkpoint directory.

Usage:
  python3 char_propagate_2hop.py --mode validate --dirs in     # graded held out run
  python3 char_propagate_2hop.py --mode validate --dirs both   # geometry variant
  python3 char_propagate_2hop.py --mode full     --dirs in     # materialise the product table
"""
import os, sys, time, json, argparse, ctypes
import multiprocessing as mp
import numpy as np
import psycopg2

WG    = os.environ.get("WG_ARRAYS", "/mnt/external/webgraph/wg_arrays")
CKPT  = os.environ.get("C2H_CKPT", "/mnt/external/webgraph/char2hop_ckpt")
HB    = os.environ.get("C2H_HEARTBEAT", "/home/jason/.kx-daemon/char-2hop.heartbeat")
AX    = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
RSEED = 20260903          # identical to char_holdout_validate.py, so the mask is the same rows
MASKFRAC = 0.10           # identical
os.makedirs(CKPT, exist_ok=True)
T0 = time.time()
G = {}


def log(*a):
    print(f"[{time.time()-T0:9.1f}s]", *a, flush=True)


def beat(phase, metric, value):
    try:
        os.makedirs(os.path.dirname(HB), exist_ok=True)
        with open(HB, "w") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{phase}\t{metric}={value}\n")
    except Exception:
        pass


def db_password():
    for l in open(os.path.expanduser("~/.kronaxis/env")):
        if l.startswith("TFS_DB_PASSWORD="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("FATAL: TFS_DB_PASSWORD not found in ~/.kronaxis/env")


def connect():
    cn = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={db_password()} dbname=tfs")
    cn.autocommit = True
    c = cn.cursor()
    c.execute("SET statement_timeout=0")
    c.execute("SET idle_in_transaction_session_timeout=0")
    c.close()
    return cn


# --------------------------------------------------------------------------- graph
def load_graph(dirs):
    """Compressed sparse row forms of the same 4.34 billion edge graph, both orientations.
    indptr/idx group by DESTINATION and hold the in neighbour source ids.
    indptr_src/idx_src group by SOURCE and hold the out neighbour destination ids.
    Verified on the box before use: node 12345 has indptr degree 1 and indeg.npy 1, and
    indptr_src degree 0 with inv_outdeg 0, i.e. dangling. Same 118,760,321 vertex numbering
    as an internal table."""
    invout = np.load(f"{WG}/inv_outdeg.npy")
    N = invout.shape[0]
    G["N"] = N
    G["in"] = (np.load(f"{WG}/indptr.npy"), np.load(f"{WG}/idx.npy", mmap_mode="r"), invout)
    assert G["in"][0].shape[0] == N + 1
    if dirs == "both":
        invin = np.load(f"{WG}/inv_indeg.npy")
        G["out"] = (np.load(f"{WG}/indptr_src.npy"), np.load(f"{WG}/idx_src.npy", mmap_mode="r"), invin)
        assert G["out"][0].shape[0] == N + 1
    log(f"  graph N={N:,} E={int(G['in'][0][-1]):,} dirs={dirs}")
    return N


def make_chunks(indptr, N, edge_budget=8_000_000):
    """Vertex ranges each holding roughly edge_budget edges. Disjoint ranges over the grouping
    key mean the accumulation has no write races, so it parallelises with no locking."""
    bounds = [0]
    tgt = edge_budget
    while bounds[-1] < N:
        nxt = int(np.searchsorted(indptr, tgt, side="left"))
        nxt = min(max(nxt, bounds[-1] + 1), N)
        bounds.append(nxt)
        tgt = int(indptr[nxt]) + edge_budget
    return [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]


def _worker(rng):
    """For every vertex d in [lo,hi): accumulate over its neighbours n in the current direction
        ACC[d] += X[n] * w[n]   over VALUED n only (unvalued n hold X = 0 so they add nothing)
        VW[d]  += w[n]          over VALUED n only   <-- THE FIX FOR FAULT 1
        NC[d]  += 1             over VALUED n only
    VW is the denominator: the neighbour weight that actually carried a value. Dividing by the
    total inbound weight instead is what biased the production map toward zero."""
    lo, hi = rng
    indptr, idx, w = G["IP"], G["IDX"], G["W"]
    X, VAL, ACC, VW, NC = G["X"], G["VAL"], G["ACC"], G["VW"], G["NC"]
    e0, e1 = int(indptr[lo]), int(indptr[hi])
    if e1 == e0:
        return          # nothing to add; never ASSIGN zero here, the other direction may
                        # already have written into this range under dirs=both
    nb = np.asarray(idx[e0:e1])
    wn = w[nb].astype(np.float64)
    vn = VAL[nb]                                    # float64 0/1, valued flag per neighbour
    wv = wn * vn
    V = X[nb].astype(np.float64)
    V *= wv[:, None]
    segs = np.minimum(indptr[lo:hi] - e0, V.shape[0] - 1)
    lens = indptr[lo + 1:hi + 1] - indptr[lo:hi]
    z = lens == 0
    a = np.add.reduceat(V, segs, axis=0); a[z] = 0.0
    b = np.add.reduceat(wv, segs);        b[z] = 0.0
    c = np.add.reduceat(vn, segs);        c[z] = 0.0
    ACC[lo:hi] += a
    VW[lo:hi]  += b
    NC[lo:hi]  += c


def shared_f64(shape):
    n = int(np.prod(shape))
    return np.frombuffer(mp.RawArray(ctypes.c_double, n), dtype=np.float64).reshape(shape)


def one_round(X, VAL, dirs, workers, tag):
    """One hop of evidence gathering. Returns (ACC, VW, NC) as plain arrays.
    ACC/VW is the seeded weight normalised neighbour mean wherever VW > 0; where VW == 0 there
    is NO EVIDENCE and the caller must emit nothing rather than a number."""
    N = G["N"]
    G["X"], G["VAL"] = X, VAL
    G["ACC"][:] = 0.0; G["VW"][:] = 0.0; G["NC"][:] = 0.0
    for d in (["in", "out"] if dirs == "both" else ["in"]):
        G["IP"], G["IDX"], G["W"] = G[d]
        chunks = make_chunks(G["IP"], N)
        t = time.time()
        with mp.get_context("fork").Pool(workers) as p:
            for i, _ in enumerate(p.imap_unordered(_worker, chunks, chunksize=1)):
                if i % 50 == 0:
                    beat(tag, f"{d}_chunks", f"{i}/{len(chunks)}")
        log(f"    {tag} direction {d}: {len(chunks)} chunks in {time.time()-t:.1f}s")
    return np.array(G["ACC"]), np.array(G["VW"]), np.array(G["NC"])


def estimate(acc, vw):
    """The corrected estimator, and the NULL rule. Nothing is invented where nothing is known."""
    ok = vw > 0
    est = np.zeros(acc.shape, np.float32)
    est[ok] = (acc[ok] / vw[ok, None]).astype(np.float32)
    return est, ok


# --------------------------------------------------------------------------- seed
def load_seed(cn):
    c = cn.cursor()
    log("  loading seed (the internal reference table JOIN an internal table)")
    c.execute("SELECT v.id, ch.domain, " + ",".join("ch." + a for a in AX) +
              " FROM the internal reference table ch JOIN an internal table v ON v.domain = ch.domain "
              "WHERE ch.rigour IS NOT NULL")
    rows = c.fetchall()
    c.close()
    ids = np.array([r[0] for r in rows], np.int64)
    doms = [r[1] for r in rows]
    vec = np.array([[r[k + 2] for k in range(8)] for r in rows], np.float32)
    log(f"  {len(ids):,} seed vertices")
    return ids, doms, vec


def split_mask(n):
    """IDENTICAL masking design to char_holdout_validate.py: same RandomState, same seed, same
    fraction, so the held out rows are the same rows and the numbers are directly comparable."""
    rs = np.random.RandomState(RSEED)
    perm = rs.permutation(n)
    k = int(round(MASKFRAC * n))
    return np.sort(perm[:k]), np.sort(perm[k:])


# --------------------------------------------------------------------------- metrics
def metrics(y, p):
    e = p - y
    r = float("nan") if (y.std() < 1e-12 or p.std() < 1e-12) else float(np.corrcoef(y, p)[0, 1])
    return r, float(np.abs(e).mean()), float(np.sqrt((e ** 2).mean()))


def grade(name, pred, ok, true, tmean, nseed):
    """Score one estimator against the held out truth, ON THE ROWS WHERE IT IS DEFINED, and
    against the predict the mean baseline COMPUTED ON THOSE SAME ROWS. The earlier evaluation
    compared an estimator scored on 189k rows with a baseline scored on 262k rows, which is not
    a like for like comparison; this is.

    Calibration is fitted on half A of the covered rows and every reported error is on half B,
    so no reported number is fitted on itself."""
    n = int(ok.sum())
    out = {"estimator": name, "defined_n": n, "masked_n": int(len(true)),
           "coverage_pct": 100.0 * n / len(true), "axes": {}}
    if n < 1000:
        out["note"] = "too few defined rows to grade"
        return out
    y_all, p_all = true[ok], pred[ok].astype(np.float64)
    rs = np.random.RandomState(RSEED + 1)
    A = rs.rand(n) < 0.5
    B = ~A
    for k, a in enumerate(AX):
        y, p = y_all[:, k], p_all[:, k]
        r_all, mae_raw, rmse_raw = metrics(y, p)
        sl, ic = (np.polyfit(p[A], y[A], 1) if p[A].std() > 1e-12 else (1.0, 0.0))
        pc = np.clip(sl * p[B] + ic, 0.0, 1.0)
        r_B, cmae, crmse = metrics(y[B], pc)
        b_mae = float(np.abs(y[B] - tmean[k]).mean())
        b_rmse = float(np.sqrt(((y[B] - tmean[k]) ** 2).mean()))
        _, rmae, rrmse = metrics(y[B], p[B])
        out["axes"][a] = {
            "r": r_all, "r_heldB": r_B,
            "calib_slope": float(sl), "calib_intercept": float(ic),
            "raw_mae_B": rmae, "raw_rmse_B": rrmse,
            "calibrated_mae_B": cmae, "calibrated_rmse_B": crmse,
            "baseline_mae_B": b_mae, "baseline_rmse_B": b_rmse,
            "r2_vs_baseline_calibrated": 1.0 - (crmse ** 2) / (b_rmse ** 2),
            "mae_gain_pct": 100.0 * (b_mae - cmae) / b_mae,
            "rmse_gain_pct": 100.0 * (b_rmse - crmse) / b_rmse,
            "true_mean_B": float(y[B].mean()), "pred_mean_calibrated_B": float(pc.mean()),
            "baseline_mean_value": float(tmean[k]),
        }
    ax = out["axes"]
    out["mean_r"] = float(np.nanmean([ax[a]["r"] for a in AX]))
    out["mean_calibrated_mae"] = float(np.mean([ax[a]["calibrated_mae_B"] for a in AX]))
    out["mean_calibrated_rmse"] = float(np.mean([ax[a]["calibrated_rmse_B"] for a in AX]))
    out["mean_baseline_mae"] = float(np.mean([ax[a]["baseline_mae_B"] for a in AX]))
    out["mean_baseline_rmse"] = float(np.mean([ax[a]["baseline_rmse_B"] for a in AX]))
    out["mean_r2_vs_baseline"] = float(np.mean([ax[a]["r2_vs_baseline_calibrated"] for a in AX]))
    out["axes_beating_baseline_mae"] = int(sum(ax[a]["calibrated_mae_B"] < ax[a]["baseline_mae_B"] for a in AX))
    out["axes_beating_baseline_rmse"] = int(sum(ax[a]["calibrated_rmse_B"] < ax[a]["baseline_rmse_B"] for a in AX))
    out["bar_a_r_beats_0.36"] = bool(out["mean_r"] > 0.36)
    out["bar_b_beats_baseline_mae_and_rmse"] = bool(
        out["mean_calibrated_mae"] < out["mean_baseline_mae"] and
        out["mean_calibrated_rmse"] < out["mean_baseline_rmse"])
    out["PASS"] = bool(out["bar_a_r_beats_0.36"] and out["bar_b_beats_baseline_mae_and_rmse"])
    # per confidence bands: the error bar a consumer actually needs
    bands = [(1, 1), (2, 2), (3, 9), (10, 49), (50, 10 ** 12)]
    ns = nseed[ok]
    out["confidence_bands"] = []
    for lo, hi in bands:
        m = (ns >= lo) & (ns <= hi)
        if m.sum() < 200:
            out["confidence_bands"].append({"n_valued_nbrs": f"{lo}-{hi}", "n": int(m.sum())})
            continue
        rr = [metrics(y_all[m, k], p_all[m, k])[0] for k in range(8)]
        rm = [float(np.sqrt(((y_all[m, k] - p_all[m, k]) ** 2).mean())) for k in range(8)]
        out["confidence_bands"].append({"n_valued_nbrs": f"{lo}-{hi}", "n": int(m.sum()),
                                        "mean_r": float(np.nanmean(rr)),
                                        "mean_raw_rmse": float(np.mean(rm))})
    return out


# --------------------------------------------------------------------------- validate
def mode_validate(dirs, workers):
    N = load_graph(dirs)
    cn = connect()
    ids, doms, vec = load_seed(cn)
    cn.close()
    mpos, tpos = split_mask(len(ids))
    mask_ids, train_ids = ids[mpos], ids[tpos]
    mask_true = vec[mpos].astype(np.float64)
    train_vec = vec[tpos]
    tmean = train_vec.astype(np.float64).mean(0)
    log(f"  rseed {RSEED}: masked {len(mask_ids):,} of {len(ids):,}; train {len(train_ids):,}")

    G["ACC"] = shared_f64((N, 8)); G["VW"] = shared_f64((N,)); G["NC"] = shared_f64((N,))
    X = np.zeros((N, 8), np.float32); X[train_ids] = train_vec
    VAL = np.zeros(N, np.float64);    VAL[train_ids] = 1.0

    ck = f"{CKPT}/validate_{dirs}_hop1.npz"
    if os.path.exists(ck):
        z = np.load(ck); e1, ok1, vw1, nc1 = z["e1"], z["ok1"], z["vw1"], z["nc1"]
        log("  RESUME hop 1 from checkpoint")
    else:
        log("  HOP 1: evidence from directly adjacent seeded vertices only")
        acc, vw1, nc1 = one_round(X, VAL, dirs, workers, "hop1")
        e1, ok1 = estimate(acc, vw1)
        np.savez(ck + ".tmp.npz", e1=e1, ok1=ok1, vw1=vw1, nc1=nc1)
        os.replace(ck + ".tmp.npz", ck)
        del acc
    log(f"  hop 1 defines {int(ok1.sum()):,} of {N:,} vertices ({100.0*ok1.sum()/N:.2f}%)")
    beat("validate", "hop1_defined", int(ok1.sum()))

    # hop 2: seeds keep their TRUE value, every other vertex carries its hop 1 estimate, and
    # vertices with no hop 1 evidence stay unvalued so they still contribute nothing.
    ck2 = f"{CKPT}/validate_{dirs}_hop2.npz"
    if os.path.exists(ck2):
        z = np.load(ck2); e2, ok2, vw2, nc2 = z["e2"], z["ok2"], z["vw2"], z["nc2"]
        log("  RESUME hop 2 from checkpoint")
    else:
        log("  HOP 2: evidence within two hops (seeds fixed at truth, others at their hop 1 value)")
        X2 = e1.copy(); X2[train_ids] = train_vec
        V2 = ok1.astype(np.float64); V2[train_ids] = 1.0
        acc, vw2, nc2 = one_round(X2, V2, dirs, workers, "hop2")
        e2, ok2 = estimate(acc, vw2)
        np.savez(ck2 + ".tmp.npz", e2=e2, ok2=ok2, vw2=vw2, nc2=nc2)
        os.replace(ck2 + ".tmp.npz", ck2)
        del acc, X2, V2
    log(f"  hop 2 defines {int(ok2.sum()):,} of {N:,} vertices ({100.0*ok2.sum()/N:.2f}%)")
    beat("validate", "hop2_defined", int(ok2.sum()))

    # cascade: use the one hop reading where it exists, fall back to two hops elsewhere. This is
    # the sensible product estimator; it is reported alongside the two graded ones, not instead.
    ec = e1.copy(); okc = ok1 | ok2
    fill = (~ok1) & ok2
    ec[fill] = e2[fill]
    ncc = np.where(ok1, nc1, nc2); vwc = np.where(ok1, vw1, vw2)

    m = mask_ids
    res = {"random_seed": RSEED, "mask_fraction": MASKFRAC, "dirs": dirs,
           "n_seed_total": int(len(ids)), "n_masked": int(len(mask_ids)),
           "n_train": int(len(train_ids)), "N_vertices": int(N),
           "graph_coverage": {
               "hop1_defined": int(ok1.sum()), "hop1_pct": 100.0 * float(ok1.sum()) / N,
               "hop2_defined": int(ok2.sum()), "hop2_pct": 100.0 * float(ok2.sum()) / N,
               "cascade_defined": int(okc.sum()), "cascade_pct": 100.0 * float(okc.sum()) / N,
               "null_at_hop2": int(N - okc.sum())},
           "graded": {}}
    for nm, e, ok, nc in (("hop1", e1, ok1, nc1), ("hop2", e2, ok2, nc2), ("cascade", ec, okc, ncc)):
        res["graded"][nm] = grade(nm, e[m], ok[m], mask_true, tmean, nc[m])
        g = res["graded"][nm]
        log(f"  {nm:8s} coverage {g['coverage_pct']:5.1f}%  mean r {g['mean_r']:.4f}  "
            f"cal MAE {g['mean_calibrated_mae']:.4f} vs base {g['mean_baseline_mae']:.4f}  "
            f"cal RMSE {g['mean_calibrated_rmse']:.4f} vs base {g['mean_baseline_rmse']:.4f}  "
            f"R2 {g['mean_r2_vs_baseline']:+.4f}  PASS={g['PASS']}")
    out = f"{CKPT}/validate_{dirs}.json"
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    log(f"  written {out}")
    # keep the fitted calibration where mode full can find it
    with open(f"{CKPT}/calibration_{dirs}.json", "w") as f:
        json.dump({nm: {a: [res["graded"][nm]["axes"][a]["calib_slope"],
                            res["graded"][nm]["axes"][a]["calib_intercept"]] for a in AX}
                   for nm in ("hop1", "hop2", "cascade")}, f, indent=2)
    return 0


# --------------------------------------------------------------------------- full
def mode_full(dirs, workers):
    """Materialise the product table from ALL the real scores, calibrated with the coefficients
    fitted in mode validate. Seeds keep their real read the text score at hop 0."""
    cal = json.load(open(f"{CKPT}/calibration_{dirs}.json"))
    N = load_graph(dirs)
    cn = connect()
    ids, doms, vec = load_seed(cn)
    G["ACC"] = shared_f64((N, 8)); G["VW"] = shared_f64((N,)); G["NC"] = shared_f64((N,))
    X = np.zeros((N, 8), np.float32); X[ids] = vec
    VAL = np.zeros(N, np.float64);    VAL[ids] = 1.0

    ck = f"{CKPT}/full_{dirs}_hop1.npz"
    if os.path.exists(ck):
        z = np.load(ck); e1, ok1, vw1, nc1 = z["e1"], z["ok1"], z["vw1"], z["nc1"]
        log("  RESUME full hop 1")
    else:
        log("  HOP 1 over the full seed")
        acc, vw1, nc1 = one_round(X, VAL, dirs, workers, "full_hop1")
        e1, ok1 = estimate(acc, vw1)
        np.savez(ck + ".tmp.npz", e1=e1, ok1=ok1, vw1=vw1, nc1=nc1); os.replace(ck + ".tmp.npz", ck)
        del acc
    ck2 = f"{CKPT}/full_{dirs}_hop2.npz"
    if os.path.exists(ck2):
        z = np.load(ck2); e2, ok2, vw2, nc2 = z["e2"], z["ok2"], z["vw2"], z["nc2"]
        log("  RESUME full hop 2")
    else:
        log("  HOP 2 over the full seed")
        X2 = e1.copy(); X2[ids] = vec
        V2 = ok1.astype(np.float64); V2[ids] = 1.0
        acc, vw2, nc2 = one_round(X2, V2, dirs, workers, "full_hop2")
        e2, ok2 = estimate(acc, vw2)
        np.savez(ck2 + ".tmp.npz", e2=e2, ok2=ok2, vw2=vw2, nc2=nc2); os.replace(ck2 + ".tmp.npz", ck2)
        del acc, X2, V2

    is_seed = np.zeros(N, np.bool_); is_seed[ids] = True
    hop = np.where(is_seed, 0, np.where(ok1, 1, np.where(ok2, 2, -1))).astype(np.int8)
    keep = hop >= 0
    out = e1.copy()
    fill = (~ok1) & ok2 & (~is_seed)
    out[fill] = e2[fill]
    out[ids] = vec                                   # seeds carry their real score, uncalibrated
    nc = np.where(ok1, nc1, nc2); vw = np.where(ok1, vw1, vw2)
    nc[ids] = 0; vw[ids] = 0.0

    # apply the held out calibration to the inferred rows only, per hop tier
    for tier, name in ((1, "hop1"), (2, "hop2")):
        sel = (hop == tier)
        for k, a in enumerate(AX):
            sl, ic = cal[name][a]
            out[sel, k] = np.clip(sl * out[sel, k] + ic, 0.0, 1.0)
    log(f"  rows to write: {int(keep.sum()):,} "
        f"(seed {int(is_seed.sum()):,}, hop1 {int((hop==1).sum()):,}, hop2 {int((hop==2).sum()):,}); "
        f"NULL {int((~keep).sum()):,}")

    vids = np.nonzero(keep)[0].astype(np.int64)
    tsv = f"{CKPT}/char8_2hop.tsv"
    with open(tsv, "w") as f:
        step = 5_000_000
        for k in range(0, len(vids), step):
            sl = vids[k:k + step]
            block = np.column_stack([sl, out[sl].astype(np.float64), hop[sl].astype(np.int64),
                                     nc[sl].astype(np.int64), vw[sl], is_seed[sl].astype(np.int64)])
            np.savetxt(f, block, fmt=["%d"] + ["%.6f"] * 8 + ["%d", "%d", "%.9g", "%d"], delimiter="\t")
            beat("full", "tsv_rows", min(k + step, len(vids)))
            log(f"    tsv {min(k+step, len(vids)):,}/{len(vids):,}")
    c = cn.cursor()
    c.execute("DROP TABLE IF EXISTS the internal reference table")
    c.execute("CREATE TABLE the internal reference table (domain text, " +
              ", ".join(a + " real" for a in AX) +
              ", hop smallint, n_valued_nbrs integer, evidence_weight double precision, is_seed boolean)")
    c.execute("DROP TABLE IF EXISTS _c2")
    c.execute("CREATE TEMP TABLE _c2(id bigint, " + ", ".join(a + " real" for a in AX) +
              ", hop smallint, n_valued_nbrs integer, evidence_weight double precision, is_seed smallint)")
    with open(tsv) as f:
        c.copy_expert("COPY _c2 FROM STDIN", f)
    log("  COPY into staging done; joining to webgraph_vertices for domain")
    c.execute("INSERT INTO the internal reference table SELECT v.domain, " +
              ", ".join("s." + a for a in AX) +
              ", s.hop, s.n_valued_nbrs, s.evidence_weight, s.is_seed::int::boolean "
              "FROM _c2 s JOIN an internal table v ON v.id = s.id")
    c.execute("DROP TABLE IF EXISTS _c2")
    c.execute("CREATE INDEX ON the internal reference table(domain)")
    c.execute("CREATE INDEX ON the internal reference table(hop)")
    c.execute("SELECT count(*), count(*) FILTER (WHERE hop=0), count(*) FILTER (WHERE hop=1), "
              "count(*) FILTER (WHERE hop=2) FROM the internal reference table")
    n, n0, n1, n2 = c.fetchone()
    c.close(); cn.close()
    os.remove(tsv)
    log(f"  the internal reference table = {n:,} rows (hop0 {n0:,}, hop1 {n1:,}, hop2 {n2:,})")
    with open(f"{CKPT}/full_{dirs}.json", "w") as f:
        json.dump({"rows": n, "hop0_seed": n0, "hop1": n1, "hop2": n2,
                   "vertices": int(N), "null_vertices": int(N - keep.sum()), "dirs": dirs}, f, indent=2)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="validate", choices=["validate", "full"])
    ap.add_argument("--dirs", default="in", choices=["in", "both"])
    ap.add_argument("--workers", type=int, default=40)
    args = ap.parse_args()
    log(f"START mode={args.mode} dirs={args.dirs} workers={args.workers} rseed={RSEED}")
    sys.exit(mode_validate(args.dirs, args.workers) if args.mode == "validate"
             else mode_full(args.dirs, args.workers))


if __name__ == "__main__":
    main()

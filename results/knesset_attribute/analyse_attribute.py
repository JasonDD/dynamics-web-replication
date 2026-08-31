#!/usr/bin/env python3
"""analyse_attribute.py — within-room character-by-attribute effects on scored Knesset turns.

Question: within the same plenary sitting (room), does the 8-axis character of a speech differ by the
speaker's REAL attribute — gender first, then coalition/opposition, party spread, nationality, age — once
the room is held fixed and length is controlled?

Room = protocol_name (one sitting = same debate day, same topic mix, same chamber temperature). Every test
below is WITHIN room: we never compare a speaker in one sitting to a speaker in another.

Legs:
  GENDER   : within-room length-matched F-vs-M pairs; per-axis paired diff, bootstrap CI, within-room
             permutation p, room-fixed-effects regression beta; per-knesset sign consistency across 30 yrs.
  COALITION: coalition vs opposition, identical within-room machinery (both present every sitting).
  PARTY    : within-room variance of each axis explained by party label (eta^2) — is party a character axis.
  NATIONALITY: Arab vs Jewish within-room (sparse; honest n + caveat).
  AGE      : within-room (room-demeaned) OLS slope per decade.

PC1 (matter vs manner) fit by PCA on the 8 standardised axes, oriented matter-positive; also a robust
matter-minus-manner composite. Numbers only. Usage: analyse_attribute.py SCORED.jsonl OUT.json
"""
import sys, json, math, random, collections
import numpy as np

random.seed(7); np.random.seed(7)
AXES = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
MATTER = ["rigour", "depth", "originality", "candour"]
MANNER = ["affect", "commercial_drive", "stance", "register"]
IN = sys.argv[1]
OUTJSON = sys.argv[2] if len(sys.argv) > 2 else "summary.json"

rows = []
for l in open(IN):
    try:
        r = json.loads(l)
    except Exception:
        continue
    if "char" not in r or not all(a in r["char"] for a in AXES):
        continue
    rows.append(r)
print(f"scored turns: {len(rows)}")


def M8(rs):
    return np.array([[r["char"][a] for a in AXES] for r in rs], float)


# ---- PC1 (matter vs manner) ----
X = M8(rows)
mu = X.mean(0); sd = X.std(0); sd[sd == 0] = 1
Z = (X - mu) / sd
C = np.cov(Z, rowvar=False)
w, V = np.linalg.eigh(C)
order = np.argsort(w)[::-1]
w = w[order]; V = V[:, order]
pc1 = V[:, 0]
# orient matter-positive
matidx = [AXES.index(a) for a in MATTER]
if pc1[matidx].mean() < 0:
    pc1 = -pc1
var1 = float(w[0] / w.sum())
for i, r in enumerate(rows):
    r["pc1"] = float(Z[i] @ pc1)
    r["mm"] = float(np.mean([r["char"][a] for a in MATTER]) - np.mean([r["char"][a] for a in MANNER]))
PC1_LOAD = {a: round(float(pc1[AXES.index(a)]), 3) for a in AXES}
print(f"\nPC1 variance explained: {var1:.3f}")
print("PC1 loadings (matter-positive):", PC1_LOAD)

METRICS = AXES + ["pc1", "mm"]


def val(r, m):
    return r["pc1"] if m == "pc1" else (r["mm"] if m == "mm" else r["char"][m])


def cohend(a, b):
    a = np.array(a); b = np.array(b)
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    na, nb = len(a), len(b)
    sp = math.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return (a.mean() - b.mean()) / sp if sp > 0 else float("nan")


def within_room_binary(rows, attr, pos, neg, lenmatch=True, nperm=2000, label=""):
    """Within each room, pair pos-vs-neg (length matched if lenmatch); aggregate paired diffs (pos-neg)."""
    by = collections.defaultdict(lambda: {"pos": [], "neg": []})
    for r in rows:
        v = r.get(attr)
        if v == pos:
            by[r["room"]]["pos"].append(r)
        elif v == neg:
            by[r["room"]]["neg"].append(r)
    rooms = [rm for rm, d in by.items() if d["pos"] and d["neg"]]
    pairs = []  # (pos_rec, neg_rec, room)
    room_signdiff = collections.defaultdict(dict)  # room -> metric -> mean(pos)-mean(neg)
    for rm in rooms:
        P = by[rm]["pos"][:]; N = by[rm]["neg"][:]
        random.shuffle(P); random.shuffle(N)
        if lenmatch:
            usedn = set()
            for p in P:
                cand = sorted((n for j, n in enumerate(N) if j not in usedn),
                              key=lambda n: abs(n["nchars"] - p["nchars"]))
                if not cand:
                    break
                n = cand[0]
                usedn.add(N.index(n))
                pairs.append((p, n, rm))
        else:
            k = min(len(P), len(N))
            for p, n in zip(P[:k], N[:k]):
                pairs.append((p, n, rm))
        for m in METRICS:
            room_signdiff[rm][m] = np.mean([val(x, m) for x in P]) - np.mean([val(x, m) for x in N])
    out = {"attr": attr, "pos": pos, "neg": neg, "n_rooms": len(rooms), "n_pairs": len(pairs), "axes": {}}
    if not pairs:
        return out
    # precompute permutation: within-room label shuffles of the paired pool
    pool = [(p, n, rm) for (p, n, rm) in pairs]
    for m in METRICS:
        dif = np.array([val(p, m) - val(n, m) for (p, n, rm) in pool])
        obs = float(dif.mean())
        # bootstrap CI over pairs
        bs = [dif[np.random.randint(0, len(dif), len(dif))].mean() for _ in range(1500)]
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        # paired cohen d
        dcoh = obs / dif.std(ddof=1) if dif.std(ddof=1) > 0 else float("nan")
        # within-pair permutation: random sign flip (exchange pos/neg within each pair)
        cnt = 0
        for _ in range(nperm):
            s = np.random.choice([-1, 1], len(dif))
            if abs((dif * s).mean()) >= abs(obs):
                cnt += 1
        p_perm = (cnt + 1) / (nperm + 1)
        # sign consistency across rooms
        sd = [room_signdiff[rm][m] for rm in rooms]
        consist = float(np.mean([np.sign(x) == np.sign(obs) for x in sd if x == x])) if sd else float("nan")
        out["axes"][m] = {"mean_diff": round(obs, 4), "ci95": [round(lo, 4), round(hi, 4)],
                          "paired_d": None if math.isnan(dcoh) else round(dcoh, 3),
                          "p_perm": round(p_perm, 4),
                          "room_sign_consistency": None if math.isnan(consist) else round(consist, 3)}
    print(f"\n=== WITHIN-ROOM {label or attr}: {pos} vs {neg}  (rooms={len(rooms)}, pairs={len(pairs)}) ===")
    print(f"{'metric':16} {'diff(pos-neg)':>13} {'ci95':>20} {'paird':>7} {'p_perm':>7} {'roomcons':>8}")
    for m in METRICS:
        a = out["axes"][m]
        print(f"{m:16} {a['mean_diff']:>13.4f} [{a['ci95'][0]:>7.3f},{a['ci95'][1]:>7.3f}]"
              f"   {str(a['paired_d']):>7} {a['p_perm']:>7} {str(a['room_sign_consistency']):>8}")
    return out


def per_knesset_direction(rows, attr, pos, neg, metric="pc1"):
    """per-knesset room-controlled direction of pos-neg on one metric (consistency across 30 years)."""
    byk = collections.defaultdict(lambda: collections.defaultdict(lambda: {"pos": [], "neg": []}))
    for r in rows:
        v = r.get(attr)
        if v == pos:
            byk[r["knesset"]][r["room"]]["pos"].append(val(r, metric))
        elif v == neg:
            byk[r["knesset"]][r["room"]]["neg"].append(val(r, metric))
    res = {}
    for kn, rms in sorted(byk.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        diffs = [np.mean(d["pos"]) - np.mean(d["neg"]) for d in rms.values() if d["pos"] and d["neg"]]
        if diffs:
            res[kn] = {"n_rooms": len(diffs), "mean_diff": round(float(np.mean(diffs)), 4)}
    return res


def within_room_eta2(rows, attr, minlab=8):
    """within-room variance of each metric explained by a categorical attr (room-demeaned one-way eta^2)."""
    # room-demean each metric
    rr = [r for r in rows if r.get(attr)]
    byroom = collections.defaultdict(list)
    for r in rr:
        byroom[r["room"]].append(r)
    dem = {}
    for rm, rs in byroom.items():
        if len(rs) < 2:
            continue
        for m in METRICS:
            mv = np.mean([val(x, m) for x in rs])
            for x in rs:
                dem.setdefault(id(x), {})[m] = val(x, m) - mv
    used = [r for r in rr if id(r) in dem]
    labs = collections.Counter(r[attr] for r in used)
    keep = {k for k, c in labs.items() if c >= minlab}
    used = [r for r in used if r[attr] in keep]
    out = {"attr": attr, "n": len(used), "n_labels": len(keep), "axes": {}}
    for m in METRICS:
        vals = np.array([dem[id(r)][m] for r in used])
        grand = vals.mean()
        ss_tot = ((vals - grand) ** 2).sum()
        ss_bet = 0.0
        for k in keep:
            gv = np.array([dem[id(r)][m] for r in used if r[attr] == k])
            ss_bet += len(gv) * (gv.mean() - grand) ** 2
        out["axes"][m] = round(float(ss_bet / ss_tot), 4) if ss_tot > 0 else 0.0
    print(f"\n=== WITHIN-ROOM party eta^2 (variance of room-demeaned axis explained by {attr}, "
          f"{len(keep)} parties, n={len(used)}) ===")
    for m in METRICS:
        print(f"{m:16} eta2={out['axes'][m]:.4f}")
    return out


def within_room_age(rows):
    """within-room (room-demeaned) OLS slope of each metric on age, per-decade."""
    rr = [r for r in rows if r.get("age")]
    byroom = collections.defaultdict(list)
    for r in rr:
        byroom[r["room"]].append(r)
    dem = []
    for rm, rs in byroom.items():
        if len(rs) < 3:
            continue
        agem = np.mean([x["age"] for x in rs])
        lnm = np.mean([math.log(x["nchars"]) for x in rs])
        for x in rs:
            row = {"age_c": x["age"] - agem, "ln_c": math.log(x["nchars"]) - lnm}
            for m in METRICS:
                mv = np.mean([val(y, m) for y in rs])
                row[m] = val(x, m) - mv
            dem.append(row)
    out = {"n": len(dem), "axes": {}}
    A = np.array([[d["age_c"], d["ln_c"], 1.0] for d in dem])
    for m in METRICS:
        y = np.array([d[m] for d in dem])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        resid = y - A @ beta
        dof = max(len(y) - 3, 1)
        s2 = (resid @ resid) / dof
        cov = s2 * np.linalg.pinv(A.T @ A)
        se = math.sqrt(max(cov[0, 0], 0))
        t = beta[0] / se if se > 0 else float("nan")
        out["axes"][m] = {"slope_per_decade": round(float(beta[0] * 10), 4),
                          "t": None if math.isnan(t) else round(float(t), 2)}
    print(f"\n=== WITHIN-ROOM age slope (room-demeaned, +len control, n={len(dem)}) ===")
    for m in METRICS:
        a = out["axes"][m]
        print(f"{m:16} slope/decade={a['slope_per_decade']:+.4f}  t={a['t']}")
    return out


summary = {"n": len(rows), "pc1_var": round(var1, 4), "pc1_load": PC1_LOAD,
           "gender_counts": dict(collections.Counter(r["gender"] for r in rows)),
           "nat_counts": dict(collections.Counter(r.get("nationality") for r in rows)),
           "coal_counts": dict(collections.Counter(r.get("coal") for r in rows))}

summary["gender"] = within_room_binary(rows, "gender", "F", "M", label="GENDER")
summary["gender_per_knesset_pc1"] = per_knesset_direction(rows, "gender", "F", "M", "pc1")
print("\nper-knesset F-M on PC1:", summary["gender_per_knesset_pc1"])

summary["coalition"] = within_room_binary(rows, "coal", "opposition", "coalition", label="POSITION")
summary["coal_per_knesset_pc1"] = per_knesset_direction(rows, "coal", "opposition", "coalition", "pc1")
print("\nper-knesset OPP-COAL on PC1:", summary["coal_per_knesset_pc1"])

summary["nationality"] = within_room_binary(rows, "nationality", "Arab", "Jewish", label="NATIONALITY")
summary["party_eta2"] = within_room_eta2(rows, "party")
summary["age"] = within_room_age(rows)

json.dump(summary, open(OUTJSON, "w"), indent=2)
print(f"\nsummary -> {OUTJSON}")

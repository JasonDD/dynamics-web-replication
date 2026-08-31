#!/usr/bin/env python3
"""cc_diaspora_gradient.py -- DIASPORA GRADIENT test (DYNAMICS-WEB, PUBLIC track, INTERNATIONAL).

Question: does a diaspora community's web character sit BETWEEN its ORIGIN country's web character
and its HOST country's web character -- i.e. is culture a CONTINUUM (a convex mix) rather than a
discrete bucket? And does the position depend on link-integration into the host (more host-linked =
closer to host)?

Held data, PURE graph + character analysis. No :8301/:8288, no new scoring.
  ORIGIN nationality signal : ccTLD of the registrable domain (a .tr / .pl / .it site).  Clean, coarse.
  HOST embedding signal     : the country distribution of the domain's LINK NEIGHBOURS on the full
                              Common Crawl web graph (118.7M vertices, 4.34B edges). A ccTLD-origin
                              domain whose neighbours resolve mostly to a DIFFERENT country Y is
                              embedded in Y -- the diaspora signal. This is INDEPENDENT of the frozen
                              ccTLD origin label, so the test is not circular.
  CHARACTER                 : cc_v3.domain_char8_expanded (2.65M scored domains, 8 DYNAMICS-WEB axes).

Method (mirrors cc_region_fullgraph.py for the graph; adds the neighbour-country histogram):
  1. Seed every vertex from its ccTLD (frozen). Stream vertices + edges, build the scored-touching
     adjacency, run <=10 rounds of majority label propagation so EVERY neighbour has a country.
  2. For each scored ccTLD-origin PLD, histogram its neighbours' final countries -> home_frac
     (neighbours in the origin country) and, for each other country Y, host_frac_Y.
  3. Assign that PLD embedding to each char8 original under it. Standardise the 8 axes across the
     whole scored set; PC1 = canonical matter/manner SVD basis (rigour+depth positive), series convention.
  4. For each corridor origin X -> host Y with enough domains:
       O = mean char of homeland-X   (origin==X, home-linked)      -- origin reference
       H = mean char of homeland-Y   (origin==Y, home-linked)      -- host   reference
       D = mean char of diaspora X-in-Y (origin==X, host_cc==Y, host_frac>home_frac)
     Intermediacy: alpha = <D-O,H-O>/<H-O,H-O> (0=origin,1=host); residual off the O->H line;
     bootstrap CI. Gradient: regress each domain's position t=<c-O,H-O>/||H-O||^2 on host_frac.
  5. Honest bounds: ccTLD is a coarse origin proxy; per-domain host embedding is a noisy majority
     vote (population tendency, not a per-domain label). A null (alpha~0 / diaspora==origin) is valid.

Env: VDIR(/mnt/external/webgraph), ROUNDS(10), CHUNK(20000000), OUT(dir for artifacts).
"""
import os, sys, gzip, time, subprocess, json, numpy as np, psycopg2

VDIR   = os.environ.get("VDIR", "/mnt/external/webgraph")
ROUNDS = int(os.environ.get("ROUNDS", "10"))
CHUNK  = int(os.environ.get("CHUNK", "20000000"))
OUT    = os.environ.get("OUT", os.path.expanduser("~/diaspora_gradient_out"))
os.makedirs(OUT, exist_ok=True)
t0 = time.time()
def log(*a): print(f"[{time.time()-t0:8.1f}s]", *a, flush=True)

# ---- ccTLD -> ISO2 seed map + gov/edu/mil -> US (identical to cc_region_fullgraph.py) ----
TLD = {"uk":"GB","gb":"GB","ca":"CA","au":"AU","nz":"NZ","za":"ZA","ie":"IE","us":"US","de":"DE","fr":"FR",
"nl":"NL","it":"IT","es":"ES","pl":"PL","se":"SE","no":"NO","dk":"DK","fi":"FI","ua":"UA","ru":"RU","ro":"RO",
"cz":"CZ","ch":"CH","at":"AT","be":"BE","pt":"PT","gr":"GR","hu":"HU","tr":"TR","jp":"JP","br":"BR","in":"IN",
"mx":"MX","ar":"AR","cl":"CL","kr":"KR","cn":"CN","vn":"VN","th":"TH","id":"ID","my":"MY","sg":"SG","ph":"PH",
"il":"IL","sa":"SA","ae":"AE","eg":"EG","ng":"NG","ke":"KE","pk":"PK","bd":"BD","lk":"LK","tw":"TW","hk":"HK",
"is":"IS","lt":"LT","lv":"LV","ee":"EE","si":"SI","sk":"SK","hr":"HR","rs":"RS","bg":"BG","by":"BY"}
US_GENERIC = {"gov", "edu", "mil"}
CC   = sorted(set(TLD.values()))
CIDX = {c: i for i, c in enumerate(CC)}
NCC  = len(CC)
DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
MATTER=["rigour","depth"]; MANNER=["affect","stance","register"]

def host_norm(d):
    h = d.split(":", 1)[0].strip().lower()
    if h.startswith("www."): h = h[4:]
    return h
def candidates(host):
    parts = host.split(".")
    return [".".join(parts[-k:]) for k in range(2, min(len(parts), 5) + 1)]
def rev(d): return ".".join(reversed(d.split(".")))
def tld_seed(dom):
    t = dom.rsplit(".", 1)[-1]
    if t in TLD: return CIDX[TLD[t]]
    if t in US_GENERIC: return CIDX["US"]
    return -1

PW = [l.split("=", 1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
db = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs")
db.autocommit = True
cur = db.cursor()

# ---- 1. load scored char8 (domain + 8 axes) ----
log("loading cc_v3.domain_char8_expanded (domain + 8 axes) ...")
cur.execute(f"SELECT domain,{','.join(DWEB)} FROM cc_v3.domain_char8_expanded")
rows = cur.fetchall()
originals = [r[0] for r in rows]
CHAR = np.array([[float(x) for x in r[1:]] for r in rows], np.float32)   # (Norig, 8)
Norig = len(originals)
log(f"char8 originals {Norig:,}")
# standardise axes across whole scored set; canonical PC1 (rigour+depth positive)
MEAN = CHAR.mean(0); STD = CHAR.std(0) + 1e-9
Z = (CHAR - MEAN) / STD
_,_,Vt = np.linalg.svd(Z.astype(np.float64), full_matrices=False); PC1 = Vt[0]
if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0: PC1 = -PC1
log("[pc1] " + ", ".join(f"{a}={PC1[i]:+.2f}" for i,a in enumerate(DWEB)))

cand_lists = [candidates(host_norm(o)) for o in originals]
cand_set = set()
for cl in cand_lists: cand_set.update(cl)
log(f"distinct candidate suffixes {len(cand_set):,}")

# ---- 2. stream vertices -> seed country + record candidate PLD vertex ids ----
log("streaming vertices.txt.gz ...")
MAXID = 130_000_000
country = np.full(MAXID, -1, np.int16)
seed    = np.full(MAXID, -1, np.int16)
cand_id = {}
NV = 0; maxid = 0
with gzip.open(f"{VDIR}/vertices.txt.gz", "rt") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 2: continue
        i = int(p[0]); dom = rev(p[1]).lower()
        if i > maxid: maxid = i
        NV += 1
        c = tld_seed(dom)
        if c >= 0: country[i] = c; seed[i] = c
        if dom in cand_set: cand_id[dom] = i
        if NV % 20_000_000 == 0: log(f"  vertices {NV:,}")
log(f"vertices {NV:,}, maxid {maxid:,}; candidate PLDs found: {len(cand_id):,}; seeded {int((seed>=0).sum()):,}")

# resolve each original to its registrable-domain vertex (shortest matching candidate)
norm_of_original = [None] * Norig
norm_id = {}
for oi, cl in enumerate(cand_lists):
    for cand in cl:
        vid = cand_id.get(cand)
        if vid is not None:
            norm_of_original[oi] = cand; norm_id[cand] = vid; break
cand_lists = None; cand_set = None
scored_norms = list(norm_id.keys())
S = len(scored_norms)
sidx_of_norm = {n:i for i,n in enumerate(scored_norms)}
scored_ids = np.array([norm_id[n] for n in scored_norms], np.int32)   # scored idx -> global id
sidx_of_gid = np.full(maxid + 1, -1, np.int32)
sidx_of_gid[scored_ids] = np.arange(S, dtype=np.int32)
scored_mask = np.zeros(maxid + 1, np.bool_); scored_mask[scored_ids] = True
target_scored = seed[scored_ids] < 0
log(f"scored PLD vertices S={S:,}; ccTLD-seeded {int((~target_scored).sum()):,}; targets {int(target_scored.sum()):,}")

# ---- 3. one edge pass -> scored-touching adjacency ----
log("streaming edges.txt.gz -> scored adjacency ...")
import pandas as pd
proc = subprocess.Popen(["pigz", "-dc", f"{VDIR}/edges.txt.gz"], stdout=subprocess.PIPE)
reader = pd.read_csv(proc.stdout, sep="\t", header=None, names=["a", "b"],
                     dtype={"a": np.int32, "b": np.int32}, chunksize=CHUNK, engine="c", na_filter=False)
key_parts=[]; nb_parts=[]; ne=0; kept=0
for chunk in reader:
    a = chunk["a"].to_numpy(); b = chunk["b"].to_numpy(); ne += len(a)
    ma = scored_mask[a]; mb = scored_mask[b]
    if ma.any():
        ka = sidx_of_gid[a[ma]]; nba = b[ma]
        good = scored_mask[nba] | (country[nba] >= 0)
        key_parts.append(ka[good]); nb_parts.append(nba[good]); kept += int(good.sum())
    if mb.any():
        kb = sidx_of_gid[b[mb]]; nbb = a[mb]
        good = scored_mask[nbb] | (country[nbb] >= 0)
        key_parts.append(kb[good]); nb_parts.append(nbb[good]); kept += int(good.sum())
    if ne % 200_000_000 < CHUNK: log(f"  edges {ne:,}  kept {kept:,}")
proc.wait()
KEYIDX = np.concatenate(key_parts) if key_parts else np.empty(0, np.int32); key_parts=None
NB     = np.concatenate(nb_parts)  if nb_parts  else np.empty(0, np.int32); nb_parts=None
log(f"adjacency endpoints {len(KEYIDX):,} ({KEYIDX.nbytes/1e9:.1f}+{NB.nbytes/1e9:.1f}GB)")

# ---- 4. propagation (resolve every neighbour) ----
log(f"propagation up to {ROUNDS} rounds ...")
KEY64 = KEYIDX.astype(np.int64)
for rnd in range(1, ROUNDS + 1):
    nbc = country[NB]; valid = nbc >= 0
    comp = KEY64[valid] * NCC + nbc[valid]
    cnt = np.bincount(comp, minlength=S * NCC).reshape(S, NCC)
    best = cnt.argmax(1); bestn = cnt[np.arange(S), best]
    assignable = target_scored & (bestn > 0)
    old = country[scored_ids].copy()
    newlab = np.where(assignable, best.astype(np.int16), old)
    country[scored_ids] = newlab
    changed = int((newlab != old).sum())
    log(f"  round {rnd}: changed {changed:,}  resolved {int((country[scored_ids]>=0).sum()):,}/{S:,}")
    del nbc, valid, comp, cnt, best, bestn
    if changed == 0: log(f"  converged at round {rnd}"); break

# ---- 5. neighbour-country histogram per scored PLD (the host embedding) ----
log("building neighbour-country histogram per scored PLD ...")
nb_c = country[NB]; valid = nb_c >= 0
comp = KEYIDX[valid].astype(np.int64) * NCC + nb_c[valid]
HIST = np.bincount(comp, minlength=S * NCC).reshape(S, NCC).astype(np.int64)   # (S, NCC)
del comp, nb_c, valid
tot_nb = HIST.sum(1)                                    # resolved neighbours per PLD
origin_sidx = seed[scored_ids]                          # ccTLD origin per scored PLD (-1 if none)
log(f"PLDs with >=1 resolved neighbour: {int((tot_nb>0).sum()):,}")

# home & host fractions per scored PLD (only ccTLD-origin PLDs are diaspora-testable)
home_cnt  = np.where(origin_sidx >= 0, HIST[np.arange(S), np.clip(origin_sidx,0,NCC-1)], 0)
HIST_nohome = HIST.copy()
oidx = origin_sidx >= 0
HIST_nohome[np.where(oidx)[0], origin_sidx[oidx]] = -1   # mask home so argmax picks the top FOREIGN host
host_sidx = HIST_nohome.argmax(1)
host_cnt  = HIST[np.arange(S), host_sidx]
with np.errstate(divide='ignore', invalid='ignore'):
    home_frac = np.where(tot_nb > 0, home_cnt / tot_nb, 0.0)
    host_frac = np.where(tot_nb > 0, host_cnt / tot_nb, 0.0)

# ---- 6. lift PLD embedding to char8 originals ----
log("assigning PLD embedding to char8 originals ...")
o_sidx = np.full(Norig, -1, np.int32)
for oi, n in enumerate(norm_of_original):
    if n is not None: o_sidx[oi] = sidx_of_norm[n]
have = o_sidx >= 0
o_origin = np.where(have, origin_sidx[np.clip(o_sidx,0,S-1)], -1)
o_host   = np.where(have, host_sidx[np.clip(o_sidx,0,S-1)], -1)
o_hostf  = np.where(have, host_frac[np.clip(o_sidx,0,S-1)], 0.0)
o_homef  = np.where(have, home_frac[np.clip(o_sidx,0,S-1)], 0.0)
o_totnb  = np.where(have, tot_nb[np.clip(o_sidx,0,S-1)], 0)
MINNB = 5
log(f"originals with ccTLD origin + >= {MINNB} resolved neighbours: "
    f"{int(((o_origin>=0)&(o_totnb>=MINNB)).sum()):,}")

np.savez(f"{OUT}/diaspora_embedding.npz",
         Z=Z.astype(np.float32), PC1=PC1.astype(np.float32),
         o_origin=o_origin, o_host=o_host, o_hostf=o_hostf.astype(np.float32),
         o_homef=o_homef.astype(np.float32), o_totnb=o_totnb.astype(np.int32),
         CC=np.array(CC), DWEB=np.array(DWEB))
log(f"saved embedding -> {OUT}/diaspora_embedding.npz")

# ================= 7. DIASPORA GRADIENT ANALYSIS =================
rng = np.random.default_rng(20260831)
def mean_char(mask):
    return Z[mask].mean(0) if mask.sum() else None

# homeland reference per country X: origin==X, home-linked (home_frac dominant, >=0.5, valid)
HOME_MIN = 0.5
def homeland_mask(X):
    xi = CIDX[X]
    return (o_origin == xi) & (o_totnb >= MINNB) & (o_homef >= HOME_MIN) & (o_homef >= o_hostf)

# diaspora X-in-Y: origin==X, dominant foreign host==Y, host-linked more than home-linked
def diaspora_mask(X, Y):
    xi, yi = CIDX[X], CIDX[Y]
    return (o_origin == xi) & (o_host == yi) & (o_totnb >= MINNB) & (o_hostf > o_homef)

# discover candidate corridors data-driven: count diaspora domains per (origin X != host Y)
log("discovering corridors ...")
corridor_n = {}
valid_o = (o_origin >= 0) & (o_totnb >= MINNB) & (o_hostf > o_homef)
oo = o_origin[valid_o]; hh = o_host[valid_o]
for xi, yi in zip(oo, hh):
    if xi == yi: continue
    corridor_n[(int(xi), int(yi))] = corridor_n.get((int(xi), int(yi)), 0) + 1
top_corr = sorted(corridor_n.items(), key=lambda kv: -kv[1])
log("top raw corridors (origin->host, n diaspora domains):")
for (xi, yi), n in top_corr[:30]:
    log(f"   {CC[xi]} -> {CC[yi]} : {n}")

MIN_CORR = 100
def analyse(X, Y):
    mO = homeland_mask(X); mH = homeland_mask(Y); mD = diaspora_mask(X, Y)
    nO, nH, nD = int(mO.sum()), int(mH.sum()), int(mD.sum())
    if nD < MIN_CORR or nO < MIN_CORR or nH < MIN_CORR: return None
    O = mean_char(mO); H = mean_char(mH); D = mean_char(mD)
    axis = H - O; denom = float(axis @ axis)
    if denom < 1e-9: return None
    alpha = float((D - O) @ axis / denom)
    resid = float(np.linalg.norm((D - O) - alpha * axis) / (np.linalg.norm(axis) + 1e-9))
    # PC1 scalar positions
    O1 = float(O @ PC1); H1 = float(H @ PC1); D1 = float(D @ PC1)
    alpha_pc1 = (D1 - O1) / (H1 - O1) if abs(H1 - O1) > 1e-9 else float('nan')
    # bootstrap alpha CI (resample domains within each group)
    iO = np.where(mO)[0]; iH = np.where(mH)[0]; iD = np.where(mD)[0]
    boots = []
    for _ in range(400):
        Ob = Z[rng.choice(iO, len(iO))].mean(0)
        Hb = Z[rng.choice(iH, len(iH))].mean(0)
        Db = Z[rng.choice(iD, len(iD))].mean(0)
        ax = Hb - Ob; dn = float(ax @ ax)
        if dn < 1e-9: continue
        boots.append(float((Db - Ob) @ ax / dn))
    boots = np.array(boots); lo, hi = np.percentile(boots, [2.5, 97.5]) if len(boots) else (float('nan'),)*2
    # GRADIENT: position t of each diaspora domain vs its host_frac
    t = ((Z[iD] - O) @ axis) / denom                 # 0=origin, 1=host projection
    hf = o_hostf[iD]
    if len(t) >= 20 and hf.std() > 1e-6:
        b1, b0 = np.polyfit(hf, t, 1)
        r = float(np.corrcoef(hf, t)[0, 1])
        n = len(t)
        # two-sided p for pearson r
        from math import sqrt
        tstat = r * sqrt((n - 2) / max(1e-12, 1 - r*r))
        try:
            from scipy import stats
            pval = float(2 * stats.t.sf(abs(tstat), n - 2))
        except Exception:
            pval = float('nan')
        grad = {"slope": float(b1), "r": r, "p": pval, "n": n}
    else:
        grad = None
    per_axis = {DWEB[i]: {"O": float(O[i]), "H": float(H[i]), "D": float(D[i])} for i in range(8)}
    return {"origin": X, "host": Y, "nO": nO, "nH": nH, "nD": nD,
            "alpha": alpha, "alpha_ci": [float(lo), float(hi)], "resid_offline": resid,
            "pc1": {"O": O1, "H": H1, "D": D1, "alpha_pc1": alpha_pc1},
            "gradient": grad, "per_axis": per_axis,
            "intermediate": bool(0.05 < alpha < 0.95 and resid < 1.0)}

# analyse the top data-driven corridors + a hand list of classic diaspora corridors
CLASSIC = [("TR","DE"),("PL","DE"),("PL","GB"),("IT","DE"),("IT","CH"),("RU","DE"),("IN","GB"),
           ("PT","FR"),("GR","DE"),("RO","IT"),("ES","FR"),("PL","NL"),("HR","DE"),("CZ","DE"),
           ("TR","NL"),("MA","FR") if "MA" in CIDX else ("PT","CH")]
seen = set()
corr_list = []
for (xi, yi), n in top_corr:
    corr_list.append((CC[xi], CC[yi]))
for pair in CLASSIC:
    if pair not in corr_list: corr_list.append(pair)

results = []
for (X, Y) in corr_list:
    if X not in CIDX or Y not in CIDX or (X, Y) in seen: continue
    seen.add((X, Y))
    r = analyse(X, Y)
    if r: results.append(r); log(f"  [corridor] {X}->{Y} alpha={r['alpha']:.2f} ci={r['alpha_ci']} "
                                  f"resid={r['resid_offline']:.2f} nD={r['nD']} "
                                  f"grad_r={(r['gradient'] or {}).get('r')}")

# pooled gradient across all analysed corridors (domain-level, position vs host_frac)
pooled_t=[]; pooled_hf=[]
for r in results:
    X, Y = r["origin"], r["host"]
    mO = homeland_mask(X); O = Z[mO].mean(0)
    mH = homeland_mask(Y); H = Z[mH].mean(0); axis = H - O; denom = float(axis @ axis)
    if denom < 1e-9: continue
    iD = np.where(diaspora_mask(X, Y))[0]
    t = ((Z[iD] - O) @ axis) / denom
    pooled_t.append(t); pooled_hf.append(o_hostf[iD])
pooled = None
if pooled_t:
    pt = np.concatenate(pooled_t); phf = np.concatenate(pooled_hf)
    if len(pt) >= 20 and phf.std() > 1e-6:
        b1, b0 = np.polyfit(phf, pt, 1); rr = float(np.corrcoef(phf, pt)[0, 1])
        pooled = {"slope": float(b1), "r": rr, "n": int(len(pt))}

summary = {
    "n_corridors": len(results),
    "n_intermediate": sum(1 for r in results if r["intermediate"]),
    "mean_alpha": float(np.mean([r["alpha"] for r in results])) if results else None,
    "pooled_gradient": pooled,
    "params": {"MINNB": MINNB, "HOME_MIN": HOME_MIN, "MIN_CORR": MIN_CORR,
               "n_scored_pld": S, "n_originals": Norig},
    "corridors": results,
    "top_raw_corridors": [{"origin": CC[xi], "host": CC[yi], "n": n} for (xi, yi), n in top_corr[:40]],
}
json.dump(summary, open(f"{OUT}/diaspora_result.json", "w"), indent=2)
log(f"wrote {OUT}/diaspora_result.json  ({len(results)} corridors, "
    f"{summary['n_intermediate']} intermediate, mean_alpha={summary['mean_alpha']})")
if pooled: log(f"pooled gradient: slope={pooled['slope']:.3f} r={pooled['r']:.3f} n={pooled['n']}")
log("DONE cc_diaspora_gradient.py")

#!/usr/bin/env python3
"""Cross-lineage field-structure / character-space dimensionality check.
7B vs 27B scorers on the SAME 1350 manipulation-set items (8 character axes).
Pure analysis, numpy only."""
import json, numpy as np

AXES = ["rigour","depth","originality","candour","affect",
        "commercial_drive","stance","register"]
BASE = "/mnt/nas/kronaxis/corpora/ira_troll/work"

def load(p):
    d={}
    for line in open(p):
        line=line.strip()
        if not line: continue
        o=json.loads(line); d[o["id"]]=o
    return d

a7 = load(f"{BASE}/baseline_7b.jsonl")
b27 = load(f"{BASE}/scored_27b.jsonl")
ids = sorted(set(a7) & set(b27))
n = len(ids)

def mat(store):
    return np.array([[store[i]["char"][ax] for ax in AXES] for i in ids], float)

X7  = mat(a7)
X27 = mat(b27)

def pca_corr(X):
    """Correlation-matrix PCA (z-score each axis). Returns eigvals(desc),
    loadings(components x axes), scores(items x comps), explained ratio."""
    mu = X.mean(0); sd = X.std(0, ddof=1)
    sd_safe = np.where(sd==0, 1.0, sd)
    Z = (X - mu) / sd_safe
    # SVD of Z / sqrt(n-1)  -> eigvals of correlation matrix
    U,S,Vt = np.linalg.svd(Z/np.sqrt(n-1), full_matrices=False)
    eig = S**2
    ratio = eig/eig.sum()
    scores = Z @ Vt.T            # item projections onto each PC
    return eig, Vt, scores, ratio, Z

def pca_cov(X):
    mu = X.mean(0)
    C = X - mu
    U,S,Vt = np.linalg.svd(C/np.sqrt(n-1), full_matrices=False)
    eig = S**2
    return eig, Vt, C @ Vt.T, eig/eig.sum()

def orient(load_vec, scores_col):
    """Sign-orient PC so rigour+depth pole is positive."""
    ri, di = AXES.index("rigour"), AXES.index("depth")
    if load_vec[ri] + load_vec[di] < 0:
        return -load_vec, -scores_col
    return load_vec, scores_col

def dims_for(ratio, thresh):
    c = np.cumsum(ratio)
    return int(np.searchsorted(c, thresh) + 1)

out = {"n_items": n, "axes": AXES}

for name, X in [("7B", X7), ("27B", X27)]:
    eig, Vt, scores, ratio, Z = pca_corr(X)
    pc1, s1 = orient(Vt[0].copy(), scores[:,0].copy())
    pc2, s2 = orient(Vt[1].copy(), scores[:,1].copy())
    out[name] = {
        "explained_ratio": [round(float(r),4) for r in ratio],
        "cum_ratio": [round(float(x),4) for x in np.cumsum(ratio)],
        "dims_80pct": dims_for(ratio,0.80),
        "dims_90pct": dims_for(ratio,0.90),
        "pc1_loadings": {ax: round(float(w),4) for ax,w in zip(AXES,pc1)},
        "pc2_loadings": {ax: round(float(w),4) for ax,w in zip(AXES,pc2)},
        "pc1_var": round(float(ratio[0]),4),
        "pc12_var": round(float(ratio[0]+ratio[1]),4),
    }
    # stash oriented pc1 scores/loadings for cross-lineage
    out[name]["_pc1_scores"] = s1.tolist()
    out[name]["_pc1_vec"] = pc1.tolist()
    out[name]["_pc2_vec"] = pc2.tolist()

# covariance-PCA variance ratios (secondary, for robustness of "2D" claim)
for name, X in [("7B", X7), ("27B", X27)]:
    eig, Vt, sc, ratio = pca_cov(X)
    out[name]["cov_explained_ratio"] = [round(float(r),4) for r in ratio]
    out[name]["cov_pc12_var"] = round(float(ratio[0]+ratio[1]),4)

# ---- cross-lineage agreement ----
v7  = np.array(out["7B"]["_pc1_vec"])
v27 = np.array(out["27B"]["_pc1_vec"])
cos = float(v7 @ v27 / (np.linalg.norm(v7)*np.linalg.norm(v27)))

s7  = np.array(out["7B"]["_pc1_scores"])
s27 = np.array(out["27B"]["_pc1_scores"])
def pearson(x,y):
    x=x-x.mean(); y=y-y.mean()
    return float(x@y/(np.linalg.norm(x)*np.linalg.norm(y)))
def spearman(x,y):
    rx=np.argsort(np.argsort(x)).astype(float)
    ry=np.argsort(np.argsort(y)).astype(float)
    return pearson(rx,ry)

# cross-basis: project each lineage's items onto the OTHER lineage's PC1 axis
# (standardise within own lineage first, consistent with corr-PCA)
def zscore(X):
    mu=X.mean(0); sd=X.std(0,ddof=1); sd=np.where(sd==0,1,sd)
    return (X-mu)/sd
Z7, Z27 = zscore(X7), zscore(X27)
# 7B items on 7B axis vs 27B items on 27B axis is s7/s27 already.
# cross: 27B items projected on 7B axis
proj_27on7 = Z27 @ v7
proj_7on27 = Z7 @ v27

out["cross_lineage"] = {
    "pc1_axis_cosine": round(cos,4),
    "pc1_score_pearson": round(pearson(s7,s27),4),
    "pc1_score_spearman": round(spearman(s7,s27),4),
    # does 7B-axis order 27B items the same as 27B-axis does?
    "proj_27on7_vs_27own_pearson": round(pearson(proj_27on7, s27),4),
    "proj_7on27_vs_7own_pearson": round(pearson(proj_7on27, s7),4),
}

# per-axis agreement of the raw instrument across lineages (same items)
out["per_axis_crosslineage_pearson"] = {
    ax: round(pearson(X7[:,j], X27[:,j]),4) for j,ax in enumerate(AXES)
}

# 8-axis vector agreement per item (mean cosine of standardised 8-vectors)
Z7n = Z7/ (np.linalg.norm(Z7,axis=1,keepdims=True)+1e-9)
Z27n= Z27/(np.linalg.norm(Z27,axis=1,keepdims=True)+1e-9)
percos = (Z7n*Z27n).sum(1)
out["per_item_8axis_cosine_mean"] = round(float(percos.mean()),4)
out["per_item_8axis_cosine_median"] = round(float(np.median(percos)),4)

# raw-vector (unstandardised) per-item cosine too
X7c=X7-X7.mean(0); X27c=X27-X27.mean(0)
def rn(M): return M/(np.linalg.norm(M,axis=1,keepdims=True)+1e-9)
out["per_item_8axis_cosine_raw_mean"] = round(float((rn(X7)*rn(X27)).sum(1).mean()),4)

# group PC1 means (sanity: matter/manner ordering preserved?)
kinds = np.array([a7[i]["kind"] for i in ids])
out["group_pc1_means"] = {}
for k in ["arg","liar","ira"]:
    m = kinds==k
    out["group_pc1_means"][k] = {
        "7B": round(float(s7[m].mean()),3),
        "27B": round(float(s27[m].mean()),3),
        "n": int(m.sum()),
    }

# strip internal keys before dump
for name in ["7B","27B"]:
    for kk in ["_pc1_scores","_pc1_vec","_pc2_vec"]:
        out[name].pop(kk,None)

print(json.dumps(out, indent=2))

#!/usr/bin/env python3
"""Cluster the held per-corpus winning-direction vectors for the decision-outcome matrix.
Each corpus contributes the standardised effect of each of the 8 axes on winning its outcome
(taken from the held result files). Scales differ (weighted_r / beta / Cohen d), so we z-score
WITHIN each corpus vector before correlating: this asks 'do two decisions reward the same SHAPE
of character', which is direction-invariant to scale. Also project each onto the fixed web PC1."""
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

AX=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
PC1={"rigour":+0.44,"depth":+0.40,"originality":+0.23,"candour":+0.39,
     "affect":-0.35,"commercial_drive":-0.26,"stance":+0.37,"register":-0.34}

# held per-axis winning-direction effect vectors (source file noted). Positive = that pole raises the win.
V={
 # ATTENTION
 "Upworthy click*":      dict(zip(AX,[-0.048,-0.054,+0.074,-0.034,+0.067,+0.019,-0.019,+0.018])), # upworthy univ weighted_r (CAUSAL)
 "UK petitions sign":    dict(zip(AX,[-0.005,+0.091,+0.121,-0.028,-0.034,-0.114,-0.030,-0.045])), # single-axis beta
 # DELIBERATIVE
 "CMV delta":            dict(zip(AX,[-0.039,-0.018,-0.027,+0.020,+0.047,-0.038,-0.099,-0.017])), # univ r
 "DDO audience vote":    dict(zip(AX,[+0.288,+0.259,+0.047,+0.014,-0.120,+0.050,+0.219,+0.135])), # within-debate Cohen d
 "Old Bailey verdict":   dict(zip(AX,[+0.314,-0.384,+0.213,+0.123,-0.065,-0.003,+0.166,-0.107])), # logit coef model C
 # FUNDING / ACTION
 "Kickstarter funded":   dict(zip(AX,[+0.021,+0.017,+0.077,-0.034,-0.034,+0.034,+0.001,-0.022])), # univ r
 "PSG donated":          dict(zip(AX,[+0.059,-0.005,-0.039,+0.024,+0.037,+0.032,-0.034,+0.001])), # univ r
}
# Stack Exchange: only PC1 given (+0.32 matter); Milkman: direction-only (matter). Handled narratively.

names=list(V.keys())
M=np.array([[V[n][a] for a in AX] for n in names],float)
# z-score within each corpus vector (scale-invariant shape)
Mz=(M-M.mean(1,keepdims=True))/M.std(1,keepdims=True)

# PC1 projection per corpus (on the RAW effect vector -> which pole the win leans)
print("=== per-corpus matter/manner PC1 lean of the winning direction (raw effect . PC1 loadings) ===")
pc1lean={}
for i,n in enumerate(names):
    proj=sum(PC1[a]*V[n][a] for a in AX); pc1lean[n]=proj
    lean="MATTER" if proj>0.005 else "MANNER" if proj<-0.005 else "~neutral"
    print(f"  {n:<22} PC1proj={proj:+.4f}  -> {lean}")

print("\n=== cross-corpus correlation of winning-character SHAPE (Pearson on z-scored vectors) ===")
C=np.corrcoef(Mz)
print("            "+"".join(f"{n[:8]:>9}" for n in names))
for i,n in enumerate(names):
    print(f"{n[:11]:<11} "+"".join(f"{C[i,j]:+9.2f}" for j in range(len(names))))

print("\n=== hierarchical clustering (1-corr distance, average linkage) ===")
D=1-C; np.fill_diagonal(D,0); D=(D+D.T)/2
Z=linkage(squareform(D,checks=False),method="average")
for k in (2,3,4):
    lab=fcluster(Z,k,criterion="maxclust")
    groups={}
    for n,l in zip(names,lab): groups.setdefault(l,[]).append(n)
    print(f"  k={k}: "+" | ".join("{"+", ".join(g)+"}" for g in groups.values()))

# originality dimension: is funding/pitch high on originality relative to its own mean?
print("\n=== originality lean (z within corpus) : funding-pitch vs the rest ===")
for i,n in enumerate(names):
    print(f"  {n:<22} orig_z={Mz[i,AX.index('originality')]:+.2f}")

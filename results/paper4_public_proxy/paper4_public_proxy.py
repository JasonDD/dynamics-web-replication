#!/usr/bin/env python3
"""
Paper 4 PUBLIC proxy coupling: run the two core analyses on the public
journalists-across-editorial-sections corpus (an internal table), the reviewable
substitute for the internally held cross site corpus (linkage method withheld).

Analyses:
  A. Trait vs performance split (ICC): decompose each DYNAMICS-8 disposition
     axis into between-author (stable trait) and within-author-across-sections
     (performed room state). Between-author share = trait share.
  B. Metatrait bridge: person-level plasticity/stability metatraits vs produced
     content character (matter-vs-manner, originality), authors averaged over
     their sections so performed state cancels.

Public corpus. No individual named. Numbers reported at their tier.
"""
import os, json, math
import psycopg2
import numpy as np

PW = open(os.path.expanduser("~/.pgpass")).readline().strip().split(":")[4]
conn = psycopg2.connect(host="an internal address", port=5432, dbname="tfs", user="titan", password=PW)
cur = conn.cursor()

# pull scored articles with an author and a section, both score blobs present
cur.execute("""
  select author, topic, disp_d8, char_dweb
  from an internal table
  where disp_d8 is not null and char_dweb is not null
    and author is not null and author <> '' and topic is not null and topic <> ''
""")
rows = cur.fetchall()
print(f"rows pulled: {len(rows)}")

D8 = ["acuity","candour","novelty","yielding","discipline","impulsivity","sociability","mercuriality"]
DW = ["rigour","depth","candour","stance","affect","commercial_drive","register","originality"]

# assemble arrays
authors=[]; sections=[]; disp=[]; char=[]
for a,t,dj,cj in rows:
    d = dj if isinstance(dj,dict) else json.loads(dj)
    c = cj if isinstance(cj,dict) else json.loads(cj)
    if not all(k in d for k in D8): continue
    if not all(k in c for k in DW): continue
    authors.append(a); sections.append(t)
    disp.append([float(d[k]) for k in D8])
    char.append([float(c[k]) for k in DW])

authors=np.array(authors); sections=np.array(sections)
disp=np.array(disp); char=np.array(char)
print(f"usable scored articles: {len(authors)}  authors: {len(set(authors))}")

# restrict to authors seen across >=2 distinct sections (multi-context = 'rooms')
from collections import defaultdict
sec_by_auth=defaultdict(set)
for a,s in zip(authors,sections): sec_by_auth[a].add(s)
multi = {a for a,ss in sec_by_auth.items() if len(ss)>=2}
mask = np.array([a in multi for a in authors])
authors=authors[mask]; sections=sections[mask]; disp=disp[mask]; char=char[mask]
print(f"multi-context (>=2 sections) authors: {len(multi)}  articles: {len(authors)}")

# standardise each axis across the corpus (z-scores) so combinations are comparable
def zcols(M):
    mu=M.mean(0); sd=M.std(0); sd[sd==0]=1.0
    return (M-mu)/sd
dz=zcols(disp); cz=zcols(char)

# ---------- A. ICC (one-way random effects, ICC(1)) per disposition axis ----------
def icc1(values, groups):
    # values: 1D array; groups: labels. Between-group var share via one-way ANOVA.
    gm=defaultdict(list)
    for v,g in zip(values,groups): gm[g].append(v)
    k=len(gm); N=len(values)
    grand=np.mean(values)
    # mean per group, group sizes
    ni=np.array([len(v) for v in gm.values()], float)
    mi=np.array([np.mean(v) for v in gm.values()], float)
    # sums of squares
    ssb=np.sum(ni*(mi-grand)**2)                 # between
    ssw=np.sum([np.sum((np.array(v)-np.mean(v))**2) for v in gm.values()])  # within
    dfb=k-1; dfw=N-k
    if dfw<=0 or dfb<=0: return float('nan')
    msb=ssb/dfb; msw=ssw/dfw
    # average group size (unbalanced correction)
    n0=(N - np.sum(ni**2)/N)/(k-1)
    denom=msb+(n0-1)*msw
    if denom<=0: return float('nan')
    return (msb-msw)/denom

print("\n=== A. Trait-vs-performance split (ICC(1), between-author share) ===")
print("axis            article-level   section-mean-level")
# section-mean level: collapse each author*section to its mean, ICC across authors
def sec_collapse(vals, auth, sec):
    key=defaultdict(list)
    for v,a,s in zip(vals,auth,sec): key[(a,s)].append(v)
    aa=[]; vv=[]
    for (a,s),lst in key.items(): aa.append(a); vv.append(np.mean(lst))
    return np.array(vv), np.array(aa)

art_iccs=[]; sec_iccs=[]
for j,ax in enumerate(D8):
    art=icc1(dz[:,j], authors)
    v2,a2=sec_collapse(dz[:,j], authors, sections)
    sec=icc1(v2, a2)
    art_iccs.append(art); sec_iccs.append(sec)
    print(f"{ax:14s}  {art:12.3f}   {sec:12.3f}")
print(f"{'MEAN':14s}  {np.nanmean(art_iccs):12.3f}   {np.nanmean(sec_iccs):12.3f}")

# ---------- metatraits & content dimensions (on standardised axes) ----------
di={k:i for i,k in enumerate(D8)}; ci={k:i for i,k in enumerate(DW)}
# plasticity = sociability(extra) + novelty(openness); stability = discipline(consc)+yielding(agree) - mercuriality(volatility)
plasticity = dz[:,di["sociability"]] + dz[:,di["novelty"]]
stability  = dz[:,di["discipline"]] + dz[:,di["yielding"]] - dz[:,di["mercuriality"]]
# content: matter(substance) - manner ; originality
matter = cz[:,ci["rigour"]] + cz[:,ci["depth"]] + cz[:,ci["candour"]] + cz[:,ci["stance"]]
manner = cz[:,ci["affect"]] + cz[:,ci["commercial_drive"]] + cz[:,ci["register"]]
matter_manner = matter - manner
originality = cz[:,ci["originality"]]

# ---------- B. Metatrait bridge at PERSON level (average over sections) ----------
def person_avg(vec, auth):
    g=defaultdict(list)
    for v,a in zip(vec,auth): g[a].append(v)
    keys=sorted(g); return np.array(keys), np.array([np.mean(g[k]) for k in keys])

ak, plas_p = person_avg(plasticity, authors)
_,  stab_p = person_avg(stability, authors)
_,  mm_p   = person_avg(matter_manner, authors)
_,  orig_p = person_avg(originality, authors)

def pearson(x,y):
    x=np.array(x); y=np.array(y)
    r=np.corrcoef(x,y)[0,1]
    n=len(x)
    # two-sided p via t
    if abs(r)>=1: p=0.0
    else:
        t=r*math.sqrt((n-2)/(1-r*r))
        # normal approx for p
        from math import erf
        p=2*(1-0.5*(1+erf(abs(t)/math.sqrt(2))))
    return r,p,n

print("\n=== B. Metatrait bridge (person-level, authors averaged over sections) ===")
print(f"n persons: {len(ak)}")
for name,x,y in [
    ("plasticity -> originality", plas_p, orig_p),
    ("plasticity -> matter/manner", plas_p, mm_p),
    ("stability  -> matter/manner", stab_p, mm_p),
    ("stability  -> originality",  stab_p, orig_p),
]:
    r,p,n=pearson(x,y)
    print(f"{name:30s}  r={r:+.3f}  p={p:.1e}  n={n}")

# also report at article level for contrast (inflated by performed state)
print("\n(article-level, for contrast; inflated by performed state)")
for name,x,y in [
    ("plasticity -> originality", plasticity, originality),
    ("plasticity -> matter/manner", plasticity, matter_manner),
]:
    r,p,n=pearson(x,y)
    print(f"{name:30s}  r={r:+.3f}  p={p:.1e}  n={n}")

cur.close(); conn.close()

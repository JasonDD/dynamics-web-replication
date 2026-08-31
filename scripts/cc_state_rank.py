#!/usr/bin/env python3
"""cc_state_rank.py — the EFFECTIVE RANK of the state displacement.

The count of nameable state variables may be open, but that is the wrong question. The
question that decides whether the equation of state is finite is: do the location offsets
of the different state variables live in a LOW-DIMENSIONAL subspace of character space?

For each state variable W, each of its groups has a mean 8-axis character; centred within W
these are the location offsets. Stack all offsets across genre + site + language, SVD, and
read the effective rank. If it is ~1-2 and aligned with matter/manner, the state's whole
contribution is low rank and the equation is finite in effect however many Ws exist.
Aggregate only, no keys, no names.
"""
import os, json, numpy as np, psycopg2
CHAR=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
FLOOR=int(os.environ.get("FLOOR","300"))
GENRE_JSON="/home/jason/projects/kronaxis/truthometer/results/prereg_genre_PF-4B/genre_assign_400_FROZEN.json"
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
db=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"); c=db.cursor()
def obj(x): return x if isinstance(x,dict) else (json.loads(x) if x else None)

# canonical matter/manner PC1 for reference direction
c.execute(f"SELECT {','.join(CHAR)} FROM cc_v3.domain_char8_expanded")
allc=np.array([[float(v) for v in r] for r in c.fetchall()],float)
MEAN=allc.mean(0); STD=allc.std(0)+1e-9
_,_,Vt=np.linalg.svd((allc-MEAN)/STD,full_matrices=False); PC1=Vt[0]
if PC1[0]+PC1[1]<0: PC1=-PC1
print(f"[rank] matter/manner PC1: "+", ".join(f"{a}={PC1[i]:+.2f}" for i,a in enumerate(CHAR)),flush=True)

def group_offsets(rows, keyfn):
    """rows: list of (char8-array, groupkey). returns centred group-mean vectors (z-scaled per axis) with n>=FLOOR."""
    by={}
    for ch,k in rows:
        if k is None: continue
        by.setdefault(k,[]).append(ch)
    G=[np.mean(v,0) for k,v in by.items() if len(v)>=FLOOR]
    if len(G)<3: return None
    M=(np.array(G)-MEAN)/STD                     # to z-axes
    return M-M.mean(0)                            # centre = the location offsets

offsets={}
# genre offsets (reddit communities -> genre)
gmap=json.load(open(GENRE_JSON))
c.execute("SELECT subreddit,char FROM cc_v3.reddit_wide WHERE char IS NOT NULL")
rr=[]
for sub,ch in c.fetchall():
    ch=obj(ch)
    if ch and all(a in ch for a in CHAR):
        g=gmap.get(sub)
        if g and g!="other_misc": rr.append((np.array([float(ch[a]) for a in CHAR]), g))
offsets["genre"]=group_offsets(rr, None);
print(f"[rank] genre offsets: {0 if offsets['genre'] is None else len(offsets['genre'])} groups",flush=True)

# site + language offsets (crosssite)
c.execute("SELECT domain,lang,char_dweb FROM cc_v3.crosssite_authorship WHERE char_dweb IS NOT NULL")
site_rows=[]; lang_rows=[]
for dom,lang,ch in c.fetchall():
    ch=obj(ch)
    if not ch or any(a not in ch for a in CHAR): continue
    v=np.array([float(ch[a]) for a in CHAR])
    tld=dom.rsplit(".",1)[-1].lower() if dom and "." in dom else None
    if tld and len(tld)<=6: site_rows.append((v,tld))
    if lang: lang_rows.append((v,lang))
offsets["site"]=group_offsets(site_rows,None); print(f"[rank] site offsets: {0 if offsets['site'] is None else len(offsets['site'])} groups",flush=True)
offsets["language"]=group_offsets(lang_rows,None); print(f"[rank] language offsets: {0 if offsets['language'] is None else len(offsets['language'])} groups",flush=True)

def eff_rank(M):
    s=np.linalg.svd(M,compute_uv=False); s2=s**2
    pr=(s2.sum()**2)/(s2**2).sum()               # participation ratio (effective rank)
    frac1=s2[0]/s2.sum(); frac2=s2[:2].sum()/s2.sum()
    return s, pr, frac1, frac2

def lead_dir(M):
    U,s,Vt=np.linalg.svd(M,full_matrices=False); v=Vt[0]
    if v@PC1<0: v=-v
    return v

print("\n================ EFFECTIVE RANK OF THE STATE DISPLACEMENT ================",flush=True)
allM=[]
for w in ("genre","site","language"):
    M=offsets[w]
    if M is None: print(f"  {w}: too few groups"); continue
    s,pr,f1,f2=eff_rank(M); v=lead_dir(M); cos=abs(float(v@PC1))
    print(f"  {w:9} {len(M):3d} offsets | eff.rank={pr:.2f} | top dim={100*f1:.0f}% top2={100*f2:.0f}% | lead|.|PC1|={cos:.2f}",flush=True)
    allM.append(M)
# combined: do the three Ws' offsets share ONE subspace?
if len(allM)>=2:
    C=np.vstack(allM); s,pr,f1,f2=eff_rank(C); v=lead_dir(C); cos=abs(float(v@PC1))
    print(f"\n  COMBINED (genre+site+language stacked): {len(C)} offsets | eff.rank={pr:.2f} | top dim={100*f1:.0f}% top2={100*f2:.0f}% | lead|.|PC1|={cos:.2f}",flush=True)
    # pairwise cosine of the three Ws' leading directions
    dirs={w:lead_dir(offsets[w]) for w in ("genre","site","language") if offsets[w] is not None}
    ws=list(dirs);
    print("  pairwise cosine of leading offset directions:",flush=True)
    for i in range(len(ws)):
        for j in range(i+1,len(ws)):
            print(f"    {ws[i]} . {ws[j]} = {abs(float(dirs[ws[i]]@dirs[ws[j]])):.2f}",flush=True)
print("=========================================================================",flush=True)
print("READ: eff.rank ~1 and high |.|PC1| across all Ws => the state displacement is essentially",flush=True)
print("      one-dimensional (translation along matter/manner). The equation is finite in EFFECT",flush=True)
print("      however many state labels exist. eff.rank climbing with more Ws => genuinely multi-dim state.",flush=True)

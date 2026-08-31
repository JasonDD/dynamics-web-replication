#!/usr/bin/env python3
"""genre_var.py — how much of manner-inflation variance does genre actually explain?
Community-level eta^2 (genre as factor on community-mean MI) and item-level eta^2, plus the
quantisation grid of the scorer. Honesty addendum to genre_calib.py."""
import os, json, numpy as np, psycopg2
CHAR=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
MATTER=["rigour","depth"]; MANNER=["affect","stance","register"]
GJ="/home/jason/projects/kronaxis/truthometer/results/prereg_genre_PF-4B/genre_assign_400_FROZEN.json"
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
cur=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
gmap=json.load(open(GJ))
def mi(ch): return float(np.mean([ch[a] for a in MANNER]))-float(np.mean([ch[a] for a in MATTER]))
cur.execute("SELECT subreddit,char FROM cc_v3.reddit_wide WHERE char IS NOT NULL")
items=[]; comm={}
for sub,ch in cur.fetchall():
    ch=ch if isinstance(ch,dict) else json.loads(ch)
    if not all(a in ch for a in CHAR): continue
    g=gmap.get(sub)
    if g is None or g=="other_misc": continue
    v=mi(ch); items.append((sub,g,v)); comm.setdefault((sub,g),[]).append(v)

def eta2(groups):
    allv=np.concatenate([np.asarray(v) for v in groups.values()])
    gm=allv.mean(); sst=((allv-gm)**2).sum()
    ssb=sum(len(v)*(np.mean(v)-gm)**2 for v in groups.values())
    return ssb/sst
# item-level
gi={}
for _,g,v in items: gi.setdefault(g,[]).append(v)
print(f"item-level  eta^2 (genre explains): {eta2(gi):.4f}  (n_items={len(items)})")
# community-level: one MI per community, grouped by genre
cmean={k:np.mean(v) for k,v in comm.items()}
gc={}
for (sub,g),m in cmean.items(): gc.setdefault(g,[]).append(m)
print(f"comm-level  eta^2 (genre explains): {eta2(gc):.4f}  (n_comm={len(cmean)})")
# spreads for the honesty sentence
allv=np.array([v for _,_,v in items]);
gmeds=np.array([np.median(v) for v in gi.values()])
print(f"between-genre SD of medians = {gmeds.std():.4f}   within-genre typical IQR ~ {np.median([np.percentile(v,75)-np.percentile(v,25) for v in gi.values()]):.3f}")
# quantisation grid
u=np.unique(np.round(allv,4))
print(f"distinct MI values: {len(u)}  smallest gaps: {np.round(np.diff(np.sort(u))[:6],4)}")

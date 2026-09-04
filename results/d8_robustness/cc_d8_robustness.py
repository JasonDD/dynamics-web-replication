#!/usr/bin/env python3
"""cc_d8_robustness.py -- the person side gauntlet: how reliable is the DYNAMICS-8 disposition read?

Every recent reduction (Biber, ELM, Coh-Metrix, Grice, the manner mirror) tested the CONTENT side, the
character instrument. The PERSON side, the disposition instrument that is half of the Ashlar bridge, has
had far less. This measures the two reliabilities that decide how much weight the bridge can bear:

  SPLIT HALF   -- for each person with several texts, split their texts in two, read a disposition mean
                  on each half, and correlate the halves across persons, per axis (Spearman Brown). This
                  is how stable the person level read is, the ceiling on any coupling that uses it.
  TWO READER   -- the agreement between two independent model families reading the SAME texts, per axis,
                  from the cross lineage sample. Already known weak on yielding and mercuriality; here it
                  is put beside the split half so the shaky axes are named with two numbers, not one.

Then the two metatraits (plasticity = novelty + sociability; stability = discipline + yielding
- mercuriality) get the same treatment, because stability is built from the two axes the readers most
disagree on, and the question is whether the composite inherits that weakness. Aggregate, analysis only.
"""
import os, json, math, time
import numpy as np, psycopg2
t0=time.time()
def log(*a): print(f"[{time.time()-t0:7.1f}s]", *a, flush=True)
D8=["discipline","yielding","novelty","acuity","mercuriality","impulsivity","candour","sociability"]
OUT=os.environ.get("OUT","/tmp/d8_robustness.json"); SEED=20260903
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
db=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"); c=db.cursor()
def obj(x): return x if isinstance(x,dict) else (json.loads(x) if x else None)
def pear(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float); a=a-a.mean(); b=b-b.mean()
    d=math.sqrt((a*a).sum()*(b*b).sum()); return float((a*b).sum()/d) if d else float("nan")
def sb(r): return 2*r/(1+r) if r>0 else r   # Spearman Brown, two halves -> full

# ---- SPLIT HALF on the full crosssite (person = ident), disp_d8 ----
log("pull disp_d8 rows for split half ...")
c.execute("SELECT ident, disp_d8 FROM the internal cross site corpus WHERE disp_d8 IS NOT NULL")
byp={}
for ident,dd in c:
    dd=obj(dd)
    if not isinstance(dd,dict) or any(a not in dd for a in D8) or not ident: continue
    try: v=[float(dd[a]) for a in D8]
    except (TypeError,ValueError): continue
    byp.setdefault(ident,[]).append(v)
rng=np.random.default_rng(SEED)
HA={a:[] for a in D8}; HB={a:[] for a in D8}
mp_plasA,mp_plasB,mp_stabA,mp_stabB=[],[],[],[]
i8={a:k for k,a in enumerate(D8)}
n_multi=0
for ident,vs in byp.items():
    if len(vs)<2: continue
    n_multi+=1; vs=np.array(vs); idx=rng.permutation(len(vs)); h=len(vs)//2
    a_=vs[idx[:h]].mean(0); b_=vs[idx[h:]].mean(0)
    for a in D8: HA[a].append(a_[i8[a]]); HB[a].append(b_[i8[a]])
    def mt(v): return (v[i8["novelty"]]+v[i8["sociability"]], v[i8["discipline"]]+v[i8["yielding"]]-v[i8["mercuriality"]])
    pa,sa=mt(a_); pb,sb_=mt(b_); mp_plasA.append(pa); mp_plasB.append(pb); mp_stabA.append(sa); mp_stabB.append(sb_)
log(f"persons with >=2 texts: {n_multi:,}")
split={a: dict(half_r=(r:=pear(HA[a],HB[a])), reliability=sb(r)) for a in D8}
mt_split={"plasticity":dict(half_r=(rp:=pear(mp_plasA,mp_plasB)),reliability=sb(rp)),
          "stability":dict(half_r=(rs:=pear(mp_stabA,mp_stabB)),reliability=sb(rs))}

# ---- TWO READER on the cross lineage sample ----
log("pull two-reader agreement (disp_d8 vs disp_d8_mist) on the xlineage sample ...")
cols=", ".join("(a.%s->>'%s')::float8" % ("disp_d8",k) for k in D8)+", "+", ".join("(a.%s->>'%s')::float8" % ("disp_d8_mist",k) for k in D8)
c.execute(f"SELECT {cols} FROM the internal cross site corpus a JOIN an internal table s USING (id) "
          f"WHERE a.disp_d8 IS NOT NULL AND a.disp_d8_mist IS NOT NULL")
M=np.array([r for r in c.fetchall() if all(x is not None for x in r)],float)
log(f"two-reader rows: {len(M):,}")
tworeader={a: pear(M[:,i], M[:,len(D8)+i]) for i,a in enumerate(D8)}
# metatrait two-reader
def mtcol(M,off): return (M[:,off+i8["novelty"]]+M[:,off+i8["sociability"]], M[:,off+i8["discipline"]]+M[:,off+i8["yielding"]]-M[:,off+i8["mercuriality"]])
pA,sA=mtcol(M,0); pB,sB=mtcol(M,len(D8)); mt_two={"plasticity":pear(pA,pB),"stability":pear(sA,sB)}
db.close()

res=dict(n_persons_multi=n_multi, n_two_reader=len(M),
         split_half=split, metatrait_split_half=mt_split, two_reader=tworeader, metatrait_two_reader=mt_two)
json.dump(res,open(OUT,"w"),indent=1)
log("=== D8 per axis: split-half reliability | two-reader agreement ===")
for a in D8: log(f"  {a:<13} split {split[a]['reliability']:+.3f}   two-reader {tworeader[a]:+.3f}")
log("=== metatraits ===")
for m in ("plasticity","stability"): log(f"  {m:<12} split {mt_split[m]['reliability']:+.3f}   two-reader {mt_two[m]:+.3f}")
weak=[a for a in D8 if split[a]['reliability']<0.4 or tworeader[a]<0.3]
log(f"WEAK axes (split<0.4 or two-reader<0.3): {weak}")
log(f"wrote {OUT}")

#!/usr/bin/env python3
"""detector_prep.py — RE-ANCHORED credibility-detector prep.

The first attempt (Experiment B, autumn 2022 BoE gilt/LDI episode) nulled because the Bank of England
was the RESPONDER, not the discredited party. This re-anchors on episodes where the central bank's OWN
credibility was lost: the 2021-2022 "transitory inflation" walk-back. Several major central banks held
that the post-COVID inflation surge was transitory, then reversed — a clear case of a central bank's own
credibility taking a hit.

Builds one scoring input per institution, 2019-2023, keeping full text + year + month, so an event study
can bin speeches by month-distance from each institution's own reversal date (t0).

Institutions + t0 (reversal / own-credibility-loss month):
  federal reserve (board + speeches merged)  t0 = 2021-11  (Powell retires "transitory", 30 Nov 2021)
  european central bank                       t0 = 2022-07  (first hike; Lagarde defended transitory into late 2021)
  reserve bank of australia                   t0 = 2022-05  (abandons "no hike until 2024" guidance; first hike; RBA Review follows)
  bank of england                             t0 = 2021-12  (first hike; transitory framing walked back)  [reuses boe_scored.jsonl]
"""
import os, json, collections
import pandas as pd

OUT="/mnt/nas/kronaxis/corpora/comms_scout"
PARQ=os.path.join(OUT,"bis_speeches.parquet")

df=pd.read_parquet(PARQ)
df["text"]=df["text"].astype(str)
df=df[df["text"].str.len()>400].copy()
df["bank"]=df["bank"].astype(str).str.strip().str.lower()
df["Year"]=pd.to_numeric(df["Year"],errors="coerce")
df["Month"]=pd.to_numeric(df["Month"],errors="coerce")
df=df.dropna(subset=["Year","Month"])
df["Year"]=df["Year"].astype(int); df["Month"]=df["Month"].astype(int)
df=df[(df["Year"]>=2019)&(df["Year"]<=2023)].copy()

# institution matchers -> canonical label
def canon(b):
    if "board of governors of the federal reserve" in b or b=="federal reserve": return "federal reserve"
    if "european central bank" in b: return "european central bank"
    if "reserve bank of australia" in b: return "reserve bank of australia"
    return None
df["inst"]=df["bank"].apply(canon)
df=df[df["inst"].notnull()].copy()

CAP=60   # per (inst, year) cap to bound scoring load and balance yearly cells
rows=[]
rng=__import__("random"); rng.seed(42)
for (inst,yr),g in df.groupby(["inst","Year"]):
    take=g.sample(min(CAP,len(g)), random_state=42) if len(g)>CAP else g
    for _,r in take.iterrows():
        rows.append({"id":f"det_{inst[:4]}_{yr}_{r['Month']}_{len(rows)}",
                     "source":"BIS_speech","inst":inst,"year":int(yr),"month":int(r["Month"]),"text":r["text"]})

with open(os.path.join(OUT,"detector_timeline.jsonl"),"w") as f:
    for r in rows: f.write(json.dumps(r)+"\n")

c=collections.Counter((r["inst"],r["year"]) for r in rows)
print(f"[prep] detector_timeline.jsonl: {len(rows)} speeches")
for k in sorted(c): print(f"   {k[0]:28s} {k[1]}  n={c[k]}")

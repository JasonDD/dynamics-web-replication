#!/usr/bin/env python3
"""comms_b_prep.py — Experiment B prep. Build two scoring inputs from the BIS central bank speeches parquet:
  1. signature_sample.jsonl  — stratified across major central banks x years (the credibility signature)
  2. boe_timeline.jsonl       — Bank of England speeches by month, bracketing the autumn 2022 gilt episode
Full text + institution + Year + Month are all present in the dataset."""
import os, json, urllib.request, sys
import pandas as pd

OUT="/mnt/nas/kronaxis/corpora/comms_scout"
os.makedirs(OUT, exist_ok=True)
PARQ=os.path.join(OUT,"bis_speeches.parquet")
URL="https://huggingface.co/datasets/samchain/bis_central_bank_speeches/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet"

if not os.path.exists(PARQ):
    print("[prep] downloading BIS parquet...",flush=True)
    req=urllib.request.Request(URL, headers={"User-Agent":"Kronaxis research jasond@kronaxis.co.uk"})
    with urllib.request.urlopen(req) as r, open(PARQ,"wb") as f:
        f.write(r.read())
    print(f"[prep] saved {os.path.getsize(PARQ)/1e6:.0f} MB",flush=True)

df=pd.read_parquet(PARQ)
df["text"]=df["text"].astype(str)
df=df[df["text"].str.len()>400].copy()
df["bank"]=df["bank"].astype(str).str.strip().str.lower()
df["Year"]=pd.to_numeric(df["Year"],errors="coerce")
df["Month"]=pd.to_numeric(df["Month"],errors="coerce")
df=df.dropna(subset=["Year"])
df["Year"]=df["Year"].astype(int)
print("[prep] total usable speeches:", len(df),flush=True)
print("[prep] top banks:\n", df["bank"].value_counts().head(20).to_string(),flush=True)

# --- signature sample: major banks, cap per bank, across years ---
MAJOR=["board of governors of the federal reserve system","federal reserve",
       "european central bank","bank of england","deutsche bundesbank","bank of japan",
       "reserve bank of india","bank of canada","reserve bank of australia","swiss national bank",
       "bank of france","bank for international settlements","reserve bank of new zealand","bank of italy"]
def match_major(b):
    for m in MAJOR:
        if m in b or b in m: return m
    return None
df["major"]=df["bank"].apply(match_major)
sig=[]
rng=__import__("random"); rng.seed(42)
for m,g in df[df["major"].notnull()].groupby("major"):
    g=g.sort_values(["Year","Month"])
    take=g.sample(min(35,len(g)), random_state=42)
    for _,r in take.iterrows():
        sig.append({"id":f"sig_{m[:8].replace(' ','')}_{r['Year']}_{int(r['Month']) if r['Month']==r['Month'] else 0}_{len(sig)}",
                    "source":"BIS_speech","bank":m,"year":int(r["Year"]),
                    "month":int(r["Month"]) if r["Month"]==r["Month"] else 0,"text":r["text"]})
with open(os.path.join(OUT,"signature_sample.jsonl"),"w") as f:
    for r in sig: f.write(json.dumps(r)+"\n")
print(f"[prep] signature_sample.jsonl: {len(sig)} speeches across {df[df['major'].notnull()]['major'].nunique()} banks",flush=True)

# --- BoE timeline: bank of england, 2018-2025, bracket autumn 2022 (t0=2022-09) ---
boe=df[df["bank"].str.contains("bank of england")].copy()
boe=boe[(boe["Year"]>=2018)&(boe["Year"]<=2025)].sort_values(["Year","Month"])
# cap to keep the queue polite: up to ~18/month is unrealistic; take all, usually modest
tl=[]
for _,r in boe.iterrows():
    tl.append({"id":f"boe_{r['Year']}_{int(r['Month']) if r['Month']==r['Month'] else 0}_{len(tl)}",
               "source":"BoE_speech","bank":"bank of england","year":int(r["Year"]),
               "month":int(r["Month"]) if r["Month"]==r["Month"] else 0,"text":r["text"]})
# safety cap
if len(tl)>260:
    rng.shuffle(tl); tl=sorted(tl[:260], key=lambda x:(x["year"],x["month"]))
with open(os.path.join(OUT,"boe_timeline.jsonl"),"w") as f:
    for r in tl: f.write(json.dumps(r)+"\n")
import collections
byyr=collections.Counter((r["year"]) for r in tl)
print(f"[prep] boe_timeline.jsonl: {len(tl)} BoE speeches | by year {dict(sorted(byyr.items()))}",flush=True)

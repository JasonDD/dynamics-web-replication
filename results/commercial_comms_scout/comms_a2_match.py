#!/usr/bin/env python3
"""Measure AAER (2015-2022 firm respondents) x S&P500 earnings-call transcript universe intersection."""
import os, json, re, urllib.request
import pandas as pd
OUT="/mnt/nas/kronaxis/corpora/comms_scout"; os.makedirs(OUT,exist_ok=True)
UA="Kronaxis research jasond@kronaxis.co.uk"
PARQ=os.path.join(OUT,"bose_sp500_calls.parquet")
URL="https://huggingface.co/datasets/Bose345/sp500_earnings_transcripts/resolve/main/"
# find parquet file(s)
def get(u,b=False):
    req=urllib.request.Request(u,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read() if b else r.read().decode("utf-8","ignore")
if not os.path.exists(PARQ):
    # resolve parquet listing via datasets-server
    j=json.loads(get("https://datasets-server.huggingface.co/parquet?dataset=Bose345/sp500_earnings_transcripts"))
    purl=j["parquet_files"][0]["url"]
    print("[a2] downloading", purl)
    open(PARQ,"wb").write(get(purl,b=True))
    print("[a2] saved", os.path.getsize(PARQ)//1_000_000,"MB")
df=pd.read_parquet(PARQ, columns=["symbol","company_name","year","quarter","date"])
def norm(s):
    s=str(s).lower()
    s=re.sub(r"[.,]"," ",s)
    s=re.sub(r"\b(inc|corp|corporation|company|co|ltd|llc|lp|plc|holdings|group|the|international|technologies|technology|systems|inc's)\b"," ",s)
    s=re.sub(r"\s+"," ",s).strip()
    return s
uni={}
for _,r in df.groupby("symbol").agg(company_name=("company_name","first"),ymin=("year","min"),ymax=("year","max")).reset_index().iterrows():
    uni[r["symbol"]]={"name":r["company_name"],"norm":norm(r["company_name"]),"ymin":int(r["ymin"]),"ymax":int(r["ymax"])}
print(f"[a2] transcript universe: {len(uni)} tickers, years {df['year'].min()}-{df['year'].max()}, {len(df)} calls")
# AAER firms
aaer=[json.loads(l) for l in open("/tmp/aaer_releases.jsonl")]
def is_person(n):
    return bool(re.search(r",?\s*(CPA|CFA|Esq|Jr|Sr|MD|PhD)\b", n)) or bool(re.match(r"^[A-Z][a-z]+ [A-Z]\.? [A-Z][a-z]+", n))
firm_aaer=[a for a in aaer if not is_person(a["name"])]
norm2ticker={v["norm"]:k for k,v in uni.items() if v["norm"]}
matches=[]
for a in firm_aaer:
    an=norm(re.sub(r",?\s*et al\.?$","",a["name"]))
    if len(an)<3: continue
    hit=None
    for tk,v in uni.items():
        vn=v["norm"]
        if not vn: continue
        if an==vn or (len(an)>=5 and (an in vn or vn in an)):
            hit=tk; break
    if hit:
        matches.append({"ticker":hit,"company":uni[hit]["name"],"aaer_name":a["name"],"aaer":a["aaer"],"date":a["date"],
                        "ymin":uni[hit]["ymin"],"ymax":uni[hit]["ymax"]})
# earliest AAER date per ticker = t0
bydate={}
def mdY(d):
    import datetime,re
    m=re.match(r"([A-Za-z]+)\.?\s+(\d{1,2}),\s+(\d{4})",d)
    if not m: return None
    mo={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}.get(m.group(1)[:3])
    if not mo: return None
    return datetime.date(int(m.group(3)),mo,int(m.group(2)))
byt={}
for m in matches:
    d=mdY(m["date"]);
    if not d: continue
    if m["ticker"] not in byt or d<byt[m["ticker"]]["t0"]:
        byt[m["ticker"]]={**m,"t0":d}
print(f"\n[a2] AAER firm respondents: {len(firm_aaer)} | matched to transcript tickers: {len(byt)}")
for tk,m in sorted(byt.items(), key=lambda x:x[1]["t0"]):
    print(f"  {tk:6s} t0={m['t0']} calls[{m['ymin']}-{m['ymax']}]  AAER-{m['aaer']}  {m['company'][:34]:34s} <- {m['aaer_name'][:34]}")
json.dump({tk:{**{k:(str(v) if k=='t0' else v) for k,v in m.items()}} for tk,m in byt.items()}, open(OUT+"/a2_fraud_matches.json","w"), indent=0)

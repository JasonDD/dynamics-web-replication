#!/usr/bin/env python3
"""Experiment A2 (wetter medium): build the earnings-call event-study input.
Fraud firms = SEC AAER respondents 2015-2022 matched (token-strict) to the S&P500 transcript universe,
with t0 = earliest AAER release date. For each: pre-exposure calls [t0-2y, t0), own earlier baseline,
and sector-matched (same 2-digit SIC) S&P500 controls over the same absolute windows."""
import os, json, re, datetime, urllib.request, time, collections
import pandas as pd
OUT="the internal corpus store/comms_scout"
UA="Kronaxis research jasond@kronaxis.co.uk"
PARQ=os.path.join(OUT,"bose_sp500_calls.parquet")

def get(u):
    for _ in range(3):
        try:
            req=urllib.request.Request(u,headers={"User-Agent":UA})
            with urllib.request.urlopen(req,timeout=60) as r: return r.read().decode("utf-8","ignore")
        except Exception: time.sleep(1.0)
    return ""

STOP=set("inc corp corporation company companies co ltd llc lp plc holdings holding group the international technologies technology systems solutions industries associates".split())
def toks(s):
    s=str(s).lower(); s=re.sub(r"[.,&]"," ",s); s=re.sub(r"\s+"," ",s)
    return set(w for w in s.split() if w and w not in STOP and len(w)>=3)
def is_person(n):
    return bool(re.search(r",?\s*(CPA|CFA|Esq|MD|PhD|CGMA)\b", n)) or bool(re.match(r"^[A-Z][a-z]+\s+[A-Z]\.?\s+[A-Z][a-z]+", n.strip()))
def mdY(d):
    m=re.match(r"([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),\s+(\d{4})",d)
    mo={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}.get(m.group(1)) if m else None
    return datetime.date(int(m.group(3)),mo,int(m.group(2))) if mo else None

df=pd.read_parquet(PARQ, columns=["symbol","company_name","year","quarter","date","content"])
df["d"]=pd.to_datetime(df["date"], errors="coerce", utc=True).dt.date
df=df.dropna(subset=["d"])
uni=df.groupby("symbol").agg(company_name=("company_name","first")).reset_index()
uni_toks={r["symbol"]:toks(r["company_name"]) for _,r in uni.iterrows()}
uni_name={r["symbol"]:r["company_name"] for _,r in uni.iterrows()}

# token-strict AAER match
aaer=[json.loads(l) for l in open("/tmp/aaer_releases.jsonl")]
byt={}
for a in aaer:
    if is_person(a["name"]): continue
    an=toks(re.sub(r",?\s*et al\.?.*$","",a["name"]))
    if len(an)<1: continue
    best=None
    for tk,vt in uni_toks.items():
        if not vt: continue
        inter=an & vt
        # strict: all fraud-name core tokens present in company tokens (or vice versa), >=1 shared distinctive token
        if inter and (an<=vt or vt<=an) and max(len(w) for w in inter)>=4:
            best=tk; break
    if best:
        d=mdY(a["date"])
        if d and (best not in byt or d<byt[best]["t0"]):
            byt[best]={"ticker":best,"company":uni_name[best],"aaer":a["aaer"],"aaer_name":a["name"],"t0":d}
print(f"[a2] token-strict fraud matches: {len(byt)}")
for tk,m in sorted(byt.items(), key=lambda x:x[1]["t0"]):
    print(f"  {tk:6s} t0={m['t0']}  AAER-{m['aaer']}  {m['company'][:40]}")

# SIC via EDGAR for ALL universe tickers, once, disk-cached
ct=json.loads(get("https://www.sec.gov/files/company_tickers.json"))
tk2cik={v["ticker"].upper():int(v["cik_str"]) for v in ct.values()}
SICF=OUT+"/sic_cache.json"
sic_cache=json.load(open(SICF)) if os.path.exists(SICF) else {}
def sic_of(tk):
    if tk in sic_cache: return sic_cache[tk]
    cik=tk2cik.get(tk.upper())
    if not cik: sic_cache[tk]=None; return None
    try:
        j=json.loads(get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")); time.sleep(0.1)
        s=str(j.get("sic","") or "")[:2]
    except Exception: s=None
    sic_cache[tk]=s; return s
allsyms0=list(uni_toks.keys())
for i,tk in enumerate(allsyms0):
    sic_of(tk)
    if (i+1)%50==0:
        json.dump(sic_cache, open(SICF,"w")); print(f"[a2] sic {i+1}/{len(allsyms0)}",flush=True)
json.dump(sic_cache, open(SICF,"w"))
print(f"[a2] sic map built ({sum(1 for v in sic_cache.values() if v)} resolved)",flush=True)
fraud_sic={tk:sic_of(tk) for tk in byt}

# controls: same 2-digit SIC, S&P500, not fraud
allsyms=list(uni_toks.keys())
def calls_between(tk, d0, d1, cap=6):
    g=df[(df["symbol"]==tk)&(df["d"]>=d0)&(df["d"]<d1)].sort_values("d")
    return list(g.itertuples())[:cap]

rows=[]
def emit(tk, rec, window, t0, company, sic):
    txt=str(rec.content)[:6000]
    if len(txt)<800: return
    rows.append({"id":f"{window}_{tk}_{rec.d}","ticker":tk,"company":company,"sic":sic,
                 "date":str(rec.d),"window":window,"t0":str(t0),"text":txt})

used_ctrl=set()
for tk,m in byt.items():
    t0=m["t0"]; sic=fraud_sic.get(tk)
    pre0=t0-datetime.timedelta(days=730); base1=t0-datetime.timedelta(days=910); base0=t0-datetime.timedelta(days=2555)
    for rec in calls_between(tk, pre0, t0): emit(tk, rec, "fraud_pre", t0, m["company"], sic)
    for rec in calls_between(tk, base0, base1): emit(tk, rec, "fraud_base", t0, m["company"], sic)
    # controls: up to 2 same-SIC S&P500 firms
    if not sic: continue
    cands=[s for s in allsyms if s not in byt and s not in used_ctrl and sic_of(s)==sic]
    picked=0
    for cs in cands:
        got=calls_between(cs, pre0, t0)
        if len(got)<1: continue
        for rec in got: emit(cs, rec, "control", t0, uni_name[cs], sic)
        used_ctrl.add(cs); picked+=1
        if picked>=2: break

with open(OUT+"/a2_calls.jsonl","w") as f:
    for r in rows: f.write(json.dumps(r)+"\n")
c=collections.Counter(r["window"] for r in rows)
print(f"\n[a2] a2_calls.jsonl: {len(rows)} calls | {dict(c)}")
print(f"[a2] fraud firms with pre-exposure calls: {len(set(r['ticker'] for r in rows if r['window']=='fraud_pre'))}")
print(f"[a2] control firms: {len(set(r['ticker'] for r in rows if r['window']=='control'))}")
json.dump({tk:{"t0":str(m['t0']),"aaer":m['aaer'],"company":m['company'],"sic":fraud_sic.get(tk)} for tk,m in byt.items()},
          open(OUT+"/a2_fraud_firms.json","w"), indent=1)

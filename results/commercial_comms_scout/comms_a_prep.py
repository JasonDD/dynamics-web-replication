#!/usr/bin/env python3
"""comms_a_prep.py — Experiment A prep. Join Bao et al (2020) accounting-fraud labels to SEC EDGAR
10-K filings by CIK, and build a scoring input for a before-vs-after (fraud-active vs clean) event study.

Design (needs no paid gvkey->CIK crosswalk):
  * Fraud firms come from AAER_firm_year.csv (carries CIK) joined to data_FraudDetection_JAR2020.csv
    (carries gvkey, fyear, p_aaer, misstate) on the AAER release number (P_AAER == p_aaer).
  * For each fraud firm we know its misstate=1 fiscal years (fraud active, i.e. BEFORE exposure) and
    its misstate=0 fiscal years (the same firm's clean baseline).
  * WITHIN-FIRM contrast: fraud-active-year filings vs the same firm's clean-year filings.
  * External baseline: a fixed set of large-cap never-flagged firms, scored over comparable years.
EDGAR full text covers 2001+, so we restrict to misstatement fiscal years >= 2001.
"""
import os, json, re, time, urllib.request
import pandas as pd

OUT="the internal corpus store/comms_scout"
os.makedirs(OUT, exist_ok=True)
UA="Kronaxis research jasond@kronaxis.co.uk"
RAW="https://raw.githubusercontent.com/JarFraud/FraudDetection/master/"

def get(url, binary=False, tries=3):
    for t in range(tries):
        try:
            req=urllib.request.Request(url, headers={"User-Agent":UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                d=r.read()
                return d if binary else d.decode("utf-8","ignore")
        except Exception as e:
            if t==tries-1: raise
            time.sleep(1.5)

# --- Bao labels ---
for fn in ["AAER_firm_year.csv","data_FraudDetection_JAR2020.csv"]:
    p=os.path.join(OUT,fn)
    if not os.path.exists(p):
        print(f"[A] downloading {fn}",flush=True)
        open(p,"w").write(get(RAW+fn.replace(" ","%20")))
aaer=pd.read_csv(os.path.join(OUT,"AAER_firm_year.csv"))   # P_AAER,CIK,YEARA,UNDERSTATEMENT
data=pd.read_csv(os.path.join(OUT,"data_FraudDetection_JAR2020.csv"), usecols=["fyear","gvkey","p_aaer","misstate","at"])
print("[A] aaer rows", len(aaer), "| data rows", len(data),flush=True)

# map P_AAER -> gvkey (fraud firms) and gather misstate years per gvkey
fr=data[data["misstate"]==1]
paaer_gvkey=fr.dropna(subset=["p_aaer"]).groupby("p_aaer")["gvkey"].agg(lambda s:s.mode().iat[0]).to_dict()
# CIK per P_AAER from aaer file
paaer_cik=aaer.dropna(subset=["CIK"]).groupby("P_AAER")["CIK"].agg(lambda s:int(s.mode().iat[0])).to_dict()

firms=[]  # (cik, gvkey, misstate_years, clean_years)
for paaer, gvkey in paaer_gvkey.items():
    cik=paaer_cik.get(paaer)
    if not cik: continue
    g=data[data["gvkey"]==gvkey]
    ms=sorted(int(y) for y in g[g["misstate"]==1]["fyear"].dropna().unique())
    cl=sorted(int(y) for y in g[g["misstate"]==0]["fyear"].dropna().unique())
    ms=[y for y in ms if y>=2001]
    if not ms: continue
    firms.append((int(cik), int(gvkey), ms, cl))
print(f"[A] fraud firms with CIK and post-2001 misstate years: {len(firms)}",flush=True)
# rank by (has clean years) then by number of misstate years; cap for feasibility
firms.sort(key=lambda x:(len(x[2])+min(len(x[3]),3)), reverse=True)
firms=firms[:45]

def edgar_filings(cik):
    j=json.loads(get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
    time.sleep(0.15)
    r=j["filings"]["recent"]; name=j.get("name","")
    out=[]
    for i in range(len(r["form"])):
        if r["form"][i] in ("10-K",):
            out.append({"acc":r["accessionNumber"][i].replace("-",""),
                        "doc":r["primaryDocument"][i],
                        "fdate":r["filingDate"][i],
                        "pend":r.get("reportDate",r.get("periodOfReport",[None]*len(r["form"])))[i]})
    return name, out

def extract_prose(html):
    t=re.sub(r"(?is)<script.*?</script>"," ",html)
    t=re.sub(r"(?is)<style.*?</style>"," ",t)
    t=re.sub(r"<[^>]+>"," ",t)
    t=re.sub(r"&#160;|&nbsp;"," ",t); t=re.sub(r"&#[0-9]+;"," ",t); t=re.sub(r"&[a-z]+;"," ",t)
    t=re.sub(r"\s+"," ",t)
    # locate MD&A narrative
    low=t.lower()
    for anchor in ["management's discussion and analysis","management s discussion and analysis",
                   "results of operations","risk factors"]:
        i=low.find(anchor)
        # skip the table-of-contents hit: require a second, deeper occurrence
        if i>0:
            j=low.find(anchor, i+80)
            k=j if j>0 else i
            seg=t[k:k+6500]
            if len(seg)>1500 and sum(c.isalpha() for c in seg)/max(1,len(seg))>0.55:
                return seg[:6000]
    # fallback: densest alpha window
    return t[8000:14000]

rows=[]
for n,(cik,gvkey,ms,cl) in enumerate(firms):
    try:
        name, fils=edgar_filings(cik)
    except Exception as e:
        continue
    lo=min(ms)-2; hi=max(ms)+1
    for fdoc in fils:
        pend=fdoc["pend"] or fdoc["fdate"]
        try: py=int(str(pend)[:4])
        except Exception: continue
        if py<lo or py>hi: continue
        label="fraud" if py in ms else ("clean" if py in cl else None)
        if label is None: continue
        url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{fdoc['acc']}/{fdoc['doc']}"
        try:
            html=get(url); time.sleep(0.15)
            prose=extract_prose(html)
        except Exception: continue
        if len(prose)<1200: continue
        rows.append({"id":f"a_{cik}_{py}_{label}","cik":cik,"firm":name,"fyear":py,
                     "filingdate":fdoc["fdate"],"label":label,"group":"fraud_firm","text":prose})
    if (n+1)%10==0: print(f"[A] fraud firms processed {n+1}/{len(firms)} | filings so far {len(rows)}",flush=True)

# external large-cap control baseline (never in Bao AAER set)
CONTROLS={"AAPL":320193,"MSFT":789019,"JNJ":200406,"PG":80424,"KO":21344,"WMT":104169,
          "XOM":34088,"CVX":93410,"IBM":51143,"MMM":66740,"CAT":18230,"HD":354950}
for tk,cik in CONTROLS.items():
    try:
        name, fils=edgar_filings(cik)
    except Exception: continue
    picked=0
    for fdoc in fils:
        pend=fdoc["pend"] or fdoc["fdate"]
        try: py=int(str(pend)[:4])
        except Exception: continue
        if py<2005 or py>2015: continue
        url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{fdoc['acc']}/{fdoc['doc']}"
        try:
            html=get(url); time.sleep(0.15); prose=extract_prose(html)
        except Exception: continue
        if len(prose)<1200: continue
        rows.append({"id":f"a_ctl_{cik}_{py}","cik":cik,"firm":name,"fyear":py,
                     "filingdate":fdoc["fdate"],"label":"control","group":"control_firm","text":prose})
        picked+=1
        if picked>=4: break

with open(os.path.join(OUT,"a_filings.jsonl"),"w") as f:
    for r in rows: f.write(json.dumps(r)+"\n")
import collections
c=collections.Counter(r["label"] for r in rows)
print(f"[A] a_filings.jsonl: {len(rows)} filings | labels {dict(c)} | fraud firms {len(set(r['cik'] for r in rows if r['group']=='fraud_firm'))}",flush=True)

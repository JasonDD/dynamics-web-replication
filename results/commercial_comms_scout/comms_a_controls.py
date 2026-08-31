#!/usr/bin/env python3
"""Top up Experiment A control-firm filings using a recent window (in EDGAR's 'recent' slice)."""
import urllib.request, json, re, time, os
UA="Kronaxis research jasond@kronaxis.co.uk"; OUT="/mnt/nas/kronaxis/corpora/comms_scout"
def get(u):
    req=urllib.request.Request(u,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=60) as r: return r.read().decode("utf-8","ignore")
def extract(html):
    t=re.sub(r"(?is)<script.*?</script>"," ",html); t=re.sub(r"(?is)<style.*?</style>"," ",t)
    t=re.sub(r"<[^>]+>"," ",t)
    t=re.sub(r"&#160;|&nbsp;"," ",t); t=re.sub(r"&#[0-9]+;"," ",t); t=re.sub(r"&[a-z]+;"," ",t)
    t=re.sub(r"\s+"," ",t); low=t.lower()
    for a in ["management s discussion and analysis","results of operations","business overview","risk factors"]:
        i=low.find(a)
        if i>0:
            j=low.find(a,i+80); k=j if j>0 else i; seg=t[k:k+6500]
            if len(seg)>1500 and sum(c.isalpha() for c in seg)/max(1,len(seg))>0.55: return seg[:6000]
    return t[8000:14000]
CTRL={"AAPL":320193,"MSFT":789019,"JNJ":200406,"PG":80424,"KO":21344,"WMT":104169,
      "XOM":34088,"CVX":93410,"IBM":51143,"MMM":66740,"CAT":18230,"HD":354950}
rows=[]
for tk,cik in CTRL.items():
    try:
        j=json.loads(get("https://data.sec.gov/submissions/CIK%010d.json"%cik)); time.sleep(0.15)
    except Exception: continue
    r=j["filings"]["recent"]; name=j.get("name",tk); picked=0
    for i in range(len(r["form"])):
        if r["form"][i]!="10-K": continue
        py=int(str(r["reportDate"][i] or r["filingDate"][i])[:4])
        if py<2016 or py>2024: continue
        acc=r["accessionNumber"][i].replace("-",""); doc=r["primaryDocument"][i]
        url="https://www.sec.gov/Archives/edgar/data/%d/%s/%s"%(cik,acc,doc)
        try: html=get(url); time.sleep(0.15); pr=extract(html)
        except Exception: continue
        if len(pr)<1200: continue
        rows.append({"id":"a_ctl_%d_%d"%(cik,py),"cik":cik,"firm":name,"fyear":py,
                     "filingdate":r["filingDate"][i],"label":"control","group":"control_firm","text":pr})
        picked+=1
        if picked>=4: break
kept=[l for l in open(OUT+"/a_filings.jsonl") if json.loads(l)["label"]!="control"]
with open(OUT+"/a_filings.jsonl","w") as f:
    for l in kept: f.write(l)
    for r in rows: f.write(json.dumps(r)+"\n")
print("controls added:", len(rows), "| distinct control firms:", len(set(r["cik"] for r in rows)))

#!/usr/bin/env python3
"""grice_reduction.py -- does the character instrument recover Gricean pragmatics?

Advisor reduction (Tier 2, the deepest homology): Grice's four maxims of the cooperative principle,
quantity, quality, relation, manner, are the foundational logic of human communication. If our eight
axes predict how far a text VIOLATES each maxim, the instrument is reading that logic, not surface
style. The judge is a DIFFERENT model family from the one that produced the character scores (Mistral
7B, the second reader lineage), so the reduction is not one model correlating with itself.

Corpus: a capped sample of the held reddit_wide comments already scored on the eight axis instrument,
bounded so the run finishes on the idle Mistral endpoints well before the overnight forum scoring needs
them. Each comment gets a 0..1 violation score on each maxim; the four are then correlated with the
eight axes and the matter against manner PC1. Pre stated expectation, written before the correlations
are read: rigour and depth should fall as the QUANTITY and QUALITY maxims are violated (an
uninformative or unsupported comment reads as low matter), and the manner pole axes (affect, register)
should track the MANNER maxim. Aggregate, analysis only.
"""
import os, re, json, time, threading, itertools
from concurrent.futures import ThreadPoolExecutor
import requests, psycopg2, numpy as np, math

URLS=[u.strip() for u in os.environ.get("SCORER_URLS",
      "an internal model endpoint").split(",") if u.strip()]
MODEL=os.environ.get("SCORER_MODEL","mistralai/Mistral-7B-Instruct-v0.2")
WORKERS=int(os.environ.get("WORKERS","48"))
CAP=int(os.environ.get("CAP","15000"))
BODYMAX=int(os.environ.get("BODYMAX","2000"))
DWEB=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
MAXIMS=["quantity","quality","relation","manner"]
OUT=os.path.expanduser("~/grice_out"); os.makedirs(OUT, exist_ok=True)
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
DSN=f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"
_rr=itertools.cycle(URLS); _l=threading.Lock()
def nexturl():
    with _l: return next(_rr)
_ix=threading.local()
def cur():
    if not hasattr(_ix,"c"):
        cx=psycopg2.connect(DSN); cx.autocommit=True; _ix.c=cx.cursor()
    return _ix.c

SYS=("You judge how far ONE online comment violates each of Grice's four maxims of cooperative "
     "communication. Score each 0.0 to 1.0 where 0.0 = fully observes the maxim and 1.0 = flagrantly "
     "violates it. QUANTITY: gives the right amount of information, neither too little nor padded. "
     "QUALITY: says what it has adequate evidence for, not falsehood or unbacked assertion. RELATION: "
     "is relevant and on point. MANNER: is clear, brief and orderly, not obscure or ambiguous. Judge the "
     "COMMUNICATION, not whether you agree. Reply ONLY JSON: "
     '{"quantity":0.0,"quality":0.0,"relation":0.0,"manner":0.0}')

def schema():
    return {"type":"object","properties":{m:{"type":"number"} for m in MAXIMS},"required":MAXIMS,"additionalProperties":False}
def ask(body):
    msgs=[{"role":"user","content":f"{SYS}\n\nCOMMENT:\n{body[:BODYMAX]}"}]
    payload={"model":MODEL,"messages":msgs,"temperature":0.0,"max_tokens":120,"stream":False,
             "response_format":{"type":"json_schema","json_schema":{"name":"maxims","schema":schema(),"strict":True}}}
    r=requests.post(nexturl(), json=payload, timeout=200)
    out=(r.json().get("choices") or [{}])[0].get("message",{}).get("content","") or ""
    m=re.search(r"\{[\s\S]*\}", out)
    if not m: return None
    try: d=json.loads(re.sub(r",\s*([}\]])",r"\1", re.sub(r"//[^\n]*","",m.group(0))))
    except Exception: return None
    try: return {k: float(d[k]) for k in MAXIMS}
    except (TypeError, KeyError, ValueError): return None

def score_one(rid, body):
    try:
        v=ask(body)
        if v is None: return False
        cur().execute("INSERT INTO an internal table(id, quantity, quality, relation, manner) VALUES(%s,%s,%s,%s,%s) "
                      "ON CONFLICT (id) DO UPDATE SET quantity=EXCLUDED.quantity, quality=EXCLUDED.quality, "
                      "relation=EXCLUDED.relation, manner=EXCLUDED.manner", (rid, v["quantity"], v["quality"], v["relation"], v["manner"]))
        return True
    except Exception:
        return False

def main():
    db=psycopg2.connect(DSN); db.autocommit=True; c=db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS an internal table(id text PRIMARY KEY, quantity real, quality real, relation real, manner real)")
    c.execute("""SELECT w.id, w.body FROM the internal Reddit corpus w
                 LEFT JOIN an internal table gg ON gg.id=w.id
                 WHERE w.char IS NOT NULL AND w.char ? 'rigour' AND length(w.body)>=200 AND gg.id IS NULL
                 ORDER BY md5(w.id) LIMIT %s""",(CAP,))
    todo=c.fetchall(); print(f"[grice] {len(todo)} comments to judge (cap {CAP}, workers {WORKERS})", flush=True)
    t0=time.time(); done=0
    for i in range(0, len(todo), 600):
        batch=todo[i:i+600]; ok=0
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            for r in ex.map(lambda x: score_one(x[0],x[1]), batch): ok+=int(r)
        done+=ok
        print(f"[grice] +{ok}/{len(batch)} | total {done} | {done/max(time.time()-t0,1):.1f}/s", flush=True)
    analyse(c)

def analyse(c):
    c.execute("SELECT gg.quantity, gg.quality, gg.relation, gg.manner, w.char, w.subreddit "
              "FROM an internal table gg JOIN the internal Reddit corpus w ON w.id=gg.id WHERE w.char ? 'rigour'")
    Q=[]; CH=[]; subs=[]
    for q,ql,rel,man,ch,sub in c.fetchall():
        ch=ch if isinstance(ch,dict) else json.loads(ch)
        if any(a not in ch for a in DWEB): continue
        Q.append([q,ql,rel,man]); CH.append([float(ch[a]) for a in DWEB]); subs.append(sub)
    Q=np.array(Q,float); CH=np.array(CH,float); subs=np.array(subs)
    n=len(Q); print(f"\n[grice] analysing {n} judged comments", flush=True)
    # PC1
    dref=psycopg2.connect(DSN).cursor(); dref.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
    allc=np.array([[float(x) for x in r] for r in dref.fetchall()],float); MEAN=allc.mean(0); STD=allc.std(0)+1e-9
    _,_,Vt=np.linalg.svd((allc-MEAN)/STD, full_matrices=False); PC1=Vt[0]
    if (PC1[DWEB.index("rigour")]+PC1[DWEB.index("depth")])<0: PC1=-PC1
    PCv=((CH-MEAN)/STD)@PC1
    def pear(a,b):
        a=a-a.mean(); b=b-b.mean(); d=math.sqrt((a*a).sum()*(b*b).sum()); return float((a*b).sum()/d) if d else float("nan")
    rooms=sorted(set(subs)); rc={r_:k for k,r_ in enumerate(rooms)}; g=np.array([rc[s] for s in subs])
    def dm(v):
        m=np.zeros(len(rooms)); nn=np.zeros(len(rooms)); np.add.at(m,g,v); np.add.at(nn,g,1); return v-(m/np.maximum(nn,1))[g]
    summary={"n":n, "n_rooms":len(rooms), "expectation":"rigour/depth fall as quantity+quality violated; affect/register track manner",
             "pc1_vs_maxim":{}, "axes_vs_maxim":{}}
    print("\n=== matter/manner PC1 vs each maxim VIOLATION (item | within room) ===")
    for j,m in enumerate(MAXIMS):
        ri=pear(PCv,Q[:,j]); rw=pear(dm(PCv), dm(Q[:,j]))
        summary["pc1_vs_maxim"][m]=dict(item=ri, within=rw); print(f"  {m:<10} item {ri:+.3f}  within {rw:+.3f}")
    print("\n=== each axis vs each maxim violation (item r) ===")
    for a in DWEB:
        ci=CH[:,DWEB.index(a)]; row={m:pear(ci,Q[:,j]) for j,m in enumerate(MAXIMS)}
        summary["axes_vs_maxim"][a]=row; print(f"  {a:<16} " + "  ".join(f"{m}={row[m]:+.2f}" for m in MAXIMS))
    json.dump(summary, open(f"{OUT}/grice.json","w"), indent=2); print(f"\n[grice] wrote {OUT}/grice.json", flush=True)

if __name__=="__main__":
    main()

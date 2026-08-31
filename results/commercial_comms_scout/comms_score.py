#!/usr/bin/env python3
"""comms_score.py — generic 8-axis character scorer over a JSONL file, same instrument (:8301, qwen2.5-7b-atlas).
Reads INPUT jsonl (each row must have 'id' and 'text'), writes OUTPUT jsonl adding 'axes'.
Self queues behind the running jobs: low WORKERS, resumable (skips ids already in OUTPUT)."""
import os, re, json, sys, time
from concurrent.futures import ThreadPoolExecutor
import requests

TEACHER=os.environ.get("TEACHER_URL","http://127.0.0.1:8301/v1/chat/completions")
MODEL=os.environ.get("TEACHER_MODEL","qwen2.5-7b-atlas")
WORKERS=int(os.environ.get("WORKERS","4"))
AXES=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
SYSTEM=("You analyse the VOICE a web page projects, the character of the writing itself, not the "
        "author's personality and not the topic. The text may not be in English; read it in its own language. "
        "Score each of eight axes as a DECIMAL between 0.0 and 1.0. Reply ONLY JSON: "
        '{"axes":{"rigour":0.5,"depth":0.5,"originality":0.5,"candour":0.5,"affect":0.5,'
        '"commercial_drive":0.5,"stance":0.5,"register":0.5}}')
VOCAB=("rigour: 0 unsourced -> 1 scholarly | depth: 0 superficial -> 1 expert | "
       "originality: 0 rehashed -> 1 primary source | candour: 0 opaque -> 1 transparent | "
       "affect: 0 neutral -> 1 sensational | commercial_drive: 0 reference -> 1 hard sell | "
       "stance: 0 balanced -> 1 polemical | register: 0 institutional -> 1 conversational")

def score_one(row):
    body=(row.get("text") or "")[:6000]
    if not body.strip(): return None
    try:
        msgs=[{"role":"system","content":SYSTEM},{"role":"user","content":f"{VOCAB}\n\nPAGE:\n{body}"}]
        r=requests.post(TEACHER,json={"model":MODEL,"messages":msgs,"temperature":0.0,"max_tokens":200,"stream":False},timeout=180)
        out=(r.json().get("choices") or [{}])[0].get("message",{}).get("content","") or ""
        m=re.search(r"\{[\s\S]*\}",out); ax=(json.loads(m.group(0)).get("axes") if m else None)
        if not ax or not all(k in ax for k in AXES): return None
        o=dict(row); o["axes"]={k:float(ax[k]) for k in AXES}; o.pop("text",None); return o
    except Exception:
        return None

def main():
    inp, outp = sys.argv[1], sys.argv[2]
    done=set()
    if os.path.exists(outp):
        for l in open(outp):
            try: done.add(json.loads(l)["id"])
            except Exception: pass
    rows=[]
    for l in open(inp):
        try:
            r=json.loads(l)
            if r["id"] not in done: rows.append(r)
        except Exception: pass
    print(f"[score] {len(rows)} to score ({len(done)} already done) -> {outp}",flush=True)
    ok=0; t0=time.time()
    with open(outp,"a") as f, ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for i,res in enumerate(ex.map(score_one, rows)):
            if res:
                f.write(json.dumps(res)+"\n"); f.flush(); ok+=1
            if (i+1)%25==0:
                print(f"[score] {i+1}/{len(rows)} ok={ok} {(i+1)/max(1e-9,time.time()-t0):.1f}/s",flush=True)
    print(f"[score] DONE ok={ok}/{len(rows)} in {time.time()-t0:.0f}s",flush=True)

if __name__=="__main__":
    main()

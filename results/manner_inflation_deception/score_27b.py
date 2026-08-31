#!/usr/bin/env python3
"""score_27b.py — score input_27b.jsonl on the 27B (:8288, qwen38-extract) with the SAME char
rubric/system/vocab/parse as cc_found_human_score.py. The 27B is a THINKING model, so we disable
thinking (chat_template_kwargs.enable_thinking=false) to get the same direct-JSON behaviour as the
non-thinking 7B — the fair cross-lineage analog. max_model_len=2048, so BODYMAX is trimmed and a
short-body retry protects group balance for the long CMV args.
"""
import os, re, json, threading
from concurrent.futures import ThreadPoolExecutor
import requests

TEACHER = os.environ.get("TEACHER_URL", "http://127.0.0.1:8288/v1/chat/completions")
MODEL   = os.environ.get("TEACHER_MODEL", "qwen38-extract")
WORKERS = int(os.environ.get("WORKERS", "6"))
BODYMAX = int(os.environ.get("BODYMAX", "4500"))
INPUT   = os.environ["INPUT"]; OUT = os.environ["OUT"]

DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
CHAR_SYS = ("You analyse the VOICE a piece of writing projects, the character of the writing itself, not the "
            "author's personality and not the topic. Score each of eight axes as a DECIMAL between 0.0 and 1.0. "
            'Reply ONLY JSON: {"axes":{"rigour":0.5,"depth":0.5,"originality":0.5,"candour":0.5,"affect":0.5,'
            '"commercial_drive":0.5,"stance":0.5,"register":0.5}}')
CHAR_VOCAB = ("rigour: 0 unsourced -> 1 scholarly | depth: 0 superficial -> 1 expert | originality: 0 rehashed -> 1 "
              "primary source | candour: 0 opaque -> 1 transparent | affect: 0 neutral -> 1 sensational | "
              "commercial_drive: 0 reference -> 1 hard sell | stance: 0 balanced -> 1 polemical | register: 0 "
              "institutional -> 1 conversational")

def _post(body, mt=150):
    msgs = [{"role":"system","content":CHAR_SYS},
            {"role":"user","content":f"{CHAR_VOCAB}\n\nTEXT:\n{body}"}]
    r = requests.post(TEACHER, json={"model":MODEL,"messages":msgs,"temperature":0.0,
                                     "max_tokens":mt,"stream":False,
                                     "chat_template_kwargs":{"enable_thinking":False}}, timeout=180)
    out = (r.json().get("choices") or [{}])[0].get("message",{}).get("content","") or ""
    m = re.search(r"\{[\s\S]*\}", out)
    ax = (json.loads(m.group(0)).get("axes") if m else None)
    return {k:float(ax[k]) for k in DWEB} if ax and all(k in ax for k in DWEB) else None

def score(body):
    try:
        ch = _post(body[:BODYMAX])
        if ch: return ch
    except Exception:
        pass
    try:                       # short-body retry (context overflow / parse miss)
        return _post(body[:1800])
    except Exception:
        return None

_wl = threading.Lock()
def emit(rec):
    with _wl:
        with open(OUT,"a") as f: f.write(json.dumps(rec)+"\n")

def main():
    open(OUT,"a").close()
    done=set()
    for l in open(OUT):
        try: done.add(json.loads(l)["id"])
        except: pass
    jobs=[]
    for l in open(INPUT):
        try: r=json.loads(l)
        except: continue
        if r["id"] in done: continue
        jobs.append(r)
    print(f"to score: {len(jobs)} (done {len(done)})", flush=True)
    n=[0]
    def work(r):
        ch=score(r["text"])
        if ch: emit({"id":r["id"],"kind":r["kind"],"outcome":r["outcome"],"char":ch})
        n[0]+=1
        if n[0]%100==0: print(f"  scored {n[0]}/{len(jobs)}", flush=True)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, jobs))
    print(f"done: {n[0]} attempted", flush=True)

if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""score_27b_generic.py — score an input JSONL on the 27B (, an internal model) with the CANONICAL
rubric (RUBRIC=char | disp), byte-for-byte the same system/vocab/parse as the manipulation-programme
second-lineage scorers (score_27b.py for char, cc_crosssite_score_27b.py for disp). Only the model differs
from the 7B run, so this is a like-for-like cross-lineage re-score.

RUBRIC=char : DYNAMICS-WEB voice axes (rigour..register), max_tokens 150, BODYMAX 4500, short-body retry 1800.
RUBRIC=disp : DYNAMICS-8 disposition axes (discipline..sociability), max_tokens 220, BODYMAX 3000.

an internal model is a thinking model; thinking is DISABLED (chat_template_kwargs.enable_thinking=false) for the same
direct-JSON behaviour as the non-thinking 7B — the fair cross-lineage analog. Resumable by id; passes through
every non-text field of the input record. Env: INPUT, OUT, RUBRIC(char), WORKERS(16), TEACHER_URL, TEACHER_MODEL.
"""
import os, re, json, threading
from concurrent.futures import ThreadPoolExecutor
import requests

TEACHER = os.environ.get("TEACHER_URL", "an internal model endpoint")
MODEL   = os.environ.get("TEACHER_MODEL", "an internal model")
WORKERS = int(os.environ.get("WORKERS", "16"))
RUBRIC  = os.environ.get("RUBRIC", "char")
INPUT   = os.environ["INPUT"]; OUT = os.environ["OUT"]

DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
D8   = ["discipline","yielding","novelty","acuity","mercuriality","impulsivity","candour","sociability"]

CHAR_SYS = ("You analyse the VOICE a piece of writing projects, the character of the writing itself, not the "
            "author's personality and not the topic. Score each of eight axes as a DECIMAL between 0.0 and 1.0. "
            'Reply ONLY JSON: {"axes":{"rigour":0.5,"depth":0.5,"originality":0.5,"candour":0.5,"affect":0.5,'
            '"commercial_drive":0.5,"stance":0.5,"register":0.5}}')
CHAR_VOCAB = ("rigour: 0 unsourced -> 1 scholarly | depth: 0 superficial -> 1 expert | originality: 0 rehashed -> 1 "
              "primary source | candour: 0 opaque -> 1 transparent | affect: 0 neutral -> 1 sensational | "
              "commercial_drive: 0 reference -> 1 hard sell | stance: 0 balanced -> 1 polemical | register: 0 "
              "institutional -> 1 conversational")

DISP_SYS = ("You are given ONE block of text written by a person somewhere on the web. Infer the DISPOSITION of "
            "the PERSON who wrote it from HOW THEY WRITE and what they choose to say — the kind of person, not the "
            "topic. The text may not be in English; read it in its own language. Score each of eight personality "
            "axes as a DECIMAL between 0.0 and 1.0 where 0.5 is the population average. Reply ONLY JSON: "
            '{"axes":{"discipline":0.5,"yielding":0.5,"novelty":0.5,"acuity":0.5,"mercuriality":0.5,'
            '"impulsivity":0.5,"candour":0.5,"sociability":0.5}}')
DISP_VOCAB = ("discipline: 0 careless -> 1 organised, diligent | yielding: 0 holds firm, challenges -> 1 persuadable, "
              "compliant | novelty: 0 conventional -> 1 seeks the new | acuity: 0 low digital fluency -> 1 fluent, "
              "sharp | mercuriality: 0 even, calm -> 1 volatile, reactive | impulsivity: 0 deliberate -> 1 reward "
              "driven, impulsive | candour: 0 guarded, strategic -> 1 frank, sincere | sociability: 0 reserved -> 1 "
              "outgoing, warm")

if RUBRIC == "disp":
    SYS, VOCAB, KEYS, MAXTOK, BODYMAX = DISP_SYS, DISP_VOCAB, D8, 220, int(os.environ.get("BODYMAX", "3000"))
else:
    SYS, VOCAB, KEYS, MAXTOK, BODYMAX = CHAR_SYS, CHAR_VOCAB, DWEB, 150, int(os.environ.get("BODYMAX", "4500"))


def _post(body, mt):
    msgs = [{"role":"system","content":SYS},
            {"role":"user","content":f"{VOCAB}\n\nTEXT:\n{body}"}]
    r = requests.post(TEACHER, json={"model":MODEL,"messages":msgs,"temperature":0.0,"max_tokens":mt,
                                     "stream":False,"chat_template_kwargs":{"enable_thinking":False}}, timeout=200)
    out = (r.json().get("choices") or [{}])[0].get("message",{}).get("content","") or ""
    m = re.search(r"\{[\s\S]*\}", out)
    ax = (json.loads(m.group(0)).get("axes") if m else None)
    return {k:float(ax[k]) for k in KEYS} if ax and all(k in ax for k in KEYS) else None


def score(body):
    try:
        ch = _post(body[:BODYMAX], MAXTOK)
        if ch: return ch
    except Exception:
        pass
    try:
        return _post(body[:1800], MAXTOK)      # short-body retry (context overflow / parse miss)
    except Exception:
        return None


_wl = threading.Lock()
def emit(rec):
    with _wl:
        with open(OUT, "a") as f: f.write(json.dumps(rec) + "\n")


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "a").close()
    done = set()
    for l in open(OUT):
        try: done.add(json.loads(l)["id"])
        except Exception: pass
    jobs = []
    for l in open(INPUT):
        try: r = json.loads(l)
        except Exception: continue
        if r["id"] in done: continue
        jobs.append(r)
    print(f"[{RUBRIC}] to score: {len(jobs)} (already done {len(done)})", flush=True)
    n = [0]
    def work(r):
        ch = score(r["text"])
        if ch:
            rec = {k: v for k, v in r.items() if k != "text"}
            rec["axes"] = ch
            emit(rec)
        n[0] += 1
        if n[0] % 200 == 0: print(f"  [{RUBRIC}] scored {n[0]}/{len(jobs)}", flush=True)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, jobs))
    print(f"[{RUBRIC}] done: {n[0]} attempted", flush=True)


if __name__ == "__main__":
    main()

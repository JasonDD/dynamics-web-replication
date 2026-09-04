#!/usr/bin/env python3
"""prep_27b.py — build a BALANCED 3-group sample for the 27B cross-lineage confirmation of the
manipulation signature, and the matched 7B baseline on the SAME items.

Groups (same definitions as manip_analyse.py):
  MANIP    = IRA political trolls (RightTroll/LeftTroll/Fearmonger)   kind=ira, outcome in POL
  SINCERE  = ChangeMyView winning-args (sincere persuasion)           kind=arg
  SHORTPOL = LIAR PolitiFact statements (length-matched short pol)    kind=liar

Writes:
  input_27b.jsonl    {id,text,outcome,kind}  -> fed to the 27B scorer
  baseline_7b.jsonl  {id,kind,outcome,char}  -> the 7B scores for the SAME ids (paired comparison)
"""
import json, random
random.seed(1729)
N_PER = 450
POL = {"RightTroll", "LeftTroll", "Fearmonger"}
DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]

W = "the internal corpus store/ira_troll/work"
CMV_SCORES = "the internal corpus store/cmv_winning_args/cmv_scores.jsonl"
CMV_UTT = "the internal corpus store/cmv_winning_args/winning-args-corpus/utterances.jsonl"
OUT_IN = "the internal corpus store/ira_troll/work/input_27b.jsonl"
OUT_B7 = "the internal corpus store/ira_troll/work/baseline_7b.jsonl"

def has8(ch): return ch and all(a in ch for a in DWEB)

# id -> text  (ira + liar)
text = {}
for l in open(f"{W}/score_input.jsonl"):
    try: r=json.loads(l)
    except: continue
    text[r["id"]] = r["text"]

# id -> 7B char (ira + liar), and outcome/kind
b7 = {}
for l in open(f"{W}/scored.jsonl"):
    try: r=json.loads(l)
    except: continue
    if has8(r.get("char")):
        b7[r["id"]] = r

# ---- MANIP: ira POL with 7B char AND text ----
manip_ids = [i for i,r in b7.items() if r.get("kind")=="ira" and r.get("outcome") in POL and i in text]
# ---- SHORTPOL: liar with 7B char AND text ----
liar_ids  = [i for i,r in b7.items() if r.get("kind")=="liar" and i in text]
random.shuffle(manip_ids); random.shuffle(liar_ids)
manip_ids = manip_ids[:N_PER]; liar_ids = liar_ids[:N_PER]

# ---- SINCERE: CMV args with 7B char, join text from utterances ----
cmv7 = {}
for l in open(CMV_SCORES):
    try: r=json.loads(l)
    except: continue
    if r.get("kind")=="arg" and has8(r.get("char")):
        cmv7[r["id"]] = r
cmv_text = {}
for l in open(CMV_UTT):
    try: u=json.loads(l)
    except: continue
    if u["id"] in cmv7:
        t = u.get("text","") or ""
        if len(t.split()) >= 10:
            cmv_text[u["id"]] = t
cmv_ids = [i for i in cmv7 if i in cmv_text]
random.shuffle(cmv_ids); cmv_ids = cmv_ids[:N_PER]

# ---- write ----
with open(OUT_IN,"w") as fin, open(OUT_B7,"w") as fb:
    for i in manip_ids:
        fin.write(json.dumps({"id":i,"text":text[i],"outcome":b7[i]["outcome"],"kind":"ira"})+"\n")
        fb.write(json.dumps({"id":i,"kind":"ira","outcome":b7[i]["outcome"],"char":b7[i]["char"]})+"\n")
    for i in liar_ids:
        fin.write(json.dumps({"id":i,"text":text[i],"outcome":b7[i]["outcome"],"kind":"liar"})+"\n")
        fb.write(json.dumps({"id":i,"kind":"liar","outcome":b7[i]["outcome"],"char":b7[i]["char"]})+"\n")
    for i in cmv_ids:
        fin.write(json.dumps({"id":i,"text":cmv_text[i],"outcome":"cmv","kind":"arg"})+"\n")
        fb.write(json.dumps({"id":i,"kind":"arg","outcome":"cmv","char":cmv7[i]["char"]})+"\n")

print(f"MANIP(ira POL)={len(manip_ids)}  SHORTPOL(liar)={len(liar_ids)}  SINCERE(cmv)={len(cmv_ids)}  total={len(manip_ids)+len(liar_ids)+len(cmv_ids)}")
print(f"wrote {OUT_IN} and {OUT_B7}")

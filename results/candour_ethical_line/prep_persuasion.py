#!/usr/bin/env python3
"""prep_persuasion.py — build one {id,text,outcome,kind} JSONL for the two legit
persuasion groups the candour ethical line test still needs scored:

  donorschoose : teacher classroom funding appeals (charity / fundraising persuasion)
                 outcome = approved / notapproved (kept as context, both are genuine appeals)
  amazon       : product reviews (a commercial genre, honest user copy)

Both are legitimate persuasion or commercial copy that is open about its intent, so both
should read HIGH candour if candour is the ethical line. Balanced, capped to keep the
 pass small and not starve sibling jobs.

IRA / CMV / kickstarter / psg / dark / phish / LIAR / Mathur are already scored and folded
in at analysis time, not here.
"""
import os, json, random

random.seed(1729)
OUT = "the internal corpus store/candour_line/input.jsonl"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
CAP_DC = 600
CAP_AZ = 600
rows = []

def add(kind, outcome, text, i):
    text = (text or "").strip()
    if len(text.split()) < 5:
        return
    rows.append({"id": f"{kind}_{i}", "text": text[:6000], "outcome": outcome, "kind": kind})

# ---- DONORSCHOOSE: charity/education funding appeals ----
dc_appr, dc_rej = [], []
for l in open("the internal corpus store/donorschoose/donorschoose.jsonl"):
    try:
        r = json.loads(l)
    except Exception:
        continue
    parts = [r.get("project_title") or ""]
    for k in ("project_essay_1", "project_essay_2", "project_essay_3", "project_essay_4"):
        v = r.get(k)
        if v and str(v) != "None":
            parts.append(str(v))
    parts.append(r.get("project_resource_summary") or "")
    t = " ".join(p for p in parts if p).strip()
    if len(t.split()) < 20:
        continue
    (dc_appr if str(r.get("project_is_approved")) == "1" else dc_rej).append(t)
    if len(dc_appr) >= 20000 and len(dc_rej) >= 20000:
        break
random.shuffle(dc_appr); random.shuffle(dc_rej)
for i, t in enumerate(dc_appr[:CAP_DC]):
    add("donorschoose", "approved", t, f"a{i}")
for i, t in enumerate(dc_rej[:CAP_DC // 3]):   # a few rejected as within genre spread
    add("donorschoose", "notapproved", t, f"r{i}")
print(f"donorschoose: approved pool={len(dc_appr)} rejected pool={len(dc_rej)}", flush=True)

# ---- AMAZON: product reviews (commercial genre, honest user copy) ----
az = []
for l in open("the internal corpus store/amazon_reviews/amazon_reviews.jsonl"):
    try:
        r = json.loads(l)
    except Exception:
        continue
    t = " ".join([str(r.get("title") or ""), str(r.get("text") or "")]).strip()
    if len(t.split()) < 15:
        continue
    az.append((t, r.get("verified_purchase")))
    if len(az) >= 40000:
        break
random.shuffle(az)
for i, (t, vp) in enumerate(az[:CAP_AZ]):
    add("amazon", "verified" if vp else "unverified", t, f"{i}")
print(f"amazon: pool={len(az)}", flush=True)

random.shuffle(rows)
with open(OUT, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(f"WROTE {len(rows)} rows -> {OUT}", flush=True)

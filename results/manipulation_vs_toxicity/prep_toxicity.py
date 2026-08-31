#!/usr/bin/env python3
"""prep_toxicity.py — acquire the gold-labelled toxicity corpus and assemble the combined
pool the two toxicity comparators run over.

Part A: download the google/civil_comments test split (login free) and build a balanced
        toxic vs clean sample with the gold toxicity float thresholded (toxic>=0.5,
        clean<=0.2 to keep a clean negative band). Writes toxicity_civilcomments/input.jsonl
        {id,text,kind,outcome,gold}.

Part B: assemble one detox_input.jsonl over every evaluation corpus that has an 8-axis score,
        joined by id: dark patterns + phishing (from the manner-inflation prep), IRA political
        trolls (text from the IRA sample), and the toxicity corpus. Only ids that already carry
        an 8-axis character score are included, so the later join is exact.

The 8-axis scores come from truthometer/scripts/cc_found_human_score.py at :8301; the two
toxicity tools run in detox_score.py. Run on DL580 (reaches HF and the NAS).
"""
import os, json, random
random.seed(1729)
NAS = "/mnt/nas/kronaxis/corpora"

# ---------------- Part A: civil_comments gold toxicity sample ----------------
def build_toxicity_corpus(n_per_class=1800):
    from huggingface_hub import hf_hub_download
    import pyarrow.parquet as pq
    outdir = f"{NAS}/toxicity_civilcomments"; os.makedirs(outdir, exist_ok=True)
    p = hf_hub_download("google/civil_comments", "data/test-00000-of-00001.parquet",
                        repo_type="dataset", cache_dir="/home/jason/detox-cache/hf")
    t = pq.read_table(p)
    txt = t.column("text").to_pylist(); tox = t.column("toxicity").to_pylist()
    pos, neg = [], []
    for x, y in zip(txt, tox):
        if x is None or y is None:
            continue
        x = x.strip()
        if len(x.split()) < 3 or len(x) > 2000:
            continue
        if y >= 0.5:
            pos.append(x)
        elif y <= 0.2:
            neg.append(x)
    random.shuffle(pos); random.shuffle(neg)
    N = min(n_per_class, len(pos), len(neg))
    rows = ([{"id": f"tox_p{i}", "text": x, "kind": "toxicity", "outcome": "toxic", "gold": 1} for i, x in enumerate(pos[:N])] +
            [{"id": f"tox_n{i}", "text": x, "kind": "toxicity", "outcome": "clean", "gold": 0} for i, x in enumerate(neg[:N])])
    random.shuffle(rows)
    with open(f"{outdir}/input.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"toxicity corpus: {len(rows)} rows ({N}/class); pool pos={len(pos)} neg={len(neg)}")

# ---------------- Part B: combined detox input over all scored corpora ----------------
def scored_ids(p):
    s = set()
    for l in open(p):
        try:
            s.add(json.loads(l)["id"])
        except Exception:
            pass
    return s

def build_detox_input(ira_cap=4000):
    out = f"{NAS}/manip_vs_tox"; os.makedirs(out, exist_ok=True)
    mi_ids = scored_ids(f"{NAS}/manner_inflation/scored.jsonl")
    ira_ids = scored_ids(f"{NAS}/ira_troll/work/scored.jsonl")
    rows = []
    for l in open(f"{NAS}/manner_inflation/input.jsonl"):
        r = json.loads(l)
        if r["kind"] in ("dark", "phish") and r["id"] in mi_ids:
            rows.append({"id": r["id"], "kind": r["kind"], "outcome": r["outcome"], "text": r["text"]})
    POL = {"RightTroll", "LeftTroll", "Fearmonger"}
    ira = []
    for l in open(f"{NAS}/ira_troll/work/ira_sample.jsonl"):
        r = json.loads(l)
        if r.get("outcome") in POL and r["id"] in ira_ids:
            ira.append({"id": r["id"], "kind": "ira", "outcome": r["outcome"], "text": r["text"]})
    random.shuffle(ira); rows += ira[:ira_cap]
    for l in open(f"{NAS}/toxicity_civilcomments/input.jsonl"):
        r = json.loads(l)
        rows.append({"id": r["id"], "kind": "toxicity", "outcome": r["outcome"], "gold": r["gold"], "text": r["text"]})
    random.shuffle(rows)
    with open(f"{out}/detox_input.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"detox_input: {len(rows)} rows -> {out}/detox_input.jsonl")

if __name__ == "__main__":
    build_toxicity_corpus()
    build_detox_input()

#!/usr/bin/env python3
"""detox_score.py — run two toxicity comparators (the incumbents) over the combined
manipulation + toxicity pool, on CPU so they never fight the GPU scorer at .

Tool 1: Detoxify 'original' (unitary/toxic-bert) — the open reproduction of Google
        Jigsaw / Perspective API's toxicity model.
Tool 2: s-nlp/roberta_toxicity_classifier — an independent RoBERTa toxicity model,
        the cross-family robustness comparator (panel discipline: never one comparator).

Reads INPUT jsonl {id,kind,outcome,text,(gold)}, writes OUT jsonl
{id,kind,outcome,(gold),detox_tox,snlp_tox}. Resumable by id. Batched.
"""
import os, json
import torch, torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from detoxify import Detoxify

INPUT = os.environ["INPUT"]
OUT = os.environ["OUT"]
BATCH = int(os.environ.get("BATCH", "64"))
MAXLEN = 256

torch.set_num_threads(int(os.environ.get("THREADS", "16")))

# Tool 1: Detoxify original (unitary/toxic-bert), CPU
detox = Detoxify("original", device="cpu")

# Tool 2: s-nlp roberta toxicity, CPU
SNLP = "s-nlp/roberta_toxicity_classifier"
stok = AutoTokenizer.from_pretrained(SNLP)
smodel = AutoModelForSequenceClassification.from_pretrained(SNLP)
smodel.eval()
# toxic index: label whose name is exactly 'toxic'
STOX = [i for i, l in smodel.config.id2label.items() if l.lower() == "toxic"]
STOX = STOX[0] if STOX else (len(smodel.config.id2label) - 1)

def snlp_batch(texts):
    enc = stok(texts, padding=True, truncation=True, max_length=MAXLEN, return_tensors="pt")
    with torch.no_grad():
        p = F.softmax(smodel(**enc).logits, dim=-1)
    return [float(row[STOX]) for row in p]

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "a").close()
    done = set()
    for l in open(OUT):
        try:
            done.add(json.loads(l)["id"])
        except Exception:
            pass
    rows = []
    for l in open(INPUT):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r["id"] in done:
            continue
        if (r.get("text") or "").strip():
            rows.append(r)
    print(f"to score: {len(rows)} (already done {len(done)})", flush=True)
    n = 0
    with open(OUT, "a") as f:
        for i in range(0, len(rows), BATCH):
            chunk = rows[i:i + BATCH]
            texts = [(r["text"] or "")[:4000] for r in chunk]
            dt = detox.predict(texts)["toxicity"]
            st = snlp_batch(texts)
            for j, r in enumerate(chunk):
                rec = {"id": r["id"], "kind": r["kind"], "outcome": r["outcome"],
                       "detox_tox": float(dt[j]), "snlp_tox": float(st[j])}
                if "gold" in r:
                    rec["gold"] = r["gold"]
                f.write(json.dumps(rec) + "\n")
            f.flush()
            n += len(chunk)
            if (i // BATCH) % 10 == 0:
                print(f"  scored {n}/{len(rows)}", flush=True)
    print(f"done: {n} scored", flush=True)

if __name__ == "__main__":
    main()

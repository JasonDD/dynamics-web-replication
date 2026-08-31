#!/usr/bin/env python3
"""fetch_modality_fix.py — second pass for the registers the first fetch missed or under-filled:
TED (prepared monologue), podcast (conversational spoken), product descriptions (non-Amazon),
customer complaints, and a deeper CUAD contract pull (first pass deduped to only 27 contracts).
"""
import os, json, re, urllib.request

BASE = "/mnt/nas/kronaxis/corpora"

def outdir(n):
    d = os.path.join(BASE, n); os.makedirs(d, exist_ok=True); return d

def path(n):
    return os.path.join(outdir(n), f"{n}.jsonl")

def already(p):
    try:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return sum(1 for _ in open(p))
    except Exception:
        pass
    return 0

def status(n, st, rows, p, note=""):
    print(f"STATUS|{n}|{st}|{rows}|{p}|{note}", flush=True)

def write(n, recs, note="", force=False):
    p = path(n)
    if already(p) and not force:
        status(n, "HELD", already(p), p, "exists"); return
    good = [r for r in recs if r.get("text") and len(r["text"].strip()) >= 40]
    with open(p, "w") as f:
        for i, r in enumerate(good):
            r.setdefault("id", f"{n}-{i:06d}")
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    status(n, "FETCHED" if good else "FAIL", len(good), p, note)

def hf_stream(repo, config=None, split="train", sample=800):
    from datasets import load_dataset
    last = "unknown"
    for rev in (None, "refs/convert/parquet"):
        try:
            kw = dict(split=split, streaming=True)
            if rev:
                kw["revision"] = rev
            ds = load_dataset(repo, config, **kw) if config else load_dataset(repo, **kw)
            rows = []
            for i, r in enumerate(ds):
                if i >= sample:
                    break
                rows.append(dict(r))
            if rows:
                return rows, f"{repo} {config or ''} rev={rev}"
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:100]}"
    raise RuntimeError(last)

def best_textkey(row, prefer=()):
    for k in prefer:
        if k in row and isinstance(row[k], str) and len(row[k]) > 60:
            return k
    cands = [(len(str(row[k])), k) for k in row if isinstance(row[k], str) and len(str(row[k])) > 60]
    return max(cands)[1] if cands else None


def f_ted():
    n = "ted_talks_spoken"
    for repo, split in [("bigscience-data/roots_en_ted_talks_iwslt", "train"),
                        ("Helsinki-NLP/opus_tedtalks", "train")]:
        try:
            rows, note = hf_stream(repo, split=split, sample=700)
            k = best_textkey(rows[0], prefer=("text", "transcript", "en"))
            if not k:
                continue
            recs = [{"id": f"{n}-{i}", "text": str(r[k]).strip()[:6000], "src": repo}
                    for i, r in enumerate(rows) if len(str(r.get(k, ""))) >= 120]
            if recs:
                write(n, recs, note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)


def f_podcast():
    n = "podcast_spoken"
    for repo, split in [("shuyuej/CC-BY-STEMM-Podcast-Transcripts", "train"),
                        ("Whispering-GPT/lex-fridman-podcast-transcript-audio", "train"),
                        ("ryang2/youtube-podcast-transcripts", "train")]:
        try:
            rows, note = hf_stream(repo, split=split, sample=700)
            k = best_textkey(rows[0], prefer=("transcript", "text", "content"))
            if not k:
                continue
            # long transcripts: chunk to ~3000 chars so each item is a scorable spoken passage
            recs = []
            for r in rows:
                t = str(r.get(k, "")).strip()
                if len(t) < 120:
                    continue
                recs.append({"id": f"{n}-{len(recs)}", "text": t[:6000], "src": repo})
                if len(recs) >= 600:
                    break
            if recs:
                write(n, recs, note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)


def f_products():
    n = "product_descriptions_transactional"
    for repo, prefer in [("LuminaAI/RCL-Ecommerce-Product-Descriptions", ("description", "text", "output")),
                         ("llm-wizard/Product-Descriptions-and-Ads", ("description", "text")),
                         ("amaye15/short-product-descriptions", ("description", "text"))]:
        try:
            rows, note = hf_stream(repo, sample=800)
            k = best_textkey(rows[0], prefer=prefer)
            if not k:
                continue
            recs = [{"id": f"{n}-{i}", "text": str(r[k]).strip()[:1500], "src": repo}
                    for i, r in enumerate(rows) if len(str(r.get(k, ""))) >= 60][:600]
            if recs:
                write(n, recs, note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)


def f_complaints():
    n = "complaints_transactional"
    for repo in ["milesbutler/consumer_complaints"]:
        try:
            rows, note = hf_stream(repo, sample=1500)
            k = best_textkey(rows[0], prefer=("Consumer Complaint", "complaint", "text", "narrative"))
            if not k:
                continue
            recs = [{"id": f"{n}-{i}", "text": str(r[k]).strip()[:2000], "src": repo}
                    for i, r in enumerate(rows) if len(str(r.get(k, ""))) >= 120][:600]
            if recs:
                write(n, recs, note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)


def f_cuad_deep():
    n = "contracts_cuad_technical"
    try:
        rows, note = hf_stream("theatticusproject/cuad-qa", sample=25000)
        seen = set(); recs = []
        for r in rows:
            ctx = str(r.get("context") or "").strip()
            if len(ctx) >= 200:
                h = ctx[:200]
                if h in seen:
                    continue
                seen.add(h)
                recs.append({"id": f"{n}-{len(recs)}", "text": ctx[:2500], "src": "cuad-qa"})
            if len(recs) >= 500:
                break
        if len(recs) > 27:
            write(n, recs, note + f" | deep dedup {len(recs)} contracts", force=True)
        else:
            status(n, "KEPT", already(path(n)), path(n), f"deep pass only found {len(recs)}, kept first pass")
    except Exception as e:
        status(n, "FAIL", 0, path(n), f"{type(e).__name__}: {str(e)[:90]}")


if __name__ == "__main__":
    f_ted(); f_podcast(); f_products(); f_complaints(); f_cuad_deep()
    print("FIX FETCH DONE", flush=True)

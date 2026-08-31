#!/usr/bin/env python3
"""fetch_modality.py — pull free, login-free samples of the REGISTERS/MODALITIES the DYNAMICS-WEB
character instrument has barely seen (spoken, creative, technical/professional, customer/transactional).

Each fetcher is independent and failure tolerant: a wall on one target never blocks the others. Every
corpus lands at /mnt/nas/kronaxis/corpora/<name>/<name>.jsonl as {"id","text",...}. Song LYRICS are
deliberately excluded (copyright). Samples target a few hundred to ~1000 substantive items each.

Run on DL580 (native venv + internet). Emits STATUS|name|status|rows|path|note lines.
"""
import os, json, re, io, gzip, zipfile, urllib.request, urllib.parse, random, time

BASE = "/mnt/nas/kronaxis/corpora"
random.seed(17)

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

def write(n, recs, note=""):
    p = path(n)
    if already(p):
        status(n, "HELD", already(p), p, "exists"); return
    good = [r for r in recs if r.get("text") and len(r["text"].strip()) >= 40]
    with open(p, "w") as f:
        for i, r in enumerate(good):
            r.setdefault("id", f"{n}-{i:06d}")
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    status(n, "FETCHED" if good else "FAIL", len(good), p, note)

def http(url, timeout=60, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0 dweb-atlas"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def hf(repo, config=None, split="train", sample=800, textkeys=None, revs=(None, "refs/convert/parquet")):
    """Generic HF loader with parquet fallback; returns list of raw dict rows (streamed)."""
    from datasets import load_dataset
    last = "unknown"
    for rev in revs:
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
            last = f"{type(e).__name__}: {str(e)[:110]}"
    raise RuntimeError(last)

# ----------------------------------------------------------------------------- SPOKEN
def f_ted():
    n = "ted_talks_spoken"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    for repo, key in [("Rogendo/Ted-Talks", "transcript"), ("gigant/ted_talks", "transcript"),
                      ("learningmachineaz/ted_talks", "text"), ("mteoBdl/ted_talks", "transcript")]:
        try:
            rows, note = hf(repo, sample=700)
            k = key if key in rows[0] else next((c for c in rows[0] if isinstance(rows[0][c], str) and len(str(rows[0][c])) > 200), None)
            if not k:
                continue
            recs = [{"id": f"{n}-{i}", "text": str(r[k]), "src": repo} for i, r in enumerate(rows)]
            write(n, recs, note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)

def f_scotus_oral():
    """Oral-argument turns from the held ConvoKit supreme corpus (spoken register, no fetch)."""
    n = "scotus_oral_spoken"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    utt = None
    for cand in ["/mnt/nas/kronaxis/corpora/supreme/supreme-corpus/utterances.jsonl",
                 "/mnt/nas/kronaxis/corpora/supreme/supreme-corpus/utterances.json"]:
        if os.path.exists(cand):
            utt = cand; break
    if not utt:
        g = None
        for root, _, files in os.walk("/mnt/nas/kronaxis/corpora/supreme"):
            for fn in files:
                if fn.startswith("utterances"):
                    g = os.path.join(root, fn); break
        utt = g
    if not utt:
        status(n, "FAIL", 0, path(n), "no supreme utterances file found"); return
    recs = []
    try:
        with open(utt) as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                t = r.get("text") or ""
                # keep substantive advocate/justice turns (oral argument speech)
                if len(t.strip()) >= 250:
                    recs.append({"id": f"{n}-{len(recs)}", "text": t.strip(),
                                 "speaker": r.get("speaker"), "src": "convokit-supreme"})
                if len(recs) >= 6000:
                    break
    except Exception as e:
        status(n, "FAIL", 0, path(n), f"{type(e).__name__}: {str(e)[:90]}"); return
    random.shuffle(recs)
    write(n, recs[:600], "ConvoKit supreme oral-argument turns (spoken register)")

def f_podcast():
    n = "podcast_spoken"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    for repo, key in [("SamAct/podcast_transcript", "text"),
                      ("MLCommons/peoples_speech", "text"),
                      ("edinburghcstr/ami", "text"),
                      ("distil-whisper/earnings22", "transcription")]:
        try:
            rows, note = hf(repo, sample=600)
            k = key if key in rows[0] else next((c for c in rows[0] if isinstance(rows[0].get(c), str) and len(str(rows[0][c])) > 120), None)
            if not k:
                continue
            recs = [{"id": f"{n}-{i}", "text": str(r[k]), "src": repo} for i, r in enumerate(rows)]
            write(n, recs, note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)

# ----------------------------------------------------------------------------- CREATIVE
def f_movie_dialogs():
    n = "movie_dialogs_creative"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    urls = ["https://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip",
            "http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip"]
    data = None
    for u in urls:
        try:
            data = http(u, timeout=90); break
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:80]}"
    if not data:
        # HF fallback
        try:
            rows, note = hf("cornell-movie-dialog/conversations", sample=1)
        except Exception:
            pass
        status(n, "FAIL", 0, path(n), last); return
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        name = next(x for x in z.namelist() if x.endswith("movie_lines.txt"))
        raw = z.read(name).decode("latin-1")
        lines = []
        for ln in raw.splitlines():
            parts = ln.split(" +++$+++ ")
            if len(parts) == 5 and len(parts[4].strip()) >= 30:
                lines.append(parts[4].strip())
        random.shuffle(lines)
        # group 4 consecutive utterances into a short dialogue chunk so there is enough text
        recs = []
        for i in range(0, min(len(lines), 4000), 4):
            chunk = " / ".join(lines[i:i + 4])
            if len(chunk) >= 80:
                recs.append({"id": f"{n}-{len(recs)}", "text": chunk, "src": "cornell-movie-dialogs"})
        write(n, recs[:600], "Cornell Movie-Dialogs (film/TV dialogue chunks)")
    except Exception as e:
        status(n, "FAIL", 0, path(n), f"{type(e).__name__}: {str(e)[:90]}")

def f_poetry():
    n = "poetry_creative"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    # Allison Parrish Gutenberg Poetry Corpus (public domain), line-level ndjson.gz
    urls = ["http://static.decontextualize.com/gutenberg-poetry-v001.ndjson.gz"]
    data = None
    for u in urls:
        try:
            data = http(u, timeout=120); break
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:80]}"
    if data:
        try:
            txt = gzip.decompress(data).decode("utf-8", "ignore")
            from collections import defaultdict
            bygb = defaultdict(list)
            for ln in txt.splitlines():
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                bygb[r.get("gid")].append(r.get("s", ""))
            gids = list(bygb.keys()); random.shuffle(gids)
            recs = []
            for g in gids:
                stanza = "\n".join(bygb[g][:14])  # ~14 lines = a poem-sized excerpt
                if len(stanza) >= 120:
                    recs.append({"id": f"{n}-{len(recs)}", "text": stanza, "gid": g, "src": "gutenberg-poetry"})
                if len(recs) >= 600:
                    break
            write(n, recs, "Gutenberg Poetry Corpus (public-domain verse, ~14-line excerpts)"); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    # HF fallback
    try:
        rows, note = hf("biglam/gutenberg-poetry-corpus", sample=8000)
        k = next((c for c in rows[0] if isinstance(rows[0].get(c), str)), None)
        recs = [{"id": f"{n}-{i}", "text": str(r[k]), "src": "hf-gutenberg-poetry"} for i, r in enumerate(rows) if len(str(r.get(k, ""))) >= 40][:600]
        write(n, recs, note); return
    except Exception as e:
        status(n, "FAIL", 0, path(n), f"{last} | hf: {type(e).__name__}: {str(e)[:70]}")

def f_fiction():
    n = "fiction_openings_creative"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    for repo, key in [("biglam/gutenberg-fiction", "text"), ("sedthh/gutenberg_english", "TEXT"),
                      ("manu/project_gutenberg", "text")]:
        try:
            rows, note = hf(repo, sample=700)
            k = key if key in rows[0] else next((c for c in rows[0] if isinstance(rows[0].get(c), str) and len(str(rows[0][c])) > 400), None)
            if not k:
                continue
            recs = []
            for i, r in enumerate(rows):
                body = str(r[k]).strip()
                # opening ~1500 chars = the narrative-prose register
                if len(body) >= 300:
                    recs.append({"id": f"{n}-{i}", "text": body[:1800], "src": repo})
            write(n, recs, note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)

# ----------------------------------------------------------------------------- TECHNICAL
def f_arxiv():
    n = "arxiv_abstracts_technical"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    cats = ["cs.LG", "math.PR", "physics.optics", "q-bio.NC", "econ.EM", "stat.ME"]
    recs = []
    for c in cats:
        try:
            q = urllib.parse.urlencode({"search_query": f"cat:{c}", "start": 0, "max_results": 120,
                                        "sortBy": "submittedDate", "sortOrder": "descending"})
            xml = http(f"http://export.arxiv.org/api/query?{q}", timeout=60).decode("utf-8", "ignore")
            for m in re.finditer(r"<entry>([\s\S]*?)</entry>", xml):
                e = m.group(1)
                ab = re.search(r"<summary>([\s\S]*?)</summary>", e)
                ti = re.search(r"<title>([\s\S]*?)</title>", e)
                if ab:
                    recs.append({"id": f"{n}-{len(recs)}", "text": re.sub(r"\s+", " ", ab.group(1)).strip(),
                                 "title": (ti.group(1).strip() if ti else ""), "cat": c, "src": "arxiv-api"})
            time.sleep(3)
        except Exception:
            continue
    write(n, recs, "arXiv abstracts (6 categories, export API)")

def f_pubmed():
    n = "pubmed_abstracts_technical"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    eutils = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    try:
        s = http(f"{eutils}/esearch.fcgi?db=pubmed&term=medicine+2025&retmax=600&retmode=json", timeout=60)
        ids = json.loads(s)["esearchresult"]["idlist"]
    except Exception as e:
        status(n, "FAIL", 0, path(n), f"esearch: {type(e).__name__}: {str(e)[:80]}"); return
    recs = []
    for i in range(0, len(ids), 150):
        batch = ids[i:i + 150]
        try:
            xml = http(f"{eutils}/efetch.fcgi?db=pubmed&id={','.join(batch)}&rettype=abstract&retmode=xml",
                       timeout=90).decode("utf-8", "ignore")
            for m in re.finditer(r"<Abstract>([\s\S]*?)</Abstract>", xml):
                txt = re.sub(r"<[^>]+>", " ", m.group(1))
                txt = re.sub(r"\s+", " ", txt).strip()
                if len(txt) >= 120:
                    recs.append({"id": f"{n}-{len(recs)}", "text": txt, "src": "pubmed-eutils"})
            time.sleep(1)
        except Exception:
            continue
    write(n, recs, "PubMed abstracts (E-utilities)")

def f_cuad():
    n = "contracts_cuad_technical"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    for repo, cfg in [("theatticusproject/cuad-qa", None), ("cuad", None), ("dvgodoy/CUAD_v1", None)]:
        try:
            rows, note = hf(repo, cfg, sample=1500)
            # CUAD-qa: 'context' holds the full contract text; dedup contexts
            seen = set(); recs = []
            for r in rows:
                ctx = r.get("context") or r.get("text") or r.get("answer") or ""
                ctx = str(ctx).strip()
                if len(ctx) >= 200:
                    h = ctx[:120]
                    if h in seen:
                        continue
                    seen.add(h)
                    recs.append({"id": f"{n}-{len(recs)}", "text": ctx[:2000], "src": repo})
                if len(recs) >= 600:
                    break
            if recs:
                write(n, recs, note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)

def f_patent():
    n = "patent_abstracts_technical"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    for repo, cfg, key in [("big_patent", "g", "abstract"), ("ccdv/patent-classification", "abstract", "text"),
                           ("HUPD/hupd", "sample", "abstract")]:
        try:
            rows, note = hf(repo, cfg, sample=700)
            k = key if key in (rows[0] if rows else {}) else next((c for c in rows[0] if "abstract" in c.lower()), None) or next((c for c in rows[0] if isinstance(rows[0].get(c), str) and len(str(rows[0][c])) > 150), None)
            if not k:
                continue
            recs = [{"id": f"{n}-{i}", "text": str(r[k]).strip()[:2000], "src": repo} for i, r in enumerate(rows) if len(str(r.get(k, ""))) >= 120][:600]
            if recs:
                write(n, recs, note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)

# ----------------------------------------------------------------------------- CUSTOMER / TRANSACTIONAL
def f_jobs():
    n = "job_postings_transactional"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    for repo, key in [("cnamuangtoun/resume-job-description-fit", "job_description_text"),
                      ("jacob-hugging-face/job-descriptions", "job_description"),
                      ("lukebarousse/data_analyst_job_postings", "description"),
                      ("nakamoto-yama/job-descriptions", "text")]:
        try:
            rows, note = hf(repo, sample=800)
            k = key if key in rows[0] else next((c for c in rows[0] if "desc" in c.lower() and isinstance(rows[0].get(c), str)), None)
            if not k:
                continue
            seen = set(); recs = []
            for r in rows:
                t = str(r.get(k, "")).strip()
                if len(t) >= 120 and t[:80] not in seen:
                    seen.add(t[:80]); recs.append({"id": f"{n}-{len(recs)}", "text": t[:2000], "src": repo})
            if recs:
                write(n, recs[:600], note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)

def f_products():
    n = "product_descriptions_transactional"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    for repo, key in [("xiyuez/red-dot-design-award-product-description", "text"),
                      ("Ateeqq/Amazon-Product-Description", "description"),
                      ("philschmid/flipkart-product-descriptions", "description"),
                      ("Multilingual-Perspectivist-NLU/product_descriptions", "text")]:
        try:
            rows, note = hf(repo, sample=800)
            k = key if key in rows[0] else next((c for c in rows[0] if ("desc" in c.lower() or "text" in c.lower()) and isinstance(rows[0].get(c), str)), None)
            if not k:
                continue
            recs = [{"id": f"{n}-{i}", "text": str(r[k]).strip()[:1500], "src": repo} for i, r in enumerate(rows) if len(str(r.get(k, ""))) >= 60][:600]
            if recs:
                write(n, recs, note); return
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
    status(n, "FAIL", 0, path(n), last)

def f_complaints():
    n = "complaints_transactional"
    if already(path(n)): status(n, "HELD", already(path(n)), path(n), "exists"); return
    # US CFPB Consumer Complaint Database — free public, consumer narratives
    try:
        url = ("https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
               "?field=complaint_what_happened&size=1200&no_aggs=true&has_narrative=true&format=json")
        data = json.loads(http(url, timeout=120).decode("utf-8", "ignore"))
        hits = data.get("hits", {}).get("hits", data if isinstance(data, list) else [])
        recs = []
        for h in hits:
            src = h.get("_source", h)
            t = (src.get("complaint_what_happened") or "").strip()
            if len(t) >= 120:
                recs.append({"id": f"{n}-{len(recs)}", "text": t[:2000],
                             "product": src.get("product"), "company": src.get("company"), "src": "cfpb"})
        write(n, recs[:600], "CFPB consumer complaint narratives")
    except Exception as e:
        status(n, "FAIL", 0, path(n), f"{type(e).__name__}: {str(e)[:90]}")

FETCHERS = [f_ted, f_scotus_oral, f_podcast, f_movie_dialogs, f_poetry, f_fiction,
            f_arxiv, f_pubmed, f_cuad, f_patent, f_jobs, f_products, f_complaints]

if __name__ == "__main__":
    only = os.environ.get("ONLY", "").split(",") if os.environ.get("ONLY") else None
    for fn in FETCHERS:
        nm = fn.__name__
        if only and nm not in only:
            continue
        try:
            fn()
        except Exception as e:
            print(f"STATUS|{nm}|FAIL|0||toplevel {type(e).__name__}: {str(e)[:100]}", flush=True)
    print("FETCH ALL DONE", flush=True)

#!/usr/bin/env python3
"""pandora_d8_score.py — score the DYNAMICS-8 PERSON instrument on labelled human authors, PER POST.

Person side robustness pass, two tier design (per the coupling framework: a single text is a PERFORMED
state, ~3/4 room and ~1/4 stable trait, so a single scored post is attenuated by design; the stable
person emerges only when the performed room is averaged out across many of the author's posts).

The DYNAMICS-8 disposition instrument (the disp_d8_behav prompt from reddit_wide_dispbehav.py) has eight
axes that ARE the six HEXACO / Big Five factors reframed and renamed plus two added levers. We score it on
EACH INDIVIDUAL POST of each author (not the concatenation), so the analyse step can build:
  1. PER TEXT tier   — each single post D8 reading vs the author gold label (predict weak: the control).
  2. PERSON tier     — mean of an author's per post D8 readings vs the gold label (predict recovers).
  3. the r vs k curve — correlation as more of the author's posts are pooled (predict climbs).

Corpus: MBTI (PersonalityCafe posts + self reported four letter type, Kaggle datasnaek mirror). Each row is
one author, text = up to 50 posts joined by triple pipe. Same 7B atlas model as the content baseline, so the
instrument is the only thing that changed.

Output: one JSON line per (author, post) — {uid, pidx, ptype, O,C,E,A, axes:{...}} — resumable.
Endpoint :8301, model qwen2.5-7b-atlas, temp 0.0, modest concurrency (shared 7B GPU).
"""
import os, json, time, random, threading, queue
import pandas as pd
import urllib.request

CORP = "/mnt/nas/kronaxis/corpora/pandora"
OUT = os.path.join(CORP, "user_d8_perpost_scores.jsonl")
N = int(os.environ.get("N", "800"))                 # authors sampled
MAXPOSTS = int(os.environ.get("MAXPOSTS", "40"))    # cap posts scored per author (for the k curve)
MINLEN = int(os.environ.get("MINLEN", "40"))        # skip near empty posts
SEED = int(os.environ.get("SEED", "42"))
WORKERS = int(os.environ.get("WORKERS", "8"))
ALL_ENDPOINTS = ["http://127.0.0.1:8301/v1/chat/completions",
                 "http://127.0.0.1:8302/v1/chat/completions"]


def live_endpoints():
    live = []
    for ep in ALL_ENDPOINTS:
        try:
            base = ep.rsplit("/v1/", 1)[0] + "/v1/models"
            urllib.request.urlopen(base, timeout=5).read()
            live.append(ep)
        except Exception:
            pass
    return live or ALL_ENDPOINTS[:1]

D8 = ["discipline", "yielding", "novelty", "acuity", "mercuriality", "impulsivity", "candour", "sociability"]
SYS = ("You are given ONE short post written by a person. Infer THAT PERSON'S disposition from HOW THEY "
       "WRITE and what they choose to say — the kind of person, not the topic. Score each of eight "
       "personality axes as a DECIMAL between 0.0 and 1.0 where 0.5 is the population average. Reply ONLY "
       'JSON: {"axes":{"discipline":0.5,"yielding":0.5,"novelty":0.5,"acuity":0.5,"mercuriality":0.5,'
       '"impulsivity":0.5,"candour":0.5,"sociability":0.5}}')
VOCAB = ("discipline: 0 careless, unstructured -> 1 organised, diligent, prudent | "
         "yielding: 0 resists influence, holds firm, challenges -> 1 persuadable, compliant, yields | "
         "novelty: 0 incurious, traditional, conformist -> 1 inquisitive, unconventional, novelty seeking | "
         "acuity: 0 low digital fluency, late adopter -> 1 platform native, privacy aware, early adopter | "
         "mercuriality: 0 emotionally stable, consistent -> 1 emotionally reactive, anxious, volatile | "
         "impulsivity: 0 deliberate, delays gratification -> 1 acts on urges, sensation seeking | "
         "candour: 0 manipulative, status seeking, self aggrandising -> 1 transparent, fair, modest | "
         "sociability: 0 reserved, solitary, lurker -> 1 socially bold, gregarious, high output")


def score(text, ep):
    body = json.dumps({
        "model": "qwen2.5-7b-atlas", "temperature": 0.0, "max_tokens": 200, "stream": False,
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": VOCAB + "\n\nPOST:\n" + text[:1500]}],
    }).encode()
    req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    content = d["choices"][0]["message"]["content"]
    a = content.find("{"); b = content.rfind("}")
    obj = json.loads(content[a:b + 1])
    ax = obj["axes"]
    return {k: float(ax[k]) for k in D8}


def main():
    df = pd.concat([pd.read_parquet(os.path.join(CORP, f"mbti_{s}.parquet"))
                    for s in ["train", "validation", "test"]], ignore_index=True)
    df = df.reset_index(drop=True)
    rng = random.Random(SEED)
    idx = list(df.index)
    rng.shuffle(idx)
    idx = idx[:N]

    # build the (uid, pidx, post) work list
    tasks = []
    meta = {}
    for i in idx:
        row = df.loc[i]
        posts = [p.strip() for p in str(row["text"]).split("|||")]
        posts = [p for p in posts if len(p) >= MINLEN][:MAXPOSTS]
        meta[int(i)] = {"ptype": str(row["ptype"]),
                        "O": int(row["O"]), "C": int(row["C"]), "E": int(row["E"]), "A": int(row["A"])}
        for pidx, p in enumerate(posts):
            tasks.append((int(i), pidx, p))

    done = set()
    kept = []
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if "axes" in r:
                done.add((r["uid"], r["pidx"])); kept.append(line)
        with open(OUT, "w") as w:
            w.writelines(kept)
    todo = [t for t in tasks if (t[0], t[1]) not in done]

    ENDPOINTS = live_endpoints()
    print(f"[d8pp] live endpoints: {ENDPOINTS}", flush=True)
    print(f"[d8pp] authors {len(idx)}, total posts {len(tasks)}, already done {len(done)}, todo {len(todo)}",
          flush=True)

    q = queue.Queue()
    for t in todo:
        q.put(t)
    lock = threading.Lock()
    fh = open(OUT, "a")
    counters = {"ok": 0, "err": 0}

    def worker(wid):
        ep = ENDPOINTS[wid % len(ENDPOINTS)]
        while True:
            try:
                uid, pidx, post = q.get_nowait()
            except queue.Empty:
                return
            m = meta[uid]
            rec = {"uid": uid, "pidx": pidx, "ptype": m["ptype"],
                   "O": m["O"], "C": m["C"], "E": m["E"], "A": m["A"]}
            ok = False
            for attempt in range(3):
                try:
                    rec["axes"] = score(post, ep)
                    ok = True
                    break
                except Exception as e:
                    rec["err"] = str(e)[:120]
                    time.sleep(1.0 * (attempt + 1))
            with lock:
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                counters["ok" if ok else "err"] += 1
                n = counters["ok"] + counters["err"]
                if n % 200 == 0:
                    dt = time.time() - t0
                    print(f"[d8pp] {n}/{len(todo)} ok={counters['ok']} err={counters['err']} "
                          f"{n/max(1e-9,dt):.1f}/s", flush=True)
            q.task_done()

    ts = [threading.Thread(target=worker, args=(w,)) for w in range(WORKERS)]
    t0 = time.time()
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    fh.close()
    print(f"[d8pp] COMPLETE ok={counters['ok']} err={counters['err']} in {time.time()-t0:.0f}s -> {OUT}",
          flush=True)


if __name__ == "__main__":
    main()

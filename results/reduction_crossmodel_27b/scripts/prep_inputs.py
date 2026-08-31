#!/usr/bin/env python3
"""prep_inputs.py — build the three 27B re-score input JSONLs (RUN ON DL580, DB is local there).

Writes to WD (default /mnt/nas/kronaxis/crossmodel_27b):
  elm_input.jsonl      {id, text, outcome, kind}          all 2500 IBM ArgQ items (from the benchmark text file)
  biber_input.jsonl    {id, text, subreddit}              stratified reddit_wide: up to PER_SUB per subreddit
  fleeson_input.jsonl  {id, text, ident, domain}          multi-site persons: 1 block per domain, up to MAXDOM domains

Sample designs (stated for the honest bound):
  ELM     : full census, 2500 items.
  BIBER   : per-subreddit cap PER_SUB (default 25) over scored docs (char has rigour, body>=200 chars). Deterministic
            by md5(id). Only subreddits with >=20 sampled docs enter the between-genre centroid test downstream.
  FLEESON : NPERS (default 6000) multi-site persons sampled by md5(ident); one block per (person,domain) chosen by
            md5(id); up to MAXDOM (default 5) domains per person (Fleeson's occasion = a distinct site). >=2 occasions
            guaranteed since selection requires >=2 domains.
"""
import os, json, psycopg2

WD      = os.environ.get("WD", "/mnt/nas/kronaxis/crossmodel_27b")
PER_SUB = int(os.environ.get("PER_SUB", "25"))
NPERS   = int(os.environ.get("NPERS", "6000"))
MAXDOM  = int(os.environ.get("MAXDOM", "5"))
os.makedirs(WD, exist_ok=True)

ELM_TEXT = "/mnt/external/benchmarks/ibm_argq.jsonl"

PW = [l.split("=",1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
DSN = f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"


def elm():
    out = os.path.join(WD, "elm_input.jsonl"); n = 0
    with open(out, "w") as f:
        for l in open(ELM_TEXT):
            r = json.loads(l)
            f.write(json.dumps({"id": r["id"], "text": r["text"],
                                "outcome": r["outcome"], "kind": r.get("kind", "ibm_argq")}) + "\n")
            n += 1
    print(f"[elm] wrote {n} -> {out}", flush=True)


def biber(c):
    out = os.path.join(WD, "biber_input.jsonl")
    c.execute(f"""
      WITH scored AS (
        SELECT id, subreddit, body,
               row_number() OVER (PARTITION BY subreddit ORDER BY md5(id)) rn
        FROM cc_v3.reddit_wide
        WHERE char IS NOT NULL AND char ? 'rigour' AND length(body) >= 200
      )
      SELECT id, subreddit, body FROM scored WHERE rn <= {PER_SUB}
    """)
    rows = c.fetchall(); n = 0
    with open(out, "w") as f:
        for _id, sub, body in rows:
            f.write(json.dumps({"id": _id, "text": body, "subreddit": sub}) + "\n"); n += 1
    subs = len({r[1] for r in rows})
    print(f"[biber] wrote {n} docs across {subs} subreddits (<= {PER_SUB}/sub) -> {out}", flush=True)


def fleeson(c):
    out = os.path.join(WD, "fleeson_input.jsonl")
    c.execute(f"""
      WITH multi AS (
        SELECT ident FROM cc_v3.crosssite_authorship
        WHERE body IS NOT NULL
        GROUP BY ident HAVING count(distinct domain) >= 2
      ),
      picked AS (SELECT ident FROM multi ORDER BY md5(ident::text) LIMIT {NPERS}),
      one_per_dom AS (
        SELECT a.id, a.ident, a.domain, a.body,
               row_number() OVER (PARTITION BY a.ident, a.domain ORDER BY md5(a.id::text)) rn_dom,
               dense_rank() OVER (PARTITION BY a.ident ORDER BY a.domain)          dr
        FROM cc_v3.crosssite_authorship a JOIN picked p USING (ident)
        WHERE a.body IS NOT NULL
      )
      SELECT id, ident, domain, body FROM one_per_dom WHERE rn_dom = 1 AND dr <= {MAXDOM}
    """)
    rows = c.fetchall(); n = 0
    persons = {}
    with open(out, "w") as f:
        for _id, ident, dom, body in rows:
            f.write(json.dumps({"id": _id, "text": body, "ident": ident, "domain": dom}) + "\n"); n += 1
            persons[ident] = persons.get(ident, 0) + 1
    keep = {k: v for k, v in persons.items() if v >= 2}
    print(f"[fleeson] wrote {n} blocks; {len(persons)} persons; {len(keep)} with >=2 occasions -> {out}", flush=True)


def main():
    db = psycopg2.connect(DSN); c = db.cursor()
    elm()
    biber(c)
    fleeson(c)
    print("[prep] done", flush=True)


if __name__ == "__main__":
    main()

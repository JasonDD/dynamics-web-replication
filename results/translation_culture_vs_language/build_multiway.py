#!/usr/bin/env python3
"""build_multiway.py -- build a genuine multi-way parallel Europarl set by exact English-pivot intersection.

Europarl v7 ships line-aligned bilingual pairs (xx-en). Within a pair line i of .xx aligns to line i of .en,
but line numbers do NOT correspond across pairs (segmentation is run per pair). So we join on the ENGLISH
string: an English sentence that appears EXACTLY ONCE in every pair's .en file, with a length in [MINLEN,MAXLEN],
gives an item present in English + all target languages, unambiguously aligned.

Out:
  items_meta.jsonl : {item, len_en, texts:{lang:text}}   (lang in en,de,fr,es,it,fi,pl,el)
  score_input.jsonl: {id:"<item>__<lang>", text, outcome:"", kind:"<lang>"}  (one row per item x lang)
"""
import os, json, random
from collections import Counter

D = "the internal corpus store/europarl_v7"
OUT = "the internal corpus store/europarl_multiway"
os.makedirs(OUT, exist_ok=True)
PAIRS = {"de":"de-en","fr":"fr-en","es":"es-en","it":"it-en","fi":"fi-en","pl":"pl-en","el":"el-en"}
LANGS = ["en","de","fr","es","it","fi","pl","el"]
MINLEN = int(os.environ.get("MINLEN","180"))
MAXLEN = int(os.environ.get("MAXLEN","1200"))
NITEMS = int(os.environ.get("NITEMS","800"))

def load(path):
    with open(path, encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f]

# per-pair unambiguous en->target maps (en appears exactly once in that pair, length-gated)
maps = {}
en_sets = []
for lang, pr in PAIRS.items():
    en = load(os.path.join(D, f"europarl-v7.{pr}.en"))
    tg = load(os.path.join(D, f"europarl-v7.{pr}.{lang}"))
    n = min(len(en), len(tg))
    cnt = Counter(en[i] for i in range(n))
    m = {}
    for i in range(n):
        e = en[i]
        if cnt[e] != 1:            # ambiguous English -> skip
            continue
        if not (MINLEN <= len(e) <= MAXLEN):
            continue
        t = tg[i].strip()
        if len(t) < 20:            # empty/degenerate translation
            continue
        m[e] = t
    maps[lang] = m
    en_sets.append(set(m.keys()))
    print(f"{lang}: pair_lines={n} usable_en={len(m)}", flush=True)

common = set.intersection(*en_sets)
print(f"COMMON English sentences across all {len(PAIRS)} pairs: {len(common)}", flush=True)

common = sorted(common)
random.seed(1234)
random.shuffle(common)
chosen = common[:NITEMS]
print(f"CHOSEN items: {len(chosen)}", flush=True)

meta_p = os.path.join(OUT, "items_meta.jsonl")
inp_p = os.path.join(OUT, "score_input.jsonl")
with open(meta_p, "w", encoding="utf-8") as mf, open(inp_p, "w", encoding="utf-8") as sf:
    for idx, e in enumerate(chosen):
        item = f"it{idx:04d}"
        texts = {"en": e}
        for lang in PAIRS:
            texts[lang] = maps[lang][e]
        mf.write(json.dumps({"item": item, "len_en": len(e), "texts": texts}, ensure_ascii=False) + "\n")
        for lang in LANGS:
            sf.write(json.dumps({"id": f"{item}__{lang}", "text": texts[lang],
                                 "outcome": "", "kind": lang}, ensure_ascii=False) + "\n")
print(f"WROTE {meta_p} and {inp_p} ({len(chosen)} items x {len(LANGS)} langs = {len(chosen)*len(LANGS)} score rows)")

#!/usr/bin/env python3
"""sample_for_scoring.py — pick a within-room gender-balanced sample to score, so scoring stays polite on the
shared GPU while every scored turn sits in a room that also contains the other gender (the atlas control).

For each room (plenary sitting): take up to FCAP female turns, and match an equal number of male turns from
the SAME room by length bucket (so within-room male/female are length-comparable by construction). Rooms with
no female (or no male) scoreable turn are skipped for the gender leg. Every scored turn still carries party /
coalition / nationality / age, so the same scored set feeds the secondary attribute legs.

Env: IN(turns_all), OUT(sample), FCAP(6), NB(6 length buckets), TOTALCAP(3600), SEED(7).
"""
import os, json, random, collections
import numpy as np

IN = os.environ.get("IN", "/mnt/nas/kronaxis/corpora/knesset_corpus/knesset_attribute_turns_all.jsonl")
OUT = os.environ.get("OUT", "/mnt/nas/kronaxis/corpora/knesset_corpus/knesset_attribute_sample.jsonl")
FCAP = int(os.environ.get("FCAP", "6"))
NB = int(os.environ.get("NB", "6"))
TOTALCAP = int(os.environ.get("TOTALCAP", "3600"))
random.seed(int(os.environ.get("SEED", "7")))

by_room = collections.defaultdict(lambda: {"M": [], "F": []})
for l in open(IN):
    try:
        r = json.loads(l)
    except Exception:
        continue
    by_room[r["room"]][r["gender"]].append(r)

# order rooms by how much female representation they carry (richest first), so the cap keeps the best rooms
rooms = sorted(by_room, key=lambda rm: -min(len(by_room[rm]["F"]), len(by_room[rm]["M"])))

sample = []
for rm in rooms:
    F = by_room[rm]["F"]
    M = by_room[rm]["M"]
    if not F or not M:
        continue
    random.shuffle(F)
    fsel = F[:FCAP]
    # length buckets over the room's male turns
    ml = np.array([m["nchars"] for m in M])
    edges = np.quantile(ml, np.linspace(0, 1, NB + 1))
    edges[0] = -1
    edges[-1] = 1e9
    mbuck = collections.defaultdict(list)
    for m in M:
        b = int(np.searchsorted(edges, m["nchars"], side="right") - 1)
        mbuck[b].append(m)
    used = set()
    msel = []
    for fr in fsel:
        b = int(np.searchsorted(edges, fr["nchars"], side="right") - 1)
        cand = [m for m in mbuck.get(b, []) if id(m) not in used]
        if not cand:  # widen to nearest non-empty bucket
            for db in range(1, NB):
                for bb in (b - db, b + db):
                    cand = [m for m in mbuck.get(bb, []) if id(m) not in used]
                    if cand:
                        break
                if cand:
                    break
        if cand:
            m = random.choice(cand)
            used.add(id(m))
            msel.append(m)
    k = min(len(fsel), len(msel))
    sample.extend(fsel[:k])
    sample.extend(msel[:k])
    if len(sample) >= TOTALCAP:
        break

random.shuffle(sample)
with open(OUT, "w") as f:
    for r in sample:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

g = collections.Counter(r["gender"] for r in sample)
print(f"sample: {len(sample)} turns, rooms used, gender {dict(g)} -> {OUT}")

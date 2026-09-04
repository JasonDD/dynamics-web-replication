#!/usr/bin/env python3
"""extract_turns.py — build scoreable speaker turns from the Knesset Corpus with REAL demographics joined.

Reads the held knesset_corpus.jsonl (365 full plenary protocols) plus the member metadata CSVs and emits one
JSON record per plenary TURN (a contiguous speaking turn = all sentences sharing turn_num_in_protocol),
attributed to a Knesset member and carrying that member's GROUND-TRUTH attributes:

  gender (from GenderDesc), nationality (Jewish/Arab/Druze/Bedouin), religion, birth-year -> age at the sitting,
  party/faction (per-knesset, date-window matched), coalition-vs-opposition (per-knesset).

room = protocol_name (one plenary sitting on one date = the internal model "room"). We hold this fixed downstream.

Discipline:
  - numeric speaker_id only (== PersonID). UUID speaker_ids are non-MK guests/officials -> dropped.
  - is_chairman turns dropped (procedural moderation, a role confound, not debate character).
  - is_valid_speaker required; turn must reach MINCHARS real characters.

No scoring here. Output: turns_all.jsonl (id, room, knesset, date, speaker_id, gender, party, faction_id,
coal, nationality, religion, birth_year, age, nchars, text).
"""
import os, json, csv, collections
from datetime import datetime

BASE = "the internal corpus store/knesset_corpus"
CORPUS = os.path.join(BASE, "knesset_corpus.jsonl")
OUT = os.path.join(BASE, "knesset_attribute_turns_all.jsonl")
MINCHARS = int(os.environ.get("MINCHARS", "300"))
MAXCHARS = int(os.environ.get("MAXCHARS", "6000"))

GEN = {"זכר": "M", "נקבה": "F"}
NAT = {"יהודי": "Jewish", "ערבי": "Arab", "דרוזי": "Druze", "בדואי": "Bedouin", "צ'רקסי": "Circassian"}


def parse_date(s):
    s = (s or "").strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:19] if " " in s else s, fmt)
        except Exception:
            pass
    return None


# ---- member personal data: pid -> gender/nat/rel/birth_year ----
demo = {}
with open(os.path.join(BASE, "knesset_members_personal_data.csv"), encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        pid = str(row["PersonID"]).strip()
        dob = parse_date(row.get("DateOfBirth", ""))
        demo[pid] = {
            "gender": GEN.get(row.get("GenderDesc", "").strip(), None),
            "nationality": NAT.get(row.get("Nationality", "").strip(), row.get("Nationality", "").strip() or None),
            "religion": (row.get("Religion", "").strip() or None),
            "birth_year": (dob.year if dob else None),
        }

# ---- per-(pid,knesset) faction rows, with date windows, + General_ID ----
memfac = collections.defaultdict(list)  # (pid,knesset) -> list of {party,fid,gid,start,end}
with open(os.path.join(BASE, "all_knesset_members_personal_and_factions_data.csv"), encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        pid = str(row["PersonID"]).strip()
        kn = str(row.get("כנסת", "")).strip()
        party = (row.get("שם מפלגה אחיד", "").strip() or row.get("סיעה", "").strip() or None)
        memfac[(pid, kn)].append({
            "party": party,
            "fid": (row.get("FactionID", "").strip() or None),
            "gid": (row.get("General_ID", "").strip() or None),
            "start": parse_date(row.get("תאריך התחלה", "")),
            "end": parse_date(row.get("תאריך סיום", "")),
        })

# ---- coalition/opposition by (General_ID, knesset), with date windows ----
coal = collections.defaultdict(list)  # (gid,knesset) -> list of {status,start,end}
COAL = {"קואליציה": "coalition", "אופוזיציה": "opposition"}
with open(os.path.join(BASE, "coalition.csv"), encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        gid = str(row.get("General_ID", "")).strip()
        kn = str(row.get("כנסת", "")).strip()
        status = COAL.get(row.get("שיוך (קואליציה/אופוזיציה)", "").strip(), None)
        coal[(gid, kn)].append({
            "status": status,
            "start": parse_date(row.get("תאריך התחלת חברות בקואליציה/אופוזיציה בכנסת", "")),
            "end": parse_date(row.get("תאריך סיום חברות בקואליציה/אופוזיציה בכנסת", "")),
        })


def pick_window(rows, d):
    """choose the row whose [start,end] window contains date d; else the first row."""
    if not rows:
        return None
    if d is not None:
        for r in rows:
            s, e = r.get("start"), r.get("end")
            if (s is None or s <= d) and (e is None or d <= e):
                return r
    return rows[0]


n_out = 0
n_prot = 0
with open(CORPUS) as fin, open(OUT, "w") as fout:
    for line in fin:
        try:
            p = json.loads(line)
        except Exception:
            continue
        if p.get("protocol_type") != "plenary":
            continue
        room = p.get("protocol_name")
        kn = str(p.get("knesset_number", "")).strip()
        d = parse_date(str(p.get("protocol_date", "")))
        year = d.year if d else None
        # group sentences into contiguous turns
        turns = collections.OrderedDict()
        for s in p.get("protocol_sentences", []):
            if not s.get("is_valid_speaker"):
                continue
            if s.get("is_chairman"):
                continue
            sid = s.get("speaker_id")
            if sid is None:
                continue
            sid = str(sid).strip()
            if not sid.isdigit():  # UUID = non-MK guest
                continue
            t = s.get("turn_num_in_protocol")
            key = (t, sid)
            turns.setdefault(key, []).append(s.get("sentence_text") or "")
        n_prot += 1
        for (t, sid), sents in turns.items():
            if sid not in demo:
                continue
            dm = demo[sid]
            if dm["gender"] is None:
                continue
            text = " ".join(x for x in sents if x).strip()
            nch = len(text)
            if nch < MINCHARS:
                continue
            fr = pick_window(memfac.get((sid, kn), []), d)
            party = fr["party"] if fr else None
            fid = fr["fid"] if fr else None
            gid = fr["gid"] if fr else None
            cr = pick_window(coal.get((gid, kn), []), d) if gid else None
            status = cr["status"] if cr else None
            rec = {
                "id": f"{room}::{t}::{sid}",
                "room": room,
                "knesset": kn,
                "date": (d.strftime("%Y-%m-%d") if d else None),
                "speaker_id": sid,
                "gender": dm["gender"],
                "party": party,
                "faction_id": fid,
                "coal": status,
                "nationality": dm["nationality"],
                "religion": dm["religion"],
                "birth_year": dm["birth_year"],
                "age": ((year - dm["birth_year"]) if (year and dm["birth_year"]) else None),
                "nchars": nch,
                "text": text[:MAXCHARS],
            }
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_out += 1

print(f"protocols(plenary): {n_prot}  turns emitted: {n_out}  -> {OUT}")

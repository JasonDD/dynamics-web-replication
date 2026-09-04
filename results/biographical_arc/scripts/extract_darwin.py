#!/usr/bin/env python3
"""extract_darwin.py — carve individual Darwin-authored letters out of the two
Gutenberg 'Life and Letters of Charles Darwin' volumes (pg2087, pg2088).

Header format is clean and one line:
    CHARLES DARWIN TO <RECIPIENT>. <place>, <date>.
The recipient is an ALL-CAPS run; the place/date part is Title-Case / bracketed.
We keep only letters SENT BY Darwin (sender == CHARLES DARWIN), pull the year
(and month where a month name is present), and take the body as the text between
this header and the next header line.

Writes two files, joined by id:
  - meta.jsonl   : {id, recipient, year, month, age, wordcount, volume}
  - score_in.jsonl : {id, text, outcome, kind}  (what cc_found_human_score.py eats;
                     outcome=year as string, kind=recipient)

Darwin born 12 Feb 1809.  age = (year - 1809) + (month-1)/12 when month known.
"""
import os, re, json

SRC = "the internal corpus store/darwin_letters"
OUTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOLS = {"pg2087.txt": "LL1", "pg2088.txt": "LL2"}

# any letter header (used to find segment boundaries)
HDR_ANY = re.compile(r"^[A-Z][A-Z.'’ &-]+ TO [A-Z]")
# Darwin-authored header prefix; recipient parsed token-wise below (place/date is Title-case)
HDR_CD = re.compile(r"^CHARLES DARWIN TO (.+)$")
UPPER_TOK = re.compile(r"^[A-Z][A-Z.'’&-]*\.?$")  # all-caps token (initials, surnames, honorifics)


def split_recipient(rest):
    """recipient = leading run of ALL-CAPS tokens; the rest (Title-case place / bracket /
    digit) is the place-date part. Returns (recipient, datepart)."""
    toks = rest.split()
    rec = []
    for j, t in enumerate(toks):
        if UPPER_TOK.match(t) and not any(c.islower() for c in t) and "[" not in t and not t[0].isdigit():
            rec.append(t)
        else:
            return " ".join(rec).rstrip("."), " ".join(toks[j:])
    return " ".join(rec).rstrip("."), ""

MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"])}
MONTH_RE = re.compile(r"\b(" + "|".join(MONTHS) + r")\b", re.I)
YEAR_RE = re.compile(r"\b(18[0-9]{2})\b")


def norm_recipient(r):
    r = r.strip().rstrip(".")
    r = re.sub(r"\s+", " ", r)
    # collapse honorifics so 'MISS S. DARWIN' and 'MISS SUSAN DARWIN' don't fragment the count
    return r


def main():
    meta_p = os.path.join(OUTDIR, "meta.jsonl")
    score_p = os.path.join(OUTDIR, "score_in.jsonl")
    mf = open(meta_p, "w")
    sf = open(score_p, "w")
    n_total = 0
    n_kept = 0
    n_nodate = 0
    for fn, vol in VOLS.items():
        path = os.path.join(SRC, fn)
        lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
        # indices of every header line
        hdr_idx = [i for i, ln in enumerate(lines) if HDR_ANY.match(ln)]
        for k, i in enumerate(hdr_idx):
            hdr = lines[i]
            m = HDR_CD.match(hdr)
            if not m:
                continue  # not a Darwin-authored letter
            n_total += 1
            recipient, datepart = split_recipient(m.group(1))
            recipient = norm_recipient(recipient)
            ym = YEAR_RE.search(datepart)
            if not ym:
                n_nodate += 1
                continue
            year = int(ym.group(1))
            mm = MONTH_RE.search(datepart)
            month = MONTHS[mm.group(1).lower()] if mm else None
            age = (year - 1809) + ((month - 1) / 12.0 if month else 0.0)
            # body: from line after header to line before next header
            end = hdr_idx[k + 1] if k + 1 < len(hdr_idx) else len(lines)
            body = "\n".join(lines[i + 1:end]).strip()
            body = re.sub(r"\n{3,}", "\n\n", body)
            wc = len(body.split())
            if wc < 40:
                continue  # too short to score a voice
            _id = f"{vol}-{k:04d}-{year}"
            n_kept += 1
            mf.write(json.dumps({"id": _id, "recipient": recipient, "year": year,
                                 "month": month, "age": round(age, 3),
                                 "wordcount": wc, "volume": vol}) + "\n")
            sf.write(json.dumps({"id": _id, "text": body, "outcome": str(year),
                                 "kind": recipient}) + "\n")
    mf.close()
    sf.close()
    print(f"Darwin-authored headers seen: {n_total}")
    print(f"  dropped (no parseable year): {n_nodate}")
    print(f"  kept (>=40 words, dated):    {n_kept}")
    print(f"meta -> {meta_p}")
    print(f"score_in -> {score_p}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""parse_federalist.py — split the Gutenberg Federalist Papers into 85 papers, attach the
canonical scholarly author labels and the 12 disputed set, and emit a JSONL for scoring.

Canonical attribution (Mosteller & Wallace 1964 / modern consensus):
  Jay:      2,3,4,5,64
  Hamilton: 1,6,7,8,9,11,12,13,15,16,17,21-36,59,60,61,65-85  (sole, undisputed)
  Madison:  10,14,37-48                                        (sole, undisputed)
  Joint:    18,19,20  (Madison with Hamilton)
  Disputed: 49,50,51,52,53,54,55,56,57,58,62,63  (Hamilton OR Madison; consensus = Madison)
"""
import re, json, sys, os

SRC = "the internal corpus store/federalist/federalist.txt"
OUT = os.path.join(os.path.dirname(__file__), "..", "papers.jsonl")
OUT = os.path.abspath(OUT)

JAY      = {2,3,4,5,64}
JOINT    = {18,19,20}
DISPUTED = {49,50,51,52,53,54,55,56,57,58,62,63}
MADISON  = {10,14} | set(range(37,49))            # 37..48
# Hamilton = everything else 1..85
def canon_label(n):
    if n in JAY:      return "JAY"
    if n in JOINT:    return "JOINT_HM"
    if n in DISPUTED: return "DISPUTED"
    if n in MADISON:  return "MADISON"
    return "HAMILTON"

def main():
    txt = open(SRC, encoding="utf-8", errors="replace").read()
    # start after gutenberg header
    start = txt.find("*** START OF THE PROJECT GUTENBERG")
    end   = txt.find("*** END OF THE PROJECT GUTENBERG")
    body  = txt[start:end]
    # split on paper headers, capturing number
    parts = re.split(r"(?m)^FEDERALIST\s+No\.\s+(\d+)\s*$", body)
    # parts = [pre, num1, text1, num2, text2, ...]
    papers = []
    for i in range(1, len(parts), 2):
        num = int(parts[i]); raw = parts[i+1]
        papers.append((num, raw))
    assert len(papers) == 85, f"got {len(papers)} papers"
    recs = []
    for num, raw in papers:
        lines = raw.split("\n")
        # byline = the ALL-CAPS author line before 'To the People'
        byline = ""
        tp = None
        for j,l in enumerate(lines):
            if l.strip().startswith("To the People of the State"):
                tp = j; break
        # search caps line just above 'To the People'
        if tp is not None:
            for k in range(tp-1, max(tp-6,-1), -1):
                s = lines[k].strip()
                if re.fullmatch(r"[A-Z ,.]+", s) and any(c.isalpha() for c in s) and s not in ("",):
                    if any(name in s for name in ("HAMILTON","MADISON","JAY")):
                        byline = s; break
        # body = from 'To the People' onward
        b = "\n".join(lines[tp:]) if tp is not None else raw
        b = b.strip()
        recs.append({"id": f"fed{num:02d}", "paper": num,
                     "label": canon_label(num), "gutenberg_byline": byline,
                     "nchars": len(b), "text": b})
    with open(OUT, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    # summary
    from collections import Counter
    c = Counter(r["label"] for r in recs)
    print("papers:", len(recs))
    for k in ("HAMILTON","MADISON","JAY","JOINT_HM","DISPUTED"):
        print(f"  {k:10} {c[k]}")
    print("disputed papers:", sorted(r["paper"] for r in recs if r["label"]=="DISPUTED"))
    print("median nchars:", sorted(r["nchars"] for r in recs)[len(recs)//2])
    # cross-check gutenberg byline vs canonical for the disputed + a few
    print("\nGutenberg byline vs canonical (disputed set):")
    for r in recs:
        if r["label"]=="DISPUTED":
            print(f"  No.{r['paper']:>2}  gutenberg='{r['gutenberg_byline']}'  canonical=DISPUTED")
    print("\nGutenberg byline for known-Madison (sanity):")
    for r in recs:
        if r["label"]=="MADISON":
            print(f"  No.{r['paper']:>2}  gutenberg='{r['gutenberg_byline']}'")
    print("OUT:", OUT)

if __name__ == "__main__":
    main()

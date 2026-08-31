#!/usr/bin/env python3
"""clean_darwin.py — strip the editor's (Francis Darwin's) voice out of each carved
letter so the character instrument scores Darwin, not his son's footnotes.

Two contaminations:
  1. Editorial footnotes inserted mid-letter inside parentheses — tell-words are
     'father', 'published', "'Life and Letters'", 'volume', 'page', or simply a very
     long parenthetical (Darwin's own asides are short).
  2. Editorial narrative appended after the letter ends — truncate at the last strong
     valediction / signature.

Reads score_in.jsonl + meta.jsonl, writes score_in_clean.jsonl + meta_clean.jsonl
(meta gains ed_frac = fraction of characters removed as editorial, and the cleaned
wordcount). Letters that fall under 40 words after cleaning are dropped.
"""
import os, re, json

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# single-level parenthetical, may span newlines
PAREN = re.compile(r"\(([^()]*)\)", re.S)
ED_TELL = re.compile(r"\b(father|published|volume|\bpage\b|'Life and Letters'|"
                     r"'More Letters'|Autobiography|the editor|footnote)\b", re.I)
# strong sign-offs (true letter end); require near end of body
SIGN = re.compile(r"(yours (?:affectionately|very sincerely|sincerely|truly|ever|"
                  r"faithfully)|ever yours|your affectionate friend|your affectionate|"
                  r"believe me[, ].{0,40}\byours|C\. DARWIN|CHARLES DARWIN)", re.I)


def strip_editorial_parens(t):
    removed = 0

    def rep(m):
        nonlocal removed
        inner = m.group(1)
        wc = len(inner.split())
        if ED_TELL.search(inner) or wc > 30:
            removed_local = len(m.group(0))
            return " \x00" * 0 or ""  # drop it
        return m.group(0)

    # two passes to catch parens revealed after an outer removal
    for _ in range(2):
        before = t
        out = []
        last = 0
        for m in PAREN.finditer(t):
            inner = m.group(1)
            if ED_TELL.search(inner) or len(inner.split()) > 30:
                out.append(t[last:m.start()])
                removed += m.end() - m.start()
                last = m.end()
        out.append(t[last:])
        t = "".join(out)
        if t == before:
            break
    return t, removed


def truncate_after_signoff(t):
    ms = list(SIGN.finditer(t))
    if not ms:
        return t, 0
    m = ms[-1]
    # only trust it as the end if it sits in the last 45% of the text
    if m.start() < 0.55 * len(t):
        return t, 0
    # keep up to the end of the sign-off line
    nl = t.find("\n", m.end())
    cut = nl if nl != -1 else len(t)
    return t[:cut], len(t) - cut


def main():
    meta = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(D, "meta.jsonl"))}
    sin = os.path.join(D, "score_in.jsonl")
    mc = open(os.path.join(D, "meta_clean.jsonl"), "w")
    sc = open(os.path.join(D, "score_in_clean.jsonl"), "w")
    kept = dropped = 0
    for l in open(sin):
        r = json.loads(l)
        orig = r["text"]
        t, rem1 = strip_editorial_parens(orig)
        t, rem2 = truncate_after_signoff(t)
        t = re.sub(r"[ \t]+", " ", t)
        t = re.sub(r"\n{3,}", "\n\n", t).strip()
        wc = len(t.split())
        if wc < 40:
            dropped += 1
            continue
        ed_frac = round((rem1 + rem2) / max(1, len(orig)), 4)
        m = meta[r["id"]]
        m2 = dict(m)
        m2["wordcount_clean"] = wc
        m2["ed_frac"] = ed_frac
        mc.write(json.dumps(m2) + "\n")
        sc.write(json.dumps({"id": r["id"], "text": t, "outcome": r["outcome"], "kind": r["kind"]}) + "\n")
        kept += 1
    mc.close()
    sc.close()
    print(f"kept {kept}, dropped {dropped} (<40 words after cleaning)")


if __name__ == "__main__":
    main()

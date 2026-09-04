#!/usr/bin/env python3
"""cc_controlled_edit_prep.py — build BASE texts + matched controlled-edit VARIANTS for the causal test.

THE CONTROLLED-EDIT CAUSAL TEST. Take fixed base texts spanning lengths, make matched variants, and score
all of them on the SAME 8-axis instrument. Tests (a) does the axis respond causally/directionally to a
deliberate edit, and (b) the asymmetry "MATTER NEEDS BANDWIDTH, MANNER IS INSTANT".

Six cells per base text T:
  base           T unchanged
  matter_insert  T + ~L words of MATTER markers (concrete number, citation/source, caveat, logical connective)
  placebo_insert T + ~L words of NEUTRAL filler (length-matched to matter_insert) -- separates MARKER from LENGTH
  affect_insert  T + ~L words of AFFECT markers (intensifier, urgency, 2nd-person, fear/outrage), length-matched
  affect_rewrite T restyled to be MORE affective with ZERO added words (charged synonym swaps + caps + '!')
  matter_rewrite T restyled to sound MORE rigorous with ZERO added words (formal synonym swaps only, NO content)

The zero-added-word pair (affect_rewrite vs matter_rewrite) is the sharp asymmetry test: affect can be added
without bandwidth, matter cannot (you cannot inject a number/source/evidence without adding content).

Base corpus: Reddit ChangeMyView utterances (single source -> no cross-source confound), sampled across
word-count bins so the set spans lengths including short texts. Deterministic (seeded).

OUT: a JSONL of {id, text, outcome, kind} consumable UNCHANGED by cc_found_human_score.py, where
     id="<base_id>__<variant>", outcome=<variant>, kind="cedit".
"""
import os, re, json, html, random, hashlib

NASC = os.environ.get("NASC", "the internal corpus store")
CMV  = f"{NASC}/cmv_winning_args/winning-args-corpus/utterances.jsonl"
OUT  = os.environ.get("OUT", f"{NASC}/controlled_edit/score_input.jsonl")
SEED = int(os.environ.get("SEED", "1729"))
PER_BIN = int(os.environ.get("PER_BIN", "45"))
BINS = [(5, 15), (15, 40), (40, 100), (100, 250)]   # word-count bins to span lengths

# ---------------------------------------------------------------- marker pools
# Each insert is a self-contained ~30-word clause. Rotated deterministically by base-id hash so no single
# identical string dominates. Matter carries number+source+caveat+connective; placebo is neutral filler of
# the same length; affect carries intensifier+urgency+2nd-person+fear/outrage.
MATTER_INSERTS = [
    "According to a 2019 study published in the American Economic Review, about 42 percent of comparable cases showed this pattern, although the sample was small; therefore the conclusion, while supported, remains provisional.",
    "A 2021 meta analysis in Nature reviewed roughly 3,400 records and found the effect held in 58 percent of trials, but measurement error was substantial, so the estimate should be read as a lower bound.",
    "Government figures from the 2020 census put the rate near 27 per thousand, and while the methodology has known gaps, the trend is consistent across three independent datasets, which strengthens the inference considerably.",
    "The 2018 Cochrane review of 71 controlled studies reported an average difference of 0.34 standard deviations, though heterogeneity was high; consequently the pooled result is best treated as suggestive rather than definitive.",
    "Data released by the Office for National Statistics in 2022 recorded 14,200 instances, and although reporting practices vary between regions, the year on year change of 6 percent is statistically robust.",
]
PLACEBO_INSERTS = [
    "The room had a single window on one side and a plain wooden door on the other, and the grey carpet reached from one wall to the far wall across the entire floor.",
    "Outside the building a row of ordinary parked cars lined the kerb, and a few pigeons walked along the pavement while the traffic light changed slowly from red to green and back again.",
    "In the corner of the office stood a metal filing cabinet with four drawers, and beside it a chair, a small desk, and a lamp that was switched off during most of the day.",
    "The path went past a hedge, then a fence, then a low brick wall, and eventually reached a gate that opened onto a wide field where the grass had recently been cut short.",
    "On the shelf there were several books of different sizes, a mug, a stapler, and a box of paper clips, all arranged in a row that stretched from the left edge to the right.",
]
AFFECT_INSERTS = [
    "This is absolutely outrageous, and you need to understand right now that it is deeply alarming; frankly it terrifies me, and you should be furious too, because time is running out fast.",
    "Honestly this is a disaster, and you cannot afford to ignore it any longer; it is horrifying, it is disgraceful, and if you do not act immediately you will bitterly regret staying silent.",
    "Wake up, because this is genuinely terrifying, and you of all people should be enraged; it is shocking, it is sickening, and every single day you wait the danger grows worse and worse.",
    "You have to see how appalling this really is, and it makes my blood boil; it is a scandal, it is an emergency, and you must be as outraged and frightened as I am now.",
    "This is heartbreaking and utterly infuriating, and you deserve to know the ugly truth right now; it is dangerous, it is unforgivable, and you should be screaming about it before it destroys everything.",
]

# ---------------------------------------------------------------- zero-length restyle lexicons
# Single-word -> single-word swaps (word count preserved). Applied case-insensitively on whole words.
AFFECT_SWAP = {
    "bad": "APPALLING", "good": "AMAZING", "important": "CRUCIAL", "problem": "CRISIS",
    "problems": "CRISES", "said": "SCREAMED", "think": "KNOW", "big": "HUGE", "small": "PATHETIC",
    "wrong": "OUTRAGEOUS", "hard": "BRUTAL", "difficult": "NIGHTMARISH", "sad": "DEVASTATING",
    "angry": "FURIOUS", "issue": "DISASTER", "issues": "DISASTERS", "change": "UPHEAVAL",
    "concern": "TERROR", "risk": "DANGER", "very": "INSANELY", "really": "INCREDIBLY",
    "many": "COUNTLESS", "fine": "TERRIFYING", "okay": "DISTURBING", "interesting": "SHOCKING",
}
MATTER_SWAP = {
    "so": "therefore", "but": "however", "big": "substantial", "small": "marginal",
    "shows": "demonstrates", "show": "demonstrate", "showed": "demonstrated", "use": "employ",
    "used": "employed", "uses": "employs", "get": "obtain", "gets": "obtains", "got": "obtained",
    "help": "facilitate", "helps": "facilitates", "start": "commence", "starts": "commences",
    "end": "conclude", "ends": "concludes", "think": "contend", "thinks": "contends",
    "a lot": "considerably", "really": "substantively", "very": "markedly", "also": "moreover",
    "because": "insofar as", "maybe": "arguably", "kind": "category", "thing": "factor",
    "things": "factors", "way": "mechanism", "ways": "mechanisms", "idea": "proposition",
}

WORD_RE = re.compile(r"[A-Za-z']+")

def clean(t):
    t = html.unescape(t or "")
    t = re.sub(r"&gt;|&lt;|&amp;", " ", t)
    t = re.sub(r"[*_~`#>]", " ", t)          # strip reddit markdown
    t = re.sub(r"\s+", " ", t).strip()
    return t

def wc(t):
    return len(t.split())

def _pick(pool, base_id, salt):
    h = int(hashlib.sha1((base_id + salt).encode()).hexdigest(), 16)
    return pool[h % len(pool)]

def matter_insert(t, bid):
    return (t.rstrip() + " " + _pick(MATTER_INSERTS, bid, "M")).strip()

def placebo_insert(t, bid):
    return (t.rstrip() + " " + _pick(PLACEBO_INSERTS, bid, "P")).strip()

def affect_insert(t, bid):
    return (t.rstrip() + " " + _pick(AFFECT_INSERTS, bid, "A")).strip()

def _swap_words(t, table):
    # multi-word keys first (only "a lot"), then single-word, whole-word, case-insensitive; count preserved.
    for k, v in table.items():
        if " " in k:
            t = re.sub(rf"\b{re.escape(k)}\b", v, t, flags=re.IGNORECASE)
    def rep(m):
        w = m.group(0)
        lw = w.lower()
        return table.get(lw, w)
    return WORD_RE.sub(rep, t)

def affect_rewrite(t, bid):
    """More affect, ZERO added words: charged single-word swaps + terminal '!' + no length change."""
    s = _swap_words(t, {k: v for k, v in AFFECT_SWAP.items() if " " not in k})
    s = re.sub(r"[.]+(\s|$)", r"!\1", s)      # periods -> exclamation (punctuation, not a word)
    if not s.rstrip().endswith(("!", "?")):
        s = s.rstrip() + "!"
    return s

def matter_rewrite(t, bid):
    """More formal/rigorous-sounding, ZERO added words: formal synonym swaps only, NO number/source/evidence."""
    return _swap_words(t, MATTER_SWAP)

VARIANTS = {
    "base":           lambda t, b: t,
    "matter_insert":  matter_insert,
    "placebo_insert": placebo_insert,
    "affect_insert":  affect_insert,
    "affect_rewrite": affect_rewrite,
    "matter_rewrite": matter_rewrite,
}

def main():
    rng = random.Random(SEED)
    buckets = {i: [] for i in range(len(BINS))}
    seen = set()
    for l in open(CMV):
        try:
            r = json.loads(l)
        except Exception:
            continue
        t = clean(r.get("text"))
        if not t or "[deleted]" in t.lower() or "[removed]" in t.lower():
            continue
        n = wc(t)
        for i, (lo, hi) in enumerate(BINS):
            if lo <= n < hi:
                # cap raw pool per bin to keep memory small but allow a random draw
                if len(buckets[i]) < PER_BIN * 8:
                    rid = r.get("id")
                    if rid and rid not in seen:
                        seen.add(rid)
                        buckets[i].append((rid, t, n))
                break
    base = []
    for i in buckets:
        pool = buckets[i]
        rng.shuffle(pool)
        base.extend(pool[:PER_BIN])
    print(f"base texts: {len(base)}  per-bin={[min(len(buckets[i]),PER_BIN) for i in buckets]}", flush=True)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    nrec = 0
    with open(OUT, "w") as f:
        for bid, t, n in base:
            for vname, fn in VARIANTS.items():
                txt = fn(t, bid)
                rec = {"id": f"{bid}__{vname}", "text": txt, "outcome": vname, "kind": "cedit"}
                f.write(json.dumps(rec) + "\n")
                nrec += 1
    # length audit
    import statistics as st
    for vname in VARIANTS:
        ws = []
        for bid, t, n in base:
            ws.append(wc(VARIANTS[vname](t, bid)))
        print(f"  {vname:14s} median_wc={st.median(ws):6.1f}  mean_wc={st.mean(ws):6.1f}", flush=True)
    print(f"wrote {nrec} records ({len(base)} bases x {len(VARIANTS)} variants) -> {OUT}", flush=True)

if __name__ == "__main__":
    main()

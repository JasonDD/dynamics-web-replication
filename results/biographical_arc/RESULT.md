# The biographical arc: does a person's character drift over a whole life, or is the person stable while only the room changes?

**Track:** PUBLIC. **Status:** lab result, cross scorer confirmed (7B + 27B panel).
**Author studied:** Charles Darwin (born 12 February 1809), 451 dated letters he wrote between 1828 and 1882, ages 19 to 73.
**Instrument:** the frozen 8 axis DYNAMICS-WEB character rubric, scored twice for the never one scorer rule (fabric #19098): `qwen2.5-7b-atlas` on DL580 :8301 (canonical) and `qwen38-extract` 27B on :8288 (second lineage).

## The gap this fills

The programme has measured the person's stability ACROSS CONTEXTS (the coupling work: same author, different room, the character holds). It had nothing ACROSS TIME. A whole life is the sternest test of a fixed point: over 54 years a person's status, topic, correspondents and health all turn over completely. If the character axes still do not move once you hold the room fixed, the person is a fixed point in time as well as in space.

## Data and cleaning

Source: the two Gutenberg volumes of *The Life and Letters of Charles Darwin* (ed. Francis Darwin), held on the NAS at `corpora/darwin_letters/` (pg2087, pg2088). Each letter carries a one line header `CHARLES DARWIN TO <RECIPIENT>. <place>, <date>.`, so the letters carve cleanly and every one is dated. We kept only letters Darwin himself wrote (535 headers), pulled the year and, where a month name is present, the month (433 of 453), and set age at writing from his birth date.

The editor (his son) inserts footnotes and narrative in his own voice. Left in, that would score Darwin's son, not Darwin. `clean_darwin.py` strips editorial parentheticals (tell words: father, published, volume, page, or any parenthetical over 30 words) and truncates the trailing editorial narrative at the last valediction. The removed fraction does not track age (r = 0.07), so the residue is noise that pulls toward the null, not a bias that fakes a trend. 453 letters survive at 40 words or more; two failed to score, leaving 451 on the canonical run.

Coverage is dense in the 1850s and 1860s (ages 40 to 60, the working peak) and thin at the tails (one letter in the teens, 15 in the seventies), so read the extreme age bands with caution.

## Cross scorer reliability: which axes can carry weight

Per letter agreement between the 7B and the 27B, 451 paired letters:

| axis | 7B vs 27B r | usable |
|---|---|---|
| affect | 0.49 | yes |
| depth | 0.46 | yes |
| matter minus manner | 0.43 | yes |
| rigour | 0.35 | yes |
| stance | 0.31 | marginal |
| commercial_drive | 0.25 | marginal |
| candour | 0.06 | no |
| originality | 0.02 | no |
| register | -0.29 | no (anti correlated) |

Only rigour, depth, affect and the matter minus manner composite carry real cross scorer signal. candour, originality and register are scorer noise on this corpus, so any trend on them is discarded regardless of its p value. Everything below rests on the four reliable measures.

## Result 1: pooled, there is a clear life arc toward matter

Regressing each axis on age, then on age with log word count (the length control below), on all 451 letters. Slopes are per decade; the Bonferroni floor across 8 axes is p < 0.00625.

Descriptive trajectory by age band (7B, means):

| age band | n | rigour | depth | affect | matter minus manner | PC1 (matter positive) |
|---|---|---|---|---|---|---|
| 20s | 33 | 0.758 | 0.676 | 0.597 | 0.275 | -0.53 |
| 30s | 30 | 0.743 | 0.690 | 0.507 | 0.278 | -0.25 |
| 40s | 85 | 0.722 | 0.698 | 0.514 | 0.282 | -0.27 |
| 50s | 213 | 0.754 | 0.705 | 0.466 | 0.299 | +0.04 |
| 60s | 74 | 0.780 | 0.736 | 0.423 | 0.318 | +0.37 |
| 70s | 15 | 0.820 | 0.787 | 0.400 | 0.363 | +0.96 |

The arc is monotone and both scorers agree on its direction: rigour and depth rise, affect (sensationalism, emotional colour) falls, matter minus manner rises, and the matter oriented PC1 climbs about 0.36 units per decade (7B) to 0.42 (27B), p < 1e-9. Taken at face value this says Darwin's writing character matured steadily over his life toward measured, rigorous, low affect scientific prose. That reading is wrong, and the next two results are why.

## Result 2: length is not the driver

Letters shorten very slightly with age (corr age, log word count = -0.09). The matter needs bandwidth rule holds strongly: log word count is the biggest single predictor of PC1 (coefficient 0.89), so a longer letter reads as more matter. But adding the length control barely moves the age slope (PC1 0.30 raw to 0.36 controlled; matter minus manner 0.020 to 0.023), and often nudges it up rather than down. The pooled arc is real, not a length artefact.

## Result 3: hold the correspondent fixed and the arc vanishes

Who Darwin wrote to turns over across his life. The decisive control is to hold the correspondent fixed and ask whether the same person, writing to the same reader, drifts.

Within his two largest lifelong correspondents, both scorers, length controlled:

| correspondent | span | n | PC1 per decade | p | matter minus manner p |
|---|---|---|---|---|---|
| J.D. Hooker | 1844 to 1881 (37 yrs) | 131 | +0.14 (7B) / -0.10 (27B) | 0.49 / 0.53 | 0.36 / 0.85 |
| C. Lyell | 1838 to 1874 (36 yrs) | 72 | +0.19 / +0.19 | 0.42 / 0.42 | 0.76 / n.a. |

Every axis and every composite goes flat, on both scorers. Hooker spans 3.7 decades: if the pooled 0.36 per decade slope were within person, PC1 would move about 1.3 units across the Hooker letters and be trivially detectable at n = 131. It is not there. The life arc is absent once the reader is held fixed.

The composition test makes the mechanism explicit. Fit each target on age with a correspondent fixed effect (the recurrent correspondents, n = 322), and compare the age slope to the pooled slope:

| target | pooled per decade (p) | with correspondent fixed effect (p) | reading |
|---|---|---|---|
| matter minus manner | 0.023 (4e-5) | 0.019 (0.10) | composition |
| rigour | 0.018 (7e-4) | 0.012 (0.28) | composition |
| depth | 0.025 (2e-5) | 0.014 (0.11) | composition |
| affect | -0.044 (2e-6) | -0.025 (0.11) | composition |
| PC1 | 0.358 (4e-10) | 0.248 (0.034 on 7B, 0.15 on 27B) | mostly composition, weak residue not scorer robust |

On every reliable individual axis and on the matter minus manner composite, the significant pooled age slope collapses to non significant once the correspondent is controlled. That is the signature of composition: the trend was the changing cast of readers, not a change in the man. The one place a residue survives is the PC1 composite, and it is not robust: the 7B keeps it at p = 0.034 (which does not clear the Bonferroni floor), the 27B kills it at p = 0.15. A residue that one scorer sees and the other does not is not a result we claim.

## Result 4: the composition is between correspondents

Between his recurrent correspondents, the mean age of the letters to each reader tracks the mean matter of those letters (corr mean age, mean PC1 = 0.38). Darwin met his high matter scientific peers (Gray, Wallace) later in life and wrote chatty early letters to Fox and Henslow (the lowest matter, highest affect). The pooled age arc is largely this ordering of relationships laid out along the life, not a trait sweeping through the person.

## Verdict

**The person is close to a fixed point; the biographical drift is mostly the room.** Darwin's letters show a strong, monotone, cross scorer arc toward matter and rigour and away from affect across his life, but it is a composition effect. Hold the correspondent fixed across 36 to 37 years and every reliable axis goes flat on both scorers; a correspondent fixed effect collapses the pooled slope to non significant on every reliable measure. This extends the programme's across context stability finding across TIME: the character a person projects is set by the relationship they are writing inside, and the life level "maturation" is the changing mix of those relationships.

There may be a very weak genuine maturation toward matter on the composite dimension, but it sits at the limit of detectability (about a third of the naive slope) and is not robust across the two scorers, so it is not claimed. The honest headline is the flat within person trajectory, which the task correctly anticipated is itself the strong, publishable result: earlier context findings were room, and time is one more room.

## Caveats

- One person. This is a within author law about Darwin, not a population estimate. The weak, non robust PC1 residue especially must not be generalised.
- Holding the correspondent fixed holds the person and the relationship, but topic and era still move inside a long correspondence, so "fixed correspondent" is a strong control, not a perfect one.
- Editorial cleaning is heuristic; the residual editor voice does not track age (r = 0.07) and adding editorial density as a covariate leaves the PC1 age term unchanged, so it is not driving anything.
- candour, originality and register have no cross scorer reliability on this corpus and are excluded; only rigour, depth, affect and matter minus manner carry the verdict.
- Coverage is thin below age 25 and above 70.

## Second author (the matrix)

Not built. No second dated single author lifetime corpus was on the NAS, and fetching and date parsing a fresh diarist or letter writer is bespoke work that would add date noise rather than a clean second row. The single author Darwin result is complete and stands on its own; a second author (a diarist with per entry dates spanning a life) is the obvious next row and is left as a flagged follow up.

## Reproduce

All paths absolute, on the laptop working tree unless noted.

```
# 1. carve dated Darwin letters from the Gutenberg volumes
python3 scripts/extract_darwin.py          # -> meta.jsonl, score_in.jsonl
# 2. strip the editor's voice
python3 scripts/clean_darwin.py            # -> meta_clean.jsonl, score_in_clean.jsonl
# 3. score on the panel (run on DL580; self queued behind the shared scorers)
#    7B  :8301  -> bioarc_scored.jsonl        (WORKERS=3, cc_found_human_score.py)
#    27B :8288  -> bioarc_scored_27b.jsonl    (WORKERS=6, score_27b.py, qwen38-extract)
# 4. regress axes + PC1 + matter minus manner on age, length controlled, correspondent fixed
python3 scripts/analyse_bioarc.py          # -> stats_7b.json / stats_27b.json
python3 scripts/bioarc_supplement.py       # -> supplement_7b.json / supplement_27b.json (composition test, decade trajectory)
```

Scored inputs staged at `/mnt/nas/kronaxis/corpora/darwin_letters/bioarc_score_in.jsonl`; both scored outputs live beside it and are copied into this directory.

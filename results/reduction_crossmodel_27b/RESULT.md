# Cross lineage check: the three unification reductions re scored on the 27B lineage

## What this test is

The three reduction results (ELM central route, Biber genre axis, Fleeson trait
versus situation) were first measured with the 7B lineage scorer. A fair question
is whether those results are an artefact of one model. This test re runs the
identical reduction recipes on scores produced by a heavier model, the 27B
lineage (served model name qwen38-extract, W4A16 AWQ, thinking disabled so it
behaves like the non thinking 7B). Only the scoring model changes. Same rubric,
same system prompt, same vocabulary, same parse, same downstream analysis code.
If the reductions are real they should survive the model swap with the same sign
and a comparable size.

The heavier model tends to compress the scale (it uses the extremes less), so the
honest expectation is same direction, possibly a smaller number. The pass or fail
question is the sign and the qualitative claim, not the third decimal place.

## Scoring completeness at time of measurement

| Corpus | Sample design | Scored | Status |
|---|---|---|---|
| ELM (IBM ArgQ) | full census, 2500 items | 2500 / 2500 | COMPLETE |
| Biber (reddit_wide) | <= 25 docs per subreddit, char rubric | 8029 / 10000, 321 subreddits (320 with >= 20 docs) | stable estimate, scoring continues to 10000 |
| Fleeson (cross site disposition) | multi site persons, one block per site, disp rubric | 6695 occasions across 2373 persons with >= 2 sites | PARTIAL (target ~6000 persons; scoring continues to 17090 blocks) |

The remaining two legs keep scoring under kx daemon (x27-biber, x27-fleeson,
each with a `*/5` cron `ensure`, stale 1200s). ELM is finished so x27-elm is
stopped. No duplicate scorers were started.

## Result 1 — ELM central route (COMPLETE, n = 2500)

The ELM claim: argument quality is carried by the central route (the matter axes
rigour and depth), not the peripheral route (the manner cue affect). The reduction
number is the partial Spearman rho of each construct against the human quality
label, controlling for text length.

| Construct | 7B partial rho | 27B partial rho |
|---|---|---|
| central pair (rigour + depth) | **+0.159** | **+0.077** |
| peripheral cue (affect) | -0.087 | -0.005 |

Raw axis correlations on the 27B scores (all p < 0.001 unless marked): depth
Spearman +0.184, rigour +0.174, central pair +0.187; affect only +0.055. The
central route axes sit at the top of the meaningful axes and the peripheral cue is
near zero, exactly as the 7B run and the ELM prediction say.

**Verdict: MATCH (direction holds).** Same sign, and the qualitative claim is
reproduced with high significance: rigour and depth predict quality, affect does
not. The length controlled partial is attenuated by roughly half (+0.077 versus
+0.159) — the heavier model gives a weaker but same signed effect once length is
partialled out.

## Result 2 — Biber genre axis (stable estimate; scoring 8029 / 10000)

The Biber claim: the manner reading PC1 (rebuilt here by SVD on the 27B char
scores of the sampled docs, oriented rigour + depth positive) recovers Biber's
Dimension 1 (involved versus informational), and does so most sharply at Biber's
own unit of analysis, the genre. D1 is oriented involved positive, so a negative
correlation is the predicted mapping.

| Unit | 7B Pearson r | 27B Pearson r |
|---|---|---|
| item level | -0.139 | **-0.151** |
| between subreddit centroids (Biber's own unit) | **-0.603** | **-0.313** |

27B centroid test on 321 subreddits (>= 20 docs each), well past the 300
subreddit stability floor. 27B PC1 loads rigour +0.583, depth +0.542 at the top
and affect -0.403, register -0.331 at the bottom, the same involved versus
informational shape as the 7B PC1.

**Verdict: MATCH on sign, magnitude attenuated at the genre unit.** The item level
number matches the 7B closely (-0.151 versus -0.139). The headline centroid
correlation keeps the correct negative sign (the genre axis is recovered) but is
about half the 7B size (-0.313 versus -0.603). The construct survives the model
swap; the strength of the genre level alignment does not fully carry over to the
heavier model.

## Result 3 — Fleeson trait versus situation (PARTIAL, 2373 persons / 6695 occasions)

The Fleeson claim: when a person is read across distinct sites, the disposition
(D8) variance splits into a stable between person part and a within person part,
and the stable part is at least as large as the situational part. The reduction
number is the room level trait share (ICC1), the mean over the 8 D8 axes of
between person variance divided by total variance.

| Quantity | 7B | 27B |
|---|---|---|
| trait share (ICC1, mean of 8 axes) | **0.516** | **0.588** |
| situation share | 0.484 | 0.412 |

Per axis on the 27B scores the trait share runs 47% (novelty) to 68%
(impulsivity), the same pattern of mostly stable axes as the 7B run.

**Verdict: MATCH.** Same sign and comparable size, in fact a slightly stronger
trait share (0.588 versus 0.516). The dispositional coupling holds under the model
swap: momentary behaviour is at least half stable trait.

**PARTIAL caveat:** this is measured on 2373 persons with >= 2 sites, below the
~6000 person target, because the disposition scorer is still running (6695 of
17090 blocks). The estimate is already on the same side of 0.5 as the 7B and
should be treated as provisional until the leg finishes; re run
`fleeson_27b.py` when `fleeson_scored.jsonl` reaches ~17090 lines for the final
number.

## Verdict column

| Test | 7B baseline | 27B lineage | Verdict |
|---|---|---|---|
| ELM central route | central partial rho +0.159 | +0.077 | **MATCH** (sign holds, ~half magnitude on length controlled partial; raw rigour/depth still top and p < 0.001) |
| Biber genre axis | centroid Pearson -0.603 | -0.313 (item level -0.151 vs -0.139) | **MATCH on sign** (correctly signed genre recovery; centroid magnitude ~half) |
| Fleeson trait share | ICC1 0.516 | 0.588 | **MATCH** (same sign, comparable/slightly stronger) — **PARTIAL** (2373 persons so far) |

All three qualitative claims survive the lineage swap: the central route is matter,
the genre axis is the involved versus informational manner axis, and disposition is
at least half stable trait. The heavier model attenuates the two correlation based
effects (ELM partial and the Biber genre centroid) to roughly half size while
keeping the sign, and slightly strengthens the variance decomposition. Honesty
note: the two attenuations are real and quantified above; the reductions are not
identical across lineages, but their direction and significance are.

## Reproduce

On DL580 (scorer at 127.0.0.1:8288, served model qwen38-extract):

```
export PATH=$HOME/bin:$PATH
WD=/mnt/nas/kronaxis/crossmodel_27b
# scoring (already staged + running under kx-daemon; resumable by id)
python3 $WD/scripts/prep_inputs.py                         # build the 3 input JSONLs from the DB
kx-daemon ensure x27-elm     --stale 1200 -- env INPUT=$WD/elm_input.jsonl     OUT=$WD/elm_scored.jsonl     RUBRIC=char WORKERS=8 python3 $WD/scripts/score_27b_generic.py
kx-daemon ensure x27-biber   --stale 1200 -- env INPUT=$WD/biber_input.jsonl   OUT=$WD/biber_scored.jsonl   RUBRIC=char WORKERS=8 python3 $WD/scripts/score_27b_generic.py
kx-daemon ensure x27-fleeson --stale 1200 -- env INPUT=$WD/fleeson_input.jsonl OUT=$WD/fleeson_scored.jsonl RUBRIC=disp WORKERS=8 python3 $WD/scripts/score_27b_generic.py
# reductions
python3 $WD/scripts/elm_27b.py
python3 $WD/scripts/biber_27b.py
python3 $WD/scripts/fleeson_27b.py
```

Scripts are mirrored under `scripts/`; the raw 27B outputs are under `outputs/`.

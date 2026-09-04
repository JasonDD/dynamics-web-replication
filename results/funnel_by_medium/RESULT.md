# Is the persuasion funnel a law of persuasion or a law of format?

**Question.** The programme headline (Paper 4B) is "manner earns attention, matter earns
conviction", measured mostly on short text. If that split is conditional on the LENGTH of
the medium, the funnel is a law of format, not of persuasion, which is a stronger and more
surprising claim. So: on a long medium, does matter start earning attention too, and does
manner's attention advantage survive?

**Axes.** matter = mean(rigour, depth). manner = mean(affect, stance, register). This is the
task definition of the two poles. It lines up with the matter/manner PC1 used elsewhere in
the series (SVD on `the internal reference table`, rigour and depth positive, affect and
register negative).

**Data.** Five already scored outcome corpora, each with an 8 axis character score, one real
human outcome, and a recoverable word count. No new scoring was run; nothing touched 
or . The corpora span very short to very long, and the outcome is either an ATTENTION
signal (a click, a signature) or a CONVICTION signal (a mind changed, an answer accepted, a
verdict).

| corpus | outcome | type | medWC | design group held fixed |
|---|---|---|---|---|
| upworthy | headline click through rate (randomised A/B) | attention | 15 | test (same article + image) |
| petitions | log10(1 + signatures), UK gov petitions | attention | 109 | same ask cluster |
| cmv | delta won (0/1), Reddit ChangeMyView | conviction | 120 | OP post (the persuadee), matched pairs |
| se | answer accepted (0/1), StackExchange | conviction | 197 | question, matched arguments |
| oldbailey | guilty verdict (0/1), Old Bailey trials | conviction | 272 | offence category |

**Method.** Per corpus, standardise matter, manner and log10(word count), demean the outcome
and the predictors within the design group (so the topic, the ask or the persuadee is held
fixed), then fit two models with standard errors clustered by that group:

- a MAIN effects model: outcome on matter + manner + length;
- a FULL model adding the two length interactions: matter x length and manner x length.

The outcome is standardised too, so every coefficient is in outcome SD per predictor SD and
is comparable across the five media. The between media test asks whether matter's pull on the
outcome climbs as the typical medium gets longer while manner's falls. The within corpus test
asks whether, inside a single medium, matter earns more of the outcome as a given text gets
longer (matter x length > 0) while manner earns less (manner x length < 0). Both signatures
would mean the split is length driven.

---

## Results

### Main effects, corpora ordered short to long

| corpus | type | medWC | n | matter | manner |
|---|---|---:|---:|---:|---:|
| upworthy | attention | 15 | 13,368 | **-0.030** | **+0.023** |
| petitions | attention | 109 | 381 | -0.065 | -0.024 |
| cmv | conviction | 120 | 19,430 | **-0.043** | **-0.064** |
| se | conviction | 197 | 66,543 | **+0.073** | +0.007 |
| oldbailey | conviction | 272 | 568 | +0.079 | -0.054 |

Bold = p < 0.05 (cluster robust). Matter's coefficient climbs from negative in the shortest
medium (-0.030 on Upworthy clicks) to clearly positive in the long conviction media (+0.073
on StackExchange, +0.079 on Old Bailey). Manner's positive pull exists only in the shortest
medium (+0.023 on Upworthy) and is gone or reversed everywhere longer.

### Length interactions, within each corpus

| corpus | medWC | wc p10..p90 | matter x length | manner x length |
|---|---:|---|---:|---:|
| upworthy | 15 | 11..19 | +0.007 (p=0.37) | -0.004 (p=0.64) |
| petitions | 109 | 48..141 | +0.104 (p=0.078) | +0.020 (p=0.44) |
| cmv | 120 | 34..382 | **+0.072** (p=3e-23) | +0.011 (p=0.13) |
| se | 197 | 63..589 | **+0.052** (p=2e-76) | -0.000 (p=0.99) |
| oldbailey | 272 | 54..1457 | **-0.104** (p=0.040) | +0.069 (p=0.33) |

In the two large long corpora, matter's contribution to winning the outcome RISES strongly
with the length of the individual text (CMV +0.072, StackExchange +0.052, both overwhelming),
while manner x length sits at zero. That is the exact format signature: give the text more
room and matter earns more of the result, manner earns no more. Upworthy cannot test this,
its headlines run 11 to 19 words with no length range, and its interaction is correctly null.
Old Bailey is a genuine counterexample: there matter x length is negative.

---

## Verdict: the funnel is a law of persuasion carried on a length gate, not a pure law of format

The honest answer is split by pole, and it is neither of the two clean headlines.

**The "manner earns attention" half is a short format effect.** Manner's positive pull on the
outcome is significant only on Upworthy (+0.023), the shortest medium, and it vanishes or
reverses in every longer medium. Manner buys the click in a headline and buys nothing once
there is a paragraph. On that pole the funnel is a law of format: manner's advantage is an
artefact of short text and does not survive length.

**The "matter earns conviction" half is bandwidth gated but stays a law of persuasion.** Matter
costs you the outcome in the shortest form (negative on Upworthy) and only pays once the text
is long enough to carry an argument. The within corpus proof is decisive on the two big
corpora: the longer the argument, the more matter earns the delta (CMV) or the accepted answer
(StackExchange). So matter's payoff genuinely depends on format, it switches on with length.
But what it switches on to earn is CONVICTION, not attention.

**Matter does NOT start earning attention just because the medium is long.** This is the claim
the format story needs, and the data does not support it. The clean test is the two attention
outcomes on their own: Upworthy clicks (short) and UK petition signatures (long). Matter is
negative in both (-0.030 and -0.065); it does not convert into attention on the longer
attention medium. The between media rise of matter in the table above runs together with a
change in the OUTCOME, because in this corpus set the short media measure attention and the
long media measure conviction. Once that confound is separated, matter earning power lives on
the conviction side at every length.

So the funnel is not a law of format in the strong sense the question asked for. It is a law of
persuasion with a length gate on the matter pole. Manner earning attention is real only in
short format. Matter earning conviction is real but needs length to appear at all, and it does
not become an attention winner in long form. The single sentence: give matter more room and it
earns more conviction, not more attention; manner's attention pull was short text all along.

---

## Honest limits

- **Length is confounded with outcome type across the corpora.** The short media here measure
  attention (clicks, signatures) and the long media measure conviction (delta, accepted answer,
  verdict). The clean within type comparisons (Upworthy vs petitions for attention; the matter
  x length interactions inside CMV and StackExchange for conviction) carry the verdict, not the
  raw ordering of the five.
- **Petitions is underpowered.** Only 381 opened petitions with usable scores, and after
  demeaning within the same ask cluster most clusters are singletons, so its matter x length
  (+0.104) is directional only (p = 0.078).
- **Old Bailey clusters on 9 offence categories** and has 568 trials, so its cluster robust
  p values rest on 8 degrees of freedom; its negative matter x length is real in this sample
  but should not be over read.
- **Old Bailey contradicts the within corpus bandwidth story** (matter x length negative). Any
  claim that matter always pays more with length is false; it holds on the two argument corpora,
  not on the trial corpus.
- Character scores are quantised to 0.1 steps by a single web tuned scorer; CMV and StackExchange
  outcomes come from matched pair designs, and within group demeaning approximates the paired
  (conditional) estimator rather than fitting it exactly.

## Reproduce

`scripts/funnel_by_medium.py` in this directory. Runs on the internal host (Postgres only for the optional
PC1 reference, internal store for the corpora, `~/kc-dwpaper` for Upworthy). Pure read, no scoring, no
 or  calls.

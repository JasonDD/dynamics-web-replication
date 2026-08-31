# Radicalisation as a manipulation problem: is extremist content the manipulation signature with worse outcomes?

*DYNAMICS-WEB series, PUBLIC track (shield). Defensive research. This reuses the manipulation
instrument and the discipline from `results/manner_inflation_deception` and treats radicalisation as
the same measurement problem as trolls, phishing and dark patterns, but with catastrophic rather than
commercial stakes. It reports effect sizes, the signature and the trajectory shape only. Any operating
threshold, detector weight or targeting read is withheld under the restricted track (see Disclosure).*

Scorer: `truthometer/scripts/cc_found_human_score.py` (8 axis DYNAMICS character instrument,
qwen2.5-7b-atlas on DL580 :8301, the free 7B teacher used across the series, identical system prompt,
vocabulary line and parse, so every scale matches). Prep: `cc_radicalisation_prep.py`. Analysis:
`cc_radicalisation_analyse.py` in this directory. All inputs on the DL580 held Reddit corpus
(`cc_v3.reddit_wide`) and the already scored deception corpora on NAS.

---

## 1. The claim under test

The programme has one manipulation signature: **manner inflated past what the matter earns**, and in
its sharpened form, **affect inflated while matter is starved**. On the 8 axes, matter is rigour plus
depth; the affect gap is affect minus matter. Verbose persuasive deception (state trolls, phishing)
carries it strongly (Cohen's d near 2.1 on the affect gap); fact check falsity and dark pattern
microcopy do not, for reasons the length result explains.

Radicalising content is a persuasion product aimed at moving a reader from a mainstream position to
an extreme one. If the manipulation signature is real and general, extremist community text should
carry it, and it should be **more extreme than ordinary partisan or benign text**, not merely
different in topic. Two legs test this.

**Leg 1, content signature (run here).** Score extremist community text against matched partisan and
benign community text on the 8 axes and test whether the affect gap separates them, how large the
effect is, and where extremist content sits on the same absolute scale as trolls, phishing and dark
patterns.

**Leg 2, trajectory (feasibility gated here).** Does a user's own character shift as they move into
extremist communities over time, the pathway made measurable within a person? Mirrors
`results/escalation_trajectory`. The feasibility gate below decides whether the held data can answer
it.

---

## 2. Discipline (read this first)

This is sensitive work and the discipline is part of the result, not a preface to it.

1. **Intelligence prior, never an accusation.** The output is a community level signal over text. It
   is a prior that raises or lowers attention, never a standalone accusation and never a diagnosis of
   an individual. A high affect gap on a post is a property of the writing, not a verdict on the
   writer.

2. **Base rate and false positive harm, named.** Extremist affiliation is very rare in the general
   population. Applying even a good community level detector to individuals therefore produces mostly
   false positives, and the cost of a false positive here is a person wrongly flagged as a violent
   extremist, which is a serious harm. This is exactly why the deployable object is a triage prior on
   content and communities, not a scoring tool pointed at people. The public claim is about text and
   communities in aggregate.

3. **Shield versus sword.** This file is the shield: effect sizes, the signature, the dose response,
   the trajectory shape and the exact missing data, all of which arm a defender and cost an attacker
   nothing new (the community pathway taxonomy is already public in the academic literature). The
   sword (operating thresholds, detector weights, gate cut points, any per community targeting read)
   is withheld under `docs/internal/restricted/radicalisation_signature/`, `DO NOT SHARE` header.

4. **No operational content and no named individuals.** Nothing here would help a recruiter aim or a
   propagandist write. No real person is named, profiled or scored. Community labels are public
   subreddit names drawn from the published radicalisation pathway literature.

---

## 3. Data, and what is missing

The held corpus is `cc_v3.reddit_wide`, a 20.1 million row sample of Reddit comments across 50,123
subreddits, of which a subset carry the 8 axis character score. It is a **per subreddit sample, not a
per author longitudinal crawl**: each community is sampled to a few hundred to a few thousand
comments, and an individual author appears only a handful of times. That distinction decides which leg
can run.

**Community tiers** (public labels, grounded in the radicalisation pathway literature, Ribeiro et al.
2020 on alt right pathways and 2021 on the manosphere):

| tier | communities (subreddits) | what it is |
|---|---|---|
| extremist | theredpill, mgtow, pussypassdenied, nonewnormal, conspiracy | manosphere (misogynist), covid conspiracy (r/NoNewNormal, banned 2021), general conspiracy |
| gateway | askthe_donald, louderwithcrowder, walkaway, kotakuinaction, tumblrinaction | alt lite and grievance gateway communities |
| idw | jordanpeterson, samharris, joerogan | intellectual dark web, the theorised on ramp |
| partisan | politics, worldnews, neoliberal, conservative | ordinary mainstream political discussion (the control that matters) |
| benign | askreddit, nostupidquestions, personalfinance, todayilearned, explainlikeimfive | non political discussion, the honest baseline |

**What is openly available and used.** The manosphere and conspiracy communities above are present in
the held corpus in quantity and are same platform, same rough genre as the controls, which makes them
a clean matched test. The reference deception corpora (IRA state trolls, phishing, dark patterns) are
already scored on the identical 7B scale and give the absolute yardstick.

**What is missing, stated plainly.** The hardest banned hate communities (CoonTown, r/altright,
r/The_Donald, frenworld, GreatAwakening) are **not present in this crawl**. The extremist tier here is
therefore the manosphere and conspiracy band, which is a real and documented radicalisation surface
but is milder than open violent extremist forums. A stronger content result needs the Reddit
quarantined and banned subreddit dumps (Pushshift archives of the removed communities) or the Ribeiro
pathway datasets, which are openly published but were not fetched in this run. This bounds the effect
sizes below to the manosphere and conspiracy band; the true extreme is likely stronger, not weaker.

---

## 4. Leg 1 method

- Prep (`cc_radicalisation_prep.py`) samples 130 usable comments per subreddit deterministically
  (hashtext order, so the run reproduces), body length at least 120 characters, `[deleted]` and
  `[removed]` dropped, capped at 6,000 characters. One `{id, text, outcome, kind}` row per comment,
  where outcome is the tier and kind is the subreddit. 2,860 comments, balanced across communities.
- Scoring hits the shared :8301 endpoint, self queued at a modest worker count behind the other jobs
  holding the endpoint, so neither this job nor the others were starved.
- Per text metrics mirror `manner_inflation_deception`: matter is the mean of rigour and depth, manner
  is the mean of affect, stance and register, the affect gap is affect minus matter, the residual is
  manner minus matter.
- Effect size is Cohen's d against the benign baseline. Separability is the Mann Whitney AUC, with the
  8 axis figure from a balanced five fold cross validated numpy logistic regression, the single axis
  figures from the raw metric with no training.
- Absolute positioning loads the already scored IRA trolls, phishing and dark patterns and compares
  the affect gap on one common scale.

---

## 5. Leg 1 measured results

Scored 2,860 comments, balanced across communities (benign 650, extremist 650, gateway 650, partisan
520, idw 390). Median length is 54 to 68 words per tier, so the tiers are matched on length and the
affect gap is not a length artefact (the length result warns that short text is forced into affect;
here every tier is the same middling length).

### 5.1 Character by tier (mean)

| tier | n | med words | matter | manner | affect | affect_gap | residual |
|---|---|---|---|---|---|---|---|
| benign | 650 | 67 | 0.460 | 0.520 | 0.587 | 0.127 | 0.060 |
| partisan | 520 | 57 | 0.434 | 0.553 | 0.652 | 0.218 | 0.119 |
| idw | 390 | 68 | 0.436 | 0.572 | 0.677 | 0.242 | 0.137 |
| gateway | 650 | 54 | 0.338 | 0.550 | 0.645 | 0.308 | 0.213 |
| extremist | 650 | 59 | 0.372 | 0.548 | 0.713 | 0.341 | 0.176 |

The affect gap climbs monotonically from benign to extremist: 0.127, 0.218, 0.242, 0.308, 0.341. This
is a dose response up the theorised pathway. Matter falls (0.460 to 0.372, and lower still in the
gateway tier at 0.338) while affect rises (0.587 to 0.713). The extremist tier is the most affect
inflated of all five, and the signature is the predicted one: affect up, matter starved.

### 5.2 All 8 axes by tier (mean)

| tier | rigour | depth | originality | candour | affect | commercial_drive | stance | register |
|---|---|---|---|---|---|---|---|---|
| benign | 0.442 | 0.479 | 0.482 | 0.846 | 0.587 | 0.202 | 0.492 | 0.482 |
| partisan | 0.399 | 0.468 | 0.520 | 0.824 | 0.652 | 0.205 | 0.574 | 0.434 |
| idw | 0.398 | 0.473 | 0.522 | 0.833 | 0.677 | 0.175 | 0.598 | 0.442 |
| gateway | 0.305 | 0.370 | 0.467 | 0.804 | 0.645 | 0.263 | 0.600 | 0.406 |
| extremist | 0.333 | 0.411 | 0.533 | 0.838 | 0.713 | 0.194 | 0.524 | 0.406 |

Candour barely moves (0.80 to 0.85 across all tiers), the same flatness the escalation baseline found
in sincere persuasion: this content is not opaque, it is confident and affect loaded. Rigour and depth
carry the matter collapse. Stance rises into the gateway and partisan tiers, consistent with
polemical mainstream politics.

### 5.3 Effect size versus the benign baseline (Cohen's d)

| tier | d(affect_gap) | d(residual) | d(matter) | d(affect) |
|---|---|---|---|---|
| partisan | +0.292 | +0.265 | -0.150 | +0.348 |
| idw | +0.369 | +0.347 | -0.137 | +0.505 |
| gateway | +0.627 | +0.715 | -0.690 | +0.276 |
| extremist | +0.726 | +0.555 | -0.529 | +0.712 |

The affect gap effect grows monotonically up the tiers, reaching a medium to large d of +0.73 for the
extremist tier and +0.63 for the gateway. Ordinary mainstream partisan discourse already carries a
smaller version of the same signature (d +0.29), which is the important nuance: the extremist tier is
more manipulation shaped than partisan content, but partisan content is not neutral either. The
difference up the pathway is one of degree on the same axis, not a new axis.

### 5.4 Separability (Mann Whitney AUC; the 8 axis figure is five fold cross validated logistic)

| contrast | 8 axes (CV) | affect_gap alone | residual alone |
|---|---|---|---|
| extremist vs benign | 0.713 | 0.712 | 0.648 |
| extremist vs partisan | 0.638 | 0.620 | 0.569 |
| gateway vs benign | 0.777 | 0.658 | 0.694 |
| idw vs benign | 0.688 | 0.618 | 0.596 |

Two honest facts sit here together. First, the single affect gap axis with no training separates
extremist from benign at 0.71, almost exactly the full 8 axis model (0.713): the signature is real and
it is carried by the one predicted axis, not by a lucky combination. Second, the separation is
**modest, not the near perfect 0.96 the state trolls reach against Change My View**. Extremist versus
ordinary partisan is only 0.64. Character alone does not cleanly divide extremist from mainstream
political discourse, because mainstream political discourse already sits part way up the affect gap.
This is the correct result for a triage prior and the wrong result for a standalone classifier, which
is exactly the discipline this file holds.

### 5.5 The manipulation spectrum: absolute affect gap on one common scale

Every corpus below is scored on the identical free 7B instrument, so the affect gap is directly
comparable. This places radicalising content on the same yardstick as trolls, phishing and dark
patterns.

| corpus | n | mean affect_gap | median |
|---|---|---|---|
| phishing emails | 700 | +0.584 | +0.700 |
| IRA state trolls (Right, Left, Fearmonger) | 8,000 | +0.489 | +0.550 |
| reddit: extremist | 650 | +0.341 | +0.350 |
| reddit: gateway | 650 | +0.308 | +0.350 |
| dark patterns (UI microcopy) | 1,168 | +0.250 | +0.150 |
| reddit: idw | 390 | +0.242 | +0.350 |
| reddit: partisan | 520 | +0.218 | +0.350 |
| reddit: benign | 650 | +0.127 | +0.250 |

Extremist and gateway community text sit **above dark patterns and above ordinary partisan and benign
content, but below state trolls and phishing**. The shape is identical to the strongest manipulation
in the programme; the magnitude is roughly two thirds of the troll level. Two things pull the reddit
figure below the troll figure and both are honest: the held extremist tier is the manosphere and
conspiracy band, not open violent extremist forums (which are absent, Section 3), so this is a lower
bound; and everyday reddit comments, even benign ones, carry more affect than a neutral baseline, which
compresses the whole reddit column upward and shrinks the visible gap.

### 5.6 Per subreddit affect gap, ranked

| subreddit | tier | n | affect_gap | matter | affect |
|---|---|---|---|---|---|
| mgtow | extremist | 130 | +0.432 | 0.331 | 0.762 |
| louderwithcrowder | gateway | 130 | +0.390 | 0.361 | 0.751 |
| pussypassdenied | extremist | 130 | +0.382 | 0.358 | 0.741 |
| joerogan | idw | 130 | +0.348 | 0.382 | 0.730 |
| nonewnormal | extremist | 130 | +0.347 | 0.381 | 0.728 |
| tumblrinaction | gateway | 130 | +0.313 | 0.384 | 0.697 |
| theredpill | extremist | 130 | +0.305 | 0.357 | 0.662 |
| conservative | partisan | 130 | +0.300 | 0.407 | 0.706 |
| askthe_donald | gateway | 130 | +0.291 | 0.233 | 0.524 |
| walkaway | gateway | 130 | +0.275 | 0.288 | 0.564 |
| kotakuinaction | gateway | 130 | +0.268 | 0.422 | 0.691 |
| askreddit | benign | 130 | +0.267 | 0.391 | 0.658 |
| jordanpeterson | idw | 130 | +0.243 | 0.430 | 0.673 |
| conspiracy | extremist | 130 | +0.240 | 0.433 | 0.673 |
| politics | partisan | 130 | +0.200 | 0.443 | 0.644 |
| worldnews | partisan | 130 | +0.197 | 0.454 | 0.651 |
| neoliberal | partisan | 130 | +0.174 | 0.432 | 0.605 |
| nostupidquestions | benign | 130 | +0.169 | 0.438 | 0.607 |
| todayilearned | benign | 130 | +0.140 | 0.468 | 0.608 |
| samharris | idw | 130 | +0.133 | 0.496 | 0.629 |
| personalfinance | benign | 130 | +0.080 | 0.482 | 0.562 |
| explainlikeimfive | benign | 130 | -0.022 | 0.522 | 0.500 |

### 5.7 Reading the per community detail

Three things in this ranking sharpen the result rather than blur it.

1. **The manosphere leads.** MGTOW tops the whole list at +0.43, the highest matter starvation
   (0.331) and near the highest affect (0.762), with r/pussypassdenied and r/TheRedPill alongside. The
   misogynist manosphere, the best documented modern radicalisation pipeline, is the purest carrier of
   the affect inflated matter starved signature. That is a real convergence of an independent
   measurement with the pathway literature.

2. **Conspiracy fakes matter rather than starving it.** r/conspiracy sits low on the affect gap
   (+0.240) with the highest matter of any extremist community (0.433). This is the same exception the
   dark pattern result found for hidden costs and the illusion of control cell: some manipulation does
   not abandon matter, it manufactures it. Conspiracist writing marshals pseudo evidence, dates,
   quotes and citations, so it reads as rigorous even when it is not, and the affect gap
   under counts it. The signature has a known blind spot and conspiracy content lands squarely in it.

3. **The tiers overlap, they do not partition.** r/Conservative (partisan) at +0.30 outscores
   r/TheRedPill (extremist), and r/samharris (idw) at +0.13 is indistinguishable from benign. The
   community label is not recoverable from character alone, and it should not be: this is a continuous
   affect gradient with extremist communities concentrated at the top, not a clean boundary. The
   honest deliverable is a prior over that gradient, never a label on a person.

---

## 6. Leg 2 trajectory: feasibility gate, design, and the exact missing data

**The literal within person test cannot run on the held data, and the reason is structural.** The
trajectory test needs the same author observed across time, before and after they enter an extremist
community, with enough posts each side to score a character slope. The held corpus is a per subreddit
sample, so author timelines are almost empty. Measured directly on the eleven manosphere and
conspiracy communities:

| quantity | value |
|---|---|
| distinct authors appearing in an extremist community | 265 |
| of those, authors with any prior post in the corpus | 9 |
| of those, authors with at least three posts before and three after their first extremist post | 3 |

Three usable trajectories is not a study. Stated plainly, as the feasibility gate demands: **the
pathway cannot be measured within a person on this corpus.** This mirrors the escalation trajectory
result, which hit the same wall for predatory conversation and reported the design plus the missing
data rather than a thin number.

**The design, ready for the moment the data exists.** Identical pipeline to the escalation trajectory
work. For each author observed to enter an extremist community at time T, order their posts by time,
score the 8 axes per post, and fit each axis and PC1 (matter versus manner) against a time index
centred on T. Test three things the content result and the escalation baseline have now framed:

1. **A within person affect gap rise.** Does an author's own affect gap climb across the transition
   into the extremist community, over and above any topic shift, the way the escalation baseline shows
   affect rising within winning persuasion?
2. **A matter collapse.** Does rigour and depth fall as the person moves in, the individual mirror of
   the cross sectional matter starvation the content leg measures between tiers?
3. **A changepoint at entry.** Is there a discriminative break at the entry turn, unlike the CMV
   proxy where the affect pivot was present but not discriminative, so a detector could flag the
   transition rather than only the endpoint.

**The exact missing data.** A per author longitudinal Reddit corpus that spans mainstream and
extremist communities for the same accounts, with post timestamps and community labels. This is openly
published and fetchable: the Pushshift monthly dumps reconstructed per author, and specifically the
Ribeiro et al. radicalisation pathway datasets (alt right, alt lite, intellectual dark web user
histories) and the banned and quarantined subreddit archives. None of these was fetched in this run.
With any one of them the design above runs unchanged. This work sits on the internal track when it
runs, because per author histories carry governance weight that the aggregate community text here does
not.

---

## 7. Verdict

**Is radicalisation the manipulation signature with worse outcomes? Yes on the signature, with two
honest qualifications, and the qualifications are the useful part.**

1. **Radicalising content carries the same signature, in the same direction.** Extremist community
   text is affect inflated and matter starved, exactly the form that state trolls and phishing carry.
   The one predicted axis, the affect gap, separates extremist from benign on its own at 0.71, as well
   as the full model, so this is the manipulation signature and not some unrelated topic marker.

2. **It is more extreme than ordinary partisan or benign content, and monotonically so.** The affect
   gap rises benign to partisan to intellectual dark web to gateway to extremist (0.13, 0.22, 0.24,
   0.31, 0.34), a clean dose response up the theorised pathway, with a medium to large effect for the
   extremist tier (Cohen's d +0.73 against benign). The manosphere communities, the best documented
   real pipeline, are the single purest carriers. An independent instrument recovered the pathway that
   the radicalisation literature describes.

3. **First qualification: it is milder than trolls and phishing, and the communities do not cleanly
   separate.** On the common scale the extremist tier reaches about two thirds of the state troll
   affect gap, and extremist versus mainstream partisan separates at only 0.64. Part of this is that
   the strongest banned violent communities are absent from the held corpus, so the measured effect is
   a lower bound. But part is real and important: mainstream partisan discourse already sits part way
   up the same axis, so radicalisation is a matter of degree on a continuum, not a categorical jump.
   That is precisely why the correct object is a triage prior over content and communities, not a
   classifier pointed at people, and it is why the false positive harm named in Section 2 is not
   hypothetical.

4. **Second qualification: conspiracy content evades the affect gap by faking matter.** r/conspiracy
   scores low on the signature because conspiracist writing manufactures pseudo rigour rather than
   abandoning it, the same illusion of control exception the dark pattern result found. The affect gap
   under counts exactly the community that dresses manipulation as evidence. A complete detector needs
   the faked matter feature the programme has already identified, not the affect gap alone.

**The worse outcomes are the stakes, not a larger signal.** The measured manipulation signature in
radicalising content is real and pathway shaped but moderate, comparable to a strong dark pattern, not
to the sharpest troll or phishing text. What makes radicalisation the more dangerous problem is not a
bigger character deviation, it is that the same moderate manipulation is aimed at moving a person
toward violence rather than a purchase, so the tolerable false positive and false negative budgets are
completely different. The instrument gives a training free, pathway ordered prior that concentrates
attention on the communities and the text where the signature is strongest, most clearly the
manosphere. It does not, and by the discipline here must not, output a judgement on any individual.

The trajectory leg, whether an individual's own character shifts as they move in, is the test that
would turn this cross sectional gradient into a within person pipeline. It cannot run on the held per
subreddit sample (three usable trajectories, Section 6). The design is specified and the exact openly
published data that would run it is named. That is the next step, on the internal track.

---

## 8. Companion and restricted pointer

The sword half (operating thresholds, per axis weights, gate cut points, the tier map as a live block
list, any per community targeting read) is at
`docs/internal/restricted/radicalisation_signature/DO_NOT_SHARE.md` and is not computed or printed in
this file. The public claim stands on the effect sizes and the spectrum position above; the operating
recipe is the withheld half by the same responsible disclosure and moat logic as the rest of the
programme.

Reference corpora for the absolute spectrum: IRA state trolls (`ira_troll/work/scored.jsonl`),
phishing and dark patterns (`manner_inflation/scored.jsonl`), all on the identical free 7B scale, no
third party model and no personal data beyond public subreddit comment text.

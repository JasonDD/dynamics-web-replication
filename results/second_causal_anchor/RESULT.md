# Paper 4B second causal anchor: the run, and its verdict

*DYNAMICS-WEB, PUBLIC track. 30 August 2026. Companion to CANDIDATES.md (the hunt). This is the RUN:
turning the found anchor, the Milkman et al. 2021 PNAS flu vaccination megastudy, into Paper 4B's
actual second causal data point. Question: does the funnel that held on Upworthy clicks (manner earns
attention, matter earns the action) also hold on a real health ACTION, taking a flu shot?*

## Verdict

**Yes, directionally, and it is the cleaner half of the funnel.** On Upworthy the manner heavy
character (affect and originality) causally raises the click. Here, on a real vaccination taken, the
measured institutional framing causally raises the action and the manner heavy framing does not. The
character that opens the door is not the character that gets the shot into the arm. This is the second
causal anchor Paper 4B needed, on a behavioural outcome, from a randomised field experiment we did not
run, and its direction is the opposite of the click, which is exactly the funnel claim.

Two independent readings agree on that direction:

1. **Our own computation on the free per arm data** (n = 19 arms, `analyse_megastudy.py`): the single
   strongest predictor of a larger causal uplift is the plainest, most institutional feature of all, the
   message stating the flu shot is already **reserved for you** (Spearman +0.63, Pearson +0.67). The
   manner markers trend the other way: any interactive gimmick (text back, click, share) is the strongest
   negative single feature (Spearman −0.27, Pearson −0.32), multimedia is negative (−0.12 / −0.19), and a
   composite of the five manner markers against the uplift is weakly negative (−0.15).
2. **The authors' own human rater analysis** (about 99 raters per message, their Table S14 to S16, which
   we did not need to recompute): a composite they name **incongruence** with normal provider messaging,
   built from surprising, interactive and casual, negatively predicts uptake (r = −0.49, p = 0.03), while
   a **reserved reminder** composite positively predicts it (r = +0.43, p = 0.07); in a joint regression
   both survive (incongruence beta −0.48, p = 0.02; reserved reminder beta +0.41, p = 0.05).

Our objective computation and their human ratings are measuring the same thing from two sides and land in
the same place: on a real health action, matter wins and manner loses.

## The data, and how it maps to Upworthy

| | Upworthy (first anchor) | Milkman 2021 megastudy (this anchor) |
|---|---|---|
| what was randomised | headline text within a test | which of 19 text nudges a patient got |
| outcome | click (attention) | flu shot taken (a real action) |
| randomisation | within test, exposure by chance | patients assigned at random to arm |
| unit | tens of thousands of headline pairs | 19 arms, N = 47,306 patients |
| per arm effect | click through rate | Beta, the regression estimated uplift vs usual care |
| access | free, OSF osf.io/jd64p | free aggregate, OSF osf.io/tucjs |

Per arm causal uplift (Beta, all patients) ranges from +0.006 to +0.046, mean +0.021, that is the top arm
adds about 4.6 points to the vaccination rate over usual care. The top arm is the plain twice sent
reminder that a shot is reserved for the patient. The join is clean: Efficacy.csv (per arm Beta) to
ObjectiveAttributes.csv (per arm features) on Intervention ID, 19 arms.

## Why the model instrument was not scored, and what it would take

The operator's plan was to score each arm's message text on the eight axes at , then cross check our
axes against the authors' twelve attribute human codings. Both steps need the verbatim per arm message
text. **That text is not in any free deposit.** It was checked at source on 30 August 2026:

- The OSF Web Appendix holds results tables as images and points to the parent working paper for the
  wordings. The full text of all 19 interventions lives in the SSRN working paper (10.2139/ssrn.3780267,
  login walled) and in a non public protocol attachment.
- The attribute study Qualtrics file (QSF, downloaded and parsed) showed each rater the message as a
  mockup image of a phone conversation, not as machine readable text; only three message images are on
  OSF, and the QSF carries no fetchable image URLs.
- The study's own one line condition labels exist in two different naming schemes (the aggregate prose
  names and the ObjectiveAttributes condition names) that cannot be reliably joined to each other or to
  the per arm Beta, and in any case a four word researcher label is not the voice of the message, so
  scoring it on an instrument built to read voice would produce a number without meaning.

Scoring a fabricated or mismatched text to manufacture an eight axis correlation would be dishonest, so it
was not done. The honest position is that the model instrument is blocked on a paywall, not on the method.
The scorer itself is ready:  was confirmed live on the internal host (an internal 7B instruct model, the same rater used on
Upworthy). The fast follow, once the SSRN appendix text is obtained or the 19 message mockup images are
put through OCR on the internal host, is to score the verbatim texts on the eight axes, correlate the matter against
manner projection with Beta, and run the cross check of our axes against the authors' twelve attribute
codings. It is a costed step of hours, not a new experiment.

## What the model instrument would be tested against (the axis mapping)

The authors coded, per message, attributes that line up cleanly with our axes, which is why their human
result already stands in for the instrument at the level of direction:

| our axis (0 to 1) | authors' attribute | sign against uptake |
|---|---|---|
| register (institutional to conversational) | casualness (casual, informal tone) | negative (casual loses) |
| originality and affect (expected to surprising, neutral to sensational) | surprise factor, incongruence | negative (surprising loses) |
| commercial_drive and interactivity | interactive (text back, click, share) | negative (gimmick loses) |
| low stance, plain reminder | reserved reminder | positive (measured wins) |

The prediction Paper 4B would make, that on a conviction style outcome the matter end wins and the manner
end loses, is the pattern the authors found and the pattern our objective computation independently
recovers.

## Honest power caveat

This anchor is causal and free but coarse. There are only 19 arms, so every correlation here has wide
error and none should be read as a precise coefficient; the load bearing fact is the SIGN and its
agreement across two independent readings, not any single number. The manner markers we have are crude
objective counts (exclamation marks, multimedia flags), which is why our manner composite is only weakly
negative while the authors' human casualness and surprise ratings, which read tone directly, give the
sharper −0.49. Pooling the 2022 Walmart megastudy (22 more randomised arms, aggregate also free on OSF)
would roughly double the arm count and is the obvious next widening. The claim this run supports is
therefore modest and exact: the funnel direction that held causally on Upworthy clicks also holds,
directionally and causally, on a real health action, from a second independent randomised dataset.

## Files

- `RESULT.md` (this file)
- `analyse_megastudy.py` the exact computation (reads the two CSVs, prints the correlations)
- `Efficacy.csv` per arm N, percent vaccinated, Beta, from OSF osf.io/tucjs
- `ObjectiveAttributes.csv` per arm objective message features, from OSF osf.io/tucjs
- `merged_arms.json` the 19 arm join used in the run
- `CANDIDATES.md` the prior hunt that found this anchor

## Sources

- Milkman et al. 2021, PNAS 118(20) e2101165118: https://www.pnas.org/doi/10.1073/pnas.2101165118 ;
  free data OSF https://osf.io/tucjs/ ; open copy https://scholarsarchive.byu.edu/facpub/8941/
- Parent working paper (verbatim texts, login walled): https://doi.org/10.2139/ssrn.3780267
- Companion 2022 Walmart megastudy (optional pooling): https://www.pnas.org/doi/10.1073/pnas.2115126119
- Upworthy Research Archive (first anchor): OSF https://osf.io/jd64p

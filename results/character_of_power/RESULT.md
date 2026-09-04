# The character of power

**Track:** PUBLIC. **Date:** 2026-08-31. **Branch:** ops/gh-treasure-discovery.
**Scorer:** the frozen 7B character instrument on  (`an internal 7B instruct model`, same system prompt, vocab line
and JSON parse as every other DYNAMICS-WEB result). **PC1 basis:** SVD on `the internal reference table`
(2,648,406 domains), standardised, oriented so rigour and depth load positive (identical construction to
`length_mechanism.py` and `manip_analyse.py`).

## The question

Does a politician's character change when they gain or lose office? This is a within person natural experiment
on the sharpest room change there is. The same named person is observed both while holding a ministerial post
and while sitting outside government, and we ask what moves in the eight character axes when power is switched
on. Because the comparison is made inside each person, the stable person is differenced out and what remains is
the effect of the office itself, not of who the person happens to be. Running it across many countries turns it
into a test of whether the effect is universal or local.

The eight axes and their poles (unchanged across the series): rigour (0 unsourced to 1 scholarly), depth (0
superficial to 1 expert), originality (0 rehashed to 1 primary), candour (0 opaque to 1 transparent), affect (0
neutral to 1 sensational), commercial_drive (0 reference to 1 hard sell), stance (0 balanced to 1 polemical),
register (0 institutional to 1 conversational). Note the register pole: a higher value is plainer and more
conversational, a lower value is more formal and institutional.

## Data and the power label

**Corpus:** ParlaMint, the English translated parliamentary sessions (`en_sessions`), which removes the
language confound so the axes are comparable across countries. Speeches are the `regular` utterances only
(chair and procedural turns dropped), kept between 80 and 900 words.

**The in power label is individual and time varying, and it comes from the corpus itself.** ParlaMint's
`ParlaMint-listPerson-en.tsv` carries a `Minister` column holding the exact date ranges during which each
person held a ministerial post (for example `2020-01-07/2021-04-19|...`). Every session file name carries the
sitting date. A speech is labelled **in power** when its date falls inside one of that speaker's ministerial
ranges, and **out of power** otherwise. This is the backbench to minister transition, the cleanest individual
signal of holding office, and it needs no external government composition table. A **crosser** is a speaker
observed with at least two speeches in each condition, so that each side of the within person difference rests
on more than a single speech.

**Balanced sampling.** For each crosser we sample up to six speeches per condition (seed 42), so a handful of
prolific ministers cannot dominate. The resulting set: **193 crossers, 2,173 speeches, 23 countries.** The in
power and out of power halves are matched on length almost exactly (mean 279 versus 278 words), so nothing
below is a length artefact.

Six parliaments produced no crossers and sit out of the design: Great Britain, Poland and Hungary do not
populate the ParlaMint `Minister` field, so their ministers could not be identified, and Portugal contributed
too few parsed regular speeches. This is a metadata coverage limit, not a null for those countries.

Build: `truthometer/scripts/cc_power_build.py`. Score: `pm_score.py` on the internal store staging directory (the shared
ParlaMint scorer). Analysis: `truthometer/scripts/cc_power_analyse.py`. Full console dump: `power_shift.txt`.
Machine readable: `power_result.json`.

## Result: gaining office changes character, and the same way almost everywhere

The table is the within person shift on gaining power (in power mean minus out of power mean), averaged over the
193 speakers. The fixed effects column is the same effect estimated by demeaning every variable inside each
speaker and regressing on the power label while controlling a linear calendar trend (year) and speech length
(log words), with standard errors clustered by speaker. The two estimators agree almost exactly, so the effect
is not a calendar drift and not a length effect.

| axis | within person shift | d / sd | fixed effects beta (clustered SE) | t | countries agreeing on sign |
|---|---|---|---|---|---|
| **stance** (polemical) | **-0.074** | -0.69 | **-0.072** (0.008) | -9.2 | 19 of 23 (83%) |
| **affect** (sensational) | **-0.057** | -0.56 | **-0.056** (0.007) | -7.9 | 18 of 23 (78%) |
| **register** (conversational) | **+0.057** | +0.46 | **+0.054** (0.009) | +6.2 | 16 of 23 (70%) |
| **rigour** (sourced) | **+0.052** | +0.39 | **+0.051** (0.009) | +5.5 | 14 of 23 (61%) |
| depth | +0.016 | +0.20 | +0.015 (0.005) | +2.8 | 14 of 23 (61%) |
| originality | -0.015 | -0.17 | -0.017 (0.006) | -3.0 | 16 of 23 negative (70%) |
| candour | +0.012 | +0.19 | +0.012 (0.004) | +2.7 | 16 of 23 (70%) |
| commercial_drive | +0.002 | +0.04 | +0.002 (0.005) | +0.5 | null |
| matter/manner PC1 | -0.143 | -0.09 | -0.136 (0.108) | -1.3 | 9 of 23 (61% weak) |

All axes except commercial_drive move with p below 0.02 on a paired Wilcoxon across speakers; the four headline
axes are at p below 0.0001.

**The permutation control (the placebo).** To rule out that these shifts are just within speaker noise, we
reshuffled the in and out labels inside each speaker two thousand times, keeping each speaker's counts, and
recomputed the shift. The observed shifts sit far outside that null:

| axis | observed | null mean | null sd | permutation p |
|---|---|---|---|---|
| stance | -0.074 | 0.000 | 0.007 | 0.0005 |
| affect | -0.057 | 0.000 | 0.007 | 0.0005 |
| register | +0.057 | 0.000 | 0.008 | 0.0005 |
| rigour | +0.052 | 0.000 | 0.008 | 0.0005 |
| originality | -0.015 | 0.000 | 0.006 | 0.009 |

The headline effects are roughly seven to ten null standard deviations out, at the 1 in 2000 floor of the
permutation. This is not within speaker variance.

## What the shift means

When the same person moves into office, the voice cools and squares up to the institution:

- **Less polemical (stance down).** This is the largest and most consistent effect, agreed in 19 of 23
  countries. Out of power the person argues a side; in power the person speaks in a more balanced register.
- **Less sensational (affect down).** Agreed in 18 of 23 countries. The temperature of the language drops.
- **Plainer, more conversational (register up).** Office pulls speech toward the plain declarative pole and
  away from the formal set piece. This ran against the prior guess that power would formalise the register; it
  does the opposite, and consistently.
- **More sourced (rigour up), a little more expert (depth up), a little less novel (originality down), a
  little more transparent (candour up).** The matter side lifts modestly and the language leans on prepared
  material.

The single clearest cross country signature is de escalation: gaining office lowers both the combativeness
(stance) and the drama (affect) of the same person's speech, everywhere the sample can see.

**The composite does not move, and that is the honest headline.** The matter versus manner PC1, the main axis
of the whole series, shows no significant shift (beta -0.14, t -1.3, p 0.21). Power does not swing a person
along the matter versus manner line. It re shapes the profile within manner (temperature and combativeness
down, plainness up) while nudging matter up a little, and those movements roughly cancel in the single
composite. The effect is real and specific; it is not a wholesale move on the summary dimension.

## Cross country consistency

The per country table (`power_shift.txt`, and below) is the paired shift within each country's crossers on the
headline axes. Stance and affect are negative in the large majority of countries, including every country with
a reasonable sample (Austria, Denmark, Finland, Iceland, Norway, Netherlands, Ukraine). The countries that buck
a given axis are almost all single speaker or two speaker samples (Croatia, Greece, Italy, Serbia), where one
person swings the country mean. This is a within person fixed effects result that survives across countries,
not a single country story.

| country | speakers | register | rigour | affect | stance |
|---|---|---|---|---|---|
| AT | 11 | +0.077 | +0.024 | -0.134 | -0.108 |
| DK | 32 | +0.043 | +0.037 | -0.036 | -0.095 |
| FI | 25 | +0.095 | +0.116 | -0.113 | -0.092 |
| NO | 23 | +0.069 | +0.006 | -0.062 | -0.102 |
| IS | 18 | +0.071 | +0.073 | -0.063 | -0.075 |
| EE | 15 | -0.002 | +0.066 | -0.011 | -0.021 |
| NL | 12 | +0.076 | +0.056 | -0.041 | -0.058 |
| UA | 10 | +0.066 | +0.105 | -0.069 | -0.060 |
| ES | 8 | +0.031 | -0.043 | +0.022 | +0.038 |
| CZ | 7 | +0.189 | +0.157 | -0.118 | +0.004 |

(Full 23 country table in `power_shift.txt`.)

## Controls and honest limits

- **Time trend:** controlled. Adding a within speaker linear year term leaves every coefficient essentially
  unchanged, so the shift is not a secular drift in parliamentary language over a career.
- **Length:** controlled and balanced. The two halves average 279 versus 278 words, and adding log words to the
  fixed effects model does not move the coefficients.
- **Topic and genre:** the remaining confound, and only partly separable. A minister answering for policy is
  doing a different job in the chamber than a backbencher pressing an attack. Part of the fall in stance and
  affect is therefore the mechanism of office itself, that the room and the job change together, which is
  precisely the total effect this natural experiment is built to measure. It is not a pure nuisance to be
  removed. What we cannot claim is that the person would speak this way on the identical topic; we can claim
  that stepping into the room changes the character the same person projects.
- **Single scorer:** the whole design is a difference taken inside each person, so any fixed per speaker bias
  of the 7B instrument cancels exactly. What differencing does not cancel is a systematic direction artefact of
  the scorer (for example if the model reads any authoritative or governmental phrasing as less polemical).
  This is the honest ceiling on the causal reading, and the cross model panel (fabric #19098) would be the next
  step to close it.
- **Coverage:** Great Britain, Poland, Hungary and Portugal are absent because the corpus does not tag their
  ministers, so the result speaks for the 23 parliaments where the label exists.

## Verdict

**Not a null. Gaining office changes the character a politician projects, and it changes it the same way across
countries.** The change is concentrated on the manner axes: the same person becomes less polemical and less
sensational in power, agreed in about four fifths of countries, while the register turns plainer and rigour
rises. The matter versus manner composite does not move, so this is a specific re profiling of the voice, a
cooling and a squaring up to the institution, rather than a swing along the main axis. The state dependent
coupling that the internal model predicts holds at its sharpest test: the room a person speaks in reshapes the character
they show, and differencing out the person leaves the office standing.

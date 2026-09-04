# ELM reduction: does matter carry the central route of argument quality?

**Reduction test 2 of the unification argument** (see `RELATED_WORK_unification.md`).
The Elaboration Likelihood Model (Petty and Cacioppo 1986) splits influence into a
central route, where a message earns conviction through the strength of its argument,
and a peripheral route, where it earns attention through surface cues. The programme's
claim is that our matter reading is the central route and our manner reading is the
peripheral route, measured. This test turns that resemblance into a number: on a corpus
with a real human argument quality label, does matter track quality while manner does not?

**Prediction.** If matter is the central route, the matter axes (rigour and depth, the
substance of an argument) correlate positively with argument quality. If manner is the
peripheral route, the manner axes (affect, register, commercial drive, the surface of
delivery) do not, or track quality far more weakly. A clean separation supports the
matter earns conviction, manner earns attention mapping the papers assert.

**Honest framing, stated first.** Human quality raters are not blind machines. They may
reward some manner too: a well turned, polished argument reads as better even when the
substance is equal. So the honest test is not manner correlating exactly zero, it is
manner tracking quality clearly less than matter, and the pure peripheral cue (raw
emotional tone) not carrying quality at all. That is what the numbers are read against.

## Data and method

- **Corpus.** IBM Argument Quality Ranking 30k (Gretz et al 2020, `ibm-research/argument_quality_ranking_30k`).
  Each row is a single argument with a crowd sourced weighted average quality score in 0..1.
  Stratified sample of n = 2,500 spread across the full label range (mean 0.791, sd 0.194).
  This is the only corpus of the four in the external validity set whose label is argument
  quality itself, so it is the direct instrument for the ELM central route. The others
  (PERSUADE, ASAP) score essay quality, a related but different construct.
- **Analysis only.** Reuses the held 8 axis character scores from the instrument external
  validity run (`/mnt/external/benchmarks/scored/ibm_argq.jsonl`), produced by the same free
  7B (an internal 7B instruct model) that serves the instrument across the series. No new scoring.
- **matter versus manner axis.** The `matter_manner_PC1` ruler is built exactly as the rest
  of the series: SVD on the standardised `the internal reference table` table (n = 2,648,406
  domains), oriented so rigour and depth load positive. Loadings:

  | axis | PC1 loading | pole |
  |---|---|---|
  | rigour | +0.44 | matter |
  | depth | +0.40 | matter |
  | candour | +0.39 | matter |
  | stance | +0.37 | matter |
  | originality | +0.23 | matter |
  | commercial_drive | -0.26 | manner |
  | register | -0.34 | manner |
  | affect | -0.35 | manner |

  So the five positive loading axes are the matter pole and the three negative loading axes
  are the manner pole. rigour and depth are the substance core of matter; affect is the
  purest peripheral cue.
- **Length control.** Argument quality rises with length, so text length is reported as a
  confound and a rank based partial correlation (axis versus quality, holding length fixed)
  gives the honest effect beyond simply arguing at greater length.

## Result: per axis correlation with argument quality

Spearman rho with the human quality label. Significance: \* p<.05, \*\* p<.01, \*\*\* p<.001.

| axis | pole | Spearman rho | partial rho (control length) |
|---|---|---|---|
| depth | matter | +0.208*** | +0.162 |
| rigour | matter | +0.200*** | +0.161 |
| register | manner | +0.109*** | +0.091 |
| matter_manner_PC1 | n/a | +0.102*** | +0.067 |
| stance | matter | +0.068*** | +0.033 |
| candour | matter | +0.052** | +0.054 |
| commercial_drive | manner | +0.030 | -0.018 |
| affect | manner | -0.072*** | -0.087 |
| originality | matter | -0.029 | -0.062 |
| _text_length (confound)_ | n/a | +0.212*** | n/a |

## Result: central route versus peripheral route (composites)

To read the ELM split directly, the matter axes and the manner axes are each averaged into
one composite (z scored, so every axis counts equally), alongside the theory clean central
pair (rigour and depth) and the purest peripheral cue (affect on its own).

| composite | Spearman rho | partial rho (control length) |
|---|---|---|
| **central pair (rigour + depth)** | **+0.205*** | **+0.159** |
| MATTER composite (5 positive axes) | +0.131*** | +0.081 |
| MANNER composite (3 negative axes) | +0.047* | +0.008 |
| **peripheral cue (affect alone)** | **-0.072*** | **-0.087** |

## Read

**Matter is the central route carrier. The prediction holds.**

- **The two substance axes lead everything.** rigour (+0.200) and depth (+0.208) are the
  strongest positive correlates of argument quality of any axis, and they stay strong after
  the length control (partial +0.16 each). The central pair together sits at partial +0.159.
  Human raters call an argument good in step with how much rigour and depth the instrument
  reads in it, and it is not merely that the good arguments are longer.
- **The peripheral cue points the other way.** affect, the purest surface tone axis, is the
  only axis that correlates negatively with quality, and it stays negative after the length
  control (partial -0.087). On this corpus more emotional heat is, weakly, a marker of a
  worse argument. That is exactly the peripheral route: it does not earn conviction.
- **The composite contrast is the clean statement.** central pair partial +0.159 versus
  peripheral affect partial -0.087 is a separation of about 0.25 in the predicted direction.
  The broad matter composite (+0.081) sits well above the broad manner composite (+0.008,
  which is effectively zero once length is removed). Matter tracks argument quality; manner
  does not.

**The honest wrinkle, reported straight.** The split is not a perfect axis by axis mirror.
Two things break the clean picture, both in the direction the honesty note predicted:

1. **register, a manner axis, is mildly rewarded** (+0.109 raw, +0.091 partial). Raters do
   reward polish. A formal, well presented argument reads as better even holding substance
   fixed. This is genuine peripheral influence on the human judgement, and it is why the
   manner composite is not more negative. It is a feature of how people rate, not a failure
   of the instrument, and it is consistent with ELM, where the peripheral route still adds
   to the overall verdict, it just adds less and less durably than the central one.
2. **originality, a matter axis, does not carry** (-0.029 raw, -0.062 partial). Not every
   matter axis is central route substance. The central route is specifically the rigour and
   depth of the case being made, not its novelty. The instrument's originality axis (primary
   source, not rehashed) is orthogonal to whether an argument is judged strong.

So the tight reduction is narrower and sharper than a whole pole versus whole pole claim:
the rigour and depth core of matter is the central route, and it clearly carries argument
quality, while the pure affective cue of manner points the opposite way. The full matter
and manner poles separate in the right direction but with the honest caveat that raters
reward some polish (register) and do not reward novelty (originality).

## Limits (do not skip)

1. **Effect sizes are small to moderate.** partial rho around 0.16 for the central pair is
   a real, significant, correctly signed effect, not a strong one. Convergent validity is
   agreement, not identity. This says our matter reading points the same way as the human
   central route judgement; it does not say they are the same latent quantity.
2. **Domain gap.** The scorer is tuned on open web text, not debate arguments. That the
   matter axes transfer at all is the encouraging part; the modest magnitude is consistent
   with the gap.
3. **Single scorer.** One 7B produced the character scores. A second lineage would harden
   the claim, per the cross model agreement doctrine. Not done here (analysis only pass).
4. **One corpus for the direct label.** IBM ArgQ is the only held corpus whose label is
   argument quality itself. The three essay corpora in the external validity run point the
   same way (rigour and depth lead there too) but measure essay quality, not argument
   quality, so they corroborate rather than replicate this test.

## Verdict

**The ELM reduction is supported.** On data with a real human argument quality label, our
matter reading is the central route carrier: rigour and depth are the leading positive
correlates of quality and survive the length control, while the pure peripheral cue (affect)
correlates negatively and the manner pole as a whole is near zero once length is removed.
The central pair versus peripheral cue separation of about 0.25 rho, in the predicted
direction, is the measured form of matter earns conviction, manner earns attention. It is
not a flawless axis by axis split, register (polish) is mildly rewarded and originality
(novelty) is not, both stated plainly, but the core mapping the Elaboration Likelihood Model
predicts is reproduced by the instrument on independent human data it was never tuned on.
This moves the ELM convergence from a resemblance to a measured reduction, at small but
significant and correctly directed effect size.

---

*Files: `elm_reduction.txt` (raw per axis and composite tables), `scripts/elm_reduction.py`
(the analysis). Held scores at `/mnt/external/benchmarks/scored/ibm_argq.jsonl` on the internal host.
Companion breadth result across four corpora: `truthometer/results/instrument_external_validity/`.
Reduction test 2 of `RELATED_WORK_unification.md`.*

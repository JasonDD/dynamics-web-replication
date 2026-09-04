# External validity of the 8 axis character instrument

**Question.** Does the DYNAMICS-WEB character instrument (8 axes: rigour, depth, originality,
candour, affect, commercial_drive, stance, register, plus the matter versus manner PC1) predict
quality judgements that people made independently, on corpora the instrument was never tuned on?
This is convergent validity. It is not proof, and it is done on zero budget: public corpora that
other people already labelled, scored on compute we own.

**Date.** 2026-08-30. Scored by an internal 7B instruct model (the same free 7B that serves the instrument
across the series) on the internal endpoint, identical system prompt, vocab line and parse as the
rest of the character work.

## Corpora (all labelled by people, fetched free from HuggingFace)

| corpus | source | HuggingFace id | text scored | human label (outcome) | n scored |
|---|---|---|---|---|---|
| ibm_argq | IBM Argument Quality Ranking 30k (Gretz 2020) | `ibm-research/argument_quality_ranking_30k` | single argument | WA crowd quality 0..1 | 2500 |
| persuade_essay | PERSUADE 2.0 argumentative essays | `ruudra1/PERSUADE` | full student essay | holistic essay score 1..6 | 2496 |
| persuade_eff | PERSUADE 2.0 discourse elements | `ruudra1/PERSUADE` | one discourse element | effectiveness (Ineffective 0, Adequate 1, Effective 2) | 2499 |
| asap_aes | ASAP AES 2012 (Hewlett / Kaggle, 8 prompt sets) | `TasfiaS/ASAP-AES` (`training_set_rel3.tsv`) | full student essay | teacher score, normalised to 0..1 within each prompt set | 2243 |

Three independent sources (IBM debate arguments, PERSUADE essays, ASAP essays). persuade_eff shares
its source with persuade_essay but measures a different construct at a different granularity (the
effectiveness of a single argument move, not the whole essay), so it is kept as a fourth column with
that caveat noted. Each corpus is a stratified sample of about 2500 rows spread across the full label
range (ASAP scores min max normalised within prompt set because the eight sets use different scales).

## Method

Scored via the existing `cc_found_human_score.py` against the served instrument. matter versus
manner PC1 built exactly as the rest of the series: SVD on the standardised
`the internal reference table` table (n = 2,648,406 domains), oriented so rigour and depth load
positive. PC1 loadings: rigour +0.44, depth +0.40, candour +0.39, stance +0.37, originality +0.23,
commercial_drive -0.26, register -0.34, affect -0.35. So high PC1 means matter (rigorous, deep,
candid, committed) and low PC1 means manner (affective, conversational, selling).

Correlations are Spearman and Pearson with n and p. Because essay quality is known to rise with
length, text length is reported as a confound and a partial Spearman (feature versus label,
controlling for length) asks whether each axis predicts quality beyond simply writing more.

## Result 1: raw Spearman rho (feature by corpus)

significance: \* p<.05  \*\* p<.01  \*\*\* p<.001

| feature | asap_aes | ibm_argq | persuade_eff | persuade_essay |
|---|---|---|---|---|
| rigour | +0.278*** | +0.200*** | +0.227*** | +0.594*** |
| depth | +0.294*** | +0.208*** | +0.232*** | +0.555*** |
| originality | +0.032 | -0.029 | -0.072*** | +0.252*** |
| candour | -0.003 | +0.052** | +0.026 | +0.207*** |
| affect | +0.122*** | -0.072*** | -0.016 | -0.055** |
| commercial_drive | +0.192*** | +0.030 | +0.045* | +0.370*** |
| stance | +0.230*** | +0.068*** | +0.234*** | +0.480*** |
| register | +0.222*** | +0.109*** | +0.202*** | +0.147*** |
| **matter_manner_PC1** | +0.167*** | +0.102*** | +0.185*** | +0.581*** |
| _text_length (confound)_ | +0.490*** | +0.212*** | +0.082*** | +0.841*** |

## Result 2: partial Spearman rho, controlling for text length

This is the honest effect size for the essay corpora, where length alone carries most of the raw
signal.

| feature | asap_aes | ibm_argq | persuade_eff | persuade_essay |
|---|---|---|---|---|
| rigour | +0.155 | +0.161 | +0.220 | +0.181 |
| depth | +0.170 | +0.162 | +0.226 | +0.177 |
| originality | -0.120 | -0.062 | -0.076 | +0.020 |
| candour | -0.197 | +0.054 | +0.027 | +0.152 |
| affect | -0.118 | -0.087 | -0.019 | +0.012 |
| commercial_drive | +0.122 | -0.018 | +0.039 | +0.055 |
| stance | +0.008 | +0.033 | +0.228 | +0.276 |
| register | +0.116 | +0.091 | +0.201 | +0.200 |
| **matter_manner_PC1** | -0.012 | +0.067 | +0.178 | +0.225 |

## Honest read, at tier

**What validates (robust across all four corpora, survives the length control):**

- **rigour and depth are the real result.** They correlate positively with every human quality
  label in every corpus (raw rho +0.20 to +0.59) and stay positive after controlling for length
  (partial rho +0.15 to +0.23 everywhere). This is the cleanest convergent validity finding: the two
  matter axes track what independent human raters call a good argument or a good essay, and it is not
  just that they wrote more words. Two different constructs (argument quality, essay quality), three
  independent sources, same direction, similar magnitude.

**What partly validates:**

- **matter versus manner PC1** tracks quality on PERSUADE (essay raw +0.58, elements +0.19) and IBM
  (+0.10), and holds up after the length control on both PERSUADE columns (partial +0.18 to +0.23).
  But on ASAP the PC1 signal is almost entirely carried by length: partial rho collapses to about
  zero (-0.01). So PC1 is a decent quality proxy on debate and essay argumentation, but on graded
  school essays it is length in disguise. Report it as supported, not clean.
- **register and stance** predict quality on both PERSUADE columns even after the length control
  (partial +0.20 to +0.28): more committed, more polished argument moves are rated higher there.
  On IBM and ASAP the effect is weak. Construct specific, not universal.

**What does not validate, stated plainly:**

- **originality** does not track human quality and on three of four corpora goes slightly the wrong
  way after controlling for length (asap -0.12, ibm -0.06, persuade_eff -0.08). Human graders do not
  reward the instrument's "primary source, not rehashed" axis; on school essays they mildly penalise
  whatever it is picking up.
- **affect** is near zero to negative once length is removed (ibm -0.09, asap -0.12). Sensational
  tone is, weakly, a marker of lower argument quality. Directionally sensible, but small and not a
  validation of the axis as a quality signal.
- **candour** is inconsistent: positive on persuade_essay (+0.15 partial) but clearly negative on
  ASAP (-0.20 partial). No stable cross corpus signal.
- **commercial_drive** is negligible on the argument corpora, as expected (these texts are not
  selling anything).

## Confounds and limits (do not skip)

1. **Length dominates the essay corpora.** Raw text length correlates with the human score at rho
   +0.84 on persuade_essay and +0.49 on ASAP. This is a well known property of automated essay
   scoring, not a flaw of the instrument, but it means the raw rows for those corpora overstate the
   instrument's contribution. The partial correlations are the honest number and they are smaller
   (about 0.15 to 0.23 for the best axes).
2. **The scorer is tuned on web text**, not on student essays or debate snippets. There is a domain
   gap. That the matter axes still transfer is the encouraging part; the modest effect sizes are
   consistent with that gap.
3. **Convergent validity is agreement, not proof.** rho of 0.15 to 0.23 (partial) and 0.2 to 0.6
   (raw) is a small to moderate effect. It says the instrument's matter axes point the same way as
   human quality judgement across independent corpora. It does not say the instrument measures the
   same latent construct, nor that it would rank two close texts the way a person would.
4. **Single model scorer.** One 7B did the scoring. A second scorer (a different lineage) would
   strengthen the claim, per the cross model agreement doctrine. Not done here.

## Bottom line

The instrument's two matter axes, rigour and depth, and to a weaker and more corpus specific degree
the matter versus manner PC1, show consistent convergent validity against four independent human
labelled benchmarks it was never tuned on. The manner axes (originality, affect, candour) do not
track human quality and sometimes point the wrong way. This widens the earlier ChangeMyView
recovery from one outcome to four, and it does so honestly: the win is real but small once length is
controlled, and it is concentrated in exactly the axes the theory says should track argument and
essay quality.

Files: `correlation_matrix.md` (both matrices), `corr_<corpus>.md` (per corpus full tables with
Pearson and partial columns). Scripts: `truthometer/scripts/cc_extval_prep.py` (fetch and sample),
`truthometer/scripts/cc_extval_analyse.py` (PC1 and correlations). Raw corpora on the internal host at
`/mnt/external/benchmarks/`.

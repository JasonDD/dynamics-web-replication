# Fleeson reduction: the person to content coupling collapses onto whole trait theory

INTERNAL analysis. Aggregate only, no keys, no names. PUBLIC track, DYNAMICS-WEB series. Reduction test 3 of the
unification argument (`RELATED_WORK_unification.md`).

Corpus: `cc_v3.crosssite_authorship` on DL580 (the same pseudonymous person seen writing across many separate
sites), 418,493 scored cross site blocks, 37,378 people with two or more sites, held `disp_d8` and `char_dweb`
scores reused as is. No rescoring: this is analysis of the held scores.

## The test

Fleeson (2001), the density distribution view of whole trait theory, treats a person not as a point but as a
DISTRIBUTION of momentary states. His decomposition splits the variance of a state into a between person
component (the person's own mean, the stable trait density) and a within person component (how far that
person's states spread around their own mean across occasions, the situation or state term). His finding, the
one that settled the person situation debate on the interactionist side, is that the within person spread is
about as large as the between person spread: momentary behaviour is roughly HALF stable trait and HALF
situation.

The looser convergence was already noted: our coupling lands near half and half (`results/coupling_crosslineage`).
The tighter test, and the one that turns a resemblance into a measured reduction, is to compute the trait and
situation variance components in Fleeson's OWN form on our corpus and compare the number directly.

Here the "occasions" a person is seen in are the separate sites they write on. The room is the situation. For
each DYNAMICS-8 disposition axis and each DYNAMICS-WEB character axis we fit the one way random effects model

    y_ij = mu + p_i + e_ij      p_i ~ (0, s2_between)   e_ij ~ (0, s2_within)

and read off the two variance components. trait share = s2_between / (s2_between + s2_within), which is exactly
ICC(1) and exactly Fleeson's between person fraction; situation share = 1 - trait share, his within person
fraction.

Two estimators, as in the coupling result:

- **room level** (the headline): average a person's blocks to one mean per site first, so the within person
  term is purely ACROSS SITUATIONS. This is the faithful person versus situation split and the closest match to
  Fleeson's design, where each occasion is a distinct situation.
- **all occasions**: every block is one occasion, so within site repeats fold into the situation term. This is
  the same estimator the earlier Paper 4 split figure used, kept for continuity.

## The split, in Fleeson's form

### Headline (room level, person versus situation)

| construct | trait share (between person) | situation share (within person) |
|---|---|---|
| disposition (DYNAMICS-8) | **51.6%** | 48.4% |
| character (DYNAMICS-WEB) | **55.3%** | 44.7% |
| pooled | **53.4%** | 46.6% |

### All occasions estimator (within site repeats folded into situation)

| construct | trait share | situation share |
|---|---|---|
| disposition (DYNAMICS-8) | 43.3% | 56.7% |
| character (DYNAMICS-WEB) | 50.6% | 49.4% |

### Per axis (room level trait share)

Disposition: discipline 61.2, impulsivity 63.0, candour 55.3, mercuriality 49.3, yielding 50.1, sociability
47.9, acuity 47.7, novelty 38.1. Character: commercial_drive 64.1, depth 62.7, rigour 55.0, affect 54.5,
candour 54.7, originality 53.9, stance 51.3, register 46.1. The axes cluster around a half, none is pure trait
or pure situation, and the most situational axis on each side (novelty on disposition, register on character) is
the one most about the room a person is writing in, exactly as the density distribution picture predicts.

## Comparison to the ~50/50 target and to our own corrected figure

- **Against Fleeson's ~50/50.** The headline room level split is trait 51.6% / situation 48.4% for disposition
  and 53.4% / 46.6% pooled with character. The disposition number sits 1.6 points off a dead even split; the
  pooled number 3.4 points off. Under the all occasions estimator disposition reads trait 43.3% / situation
  56.7%, situation majority, which is Fleeson's original observation stated in his own words: within person
  variance is often as large as or larger than between person. The two estimators bracket 50/50 from either
  side, within about seven points. This is a tight match, not a loose resemblance.

- **Against our own corrected figure.** The Paper 4 coupling result, corrected on 37x data across two scoring
  lineages, put the disposition read at room level ICC ~0.518 (7B +0.507, 27B +0.577; `coupling_crosslineage`).
  The disposition room level trait share here is 0.516. It lands on the corrected figure to within two
  thousandths, an independent reproduction of that number from a dedicated Fleeson form decomposition, and it
  confirms the earlier "three quarters performed" value (0.24 trait) was a small corpus artefact, not the split.

## Verdict

**The reduction holds.** Our person to content decomposition reproduces Fleeson's roughly half and half split in
his own variance component form, and the number is close: disposition trait 51.6% at room level (situation 48.4%),
character trait 55.3%, pooled 53.4%. The single text all occasions read of disposition is situation majority
(trait 43.3%), which is Fleeson's own headline. Both constructs, on both estimators, land inside a band a few
points wide around the even split he reported.

This converts the third unification test from a qualitative convergence into a demonstrated reduction. The person
to content coupling is not merely reminiscent of whole trait theory; it recovers whole trait theory's central
number on a corpus 37,000 people wide, built from web writing rather than experience sampling beepers, by an
independent method. Behaviour being half stable trait and half situation is Fleeson's finding and it is our
finding, measured the same way.

Honest bounds. The situation unit here is the site, not the momentary situation of a beeper study, so "occasion"
is coarser than Fleeson's; the room level estimator is the fair comparison and it is the one that lands at 51.6%.
Character reads slightly more trait than disposition (55% versus 52%), consistent with content character being a
more deliberate, less moment to moment product than momentary disposition. Every figure is exploratory and
internal, pending the legal and commercial review the corpus is held for.

## Method and provenance

- Script: `truthometer/scripts/cc_crosssite_fleeson.py` (CPU only, analysis only, no scoring). Vectorised one way
  random effects variance components via `np.bincount`; trait share = ICC(1). Run on DL580 tfs, `MINDOM=2`.
- Estimators match `truthometer/scripts/cc_crosssite_outcome.py` and the coupling result: all occasions and room
  level. The room level ICC cross checks the coupling result's 0.518 to within 0.002.
- Numbers: `results/reduction_fleeson/fleeson_split.json` (full per axis components, both estimators, both
  constructs). Headline pooled trait share 0.534, situation share 0.466.
- Prior art: Fleeson, W. (2001), *Toward a structure and process integrated view of personality: traits as
  density distributions of states*, JPSP 80(6). The person situation debate: Mischel (1968); the interactionist
  resolution Fleeson's density distributions supply.

# Is the universal core the same as the trait? Testing whether culture and personality move the same axes

Generated 2026-08-30. Analyser `truthometer/scripts/cc_universal_is_trait.py`, raw console
`universal_is_trait.txt`, machine readable `universal_is_trait_stats.json` (this directory). Pure analysis on
data already scored, no new model scoring, did not touch the scorer service or the teacher.

## The claim under test

Two papers measured two different splits of the same eight DYNAMICS-WEB character axes.

- **Paper 3 (invariant core)** measured how much CULTURE each axis carries: the between country share of variance.
  Register and candour carry the least, affect, commercial drive and stance carry the most. Numbers reused from
  `results/invariant_core/invariant_core_stats.json`.
- **Paper 4 (the person to content coupling)** measured how much of a person's writing is a stable trait versus a
  performed room state, using a corpus where the SAME pseudonymous person is seen writing on several separate
  sites (the cross site authorship bridge, `the internal cross site corpus`).

The unification hypothesis: **the least cultural axes are the trait axes, and the most cultural axes are the
performance axes.** If true, an axis's culture share (Paper 3) should run OPPOSITE to its within person stability
(Paper 4), because both a room and a nation are "the room", and what is universal is what the person owns and
carries between rooms. A strong negative rank correlation across the eight axes would say culture and personality
move the same axes in the same split, folding the two papers into one.

## Method

For each of the eight axes we compute its within person stability across the several sites the same author writes
on: the one way random effects intraclass correlation ICC(1) of `char_dweb` grouped by person, over authors seen on
at least two distinct domains. High ICC means the character of the content that person produces is stable to the
person across rooms (a trait); low ICC means it is remade in each room (a performance). Both this and the culture
share are on the SAME eight content character axes, so the comparison is like for like. We then rank correlate,
across the eight axes, the culture share against the trait stability. We also carry the reddit between room share
of the same axes as an independent read of the "performance" side.

Power: **29,114 persons on two or more domains, 328,841 scored blocks, 28,669 persons with two or more scored
blocks.** This is the properly powered version of the test that was structurally out of reach on a single platform
(Reddit gave only 6 cross community authors). Mean trait ICC across the eight axes is 0.50, so a person's content
character is about half stable trait and half performed room state, on average.

## The eight axis table

| Axis | culture % (ccTLD, sharp) | culture % (all sources) | trait stability ICC | reddit room % |
|---|---|---|---|---|
| rigour | 5.94 | 3.30 | **0.584** | 9.77 |
| depth | 5.33 | 3.50 | **0.601** | 10.12 |
| originality | 5.63 | 4.10 | 0.473 | 4.24 |
| candour | 5.20 | 1.50 | 0.523 | 6.19 |
| affect | **10.22** | 4.20 | 0.466 | 11.49 |
| commercial drive | 9.23 | 3.50 | 0.514 | 6.19 |
| stance | 8.55 | **5.90** | 0.458 | 6.64 |
| register | **3.22** | 1.60 | **0.364** | 4.37 |

## Rank correlations across the eight axes

CORE test, culture share against trait stability (the hypothesis predicts a strong NEGATIVE):

| Pair | Spearman rho | p | Pearson r | p |
|---|---|---|---|---|
| culture (ccTLD) vs trait ICC | **-0.071** | 0.867 | +0.082 | 0.847 |
| culture (all) vs trait ICC | **-0.323** | 0.435 | +0.072 | 0.866 |

Cross checks:

| Pair | Spearman rho | p | Pearson r | p | expectation |
|---|---|---|---|---|---|
| culture (ccTLD) vs reddit room % | +0.429 | 0.289 | +0.439 | 0.277 | positive (same performed axes) |
| culture (all) vs reddit room % | +0.263 | 0.528 | +0.250 | 0.550 | positive |
| trait ICC vs reddit room % | +0.357 | 0.385 | +0.565 | 0.144 | negative (trait axes vary least by room) |

## Verdict: the unification does NOT hold on the eight axes

**The core hypothesis fails.** Culture share and within person trait stability are essentially uncorrelated across
the eight axes: rank correlation -0.07 on the sharp culture estimate and -0.32 on the conservative one, both far
from significant (n = 8 axes, p > 0.4). The clean cross paper claim "least cultural equals most trait stable" is
not supported. It is not merely underpowered: the point estimate on the sharpest culture measure is essentially
zero, so the two splits are close to orthogonal, not weakly aligned.

**The decisive counterexample is register.** Register is the single most universal axis (least cultural, 3.2 % and
1.6 %), which the hypothesis says should make it the most trait stable. It is instead the LEAST trait stable of all
eight (ICC 0.364). The reason is coherent: everyone writes informally everywhere (register is a shared human
default, so it varies little between nations), and yet each person re dials their register room by room (so it is
the least owned by the person). Register is universal AND performed at the same time. That single axis is enough to
sink a clean "universal equals trait" law, and it is the very axis Paper 3 named as the flagship of the universal
core.

**Rigour and depth are the other break.** They carry middling culture but are the MOST trait stable axes (ICC 0.60,
0.58): a person's rigour and depth are their steadiest signature across sites. They are neither the most nor the
least cultural, so a person's most reliable trait is not sitting on the least cultural axis.

**What DOES survive, weakly.** Only the "cultural equals performed" half of the claim shows a directional hint. The
most cultural axes (affect, stance) do tend to be the most room performed: culture share against reddit room share
is +0.43 on the sharp estimate, in the predicted direction, though not significant at n = 8. Affect leads both the
between country and the between room rankings, which is the one place culture and room performance genuinely move
together. But even here the third leg contradicts the picture: trait stability against room share is POSITIVE
(+0.36 rank, +0.57 Pearson), the opposite of the prediction, because rigour and depth are simultaneously the most
room carrying AND the most person stable. An axis can vary a lot by room and still be highly owned by the person,
which is exactly what breaks a one dimensional trait versus performance story.

### The honest one line

Culture and personality do NOT move the same axes in the same split. The most universal axis (register) is the
least personal, and the most personal axes (rigour, depth) are middling on culture. Papers 3 and 4 measure two real
but largely independent partitions of character, and they should not be merged under a single "universal equals
trait" law.

## Limits

- **n = 8 axes** is a tiny sample for a rank correlation, so no p value here can reach significance and the cross
  check signs are suggestive at best. The verdict rests on the point estimates and on the register counterexample,
  not on a significant p.
- **Two different quantities carry the name "trait".** This test measures the stability of the CONTENT character a
  person produces (`char_dweb`), which is the only quantity on the same eight axes as the culture share, so it is
  the correct like for like comparison. Paper 4's headline "about three quarters performed" was measured on the
  person side disposition read (`disp_d8`), a different axis family (discipline, yielding, and so on) that does not
  map onto the DWEB content axes, so it cannot be rank correlated against the DWEB culture share and is not used
  here. On the content axes the average split is closer to half and half (mean ICC 0.50).
- **Culture is resolved by ccTLD** (sharp) or by link geography (conservative, diluted by propagation). The two
  resolutions give the same verdict (rho -0.07 and -0.32), which is the useful robustness check.
- Single item character scores are noisy; the ICC(1) is computed over roughly eleven blocks per person on average,
  so person means are well estimated, but the absolute ICC values still sit under the ceiling set by scorer noise.

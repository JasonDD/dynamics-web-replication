# PF-4B-GENRE-20260829-REV-1 — RESULT

Fit run against FROZEN genre assignment (audit hash 2d701e0c; classifier committed 9d3bd4506), 7B disposition
(disp_d8_behav_7b — the column carrying the 400-community 0.74 coupling; 27B pass incomplete, 622 rows).
disp = community mean PLASTICITY (sociability+novelty, half A); character half B; 394 communities (other_misc
excluded), 14 genres. Script truthometer/scripts/cc_genre_state_fit.py.

## DEVIATION (documented catch #4): CV corrected from leave-one-genre-out to leave-communities-out.
Leave-one-genre-out cannot distinguish Model A (genre random slope) from Model B (genre fixed effect): a fully
held-out genre has parameters in neither, so both predict the population line and RMSE is identical by
construction. Leave-communities-out (stratified 5-fold, every genre in training) lets Null/B/A diverge on
held-out communities of known genres. Taxonomy hash unchanged; only the CV partition corrected.

## Held-out RMSE (lower better)
| dim | Null (disp) | +genre level (B) | +genre x disp slope (A) |
|---|---|---|---|
| matter_manner (PRIMARY) | 0.990 | 0.923 | 0.928 |
| originality             | 0.925 | 0.868 | 0.865 |
| stance                  | 0.977 | 0.876 | 0.881 |

## Secondary (genre disp-slope variance + BLUP order)
tau^2_1: matter_manner 0.0051, originality 0.0015, stance 0.0074 (all small; LRT numerically unstable, singular RE).
matter_manner slope BLUPs: politics/profession/place negative; support/snark/reality-TV positive (orders sensibly).

## READ (interpretation tree)
Genre is a strong LEVEL effect, NOT a coupling-slope modulator. Adding genre as a location term cuts RMSE 7-10%
(Null->B); adding the genre-by-disposition SLOPE on top does nothing beyond it (B->A flat, slightly worse on
matter/manner and stance, a whisker better on originality). So genre enters the state as an ADDITIVE room
LOCATION coordinate (the community's matter/manner centre), not as an interaction that gates how disposition
couples to character. In M.W.S terms: genre shifts the intercept, the genre x disposition off-diagonal of W is
~0 on the dominant axis. This REFINES the favoured prior (matter/manner absorbs genre): genre is not nuisance
(it carries a lot) but what it carries is the room's location, and the disposition->character coupling is
genre-INVARIANT. Section 7 fork resolves toward: keep genre as a location term in S, do NOT model it as gating W.
Originality is the one dim with a whisper of slope-modulation (A<B<Null), consistent with it being the partly
independent PC2, but the margin (0.003) is within noise -> suggestive at most, not claimed.

# PF-4B-GENRE — 27B second-lineage confirmation of genre-as-state

Independent-lineage replication of the genre test, on the 27B disposition (disp_d8_behav_27b, 79,293 comments,
390 communities, 14 genres) vs the original 7B run. Same frozen taxonomy (hash 2d701e0c), same model spec,
same leave-communities-out CV. This is the cross-lineage check the programme's guard demands.

## Held-out RMSE, both lineages (lower better)
| dim | lineage | Null (disp) | +genre level (B) | +genre x disp slope (A) | A vs B |
|---|---|---|---|---|---|
| matter_manner | 7B  | 0.990 | 0.923 | 0.928 | A worse by 0.005 |
| matter_manner | 27B | 0.953 | 0.901 | 0.892 | A better by 0.009 |
| originality   | 7B  | 0.925 | 0.868 | 0.865 | A better by 0.003 |
| originality   | 27B | 0.764 | 0.725 | 0.718 | A better by 0.007 |
| stance        | 7B  | 0.977 | 0.876 | 0.881 | A worse by 0.005 |
| stance        | 27B | 0.937 | 0.841 | 0.845 | A worse by 0.004 |

Secondary tau^2_1 (genre disp-slope variance): 7B matter_manner 0.0051; 27B 0.0394, LRT chi2=5.33 p=0.070.

## Honest read
1. **CONFIRMED across both lineages: genre is a strong LEVEL effect.** Adding genre as a location term cuts
   held-out RMSE ~5-10% on both lineages (Null->B: 7B 0.990->0.923; 27B 0.953->0.901). The core finding —
   genre is a real state coordinate that shifts where a community sits on the axis — replicates independently.
   This takes the LEVEL claim from firm to settled.
2. **NOT cleanly confirmed: the "genre does NOT modulate the coupling / W is invariant" sub-claim.** The two
   lineages disagree in degree. The 7B found the genre-by-disposition SLOPE adds nothing (A ~ B, slope hurts a
   hair) -> "pure location, W invariant". The 27B leans the other way: A beats B by <1% RMSE on matter/manner and
   originality, and the genre-slope variance is larger (0.039 vs 0.005) and marginally significant (p=0.070).
3. **What this means, stated plainly.** The genre-slope (modulation) effect is at or near the noise floor in BOTH
   lineages (all A-vs-B margins <1% RMSE) and its SIGN is not stable across them (7B slightly negative, 27B
   slightly positive; 27B tau^2 marginal). So genre-modulation is NOT robustly distinguishable from zero, and it
   is NOT robustly non-zero either. The dominant, replicated effect is the LEVEL; the modulation is unresolved.

## Consequence for the paper (v60 Section 7)
v60 states the field is "affine in genre, W invariant" — genre a pure location, not a modulator. That was the 7B
reading. The 27B does not confirm the strict-invariance half; it shows a marginal (p=0.07) hint of modulation the
7B did not. The honest claim to carry: **genre is dominantly a location effect (robust across two independent
model lineages); whether it also weakly modulates the disposition-to-character coupling is unresolved — the
lighter lineage says no, the heavier lineage marginally suggests yes, and both put the effect below 1% of held-out
error.** The level result hardens to settled; the strict-W-invariance sub-claim should be softened, not asserted.
This is exactly what the cross-lineage guard is for: it confirmed the load-bearing effect and caught an
over-stated sub-claim. A paper temper (v62) is owed, not run here.

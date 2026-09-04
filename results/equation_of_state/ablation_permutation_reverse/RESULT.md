# Ablation, permutation null and reverse prediction for the three part model

*DYNAMICS-WEB series, 3 September 2026. Script `cc_state_ablation.py` (built on the competitor test's data
path, so folds, records and models are identical). Held out gain = 1 − SSE(model) / SSE(room mean), pooled
over the eight character axes, five person grouped folds. Domains: `the internal cross site corpus`, 1,008
rooms, 161,867 person room records, 48,293 persons. Subreddits: `the internal Reddit corpus`, 400 rooms, 50,346
records, 47,514 persons.*

## Ablation: what each named part earns

| Model | Subreddits | Web domains |
|---|---|---|
| room mean only | 0 | 0 |
| curved map, no room term | +0.056 | **−0.287** |
| room shift, straight map | +0.091 | +0.036 |
| room shift, curved map | +0.099 | +0.041 |
| room shift, curved map, room bend (the three part model) | **+0.101** | **+0.065** |
| the same with the rank two plane on the shift | +0.090 | +0.003 |

On the domains the room shift is the largest term in the equation: a map with no room term does far worse
than the room average. The bend earns +0.025 on the domains, the largest single addition after the shift,
and +0.001 on the subreddits, which is the "bend on domains, absent on subreddits" finding by a third
method. The rank two plane costs +0.011 on the subreddits and +0.062 on the domains.

## Permutation null: disposition shuffled among persons within each room

Twenty shuffles per corpus, the three part model refitted each time. Null gain −0.0001 (sd 0.0000) on the
subreddits against a real +0.1005; −0.0000 (sd 0.0000) on the domains against +0.0654. Nothing the model
finds is available once disposition is decoupled from the person, so it reads disposition, not room
artefacts.

## Reverse prediction: character to disposition

With the same folds and a room shift, predicting disposition from character gains +0.269 on the subreddits
and +0.126 on the domains, against +0.091 and +0.036 for the linear forward direction. The reverse is
about three times easier. That is expected from eight inputs predicting two rather than two predicting
eight and is not, on its own, evidence that the reader reads both from the same text; the guard that
settles that question is the cross reader run in `../../second_reader_lineage/`, where disposition and
character are read by different models and the coupling keeps its shape. Reported as measured.

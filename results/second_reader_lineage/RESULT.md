# The second reader lineage: does the coupling survive a different model reading the same text?

*DYNAMICS-WEB series, 3 September 2026. The within room differencing analysis rerun with disposition and
character re read by Mistral 7B Instruct v0.2 (a different pretraining lineage from the Qwen readers that
produced every earlier number), on a matched sample of 45,502 rows, 23,412 persons, 300 rooms of the cross
site corpus (`cc_v3.xlineage_diff_sample`). Legs: A both by the first reader; B both by Mistral; X the
cross legs, disposition by one reader and character by the other, so neither side can copy the other.
JSONs in this directory; scoring scripts `cc_crosssite_score_xlineage_mistral.py`, driver
`cc_diff_xlineage_driver.sh`.*

## The pooled coupling, rows disposition (plasticity, stability), columns character (matter against manner, originality)

| Leg | W | Anti diagonal |
|---|---|---|
| A, first reader both sides | [[−0.03, **+0.18**], [**+0.14**, −0.02]] | clean |
| B, Mistral both sides | [[+0.20, **+0.17**], [**+0.09**, −0.02]] | holds, plus a diagonal plasticity to matter term the first reader lacks |
| X, disposition Mistral, character first reader | [[−0.04, **+0.10**], [**+0.08**, −0.08]] | holds with circularity broken |
| X, disposition first reader, character Mistral | [[+0.07, **+0.07**], [**+0.19**, +0.09]] | holds with circularity broken |

Both anti diagonal cells are positive with bootstrap intervals clear of zero in all four fits, including
the two cross reader legs. The bend survives every leg: the room to room spread of W exceeds its sampling
error in all four cells at p = 0.005 (excess 0.07 to 0.15 on A, 0.13 to 0.21 on B, 0.10 to 0.15 on X).

## Reader agreement per axis (r, same rows)

Disposition: discipline 0.49, candour 0.49, sociability 0.48, novelty 0.36, impulsivity 0.23, acuity 0.20,
mercuriality 0.08, **yielding −0.06**. Character: rigour 0.47, depth 0.45, originality 0.27. The two
readers do not agree on yielding or mercuriality, so the stability metatrait (discipline plus yielding
minus mercuriality) is the shakier of the two; the matter against manner ruler's agreement is 0.54 raw and
0.42 within room.

## Reading

The coupling and the bend are not one model's habit. The held out gains stay small on every leg (leave
room out R² 0.003 to 0.03), and the second reader's own leg carries an extra diagonal term the first
does not, which is a reader difference to report rather than resolve here.

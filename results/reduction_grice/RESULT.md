# Grice reduction: does the character instrument recover the maxims of the cooperative principle?

*DYNAMICS-WEB series, 3 September 2026. Scripts `grice_reduction.py` (judge) and `grice_length_control.py`.
A capped sample of 15,000 held `the internal Reddit corpus` comments already scored on the eight axis instrument was
judged by Mistral 7B Instruct, a different pretraining lineage from the an internal model reader that produced the
character scores, for how far each violates Grice's four maxims (0 observes, 1 flagrantly violates):
quantity (the right amount of information), quality (backed by evidence), relation (relevant), manner
(clear and brief). Violations are correlated with the eight axes and the matter against manner PC1. The
expectation was written into the script before the correlations were read: rigour and depth should fall as
the quantity and quality maxims are violated, and the manner pole axes should track the manner maxim.*

## matter against manner PC1 versus each maxim violation

| Maxim | raw item | raw within room | length controlled partial |
|---|---|---|---|
| relation | +0.256 | +0.240 | **+0.176** |
| quantity | +0.238 | +0.231 | +0.115 |
| quality | +0.185 | +0.172 | +0.096 |
| manner | +0.088 | +0.077 | +0.041 |

Per axis (item r): rigour and depth rise with quantity (+0.28, +0.29), relation (+0.29, +0.30) and quality
(+0.18, +0.18) violation; affect falls with them (−0.21, −0.21); the manner maxim is flat for every axis.
The matter axis is tied to length, r(PC1, log length) = +0.378, so the raw numbers carry a verbosity
component; the length controlled partial correlations halve but do not vanish.

## Reading, including where the prediction was wrong

The written prediction was the wrong sign, and it is reported as such. The matter axis does not fall as the
maxims are violated; it **rises** with violation of quantity and relation. The coherent reading, and the one
the length control supports, is that matter heavy writing is judged to give more information than a casual
thread requires (quantity) and to be less strictly on point (relation), a real pragmatic tension between
informativeness and brevity rather than a failure of cooperation. About half of the raw effect is length;
the residual after a length control is a modest r of 0.12 to 0.18 on quantity and relation, weak on quality,
and a clean null on manner. So the instrument recovers the quantity and relation maxims partially and
correctly signed once length is controlled, and does not recover the manner maxim. It is a tempered
reduction, not the sweeping homology, and it is stated at that tier. One judge lineage, English, a capped
sample; the natural next step is a second judge family and the full corpus.

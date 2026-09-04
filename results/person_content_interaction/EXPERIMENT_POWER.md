# Experiment power: how many people the severe test needs (simulation first)

`cc_experiment_power_design.py` simulates the planned randomised experiment (`EXPERIMENT_DESIGN_the_hammer.md`)
through the exact frozen detection pipeline and asks: what N detects an injected Ashlar shaped interaction of
delta R squared = 0.01 at 80, 90 and 95 per cent power? tau = 0.01, five arms, spread 0.8, 50 repetitions.

## The N curves

| design | N | power at +0.01 |
|---|---|---|
| between subjects (one item per person) | 600 | 0.08 |
| | 1,200 | 0.10 |
| | 2,400 | 0.34 |
| | 4,000 | 0.40 |
| | 6,000 | 0.30 |
| repeated measures (six items per person) | 150 | 0.12 |
| | 300 | 0.30 |
| | 800 | 0.32 |
| | 1,200 | 0.46 |

Neither design reaches 80 per cent power at +0.01 in the range tested. Repeated measures is clearly more
efficient per person (N = 1,200 people times six items beats 6,000 people times one), which is the
economically important result, but it does not on its own clear the bar.

## The binding constraint is the threshold, not just N

The reason mirrors the UCSC assay finding: the held out incremental R squared is a **downward biased**
estimator of a true 0.01 effect (mean held out increment about 0.0075 for a true 0.01), so the frozen +0.01
**held out absolute** pass rule effectively requires a true effect near 0.013 to 0.015. Raising N tightens the
estimate around ~0.0075, which still sits below 0.01, so power plateaus rather than climbing to 0.8. This is a
threshold and estimator mismatch, exposed before a pound was spent, which is exactly what a simulation first
design is for.

## Two design corrections required before the severe test is run (flagged, not silently applied)

1. **Target a larger substantive effect through a stronger manipulation.** The UCSC power curve shows the
   frozen coupling reaches 0.87 power at a true effect of 0.02 and 0.99 at 0.03. So the stimulus set should be
   built to produce genuinely large between arm DYNAMICS separation, aiming for a coupling effect near 0.02
   rather than the bare 0.01 floor. Manipulation strength buys more power than sample size here.
2. **Or restate the decision rule on a less biased estimator.** Define the +0.01 as the **population or in
   sample** increment, with the held out increment used for validation and a permutation test on the coupling
   coefficient as the significance gate, rather than an absolute held out R squared threshold that is biased
   low.

## Consequence for cost

With the corrected target (a strong manipulation aiming near 0.02, repeated measures), the required N is
plausibly in the low thousands of participants; a fresh N curve at the corrected target is the immediate
pre registration step before recruitment. At Prolific rates of roughly four to five pounds per participant for
a twenty minute repeated measures study, low thousands of participants is single digit thousands of pounds up
to roughly fifteen thousand, depending on N and whether a behavioural endpoint is included. The number is set
by the corrected simulation, never by budget.

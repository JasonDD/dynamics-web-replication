# Result: UCSC assay sensitivity (was the hammer capable of breaking the theory?)

**Verdict: no. The UCSC pipeline could not have detected a frozen Ashlar interaction of the size we committed
to caring about, so the observed null does not count against the theory.** Frozen and tagged before the run
(`papers-ucsc-power-frozen`, `PREREGISTRATION_POWER.md`). Adjudicator anchored to the frozen coupling shape at
tau = 0.01.

## The adjudicating number

> At the frozen +0.01 substantive threshold, the exact UCSC pipeline had **26 per cent** probability of
> detecting an injected interaction of the preregistered (frozen coupling) form.

Well below the ~80 to 90 per cent that the frozen decision table required to let the observed null (+0.0004)
count. By the pre committed rule, **UCSC is non adjudicative**: it contributes zero evidence, for or against.

## The three injected shapes (power at each injected effect size)

| injected tau | frozen coupling | sparse single axis | balanced dense |
|---|---|---|---|
| 0.000 | 0.00 | 0.00 | 0.00 |
| 0.005 | 0.06 | 0.00 | 0.00 |
| 0.008 | 0.13 | 0.00 | 0.02 |
| **0.010** | **0.26** | 0.01 | 0.05 |
| 0.015 | 0.66 | 0.03 | 0.26 |
| 0.020 | 0.87 | 0.05 | 0.31 |
| 0.030 | 0.99 | 0.17 | 0.73 |

The tau = 0 row returns zero power for every shape: the pipeline does not manufacture threshold crossings from
nothing. The frozen coupling form (the adjudicator) is the easiest of the three to detect and still needs a
true effect near 0.02 to reach acceptable power; the sparse and dense shapes are harder still.

## The two independent assay failures (both stand)

1. **The reference interaction does not reproduce in sample.** The paper's own Big Five by fact/feeling
   interaction, conventional OLS, incremental R squared 0.0013, F 0.57, **p = 0.73**, on the simple faithful
   baseline and the demanding one alike. Held out, delta -0.0034.
2. **The assay has only 26 per cent power at +0.01.**

These are distinct: not merely failing a hard modern predictive criterion, but also failing to recover the
literature interaction under a conventional analysis in the reconstructed dataset.

## The estimator finding (why this is not only a sample size problem)

The mean held out increment for a **true** 0.01 interaction is only **0.0075** (frozen coupling row). The out
of sample incremental R squared is a downward biased estimator of the population effect, by roughly a quarter
to a third at this structure. So the frozen +0.01 **held out absolute** threshold effectively demands a true
effect of about 0.013 to 0.015 before it is reliably met. This bias, not sample size alone, is why power sits
low at the substantive threshold, and it carries directly into the design of the fresh experiment
(`EXPERIMENT_POWER.md`).

## Classification (locked)

UCSC is an **insufficiently sensitive assay / non adjudicative dataset under the frozen evaluation** (not a
software failure: the tau = 0 floor proves the pipeline is correct; the limit is statistical power). It
contributes **zero positive evidence**: it neither counts against Ashlar nor for it. Effect side Ashlar
remains unresolved. **The hammer was not capable of breaking the theory; the experiment that could remains
outstanding.**

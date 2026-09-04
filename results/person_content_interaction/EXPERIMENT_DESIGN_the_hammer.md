# The hammer: a simulation first randomised experiment for effect side Ashlar

Detectability is designed in first; the corpus is not found and hoped over afterwards. UCSC's lasting
contribution was to define this spec: it showed that a superficially excellent existing corpus is
non adjudicative because it lacks the power to see a frozen Ashlar interaction at the substantive threshold.

## The experiment in one sentence

**Measure the person, randomise the message geometry, and test whether the frozen Ashlar score prospectively
predicts which person changes under which message.**

## Four essential ingredients

1. **Measured personality before exposure** (Big Five, mapped by the frozen DeYoung recipe to the DYNAMICS-8
   metatraits, unchanged from the corpus legs).
2. **Experimentally assigned message character**: several messages that preserve the same underlying factual
   proposition but deliberately occupy different frozen DYNAMICS coordinates, holding topic, factual claims,
   length band, readability band, source identity, formatting and evidence set as constant as possible. Four
   to six arms spanning the geometry enough to create real between message variance.
3. **A real outcome**, harder than "I liked it": pre belief to post belief, plus one behavioural endpoint
   (willingness to sign, choose, donate, share, or an incentivised choice).
4. **Enough independent participants** for the frozen Ashlar interaction to reach at least 80 to 90 per cent
   power at the substantive threshold. The number is decided by simulation, not by budget.

## Design shape

A multi message randomised trial with repeated propositions. Each participant sees several independently
randomised items but never two versions of the same proposition, giving many person by message observations
without pretending they are independent. Analysis clusters by participant and by item.

## Ashlar is used frozen, not refitted

No new person by content interaction matrix is estimated. For each participant and message the coupling score
is computed from the existing frozen operator (plasticity times originality plus stability times matter
manner) before outcomes are opened, and the test asks whether that preregistered scalar moderates treatment
response.

## The frozen decision table

- **Pass**: the frozen Ashlar interaction exceeds +0.01 incremental out of sample R squared, bootstrap lower
  bound above zero, permutation p below the locked threshold, and the effect direction matches prediction.
- **Weak / partial**: positive but below the substantive threshold.
- **Fail**: a powered assay returns a near zero or opposite interaction.
- **Non adjudicative**: a manipulation check fails, or prospective power falls below the locked sensitivity
  threshold.

## Two manipulation checks, required before the effect test is interpreted

1. Independent scorers confirm the treatment messages actually moved to their intended DYNAMICS coordinates.
2. The realised experiment retains enough between treatment geometric variance to keep the planned detection
   power valid.

## Severity: double independent

One team generates stimuli without seeing outcomes; a second scores DYNAMICS; the outcome analysis runs
against a locked preregistration; ideally the final analysis is independently reproduced.

## The first practical step (before spending a pound)

Simulate the exact planned design through the exact frozen pipeline and find the N that detects an injected
Ashlar shaped effect of delta R squared = 0.01 at 80, 90 and 95 per cent power. Keep raising N until the
criterion is met; that number is the minimum sample size. The simulation, not intuition, sets N, and N sets
the cost bracket. `cc_experiment_power_design.py` + `EXPERIMENT_POWER.md` carry that result.

# Preregistration: UCSC assay sensitivity (was the hammer capable of breaking the theory?)

**Frozen before the official run.** The UCSC person by content interaction came back near zero
(`RESULT_UCSC.md`, increment +0.0004), but the positive control (the paper's own Big Five by fact/feeling
interaction) also failed out of sample, so the corpus failed an assay sensitivity check. This diagnostic
decides whether that near zero is allowed to count against Ashlar, using logic fixed here before the number.

## The three steps and the decision logic

**A. Conventional in sample reproduction.** Fit the paper's reference interaction (Big Five by fact/feeling)
in sample by OLS, over two baselines: a simple one (Big Five, prior belief, style) faithful to the original,
and a demanding one that also controls our content axes. Report incremental R squared and the F test.
- If the reference does not reproduce even in sample on the simple baseline, the reconstruction or the content
  scoring is suspect and UCSC is unusable until that is resolved.

**B. The reference under the held out criterion.** The same reference interaction under the worker clustered
nested CV (already seen to vanish; recorded for completeness).

**C. Power injection through the exact pipeline (the adjudicator).** Inject a known population interaction of
size tau into the real UCSC design and worker structure, in three shapes so we do not prove sensitivity to an
easy synthetic effect the real hypothesis would not share:
- **frozen_coupling** = the preregistered form, plasticity times originality plus stability times matter
  manner. **This is the adjudicator.**
- **sparse_single_axis** = conscientiousness times affect (paper like).
- **balanced_dense** = a dense linear interaction across all person and content axes.
Run each injected outcome through the exact frozen detection pipeline (fit the DYNAMICS interaction block,
held out nested CV, worker clustered bootstrap) and estimate detection power at each tau, where detection is
the pre committed rule proxy: held out increment > 0.01 and bootstrap lower bound > 0.

## The adjudicating number and what it licenses (fixed now)

The one sentence: **"At the frozen +0.01 substantive threshold, the exact UCSC pipeline had X per cent
probability of detecting an injected interaction of the preregistered form."**

- If X is high (about 80 per cent or more) and the observed Ashlar increment is still +0.0004, the negative
  interpretation is **reinstated**: the assay could have seen an effect of the size we committed to caring
  about, and did not. The failed positive control no longer rescues it.
- If X is low, UCSC **cannot decide** the question: it is struck from the evidence column and classified as
  inconclusive due to assay sensitivity, neither positive nor negative, underpowered relative to the
  preregistered +0.01 threshold.

Whatever the number says, it is accepted.

# Result: person by content interaction leg 2 (UCSC Persuasion and Personality)

**Verdict: INCONCLUSIVE, not a negative.** The frozen person by content interaction adds nothing out of
sample here, but a positive control shows the analysis cannot detect the reference interaction either, so this
corpus does not, in this framework, constitute a test of the coupling. Frozen spec tagged
`papers-ucsc-interaction-frozen` before the run; same DeYoung person mapping and frozen content directions as
PSG. Fact/feeling experiment: 2,000 responses, 80 workers, 100 arguments, Big Five measured before exposure,
belief change after an assigned argument (Lukin et al., EACL 2017).

## The numbers (nested five fold, grouped by worker, incremental R squared)

| block | held out R squared |
|---|---|
| baseline (Big Five + prior belief + fact/feeling label + classical text) | +0.0549 |
| + embedding (nomic-embed-text, top PCs) | +0.0131 |
| + content (frozen eight axis character) | +0.0100 |
| + interaction (frozen person by content 2x2) | +0.0104 |

Interaction increment over baseline plus embedding plus content = **+0.0004, bootstrap CI [-0.0016, +0.0021],
permutation p = 0.14**. Below the pass mark.

## Why this is inconclusive rather than a negative

**Positive control: the paper's own found interaction, Big Five by fact/feeling label, increment = -0.0003,
permutation p = 0.45.** The original paper reported that conscientious, open and agreeable people are more
moved by emotional arguments, a personality by style interaction significant in sample. That same interaction
does not surface as out of sample incremental R squared in this pipeline. When the reference interaction
cannot be detected by the method, the method cannot be used to reject our own interaction either.

The reason is the bar, not the theory. Out of sample incremental R squared, clustered by worker across 80
workers, is a stringent test for a cross level interaction (a person level trait times an item level content
score). It is the same bar that the ArgQ and embedding contests passed cleanly, but those had 2,500 to 5,000
independent items; here there are 80 person clusters and the held out prediction is for unseen workers, which
discards much of the within person heterogeneity an interaction lives in. A coefficient can be real in sample
and still carry almost no out of sample incremental variance at this sample size.

A second limitation, stated plainly: the content was scored on this corpus by a different model from the one
that built the reference geometry (the atlas scorer was not serving; a 7B was used), so the content axes are
noisier here and the frozen direction was applied after within corpus standardisation. A weaker content
instrument attenuates any content signal, including the interaction. This alone would soften any negative
claim.

## What this does and does not license

It does **not** fire the pre committed decision rule ("if UCSC is null under random assignment, move the
probability on the large interpretation down"). That rule assumed UCSC was a real test of the interaction. The
positive control shows it is not, in this out of sample framework. So neither leg so far is evidence against
the coupling: PSG is a confounded association leg that came back null as registered, and UCSC cannot detect
the reference effect it was chosen for.

## What would make it a real test

Two routes, honestly separate from the preregistered held out analysis. First, an in sample mixed effects
replication that matches the original method (worker random effects, personality by content fixed effect),
reported as an in sample association, which would at least confirm our geometry recovers the paper's own
interaction before asking whether it predicts out of sample. Second, and better, a larger assigned corpus with
many more people, where out of sample interaction power exists. The Anthropic persuasion corpus has far more
participants (about 3,800) under assigned content, but no personality measure, so it can carry the content by
initial state version of the test, not the full person by content one. The search for an assigned corpus with
both many people and measured personality continues.

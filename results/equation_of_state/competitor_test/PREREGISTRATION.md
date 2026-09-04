# Competitor test: preregistration

*DYNAMICS-WEB series, 3 September 2026, written and committed BEFORE the run. Script
`truthometer/scripts/cc_competitor_test.py`. Operator instruction: "run the competitor test. I want
to see if we unify or not!"*

## The question

Does an assumption free, high capacity model find more structure in how disposition and room
produce character than the constrained architecture the series settled on, once both are judged on
persons neither has seen? If the flexible model wins clearly, the unified geometry is a story told
about a fit. If the constrained model matches it with a small fraction of the moving parts, that is
the evidence unification needs. A draw is a win for the constrained model.

## The fair fight

The constrained model is the UPDATED architecture, not the old straight line, same everywhere one
that today's within room tests already showed to be incomplete: a curved pooled disposition map, a
room specific slope deviation shrunk toward zero with the shrinkage chosen by inner cross validation
on training persons only, and a room state shift constrained to a rank two subspace across rooms.
Eight standardised character axes, so that rank two means something.

Against it: gradient boosted trees and a two layer perceptron, each given the disposition, its
squares and cross term, and a room profile built only from training persons (mean character, mean
disposition, log room size). Also on the sheet: the old invariant linear model, the invariant
curved model, the full rank state ablation, and the unshrunk per room model (the overfit pole).

## The design

Persons are assigned to five folds. A person sits in exactly one fold across every room, so no
person leakage. Every room appears in training and in test with different persons, so every model
can learn room parameters and the flexible models can learn any disposition by room interaction.
Test records in rooms with fewer than five training persons are dropped for every model alike.
Rooms need ten persons to enter.

## The criterion (fixed now)

gain(M) = 1 − SSE(M) / SSE(room mean), pooled over the eight axes, on held out persons.

Delta = gain(best flexible) − gain(updated architecture). Ninety five per cent interval by a room
block bootstrap over test rooms, 500 draws.

## Power calibration by injection

A per room disposition interaction (P1 × P2 with a random sign per room) of size 0.06 and 0.15 SD
of character is added and the whole comparison rerun. No constrained model can absorb it (the
pooled map has P1 × P2 but no room specific version; the deviation is linear in P). The flexible
model must show it: Delta at 0.06 must exceed Delta at 0 by at least 0.01, or the test is
UNINFORMATIVE and a draw proves nothing.

## The pass mark

| Outcome | Rule |
|---|---|
| PASS, unification holds | Delta ≤ 0.02 and the upper interval bound ≤ 0.04, on an informative test |
| FAIL, the flexible model finds structure we lack | Delta > 0.05 and the lower interval bound > 0.02 |
| UNEXPLAINED, not dismissed | anything between |
| UNINFORMATIVE | the injection at 0.06 is not detected |

Secondary, recorded whatever the primary says: the updated architecture must beat the old invariant
linear model held out (else curvature and rotation earn nothing out of sample); it must beat the
unshrunk per room model (else the shrinkage earns nothing); the rank two state is compared with the
full rank state (if full rank wins, the rank two collapse is decoration, not structure).

## Corpora

Run 1: `the internal cross site corpus`, room = domain, the corpus every prior test used. Run 2:
`the internal Reddit corpus`, room = subreddit, disposition from the 27B behavioural reader, the corpus on
which the rotation did not travel. The verdict is read on run 1; run 2 says whether it travels.

## What is and is not at risk

At risk: the unification framing and Paper 4's architecture story, both already hedged as "a
candidate unifying geometry". Not at risk: Papers 1, 2, 5, 6, 7 and the manipulation work, none of
which depend on unification.

---

## Amendment 1, written 3 September 2026 at 14:50 UK (git 85df3a7b2), after the first pass and before the corrected run

**What the first run returned.** Crosssite (the verdict corpus), no injection: Delta (perceptron minus the
preregistered model) = +0.083, interval [+0.076, +0.089]. That is a FAIL under the mark above and it stands:
a loss needs no power calibration. Reddit: Delta = +0.018 [+0.016, +0.020], inside the PASS band on its face.
The preregistered ablation located the crosssite failure: the rank two state constraint alone takes the model
from +0.065 (full rank) to +0.003; on reddit it costs +0.101 to +0.090. Unshrunk per room slopes beat both
invariant models on crosssite (+0.047 against +0.041 and +0.036), so the rotation is real there.

**The flaw in the power check, found by the power check.** The injected structure carried a random sign per
room, but the flexible models were given a room profile (mean character, mean disposition, size) and never
room identity, so two rooms with the same profile and opposite signs were indistinguishable to them. The
injection was invisible by construction; on reddit Delta at tau 0.06 moved from +0.0179 to +0.0170. The rule
above therefore reads UNINFORMATIVE for reddit, which is the right verdict for a check that could not see
its own plant. The first run's logs and JSON are kept as `crosssite_v1_blind_injection.json`,
`reddit_v1_blind_injection.json`, and the crosssite FAIL is read from them.

**The corrected run, and nothing else changes.** Two changes, both to make the plant visible:
1. the injected sign is now a function of the room profile (positive where the room's mean plasticity sits
   above the median, negative below), so the profile fed models can express it;
2. a further competitor M6, the same perceptron given room identity as a one hot block, so structure tied
   to the room itself is in reach of a flexible model.
The pass mark, the criterion, the folds, the seed, the corpora and the model under test are unchanged. The
best flexible model is now the best of M4, M5 and M6. Any verdict on reddit, and the size of the residual
crosssite gap in units of injected structure, are read from the corrected run.

---

## Amendment 2, written 3 September 2026 at 15:11 UK (git 7fcaf87cc), before any M6 result exists

**A second, pre specified test of the three part model.** The first test's verdict on the preregistered
model is settled (FAIL on crosssite) and is not reopened. This amendment declares a second test whose
subject is the model the ablation pointed to: the same architecture with the rank two state constraint
removed, that is a curved pooled map, a ridge shrunk room slope deviation, and an unconstrained room shift
(M2f in the script). Three named parts, no plane.

**What is already known when this is written, stated so nobody can pretend otherwise.** On crosssite,
M2f = +0.065 against the profile fed perceptron M5 = +0.085, a gap of 0.020, which sits exactly on the pass
boundary of the mark below. On reddit, M2f = +0.101 against M5 = +0.108, a gap of 0.006. What is NOT known
is what M6, the perceptron given room identity, will find; that is the unknown this test turns on, and the
corrected run is in flight with no M6 line yet reported on either corpus.

**The mark, unchanged from the first test.** Delta2 = gain(best of M4, M5, M6) − gain(M2f), read from the
corrected run (visible plant). PASS: Delta2 ≤ 0.02 and the upper interval bound ≤ 0.04, on an informative
test. FAIL: Delta2 > 0.05 and the lower interval bound > 0.02. Between: unexplained, not dismissed.
UNINFORMATIVE if the plant at 0.06 is not seen.

**What each outcome will be read as.** PASS: one geometry with three named parts is as good as an
unconstrained model on both corpora; the plane was the only wrong assumption. FAIL or between, driven by
M6: a fourth term exists and it is tied to room identity rather than to anything measured about the room
(profile, topic, language, size); its size is Delta2; the leading candidate, labelled a guess, is which
persons a room selects. In every outcome the shift and the bend stand on the tests already run, and the
rank two state stays withdrawn.

---

## Amendment 3, written 3 September 2026 at 19:05 UK, after the reddit tau = 0.06 line of the corrected run and before its tau = 0.15 line

**A unit error in the informativeness rule, corrected before the line it applies to.** The rule above asks
the injection at tau = 0.06 to lift Delta by at least 0.01. An injected term of size tau in standard
deviation units can add at most about tau squared to a gain measured as a share of variance: 0.0036 at
tau = 0.06, 0.0225 at tau = 0.15. The 0.01 threshold at tau = 0.06 was therefore unreachable by any model
and the rule as written could only ever return "uninformative". On the corrected reddit run the flexible
model's Delta rose by 0.0016 at tau = 0.06, which is 44 per cent of that ceiling, that is, the plant was
seen in proportion to its size.

**Rule as corrected.** The test is informative if, at tau = 0.15, Delta rises by at least half of the
ceiling, 0.011, that is if the flexible model captures at least half of an injected unmodelled term of
that size. The pass and fail marks, the criterion, the folds and the models are unchanged. The reddit
tau = 0.15 line had not been reported when this was written; the crosssite corrected run was in its
tau = 0.06 pass.

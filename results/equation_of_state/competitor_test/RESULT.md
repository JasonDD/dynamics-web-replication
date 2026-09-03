# Competitor test: does the unified architecture match a model with no assumptions?

*DYNAMICS-WEB series, 3 September 2026. Preregistration and its three amendments in `PREREGISTRATION.md`,
each committed before the line it governs. Script `truthometer/scripts/cc_competitor_test.py`. Held out
gain = 1 − SSE(model) / SSE(room mean) over the eight character axes, five person grouped folds, room
block bootstrap of 500 for every interval. Web domains: `cc_v3.crosssite_authorship`, 1,008 rooms,
161,867 person room records, 48,293 persons. Subreddits: `cc_v3.reddit_wide`, 400 rooms, 50,346
records, 47,514 persons. JSONs: `crosssite_v3.json`, `reddit_v3.json` (corrected run), `*_v4_tau0.json`
(the test 2 interval), `*_v1_blind_injection.json` (the first run, kept).*

## The table, corrected run, no injection

| Model | Subreddits | Web domains |
|---|---|---|
| room mean | 0 | 0 |
| invariant linear (the old architecture) | +0.091 | +0.036 |
| invariant curved | +0.099 | +0.041 |
| **preregistered: curved map, shrunk room bend, rank two state** | **+0.090** | **+0.003** |
| three part: the same without the plane (amendment 2) | +0.101 | +0.065 |
| unshrunk per room | +0.077 | +0.047 |
| gradient boosted trees | +0.066 | −0.009 |
| perceptron on disposition and room profile | +0.108 | +0.085 |
| perceptron with room identity (learned embedding) | **+0.109** | **+0.087** |

## Verdicts

**Test 1, the preregistered model.** Subreddits: Delta 0.019 [0.017, 0.022], PASS. Web domains: Delta
0.084 [0.078, 0.091] against a fail line of 0.05, **FAIL**. The preregistered ablation locates the whole
of the domain failure in the rank two state: removing it takes the model from 0.003 to 0.065. Effective
rank near two was a true description of the spread of the room shifts and a false licence to truncate to
it; the rank two state is withdrawn.

**Test 2, the three part model (pre specified before any room identity result existed).** Subreddits:
gap 0.008 [0.007, 0.010], PASS. Web domains: gap 0.021 [0.019, 0.024], which sits at the pass line and is read as
**unexplained, not dismissed**, per the rule.

**Power.** An injected term of size tau can add at most tau squared to a variance share, so the original
rule (a rise of 0.01 at tau 0.06) was unreachable and was corrected before the tau 0.15 lines (amendment
3): informative if the flexible lead rises by at least half the ceiling, 0.011, at tau 0.15. Subreddits:
rise 0.016, informative. Web domains: rise 0.013, informative.

**Room identity.** Giving the perceptron the room itself, through a learned embedding, adds 0.001 over
giving it the room's profile, on both corpora. Whatever the domain remainder is, it is not a term tied to
which room it is.

## What the first run got wrong, and how it is kept

The first run planted a random sign per room that the profile fed models could not see by construction;
the power check returned "not seen", which was the right verdict for a plant that was invisible, and the
run's tables are kept under `*_v1_blind_injection.json`. A sklearn one hot room model in the second
attempt was undertrained (0.066 on the subreddits against 0.108 for the profile model) and stalled on the
domains; it was replaced by the embedding model. None of this touched the model under test, the folds, the
seed or the marks.

## Reading, in one paragraph

One geometry with three named parts, a curved map from disposition to character, a shift belonging to
the room and a bend belonging to the room, matches an unconstrained model on the subreddits and sits at
the pass boundary on the web domains. The preregistered version of that geometry, which also forced the
room shifts into a plane, failed on the domains and the failure is entirely that constraint. The remainder
on the domains, about two points against an unconstrained model, is not room identity; the selection
tests in `../selection_vs_treatment/` find both a small room treatment beyond shift and bend and a small
homophily on the state tail on the domains and neither on the subreddits, so the remainder is real,
small, and still without a name.

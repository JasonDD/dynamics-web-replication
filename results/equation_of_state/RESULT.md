# Equation of state, first per state variable identification run

*The first pass of the equation of state programme: for each state variable we can label, does it enter the disposition to character coupling as a LOCATION (an affine offset, the coupling invariant), a ROTATION (it modulates the slope, a genuine interaction), contribute nothing, or leave residual structure. Extends the genre result (cc_genre_state_fit.py, genre = location) to the other Five Ws. Script: `truthometer/scripts/cc_state_fit_multi.py`. Substrate: cc_v3.crosssite_authorship, internal hold, analysis only, no scoring.*

## Method

For each state variable S, three models compared by held out RMSE, character in z units:

- **Null**: C ~ P                       (coupling only)
- **B (location)**: C ~ P + fixed effects of S    (S shifts the level, affine)
- **A (rotation)**: C ~ P + S + disposition by S interaction   (S modulates the coupling)

C is the matter versus manner PC1 (canonical ruler). P is the person mean plasticity (DeYoung Big Two, sociability plus novelty), computed per person so the disposition read is not taken from the identical text as the character. The cross validation is **person grouped**: every one of a person's rows shares a fold (assigned by hashing the identifier), so no person leaks between train and test, which matters because disposition is a person level quantity. Each kept state group must span at least four of the five folds. A state term is read as location when B beats Null and A does not beat B, as rotation when A beats B beats Null, and as absorbed when none separates, at a held out RMSE threshold of 0.002.

## Result (492,246 posts, 45,158 persons)

| State variable | n | groups | Null | B location | A rotation | verdict |
|---|---|---|---|---|---|---|
| WHERE, site kind | 482,739 | 72 | 0.9976 | 0.9758 | 0.9759 | LOCATION |
| language | 468,536 | 45 | 0.9879 | 0.9607 | 0.9589 | LOCATION |
| WHEN, era (five year) | 13,286 | 4 | 0.9568 | 0.9549 | 0.9584 | absorbed (underpowered) |
| genre (prior, separate script) | | | | | | LOCATION |
| WHAT, topic | | | | | | not testable (column too sparse) |

## Reading

**Every state variable with a detectable contribution enters as a location, and none rotates the coupling.** Site kind and language both shift the character level while the disposition to character slope stays invariant, which is the genre result reproduced on two further independent state variables. Language shows a whisper of possible rotation (A beats B by 0.0018, just under the threshold), the same faint modulation genre showed on the heavier model, watched but not claimed. Era shows no contribution, but with only four buckets and 13,286 rows it is genuinely underpowered on this time narrow corpus, so it is a weak null rather than evidence that when is absorbed.

The affine form `g(P) + sum over w of h_w(S)` is therefore generalising beyond the one term: it holds for genre, site kind and language. That is direct evidence for the additive, writable equation of state on more than one state variable.

## The honest magnitude, and where the closure test does not belong

The absolute numbers matter. Null RMSE is about 0.99 in z units, so the person level coupling explains about half a per cent of the variance, and disposition plus all the location terms together reach about five per cent. The residual is about ninety five per cent. This is the per post individual regime, where most of the variance is the irreducible within person within state spread (the Fleeson floor, about half of disposition is performed room) plus per post scorer noise. It is a far harsher signal to noise regime than the community aggregate level, where the same coupling reaches about 0.74.

So this run classifies the functional form of each term, which is what it was built to do, but it is the wrong level to ask whether the state vector closes, because the residual is dominated by the irreducible floor by construction. The closure test, residual against the sum of the Fleeson within person variance and the cross model measurement noise, belongs at the aggregate level where the coupling is strong.

## What this establishes, and what is next

- Establishes: the affine location form generalises across genre, site kind and language; no rotation detected on any tested state variable; the leak free person grouped cross validation at 45,158 persons makes the consistency a real signal.
- Next: run the closure test at the community aggregate level (residual against the independently measured floor); label who (audience) and a cleaner when on richer substrates; fold the multi term affine result into Paper 4 alongside the genre term.

## Bounds

Per post individual regime, weak coupling, so power to detect a rotation on top of a small location effect is limited; a null on rotation is not proof of strict invariance, only its absence at this power. Topic and a clean audience label are not available on this corpus. Single scorer lineage for the character read here; the cross lineage guard is owed on the terms that survive.

## Closure probe (first pass, and what it teaches)

The identification run above answers what form the state terms take. Closure is a separate question at a coarser level: after removing the identified terms, does the systematic residual reach the independently estimated floor? Script: `truthometer/scripts/cc_state_closure.py`. On the community aggregate reddit regime (394 communities, disjoint halves), fitting C = g(P) + genre and comparing the between community residual variance to the sampling floor (each community's own within variance divided by its post count):

| quantity | value (z units) |
|---|---|
| between community variance of C | 1.0025 |
| residual after g(P) | 0.8971 (disposition explains 10.5 per cent) |
| residual after g(P) plus genre | 0.7604 (genre adds 13.6 per cent) |
| independently estimated sampling floor | 0.0980 |
| **closure ratio, residual over floor** | **7.8, OPEN** |

The solid result: the floor is independently estimable, so closure is a real numerical test, and the residual after disposition and genre sits about eight times above it, so the remaining between community variance is systematic structure and not sampling noise.

The honest caveat that this probe teaches: the coupling used here is weak (the plasticity metatrait alone captures only about a tenth of the between community variance, well below the roughly 0.74 the stronger construction reaches), and only genre was removed, not site, language or the community norm term. So the large residual conflates genuinely missing state terms with an under captured person coupling, which cannot be separated at this power. The definitive closure test therefore needs the strongest possible g(P) and every identified location term removed, at which point a residual above the floor cleanly means a missing state variable rather than an under fit person side. The value of this probe is that it makes the floor measurable and specifies that clean experiment, not that it settles closure.

## The effective rank of the state displacement (does S have to close in count?)

The count of nameable state variables may be open, since a genuinely new communicative environment can always add a label. But the count is the wrong question. The question that decides whether the equation of state is finite is the effective rank of the state displacement: do the location offsets of the different state variables live in a low dimensional subspace of character space, or do they spread across it. Script: `truthometer/scripts/cc_state_rank.py`. For each state variable, each group has a mean 8 axis character; centred within the variable these are its location offsets. Stacking the offsets of genre, site and language and taking the singular value spectrum:

| state variable | offsets | effective rank | top axis | top two axes | leading axis versus matter/manner |
|---|---|---|---|---|---|
| genre | 14 | 2.61 | 54 per cent | 83 per cent | 0.57 |
| site kind | 73 | 1.97 | 69 per cent | 83 per cent | 0.64 |
| language | 47 | 2.05 | 68 per cent | 80 per cent | 0.64 |
| combined | 134 | 2.06 | 68 per cent | 82 per cent | 0.64 |

Leading direction cosines: site and language 0.98, genre and site 0.45, genre and language 0.34.

The state displacement is low rank. Across three independent state variables the combined offsets have an effective rank of about two: one axis carries 68 per cent of the displacement and two carry 82 per cent. Site kind and language push character in essentially the same direction (cosine 0.98), a single shared axis; genre carries a second, related but distinct direction, which is why the rank is two rather than one. The primary axis is mostly, though not purely, matter versus manner (cosine 0.64).

The consequence is the answer to whether the state vector must close in count: it need not. The number of state labels may keep growing, but so far every one of them displaces the character field within a subspace of effective rank about two. The equation of state is finite in its effect regardless of how many labels the state turns out to have. The test to carry forward as who, when and topic are added is simply whether the effective rank holds near two or climbs; if it holds while the label list grows, the result is a finite equation of state over an open label set, which is a stronger statement than a closed five variable list would have been.

Bounds: three state variables so far, so the rank could climb as more are added; the rank is about two rather than one, so there is a real second state axis and an eighteen per cent tail beyond it; and the primary axis aligns with matter versus manner only moderately (0.64), so it is that plane approximately, not exactly.

## The who term (audience), a first attempt and an honest null

The audience of a reply is the author of the parent comment, so on the reddit corpus each reply carries the writer's disposition, the audience's disposition (the parent author's), and the produced character. Script: `truthometer/scripts/cc_state_who.py`. Testing whether audience enters as a location or a rotation, with person grouped cross validation by the writer:

The join covers only about a tenth of comments, 8,082 replies whose parent comment is itself in the table, and on those the held out RMSE moves from 0.9872 with the writer coupling alone to 0.9859 adding audience as a location and the same adding the interaction. That is a change of about one thousandth, below the threshold, so the verdict is no detectable contribution. This is not evidence that audience does not matter; it is an underpowered null, on a tenth of the data in the per post regime where the coupling is already weak, and it sits with era rather than with the resolved location terms. Importantly the interaction term does not help either, so there is still no rotation detected on any state variable tested.

The clean test of the who term is a corpus where every message has an explicit recipient, so the audience join is complete rather than a tenth: the Enron email corpus is the obvious candidate, and it would give the audience term the power the reddit parent join cannot. This attempt establishes the method and the honest current status, not the answer.

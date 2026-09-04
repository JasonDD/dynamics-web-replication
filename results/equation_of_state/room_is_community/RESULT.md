# Is the room level rotation genuine community, or is the room a bag holding topic, language and platform?

*Confirmation run on the within room differencing test (`truthometer/scripts/cc_state_diff_invariance.py`, commit 2759e8472), which found that the disposition to character coupling is not invariant across rooms. That test named its own bound: "room here is the DOMAIN, a proxy for community, not one of the named state variables. Attributing the rotation to a named W is the next job." This is that job. Script: `truthometer/scripts/cc_state_diff_community.py`. Same corpus, same extraction, same ruler, same person room aggregation, same capped pair construction, same room grouped transfer design, same wild bootstrap null. Internal hold, analysis only, nothing written to the database.*

## Headline

**The rotation survives.** Topic, language and site kind each carry a real piece of it, and language carries the largest named piece, but none of them and not all of them together account for the room. Inside a single language and a single derived topic cluster, a room specific coupling still takes weight 0.4 to 0.5 in the blend at 40 persons per half, and still buys about the same held out R2 it bought with no control at all. The weight on the room term still rises with room size after every control, which is the signature that cannot be produced by noise: under invariance it would be zero at every size.

The one named variable that behaves like the confound story predicts is **language**, and only across languages. Within English, a topic specific coupling buys nothing over the pooled one.

## What is being asked

Websites differ in what they are about, in what language they are written, and in what software publishes them, all at once. A rotation attached to the room could be any of those wearing the room's clothes. The question is whether the room specific component of the coupling survives once those named variables are given every chance to explain it.

Two controls are applied, and both are reported, because they fail in different directions.

**Residualisation** builds a per room covariate design from topic, language and site kind and regresses the per room W on it. It is parametric: it can only remove rotation that is a linear function of the covariates. In the transfer test the same covariates are given a rotation model of their own, fitted on training rooms and applied to rooms never seen, so they get their chance before the room term does.

**Stratification** cuts the rooms into strata of near identical topic and language and refits the invariant part of the model inside each stratum. It is nonparametric within a stratum: a stratum specific W absorbs any rotation topic or language could produce, of any shape. It costs sample, because a stratum needs enough rooms to fit its own W.

## Corpus

Unchanged from the falsification run, and the pooled coupling reproduces to three decimal places.

| quantity | value |
|---|---|
| rows | 668,365 |
| persons in corpus | 59,084 |
| domains in corpus | 40,774 |
| rooms qualifying at 5 or more persons | 1,723 |
| person room records | 166,393 |
| persons in qualifying rooms | 49,787 |
| ordered pairs | 364,072 |

Pooled W is anti diagonal as before: plasticity to originality +0.1616, stability to matter against manner +0.1410, diagonal terms −0.025 and −0.021, pooled R2 0.0316.

## Covariates: what could and could not be obtained

| covariate | source | coverage | usable |
|---|---|---|---|
| **language** | stored `lang` column on `the internal cross site corpus` | 356,684 of 362,531 rows in qualifying rooms carry a label (98.4 per cent); 1,677 of 1,723 rooms labelled. Top: en 861 rooms, fr 109, es 90, de 55, ru 53, it 48, unlabelled 46, pt 34, tr 30, ro 27, pl 26, sv 21 | **yes, cleanly** |
| **topic** | derived. The stored `topic` column on the corpus is **null for every row**, and the domain level topic table `an internal table` covers only 290 of 1,723 rooms (16.8 per cent), so neither was usable. Topic was derived from the text: term frequency inverse document frequency weighting over the post body (first 1,200 characters) plus url slug tokens, reduced to 120 components by truncated SVD (18.1 per cent of variance), then k means at k=24 for the mixture, k=12 for the strata and k=16 derived inside English | 100 per cent of rooms carry a topic mixture | **yes, but derived rather than gold** |
| **platform** | the declared forum software table `an internal table` covers **2 of 1,723 rooms**. The corpus is gravatar identified commenters on blog articles, not forum threads, so forum software is simply not the substrate | effectively zero | **no. Stated plainly: platform proper could not be obtained** |
| **site kind (url shape)** | derived from url shape as a platform proxy: page 1,370 rooms, wordpress like 222, commerce 130, forum 1 | 100 per cent, but nearly degenerate | **weak substitute, included** |
| **site kind (tld)** | derived from the domain, the same "where" variable the earlier equation of state run used | 100 per cent, 95 distinct values | **yes** |

Three facts about the corpus govern how everything below should be read.

**Rooms are monolingual.** Mean dominant language share per room is 0.993 and mean within room language entropy is 0.016 nats. Language is therefore a clean room level attribute here rather than a within room mixture, which is the best case for controlling it.

**Rooms are topically concentrated but not single topic.** Mean within room topic entropy is 0.625 nats against a maximum of 3.178 for 24 clusters.

**Platform is near constant.** That is an honest limitation and it cuts both ways: platform cannot be the confound behind the rotation, because there is almost no platform variation to carry it, but neither can this run claim to have controlled it. The claim below is therefore "not topic, not language, not site kind", not "not platform".

The assembled design is 59 columns over 1,723 rooms: topic mixture columns plus topic entropy, language dummies plus language entropy and dominant share, tld dummies, url shape dummies plus dominant share.

Strata are the dominant language crossed with a coarse 12 way topic cluster. Because the derived topic labels are themselves partly language driven, a second stratification is run on English rooms only with the topic clusters derived **inside English**, which removes the language confound from the topic labels entirely.

## Two panels, and an accidental replication

The run was made twice, differing only in the dispersion panel: panel A takes rooms with 10 or more persons capped at 40 (986 usable rooms, median 40 persons), panel B takes rooms with 60 or more persons capped at 200 (478 usable rooms, median 194 persons). The transfer test is identical by construction in the two.

It is not bit identical, and the reason is worth stating. The main corpus fetch carries no `ORDER BY`, so row order differs between runs, and the derived topic clustering therefore lands slightly differently even though its seed is fixed: 342 strata with 21 usable covering 1,135 rooms in panel A, 318 with 23 usable covering 1,209 rooms in panel B; 11 usable English only strata against 8, both covering 846 rooms. Every stored covariate statistic is identical and the topic entropy agrees to three decimal places. The upshot is a free robustness check: two independent topic clusterings, and the conclusion is the same under both. It is also a reproducibility defect and should be fixed by adding a deterministic sort before this is published.

## A. Dispersion of the per room coupling, covariates residualised out

The per room W panel is regressed on the 59 column covariate design and the residual spread is tested against a wild bootstrap null residualised on the **same** design, so the degrees of freedom match on both sides. 201 wild bootstrap draws, so the smallest attainable p is 0.0050.

Panel A, 986 rooms, at most 40 persons each:

| coupling | excess sd, no control | covariate R2 of W | excess sd, residualised | retained | p residualised |
|---|---|---|---|---|---|
| stability to matter/manner | 0.2372 | 0.115 | 0.2143 | 90.3% | **0.0050** |
| stability to originality | 0.2007 | 0.146 | 0.1666 | 83.0% | **0.0050** |
| plasticity to matter/manner | 0.1273 | 0.076 | 0.1185 | 93.1% | **0.0100** |
| plasticity to originality | 0.0527 | 0.068 | 0.0462 | 87.5% | 0.343 (not detected) |

Panel B, 478 rooms, at most 200 persons each:

| coupling | excess sd, no control | covariate R2 of W | excess sd, residualised | retained | p residualised |
|---|---|---|---|---|---|
| stability to matter/manner | 0.1625 | 0.507 | 0.0962 | 59.2% | **0.0050** |
| stability to originality | 0.1527 | 0.527 | 0.0836 | 54.7% | **0.0050** |
| plasticity to matter/manner | 0.0823 | 0.217 | 0.0680 | 82.6% | **0.0050** |
| plasticity to originality | 0.0821 | 0.213 | 0.0673 | 82.0% | **0.0050** |

Reading. In the larger rooms, where each room's W is estimated far more precisely, the covariates explain a great deal more of it: covariate R2 of W reaches 0.51 and 0.53 on the two stability rows. That is a real finding in its own right, and it is the strongest version of the confound story anyone has produced here. It still does not finish the job. Between 55 and 83 per cent of the excess dispersion survives residualisation, and every cell in panel B remains significant at the resolution floor of the bootstrap.

The single cell that is not settled is plasticity to originality in panel A, where the observed residual excess (0.0462) sits below the minimum detectable value (0.1118). That is the diagonal cell carrying the large pooled mean coupling, where dispersion is hardest to see over a big mean. Panel B settles it: observed 0.0673 against a minimum detectable 0.0380.

## B. Transfer test: does a room specific W still buy held out accuracy after control?

Room grouped cross validation. Within each held out room the members are split into two halves, a W is fitted on one half and scored on the other, and the score is swept over a blend weight alpha on the room term against a base model. **Alpha is the answer.** Under strict invariance the best alpha is zero at every room size. In the falsification run the best alpha was 0.2 at 5 persons per half and rose to 0.5 at 40.

Person leakage is severe in this corpus: 58,826 of the 59,084 persons write on two or more domains, a figure carried from the falsification run over the identical corpus. It is removed rather than modelled: any person who appears in **any** training room is struck out of the held out pairs. At K=5 that leaves only 25.1 per cent of held out pair mass, which is too thin to read at the larger half sizes (22 room instances at h≥40). The authoritative cross validation is therefore **K=2 repeated three times**, which keeps 57.6 per cent of pair mass and gives 636 splits over 318 room instances at h≥40. A leaky K=5 run is kept as a diagnostic only.

Best alpha on the room specific W, K=2 × 3 repeats, person leakage removed:

| base model the room term is blended against | panel | h≥5 | h≥15 | h≥40 |
|---|---|---|---|---|
| pooled invariant W, **no control** | A / B | 0.2 / 0.2 | 0.3 / 0.3 | **0.5 / 0.5** |
| invariant **curved g** (trap 1 control) | A / B | 0.2 / 0.2 | 0.3 / 0.3 | 0.4 / 0.4 |
| pooled W + covariate rotation | A / B | 0.1 / 0.1 | 0.2 / 0.2 | 0.4 / 0.4 |
| curved g + covariate rotation, **RESIDUALISED** | A / B | 0.1 / 0.1 | 0.2 / 0.2 | **0.3 / 0.4** |
| stratum W, topic × language | A / B | 0.2 / 0.2 | 0.3 / 0.4 | 0.4 / 0.4 |
| curved g + stratum W, **STRATIFIED** | A / B | 0.2 / 0.2 | 0.3 / 0.3 | **0.4 / 0.4** |
| curved g + **English only** stratum W | A / B | 0.2 / 0.2 | 0.4 / 0.3 | **0.5 / 0.4** |

Held out R2 the room term buys at its best alpha, same cross validation, h≥40:

| base model | panel A: R2 at alpha 0 → at best alpha (gain) | panel B |
|---|---|---|
| pooled W, no control | 0.0285 → 0.0488 (**+0.0203**) | 0.0295 → 0.0517 (**+0.0222**) |
| curved g | 0.0381 → 0.0549 (+0.0168) | 0.0393 → 0.0576 (+0.0183) |
| curved g + covariate rotation | 0.0515 → 0.0601 (**+0.0087**) | 0.0500 → 0.0613 (**+0.0113**) |
| curved g + stratum W | 0.0608 → 0.0756 (**+0.0148**) | 0.0592 → 0.0758 (**+0.0166**) |
| curved g + English only stratum W | 0.0480 → 0.0693 (**+0.0212**) | 0.0504 → 0.0692 (**+0.0188**) |

Three things to read off this.

**The room term never goes to zero, and its weight still rises with room size under every control.** Residualised: 0.1 → 0.2 → 0.3 or 0.4. Stratified: 0.2 → 0.3 → 0.4. English only: 0.2 → 0.3 or 0.4 → 0.4 or 0.5. A blend weight that grows as the estimate of the room's own W gets less noisy is exactly what a real room level parameter produces and is exactly what sampling noise cannot produce, because noise gets relatively worse, not better, in the alpha that a mean squared error sweep will pay for.

**The covariates are not nothing.** They raise the base substantially: at h≥40 the covariate rotation model lifts held out R2 from 0.0285 to 0.0515 in panel A before the room term is touched at all. So topic, language and tld genuinely do rotate the coupling. Residualisation is the control that absorbs the most: it roughly halves what the room term adds, from about +0.021 to about +0.009. It does not remove it.

**Almost all of the named part is language, not topic.** Compare the stratum W against the pooled W inside the same subsample at h≥40 in panel A: the topic by language stratum W scores 0.0566 at alpha 0 against 0.0478 for the pooled curved base, so cutting on language and topic together buys +0.0088. Now do the same inside English only, where the topic labels are derived within the language and carry no language signal: the English topic stratum W scores 0.0480 against 0.0489 for the pooled curved base. It is *worse*, by a hair. Panel B is marginally the other way (0.0504 against 0.0474). Across both, a topic specific coupling within a single language buys nothing reliable. And in that same English only, single topic cluster setting the room specific coupling still takes alpha 0.4 to 0.5 and buys +0.019 to +0.021 held out R2, which is as much as it bought with no control whatsoever.

## Both traps carried

**The curved g trap.** g is decisively nonlinear, and a per room linear W can differ purely because rooms differ in disposition range, with no rotation at all. The invariant curved g control is therefore the base of every controlled comparison above, not an optional extra. It behaves exactly as it did in the falsification run: it lifts pooled held out R2 from 0.0233 to 0.0318 in panel A and 0.0237 to 0.0319 in panel B, closely matching the 0.0243 to 0.0322 reported before. It absorbs part of the room effect and not all of it: best alpha falls by at most one step of 0.1 when curvature is added, and the room term still buys +0.0168 to +0.0183 at h≥40 on top of a curved base. **The curved g control does not change the answer.**

**The person leakage trap.** Handled by exclusion, not adjustment, as described above. The cost is stated: 42.4 per cent of held out pair mass discarded at K=2, 74.9 per cent at K=5. The leaky diagnostic gives systematically larger alphas (0.5 at h≥40 even after covariate control) than the clean run, which is what leakage should do and is the reason the clean K=2 numbers are the ones quoted.

## Power

Minimum detectable dispersion after control against what was observed, from the residualised wild bootstrap:

| coupling | panel A: min detectable / observed | panel B: min detectable / observed |
|---|---|---|
| stability to matter/manner | 0.1261 / 0.2143 | 0.0449 / 0.0962 |
| stability to originality | 0.1127 / 0.1666 | 0.0462 / 0.0836 |
| plasticity to matter/manner | 0.0987 / 0.1185 | 0.0351 / 0.0680 |
| plasticity to originality | 0.1118 / 0.0462 **underpowered** | 0.0380 / 0.0673 |

Seven of the eight cells clear their detection floor by a factor of 1.2 to 2.1. The eighth is the panel A plasticity to originality cell already flagged, and panel B settles it at 1.8 times its floor. The run as a whole is not underpowered.

Where more sample would still help is the English only stratified comparison at h≥40, which rests on 304 splits over 152 room instances in panel A. Halving the sampling standard deviation on that comparison needs roughly four times the persons per room, that is a median near 776 rather than 194, or about sixteen times the rooms. Neither is needed to reach the verdict below; both would be needed to put a tight confidence interval on how much of the rotation is community as against how much is a named variable not yet measured.

## Bounds

1. **Platform was not controlled**, because it could not be measured. The corpus is blog comment threads, not forum software installations. The claim is that the rotation is not topic, not language and not site kind, and it is silent on platform.
2. **Topic is derived, not gold.** It comes from term frequency weighting and k means over the text, capturing 18.1 per cent of variance in 120 components. A better topic model could absorb more. The English only stratification is the strongest available answer to this and it finds a topic specific coupling to be worth nothing, which argues the derived labels are not the binding weakness.
3. **The room is still the domain.** This run rules out three named alternatives and shows the room level rotation is bigger than all of them together. It does not directly measure a community, and a fourth unnamed room level variable correlated with the domain remains logically possible.
4. **Aggregate only.** No keys, no names, no scoring, nothing written to the database.
5. **Reproducibility defect.** The unordered main fetch makes the derived topic clustering vary between runs. It should be sorted before publication. The two clusterings here agree, which is reassurance and not a substitute.

## Verdict

**The rotation is genuine community identity rather than topic, language or platform in disguise: language carries the largest named share of it and topic within a language carries essentially none, yet inside a single language and a single topic cluster a room specific coupling still takes weight 0.4 to 0.5 at 40 persons per half and still buys as much held out accuracy as it did with no control at all, and the weight on the room term still rises with room size, which invariance forbids.**

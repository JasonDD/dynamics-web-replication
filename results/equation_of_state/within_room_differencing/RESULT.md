# Within room differencing: does the coupling survive as invariant?

*The Paper 4 closure experiment. Every earlier equation of state run fitted LEVELS, so the state term h(S) had to be estimated and could quietly absorb error. Differencing removes h. For two persons i and j writing in the SAME room the room offset cancels exactly, so C_i − C_j = g(P_i) − g(P_j), and for a linear g that is dC = W dP with no intercept and W constant across rooms. This run tests that by transfer: fit W on training rooms, predict dC in rooms never seen in training. Script: `truthometer/scripts/cc_state_diff_invariance.py`. Substrate: cc_v3.crosssite_authorship, the same leak free cross site corpus and the same person, disposition and character extraction as `cc_state_fit_multi.py`. Internal hold, analysis only, no scoring.*

## Headline

**The coupling does not survive as invariant. It shows a rotation, and it shows curvature, and both survive out of sample with person leakage removed. The test was not underpowered: it detected both.**

Alongside that, a correction to the earlier level runs that matters more than the invariance question itself: **most of what the level fits measured as a person coupling was between rooms, not within one.** The specific slope Paper 4 leaned on, plasticity to matter against manner, is essentially zero once you difference inside a room.

## Design

Room is the site (domain). Each person is aggregated within each room, giving 214,004 person room records. Rooms are kept when they hold at least 5 distinct persons. Disposition P is the DeYoung Big Two read off DYNAMICS 8 (plasticity = novelty + sociability, stability = discipline + yielding − mercuriality). Character C is the canonical matter against manner ruler (PC1 of the 8 axes over 2,648,406 rows of cc_v3.domain_char8_expanded) plus originality. Both P and C are standardised over person room records, so W is in z units.

Within each room, unordered person pairs are formed, sampled at a cap of 200 per room where the room is larger, and **both orderings of every pair are kept**, so the intercept is zero by construction. W is fitted with no intercept, pooled across rooms. Uncertainty comes from a room block bootstrap of 400 draws.

| quantity | value |
|---|---|
| usable rows | 668,365 |
| persons, all | 59,084 |
| domains, all | 40,774 |
| person room records, all | 214,004 (mean 3.12 rows each) |
| rooms with at least 5 persons | 1,723 |
| person room records kept | 166,393 |
| distinct persons kept | 49,787 |
| unordered within room pairs | 182,036 |
| ordered pairs fitted | 364,072 |

PC1 loadings: rigour +0.44, depth +0.40, candour +0.39, stance +0.37, originality +0.23, commercial drive −0.26, register −0.34, affect −0.35.

## The pooled W

| | to matter against manner | to originality |
|---|---|---|
| plasticity | **−0.0233** (se 0.0063, 95% CI −0.0349 to −0.0122) | **+0.1637** (se 0.0052, CI +0.1537 to +0.1731) |
| stability | **+0.1459** (se 0.0075, CI +0.1330 to +0.1608) | **−0.0166** (se 0.0077, CI −0.0320 to −0.0009) |

In sample RMSE 1.0440, R2 0.0328. The exact room centred fit over every person with no pair cap gives [[−0.0389, +0.1751], [+0.1452, −0.0263]], so the pair sampling is not doing any work.

**The coupling that survives differencing is entirely off diagonal.** Plasticity drives originality, stability drives matter against manner, and each metatrait has no reliable effect on the other axis. The plasticity to matter against manner slope, which is the one the earlier level runs used, is −0.023, and fitted on its own as a scalar it is −0.040. That is the coupling Paper 4 rested on, and inside a room it is gone.

## The checks the algebra demands

**Intercept.** With both orderings kept the intercept is exactly zero by construction (1.0e−18, 3.7e−19). The real check is a single arbitrary ordering, where nothing forces it: −2.3e−4 (se 2.3e−3) and +4.1e−5 (se 2.6e−3). Both are indistinguishable from zero, so the pairing is right and the differencing did what it was meant to do.

**Shuffle null.** Permuting P across persons within each room, leaving character in place, collapses the fit to W = [[+0.0015, +0.0033], [+0.0057, +0.0005]] and R2 = 0.0000, against 0.0328 for the real data. The signal is in the pairing, not in the construction.

**Circularity.** P and C are read from the same text, which could manufacture a coupling. Re fitting with P taken **only from the person's other rooms** (163,582 records in 1,503 rooms) gives [[−0.0356, +0.1142], [+0.1183, −0.0053]]. The off diagonal coupling shrinks by about 30 per cent but survives clearly, so it is not a shared text artefact.

## What the level fits were actually measuring

| slope | plasticity to matter/manner | plasticity to originality | stability to matter/manner | stability to originality |
|---|---|---|---|---|
| naive level, no room term | −0.0232 | +0.2223 | +0.3668 | +0.1994 |
| between rooms (room means) | +0.1150 | +0.5723 | **+0.8695** | **+0.7484** |
| **within room (this test)** | **−0.0233** | **+0.1637** | **+0.1459** | **−0.0166** |

The between room slope for stability to matter against manner is +0.87 against +0.15 within, a factor of six. For stability to originality it is +0.75 between against −0.02 within, and the sign flips. **The level fitted coupling was mostly room composition.** That is precisely the error differencing was built to expose, and it was there.

## The invariance test, by transfer

Rooms are grouped into folds. W is fitted on training rooms and used to predict pairs in held out rooms. **Person leakage** is the trap here and it is severe on this corpus: 58,826 of 59,084 persons write on two or more domains, so most persons straddle any room split. Persons appearing in any training room are dropped from the held out rooms entirely. The cost is stated below as the fraction of held out pair mass that survives.

| design | held out pair mass kept | held out ordered pairs | pooled linear W, R2 | invariant but nonlinear g, R2 |
|---|---|---|---|---|
| K=5, person leakage left in (diagnostic only) | 100.0 per cent | 364,028 | 0.0313 | 0.0367 |
| K=5, leakage removed | 25.1 per cent | 92,624 | 0.0205 | 0.0323 |
| K=2 (50/50 rooms) by 5 repeats, leakage removed | 57.5 per cent | 1,048,082 | 0.0243 | 0.0322 |

A single pooled W does transfer to rooms it has never seen. The question is whether letting it vary per room buys anything, and that needs a fair fight: a room specific W must be fitted on one half of a held out room's persons and judged on the other half, exactly as the pooled W is judged. Room sizes are swept, because a room specific W fitted on 5 persons is unestimable whatever the truth is.

Best powered comparison, K=2 by 5 repeats with leakage removed, held out halves of at least 40 persons (1,070 splits, 428,000 pairs), all R2 on the same held out pairs:

| model | held out R2 |
|---|---|
| room specific W alone | 0.0199 |
| pooled linear invariant W | 0.0284 |
| best blend of pooled linear and room specific (weight 0.4 to 0.5 on the room) | **0.0468** |
| invariant but **nonlinear** g, no room specific parameters at all | 0.0370 |
| best blend of the curved invariant g and a room specific W (weight 0.4) | **0.0530** |

Two things fall out, and they point the same way.

**A room specific W alone is always worse than the pooled one.** At every room size tested, fitting a coupling per room and using it out of sample loses to the single global W. So there is no naive reading in which the coupling is simply room specific.

**But a shrunk mixture of the two beats either.** The blend curve peaks well away from zero, and the peak moves outward as rooms get bigger: weight 0.2 on the room term for halves of at least 5 persons, 0.3 at 15, 0.4 to 0.5 at 40. That is the signature of a real room specific component being progressively better estimated. If the coupling were truly invariant the optimum would sit at zero at every room size, and it does not.

## Rotation or curvature? The trap in the trap

Differencing removes h(S) only. It does **not** linearise g. If g is curved, then dC depends on where the pair sits as well as on how far apart it is, and a linear W fitted separately inside each room will differ between rooms whose disposition ranges differ, with no rotation present at all. Read carelessly, curvature in g looks exactly like a state dependent coupling.

Adding the pair level to the model, dC = W dP + V (dP by centred mean P), separates them. It is antisymmetric in the pair, so it leaves the no intercept algebra untouched.

| curvature term | to matter against manner | to originality |
|---|---|---|
| dPlasticity by mean plasticity | −0.0173 (se 0.0074) | **+0.0786** (se 0.0073) |
| dPlasticity by mean stability | **+0.0548** (se 0.0057) | +0.0289 (se 0.0061) |
| dStability by mean plasticity | **+0.0574** (se 0.0059) | +0.0283 (se 0.0063) |
| dStability by mean stability | **+0.0482** (se 0.0072) | +0.0231 (se 0.0062) |

**g is nonlinear, decisively.** The four largest terms sit at seven to eleven standard errors, and an invariant curved g with no room specific parameters lifts held out R2 from 0.0243 to 0.0322 on the largest clean design, a third better than the linear invariant model.

That absorbs part, but not all, of the apparent room heterogeneity. Against the linear pooled model the room term lifted 0.0284 to 0.0468, a gain of 65 per cent. Against the curved pooled model it lifts 0.0370 to 0.0530, a gain of 43 per cent, and the optimal weight on the room term falls from 0.5 to 0.4. **So part of what looked like a rotation was curvature in g being read as a room specific slope, and a real room specific residue remains after curvature is allowed for.**

## Dispersion of the per room W against its own sampling error

986 rooms with at least 10 persons, each subsampled to at most 40, giving 30,643 persons in the panel. The null must fix each room's own design matrix and its own residual scale, otherwise rooms with a narrow spread of P, whose W is genuinely noisier, get blamed on real heterogeneity. A wild bootstrap does that: hold the coupling at the pooled W, keep each room's P values and its own residuals, flip only the residual signs.

| cell | mean W | sd observed | sd under invariance | p | excess sd | p after controlling per room reliability |
|---|---|---|---|---|---|---|
| plasticity to matter/manner | −0.0119 | 0.2615 | 0.2272 | 0.005 | 0.1296 | 0.015 |
| plasticity to originality | +0.1887 | 0.2681 | 0.2609 | 0.219 | 0.0616 | 0.647 |
| stability to matter/manner | +0.1433 | 0.3448 | 0.2582 | 0.005 | 0.2285 | 0.005 |
| stability to originality | +0.0055 | 0.3282 | 0.2698 | 0.005 | 0.1870 | 0.005 |

Three of the four cells carry room to room spread beyond what sampling can produce, at excess standard deviations of 0.13 to 0.23 in z units, which is the same size as the couplings themselves. Because rooms differ in how much their members write, they differ in how attenuated their W is, which would mimic heterogeneity; dividing the observed slopes and every null draw by the same per room reliability leaves the same three cells significant, so that is not the explanation.

The one cell with no detectable heterogeneity, p = 0.219, is **plasticity to originality**, which is also the largest and best determined coupling in the matrix. The strongest arm of the coupling is the one that behaves invariantly; the weaker arms are the ones that move.

## The same test on large rooms only, where W is properly estimable

The panel above uses rooms of at least 10 persons. Repeating it on rooms of at least 60 persons, each subsampled to at most 200, gives 478 rooms holding 77,780 persons, a mean of 163 persons per room. That is four times the persons per room, so the sampling spread of the per room W should fall by about a factor of two, and it does: from about 0.26 to about 0.09. The detection floor falls with it, from 0.105 to 0.135 down to 0.036 to 0.056.

| cell | mean W | sd observed | sd under invariance | p | excess sd | p after controlling per room reliability |
|---|---|---|---|---|---|---|
| plasticity to matter/manner | −0.0248 | 0.1161 | 0.0818 | 0.005 | 0.0824 | 0.005 |
| plasticity to originality | +0.1712 | 0.1151 | 0.0843 | **0.005** | 0.0784 | 0.015 |
| stability to matter/manner | +0.1305 | 0.1894 | 0.0980 | 0.005 | 0.1621 | 0.005 |
| stability to originality | −0.0380 | 0.1795 | 0.0991 | 0.005 | 0.1496 | 0.010 |

**All four cells now show heterogeneity beyond sampling, including plasticity to originality**, which was the one cell the smaller rooms left undecided (p was 0.219 there against a floor of 0.116, and its excess of 0.078 sits comfortably above the floor of 0.036 here). Every cell survives the reliability control. The excess standard deviations also come down and tighten, from a range of 0.062 to 0.229 on the noisy panel to 0.078 to 0.162 on the clean one, which is what you expect when better estimated per room slopes stop inflating the spread. **The honest size of the rotation is therefore about 0.08 to 0.16 in z units against couplings of 0.13 to 0.17: of the same order as the coupling, and roughly half of it.**

## Regression dilution, measured rather than assumed

P is estimated from text and is noisy, and differencing two noisy estimates doubles the error variance, so a weak differenced W could be attenuation rather than absent coupling. The error is measured here rather than assumed. The row level scatter of P inside a person room record (454,361 degrees of freedom) gives the error covariance of a record mean; a pair of records carries the sum of two such errors.

| quantity | plasticity | stability |
|---|---|---|
| observed variance of dP | 1.4406 | 1.5042 |
| error variance of dP | 0.8676 | 0.7972 |
| **reliability of the within room person estimate** | **0.398** | **0.470** |

Attenuation is severe: 60 per cent of the within room spread of the measured plasticity is noise, and 53 per cent of the stability. Correcting for it (multivariate errors in variables, W_true = (Sigma_obs − Sigma_err)^-1 Sigma_obs W_obs) gives

| | to matter against manner | to originality |
|---|---|---|
| plasticity | −0.0905 | **+0.4143** |
| stability | **+0.3134** | −0.0626 |

an attenuation factor of 2.5 on the plasticity row and 2.1 on the stability row. Two things follow. The real off diagonal coupling is around 0.31 to 0.41 in z units, not 0.15 to 0.16, so the coupling is not weak, it is badly measured. And attenuation cannot rescue invariance: it makes a coupling look small, it does not make a rotation look present.

A note on what this reliability means. All within record variation is counted as error, which is correct for the construct being used here, a person's disposition **in that room**. It is not the reliability of a stable trait. At a mean of 3.12 rows per record it implies a single post reliability of about 0.18 for plasticity and 0.22 for stability, which sits alongside the single item trait ICC of about 0.12 reported elsewhere.

## Power, and what would settle the remaining question

| cell | sampling sd of W under invariance | minimum detectable heterogeneity | observed excess |
|---|---|---|---|
| plasticity to matter/manner | 0.2272 | 0.105 | 0.130 |
| plasticity to originality | 0.2609 | 0.116 | 0.062 |
| stability to matter/manner | 0.2582 | 0.135 | 0.229 |
| stability to originality | 0.2698 | 0.121 | 0.187 |

The detection floor scales as the inverse square root of persons per room and the inverse fourth root of rooms. The large room panel already carried out that four fold increase in persons per room, and the floor duly fell by about half, from 0.105 to 0.135 down to 0.036 to 0.056, which resolved the one cell the small room panel could not call. Nothing further is needed to settle whether the coupling is invariant: the answer is already in. Halving the floor again would take 776 persons per room across 478 rooms, or 7,648 rooms at the current 163, and would only be worth doing to measure the shape of the rotation rather than to detect it.

## Verdict

**The coupling does not survive as invariant under the cleaner test. It shows a rotation.** After removing the room offset exactly by differencing, removing person leakage, and allowing g to be nonlinear, letting the coupling vary by room still lifts held out prediction from 0.037 to 0.053 on rooms of at least 80 persons; and on rooms of at least 60 persons the room to room spread of W exceeds its own sampling error in **all four** cells at p = 0.005, with an excess of 0.08 to 0.16 in z units against couplings of 0.13 to 0.17. The test is not underpowered; quadrupling the persons per room cut the detection floor in half exactly as predicted and turned the one open cell positive.

## What to carry into Paper 4, stated plainly

- The claim "state variables enter as locations, with the coupling g invariant" is **too strong** and should be weakened. The location term is real and dominant, but it is not the whole state dependence.
- The honest form is **C = g(P) + h(S) + (a small state dependent rotation of g) + eps**, with g itself nonlinear, and with the rotation small enough that a single global W remains the best single estimate for any room you have not measured.
- The specific coupling the earlier level runs reported, plasticity to matter against manner, **does not survive differencing** and should not be carried forward. What survives is off diagonal: plasticity to originality, stability to matter against manner.
- Between room and within room slopes differ by up to a factor of six, so **any level fitted coupling on this corpus is mostly room composition** unless it is explicitly demeaned within room.
- Effect sizes are small in absolute terms, held out R2 of 0.02 to 0.05, which is the per post individual regime the earlier run already flagged as dominated by the within person floor. The rotation is real and it is also small.

## Bounds

Room is the domain, which is a proxy for a community and not the same object as the named state variables (genre, site kind, language); a room specific rotation is not by itself a rotation in any one named state variable, and attributing it to a named W is the next job. Single scorer lineage (disp_d8 and char_dweb, the same lineage as the first identification run); the heavier 27B lineage guard is owed. The heterogeneity test controls for per room reliability by a divisor that is itself noisy and heavy tailed, so its p values are indicative rather than exact. Disposition and character are read from overlapping text; the leave room out control removes that overlap and the coupling survives at about 70 per cent of its size, but only for persons writing in more than one room. On the large room panel the stability row of the per room W correlates with how much a room's members write (+0.34 and +0.45 against log mean rows per person), which is a measurement channel rather than a state one; removing it linearly takes the excess for stability to matter against manner from 0.162 to 0.149 and for stability to originality from 0.150 to 0.126, so it does not account for the heterogeneity but it does inflate it somewhat.

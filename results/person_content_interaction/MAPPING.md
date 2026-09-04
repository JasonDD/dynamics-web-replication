# Frozen person side mapping and interaction: PersuasionForGood

**Frozen before any outcome is read. Theory derived, never fitted.** Committed and tagged prior to the run.
This fixes exactly how the persuadee's measured personality becomes a DYNAMICS-8 disposition, how the
persuader's content becomes the frozen character geometry, and which interaction terms carry the preregistered
prediction. No loading here is estimated from the donation outcome.

## Person side: Big Five to DYNAMICS-8, via the published Big Two

The persuadee (PersuasionForGood role B4==1) carries five measured Big Five scores. The correspondence to the
DYNAMICS-8 disposition axes is direct and stated in advance:

    openness        -> novelty
    extraversion    -> sociability
    conscientiousness -> discipline
    agreeableness   -> yielding
    neuroticism     -> mercuriality

The two DYNAMICS-8 metatraits are then exactly the DeYoung (2006) higher order Big Two, which is why this
mapping needs no fitting:

    person plasticity  P_plas = z(openness) + z(extraversion)          [ = novelty + sociability ]
    person stability   P_stab = z(conscientiousness) + z(agreeableness) - z(neuroticism)
                                                                        [ = discipline + yielding - mercuriality ]

z() is standardisation WITHIN the PersuasionForGood persuadee sample. Decision style (rational, intuitive) and
demographics enter only as baseline main effect controls, never in the interaction.

## Content side: the frozen character geometry

The persuader's concatenated turns are already character scored on the eight axes (psg_scores.jsonl, scored
2026-08-29, before this registration). From those eight axes we take, with the identical SVD recipe used in
every prior test (fit on cc_v3.domain_char8_expanded, never on this corpus):

    MM   = matter/manner PC1     (how much substance relative to how much heat)
    OR2  = the second axis        (the originality facing projection)

## The preregistered interaction (the headline)

The equation of state atlas predicts a specific off diagonal coupling: plasticity couples to originality,
stability couples to matter/manner. Carried to the person by content interaction, the directional prediction
is:

    a higher plasticity persuadee is moved more by higher originality content   ->  term  P_plas x OR2
    a higher stability persuadee is moved more by higher matter content         ->  term  P_stab x MM

Both diagonal terms are predicted to carry. The two off diagonal terms (P_plas x MM, P_stab x OR2) are
included so the block is complete and the prediction can fail in a readable way (if the off diagonal carries
and the diagonal does not, the atlas prediction is wrong).

Interaction block = { P_plas x OR2, P_stab x MM, P_plas x MM, P_stab x OR2 }.

## The analysis (unchanged from the registered battery)

Nested five by five CV ridge. Blocks added in fixed order:

1. **baseline**   person main effects (five Big Five, rational, intuitive) + demographic controls
                  (age, sex, education, income, ideology) + classical textual measures of the persuader turns
                  (length, readability, sentiment, Biber).
2. **+ embedding** the 768 dimension nomic-embed-text representation of the persuader turns.
3. **+ content**  the frozen eight axis character geometry (main effects).
4. **+ interaction**  the four preregistered person by content terms above.

**Headline quantity:** incremental R squared of block 4 over block 3, i.e. the person by content interaction
beyond both margins (person main effects already in baseline, content main effects already in block 3) and
beyond a modern embedding. Persuadee clustered bootstrap for the interval (each row is one persuadee).
Permutation: shuffle the persuadee to content pairing in the interaction construction only, holding both
margins fixed, refit, recompute the increment.

**Outcome:** primary is donated versus not (robust to the heavy tail, base rate about 0.54); secondary is
log(1 + donation) continuous.

**Pass rule (fixed):** delta R squared > 0.01, bootstrap lower bound > 0, permutation p < 0.01 -> the frozen
person by content interaction adds real predictive value. Null if delta <= 0.005 or lower bound <= 0. Weak
between.

## Honest ceiling for this corpus

PersuasionForGood did not randomly assign message character, so a pass here is a heterogeneity association
(the frozen coupling predicts which persuadee was moved by which persuader's character), not the causal
interaction. It is the joining leg, read as association. The causal interaction is reserved for the randomly
assigned corpora (UCSC Persuasion and Personality, Anthropic persuasion) per Amendment 1.

## Amendment 2 (before the corrected run): embedding compressed to top 50 PCs

Forced by the data. At n about 1012 the raw 768 dimension embedding block reduces out of sample R squared
(baseline 0.0263 falls to 0.0182 when the raw embedding is added), and a 200 draw permutation over a 768 wide
design does not complete in the compute budget. Standard remedy: replace the raw embedding with its top 50
principal components (SVD on the standardised embedding, the same compression for every block, a nuisance
control representation, not the object of the test). This keeps the embedding as a strong learned baseline
while making the permutation tractable and reducing the overfit. The interaction headline, its pass rule and
the frozen person and content sides are unchanged.

The chronology, stated plainly so it cannot be read as tuning the representation until the interaction appeared or disappeared: the raw 768 dimension embedding was the original frozen specification and was attempted first; its failure mode was purely mechanical (it reduced out of sample R squared, an overfit at this sample size, and a two hundred draw permutation over a 768 wide design did not complete in budget); the fixed compression to the top 50 principal components was then written down here BEFORE the corrected interaction increment was computed or read. The compression is applied identically to every block and is not a free parameter searched against the outcome.

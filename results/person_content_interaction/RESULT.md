# Result: person by content interaction leg 1 (PersuasionForGood)

**Verdict: NULL on both outcomes.** The frozen person by content interaction adds no predictive value on
PersuasionForGood beyond persuadee personality, content character and a modern embedding. Preregistered in
`PREREGISTRATION.md` + `MAPPING.md` (frozen tag `papers-psg-interaction-frozen`, commit before the run);
Amendments 1 (sharpened target) and 2 (embedding compressed to top 50 PCs) recorded before the corrected run.
Content was character scored 2026-08-29, long before this test. n = 1012 dialogues.

## The numbers (nested five by five CV ridge, incremental R squared)

Primary outcome, donated versus not (base rate 0.538):

| block | held out R squared |
|---|---|
| baseline (persuadee Big Five + decision style + demographics + classical text) | +0.0263 |
| + embedding (50 PCs of nomic-embed-text) | +0.0330 |
| + content (frozen eight axis character) | +0.0310 |
| + interaction (the frozen person by content 2x2) | +0.0302 |

**Interaction increment over baseline plus embedding plus content = -0.0008, bootstrap CI [-0.0031, +0.0015],
permutation p = 0.44.** Below the preregistered pass mark on every criterion. NULL.

Secondary outcome, log(1 + donation): interaction increment = -0.0013, CI [-0.0026, -0.0002], perm p = 0.63.
NULL.

## What this means, honestly

On PersuasionForGood the frozen coupling does not predict which persuadee was moved by which persuader's
character. Read straight, that is a negative result for the interaction on this leg.

It weakens the claim that the coupling should be observable as a generic association in unconstrained
natural dialogue, but it does not directly test the stronger causal claim under randomly assigned content
exposure. The reason was stated in the preregistration before the run: PersuasionForGood is the weakest of
the planned legs. It is free dialogue, not randomly assigned content, so the character of what each persuadee
saw is confounded with who they were talking to and how the conversation went. It is a single charity, so the
between dialogue variance in content character is small. And the outcome, a real donation, is dominated by
disposition and situation. This leg was registered as the heterogeneity association leg, read as association,
precisely because it cannot isolate assigned content movement.

The surviving formulation is narrower than the one we could have stated a day ago, which is the scientific
gain. We can no longer say person by content fit should show up wherever persuasion happens; on
PersuasionForGood it did not. What survives is a specific, testable constraint:

> the coupling may require exogenous variation in content character to become identifiable; observational
> dialogue is insufficient because message character is endogenous to the interaction.

That constraint is exactly what the next leg is built to test.

The value of running it anyway: it is an honest negative that sharpens the case for the corpora that can carry
the sharp test. If the interaction cannot be seen even in association here, the randomly assigned corpora
(UCSC Persuasion and Personality, Anthropic persuasion) are where the coupling has a fair chance, because
there the content character is varied by the experimenter rather than confounded with the conversation. Those
are leg 2 and leg 3.

## What did carry (context, not the test)

The persuadee's own personality predicts donation on its own (baseline R squared 0.026 on the binary), and the
embedding adds a little (0.033). Content character and the interaction do not add beyond that here. So on this
leg the person matters, the message character does not, and the fit between them does not. The theory's claim
is about the fit, and on the one leg that can only measure it as a confounded association, the fit is not
visible.

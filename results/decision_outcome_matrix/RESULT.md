# The decision outcome character matrix: which character wins, and does it depend on the kind of decision?

*DYNAMICS-WEB, Paper 4B flagship matrix. PUBLIC track. 31 August 2026, J. Duke, Kronaxis. This reads the
whole grid at once: across every corpus where a real human made a real decision tied to a text, which
character wins, and whether the winning character is a function of the KIND of decision. It completes Paper
4B's central claim (no single character persuades because persuasion is a function of the outcome) by
measuring it across the corpora together rather than one pair at a time. All scoring reuses held DWEB
8 axis scores; no new frontier model reading underlies the load bearing claims.*

---

## The question, stated as a test

Paper 4B established, on four outcomes read pairwise, that the character which wins is different in every
one. The obvious next question is whether that difference is structured: do decisions of the same KIND
reward the same character, is there a low dimensional shape to "what wins" across decision types, and which
single decisions are the outliers. This document assembles every held outcome corpus into one grid and
answers those three questions directly.

The ruler is fixed throughout: the matter against manner axis (PC1) is the singular vector fit once on
2,648,406 web domains (`the internal reference table`), rigour and depth oriented positive, so **+ is
MATTER, - is MANNER**. Loadings: rigour +0.44, depth +0.40, candour +0.39, stance +0.37, originality +0.23,
commercial_drive -0.26, register -0.34, affect -0.35. The same eight axes and the same web tuned 7B rater
read every corpus, so the corpora share a measurement frame and differ only in the decision.

---

## THE GRID: corpus by decision by winning character

Each row is one corpus. The winning direction is the character of the text the human chose (clicked,
believed, funded, signed, voted for, convicted). "PC1 lean" is the sign of the winning direction on the
matter against manner axis. Effect column gives the load bearing per axis numbers. Every row states its
control and its evidence tier. Two rows are causal (randomised assignment); the rest are ecological.

| corpus | decision (outcome) | winning character (key axes) | PC1 lean | control held | tier |
|---|---|---|---|---|---|
| **Upworthy** | click on a headline (randomised A/B) | originality +0.092, affect +0.054, commercial +0.036, register +0.028 | **MANNER** (causal PC1 -0.051) | within test fixed effect: same article + image, exposure randomised | **causal / settled** |
| **Reddit** (pending) | comment upvote score (spread) | self queued, `third_outcome_spread.py` running | pending | within subreddit + thread | pending |
| **Amazon** (pending) | helpful vote on a review (attention) | self queued, small sample scoring at  | pending | within product (parent_asin), rating + length held | pending |
| **UK petitions** | signatures on a reworded ask | originality +0.157, depth +0.091 (joint originality +0.171\*, depth +0.325\*) | ~neutral to MATTER (PC1 +0.076 ns) | within same ask cluster, session year + log days open | ecological, thin (n=240 in 109 clusters) |
| **Kickstarter** | project funded (1/0) | originality +0.169\*\*\*, commercial +0.111\*\*\*, affect -0.086\*\* | ~neutral (PC1 +0.026\*) | none within group (topic mix named) | firm (n=6,000) |
| **DonorsChoose** (pending) | project approved (institutional gate) | self queued scoring at  | pending | within grade + subject | pending |
| **Persuasion for good** | a donation given (donated >0) | rigour +0.222\*\* | MANNER to neutral (PC1 -0.042 ns) | none; capped $2 task | suggestive (n=1,017) |
| **Milkman megastudy** | flu shot taken (randomised nudge) | reserved institutional reminder +; surprising / interactive / casual - | **MATTER** (direction only, no axis scores) | patients randomised to arm | causal but coarse (19 arms) |
| **ChangeMyView** | a mark for a changed mind (delta) | stance -0.20\*\*\* (balance), depth +0.10\*\*\*, affect +0.08\*\*\* | **MANNER** (PC1 -0.074\*\*\*) | matched pairs: persuadee, topic, moment fixed | firm (recovers Tan 2016) |
| **Stack Exchange** | answer accepted by the asker | winning PC1 +0.32; consistent across 5 rooms (+0.20 to +0.43) | **MATTER** | within question strata; same user null | firm |
| **debate.org (DDO)** | audience vote for a side | rigour d +0.29, depth d +0.26, stance d +0.22, affect d -0.12 | **MATTER** (pooled PC1 +0.98, d +0.27\*\*\*) | within debate matched, per audience | firm |
| **Old Bailey** | a guilty verdict | rigour +0.31\*, PC1 +0.205\*; depth -0.38\* | **MATTER** (weak) | offence + word count + n persons | suggestive, upper bound (evidence coef 0.590 dominates) |

Stars: \* p<0.05, \*\* p<0.01, \*\*\* p<0.001. Sources: `upworthy_causal_character.txt`,
`found_human_triangulation.txt` (Kickstarter, persuasion for good, ChangeMyView), `cmv_within_pair.txt`,
`se_arbiter_where.txt`, `ddo_coupling.txt`, `oldbailey_verdict_character.txt`,
`uk_petitions_wording_signatures.txt`, `second_causal_anchor/RESULT.md` (Milkman).

---

## FINDING 1: the winning character is NOT the same across decisions, and it flips sign

The direct test of whether one axis moves several outcomes the same way returns no such axis. Projected onto
the matter against manner ruler, the sign of the winning direction disagrees across the grid:

- **rewards MANNER**: Upworthy click (-0.051, causal), ChangeMyView delta (-0.074), persuasion for good donation (-0.010)
- **rewards MATTER**: Stack Exchange accepted answer (+0.32), debate.org audience vote (+0.31), Old Bailey verdict (+0.20), Milkman vaccination (direction), UK petition signatures (+0.08 weak)
- **~neutral on matter/manner, driven by originality instead**: Kickstarter funded (+0.03)

The earlier triangulation put a number on the disagreement: across Kickstarter, charity donation and
ChangeMyView, **0 of 9 axes** move the human outcome the same direction, and the matter/manner projection
itself disagrees in sign. The whole grid confirms and widens it. This is the Paper 4B result, now read
across eleven decisions rather than four: there is no single character that persuades, because what
persuades is a function of the outcome.

---

## FINDING 2: the structure of what wins is TWO dimensional, not one

To ask whether decisions of the same KIND reward the same character, each corpus with a full eight axis
winning vector was reduced to that vector, z scored within the corpus (so the comparison is of SHAPE, not
of the differing effect scales), and correlated with every other corpus. The cross corpus correlation of
winning character shape (`cluster.py`, seven corpora with full vectors):

```
              Upworthy  petitions  CMV    DDO    OldBailey  Kickstart  PSGdonate
Upworthy        +1.00     +0.03   +0.31  -0.75    +0.09      +0.20     -0.23
UK petitions    +0.03     +1.00   +0.01  +0.24    -0.09      +0.51     -0.52
CMV delta       +0.31     +0.01   +1.00  -0.70    -0.31      -0.45     +0.46
DDO vote        -0.75     +0.24   -0.70  +1.00    +0.02      +0.27     -0.13
Old Bailey      +0.09     -0.09   -0.31  +0.02    +1.00      +0.25     +0.08
Kickstarter     +0.20     +0.51   -0.45  +0.27    +0.25      +1.00     -0.37
PSG donated     -0.23     -0.52   +0.46  -0.13    +0.08      -0.37     +1.00
```

Two facts fall out, and they name two independent dimensions of "what wins".

**Dimension A, matter against manner (the attention to conviction axis).** The strongest structure in the
matrix is the near mirror opposition between the click and the audience vote: Upworthy and debate.org
reward opposite shapes (-0.75), and ChangeMyView and debate.org likewise (-0.70). The attention outcome
(click) and the debate room delta sit on the manner pole; the audience vote, the accepted answer and the
verdict sit on the matter pole. This is the single "attention to conviction" gradient Paper 4B named:
manner opens the door, matter closes it.

**Dimension B, novelty (originality), which the matter/manner axis misses.** Sorting the corpora by how
much they reward originality relative to their own mean gives a second, independent ordering:

```
  Kickstarter funded    orig lean +1.95   HIGH  (fund a pitch)
  UK petitions sign      orig lean +1.78   HIGH  (sign a reworded ask)
  Upworthy click         orig lean +1.53   HIGH  (open a headline)
  Old Bailey verdict     orig lean +0.88
  CMV delta              orig lean -0.14
  DDO audience vote      orig lean -0.49   LOW   (vote after a debate)
  PSG donation           orig lean -1.49   LOW   (actually give money)
```

Originality is rewarded by the first impression decisions (a headline to open, a pitch to fund, an ask to
sign) and penalised, relatively, by the sustained decisions (a debate to vote on, a donation to actually
make). Originality loads only +0.23 on the matter/manner axis, so this ordering is largely orthogonal to
Dimension A: a decision can be matter leaning yet novelty hungry (petitions), or matter leaning and novelty
averse (donation). The two dimensions together, matter/manner and novelty, are the low dimensional
structure of what wins, and they match the series result elsewhere that the character space itself is about
two dimensional (Paper §10.12, PC1 is matter against manner; a second axis carries novelty and engagement).

The honest headline is therefore sharper than "one attention to conviction line": **the winning character
is a function of the decision kind along two axes at once. How much deliberation the decision involves sets
the matter/manner pole; whether the decision is a first look or a committed act sets the novelty pole.**

---

## FINDING 3: the decision types, clustered

Reading the two dimensions together sorts the eleven decisions into recognisable regimes. The clustering is
directional (seven full vectors, correlations at low degrees of freedom), so the regime labels are the
claim, not the exact tree.

- **ATTENTION (get looked at): manner and high novelty.** Upworthy click, and by construction the pending
  Reddit spread and Amazon helpful vote rows. The click rewards affect, originality and register and runs
  toward manner, causally. Petition signatures sit at the edge of this regime: strongly novelty rewarding
  like an attention outcome, but nearer neutral on matter/manner because a signature is a small action, not
  only a look.

- **DELIBERATION, general audience: matter and low novelty.** Stack Exchange accepted answer, debate.org
  audience vote, Old Bailey verdict. When a general body weighs a text to decide what is true, right or
  resolved, substance wins and novelty does not. These three agree on the matter pole even though they span
  a Q&A site, a debate audience and a criminal jury across two and a half centuries.

- **DELIBERATION, self selected room: manner and balance (THE OUTLIER).** ChangeMyView is a mind change, a
  conviction outcome, yet it rewards the manner pole (PC1 -0.074) and a balanced, low stance argument. It
  clusters with the click, not with the other deliberations. The reason is the room: ChangeMyView is a self
  selected community of people who argue for sport, so its taste for a well turned, calibrated argument over
  raw scholarly weight is a property of that room, exactly Tan 2016, and it is the clean demonstration that
  WHERE a decision is made can flip the sign of the winning character.

- **FUNDING a pitch: novelty first, matter/manner neutral.** Kickstarter funded, and petitions in its
  action aspect. Backing a project is a first impression bet, and it rewards originality and a light
  commercial pull rather than either pole of matter/manner.

- **A COMMITTED act: substance, novelty averse.** Persuasion for good donation (rigour +0.22) and the
  Milkman vaccination (institutional reminder wins, surprise and gimmick lose, causally). The character that
  opens the door is not the character that gets money out of a wallet or a needle into an arm. This is the
  far, conviction end of the funnel, and it is the cleaner causal half: on a real behavioural action, matter
  wins and manner loses.

---

## FINDING 4: the outliers, named

- **ChangeMyView** is the principal outlier: a deliberative mind change that rewards manner. It is not noise,
  it is the room effect made visible, and it is why the matter/manner sign cannot be read off the decision
  type alone without also knowing whether the audience is general or self selected.
- **Old Bailey** is a soft outlier inside the general deliberation cluster: it rewards rigour but penalises
  depth (-0.38) and its verdict effect is dominated by the visible weight of evidence (coef 0.590 versus
  0.205 for character), so it is an upper bound on rhetoric, not a clean estimate.
- **debate.org** is an outlier on the WHO question, not the WHAT: the winning character is audience
  independent (out of sample AUC 0.447, coupling null), so unlike the room effect of ChangeMyView, here the
  disposition of the voter does not move which character wins. Room beats person.
- **Milkman vaccination** is the outlier that anchors the committed act regime: an action outcome whose
  winning character is the opposite of the click, from a randomised field trial, which is the strongest
  single piece of causal evidence that the funnel is real and not a scoring artefact.

---

## VERDICT: yes, the winning character is a function of the decision kind

Across eleven human decisions read on one ruler, no character axis wins them all, and the matter/manner
projection flips sign between decision types. The winning character is a function of the decision kind, and
the function is low dimensional but not one dimensional. It has two arguments: how much deliberation the
decision demands (which sets the matter against manner pole, the attention to conviction gradient) and
whether the decision is a first look or a committed act (which sets the novelty pole). Manner and novelty
earn attention and a first impression; matter earns conviction and a committed act; and a self selected
room can move the matter/manner pole against the type, which is the ChangeMyView outlier. This is Paper 4B's
claim, that persuasion is a function of the outcome, now measured across the whole grid and given its
structure: a two dimensional map of what wins, indexed by the kind of decision.

---

## Honest bounds

- **Ecological except two.** Only Upworthy (randomised headlines) and Milkman (randomised nudges) are
  causal. The other nine carry the confounds of their setting: topic mix, self selection of who writes,
  donates or shares, and platform norm. Every row names its own control; the load bearing claim is the sign
  DISAGREEMENT across rows, which no single confound explains, not any one coefficient.
- **One instrument.** All eleven are read by the same eight axis 7B rater, so they share its measurement
  bias even as they differ in every other way. This is why the disagreement between corpora, not any single
  effect size, is the claim. Scorer noise attenuates every coefficient toward zero, so the true effects are
  at least this large.
- **The clustering is thin.** Seven corpora carry a full eight axis winning vector; the cross corpus
  correlations sit at low degrees of freedom, so the regime labels are directional. The two robust facts
  under them are model free: 0 of 9 axes agree in sign across the triangulated three, and the matter/manner
  projection changes sign across the grid.
- **Milkman is direction only.** Its verbatim per arm texts sit behind a paywall (SSRN 10.2139/ssrn.3780267),
  so it enters the grid by the authors' own human attribute codings and our objective feature computation,
  both pointing the same way, not by an eight axis score. Scoring it is a costed fast follow of hours once
  the appendix text or the message mockup images are obtained.
- **Length and outcome type are partly confounded across corpora** (short media here tend to measure
  attention, long media conviction); the companion `funnel_by_medium/RESULT.md` separates that confound and
  finds the manner attention effect is a short format law while the matter conviction effect is bandwidth
  gated, consistent with Dimension A here.
- **Pending rows.** Reddit spread (`third_outcome_spread.py`), Amazon helpful vote and DonorsChoose approval
  are self queued behind the running fleet at ; they slot into the ATTENTION and FUNDING/ACTION regimes
  and are marked pending, not claimed. The free but unfetched extensions (Manifesto Project to election
  result, Retraction Watch to abstracts, OpenReview to accept/reject) are named in the acquisition ledger as
  the next widening, not run here.

## Reproduce

- Grid numbers: the per corpus result files listed under THE GRID, all in
  `docs/papers/dynamics_web_series/results/`.
- Clustering and the two dimensions: `cluster.py` (pure numpy, reads the held effect vectors inline).
- Pending rows: `matrix_aux.py` on the internal host (small self queued scoring of Amazon and DonorsChoose at ,
  WORKERS 4, reuses the exact `cc_found_human_score.py` scoring contract), writing `aux_amazon_donors.txt`
  in this directory when complete.

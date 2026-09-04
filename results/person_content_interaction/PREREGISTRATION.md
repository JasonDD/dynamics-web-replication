# Preregistration: the person by content interaction battery

**Registered before any outcome column is read.** Companion to the frozen geometry
(`prediction_contest/PREREGISTRATION.md`, tag `papers-v80-frozen`) and the embedding round
(`prediction_contest/argq_contest_embed.json`, tag `papers-v82-embedding`). This registers the next tier of
the measurement to theory ladder: does the frozen person by content geometry predict which real person was
moved by which real message, in humans whose personalities, exposures and outcomes were all recorded years
before the geometry existed.

## The question

Content alone barely moves these outcomes. The found human triangulation already run on the content side
(`found_human_triangulation.txt`: Kickstarter, PersuasionForGood, ChangeMyView) shows the eight character axes
carry only a weak content main effect on a human persuasion outcome (Kickstarter originality and commercial
drive significant; PersuasionForGood donation essentially null on the matter/manner ruler). That is not a
failure. The theory does not say the message wins on its own. It says the fit between a particular person and
a particular message decides the response. So the test is the interaction, not the main effect.

Formally, for participant i exposed to message j, predict the observed human response from information
available before the response only:

    response_ij  ~  f( person_state_i , frozen_DYNAMICS_content_j , person_i x DYNAMICS_j coupling )

## What is frozen, and when

Frozen before any outcome is read, and tagged:

1. The eight axis character scores of every message (already computed; PersuasionForGood at `psg_scores.jsonl`,
   scored 2026-08-29, long before this registration). Never refitted to the outcome.
2. The matter/manner PC1 recipe (SVD on `the internal reference table`), identical to every prior test.
3. The person to person space mapping: the published Ashlar coupling direction from the disposition axes to the
   character axes, used to build the interaction terms. The mapping from each corpus's native person
   instrument (Big Five, Schwartz values, decision style) into the DYNAMICS-8 disposition frame is written
   down here, as fixed loadings, before the outcome is touched. It is a stated hypothesis, not a fit.

## The corpora, in the order they run

**1. PersuasionForGood (Wang et al., ACL 2019), primary, runnable now, no new scoring.**
1,017 real donation dialogues, 1,285 participants. `full_info.csv` already on the box carries, per person:
Big Five, the ten Schwartz values, Moral Foundations, rational and intuitive decision style, and full
demographics. Outcome: the persuadee's actual donation (continuous dollars; and donated versus not as the
robust binary). The persuader's turns are already character scored. This is the cleanest immediately runnable
person by content interaction test we hold, and the outcome involves real money.

**2. Persuasion and Personality Corpus (UC Santa Cruz, nlds.soe.ucsc.edu), to acquire.**
637 subjects, Big Five, prior belief per socio political issue, the argument shown (factual versus emotional),
and measured belief change after exposure. The cleanest belief change interaction: per argument attitude
movement against a full personality profile. Acquire, confirm licence, reduce to the common shape.

**3. Anthropic persuasion dataset (Hugging Face), content by initial state replication.**
Participant, claim, argument shown, rating_initial and rating_final. No rich personality, so it cannot test
the full person side; it independently replicates frozen DYNAMICS(content) by initial state to attitude
movement. A clean, public replication leg.

**4. ChangeMyView personalised (ACL 2026 findings) plus Webis CMV, ecological scale.**
Person's prior writing to derive the person side, competing messages to the same original poster, actual
delta as the outcome. Derive DYNAMICS-8 from prior writing only; ask whether the frozen coupling predicts
which competing argument changes this particular person's mind. Largest and most naturalistic; run last.

## The one analysis, applied unchanged to every corpus

Nested five by five cross validation, ridge, incremental held out R squared, exactly as the ArgQ and embedding
contests. Feature blocks added in a fixed order:

- **Baseline:** prior belief or initial state + person main effects (Big Five and values as given) + topic or
  argument identity + classical textual measures (length, readability, sentiment, Biber).
- **+ embedding:** the 768 dimension nomic-embed-text representation of the message, the hard rival that
  passed in v82.
- **Hard model:** + frozen DYNAMICS content geometry + the preregistered person by DYNAMICS coupling
  interaction terms.

**Headline quantity:** the incremental R squared of the interaction block over baseline plus embedding, with a
participant clustered bootstrap interval and a permutation test that shuffles the person to message pairing
(breaking only the interaction, holding both margins). One pass rule, fixed now, for every corpus.

## Pass rule (fixed before any number)

For each corpus, the frozen person by content interaction **passes** when all three hold:
delta R squared over baseline plus embedding > 0.01, bootstrap lower bound > 0, permutation p < 0.01.
**Null** when delta <= 0.005 or the bootstrap lower bound <= 0 (the interaction adds nothing beyond
personality, content and a modern embedding). **Weak** between.

Reported honestly across the battery: pass in one is interesting; the same frozen mapping passing across belief
change, real money donation and naturally occurring mind change, with no refit, is a different evidential
category from anything shipped so far.

## The honest ceiling (stated up front)

None of these corpora randomised messages **by DYNAMICS coordinates**. So a pass is a prospective, frozen test
of heterogeneous treatment response in real humans, not causal proof that the geometry is the machinery. It
narrows the gap to the one decisive experiment named in Paper 4A (move the geometry, predict the person); it
does not close it. A failure across the battery, by contrast, would land a serious hit on the large
interpretation.

## Amendment 1 (before any run): the sharpened target

Recorded after reading v82's Paper 4B, before any outcome is touched. Paper 4B already establishes the
**causal anchor** on the content side: the headline archive holds about 32,000 variants, 2,599 usable
randomised tests across 11,098 arms, where character differences between alternative headlines for the same
item causally change clicks. So this battery does **not** need to re establish that content character moves
behaviour. Its job is to **join the two halves already established independently** (content character causes
behaviour; person disposition couples to content character) into the complete triangle:

> person measured independently before exposure  x  experimentally varied content character  ->  heterogeneous human response

This reprioritises the corpora by whether the message was **randomly assigned**:

- **Sharp causal interaction test** (random assignment + pre exposure personality + individual outcome): the
  UCSC Persuasion and Personality corpus (factual versus emotional arguments, assigned) and the Anthropic
  persuasion dataset (assigned arguments, rating_initial to rating_final) are promoted to the front of the
  queue if assignment is confirmed random. There the question is the sharp one: did the assigned movement in
  content character move different real people differently, in the direction the frozen person by content
  geometry predicted in advance.
- **Heterogeneity association** (no random assignment): PersuasionForGood (free dialogue, real donation) and
  ChangeMyView (observational) test whether the frozen coupling predicts which person was moved by which
  message, but cannot attribute it to the assigned movement. Still run, as the joining and scale legs, and
  read as association not as the causal interaction.

The pass rule and the one analysis are unchanged; only the run order and the interpretation label per corpus
are refined. The prize the advisor names: if the sharp test passes without fitting the coupling to the
outcome, the large interpretation moves substantially.

## Amendments

Any deviation forced by the data (a mapping that cannot be built, an outcome distribution that breaks the
model) is recorded here as a numbered amendment, with its reason, before the corrected run, never silently.

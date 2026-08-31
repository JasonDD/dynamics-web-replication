# Manner inflation as a deception signature, and dark patterns as the test case

*DYNAMICS-WEB series: Appendix B, tested (PUBLIC track). Signature, detector, PCAA gate, and
the expanded manipulation taxonomy. The pattern to persona coupling table is measured under a
separate restricted track and is deliberately absent here (see Disclosure below).*

Scorer: `truthometer/scripts/cc_found_human_score.py` (8 axis DWEB character instrument,
qwen2.5-7b-atlas on DL580 :8301). Analysis: `analyse_manner_inflation.py` in this directory.
Data prep: `prep_deception.py`. All inputs on NAS `/mnt/nas/kronaxis/corpora/`.

---

## 1. The claim under test

Manipulation should show a measurable character signature: **manner inflated past what the
genre's matter earns**. On the 8 axes, matter = rigour + depth; manner = affect + stance +
register. The per text metric is a residual:

    residual  = mean(manner axes) - mean(matter axes)
    aff_gap   = affect - matter          (the precise predicted form)

The companion length result (`results/length_mechanism/RESULT.md`) says matter needs bandwidth
while affect is instant: short text cannot express rigour or depth, so a short manipulative
message is forced into an affect channel. That sharpens the prediction from "generic high manner"
to a specific form: **high affect with starved matter**. Dark pattern microcopy, being the
shortest deceptive text there is, is the sharpest place to test it.

## 2. Domains (deceptive vs a matched honest control)

| domain | deceptive | honest control | control kind |
|---|---|---|---|
| IRA | Internet Research Agency political trolls | Change My View winning arguments | cross genre (sincere persuasion) |
| phishing | phishing emails | legitimate ("safe") emails | same genre, same source |
| dark | dark pattern UI microcopy (RachitD set) | neutral UI and product microcopy | same genre, same source |
| LIAR | PolitiFact false / pants on fire claims | PolitiFact true claims | same genre, same source |

The IRA control is cross genre (long form Reddit), so its gap is confounded by length; the other
three controls are same genre and same source. LIAR "deception" is fact check falsity, which is
not the same as intent to manipulate, so it is the weak case by design.

Separately, the **Mathur et al. 2019** dark pattern corpus (1,818 instances, seven categories,
fifteen surface types) carries surface form labels and is scored on its own to test whether each
surface form carries the predicted signature.

## 3. The expanded manipulation matrix (five axes)

Appendix B of *Obsidian: Engine of Influence* gives one axis: trait. The measured object is the
product of five. The taxonomy below is public knowledge (Cialdini, Mathur, the FTC and EU
deceptive design categories); what is withheld is the measured lift of each pattern on each
persona (see Disclosure).

**Axis 1, Target.** HEXACO trait poles, mapped also onto DYNAMICS-8 (the disposition instrument
we measure) and the Dark Tetrad as target types: narcissism (ego traps, exclusivity),
Machiavellianism (complicity offers), psychopathy (thrill and challenge), sadism (outrage bait).

**Axis 2, Mechanism.** Cialdini's seven (reciprocity, commitment and consistency, social proof,
authority, liking, scarcity, unity) plus the cognitive bias exploits (loss aversion, anchoring,
sunk cost, status quo default, framing).

**Axis 3, Affect channel.** The short form weapon, sub channelled: fear, greed, guilt, shame,
FOMO, hope, outrage. This is where measurement bites hardest because short text has no room for
matter.

**Axis 4, Surface form.** Grounded in the corpus labels: Mathur's sneaking, urgency,
misdirection, social proof, scarcity, obstruction, forced action, and the FTC and EU deceptive
design categories.

**Axis 5, State and severity.** Manipulation is trait by state: grief, financial stress,
isolation and decision fatigue amplify specific patterns (Paper 4 state dependence applied to
harm). Each cell carries a harm rating and a reversibility rating that tell the gate what to
block hard versus flag.

### The matrix, by surface form

Harm: how much a fooled user loses. Reversibility: how easily they undo it (high = easy return,
low = trapped in recurring charges or a cancellation maze). "Signature (predicted)" is the
character form the theory implies; the measured column is filled in Section 6.

| Surface type (Mathur) | Category | Mechanism | Affect channel | Target pole / Tetrad | Harm | Reversibility | Signature (predicted) |
|---|---|---|---|---|---|---|---|
| Low stock message | Scarcity | scarcity, loss aversion | FOMO, greed | high Emotionality; impulsive | mild | high | high affect, starved matter |
| Countdown timer | Urgency | scarcity, loss aversion | FOMO, fear | impulsive | mild | high | high affect, starved matter |
| Limited time message | Urgency | scarcity, loss aversion | FOMO | impulsive | mild | high | high affect, starved matter |
| High demand message | Scarcity | social proof, scarcity | FOMO | conforming | mild | high | high affect, starved matter |
| Activity notification | Social Proof | social proof | FOMO, conformity | high Agreeableness; low self esteem | mild | high | high affect, starved matter |
| Confirmshaming | Misdirection | framing, liking | guilt, shame | high Agreeableness; guilt prone | moderate | high | high affect (guilt), starved matter |
| Pressured selling | Misdirection | authority, anchoring | fear of loss | low domain knowledge | moderate | moderate | faked matter (pseudo expert) |
| Trick questions | Misdirection | framing, default | confusion | low Conscientiousness | moderate | moderate | starved matter |
| Testimonials of uncertain origin | Social Proof | authority, social proof | trust, hope | high Agreeableness; high Honesty Humility | moderate | moderate | faked matter (fake credibility) |
| Hidden costs | Sneaking | anchoring, sunk cost | (quiet) | low Conscientiousness | high | low | faked matter (itemised totals look rigorous) |
| Hidden subscription | Sneaking | status quo default | (quiet) | low Conscientiousness | high | low | starved matter, quiet |
| Sneak into basket | Sneaking | default | (quiet) | low Conscientiousness | moderate | moderate | starved matter, quiet |
| Hard to cancel | Obstruction | sunk cost, status quo | frustration | high Conscientiousness (exploited by friction) | high | low | structural, not textual |
| Forced enrollment | Forced Action | forced choice | (none) | any | moderate | moderate | structural, not textual |
| Visual interference | Misdirection | salience, framing | (none) | any | moderate | high | structural, not textual |

### The exception that proves the frame

Every affect weapon abandons matter because it has no room for it. One family does the opposite:
it **fakes** matter. Hidden costs fabricate an itemised total that reads as precise and rigorous;
testimonials of uncertain origin fabricate credibility; pressured selling fabricates a pseudo
technical justification. In Appendix B this is the illusion of control cell (high
Conscientiousness): the mark trusts numbers, so the pattern manufactures numbers. The instrument
should catch these as inflated matter rather than inflated affect. Section 6 tests exactly that.

The target column reads onto DYNAMICS-8, the disposition instrument the programme measures:
"impulsive" is high impulsivity and low discipline; "conforming" is high sociability and high
yielding; "guilt prone" is high yielding with high candour; "low domain knowledge" is low acuity.
This is the theory side mapping only. The measured question, which measured persona each pattern
lands hardest on, is the coupling table and is withheld (Section 4).

The Dark Tetrad and HEXACO target cells (ego traps for narcissism, complicity offers for
Machiavellianism, outrage bait for sadism, authority deception for high Honesty Humility) are
theory rows: the shopping corpora do not contain them in quantity, so they are named in the
matrix but not measured here. They are the natural target of a future corpus.

---

## 4. Disclosure (hard split)

This file is the **PUBLIC** track. It carries the signature, the detector, the PCAA gate and its
block rates, the capability claim, and the taxonomy above, all of which arm defenders and cost
attackers nothing new (Cialdini, Mathur, the FTC and EU categories are already public).

The **pattern to persona coupling table** (which pattern lands hardest on which measured persona,
with lift) is an operator's manual and a trade secret. It is computed and stored only under the
restricted track (`docs/internal/restricted/obsidian_coupling/`, `DO NOT SHARE` headers) and is
**not** computed or printed anywhere in this file. Two converging reasons: responsible disclosure
(publish the detector and the fix, never the exploit), and the coupling is the moat (findings are
unpatentable; the gate plus the know how is the defensible asset). Restraint here is a credibility
signal to DSTL, SBRI and serious investors, not a limitation.

---

## 5. Method

- Prep (`prep_deception.py`) builds one `{id,text,outcome,kind}` file, balanced and capped per
  class, for phishing, dark (RachitD), LIAR, plus the Mathur strings with a metadata sidecar
  (`mathur_meta.jsonl`) carrying surface type, category, and word count. IRA and CMV are already
  scored and are folded in at analysis time.
- Scoring hits the shared :8301 endpoint. The run coordinated with a concurrent `manip-score`
  job: scoring paused while that job held the endpoint and resumed at full worker count once it
  finished, so neither job was starved.
- Classifiers are numpy logistic regression with five fold cross validation; AUC is the
  Mann Whitney statistic. Cross domain AUC trains on one domain and tests on another. The pooled
  leave one domain out detector trains on three domains and is tested on the fourth, so its block
  rate on a domain comes from a model that never saw it.

---

## 6. Measured results

Scored 6,244 texts in this run (plus 8,000 IRA and 2,000 CMV already held). Balanced per class
for every classifier.

### 6.1 Character by domain (mean per axis group)

| domain | group | matter | manner | affect | residual | affect_gap |
|---|---|---|---|---|---|---|
| IRA vs CMV | deceptive | 0.277 | 0.528 | 0.766 | 0.250 | 0.489 |
| IRA vs CMV | honest | 0.587 | 0.544 | 0.539 | -0.043 | -0.047 |
| phishing vs safe | deceptive | 0.151 | 0.361 | 0.736 | 0.209 | 0.584 |
| phishing vs safe | honest | 0.481 | 0.465 | 0.473 | -0.016 | -0.007 |
| dark vs neutral UI | deceptive | 0.140 | 0.205 | 0.390 | 0.065 | 0.250 |
| dark vs neutral UI | honest | 0.274 | 0.345 | 0.406 | 0.071 | 0.132 |
| LIAR false vs true | deceptive | 0.410 | 0.550 | 0.519 | 0.140 | 0.110 |
| LIAR false vs true | honest | 0.479 | 0.543 | 0.487 | 0.064 | 0.009 |

### 6.2 The deception gap (deceptive minus honest): generic residual vs the precise affect form

| domain | residual d | residual gap | affect_gap d | affect_gap gap |
|---|---|---|---|---|
| IRA vs CMV | +1.61 | +0.293 | +2.18 | +0.537 |
| phishing vs safe | +1.23 | +0.225 | +2.08 | +0.592 |
| dark vs neutral UI | -0.04 | -0.006 | +0.39 | +0.118 |
| LIAR false vs true | +0.32 | +0.076 | +0.43 | +0.101 |

The affect form (affect minus matter) beats the generic manner form (manner minus matter) in every
domain, and dramatically so for dark patterns: the generic residual finds nothing there (d = -0.04)
while the affect form finds a small but real gap (d = +0.39). The programme's own length result
predicted this: stance and register are style axes that short manipulative text cannot carry, so
they add noise; affect is the channel that survives at any length. The right instrument is affect
starvation of matter, not generic manner.

### 6.3 Within domain separability (balanced, five fold cross validation, AUC)

| domain | 8 axes | residual only |
|---|---|---|
| IRA vs CMV | 0.958 | 0.856 |
| phishing vs safe | 0.973 | 0.793 |
| dark vs neutral UI | 0.861 | 0.520 |
| LIAR false vs true | 0.654 | 0.592 |

Every domain is separable on the full 8 axes (dark patterns strongly, LIAR weakly). But the
manner residual alone separates only the verbose domains; for dark patterns it is at chance
(0.520). Dark patterns are detectable by character, just not by manner inflation.

### 6.4 Cross domain transfer (train on the row domain, test on the column domain), 8 axis logistic

| train \ test | ira | phish | dark | liar |
|---|---|---|---|---|
| ira | 0.956 | 0.966 | 0.462 | 0.644 |
| phish | 0.945 | 0.974 | 0.567 | 0.632 |
| dark | 0.802 | 0.820 | 0.862 | 0.507 |
| liar | 0.891 | 0.773 | 0.410 | 0.665 |

IRA and phishing transfer to each other almost perfectly (0.945 and 0.966): one signature, two
domains. Nothing transfers to dark patterns (0.46 to 0.57, at or below chance) and dark does not
transfer to LIAR. The verbose persuasive family shares a signature; dark patterns sit outside it.

### 6.5 Residual only cross domain, and the pooled leave one out detector

| domain | residual only AUC (no training) | leave one domain out AUC |
|---|---|---|
| IRA vs CMV | 0.860 | 0.918 |
| phishing vs safe | 0.792 | 0.877 |
| dark vs neutral UI | 0.479 | 0.428 |
| LIAR false vs true | 0.593 | 0.628 |

The manner residual, used raw as a deception score with no training at all, scores IRA and
phishing at 0.86 and 0.79: that is the domain independent signature, and it is genuinely
independent (the leave one out detector, which never saw the test domain, still lands 0.92 and
0.88). On dark patterns the same detector is below chance (0.428): trained on the other three
domains it actively mispredicts dark patterns, because their honest control is itself short and
affect tinged.

### 6.6 PCAA gate: block rate on deceptive at a fixed false positive rate on the honest control

The gate score is the pooled detector that never saw the domain (Section 6.5), so these are the
honest cross domain block rates a defender would actually get.

| domain | block at 5% false positive | block at 10% false positive |
|---|---|---|
| IRA vs CMV | 65.8% | 76.0% |
| phishing vs safe | 36.4% | 63.7% |
| dark vs neutral UI | 8.2% | 21.2% |
| LIAR false vs true | 15.5% | 26.2% |

A character only gate catches most troll content and a majority of phishing at a 10% false alarm
budget, with no domain specific training. It is near useless on dark patterns cross domain (8%),
which need their own within domain model or a non character feature.

### 6.7 The signature by surface form (Mathur 2019, per pattern type)

This is the test that matters for Appendix B. Neutral UI baseline: matter 0.274, affect 0.406.
`aff-mat` is affect minus matter within the type; the last two columns are the lift over the
neutral baseline.

| surface type | n | median words | matter | affect | `aff-mat` | affect vs base | matter vs base |
|---|---|---|---|---|---|---|---|
| Confirmshaming | 169 | 7 | 0.286 | 0.707 | +0.421 | +0.301 | +0.012 |
| Pressured Selling | 45 | 7 | 0.200 | 0.553 | +0.353 | +0.147 | -0.074 |
| Limited time message | 88 | 8 | 0.076 | 0.367 | +0.291 | -0.039 | -0.198 |
| High demand message | 47 | 15 | 0.229 | 0.502 | +0.273 | +0.096 | -0.045 |
| Low stock message | 631 | 4 | 0.030 | 0.293 | +0.263 | -0.113 | -0.244 |
| Countdown timer | 138 | 7 | 0.106 | 0.364 | +0.258 | -0.042 | -0.168 |
| Visual interference | 14 | 5 | 0.218 | 0.393 | +0.175 | -0.013 | -0.056 |
| Activity notification | 313 | 8 | 0.183 | 0.288 | +0.105 | -0.118 | -0.091 |
| Trick questions | 8 | 32 | 0.319 | 0.375 | +0.056 | -0.031 | +0.045 |
| Hard to cancel | 30 | 50 | 0.443 | 0.293 | -0.150 | -0.113 | +0.169 |

The scarcity and urgency weapons behave as the theory says at the matter end: low stock messages,
the single largest and shortest type (631 instances, median four words), score matter 0.030,
essentially zero, the extreme of starved matter. Confirmshaming, the guilt weapon, has the highest
affect of any type (0.707, +0.30 over baseline). What most types do not show is affect inflated
*over the neutral baseline*: the neutral UI control is itself full of live product copy, so its
affect is already 0.406, and a four word "Only 2 left" cannot beat it on affect. The manipulation
shows up as matter collapse, not affect spike, once the control is this short.

**The exception holds.** Hard to cancel, the obstruction pattern, is the only type that inverts:
matter 0.443 (the highest, +0.17 over baseline) and affect below baseline, `aff-mat` negative. It is
also the longest type (median 50 words) and reads as procedural, bureaucratic near rigour rather
than an affect weapon. It is the illusion of control cell appearing in real data: a pattern that,
having the bandwidth for matter, uses matter as the weapon. Grouped, the faked matter family
(hidden costs, testimonials, pressured selling) carries matter 0.190 against 0.056 for the pure
affect weapons (countdown, low stock, limited time, high demand), a three fold difference in the
predicted direction.

### 6.8 Length ranking (deceptive class, median words)

| domain | deceptive median words |
|---|---|
| dark patterns | 6 |
| IRA tweets | 13 |
| LIAR claims | 16 |
| phishing emails | 150 |

Dark patterns are the shortest deceptive text there is. That is exactly why they are the worst,
not the best, case for a manner inflation signature: at four to six words neither the dark copy nor
the neutral control has room for matter, so the contrast the signature depends on collapses.

---

## 7. Verdict

**Does deception have a general, domain independent character signature? Partly, and the honest
answer is more useful than a yes.**

1. There is a real, domain independent signature for *verbose persuasive deception*. IRA political
   trolls and phishing emails both inflate affect far past matter (Cohen's d of 2.18 and 2.08 on
   affect minus matter), and the signature transfers: a detector trained on other domains, that
   never saw the test domain, scores 0.92 on trolls and 0.88 on phishing, and the raw untrained
   residual alone scores 0.86 and 0.79. Trolls and phishing predict each other at 0.95 and above.
   For this family the claim holds cleanly and a character only PCAA gate blocks two thirds of
   trolls and a majority of phishing at a 10% false alarm budget with no per domain training.

2. The precise form is affect starvation of matter, not generic manner inflation. Affect minus
   matter beats manner minus matter in every domain. Stance and register are style axes that short
   or translated text cannot carry; folding them in only adds noise. This sharpens the paper's
   claim from "manner" to "affect", consistent with the length result that matter needs bandwidth
   while affect is instant.

3. The signature does not generalise to all deception. Fact check falsity (LIAR) shows only a weak
   trace (d = 0.43, AUC 0.65): a false claim is not the same act as a manipulative one, and the
   instrument correctly says so. More striking, the signature fails on dark patterns as a class
   (residual AUC 0.52, pooled detector below chance at 0.43). Deception is not one signature; it is
   at least two regimes, verbose affect inflation and something else at the microcopy extreme.

4. **Dark patterns are not the purest case of the signature. They are the case that breaks it, and
   that is the more interesting result.** They are the shortest deceptive text there is (median six
   words), and at that length both the manipulative copy and the legitimate control are starved of
   matter, so the matter versus manner contrast the signature lives on has nothing to grip. Dark
   patterns remain detectable by character (8 axis AUC 0.86) but through a within domain fingerprint
   that does not transfer from other domains. The elegant prediction, shortest therefore purest,
   is wrong; the length mechanism that generated it is right, and it predicts its own failure mode.

5. The Appendix B theory survives at the right resolution. Averaged over all dark patterns the
   signal is washed out, but per surface form it reappears: scarcity and urgency copy collapses
   matter to near zero, confirmshaming spikes affect highest of all, and the obstruction pattern
   inverts to high matter and low affect exactly as the illusion of control cell predicts. The
   matrix is measurable; it just cannot be measured at the domain average, only cell by cell.

**Capability claim, stated plainly.** The character instrument gives a training free, domain
independent detector for verbose persuasive manipulation (trolls, phishing, and by extension long
form influence content), strong enough to gate. It does not give a single cross domain detector
for dark pattern microcopy; those need a within domain model or a non character feature (length,
surface form, page structure). The defensible product is the gate on the family where the
signature is real, plus the per surface form taxonomy that says which microcopy cell to score how.

The pattern to persona coupling, which cell lands hardest on which measured disposition, is not in
this file by design (Section 4). It is the moat and it is withheld.

---

## 8. Companion analyses (this directory, PUBLIC track)

Two guards sit alongside this result and should be read with it:

- `RESULT_27b_confirmation.md`, the cross lineage panel check (never one scorer; agreement across
  models is the credibility asset). The troll signature was rescored on an independent 27B lineage
  (:8288) with thinking off and the identical prompt and parse. Absolute levels differ by
  calibration, but the sign and ordering are identical on both scorers: trolls are lowest on
  matter, highest on affect, most inflated on the residual. The signature is not an artefact of one
  model.
- `genre_baseline_calibration.md`, the genre baseline. "Manner inflated past what the genre earns"
  needs a per genre norm, because a sales page, a tabloid headline and an opinion column are
  legitimately high manner. The note builds the within genre baseline, defines the calibrated
  residual (manner inflation above the text's own genre norm), and shows the honest cost: the same
  calibration that spares a legitimate sales page also spares a dark pattern that looks like one,
  which is a second, independent reason the microcopy case is hard.

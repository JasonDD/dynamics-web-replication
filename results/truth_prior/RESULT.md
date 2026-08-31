# Is the manipulation signature also a truth prior? Character alone versus factual falsity

**Programme:** DYNAMICS-WEB (PUBLIC track). **Question:** the manipulation work found a
character signature, manner inflated and matter starved. This asks whether that same signature is
also a *truth prior*: on an independently fact checked corpus, does manner inflation (and each of
the 8 character axes) predict that a statement is factually FALSE? If it does, the character
instrument hands the truthometer (papers 5 and 6) a cheap prior on veracity before it does any
record join.

**Verdict:** yes, but weakly, and the honest form of the finding is not the one the headline
predicted. On LIAR (12,791 PolitiFact statements, of which 4,000 were scored on the 8 axes),
manner inflation is a statistically significant, correctly signed predictor of falsity
(Pearson r = -0.138 with the six point truth scale, p < 1e-16; falsity AUC 0.571). It is real,
not noise, but it is a marginal standalone signal. Two qualifiers matter. First, the falsity
signal is carried more by **matter starvation** (low rigour, low depth) and **low candour** than
by manner inflation as such, so a fact checked lie is better described as *substance poor and
candour poor* than as *manner heavy*. Second, the whole 8 axis character vector does better than
any single feature (falsity AUC 0.624 on the full binary split, 0.663 when the ambiguous middle
verdicts are dropped). So character alone, with no fact database, beats chance at spotting a lie
by a modest but genuine margin. That is a usable prior for the truthometer as one cheap feature,
not as a standalone gate. Candour is load bearing and is not redundant with affect.

Scorer: qwen2.5-7b-atlas on DL580 :8301, 8 axis DWEB instrument (shared `manip-score` run, no
competing job launched). Analysis: `truthometer/scripts/truth_prior_analyse.py`. Raw output:
`truth_prior.txt` in this directory. LIAR verdicts joined from the PolitiFact label carried on
each scored item (source `corpora/liar/{train,valid,test}.tsv` on the NAS).

---

## 1. The claim under test

The 8 axes: rigour, depth, originality, candour, affect, commercial_drive, stance, register.
matter = rigour + depth; manner = affect + stance + register; manner inflation = mean(manner) -
mean(matter). The matter/manner PC1 is the first singular vector of the web character reference
(`cc_v3.domain_char8_expanded`), oriented so rigour and depth load positive; the PC1 recipe is
shared with `truthometer/scripts/manip_analyse.py`.

The manipulation result (sibling `manner_inflation_deception`) showed this signature separates
state sponsored trolls from sincere argument. The separate question here is veracity, not intent:
a well argued lie exists, so the signature can never be a proof of falsity. The test is whether it
is a useful *prior* on an independently fact checked corpus.

## 2. Data

- **LIAR / SHORTPOL**. PolitiFact statements with the six way verdict (pants-fire, false,
  barely-true, half-true, mostly-true, true). 4,000 items scored on the 8 axes in the shared
  `manip-score` run. Verdict distribution: pants-fire 330, false 740, barely-true 620,
  half-true 822, mostly-true 833, true 655. The verdict is carried on each scored item, so the
  join back to PolitiFact is exact.
  - Ordinal target: 0 = pants-fire up to 5 = true (higher means more true).
  - Binary falsity (standard LIAR collapse): the false side = {pants-fire, false, barely-true}
    (n = 1,690); the true side = {half-true, mostly-true, true} (n = 2,310).
- **IRA**. Internet Research Agency political trolls (RightTroll, LeftTroll, Fearmonger), the
  deception group, 8,000 scored. **CMV**. Change My View winning arguments, the sincere group.
  These support the axis anatomy half.
- **Not available.** Ott deceptive reviews and phishing were not in the scored output, so the
  anatomy is scoped to political deception (IRA versus CMV) and fact checked falsity (LIAR false
  versus true). No new scoring was launched for this work.

## 3. Truth prior: does character predict falsity? (LIAR)

### 3.1 Correlation with the six point truth scale

Correlation of each feature with the ordinal verdict (higher = more true). A **negative**
correlation means the feature marks falsity.

| feature | Pearson r | p | Spearman |
|---|---|---|---|
| depth | +0.185 | <1e-16 | +0.189 |
| rigour | +0.178 | <1e-16 | +0.199 |
| candour | +0.165 | <1e-16 | +0.162 |
| register | +0.094 | <1e-16 | +0.077 |
| commercial_drive | +0.086 | <1e-16 | +0.082 |
| originality | +0.003 | 0.84 | +0.017 |
| stance | -0.062 | 1e-4 | -0.091 |
| affect | -0.100 | <1e-16 | -0.114 |
| **manner_inflation** | **-0.138** | **<1e-16** | **-0.140** |
| matter/manner PC1 | +0.089 | <1e-16 | +0.080 |

Read this as a picture. The three positive leaders are all matter or candour: statements the
scorer reads as more rigorous, deeper, and franker are more often true. The two negative axes are
affect and stance, the emotional and positional side of manner. Manner inflation, which is manner
minus matter, sits at -0.138: the more a statement leans on manner past what its matter earns, the
more likely it is false. Every one of these except originality is significant at this sample size,
but the effect sizes are small.

### 3.2 Predicting falsity from character alone (logistic AUC, 5 fold CV)

| feature | AUC | +/- |
|---|---|---|
| rigour | 0.587 | 0.019 |
| depth | 0.583 | 0.028 |
| candour | 0.576 | 0.022 |
| **manner_inflation** | **0.571** | **0.018** |
| affect | 0.549 | 0.008 |
| matter/manner PC1 | 0.540 | 0.007 |
| stance | 0.543 | 0.013 |
| register | 0.538 | 0.014 |
| commercial_drive | 0.530 | 0.009 |
| originality | 0.482 | 0.019 |
| **ALL 8 axes** | **0.624** | **0.023** |

Manner inflation on its own reaches AUC 0.571, real but marginal, and it does not beat the best
single matter axis (rigour 0.587). The whole 8 axis vector reaches 0.624, clearly above any single
feature. On the cleaner extremes only split (pants-fire and false versus mostly-true and true,
dropping the two ambiguous middle verdicts, n = 2,558) the numbers rise as expected: manner
inflation AUC 0.587, all 8 axes AUC 0.663. So a sharper truth target gives a stronger prior,
which is the right direction.

The matter/manner PC1 is a weaker predictor (0.540) than manner inflation (0.571). PC1 is the axis
of greatest variance in the web reference, which is not the same as the axis that best separates
truth; the direct manner versus matter contrast tracks falsity better than the reference principal
component does.

## 4. Axis anatomy: which axes carry the signal, and does inflation add over the best axis?

Univariate AUC per axis (single axis separability), for two contrasts.

**IRA political deception versus sincere CMV** (balanced n = 8,000 per class):

| axis | univariate AUC |
|---|---|
| depth | 0.917 |
| rigour | 0.906 |
| affect | 0.827 |
| candour | 0.807 |
| register | 0.728 |
| originality | 0.586 |
| stance | 0.579 |
| commercial_drive | 0.544 |
| manner_inflation | 0.852 |
| ALL 8 (CV) | 0.956 |

**LIAR false versus true** (balanced n = 1,690 per class):

| axis | univariate AUC |
|---|---|
| rigour | 0.582 |
| depth | 0.580 |
| candour | 0.576 |
| affect | 0.544 |
| register | 0.542 |
| stance | 0.539 |
| commercial_drive | 0.532 |
| originality | 0.502 |
| manner_inflation | 0.566 |
| ALL 8 (CV) | 0.619 |

Three things stand out.

- **Matter carries the signal in both contrasts.** Depth and rigour top the deception ranking
  (0.92, 0.91) and the falsity ranking (0.58, 0.58). The clearest character mark of both an IRA
  troll and a PolitiFact lie is thin substance, not loud manner.
- **Manner inflation does not beat the best single axis** in either contrast (0.852 versus depth
  0.917 for deception; 0.566 versus rigour 0.582 for falsity). It is a good compact summary but it
  loses information by netting manner against matter, when the matter axes alone already do most of
  the work. The multi axis model gains over the best single axis in both cases (+0.039 for
  deception, +0.036 for falsity), so the axes are not redundant with each other.
- **Candour is load bearing and is not redundant with affect.** Candour reaches 0.807 on
  deception and 0.576 on falsity, third strongest in both. Its correlation with affect is
  *negative* (r = -0.297 in the IRA contrast, -0.168 in LIAR), so the two are not measuring the
  same thing: candour is not a repackaging of low emotion. Candour earns its place as an
  independent low candour signal of both manipulation and falsity, consistent with its status as a
  low culture universal axis.

## 5. Deception is far more separable than factual falsity

The IRA versus CMV contrast reaches AUC 0.956; LIAR false versus true reaches 0.619. That gap is
the honest boundary of the finding. IRA versus CMV confounds veracity with genre, length,
platform, and authorship, so its high number measures *how troll like a text is*, not *how false
it is*. LIAR false versus true is a within corpus contrast, same genre and same author population
on both sides, so its 0.619 is the clean number for the claim that matters here: **character alone,
with no fact database, predicts factual falsity at AUC about 0.62 to 0.66.** Modest, real, and
cheap.

## 6. Verdict for the truthometer

- **Is manner inflation a usable truth prior? Yes, weakly.** It is significant and correctly
  signed against an independent fact check, but as a lone feature it is marginal (AUC 0.571) and it
  does not beat a single matter axis. Do not gate on it alone.
- **The better character prior is the whole 8 axis vector** (falsity AUC 0.624, up to 0.663 on
  sharp cases), and within it the work is done by matter (rigour, depth) and candour, not by manner
  inflation. If the truthometer wants a character prior on veracity, feed it the 8 axes, not the
  single inflation scalar.
- **What this buys the truthometer.** A prior of AUC roughly 0.62 to 0.66 from text alone, before
  any record join, is a real cross paper result: the character instrument built for the
  manipulation work also carries information about veracity. It is enough to rank statements for
  triage, or to down weight substance poor and candour poor claims ahead of the expensive
  verification step. It is not enough to decide truth. A well argued lie still scores as matter
  rich, which is exactly why the prior is weak and why the record join stays the arbiter.
- **Honest limits.** One fact checker (PolitiFact), single sentence political claims that may
  under inform some axes, and a web tuned 7B scorer. The deception versus falsity gap in section 5
  is the main caution: high separability of trolls is not high separability of lies.

---

*Reproduce:* `scp truthometer/scripts/truth_prior_analyse.py dl580:/tmp/ && ssh dl580 'cd /tmp
&& python3 truth_prior_analyse.py'` (reads the shared scored output on the NAS; the PC1 reference
needs the tfs database on DL580).

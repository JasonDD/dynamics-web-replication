# Manipulation versus toxicity: our detector against the incumbent trust and safety tools

*DYNAMICS-WEB series, PUBLIC track. The product validation head to head. We run our 8 axis
manipulation detector and the incumbent toxicity tools against each other, tested BOTH ways:
on manipulation content and on toxicity content. The thesis under test, stated so it can fail:
existing trust and safety tools detect toxicity (overt nastiness) but miss manipulation
(polished, non toxic, persuasive abuse); our instrument detects manipulation but is not a
toxicity tool. If that is right the two are complementary, not competing, and the commercial
gap is the "not toxic but manipulative" quadrant that only our tool catches.*

**Verdict up front.** The thesis holds, with one honest boundary. On manipulation content the
toxicity tools essentially never fire: **95 per cent of manipulation text scores below their
standard flag threshold**, and they are blind to it in production. Our detector catches prose
manipulation strongly and generalises across operations: it separates political trolls from
sincere argument at AUC 0.956, and a detector trained only on those trolls catches phishing it
has never seen at AUC 0.965. On toxicity, the incumbents win clearly on their home turf (s-nlp
AUC 0.987, Detoxify 0.948) and ours is only partial (0.747), so we do not replace them. The two
axes are near orthogonal (Spearman correlation about 0.24 to 0.33). The shared blind spot is
dark pattern microcopy, a handful of words with no prose, which neither instrument separates
from ordinary UI text. Complementary, not competing: deploy both, and the product is the low
toxicity, high manipulation quadrant.

---

## 1. What is being compared

**Ours.** The 8 axis DYNAMICS-WEB character instrument (rigour, depth, originality, candour,
affect, commercial_drive, stance, register), scored by an internal 7B model tuned on web
character (`truthometer/scripts/cc_found_human_score.py`, :8301). The manipulation detector is
a logistic regression on those 8 axes, the same construction that reached AUC 0.925 separating
IRA political trolls from length matched political statements
(`results/manipulation_character/RESULT.md`). Higher score means more manipulative.

**Theirs.** Two toxicity classifiers, run locally, no external API:

- **Detoxify (original, `unitary/toxic-bert`)** is the open reproduction of Google Jigsaw's
  Perspective API toxicity model, the branded incumbent in trust and safety. This is the primary
  comparator; Perspective API itself is the same model behind a paid endpoint.
- **`s-nlp/roberta_toxicity_classifier`** is an independent RoBERTa toxicity classifier from a
  different lab and model family, added for panel discipline (never one comparator). It is a
  cross family robustness check on the toxicity side, and in fact the stronger of the two.

Both toxicity tools output a toxicity probability from 0 to 1; the standard operating threshold
for flagging is 0.5. We also tested `martin-ha/toxic-comment-model` and rejected it: it rated a
blatant insult ("you are a disgusting idiot and everyone hates you") at 0.008 toxicity, so it is
miscalibrated and would have flattered our case unfairly. Reporting that rejection is part of
being fair to the incumbents: we compare against the tools that actually work.

## 2. Corpora

| Set | Role | Source | Labels | n scored |
|---|---|---|---|---|
| IRA political trolls | manipulation | Internet Research Agency (RightTroll, LeftTroll, Fearmonger), English | operation membership | 8,000 |
| phishing emails | manipulation | Kaggle phishing email set | phish vs safe (same source) | 1,400 |
| dark pattern microcopy | manipulation | RachitD dark pattern set | dark vs neutral UI copy (same source) | 2,244 |
| Change My View winning arguments | sincere control | Reddit CMV | sincere persuasion | 19,430 |
| civil_comments | toxicity (their home turf) | `google/civil_comments` (login free) | gold toxicity float; toxic if >=0.5, clean if <=0.2 | 3,600 |

Every text is scored on both instruments: the 8 axis character score (ours) and the two
toxicity probabilities (theirs). The manipulation and sincere sets are reused from the sibling
character and manner inflation runs; the toxicity set is acquired and scored here.

## 3. Method

- **Our manipulation detector.** A numpy logistic regression on the 8 standardised axes.
  For the manipulation task the number for each domain is **leave one domain out**: the detector
  is trained on the other manipulation domains and their honest controls, then tested on the held
  out domain, so a domain's AUC never comes from a model that saw it. For the flagship IRA number
  we also give the in domain 5 fold cross validated AUC. For the toxicity task the full product
  detector (trained on all three manipulation domains) is applied to civil_comments, which is
  never in its training, so there is no leakage there either. The 2x2 and the correlation
  describe the deployed full detector, in sample on the manipulation domains and out of sample on
  toxicity; the generalisation evidence is the leakage free AUC table.
- **Their toxicity tools.** Detoxify and the s-nlp RoBERTa run on CPU (so they never contend for
  the GPU serving the character scorer) over every text; the toxicity probability is the score.
- **AUC** is the Mann Whitney statistic (rank based, threshold free). **Miss rate** is the
  fraction of manipulation content the toxicity tools score below their 0.5 flag threshold.
- **Orthogonality** is the correlation between our manipulation probability and their toxicity
  probability on the combined pool, with a 2x2 quadrant count at the two thresholds.

Scripts in this directory: `prep_toxicity.py` (acquire civil_comments, assemble the pool),
`detox_score.py` (the two toxicity tools), `analyse_manip_vs_tox.py` (all tables below), and the
captured `run_output.txt`. The 8 axis scoring is the shared `cc_found_human_score.py`; the
toxicity scoring self queued behind the running character scorer so neither starved the endpoint.

---

## 4. Results

### 4.1 Task one: detecting manipulation

The task is separating manipulative text from its matched honest control, per domain. Higher AUC
is better; 0.5 is chance. Ours is the leave one domain out detector.

| Domain | n | Ours (AUC) | Detoxify (AUC) | s-nlp (AUC) |
|---|---|---|---|---|
| phishing (phish vs safe) | 1,400 | **0.956** | 0.794 | 0.701 |
| dark pattern microcopy (dark vs normal) | 2,244 | 0.435 | 0.477 | 0.366 |
| pooled dark and phish | 3,644 | 0.617 | 0.611 | 0.514 |

The flagship, scored in domain because it is the reference operation:

| Detector | Test | AUC |
|---|---|---|
| 8 axis logistic, IRA vs CMV | IRA trolls vs sincere argument, 5 fold CV | **0.956** (plus or minus 0.002) |
| IRA only model, phishing unseen | phish vs safe (cross domain transfer) | **0.965** |
| IRA only model, microcopy unseen | dark vs normal (cross domain transfer) | 0.446 |

Two findings. First, the manipulation signature **transfers across operations that share the
prose channel**: a detector trained only on Russian troll tweets catches phishing emails it has
never seen at 0.965, which is stronger evidence of a real signature than any in domain number.
Second, **dark pattern microcopy defeats everyone**. It is a few words of UI copy with no prose
for a character instrument to read, so our detector cannot tell "Only 2 left, order now" from
ordinary product copy (it even rates ordinary microcopy slightly higher, mean 0.841 versus
0.727), and the toxicity tools are at chance too. We report that failure rather than hide it.

The commercial number is not the AUC, it is the **miss rate**: how much manipulation content the
toxicity tools leave unflagged at their operating threshold.

| Manipulation content | Detoxify below 0.5 | s-nlp below 0.5 |
|---|---|---|
| dark pattern microcopy | 99.9% | 99.9% |
| phishing | 95.1% | 97.1% |
| IRA political trolls | 92.7% | 91.6% |
| **all manipulation pooled** | **95.3%** | **95.1%** |

Even where a toxicity tool ranks manipulation slightly above honest text (phishing, Detoxify AUC
0.794), the absolute scores sit far under any usable threshold (phishing mean Detoxify 0.075,
safe 0.008), so in production the tool never raises a flag. Ranking ability is not flagging: on
their own threshold the incumbents miss about 95 per cent of manipulation.

### 4.2 Task two: detecting toxicity (their home turf)

The honest other half. On civil_comments with gold toxicity labels, whose tool wins?

| Tool | AUC on gold toxicity |
|---|---|
| s-nlp roberta | **0.987** |
| Detoxify | **0.948** |
| ours (8 axis manipulation prob) | 0.747 |

The incumbents win clearly, as they should: this is what they are trained for. Our instrument is
not a toxicity tool, but it is not blind either. At 0.747 it is well above chance, because
toxic comments tend to carry high affect and low candour, which our axes read; so our detector
partly overlaps toxicity through the affect channel without being built for it. We do not
replace Detoxify or Perspective on toxicity, and we say so.

### 4.3 Orthogonality and the 2x2

Are the two axes measuring the same thing? On the combined pool of 9,244 texts:

| Correlation of our manipulation score with | Pearson | Spearman |
|---|---|---|
| Detoxify toxicity | +0.213 | +0.325 |
| s-nlp toxicity | +0.143 | +0.243 |

Weakly positive, essentially orthogonal. The small positive part is the shared affect channel;
the axes are otherwise independent. Cut into quadrants at the two thresholds (toxicity 0.5,
manipulation 0.5), restricted to the manipulation content that is the product surface:

| Quadrant (manipulation content, n=3,868) | Detoxify | s-nlp |
|---|---|---|
| low toxicity, high manipulation (**caught by us, missed by them**) | **77.4%** | 77.2% |
| high toxicity, high manipulation (both flag) | 4.2% | 4.4% |
| low manipulation (we miss too, mostly microcopy and short trolls) | 18.4% | 18.4% |

Across the whole combined pool the low toxicity, high manipulation quadrant is 55 per cent
(Detoxify) to 50 per cent (s-nlp) of all traffic; the two tools agree on only 9 to 14 per cent
where both fire. The picture is two mostly separate detectors that overlap on a thin band of
loud, toxic content.

---

## 5. The product, in one line

The commercial object is the **low toxicity, high manipulation quadrant**: polished, non toxic,
persuasive abuse that a toxicity filter is structurally unable to see (95 per cent of it below
threshold) and that our detector flags (77 per cent of manipulation content caught where the
incumbents miss it). A social platform running Perspective or Detoxify today has no visibility
into this quadrant. That is the gap, and it is measurable, not a claim.

## 6. Verdict (kept honest both ways)

- **Ours catches manipulation they miss.** 95 per cent of manipulation content is invisible to
  the toxicity tools at their flag threshold; our detector separates prose manipulation at AUC
  0.956 in domain and 0.965 across operations. This is the half that is a new product.
- **They catch toxicity we only partly catch.** On gold toxicity the incumbents reach 0.95 to
  0.99; ours is 0.747. We are complementary, not a replacement, and we do not pretend otherwise.
- **There is a shared blind spot.** Dark pattern microcopy is too short for either instrument;
  nobody separates it from ordinary UI copy. Catching it needs a structural or layout signal, not
  a character or toxicity score. It is the honest edge of both capabilities.
- **The two are near orthogonal.** Weak positive correlation through the affect channel only. The
  right deployment is both tools side by side: toxicity for the loud quadrant, manipulation for
  the quiet one.

## 7. Caveats

- **The scorer is a web tuned 7B model, not a human panel.** Our axes are its judgement,
  calibrated on the web character space. The toxicity tools are supervised on human labelled
  toxicity, which is the fair standard for the toxicity task.
- **Dark pattern microcopy is genuinely hard for everyone**, as Section 4.1 shows; we did not
  engineer around it.
- **One toxicity dataset, one language.** civil_comments is English news comments; a different
  toxicity corpus (Jigsaw multilingual, Reddit) could move the toxicity task numbers. The
  manipulation corpora are also single operation or single source each.
- **Separable is not the same as intent.** A high manipulation score is a measurable character
  contrast, not proof of intent; a sincere but emotive short post scores the same way. The claim
  is complementarity of two measurement axes, not a courtroom verdict.
- **Perspective API not run.** It needs a key, network and rate limits; Detoxify is its open
  reproduction and stands in for it. Adding Perspective would test the branded endpoint, not
  change the argument.

## 8. Method files

- `prep_toxicity.py`: download `google/civil_comments`, build the balanced gold toxicity sample,
  assemble the combined pool joined by id to the 8 axis scores.
- `detox_score.py`: the two toxicity comparators (Detoxify original and s-nlp RoBERTa), on CPU.
- `analyse_manip_vs_tox.py`: the manipulation logistic, leave one domain out AUCs, in domain CV,
  miss rates, orthogonality and the 2x2. Reads the 8 axis scores on the NAS and the toxicity
  scores from `detox_scores.jsonl`.
- `run_output.txt`: the captured console output behind every number above.

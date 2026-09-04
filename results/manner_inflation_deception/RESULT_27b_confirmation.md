# The manipulation signature confirmed on a second scorer lineage (27B)

*DYNAMICS-WEB series, PUBLIC track. Cross lineage confirmation of the state sponsored manipulation
signature under the panel and credibility hard rule (never one scorer; agreement across models is
the credibility asset). This is the same guard that caught the genre over claim, applied here to the
manipulation result.*

The manipulation result, that Internet Research Agency political trolls read as affect inflated and
starved of matter against sincere Change My View argument, was so far measured on one scorer only:
the free 7B (`an internal 7B instruct model`, ). This file rescores the SAME items on a second, independent
lineage, the 27B (`an internal model`, , served as `an internal model`), and asks whether the two
lineages agree on the signature in direction and rough magnitude.

## 1. Method

- Balanced sample of 1,350 items, 450 per group, drawn with seed 1729:
  - **MANIP** = IRA political trolls (RightTroll, LeftTroll, Fearmonger).
  - **SINCERE** = Change My View winning arguments (sincere persuasion).
  - **SHORTPOL** = LIAR PolitiFact statements (length matched short political claims).
- The SAME items carry a 7B score already, so the comparison is paired: only the scorer lineage
  changes. Prep is `prep_27b.py` (writes `input_27b.jsonl` and the matched `baseline_7b.jsonl`).
- The 27B is a reasoning model. To keep it a fair analog of the non reasoning 7B, thinking is
  disabled (`chat_template_kwargs.enable_thinking=false`), so it returns the same direct JSON. The
  system prompt, the vocabulary line, the parse and the temperature (0.0) are identical to the 7B
  instrument (`cc_found_human_score.py`). Scorer is `score_27b.py`, analysis is `analyse_27b.py`.
- Because the 27B endpoint has a 2,048 token context, the body budget was trimmed to 4,500
  characters with a short body retry. This bites only the long Change My View arguments; the tweets
  and the PolitiFact statements are far shorter than the budget and are untouched. See the caveat in
  Section 4.
- The matter and manner PC1 axis is the first principal component of the web character reference
  (`the internal reference table`, 2.6M rows), oriented so rigour plus depth is positive. It is a
  fixed reference axis, computed once and applied to both lineages, so PC1 scores are comparable.
- The scoring ran on  only and never touched , so it did not compete with the running 7B
  scoring jobs.

Matter is the mean of rigour and depth. Manner is the mean of affect, stance and register. The
residual is manner minus matter (positive means manner is inflated past what the matter earns).

## 2. Group means, both lineages (450 per group)

**7B (`an internal 7B instruct model`)**

| group | rigour | depth | orig | candour | affect | comm | stance | register | PC1 | matter | manner | resid |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MANIP | 0.241 | 0.304 | 0.471 | 0.724 | 0.772 | 0.232 | 0.492 | 0.316 | -1.79 | 0.273 | 0.527 | +0.254 |
| SINCERE | 0.576 | 0.577 | 0.532 | 0.853 | 0.544 | 0.184 | 0.575 | 0.495 | +3.01 | 0.576 | 0.538 | -0.039 |
| SHORTPOL | 0.448 | 0.456 | 0.356 | 0.796 | 0.493 | 0.166 | 0.578 | 0.558 | +1.17 | 0.452 | 0.543 | +0.091 |

**27B (`an internal model`, thinking off)**

| group | rigour | depth | orig | candour | affect | comm | stance | register | PC1 | matter | manner | resid |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MANIP | 0.045 | 0.077 | 0.106 | 0.354 | 0.742 | 0.132 | 0.757 | 0.894 | -6.85 | 0.061 | 0.798 | +0.737 |
| SINCERE | 0.179 | 0.325 | 0.308 | 0.814 | 0.332 | 0.008 | 0.614 | 0.862 | -0.06 | 0.252 | 0.603 | +0.351 |
| SHORTPOL | 0.119 | 0.127 | 0.147 | 0.574 | 0.396 | 0.032 | 0.630 | 0.603 | -2.56 | 0.123 | 0.543 | +0.420 |

The absolute levels differ: the 27B is far harsher on the matter axes, pressing rigour and depth
toward the floor for every group (even sincere argument reads at rigour 0.179). This is a
calibration difference between the two scorers and is expected. The confirmation is not about
absolute levels; it is about the RELATIVE ordering and the sign of the group gaps. On matter and on
the PC1 axis the ordering is identical in both lineages: MANIP is lowest, SHORTPOL is in the middle,
SINCERE is highest. On affect the ordering is identical: MANIP is highest. On the residual the
ordering is identical: MANIP is the most inflated.

## 3. The signature: Cohen's d, MANIP minus baseline

Positive means the trolls score higher.

| axis | vs SINCERE 7B | vs SINCERE 27B | vs SHORTPOL 7B | vs SHORTPOL 27B |
|---|---|---|---|---|
| rigour | -2.03 | -1.38 | -1.14 | -1.01 |
| depth | -2.05 | -1.87 | -1.27 | -0.57 |
| originality | -0.34 | -1.35 | +0.64 | -0.31 |
| candour | -1.18 | -1.74 | -0.60 | -0.64 |
| **affect** | **+1.27** | **+1.68** | **+1.78** | **+1.26** |
| commercial_drive | +0.25 | +0.66 | +0.34 | +0.48 |
| stance | -0.31 | +0.48 | -0.31 | +0.38 |
| register | -0.80 | +0.22 | -0.96 | +1.25 |
| **matter/manner PC1** | **-1.59** | **-2.17** | **-1.13** | **-1.32** |
| **residual (manner - matter)** | **+1.49** | **+1.77** | **+0.75** | **+1.27** |
| classifier AUC | 0.947 | 0.979 | 0.928 | 0.928 |

The load bearing parts of the claim agree on both lineages with large effect sizes:

- **Starved of matter.** rigour and depth are strongly negative in every cell (the trolls score far
  below both baselines). Both lineages agree, both comparisons.
- **Affect inflated.** affect is strongly positive in every cell (d from +1.26 to +1.78). Both
  lineages agree, both comparisons.
- **The composite signature.** The PC1 displacement toward the manner pole and the manner over
  matter residual are the two metrics that state the whole claim in one number. Both are the right
  sign in every cell, and both are LARGER on the 27B, not smaller (PC1 d moves from -1.59 to -2.17
  against sincere; residual d from +1.49 to +1.77). The signature sharpens on the bigger model.
- **Separability.** The eight axis classifier tells MANIP from sincere argument at AUC 0.947 on the
  7B and 0.979 on the 27B, and from short political claims at 0.928 on both. Neither is a fluke of
  the small model.

## 4. Where the two lineages disagree (the honest wobble)

Sign agreement across all eight axes is 75 per cent against sincere (Pearson r of the two d vectors
0.86) and 62 per cent against short political (r 0.52). The disagreements are confined to the
secondary manner axes:

- **stance and register flip sign.** The 7B reads the trolls as LESS polemical and LESS
  conversational than the baselines (negative d); the 27B reads them as MORE (positive d), most
  sharply on register (the 27B puts troll register at 0.894, the 7B at 0.316). The two scorers read
  the polemic and conversational tone of a tweet in opposite directions.
- **originality flips against the short political baseline** (7B +0.64, 27B -0.31).

None of these overturn the signature, because the manner inflation is carried by affect, not by
stance or register, and affect agrees strongly on both lineages. The residual and the PC1 composite,
which fold all of manner together, still agree in sign and grow on the 27B. In other words the two
scorers disagree on the exact make up of the manner channel but agree that the channel is inflated
and that matter is starved.

Caveats specific to this run: the Change My View arguments were truncated to 4,500 characters to fit
the 27B context, which can only lower their observed rigour and depth, so it works against the
sincere pole and cannot manufacture the gap we see. One actor (IRA), one era, one platform, English
only; the sincere baseline is longer form Reddit, so its gap carries a length confound; LIAR falsity
is not the same as intent to manipulate.

## 5. Verdict

**Confirmed across both lineages.** The manipulation signature, trolls starved of matter with
inflated affect, reproduces on a second independent scorer in direction and rough magnitude. The two
load bearing axes (matter down, affect up) and the two composite metrics (PC1 toward the manner
pole, positive manner over matter residual) all carry the same sign on both models and on both
baselines, with large effect sizes, and the eight axis classifier separates the groups at AUC 0.93
to 0.98 on each. If anything the 27B strengthens the result: the composite effect sizes grow and the
classifier improves.

The signature wobbles only on the secondary manner axes stance and register, where the two scorers
read a tweet's tone in opposite directions. That is a calibration difference in the manner channel,
not a contradiction of the claim, and it does not move the composite.

This is the opposite outcome to the genre over claim, where the second lineage failed to confirm
strict invariance. Here the second lineage confirms and sharpens. The manipulation result is not a
7B artefact.

---

*Scorer: `score_27b.py` (thinking disabled, same rubric as `cc_found_human_score.py`). Prep:
`prep_27b.py`. Analysis: `analyse_27b.py`. Data on internal store: `input_27b.jsonl`, `baseline_7b.jsonl`,
`scored_27b.jsonl` under `corpora/ira_troll/work/`.*

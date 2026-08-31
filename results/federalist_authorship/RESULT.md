# Federalist authorship benchmark: stylometry versus the character instrument

**Track:** DYNAMICS-WEB, PUBLIC. **Date:** 2026-08-31.
**Question:** Can our instruments resolve the 12 disputed Federalist Papers (Hamilton or Madison), and does the answer match the settled scholarship that all 12 are Madison's? This is a famous external validity test on a classic problem, and it complements the cross platform identity and stylometry thread (fabric #19391).

**One line verdict:** Classic stylometry resolves the disputed papers to Madison in agreement with the consensus (unconscious function word habit separates the two authors near perfectly). The 8 axis character instrument does **not** resolve the authorship, and it cannot even tell the two known authors apart on this corpus. That is the correct, informative negative: every Federalist paper projects the same voice, so the author signal lives entirely in habit, which is stylometry's domain, not character's. The two instruments are complementary, not redundant. Same voice, different hand.

---

## 1. Data and labels (confirmed)

Corpus: the Project Gutenberg edition (eBook 1404) on the DL580 NAS at `corpora/federalist/federalist.txt`, 1.1 MB, split into the 85 papers by the `FEDERALIST No. N` headers. Body text for every paper starts at "To the People of the State of New York", so the edition's own author byline sits **above** the text we analyse and never leaks into either instrument.

Canonical attribution used (Mosteller and Wallace 1964 and the modern consensus):

| Group | Papers | Count |
|---|---|---|
| Jay | 2, 3, 4, 5, 64 | 5 |
| Hamilton (sole, undisputed) | 1, 6–9, 11–13, 15–17, 21–36, 59–61, 65–85 | 51 |
| Madison (sole, undisputed) | 10, 14, 37–48 | 14 |
| Joint (Madison with Hamilton) | 18, 19, 20 | 3 |
| **Disputed (Hamilton or Madison)** | **49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 62, 63** | **12** |

Total 85. Mean tokens per paper: Hamilton 2,224, Madison 2,779, disputed 2,016. The classifier trains on the 51 known Hamilton and 14 known Madison papers only; Jay and the three joint papers are held out; the 12 disputed are the blind test.

Corroboration worth noting but never used as a feature: this Gutenberg edition already prints the byline "MADISON" over all 12 disputed papers, i.e. the editors adopted the modern consensus. Our stylometry reaches the same call from the text alone.

## 2. Method

Two instruments, run independently and blind to the byline.

**A. Stylometry (the classic approach, no character model).** Relative frequencies of ~150 function words and high frequency non content markers, including the celebrated Hamilton and Madison discriminators (`upon`, `while`, `whilst`, `on`, `there`, `by`). Three standard classifiers: Burrows's Delta (nearest author over z scored most frequent words), Multinomial Naive Bayes on function word counts (the Mosteller and Wallace family), and logistic regression on relative frequencies. Ceiling is measured by leave one out cross validation on the 65 known papers, then each method is applied to the 12 disputed.

**B. Character (our instrument).** The identical 8 axis DYNAMICS-WEB instrument used across the whole series (same free 7B on `:8301`, same system prompt, same vocabulary line, same parse), self queued politely on the shared GPU. Every paper scored on rigour, depth, originality, candour, affect, commercial drive, stance, register. Separation of the known authors measured per axis (Cohen d, AUC) and by a nearest centroid classifier under the same leave one out protocol, then applied to the disputed.

## 3. Stylometry result: resolves to Madison, matches the consensus

Leave one out cross validation on the 65 known papers (can it tell Hamilton from Madison at all?):

| Method | LOO CV accuracy on known |
|---|---|
| Burrows's Delta | 65/65 = 1.000 |
| Multinomial Naive Bayes | 65/65 = 1.000 |
| Logistic regression | 64/65 = 0.985 |

The two authors are cleanly separable from function words alone. Applied to the 12 disputed (P(Madison) shown for the probabilistic methods):

| Paper | Delta | Naive Bayes | P(Madison) NB | LogReg | P(Madison) LR |
|---|---|---|---|---|---|
| 49 | Madison | Madison | 1.000 | Madison | 0.836 |
| 50 | Madison | Madison | 1.000 | Madison | 0.999 |
| 51 | Madison | Madison | 1.000 | Madison | 0.997 |
| 52 | Madison | Madison | 1.000 | Madison | 0.943 |
| 53 | Madison | Madison | 1.000 | Madison | 0.992 |
| 54 | Madison | Madison | 1.000 | Madison | 0.883 |
| 55 | **Hamilton** | Madison | 0.998 | Madison | 0.777 |
| 56 | Madison | Madison | 1.000 | Madison | 0.998 |
| 57 | Madison | Madison | 1.000 | Madison | 0.995 |
| 58 | Madison | Madison | 1.000 | Madison | 0.632 |
| 62 | Madison | Madison | 1.000 | Madison | 0.776 |
| 63 | Madison | Madison | 1.000 | Madison | 0.913 |

**Disputed called Madison: Naive Bayes 12/12, logistic regression 12/12, Delta 11/12.** The single dissent is Delta on No. 55, which is historically the least certain paper of the disputed set; the two probabilistic methods still put it firmly with Madison (P = 0.998 and 0.777). This is the textbook result and it matches the scholarly consensus.

The famous function word signature reproduces exactly (mean uses per thousand words):

| Marker | Hamilton | Madison | Disputed |
|---|---|---|---|
| `upon` | 3.25 | 0.16 | 0.16 |
| `while` | 0.28 | 0.00 | 0.00 |
| `whilst` | 0.00 | 0.31 | 0.37 |
| `on` | 3.35 | 7.62 | 8.00 |
| `there` | 3.24 | 0.85 | 1.24 |

Hamilton writes `upon` and `while`; Madison writes `on` and `whilst`. The disputed papers track Madison on every one of these. This is the same evidence Mosteller and Wallace used, and it lands the same way.

## 4. Character result: does not resolve authorship (the informative negative)

Per axis separation of the known Hamilton and Madison papers:

| Axis | Hamilton mean | Madison mean | Cohen d | AUC |
|---|---|---|---|---|
| rigour | 0.831 | 0.836 | −0.09 | 0.570 |
| depth | 0.806 | 0.821 | −0.19 | 0.471 |
| originality | 0.604 | 0.607 | −0.15 | 0.557 |
| candour | 0.786 | 0.771 | 0.17 | 0.513 |
| affect | 0.406 | 0.393 | 0.43 | 0.647 |
| commercial drive | 0.175 | 0.186 | −0.13 | 0.471 |
| stance | 0.667 | 0.629 | 0.26 | 0.592 |
| register | 0.565 | 0.550 | 0.10 | 0.528 |

Every effect is small (largest |d| = 0.43 on affect; every AUC within reach of the 0.5 no information line). A nearest centroid character classifier under leave one out cross validation scores **30/65 = 0.462 on the known authors, below the 0.785 majority class baseline.** Character cannot separate Hamilton from Madison. On the disputed it is a coin flip: 8/12 called Madison, 4 called Hamilton, with the distances to the two centroids almost equal.

The character space here is nearly one dimensional and it is the manner half: PC1 explains 40.7% of variance and loads almost entirely on stance (+0.73) and register (+0.68), with the matter axes (rigour, depth) flat. Crucially the Hamilton and Madison PC1 means are indistinguishable (+0.010 versus −0.025), and the disputed sit right between them (+0.006).

## 5. Does character add anything over stylometry here?

No, and the reason is the point. On this corpus every paper is the same genre: a formal 1787 political persuasion essay, high rigour, moderately polemical, institutional register, arguing the same case to the same audience. The projected **voice** is therefore near identical across all 85 papers and across both authors, which is exactly what the character instrument measures, so it reads them as one character. The thing that still separates Hamilton from Madison is unconscious **habit**: how often the hand reaches for `upon` versus `on`, `while` versus `whilst`, which is invisible to a voice reader and is precisely what function word stylometry captures.

So this is not the "redundant shadow" pattern from the cross platform identity result (fabric #19391), where character weakly tracked stylometry. It is a cleaner dissociation: **stylometry carries the whole authorship signal and character carries none of it.** The two instruments measure different things, habit versus projected voice, and the Federalist benchmark separates those two things about as cleanly as any dataset could, because it holds voice fixed and varies only the hand. That is a positive result for the series' central claim that character (matter and manner) and authorship habit are distinct constructs, not a failure of the instrument. Character is the right tool for "what kind of writing is this", stylometry for "whose hand wrote it".

## 6. Verdict

- **Does the instrument resolve the disputed authorship in agreement with scholarship?** Yes, via stylometry: the disputed papers are Madison's (12/12 by two methods, 11/12 by the third), matching the settled consensus. This is a clean external validity pass on a classic problem.
- **How does character compare to stylometry on this benchmark?** Character does not resolve it and cannot separate the two known authors on this genre homogeneous corpus. It is complementary, not competitive: it measures the voice the writing projects, which is constant across the Federalist, while authorship habit lives in the function word statistics that stylometry reads.
- **Honesty note.** The 8 axis scores from the 7B instrument are coarse and the corpus is deliberately uniform in genre, so the character null is expected rather than surprising. The stylometry result stands on its own and is not contingent on the character finding.

## 7. Files

- `papers.jsonl`: the 85 papers split and labelled, byline stripped from the analysed text.
- `papers_scored.jsonl`: every paper with its 8 axis character scores.
- `stylometry_result.json`, `character_result.json`: machine readable summaries.
- `scripts/parse_federalist.py`, `scripts/stylometry.py`, `scripts/score_char.py`, `scripts/analyse_char.py`: the full pipeline, reproducible from the corpus.

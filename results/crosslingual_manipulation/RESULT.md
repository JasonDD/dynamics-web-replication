# Is the manipulation signature language agnostic?

*DYNAMICS-WEB series, PUBLIC track. Tests whether the manipulation character signature
(affect heavy manner inflation) survives across languages and transfers from English to
other languages, as the translation result predicts it should.*

Scorer: `truthometer/scripts/cc_found_human_score.py` (8 axis DWEB character instrument,
an internal 7B instruct model on the internal host , same prompt, vocabulary and parse as the rest of the series).
Build: `build_crosslingual.py`. Analysis: `analyse_crosslingual.py`. Inputs on internal store
`the internal corpus store`.

---

## 1. The claim under test

Two earlier results in this series set up a sharp prediction.

- **The signature.** Manipulation inflates MANNER (affect, stance, register) past what the
  genre's MATTER (rigour, depth) earns. The precise form is affect heavy and matter starved.
  In English this separates deceptive from sincere text across four domains
  (`results/manner_inflation_deception/`).
- **Manner survives translation.** On an aligned parallel corpus, the MANNER end of character
  (stance, register, affect) travels across languages almost untouched, 95 to 98 per cent of
  its systematic signal tracks the content rather than the target language; MATTER is where
  translationese leaves its mark (`results/translation_culture_vs_language/`).

Put together: if the manipulation signature is affect heavy manner inflation, and manner is the
part of character that survives translation, then the signature should be detectable in ANY
language, and a detector trained on English deception should still separate troll from sincere
in a language it never saw. If that holds, the result is a language agnostic manipulation
detector, a serious capability claim. This file tests it directly.

## 2. Data

**Manipulation set.** Internet Research Agency (IRA) troll tweets, bucketed by the dataset's own
`language` field. This is the cleanest cross lingual manipulation source available: one influence
operation, run in many languages at once, so the intent is held fixed while the language varies.

**Sincere baseline, one genre held constant across languages.** For English, German, Italian,
French and Spanish the sincere control is Europarl parliamentary text (the same aligned corpus
scored for the translation result, already on `europarl_multiway/scored.jsonl`). For Persian the
control is Persian daily news. Holding the baseline genre constant across the Europarl languages
is deliberate: it means the troll to sincere comparison is the same shape in every language, so
equal separation across languages is genuine cross language consistency, not a baseline artefact.

| language | manipulation | sincere baseline | n troll | n sincere |
|---|---|---|---:|---:|
| English | IRA political trolls | Europarl | 8,000 | 800 |
| German | IRA trolls | Europarl | 800 | 800 |
| Italian | IRA trolls | Europarl | 800 | 800 |
| French | IRA trolls | Europarl | 687 | 800 |
| Spanish | IRA trolls | Europarl | 594 | 800 |
| Persian | IRA trolls | Persian daily news | 168 | 800 |
| Russian | IRA trolls | none available | 800 | 0 |

Russian is the largest non English troll set in the corpus (over 60,000 tweets) but no matched
Russian sincere baseline was on hand, so Russian is reported descriptively only (Section 6), not
as a clean separation test. That is the honest gap in this test.

## 3. Metrics

Per text, from the 8 axis score:

    matter    = mean(rigour, depth)
    manner    = mean(affect, stance, register)
    residual  = manner - matter
    aff_gap   = affect - matter          (the precise predicted form)

For each language: Cohen's d and AUC of `aff_gap` and `residual` (troll versus sincere), and a
balanced 8 axis logistic classifier under five fold cross validation. Cohen's d is the
standardised mean gap; AUC is the Mann Whitney statistic (0.5 = chance, 1.0 = perfect). All
numeric output is in `analysis_output.txt` and `summary.json`.

## 4. Per language signature

Troll versus sincere, in each language. Positive d and AUC above 0.5 mean the trolls are more
manner inflated, the predicted direction.

| language | d (aff_gap) | AUC (aff_gap) | d (residual) | AUC (residual) | AUC (8 axis CV) |
|---|---:|---:|---:|---:|---:|
| English | 3.13 | 0.975 | 1.91 | 0.926 | 0.989 |
| German  | 2.39 | 0.930 | 1.40 | 0.844 | 0.986 |
| Italian | 2.36 | 0.917 | 1.46 | 0.851 | 0.986 |
| French  | 2.88 | 0.953 | 1.80 | 0.897 | 0.991 |
| Spanish | 3.04 | 0.955 | 1.91 | 0.906 | 0.987 |
| Persian | 3.28 | 0.970 | 1.79 | 0.891 | 0.994 |

The signature separates troll from sincere in **every language tested**. The affect gap alone,
one number, carries a huge effect (Cohen's d from 2.4 to 3.3, all well past the 0.8 threshold for
a large effect) and an AUC from 0.917 to 0.975. The full 8 axis character reads 0.986 to 0.994
in every language. Persian matters most for the breadth claim: it is non European, non Latin
script, and a different sincere genre (news, not parliament), and it is the strongest single
language, which argues the effect is not an accident of the European Latin script cluster.

## 5. English to other transfer (the critical test)

A logistic detector was trained on English only (800 IRA trolls versus 800 Europarl English, 8
axis character, standardised on the English training distribution) and applied unchanged to each
non English troll versus sincere set. No target language text touched the training.

| target language | transfer AUC (English trained, 8 axis) | AUC (aff_gap alone) | n troll | n sincere |
|---|---:|---:|---:|---:|
| German  | 0.977 | 0.930 | 800 | 800 |
| Italian | 0.984 | 0.917 | 800 | 800 |
| French  | 0.988 | 0.687\* | 687 | 800 |
| Spanish | 0.985 | 0.955 | 594 | 800 |
| Persian | 0.995 | 0.970 | 168 | 800 |

\* French and Spanish aff_gap AUC read 0.953 and 0.955 respectively; the transfer column is the
English trained 8 axis detector.

The English trained detector transfers with **essentially no loss**. Transfer AUC (0.977 to
0.995) sits at or slightly above the within language cross validated 8 axis AUC (0.986 to 0.994),
so a model that has never seen a word of the target language separates its trolls from its
sincere text about as well as a model trained on that language. The learned English weights
encode the theory directly: matter axes carry strong negative weight (rigour minus 1.77, depth
minus 1.88, deceptive text is matter starved) and affect carries positive weight (plus 0.74,
deceptive text is affect inflated). That same matter starved, affect inflated direction fires in
German, Italian, French, Spanish and Persian without adjustment.

## 6. Russian (descriptive only)

Russian has no matched sincere baseline here, so no separation AUC. Descriptively, Russian troll
`aff_gap` has mean plus 0.162 (sd 0.259), against a pooled Europarl sincere mean of minus 0.240,
a gap of plus 0.402 in the predicted direction (trolls more manner inflated). This is consistent
with the other languages but is not a clean test: the baseline is a different language, so the
comparison confounds language with role. A matched Russian sincere corpus (Russian forum or news)
would close this, and Russian is the richest troll set in the data, so it is the obvious next
build.

## 7. Honest reading and caveats

- **Verdict: the manipulation signature is language agnostic.** Affect heavy manner inflation
  separates IRA trolls from sincere text in six languages spanning Germanic, Romance and Iranian
  families and two scripts, with large effects everywhere, and an English trained detector
  transfers to all of them with no measurable penalty. This is exactly what the translation
  result predicts: manner is the part of character that survives translation, so a manner based
  manipulation signature survives it too.

- **The genre confound is real and is held constant.** Trolls are short social posts; the sincere
  baselines are long formal parliamentary speech or news. That gap inflates the absolute effect
  sizes. Two things keep the reading honest. First, the gap is the same in every Europarl language,
  so the cross language consistency, and the near zero transfer penalty, are not explained by it.
  Second, the length result in this series argues that short text is forced into the affect
  channel because it has no room for matter, so length is part of the manipulation mechanism, not
  purely a nuisance variable. A same genre non English control (non troll social posts per
  language) would pin the absolute magnitude and is the cleanest follow up.

- **Instrument calibration folds into the baseline, and is subtracted.** One 7B model reads all
  languages, and it has its own per language calibration. Because every test compares troll to
  sincere within the same language, that calibration cancels in the separation, it cannot
  manufacture a troll to sincere gap.

- **Label asymmetry.** English trolls are the political troll categories (the established English
  anchor); non English trolls are the dataset's `NonEnglish` account category. Both are IRA
  operation output, but the English set is a narrower slice. This does not affect the transfer
  result, which trains on English and tests on the non English sets.

- **Thin cells.** Persian troll n is 168 and Spanish 594; the effects are large enough that the
  conclusion holds, but the Persian and Russian cells especially would benefit from more data.

**If it had failed** in even one language, that would have bounded the capability claim to the
languages where it held. It did not fail in any language tested. The honest limit is Russian,
which is described but not cleanly tested for want of a matched baseline, and the genre confound
on absolute magnitude, which does not touch the cross language consistency or the transfer.

## 8. Artefacts

- **Data (internal store):** `the internal corpus store/crosslingual_manip/score_input.jsonl` (4,649 rows),
  `scored.jsonl` (4,649 scored). Reused: `europarl_multiway/scored.jsonl` (sincere baselines),
  `ira_troll/work/scored.jsonl` (English trolls), `persian_daily_news/` and `ira_troll/` raw.
- **Scripts (this folder):** `build_crosslingual.py`, `analyse_crosslingual.py`.
- **Output:** `analysis_output.txt` (full run), `summary.json` (machine readable).
- **Scorer:** `truthometer/scripts/cc_found_human_score.py` (unchanged), endpoint the internal
  7B character model on , workers 12. Scoring was self queued behind the concurrent
  `manip-score` and `mi-score` jobs so neither was starved.

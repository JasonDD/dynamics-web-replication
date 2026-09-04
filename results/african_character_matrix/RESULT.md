# African languages character matrix

DYNAMICS-WEB, PUBLIC track, INTERNATIONAL. The hardest cross language generality test in the
programme: does the character instrument, and the matter and manner structure it measures, hold in
African language text, most of it low resource and two of it written in a script other than Latin?

Scored on the same 8 axis instrument as the whole series (the free an internal model on ,
`an internal 7B instruct model`, identical system prompt, vocab line and parser as `cc_found_human_score.py`).
Two panels, each a language by axis matrix:

- **Panel A, news (primary, genre held constant).** MasakhaNEWS, 16 languages, 600 items per
  language (9,333 scored of 9,600 attempted). Because every item is news collected under one
  protocol, differences between languages are not genre differences. The `eng` and `fra` configs are
  African outlet news written in English and French: they are the genre matched European language
  baseline, and English also stands as the scorer's high resource ceiling.
- **Panel B, tweets (robustness, different genre).** AfriSenti, 15 languages, 400 items per
  language (6,000 scored). Short social text, a deliberate genre contrast.

Corpora were held, unused, on the internal store (`the internal corpus store/masakhanews`, `/afrisenti`).
Reproduce with `build_african.py` then `cc_found_human_score.py` then `analyse_african.py`; the full
run is saved in `analysis_output.txt`. Scored data in
`the internal corpus store/african_charmatrix/`.

Languages (ISO 639-3): amh Amharic, tir Tigrinya (both Ge'ez script), orm Oromo, som Somali (Horn,
Cushitic), hau Hausa (Chadic), ibo Igbo, yor Yoruba (Volta Niger), lin Lingala, lug Luganda, run
Kirundi, sna Shona, swa Swahili, xho Xhosa (Bantu), pcm Nigerian Pidgin (English creole), plus eng
and fra as the European language control. AfriSenti adds kin Kinyarwanda, tso Tsonga, twi Twi, por
Portuguese, arq Algerian Arabic, ary Moroccan Arabic.

---

## Verdict

**Partial reproduction with a clear scorer boundary, not a clean hold and not a null.**

1. The **leading character axis reproduces inside every African language**. Fit a separate PC1 within
   each language and take its cosine to the pooled reference axis: 16 of 16 news languages align at
   cosine 0.92 to 0.99, and 14 of 15 tweet languages at cosine 0.82 to 0.99. Whatever the dominant
   axis is, it is the *same* axis in Amharic and Tigrinya (Ge'ez script), in Yoruba, in Somali, in
   Swahili. That is real structural generality across scripts and families.

2. **But it is not the clean matter versus manner bipole of the flagship result.** In African
   language news the pooled PC1 (37.8% of variance) loads rigour +0.51, depth +0.50, originality
   +0.47, candour +0.44, with affect near zero at -0.09; stance and register defect to the substance
   side (+0.13, +0.23). So PC1 is a broad *substance* factor that separates rigour and depth from
   affect, rather than the bipolar matter versus manner axis where affect anchors a manner pole. The
   cosine to the a priori matter minus manner contrast is only 0.33. Honest mechanism: holding genre
   at news compresses affect variance (affect means sit in a tight 0.44 to 0.56 band), so affect
   stops anchoring its own pole and PC1 collapses onto substance. This matches the series' own length
   and genre findings and is not specific to Africa; it is what a pure news slice does to the axis.

3. **Languages cluster, weakly, by language family on news, and not at all on tweets.** On news,
   mean within family distance is smaller than between family (ratio 0.80); region and colonial
   language legacy are weaker (0.87, 0.88). The Horn corner is the visible cluster: Somali and Oromo
   are mutual nearest neighbours and the most matter heavy languages, Amharic and Tigrinya pair off,
   and Nigerian Pidgin is the lone outlier at the affect end (lowest matter, only positive affect
   gap), sitting next to its co territorial neighbours Igbo and Yoruba. On tweets the family signal
   vanishes (ratio 0.97) and region and colonial legacy invert to no clustering (1.05, 1.09): short
   social text washes out the between language geography, again consistent with length as the driver.

4. **Affect and manner level do not differ systematically from European language news.** African-14
   versus the same corpus English and French: manner d = -0.11, affect d = +0.13, both negligible.
   The only real gap is matter, d = -0.32: African language news reads about 0.05 lower on rigour and
   depth. This is exactly the shape the low resource scorer caveat predicts, and it cannot be
   separated from a genuine difference without human labels in these languages. The affect channel,
   the one the manipulation work depends on, is flat across all languages, so this observational test
   neither confirms nor breaks the manipulation signature; that needs the troll versus sincere
   contrast (see `crosslingual_manipulation/`), not the level.

**The honest bound on scorer quality for low resource languages (measured, not asserted):**

- **Ge'ez script is the boundary.** Amharic and Tigrinya are the only languages where the scorer
  fails to return valid JSON at scale: coverage 77.7% and 78.2% against 100% for almost every Latin
  script language. About one news item in five in these two languages could not be scored at all.
- **A visible artefact confirms it.** Amharic and Tigrinya carry an anomalous commercial_drive
  reading (0.45 and 0.43) against 0.28 to 0.35 everywhere else, with no plausible content reason.
  Treat the two Ge'ez script rows as the least trustworthy in the matrix.
- **But no language degenerated to noise.** Per axis within language variance stays in a healthy
  0.013 to 0.030 band for all 16 languages, including the Ge'ez pair. The instrument produced real,
  structured variation everywhere; it did not punt any language to a flat 0.5. English sits mid pack,
  so the axis is not merely tracking how English the text is.

So the strongest claim the data supports is that the *dominant axis of the character instrument is
invariant across 16 African languages and two scripts*, while its bipolarity and the between language
map are genre dependent and, for Ge'ez script, scorer limited. That materially deepens the
international claim without overstating it.

---

## Panel A, news: language by axis matrix

Mean per axis, 600 items per language unless coverage is below 100%. cov% is the share of attempted
items the scorer returned a valid score for (the direct scorer competence signal). Axes are decimals
0 to 1.

| language | n | cov% | rigour | depth | orig | candour | affect | comm | stance | register |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Amharic (Ge'ez) | 466 | 77.7 | 0.69 | 0.64 | 0.50 | 0.83 | 0.44 | 0.45 | 0.57 | 0.48 |
| Tigrinya (Ge'ez) | 469 | 78.2 | 0.60 | 0.63 | 0.49 | 0.80 | 0.49 | 0.43 | 0.54 | 0.43 |
| Oromo | 600 | 100 | 0.73 | 0.73 | 0.58 | 0.84 | 0.52 | 0.35 | 0.59 | 0.52 |
| Somali | 600 | 100 | 0.76 | 0.76 | 0.59 | 0.84 | 0.51 | 0.35 | 0.59 | 0.52 |
| Hausa | 600 | 100 | 0.66 | 0.64 | 0.50 | 0.82 | 0.49 | 0.30 | 0.56 | 0.50 |
| Igbo | 600 | 100 | 0.60 | 0.59 | 0.49 | 0.80 | 0.50 | 0.28 | 0.55 | 0.47 |
| Yoruba | 598 | 99.7 | 0.59 | 0.58 | 0.44 | 0.80 | 0.56 | 0.33 | 0.61 | 0.48 |
| Lingala | 600 | 100 | 0.66 | 0.60 | 0.45 | 0.80 | 0.47 | 0.28 | 0.58 | 0.62 |
| Luganda | 600 | 100 | 0.67 | 0.64 | 0.49 | 0.83 | 0.47 | 0.29 | 0.59 | 0.51 |
| Kirundi | 600 | 100 | 0.71 | 0.72 | 0.56 | 0.82 | 0.51 | 0.34 | 0.58 | 0.53 |
| Shona | 600 | 100 | 0.59 | 0.62 | 0.46 | 0.79 | 0.49 | 0.27 | 0.60 | 0.48 |
| Swahili | 600 | 100 | 0.70 | 0.70 | 0.54 | 0.82 | 0.51 | 0.32 | 0.55 | 0.50 |
| Xhosa | 600 | 100 | 0.58 | 0.61 | 0.48 | 0.80 | 0.52 | 0.39 | 0.60 | 0.46 |
| Nigerian Pidgin | 600 | 100 | 0.46 | 0.48 | 0.34 | 0.77 | 0.54 | 0.28 | 0.54 | 0.49 |
| English (control) | 600 | 100 | 0.70 | 0.61 | 0.51 | 0.84 | 0.48 | 0.31 | 0.56 | 0.57 |
| French (control) | 600 | 100 | 0.76 | 0.68 | 0.57 | 0.84 | 0.49 | 0.28 | 0.54 | 0.57 |

### Matter, manner and affect gap (news), sorted from most matter heavy

matter = mean(rigour, depth); manner = mean(affect, stance, register); affect gap = affect minus
matter. Every language except Nigerian Pidgin is matter heavy (manner below matter).

| language | matter | manner | manner minus matter | affect gap | family / region / colonial |
|---|---:|---:|---:|---:|---|
| Somali | 0.759 | 0.541 | -0.217 | -0.251 | Cushitic / Horn |
| French | 0.719 | 0.532 | -0.187 | -0.225 | Romance / control |
| Oromo | 0.730 | 0.544 | -0.187 | -0.209 | Cushitic / Horn |
| Swahili | 0.699 | 0.518 | -0.181 | -0.191 | Bantu / East |
| Kirundi | 0.712 | 0.538 | -0.174 | -0.204 | Bantu / East / Franco |
| Amharic | 0.664 | 0.497 | -0.167 | -0.222 | Semitic / Horn |
| Hausa | 0.651 | 0.518 | -0.133 | -0.157 | Chadic / West |
| Tigrinya | 0.615 | 0.485 | -0.130 | -0.129 | Semitic / Horn |
| Luganda | 0.654 | 0.526 | -0.128 | -0.182 | Bantu / East |
| English | 0.659 | 0.539 | -0.120 | -0.181 | Germanic / control |
| Igbo | 0.597 | 0.508 | -0.089 | -0.100 | Volta Niger / West |
| Shona | 0.603 | 0.523 | -0.081 | -0.116 | Bantu / Southern |
| Lingala | 0.633 | 0.556 | -0.077 | -0.167 | Bantu / Central / Franco |
| Xhosa | 0.593 | 0.526 | -0.068 | -0.072 | Bantu / Southern |
| Yoruba | 0.587 | 0.550 | -0.036 | -0.026 | Volta Niger / West |
| Nigerian Pidgin | 0.470 | 0.523 | +0.053 | +0.066 | English creole / West |

---

## Test 1: does the matter and manner PC1 structure reproduce per language?

Two parts to the answer, and they point in different directions, so both are stated.

**The axis reproduces.** Pooled reference PC1 on all African news, then per language PC1 fitted inside
each language and cosined to the reference:

| language | PC1 % var | cos(PC1, reference) |
|---|---:|---:|
| Tigrinya | 41.5 | 0.992 |
| Swahili | 37.2 | 0.986 |
| Hausa | 42.1 | 0.984 |
| Igbo | 42.0 | 0.983 |
| Shona | 44.0 | 0.982 |
| Yoruba | 39.3 | 0.981 |
| Nigerian Pidgin | 32.8 | 0.981 |
| Lingala | 42.7 | 0.978 |
| Oromo | 29.7 | 0.972 |
| French | 33.1 | 0.970 |
| Kirundi | 36.1 | 0.965 |
| Amharic | 36.5 | 0.961 |
| English | 33.7 | 0.961 |
| Luganda | 45.2 | 0.961 |
| Xhosa | 39.3 | 0.953 |
| Somali | 27.8 | 0.918 |

**16 of 16** at cosine above 0.80. The dominant axis is one thing across all sixteen languages and
both scripts.

**But the axis is substance, not the bipolar matter versus manner.** Pooled PC1 loadings:

| axis | loading |
|---|---:|
| rigour | +0.510 |
| depth | +0.495 |
| originality | +0.467 |
| candour | +0.445 |
| register | +0.226 |
| stance | +0.130 |
| commercial_drive | +0.065 |
| affect | -0.085 |

Rigour and depth versus affect survives (opposite signs), but stance and register load with the
substance axes rather than against them, so this is a substance factor, not the matter versus manner
contrast (cosine to that contrast only 0.33). The cause is genre: a pure news slice has little affect
variance for affect to anchor a pole. On the tweet panel, where affect and stance vary far more, the
pooled PC1 shifts again (rigour, depth, stance, register positive, affect and candour negative) and
still reproduces per language in 14 of 15. The lesson is that the *leading axis is invariant across
languages* but *its composition is set by genre*, not by language.

---

## Test 2: where do the African languages sit, and by what do they cluster?

Clustering of the 16 language mean vectors (standardised across languages), tested against language
family, region and European colonial language legacy. Ratio below 1 means within group is closer than
between group, that is, the metadata organises the space.

| grouping (news) | within | between | ratio |
|---|---:|---:|---:|
| language family | 3.21 | 4.02 | **0.80** |
| region | 3.44 | 3.96 | 0.87 |
| colonial language | 3.59 | 4.08 | 0.88 |

Language family is the strongest organiser, region and colonial legacy weaker and about equal. The
readable structure:

- **Horn cluster.** Somali and Oromo (Cushitic) are mutual nearest neighbours and the two most matter
  heavy languages. Amharic and Tigrinya (Semitic, Ge'ez) pair with each other. The Horn as a whole
  occupies the matter heavy corner of the map.
- **Nigerian Pidgin is the outlier**, alone at the affect end (the only positive affect gap, lowest
  matter), nearest to its co territorial neighbours Igbo and Yoruba.
- **Bantu is spread, not a single cluster**: Swahili and Kirundi sit near French, Lingala near
  English and Luganda, Xhosa near Yoruba and Shona. Bantu does not hang together as tightly as the
  Horn does.

On tweets the geography collapses: family ratio 0.97, region 1.05, colonial 1.09. There is no
between language clustering in short social text. The between language map is a property of long form
news, not of the languages in the abstract.

---

## Test 3: affect and manner level versus European language news

African-14 pooled against the same corpus, same genre English and French news:

| measure | African-14 | eng + fra | delta | Cohen d |
|---|---:|---:|---:|---:|
| matter | 0.641 | 0.689 | -0.048 | -0.32 |
| manner | 0.526 | 0.535 | -0.009 | -0.11 |
| affect | 0.502 | 0.486 | +0.016 | +0.13 |
| affect gap | -0.139 | -0.203 | +0.064 | +0.30 |

Manner and affect are effectively equal. The only real difference is a small matter deficit (d =
-0.32), which is precisely what a scorer weaker on low resource languages would produce and cannot be
told apart from a genuine difference without human labels. Because affect is flat, the observational
level gives no evidence either way on the manipulation signature; that lives in the deception
contrast, not the baseline.

---

## Caveats and scope

- **The instrument, not the ground truth.** These are one 7B scorer's readings. On the Ge'ez script
  pair the scorer fails one item in five and shows a commercial_drive artefact, so Amharic and
  Tigrinya are the least trustworthy rows. Everywhere else coverage is 100% and variance is healthy,
  but there is no human labelled African language set to calibrate against, so absolute levels
  (especially the small matter deficit) carry an unquantified scorer error. Cross language *structure*
  (per language PC1 alignment, family clustering) is far more robust to this than absolute *level*.
- **News baseline.** Panel A holds genre at news so the between language comparison is clean. The
  tweet panel shows the ordering is genre dependent, which is a result in itself, not a failure.
- **English and French are African outlet news**, so they are a fair genre matched control but not a
  European newsroom sample; the comparison is like for like on protocol, not on newsroom.

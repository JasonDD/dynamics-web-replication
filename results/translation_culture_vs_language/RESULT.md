# Culture or language mechanics? A parallel corpus decomposition

**Question.** The DYNAMICS-WEB series finds a between nation signal in rhetorical
character. Is that signal in the CONTENT (real culture that would survive being
said in another language) or in the LANGUAGE MECHANICS (the same idea just reads
differently once it is in German or Greek)? Prior tests were observational and
could not separate the two, because in the wild a nation and its language move
together (fabric #18993, #18997, #19005). This test breaks the tie directly with
a parallel corpus: the SAME content, professionally translated and aligned across
eight languages, scored on all eight rhetorical axes, then decomposed into a
content component and a target language component.

**Verdict.** On this corpus the between version character signal is overwhelmingly
CONTENT, not language mechanics. Of the systematic (reproducible direction)
between version variance in matter versus manner, **about 90% tracks the content
item and about 10% is the target language** reasserting its own norm. Character
survives translation in direction, though it is measured noisily on single
sentences. This tempers, but does not erase, the language confound: the confound
is real and it is small.

---

## Method

**Corpus.** Europarl v7 (statmt.org), the canonical parallel corpus of European
Parliament speeches, professionally translated and sentence aligned. Europarl
ships as line aligned bilingual pairs (each target language against English), so
a genuine eight language set was built by an exact English pivot: an English
sentence that appears exactly once, at length 180 to 1200 characters, in every one
of the seven pairs joins that pair's translation in each language. 121,912 English
sentences met that bar; 800 were sampled at random (seed fixed). Each item is one
speech sentence present, unambiguously aligned, in all eight languages.

- **Languages (8, spanning four families):** English, German, French, Spanish,
  Italian (Germanic and Romance), Finnish (Uralic), Polish (Slavic), Greek
  (Hellenic).
- **Items:** 800, each present in all 8 languages = 6,400 scored versions.
- **Median English item length:** 233 characters (a substantial single sentence).

**Scoring.** The exact series scorer and rubric were reused
(`truthometer/scripts/cc_found_human_score.py`, the free internal 7B character
model, same system prompt, same vocabulary line, same parse). Every version scored
on the eight axes: rigour, depth, originality, candour, affect, commercial drive,
stance, register. Matter versus manner is PC1 (SVD on `the internal reference table`,
standardised, oriented rigour plus depth positive), the same ruler as the rest of
the series.

**Decomposition.** Two reads per axis:

1. *Does character survive translation?* Treat each item as a group of eight
   language versions and measure agreement: the intraclass correlation ICC(item),
   the mean correlation between languages, and the correlation of the English
   score against the mean of the seven translations. High agreement means the
   content, not the language, sets the score.
2. *Content versus target language.* A balanced two way random effects model,
   value(item, language) = mean + item + language + residual (one observation per
   cell, so the item by language interaction folds into the residual). The item
   component is CONTENT; the language main effect is the TARGET LANGUAGE NORM
   reasserting uniformly; the residual is measurement noise plus interaction.

---

## Results

### Headline: matter versus manner (PC1)

| Share of variance | Content (item) | Target language | Residual (noise) |
|---|---|---|---|
| of TOTAL variance | 32.4% | 3.7% | 63.9% |
| of SYSTEMATIC signal (content + language) | **89.8%** | **10.2%** | n/a |

Both components are decisively real: item p ≈ 3e-291, language p ≈ 2e-65.
Bootstrap over items (B = 1000) gives the content share 28.7% to 36.4% of total
and the language share 2.9% to 4.7% of total, i.e. content is roughly 86% to 92%
of the systematic signal. Character survives translation moderately: PC1
ICC(item) = 0.32, mean correlation between languages = 0.34, English against the
mean translation = 0.50.

### Per axis (content versus language, of the systematic signal)

| axis | content% | language% | ICC(item) |
|---|---|---|---|
| stance | 98.5 | 1.5 | 0.48 |
| register | 98.5 | 1.5 | 0.38 |
| affect | 94.7 | 5.3 | 0.32 |
| candour | 89.5 | 10.5 | 0.20 |
| originality | 89.1 | 10.9 | 0.31 |
| commercial drive | 88.4 | 11.6 | 0.25 |
| rigour | 84.2 | 15.8 | 0.33 |
| depth | 78.7 | 21.3 | 0.25 |

A clean pattern: the MANNER end (stance, register, affect) survives translation
almost untouched by the target language, while the MATTER end (rigour, depth)
is where the language reasserts most (16% to 21% of its signal). This is the
opposite of the naive worry that manner would be the fragile, language bound part.
Manner travels; matter is where translationese leaves its biggest, though still
minority, mark.

### The target language norm, concretely

Mean PC1 (matter versus manner) per language, same 800 items:

```
de +3.72   en +3.67   fr +3.68   it +3.30   es +3.24   pl +3.06   fi +2.88   el +2.65
```

The Germanic and Romance core sits high on the matter end; Finnish (Uralic) and
Greek (Hellenic) pull toward manner. That pull is the language main effect made
visible, but it spans about one PC1 unit against a within language spread of about
two units, a real shift, and a small one.

---

## Honest reading

- **The confound is real but small.** When identical content is professionally
  translated across eight languages and four families, the target language accounts
  for only about a tenth of the systematic character signal; about nine tenths
  tracks the content. So the between nation character the series measures is
  mostly culture that would survive being said in another language, not an artefact
  of the language it was said in. This is the direct answer the earlier
  observational tests (fabric #18997, #18998) could not give.

- **Survival is directional, not tight.** Residual is 64% of total variance. Most
  of that is the scorer reading single sentences, where a few hundred characters
  give a noisy character estimate, plus genuine item by language translation
  choices. So character survives translation in DIRECTION (the systematic split is
  90/10 content) but any single translated sentence is a noisy copy of the original
  (correlation about 0.34 to 0.50). Longer passages would raise the absolute
  agreement; the content versus language split would not move, because noise sits
  in the residual, not in either main effect.

- **Translation flattens voice, so the language share is a floor.** Professional EU
  translators normalise register; a translated speech is a smoothed version of the
  original voice. That normalisation, if anything, SUPPRESSES the target language's
  fingerprint, so the 10% language share is a conservative floor, not a ceiling.
  Wild text, where an author freely chooses the language and its idioms, could show
  more language mechanics than translationese does.

- **The language component includes model calibration.** The target language main
  effect blends genuine translationese voice with the scorer's own per language
  calibration (the 7B is web tuned and reads formal parliamentary text, a domain
  gap). Both belong on the not content side for this question, so the split stands,
  but the 10% is not purely linguistic culture; part of it is the instrument.

- **Scope.** This decomposes the confound for translated equivalent content on one
  parallel corpus. It does not settle the observational web claim, where nation and
  language are chosen together rather than held fixed. It is a clean, direct piece
  of evidence that the series' character signal is not mainly a language artefact,
  in one high quality but non neutral setting.

**If the finding had gone the other way**, with character not surviving translation
and language dominating, it would have forced a retreat on the culture claims. It did
not. The culture reading stands, with the language mechanics quantified as a real
but minority contributor.

---

## Artefacts

- **Data (internal store):** `the internal corpus store/europarl_multiway/` holds
  `items_meta.jsonl` (800 aligned items, all 8 languages), `score_input.jsonl`
  (6,400 scoring rows), `scored.jsonl` (6,400 scored versions).
  Source pairs: `the internal corpus store/europarl_v7/`.
- **Scripts (this folder):** `fetch_europarl.sh` (download and extract v7 pairs),
  `build_multiway.py` (English pivot multi language build), `analyse_multiway.py`
  (survival plus variance decomposition).
- **Full numeric output:** `analysis_output.txt`.
- **Scorer:** `truthometer/scripts/cc_found_human_score.py` (unchanged), endpoint
  the internal 7B character model, workers 12.

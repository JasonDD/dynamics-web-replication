# The translator fingerprint: does a target language stamp a reproducible character offset?

**Question.** A companion test (`results/translation_culture_vs_language`) showed that
when the same content is professionally translated across eight languages, MANNER
(stance, register, affect) survives almost untouched while MATTER (rigour, depth)
takes the language hit. That result treated the target language as a single nuisance
number per axis. This test asks the sharper question: does each target language impose
a CONSISTENT, REPRODUCIBLE character shift on the same source text, a per language
signature across all eight axes, that shows up again in an independent parallel corpus?
If it does, that signature is a translation authenticity signal: a fingerprint of which
language a text was rendered into, and of the act of translation itself.

**Verdict.** Yes, with an honest size caveat. Each target language carries a
reproducible eight axis character offset (every per axis language main effect is
significant at p far below 1e-9), and the offsets are STRUCTURED, not random: they
cluster by language family (Germanic and Romance versus the Uralic, Slavic, Hellenic
periphery), and a large shared component is a generic translationese direction present
in every target. The fingerprint replicates in direction across corpora: the German,
French and Spanish offsets measured on Europarl point the same way as the same three
measured on an independent multilingual Bible (pooled cosine 0.72, Pearson r 0.60 over
the 24 axis cells; French and Spanish r about 0.7). But the
fingerprint is a MINORITY of the signal: the target language explains only about 0.6 to
7 percent of per axis variance (content and single sentence noise dominate). So the
language fingerprint is real, reproducible and family structured, and it is small. As a
commercial signal it is usable in aggregate (many sentences), not on a single sentence.

---

## Method

**Corpora.** Two independent parallel sets, same content rendered in multiple languages,
same scorer, same eight axes.

1. **Europarl multiway** (held, `results/translation_culture_vs_language`):
   `the internal corpus store/europarl_multiway/`. 800 English source sentences, each
   present and aligned in all 8 languages (English, German, French, Spanish, Italian,
   Finnish, Polish, Greek) = 6,400 scored versions. A balanced item x language design.
2. **Multilingual Bible** (independent replication):
   `the internal corpus store/bible_multilingual/`. Verse aligned bilingual pairs
   (English against each target). Seven well populated target languages sampled
   (German, French, Spanish, Portuguese, Arabic, Chinese, Swahili), ~200 verses per
   pair, each verse scored in English and its target = a PAIRED within verse contrast.
   Overlap with Europarl for direct replication: German, French, Spanish.

**Scoring.** Identical to the series: `truthometer/scripts/cc_found_human_score.py`,
the free internal 7B character model (`an internal 7B instruct model` on the shared  endpoint),
same system prompt, same vocabulary line, same parse. Eight axes: rigour, depth,
originality, candour, affect, commercial drive, stance, register (each 0 to 1).

**The fingerprint.** For Europarl, an item x language two way random effects model per
axis (`value = mean + item + language + residual`) gives the language MAIN EFFECT: the
part of the score that moves with the target language, holding content fixed. The per
language mean on each axis, expressed as an offset from the English source and divided
by the pooled per axis standard deviation (z units), is the eight axis FINGERPRINT
vector for that language. For the Bible, the fingerprint is the mean paired difference
(target minus English) per axis, z scored by the pooled Bible axis SD. Both are offsets
relative to English, so they are directly comparable across corpora.

---

## Results

### 1. The target language offset is real and it is small (Europarl, per axis)

Item x language variance split (percent of total per axis variance):

| axis | content (item) % | target language % | residual % | p(language) |
|---|---|---|---|---|
| rigour | 33.3 | 6.2 | 60.4 | 3e-116 |
| depth | 26.0 | 7.1 | 66.9 | 2e-118 |
| originality | 31.5 | 3.8 | 64.6 | 2e-67 |
| candour | 20.5 | 2.4 | 77.1 | 2e-35 |
| affect | 32.2 | 1.8 | 65.9 | 4e-31 |
| commercial drive | 25.6 | 3.4 | 71.1 | 1e-53 |
| stance | 48.1 | 0.7 | 51.2 | 4e-16 |
| register | 38.1 | 0.6 | 61.4 | 2e-10 |
| **matter/manner (PC1)** | **32.4** | **3.7** | **63.9** | **2e-65** |

Every language effect is overwhelmingly significant, so the fingerprint is definitely
there; it is also small (0.6 to 7 percent of variance), because content and single
sentence measurement noise dominate. The fingerprint lives in the systematic direction,
not in the amount of variance it moves.

### 2. The fingerprint: per language eight axis offset from English (z units, Europarl)

Positive = the target language reads HIGHER than the English source on that axis.

```
lang   rigour  depth  origin cando  affect commerc stance regis   || length
en      +0.00  +0.00  +0.00  +0.00  +0.00  +0.00   +0.00  +0.00     0.00
de      +0.25  +0.30  +0.49  -0.08  -0.07  +0.32   -0.12  +0.14     0.73
fr      +0.18  +0.35  +0.63  -0.06  -0.03  +0.40   -0.25  -0.02     0.88
es      -0.05  +0.07  +0.35  -0.06  +0.21  +0.59   -0.18  +0.04     0.75
it      -0.06  +0.07  +0.32  -0.12  +0.04  +0.41   -0.22  +0.01     0.58
fi      -0.36  -0.26  +0.20  -0.31  +0.30  +0.53   -0.14  -0.08     0.85
pl      -0.37  -0.23  +0.21  -0.33  +0.06  +0.45   -0.07  +0.00     0.74
el      -0.41  -0.40  +0.15  -0.43  +0.23  +0.55   -0.26  -0.14     0.99
```

Reading it:
- **Germanic and Romance core (de, fr)** render MORE rigorous, deeper and more original
  than the English source.
- **The periphery (fi, pl, el)** render LESS rigorous, shallower and less candid, and
  more affective. Greek is the strongest departure from English (length 0.99).
- **Every target** reads higher than English on ORIGINALITY and COMMERCIAL DRIVE and
  lower on STANCE. That shared shift (see 4) is a translation direction signature, not a
  property of any one language.

### 3. The fingerprints cluster by language family (Europarl)

Cosine between per language offset vectors (1.0 = identical direction, 0 = unrelated):

```
      de     fr     es     it     fi     pl     el
de   +1.00  +0.96  +0.71  +0.77  +0.18  +0.21  +0.08
fr   +0.96  +1.00  +0.78  +0.85  +0.30  +0.30  +0.21
es   +0.71  +0.78  +1.00  +0.95  +0.76  +0.69  +0.65
it   +0.77  +0.85  +0.95  +1.00  +0.73  +0.72  +0.67
fi   +0.18  +0.30  +0.76  +0.73  +1.00  +0.95  +0.97
pl   +0.21  +0.30  +0.69  +0.72  +0.95  +1.00  +0.95
el   +0.08  +0.21  +0.65  +0.67  +0.97  +0.95  +1.00
```

Two tight clusters: {de, fr} (cosine 0.96) and {fi, pl, el} (cosine 0.95 to 0.97), with
Romance {es, it} bridging them. German and Greek are almost orthogonal (0.08). The
fingerprint is not per language noise; it carries the geography of the language families.

### 4. Shared translationese versus language specific signature (Europarl)

Splitting each offset into a component shared by all seven targets (the mean vector) and
a per language residual:

```
         rigour  depth  origin cando  affect commerc stance regis  || length
GENERIC  -0.12  -0.01  +0.33  -0.20  +0.11  +0.46   -0.18  -0.01    0.65
```

- **Share of total offset energy: generic (common) = 66 percent, language specific = 34
  percent.** So most of the "this is a translation" signal is a direction every target
  shares (up on originality and commercial drive, down on candour and stance), and a
  substantial minority is genuinely per language.
- The generic vector is itself a usable signal: it separates translated text from source
  text regardless of which language, distinct from the per language fingerprint that
  says which language.

Language specific residuals (offset minus the generic vector) keep the family structure:
de/fr stay high on rigour and depth, the periphery stays low, confirming the per
language part is real after the shared translationese direction is removed.

### 5. Cross corpus replication (Europarl versus independent Bible)

The same three languages present in both corpora (German, French, Spanish) were scored
on the Bible as a paired target minus English offset (~198 verse pairs each). Two very
different registers, parliamentary debate and scripture, so a fingerprint that survives
the switch is a property of the target language, not of the domain.

Bible paired offsets (target minus English, z units, pooled Bible SD):

```
lang  rigour  depth  origin cando  affect commerc stance regis  || length  nPairs
de    +0.71  +0.74  +0.21  +0.30  -0.01  +0.17   +0.21  +0.11    1.12      198
fr    +0.69  +0.79  +0.53  +0.01  +0.13  +0.43   +0.18  +0.32    1.31      198
es    +0.22  +0.24  +0.49  -0.16  +0.31  +0.79   +0.39  +0.17    1.13      197
pt    +0.13  +0.21  +0.76  -0.25  +0.28  +0.77   +0.32  +0.11    1.22      198
ar    +0.70  +0.56  +1.18  +0.08  +0.07  +0.93   +0.64  +0.60    1.96      197
zh    -0.31  -0.29  +0.04  -0.69  -0.03  +0.11   +0.16  -0.22    0.86      168
sw    -0.79  -0.65  +0.66  -0.74  +0.64  +1.04   +0.72  +0.14    2.01      198
```

Agreement of the eight axis offset vector, Europarl versus Bible, for the overlap
languages:

| language | cosine (Europarl vs Bible) | Pearson r |
|---|---|---|
| German | 0.63 | 0.34 |
| French | 0.74 | 0.69 |
| Spanish | 0.78 | 0.74 |
| **pooled (de, fr, es; 24 axis cells)** | **0.72** | **0.60** |

**The fingerprint replicates in direction.** All three overlap languages point the same
way across two unrelated corpora, and the German/French/Spanish rank order of matter
loading holds (German and French heaviest on rigour and depth, Spanish lighter and more
affective and commercial). The replication is strongest for French and Spanish (r about
0.7) and weaker but still clearly positive for German (r 0.34), where the Bible offset is
larger and more rigour and depth loaded than Europarl's. The offsets are bigger in the
Bible overall (King James style archaic English as the low baseline inflates every
target), but the shape, which axes go up and which go down, is what replicates, and it
does.

**The family and periphery pattern extends beyond Indo European.** Arabic loads high on
almost every matter axis (a very formal Quranic register in translation); Chinese sits at
the low, plain end (negative rigour, depth and candour, like Europarl's Finnish, Polish
and Greek periphery); Swahili is the affect and commercial extreme. Chinese, an isolate
relative to the European set, lands in the same low matter region the Uralic, Slavic and
Hellenic languages occupy in Europarl, so the matter to manner axis of the fingerprint is
not a European artefact.

---

## Honest reading

- **The fingerprint exists and is reproducible.** Every target language stamps a
  significant, structured, family clustered character offset on identical content. This
  is a genuine, previously unquantified property: translation into a given language
  moves the eight axis character in a consistent, predictable direction.

- **It is a minority signal.** The target language explains only about 0.6 to 7 percent
  of per axis variance. Content and single sentence noise dominate. The fingerprint is
  a direction you can only read reliably in aggregate (many sentences), never from one
  translated sentence.

- **Most of it is generic translationese, not per language voice.** 62 percent of the
  offset energy is a direction every target shares; 38 percent is language specific. So
  the strongest, most portable signal is "this text was translated" rather than "this
  text was translated into German".

- **Commercial angle: a translation authenticity signal.** A consistent per language
  character offset, and an even stronger generic translationese offset, is a machine or
  human translation detector and a translation provenance signal. Given enough text, the
  eight axis character profile shifts toward the fingerprint of the target language and
  toward the generic translationese direction; a native original does not carry that
  shift. This is a soft, aggregate signal (useful over a document or a corpus, not a
  sentence), and it is confounded with the scorer's own per language calibration, so it
  is an indicator to combine with others, not a standalone verdict.

- **Caveat, the scorer is part of the language effect.** The per language offset blends
  genuine translationese with the 7B model's own per language calibration on formal
  text. Both sit on the not content side, so the fingerprint is real for the authenticity
  use, but it is not purely linguistic culture.

---

## Artefacts

- **Data (internal store):** `the internal corpus store/europarl_multiway/scored.jsonl` (6,400
  scored versions, held); `the internal corpus store/bible_multilingual/fingerprint_scored.jsonl`
  (Bible paired scores, this test) with `fingerprint_score_input.jsonl`.
- **Scripts (this folder):** `fingerprint_analyse.py` (per language offset decomposition,
  translationese split, cross corpus replication), `build_bible_input.py` (Bible pair
  sampler).
- **Full numeric output:** `analysis_output.txt`.
- **Scorer:** `truthometer/scripts/cc_found_human_score.py` (unchanged), endpoint the
  internal 7B character model.

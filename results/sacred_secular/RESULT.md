# Is there a universal character of command across sacred and secular authority?

DYNAMICS-WEB experiment child, PUBLIC track. Authority type by culture character matrix on the shared
8 axis instrument (same 7B teacher on :8301, same system prompt and vocabulary line as every other child
in the series). Question: do the commanding registers of religion and of law and state share a character,
or diverge, across cultures?

## What was measured

9,023 authority passages, each scored on the eight axes (rigour, depth, originality, candour, affect,
commercial drive, stance, register). Every score reused from disk where present; nothing was scored
again for this run. The corpus spans four authority types across three civilisational cultures plus a Greco Roman
oratory bucket.

| Type | Source | Culture | n |
|---|---|---|---|
| Sacred | Bible (World English Bible) | western | 180 |
| Sacred | Quran (Sahih English + Arabic) | islamic | 280 |
| Sacred | OpenITI classical Arabic prose | islamic | 140 |
| Sacred | Analects (Legge English + classical Chinese) | sinic | 110 |
| Secular state | UN General Debate addresses | western / islamic / sinic | 1929 / 2086 / 76 |
| Secular legislative | ParlaMint parliamentary speech | western / islamic (TR) | 1620 / 55 |
| Secular judicial | Old Bailey, ECHR, SCOTUS | western | 568 / 700 / 800 |
| Ancient oratory | Cicero, Demosthenes | greco_roman | 14 / 20 |
| Ancient strategic | Zhanguo Ce | sinic | 445 |

Coverage is honest but uneven: judicial authority is western only (no Islamic or Sinic court sample was
held), so the full type by culture grid is not square. The clean balanced sub design is sacred versus
secular state across all three cultures, and that is where the culture versus type test is run.

## The matrix (source means, PC1 is the series matter versus manner axis, + is toward matter)

| source | type | culture | n | rigo | dept | orig | cand | affe | comm | stan | regi | PC1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cicero | ancient_oratory | greco_roman | 14 | 0.79 | 0.72 | 0.55 | 0.84 | 0.54 | 0.16 | 0.81 | 0.53 | +0.80 |
| demosthenes | ancient_oratory | greco_roman | 20 | 0.80 | 0.82 | 0.59 | 0.79 | 0.45 | 0.17 | 0.77 | 0.56 | +1.13 |
| zhanguo_ce | ancient_strategic | sinic | 445 | 0.65 | 0.65 | 0.36 | 0.75 | 0.33 | 0.15 | 0.57 | 0.45 | -0.25 |
| openiti | sacred | islamic | 140 | 0.60 | 0.67 | 0.34 | 0.72 | 0.39 | 0.14 | 0.51 | 0.42 | -0.66 |
| quran | sacred | islamic | 280 | 0.69 | 0.58 | 0.28 | 0.77 | 0.40 | 0.11 | 0.40 | 0.41 | -0.72 |
| analects | sacred | sinic | 110 | 0.70 | 0.67 | 0.29 | 0.78 | 0.39 | 0.13 | 0.50 | 0.47 | -0.32 |
| bible | sacred | western | 180 | 0.60 | 0.55 | 0.25 | 0.73 | 0.42 | 0.12 | 0.45 | 0.34 | -1.17 |
| echr | secular_judicial | western | 700 | 0.88 | 0.77 | 0.42 | 0.78 | 0.41 | 0.30 | 0.46 | 0.78 | -0.21 |
| oldbailey | secular_judicial | western | 568 | 0.75 | 0.54 | 0.28 | 0.86 | 0.32 | 0.10 | 0.37 | 0.53 | -0.35 |
| scotus | secular_judicial | western | 800 | 0.81 | 0.72 | 0.56 | 0.84 | 0.42 | 0.19 | 0.76 | 0.69 | +0.73 |
| parlamint | secular_legislative | islamic | 55 | 0.39 | 0.47 | 0.36 | 0.75 | 0.68 | 0.16 | 0.75 | 0.47 | -2.23 |
| parlamint | secular_legislative | western | 1620 | 0.63 | 0.58 | 0.41 | 0.82 | 0.50 | 0.19 | 0.72 | 0.59 | -0.67 |
| ungd | secular_state | islamic | 2086 | 0.78 | 0.68 | 0.53 | 0.82 | 0.45 | 0.22 | 0.72 | 0.61 | +0.32 |
| ungd | secular_state | sinic | 76 | 0.78 | 0.68 | 0.53 | 0.83 | 0.43 | 0.23 | 0.76 | 0.60 | +0.45 |
| ungd | secular_state | western | 1929 | 0.80 | 0.70 | 0.56 | 0.84 | 0.45 | 0.23 | 0.69 | 0.61 | +0.46 |

## Three findings

### 1. There is no single commanding voice shared by sacred and secular authority. They split.

Sacred versus all secular authority, per axis, with Cohen's d (secular is every non sacred row):

| axis | sacred | secular | diff | Cohen d |
|---|---|---|---|---|
| rigour | 0.650 | 0.753 | -0.103 | -0.57 |
| depth | 0.602 | 0.664 | -0.062 | -0.48 |
| originality | 0.288 | 0.481 | -0.193 | **-1.50** |
| candour | 0.753 | 0.822 | -0.069 | -0.55 |
| affect | 0.400 | 0.439 | -0.039 | -0.28 |
| commercial_drive | 0.121 | 0.208 | -0.087 | -0.95 |
| stance | 0.450 | 0.665 | -0.215 | **-1.11** |
| register | 0.400 | 0.612 | -0.212 | -0.92 |

Sacred PC1 mean -0.76 versus secular +0.06. Centroid separation in the 8 axis space is highly reliable
(permutation p = 0.0005 over 2,000 shuffles). The hypothesis that authority carries one commanding
signature of high stance and a command register is **rejected**. The commanding, polemical, high stance
voice belongs to the secular side (state addresses, parliamentary speech, apex court advocacy, classical
oratory), not to scripture. Scripture sits lower on stance, lower on register (more institutional and
formal, less conversational), lower on originality, and lower on rigour.

The one thread the two sides do share is thin: both are high on candour (transparency, 0.75 versus 0.82)
and both are near the floor on commercial drive. So if there is a common signature of authority at all, it
is "direct and not selling", not "commanding".

### 2. Authority character varies far more by TYPE than by CULTURE.

On the balanced sacred versus secular state partition across all three cultures (n = 4,801), multivariate
eta squared:

- eta^2 TYPE (sacred versus secular) = **0.176**
- eta^2 CULTURE (western / islamic / sinic) = **0.016**

Type explains about eleven times more variance than culture. What a text is doing (scripture versus a
state at the podium) marks its character an order of magnitude more strongly than which civilisation it
comes from.

### 3. Scripture has a universal voice ACROSS cultures, and it is not its own state's voice.

Nearest neighbour on the standardised centroids: each culture's scripture is closest to another culture's
scripture, and very far from its own state voice.

| scripture | nearest | own state | foreign scripture |
|---|---|---|---|
| western | islamic scripture (1.08) | 4.22 | sinic 1.87 |
| islamic | sinic scripture (0.90) | 3.11 | western 1.08 |
| sinic | islamic scripture (0.90) | 2.77 | western 1.87 |

The Bible, the Quran and the Analects read more like each other than any of them reads like the modern
state that grew up around it. So there IS a universal character of authority here, but it is the universal
character of SCRIPTURE, sitting across all three cultures, and it is a distinct register from the universal
character of the secular STATE (the three UNGD state voices are almost identical to one another too:
western / islamic / sinic PC1 = +0.46 / +0.32 / +0.45). Two universals, one per type, not one universal of
command.

## Controls

**Translation.** Most sacred text is translated, most secular text is not, so translation is the obvious
confound. It is real and large: within the same scripture, English versus original language moves PC1 by
0.80 (Quran) and 0.91 (Analects), which is about the size of the whole sacred versus secular PC1 gap. That
alone would sink the result, so it was checked against a comparison that holds language and culture
constant.

**Same language, same culture check (the decisive one).** English Bible versus western secular authority
that is natively in English (UNGD western, Old Bailey, ECHR, SCOTUS, all English): PC1 -1.63 versus +0.13,
a gap of 1.76 with Cohen d = -1.27. Both sides are English and both are western, so neither translation
nor culture can be creating it. The split survives. Restricting the whole type test to English only texts
keeps eta^2 TYPE at 0.081 with per axis effects still strong (originality d = -2.12, depth -1.13,
commercial_drive -1.11, stance -1.10, rigour -1.03, register -1.02). The sacred versus secular divide is
not a translation artefact.

**Length.** PC1 correlates +0.34 with log length across records, so longer texts read a little more toward
matter. Sacred passages were chunked to about 1,200 characters by design, so within sacred length is
controlled; and the length matched secular comparison (short parliamentary turns) still sits above
scripture on PC1, so length does not explain the gap either.

## Verdict

**A clean split, plus a universal that is not the one the question proposed.**

There is no single universal voice of command spanning God, law and state. Sacred and secular authority
diverge systematically and reliably (permutation p = 0.0005; the split holds within English and within one
culture at Cohen d = -1.27, so it is not a translation or a culture artefact). Authority character is
governed about eleven times more by TYPE than by CULTURE. The commanding register of high stance, high
originality and a forceful voice is a SECULAR trait, carried by states, parliaments, courts and orators;
scripture commands through the opposite register, low stance, institutional and canonical, high in candour
and near zero in commercial drive.

What IS universal is narrower and cuts the other way: scripture shares one character across western,
islamic and sinic traditions, and the secular state shares another across the same three. The universality
lives WITHIN each authority type across cultures, not ACROSS the sacred and secular divide. The character
of command is set by the institution doing the commanding, not by the civilisation it commands in.

Caveats kept in view: judicial and oratory cells are western or Greco Roman only, so the square type by
culture grid is not fully populated and the strong claims rest on the balanced sacred versus secular state
sub design and the English only robustness checks; the Islamic legislative cell (ParlaMint Turkey, n = 55)
is thin and reads as an outlier and should not be over read.

## Artefacts

- `analysis_console.txt`: full analyser output for this run.
- `matrix_stats.json`: machine readable source rows, Cohen d per axis, PC1 means, eta squared, permutation p.
- Scores reused from `/mnt/nas/kronaxis/corpora/sacred_secular/sacred_scored.jsonl` (sacred) and the held
  secular scores under `ungd/`, `parlamint/`, `oldbailey/`, `legal_matrix/`, `classical/`.
- Scorer and analyser: `/mnt/nas/kronaxis/corpora/sacred_secular/{score.py,build_sacred.py,analyse_sacred_secular.py}`.

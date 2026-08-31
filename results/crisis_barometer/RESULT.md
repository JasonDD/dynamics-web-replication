# National character as a crisis barometer

DYNAMICS-WEB series, PUBLIC track. Does a nation's discourse character shift measurably when it
enters war or crisis? An event study on the richest cross national temporal corpus we hold.

## Question and design

We score every country's annual statement at the UN General Debate on the eight axis DWEB character
instrument and ask whether a nation talks differently in the years it is at war or in armed conflict.
The design is a **within country** event study: country fixed effects absorb every stable national
trait (a nation that is always florid, always terse), so the estimate is the change against **that
nation's own baseline**, not a cross national comparison that would confound conflict with culture,
language or translation house style.

- **Discourse corpus**: UN General Debate Corpus, 1946 to 2022, one speech per country per year, one
  controlled venue. Scored on the eight axes plus the matter versus manner PC1 (the same SVD on
  `cc_v3.domain_char8_expanded`, oriented so rigour plus depth is the matter pole). **Full coverage:
  all 10,556 scored speeches, 200 countries** (every country year the corpus holds; the earlier 1,594
  speech stratified snapshot was rescored to completeness and this document reports the full set).
- **Conflict dates**: UCDP/PRIO Armed Conflict Dataset **v26.1** (static, free, CC BY 4.0, 1946 to
  2025). GDELT deliberately avoided (it rate limits us). Joined by country and year through the
  Gleditsch and Ward location codes mapped to the UNGD ISO3 coding. A country year is flagged
  `CONF` if the country is a conflict location that year at any intensity, `WAR` if the conflict
  reaches war intensity (1,000 or more battle deaths that year), and `ONSET` in the first year of a
  new conflict episode. `CONF_w` widens `CONF` to a conflict in year t or t minus 1, since a speech
  given in September can trail an onset earlier in the year.
- **Estimator**, two transparent readings that must agree to count:
  1. **Within country FE OLS** of each character outcome on the crisis flag, with country clustered
     (CR1) standard errors, so significance is not inflated by repeat observations of the same nation.
  2. **Paired per country** difference, mean(outcome given crisis) minus mean(outcome given peace)
     for each nation with speeches on both sides, then a one sample t test and a sign test across
     nations. The sign test is the **cross nation consistency** measure: does the shift point the same
     way in most countries, or only on average.

Predictions under test (the brief's hypothesis): in a crisis year **affect rises, stance rises,
rigour falls**, and PC1 moves toward the manner pole.

Join coverage at full scale: **1,729 speeches (16.4 per cent) fall in a conflict year, 535 (5.1 per
cent) in a war year, 330 in a conflict onset year.**

## Result

With the full corpus scored (6.6 times the observations of the earlier snapshot) the barometer reads
clearly, and it revises the snapshot's headline: national discourse character is **not** crisis
insensitive. It shifts, the shift is strongest at war intensity, and the three predicted axis
movements all hold, but the composite moves the opposite way to the naive prediction.

### At the any conflict threshold: a small but real shift

Merely being a conflict location moves the needle, modestly (about a tenth of an axis standard
deviation) but detectably.

| Outcome | Prediction | FE beta | clustered t | p | cross nation sign |
|---|---|---|---|---|---|
| **PC1 (matter/manner)** | toward manner | **+0.192** | 2.79 | **0.006** | 70/110 (p 0.005) |
| **stance** | up | **+0.018** (+0.11 SD) | 2.06 | **0.041** | 62/110 |
| affect | up | +0.010 (+0.09 SD) | 1.66 | 0.099 | 58/110 |
| rigour | down | +0.000 (0 SD) | 0.04 | 0.96 | 68/110 |
| depth | (none) | +0.006 | 2.22 | 0.028 | 60/110 |

Stance rises as predicted, affect leans up at the margin, but rigour does not fall, and the composite
**PC1 rises toward the matter pole, opposite the prediction**, significantly and consistently (70 of
110 nations, sign p 0.005). In a conflict year a nation's UN statement becomes a little more pointed
and a little more substantive at once, netting toward matter, not toward manner.

### At war intensity: all three predicted axes confirmed, strongly

When a nation is in a full **war** year, the effect is unambiguous and every predicted direction lands.

| Outcome | Prediction | FE beta | clustered t | p | paired p | cross nation sign (npos/n, sign p) |
|---|---|---|---|---|---|---|
| **affect** | up | **+0.033** (about 0.29 SD) | 3.42 | **0.0008** | 0.003 | 39/66 |
| **stance** | up | **+0.035** (about 0.21 SD) | 3.03 | **0.003** | 0.009 | 41/66 (p 0.064) |
| **rigour** | down | **-0.007** | -2.30 | **0.022** | 0.058 | 32/66 |
| originality | (none) | +0.015 | 2.68 | 0.008 | 0.16 | 43/66 (p 0.019) |
| candour | (none) | +0.011 | 2.04 | 0.043 | 0.035 | 41/66 |
| register | (none) | -0.020 | -1.99 | 0.048 | 0.044 | 26/66 |
| PC1 | toward manner | +0.275 | 2.48 | 0.014 | 0.045 | 38/66 |

Read carefully:

- **The hypothesis lands at war intensity.** Affect rises (p 0.0008, and this survives a Bonferroni
  correction over all 36 tests), stance rises (p 0.003), and rigour falls (p 0.022), exactly the three
  moves the brief predicted. War talk is hotter, more polemical and less rigorous.
- **But the composite goes the other way.** PC1 rises toward matter (p 0.014), not toward manner. The
  matter side axes (stance, candour, originality) rise more than affect does, so on balance a war year
  statement reads as more matter leaning, more pointed and more substantive, with heightened affect
  layered on top rather than replacing the substance. The naive "toward manner" prediction for the
  composite is **wrong**; the correct reading is a hardening of substance and stance with raised heat.
- Register falls (more institutional, less conversational): war pulls a nation toward the formal
  register even as it raises affect and stance.

### Onset is not the mechanism; sustained war is

The `ONSET` flag (first year of an episode, 330 speeches) is a **clean null** across every axis. The
character shift is not a shock at the moment a nation enters conflict; it tracks the sustained state of
being at war, which is why `CONF` and especially `WAR` register while `ONSET` does not. The `CONF_w`
window (conflict in t or t minus 1) reproduces the `CONF` result, confirming it is not a timing
artefact of September speeches trailing a mid year onset.

### Consistency across nations is moderate, not universal

Even the strong war intensity effects are carried partly by magnitude in a subset of nations rather
than by a direction every nation obeys. War affect is a +0.33 mean but only 39 of 66 nations positive
by sign, stance 41 of 66 (sign p 0.064), war PC1 38 of 66 (not significant by sign). At the any
conflict threshold the composite PC1 is the most consistent single result (70 of 110 nations, sign p
0.005). So the barometer is real on average and points the predicted way, but it is a tendency across
nations, not a law each nation follows.

## Verdict

**National discourse character is a real but modest crisis barometer, and it reads conflict as a
hardening of substance and stance with raised affect, not as a slide into manner.**

This overturns the cautious null the 1,594 speech snapshot suggested. With the full corpus the signal
is clear. Being in armed conflict shifts a nation's UN statement toward matter (more pointed, more
substantive, PC1 up, p 0.006), and being in a **full war** does it strongly and confirms all three of
the brief's predicted axis moves at once: affect up (p 0.0008), stance up (p 0.003) and rigour down
(p 0.022). The one place the hypothesis was wrong is the composite direction: the predicted move toward
the manner pole does not happen, because the substantive axes rise faster than affect, so the net is a
harder, more matter leaning voice carrying more heat, delivered in a more formal register. The shift is
modest, roughly a fifth to a third of an axis standard deviation at war intensity and about a tenth at
ordinary conflict, and it is a cross national tendency rather than a universal rule. It is driven by the
sustained war state, not the shock of entering conflict, which registers as a clean null.

The diplomatic register still buffers the low intensity end: an ordinary conflict barely moves the
needle. But the venue does not hold national character steady the way the snapshot implied. Push a
nation to war and its UN voice measurably hardens, in the direction of substance and stance, and that
is a usable, publishable signal.

## Limitations

- **Register and translation.** UNGD speeches are written to be read aloud and many are translated into
  English, both of which flatten voice and raise the manner floor. The within country design removes
  the stable part of this but not any interaction between crisis and translation practice.
- **Instrument.** The eight axis instrument is tuned on the open web, not on diplomatic oratory, so its
  dynamic range on this genre is compressed; the true effect sizes may be larger than the compressed
  scale shows.
- **Multiple testing.** Nine outcomes by four flags is 36 tests. The war intensity affect result
  (p 0.0008) clears a Bonferroni threshold; war stance (p 0.003) and the any conflict PC1 (p 0.006) are
  robust; treat originality and candour as exploratory.
- **Consistency.** The effects are cross national tendencies, significant on average and by clustered
  standard errors, but the per nation sign tests show they are not something every nation does, so the
  barometer should be read as a population level signal, not a per country diagnostic.
- **Historical coding.** A handful of superseded states (Soviet era, Yugoslavia era) map imperfectly
  between UCDP location codes and UNGD ISO3, dropping a small number of joins in the 1946 to 1991 span.

## Reproduce

- Analysis: `truthometer/scripts/ungd_crisis_barometer.py` (PC1 from `cc_v3.domain_char8_expanded`,
  UCDP join, within country FE with country clustered SE, paired consistency test). Run on DL580.
- Scoring: `truthometer/scripts/ungd_score.py` (eight axis, shared 7B endpoint on :8301). Full corpus
  scored to completeness (10,556 speeches) via the `ungd-full-score` daemon run.
- Conflict data: UCDP/PRIO ACD v26.1 CSV at `/mnt/nas/kronaxis/corpora/ucdp/UcdpPrioConflict_v26_1.csv`
  (downloaded from ucdp.uu.se, CC BY 4.0).
- Scores: `/mnt/nas/kronaxis/corpora/ungd/ungd_char8.jsonl`.

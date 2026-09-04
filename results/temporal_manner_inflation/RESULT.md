# Is the web getting more manipulative over time?

**Question.** The manipulation signature the programme measures is AFFECT inflated and MATTER
starved (results/manner_inflation_deception/APPENDIX_B_TESTED_SPEC.md; results/length_mechanism/).
So: across the Common Crawl years 2020 to 2026, is the affect heavy, matter starved fraction of
the web RISING or FALLING? "Is the web getting more manipulative" is the headline form.

**Verdict. No. On the same domains, the web is getting LESS manipulative, not more, over
2020 to 2026, and the reason is not that affect is cooling (it is dead flat) but that matter
is rising underneath it.** The affect heavy, matter starved share is stable to slightly falling.

Deep time (periodicals 1810 to 1960) runs the OTHER way, drifting manner ward within a title,
but its driver is commercialisation, not affect. Across both eras the affect axis itself barely
moves. Manipulation, measured as inflated affect, is not the axis that changes over historical time.

---

## Data and method

Pure read on already scored data. Four Common Crawl snapshots, 8 axis character per domain:
`the internal reference table{2020,2022,2024,2026}` (50,855 / 56,330 / 73,935 / 94,677 domains). No new
character scoring, no , no , Postgres :5432 only. Script:
`analyse_temporal_manner_inflation.py` in this directory (runs on the internal host).

- 8 axes: rigour, depth, originality, candour, affect, commercial_drive, stance, register.
- **matter = rigour + depth ; manner = affect + stance + register** (spec definition).
- Standardisation: pooled z scores over all four snapshots (matches the matter/manner PC1 recipe
  in `truthometer/scripts/manip_analyse.py`).
  - `matter_z = z(rigour) + z(depth)`, `manner_z = z(affect) + z(stance) + z(register)`.
  - **manner inflation = manner_z − matter_z** (higher = more manner relative to matter).
  - **matter starved fraction** = share with `manner_z > 0 AND matter_z < 0` (the signature), at
    fixed pooled thresholds every year. A stricter variant: `z(affect) > 0.5 AND z(rigour+depth) < −0.5`.

**Discipline (this bit us before).** The archive wide mean is a COMPOSITION artefact, the crawl
grows from 51k to 95k domains and its mix changes. The honest test is WITHIN the same source over
time. Two composition controlled tests are reported: a fixed panel of the 41,674 domains present in
ALL FOUR snapshots, and the 50,462 domain paired endpoints 2020 vs 2026. The per snapshot mean is
shown only as the confounded baseline. The separate affect axis IS available per snapshot, so this
is not a PC1 only proxy, affect, matter_z, manner_z and the starved fraction are each tracked.

---

## Result 1: the affect axis is dead flat (the clean finding)

Within the same domains 2020 to 2026 the raw affect axis does not move at all:

| measure | 2020 | 2026 | Δ | paired t | p |
|---|---|---|---|---|---|
| affect (raw) | +0.388 | +0.388 | +0.000 | +0.66 | 0.51 |

Fixed 4 snapshot panel: affect slope −0.0000/yr, r=−0.20, p=0.80. There is no affect trend in
either direction. Whatever else the web is doing, it is not turning up the affect dial.

## Result 2: manner inflation FALLS; matter is what rises

Within domain, manner inflation (manner minus matter) drops hard, but the movement is entirely on
the MATTER side, not the manner side:

| measure (paired, 50,462 domains) | 2020 | 2026 | Δ | paired t | p |
|---|---|---|---|---|---|
| **manner inflation** | −0.035 | −0.135 | **−0.099** | −12.56 | 3.9e-36 |
| matter_z | +0.015 | +0.107 | +0.092 | +15.27 | 1.7e-52 |
| manner_z | −0.020 | −0.028 | −0.007 | −1.72 | 0.085 |
| matter/manner PC1 | +0.031 | +0.106 | +0.075 | +11.55 | 7.9e-31 |

manner_z is essentially flat (−0.007, not significant). matter_z climbs +0.092 (p=1.7e-52). So the
fall in manner inflation is **matter growing, manner standing still**, the same domains add
substance over six years, they do not shed style. The PC1 figure reproduces the prior WHEN leg
exactly (+0.031 → +0.106, Δ+0.075, t+11.55, p=7.9e-31; matches when_drift.txt), confirming the setup.

Fixed 4 snapshot panel (composition held constant across all four years) agrees and is monotone:
manner inflation slope **−0.016/yr, r=−0.99, p=0.010**; matter_z +0.0126/yr, r=+0.98, p=0.020;
manner_z −0.0034/yr (ns); affect −0.0000/yr (ns).

## Result 3: the matter starved (manipulation signature) fraction is stable to slightly down

| fraction (paired) | 2020 | 2026 | Δ | paired t | p |
|---|---|---|---|---|---|
| matter starved (manner_z>0 & matter_z<0) | 28.46% | 27.68% | −0.77pp | −3.88 | 1.1e-4 |
| strict (z affect>0.5 & z matter<−0.5) | 19.33% | 18.65% | −0.68pp | −3.94 | 8.1e-5 |

Statistically significant but SMALL: the affect heavy, matter starved slice of the web shrinks by
under one point in six years. It is not vanishing (affect is flat, so the signature content is still
there), it is being diluted as substantive content grows around it. Fixed panel slope −0.11pp/yr
(r=−0.91, p=0.092). Honest reading: the manipulative fraction is flat to gently falling, definitely
not rising.

## Result 4: direction holds across countries

Within domain Δ manner inflation by ccTLD: **17 of 20 countries move toward LESS manner** (negative
Δ). The three small exceptions are RU +0.032, US +0.067, SE +0.037 (FR ~0). The Δ affect column is
≈0.00 for every single country, the flat affect finding is universal, not an aggregate that hides
national swings. Largest falls: NL −0.188, GB −0.140, BR −0.140, IN −0.137.

---

## Deep time leg (periodicals 1810 to 1960): the opposite direction, but a commercial driver

From the already computed historical legs (results/within_source_articles_*.txt,
histchar_deeptime.txt, books_deeptime.txt). The archive wide aggregate drifts toward matter
(+0.0166/yr, r=+0.79) but that is the SAME composition artefact, the digitised genre mix changes
across two centuries. The honest WITHIN TITLE read (genre and source held fixed, 16 periodical
titles with ≥4 issues over ≥40 years) drifts the other way:

- Within title matter/manner slope **−0.0236/yr, one sample t=−2.80, p=0.013; 15 of 16 titles drift
  toward MANNER** (sign test p=5e-4). Opposes the confounded cross section.
- The per axis driver is **commercial_drive +2.30/century (t=+4.44, p<0.001, 15/16 titles up)**.
  **Affect within title is FLAT: +0.28/century, t=+0.50, p=0.63.** Books (a genre control) show
  commercial_drive flat, so the commercial rise is periodical specific, not universal.

So even where the manner pole rises over historical time, it is the COMMERCIAL sub axis that moves,
not affect. This lines up with the digital era: across 210 years of periodicals AND six years of the
web, the affect axis is the one axis that stays put. If "more manipulative" means "more affect
inflated", the data says no in both eras. If it means "more commercial", deep time periodicals say
yes within a title, but the modern web does not (manner_z flat, matter_z rising).

Caveats on the deep time leg: OCR quality improves within a title over time, the scorer is web
tuned (register recalibration owed), and digitisation/survivorship bias. These are noted in the
source files; the within title slopes are smaller than the archive wide ones but not zero.

---

## What is available vs missing

- **Available and used:** the separate affect axis, matter_z, manner_z and the matter starved
  fraction per snapshot, not a PC1 only proxy. All four CC snapshots carry the full 8 axes.
- **Missing / limits:** four snapshots is n=4 for the year level trend (the paired endpoint and
  fixed panel tests carry the weight, not the 4 point regression). Scores are a single web tuned 7B
  scorer quantised to 0.1 steps. Common Crawl domain coverage is not a random sample of the web;
  it over represents live, linkable, English leaning domains, so this is "the crawlable web", not
  "all content". The starved fraction thresholds are fixed but chosen (>0 split); the trend sign is
  robust to the strict variant, which is the point that matters.

## Bottom line

The crawlable web did not get more manipulative between 2020 and 2026. On the same domains the
affect heavy, matter starved fraction is flat to slightly down, the affect axis itself does not move
at all, and the whole matter/manner shift is substance rising, not style cooling. The one era where
the manner pole climbs within a fixed source, Victorian to mid century periodicals, is driven by
commercialisation, not affect. Affect inflation, the core of the manipulation signature, is the
single most stable thing across everything measured.

## Reproduce

`analyse_temporal_manner_inflation.py` in this directory. Runs on the internal host, reads Postgres :5432 for the
four `the internal reference table{year}` tables. Pure read, no scoring, no  or .

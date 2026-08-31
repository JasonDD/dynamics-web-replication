# Historical press drift matrix — did the character of the press change over 1800 to 1960, and does it differ by country?

*DYNAMICS-WEB daughter result, PUBLIC track. Scored on the eight axis character instrument (:8301, Qwen2.5-7B-atlas), same
scorer, same prompt, same vocabulary line as the rest of the series, so every scale matches. 31 August 2026.*

## The question

The digital web drifts toward matter over 2013 to 2026 (affect roughly flat, the substance axes rising), but that panel is
twelve years long. This asks the deep time version on newspaper corpora we hold but had not used as a grid: over roughly a
century and a half, did the voice of the press move toward matter or toward manner, more affect or less, and is whatever
happened shared across countries (a common modernisation of the press voice) or specific to each country?

The binding discipline, learned the hard way earlier in the programme: measure the change **within a single title over time**,
never across a changing archive composition. The archive wide "toward matter" trend the programme first reported (r=0.79) was a
composition artefact; the honest within title read reversed it. This result holds that line, and adds two guards the deep time
work needs: an OCR quality floor with OCR carried as a covariate (legibility improves over time and can pose as culture), and a
title balanced matrix so a decade full of one kind of paper cannot masquerade as a trend.

## What the data actually supports (confirm dates per corpus)

Eight historical corpora were checked for a usable dated slice. Only two carry the three things the test needs together — a
newspaper title, a per document date, and body text — across the deep time window. The rest are honest gaps, named below, not
papered over.

| Country | Corpus | Title? | Per doc date? | Body text? | OCR signal | Verdict |
|---|---|---|---|---|---|---|
| **FR** | french_pd_news | yes | yes (1676 to 1980, dense 1820 to 1950) | yes (full issues) | `ocr` 0 to 100, median 92 | **usable, deep and dense** |
| **EN** | histchar periodicals (held) | yes (16 titles) | yes (1810 to 1961) | yes (article prose) | web tuned scorer caveat | **usable, reused held scores** |
| **NO** | ncc_norwegian | yes (title in id) | yes but **1940 to 2018 only** | yes | `lang_fasttext_conf` proxy | thin, post 1940, 3 qualifying titles |
| US | american_stories | **no** | **no** (the flattened "all years" export dropped the year and the paper name) | yes | legibility label | **gap** — cannot place a title in a decade |
| NZ | papers_past_nz | yes | yes | **no** (metadata only; `description` all null, body behind an API url) | n/a | **gap** — nothing to score |
| DK | danish_gigaword | source only | **no** (the `created` field is a constant 1700 to 2022 range) | yes | n/a | **gap** — lexical and book material, not dated press |
| IR | persian_daily_news | no | **no** (only text and summary) | yes | n/a | **gap** — modern content, no historical slice |
| CN | weibo_sentiment | no | yes but **2025 to 2026 only** | yes | n/a | **gap** — modern only |

So the real matrix is France (deep, 103 long running titles, 1059 issues scored), England (the held reference, 16 titles, 454
issues), and Norway (thin, mid century to modern, 204 issues). This is the mosaic with holes the design predicted: report what
the data supports, mark the rest blank rather than interpolated.

## The country by decade matrix

Each cell is the mean matter versus manner position **M** (matter z minus manner z, so a higher number is more toward matter),
built title balanced: average within each title and decade first, then average those title means, so no single decade is carried
by whichever papers happen to sit in it. `n` is issues in the cell. z is pooled globally across the three countries so the cells
sit on one ruler.

```
  decade           EN          FR          NO
    1800           --   +3.91( 4)          --
    1810    -0.15( 1)   +3.82( 4)          --
    1820    -0.21( 8)   +3.02(14)          --
    1830    -0.68( 8)   +0.06(22)          --
    1840    -0.12(14)   -0.45(22)          --
    1850    -0.33(26)   -0.38(24)          --
    1860    -0.37(29)   -0.04(34)          --
    1870    -0.05(35)   +1.04(51)          --
    1880    -0.07(43)   +0.34(103)         --
    1890    -0.27(38)   +0.72(126)         --
    1900    -0.06(41)   +0.31(138)         --
    1910    -0.16(45)   +0.61(154)         --
    1920    -0.80(42)   +0.01(146)         --
    1930    -0.73(37)   +0.59(141)         --
    1940    -0.69(34)   +0.95(61)   -1.96(23)
    1950    -0.70(33)   -0.65( 9)   -1.66(29)
    1960    -0.45(20)   -0.07( 4)   -1.52(37)
    1970           --      (n=1)    -2.01(28)
    1980           --      (n=1)    -0.99(15)
    1990           --           --  -1.26(23)
    2000           --           --  -1.29(22)
    2010           --           --  -1.40(27)
```

Read the matrix with care. The very early French decades (1800 to 1820) sit high on matter, but each rests on only four to
fourteen issues from a handful of official and legal titles, so that is thin composition, not a reading of "the French press in
1800". The dense, trustworthy band is 1860 to 1940. There the French cells hover around zero with no staircase in either
direction; the English cells sit slightly on the manner side throughout and dip a little further after 1910. Norway sits well
onto the manner side across its whole 1940 to 2018 window, which is a level difference between countries, not a trend.

## The honest test — drift within a title

For each title with at least six issues spanning at least thirty years, regress its M on year; a positive slope means that paper
moved toward matter over its own life, a negative slope toward manner. Then aggregate the per title slopes per country.

| Country | Qualifying titles | Mean within title slope | One sample t | p | Toward matter | Verdict |
|---|---|---|---|---|---|---|
| **EN** | 16 | **-0.0062 /yr** | -1.42 | 0.18 | 6 of 16 | weak lean to manner, not significant |
| **FR** | 48 | **-0.0009 /yr** | -0.16 | 0.87 | 28 of 48 | **flat — no net drift** |
| **NO** | 3 | +0.0171 /yr | +0.94 | 0.45 | 2 of 3 | toward matter, underpowered, post 1940 |

France, the deepest and densest panel, is flat: over roughly 150 years the average French newspaper did not move toward matter
or toward manner. The individual titles scatter both ways and some of that scatter is real and large — the *Journal officiel*
and *Le Charivari* moved firmly toward matter (+0.085 p=0.002, +0.080 p=0.009), *Le Petit Oranais* and *Gil Blas* firmly toward
manner (-0.125, -0.088) — but there is no shared direction, so the mean is a null. England leans faintly toward manner but the
lean does not clear significance on the shared ruler. Norway's three papers lean the other way, toward matter, but three titles
starting in 1940 cannot speak to 1800 to 1960.

**The composition artefact, shown directly.** Pool every French issue and ignore the title, and M drifts toward manner at
-0.0049 /yr, p=0.044 — a "significant" trend. Measure the same corpus within title and it collapses to -0.0009 /yr, p=0.87. The
pooled trend is the changing mix of papers over the decades, not any paper changing. This is exactly the discipline the earlier
work paid for, reproduced in a second country.

**A note on the ruler.** The earlier England only read reported -0.0236 /yr, p=0.013 toward manner. That used a ruler
standardised on the English archive alone. On the shared three country ruler the English lean is the same direction but weaker
and not significant (-0.0062 /yr, p=0.18). The direction is robust; the significance is fragile to the choice of ruler, and the
honest statement is "a weak manner lean in England, no drift in France".

## Per axis — is affect rising?

Mean within title slope of each raw axis (x100 per year), which shows what is moving underneath M.

| Country | rigour | depth | affect | stance | register | originality | candour | commercial |
|---|---|---|---|---|---|---|---|---|
| EN | -0.11 | -0.09 | **+0.02** | -0.07 | -0.04 | -0.06 | -0.04 | +0.29 |
| FR | +0.02 | -0.02 | **-0.09** | +0.02 | +0.10 | -0.01 | +0.01 | -0.05 |
| NO | +0.09 | +0.05 | **-0.20** | -0.11 | +0.11 | +0.11 | +0.01 | +0.08 |

The one thread that does hold across all three countries is affect. **Affect does not inflate over 1800 to 1960** — it is flat
in England and falling in France and Norway. Sensational tone is not a thing the historical press acquired over time. Beyond
affect the countries diverge: England's matter axes (rigour, depth) fall while its commercial drive rises sharply; France's
register rises (more conversational) while its matter axes hold flat; Norway's substance axes rise. Different countries moved
different levers.

## The OCR confound

The floor was applied in preparation (France `ocr` at least 80, median kept 99; Norway language confidence at least 0.5) and OCR
was then carried as a covariate.

- **France**: OCR barely tracks year (r=+0.09) and barely tracks M (r=+0.07). Controlling for OCR leaves the pooled year slope
  essentially unchanged (-0.0055 versus -0.0049), and the high OCR half alone drifts toward manner slightly harder (-0.0112,
  p=0.003). Rising legibility is not manufacturing the French signal; if anything it works against it.
- **Norway**: OCR is uncorrelated with M and the high OCR half flattens to zero (+0.0009, p=0.92), which says the thin Norwegian
  matter lean is not robust.

OCR is therefore not the driver of what little movement there is. The larger caveat is not legibility but the scorer: it is one
7B model tuned on the modern English web, reading nineteenth century French full issues that mix front page prose with
advertisements and notices. That is out of its training distribution, and only the English leg carries the earlier Qwen plus
Claude panel cross check. The French and Norwegian legs are one scorer, and should be read as directional, not precise.

## Verdict

1. **Does press character drift over 1800 to 1960, toward matter or manner?** Within a title, essentially no. France, the deep
   panel, is flat (-0.0009 /yr, p=0.87). England leans weakly toward manner but not significantly on the shared ruler. The press
   voice is remarkably stable within a title across a century and a half. The archive wide "toward matter through line" the
   programme once saw is a composition artefact that dies under the within title test, in a second country now, not only in
   England.

2. **Is the drift consistent across countries?** No. England leans faintly to manner, France sits flat, Norway (thin, and post
   1940) leans to matter. There is no shared modernisation of the press voice — no common direction the world's newspapers
   travelled. What movement exists is specific to the country, and within France specific to the individual title.

3. **Does it echo the web era (affect flat, matter rising)?** Half, and the more interesting half. Affect is flat to falling
   everywhere in deep time, so the "affect flat" half of the web era finding extends back a century and a half — sensationalism
   is not a monotone historical acquisition. But matter does **not** rise within a title in deep time (flat in France, falling in
   England), so the "matter rising" half is a property of the digital web era, not a two century law. The long run toward matter
   story only appears when you let the composition change; hold the title fixed and it is gone.

**In one line:** the character of the press is far more stable across deep time than the web era drift suggested; the one durable
cross country regularity is that affect never inflated; and the apparent long run march toward matter is composition, not culture.

## Caveats, kept in view

- The matrix is a mosaic with holes: only France and England reach across 1800 to 1960; Norway is post 1940 and thin; the United
  States, New Zealand, Denmark, Iran and China corpora could not enter, each for a stated reason (no dated title, no body text,
  no usable dates, or modern only).
- One 7B scorer, web tuned, reading historical and non English registers out of distribution. Only England has the two model
  panel cross check.
- French records are full newspaper issues; the scorer reads the leading 6000 characters, which mixes lead prose with masthead
  and notices. England is cleaner article prose. This is a genre difference between the two deep legs.
- Significance of the England lean is fragile to the standardisation ruler; direction is not.

## Reproduce

- `scripts/prep_worldpress.py` — builds the within title samples for France and Norway with the OCR floor and per title decade caps.
- `scripts/analyse_press_drift.py` — the matrix, the within title slopes, the per axis slopes, the OCR confound check and the cross country consistency read.
- `analysis_output.txt` — the full captured run.
- Scored issues live on the NAS at `/mnt/nas/kronaxis/corpora/results/historical_press_drift/scored.jsonl` (1276 issues, resumable), England reuses the held `histchar/within_source_articles_only.jsonl`.

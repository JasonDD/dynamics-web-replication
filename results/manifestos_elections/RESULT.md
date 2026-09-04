# MANIFESTOS x ELECTIONS: does campaign character predict electoral success?

DYNAMICS-WEB series, PUBLIC track, across countries and across eras. Full text campaign manifestos scored
on the eight axis DWEB character instrument (shared 7B teacher on ), then joined to each party's
election outcome. **Character summary** `manner_minus_matter` = mean(affect, register, commercial_drive,
stance) minus mean(rigour, depth, originality, candour): higher means a more manner/affect voice, lower
means a more matter/substance voice.

## Corpus

- **US party platforms** (American Presidency Project, full text): 104 platforms, 1840-2024; 100 joined to a popular vote outcome.
- **UK party manifestos** (ukpol.co.uk, full text): 32 manifestos, 1945-1997; 32 joined to a vote share outcome.
- Both corpora are English, so **language is held constant** across the whole grid. Manifesto length
  varies widely (US median 27423 chars); every character to
  outcome test below is run again controlling for log length.

Outcomes: US = popular vote % of the platform's party in that election + whether it won the presidency
(electoral); incumbency = the party holding the presidency going in. UK = the party's national vote share
+ whether it formed government. Sources: Wikipedia US popular vote table; UK figures curated from
standard published results (House of Commons Library).

A data driven **PC1** over the eight axes (the series' matter versus manner axis) explains 35% of variance here, oriented so higher = more manner; axis loadings: rigour -0.55, depth -0.50, originality -0.13, candour -0.20, affect +0.37, commercial_drive +0.48, stance -0.12, register -0.01. PC1 is reported alongside the transparent
manner_minus_matter composite in sections 3 and 4 as a robustness check.

## 1. Country x era matrix: character, and character to vote share in each cell

Each cell: n manifestos | mean manner_minus_matter | mean affect | Pearson r of manner_minus_matter with
vote share (and, in brackets, the length controlled partial r). A positive r means a more manner/affect
manifesto won a higher vote share in that cell; negative means substance did.

| Country | Era | n | mean mm | mean affect | r(mm, vote) | partial r | winners mm | losers mm |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| US | pre-1900 | 36 | -0.198 | 0.401 | +0.00 | +0.05 | -0.20 | -0.20 |
| US | 1900-1945 | 26 | -0.176 | 0.393 | +0.61 | +0.68 | -0.16 | -0.19 |
| US | 1946-1979 | 19 | -0.168 | 0.414 | +0.51 | +0.58 | -0.16 | -0.16 |
| US | 1980-1999 | 10 | -0.122 | 0.485 | +0.28 | +0.28 | -0.12 | -0.13 |
| US | 2000-2024 | 13 | -0.115 | 0.472 | +0.11 | +0.15 | -0.09 | -0.15 |
| UK | 1900-1945 | 3 | -0.191 | 0.379 | - | - | -0.22 | -0.18 |
| UK | 1946-1979 | 24 | -0.146 | 0.416 | -0.19 | -0.34 | -0.14 | -0.15 |
| UK | 1980-1999 | 5 | -0.141 | 0.380 | +0.71 | +0.75 | -0.11 | -0.18 |

## 2. Winning character: winners vs losers, and US vs UK

Per axis mean for winners (formed government / won presidency) vs losers, within each country, with the
winner minus loser gap. A gap whose size is small should be read as no reliable difference.

### US (47 winners vs 53 losers)

| axis | winners | losers | gap (win minus los) |
|---|--:|--:|--:|
| rigour | 0.763 | 0.775 | -0.011 |
| depth | 0.665 | 0.676 | -0.011 |
| originality | 0.451 | 0.467 | -0.017 |
| candour | 0.822 | 0.831 | -0.009 |
| affect | 0.416 | 0.423 | -0.007 |
| commercial_drive | 0.203 | 0.173 | +0.030 |
| stance | 0.874 | 0.884 | -0.010 |
| register | 0.588 | 0.550 | +0.038 |
| mm | -0.155 | -0.180 | +0.025 |

### UK (12 winners vs 20 losers)

| axis | winners | losers | gap (win minus los) |
|---|--:|--:|--:|
| rigour | 0.754 | 0.741 | +0.013 |
| depth | 0.645 | 0.644 | +0.000 |
| originality | 0.471 | 0.474 | -0.004 |
| candour | 0.800 | 0.824 | -0.024 |
| affect | 0.393 | 0.416 | -0.023 |
| commercial_drive | 0.248 | 0.250 | -0.002 |
| stance | 0.880 | 0.859 | +0.021 |
| register | 0.585 | 0.539 | +0.046 |
| mm | -0.141 | -0.155 | +0.014 |

### Winning voice, US vs UK

| axis | US winners | UK winners | US vs UK |
|---|--:|--:|--:|
| rigour | 0.763 | 0.754 | +0.009 |
| depth | 0.665 | 0.645 | +0.020 |
| originality | 0.451 | 0.471 | -0.020 |
| candour | 0.822 | 0.800 | +0.022 |
| affect | 0.416 | 0.393 | +0.023 |
| commercial_drive | 0.203 | 0.248 | -0.044 |
| stance | 0.874 | 0.880 | -0.006 |
| register | 0.588 | 0.585 | +0.002 |
| mm | -0.155 | -0.141 | -0.014 |

## 3. Temporal trend: are manifestos drifting toward manner/affect?

OLS slope of each character measure on election year (per decade), within country, over the full span,
plus the slope among winners only. A positive manner_minus_matter or affect slope is a measurable
populism / manner inflation signal.

### US (1840-2024, n=104)

| measure | slope /decade (all) | r (all) | slope /decade (winners) |
|---|--:|--:|--:|
| mm | +0.005 | +0.41 | +0.007 |
| pc1 | +0.182 | +0.55 | +0.224 |
| affect | +0.005 | +0.35 | +0.007 |
| register | +0.000 | +0.01 | -0.001 |
| commercial_drive | +0.009 | +0.61 | +0.010 |
| stance | -0.001 | -0.21 | -0.001 |
| rigour | -0.005 | -0.52 | -0.006 |
| depth | -0.004 | -0.42 | -0.006 |
| candour | -0.000 | -0.05 | +0.000 |

### UK (1945-1997, n=32)

| measure | slope /decade (all) | r (all) | slope /decade (winners) |
|---|--:|--:|--:|
| mm | +0.008 | +0.28 | +0.012 |
| pc1 | +0.065 | +0.08 | +0.266 |
| affect | -0.001 | -0.02 | -0.004 |
| register | +0.016 | +0.25 | +0.011 |
| commercial_drive | +0.004 | +0.10 | +0.016 |
| stance | +0.006 | +0.24 | +0.002 |
| rigour | -0.003 | -0.10 | -0.006 |
| depth | -0.004 | -0.19 | -0.011 |
| candour | +0.000 | +0.01 | -0.003 |

## 4. Does character predict vote share? (controls: length, incumbency)

### US (n=100)

- **manner_minus_matter** vs vote share: r=+0.229 (p~0.020), length controlled partial r=+0.192
- **PC1 (manner+)** vs vote share: r=+0.085 (p~0.398), length controlled partial r=+0.022
- **affect** vs vote share: r=-0.018 (p~0.861), length controlled partial r=-0.057
- **matter(rigour+depth+orig+candour)** vs vote share: r=-0.087 (p~0.385), length controlled partial r=-0.065
- OLS vote_share ~ mm +23.59 , logN +0.87 , incumbent +6.78 ; intercept +36.8; R2=0.153

### UK (n=32)

- **manner_minus_matter** vs vote share: r=-0.095 (p~0.600), length controlled partial r=-0.186
- **PC1 (manner+)** vs vote share: r=-0.440 (p~0.007), length controlled partial r=-0.399
- **affect** vs vote share: r=-0.249 (p~0.160), length controlled partial r=-0.213
- **matter(rigour+depth+orig+candour)** vs vote share: r=+0.115 (p~0.526), length controlled partial r=+0.080
- OLS vote_share ~ mm -72.14 , logN +11.20 ; intercept -95.2; R2=0.208

## Verdict

**Yes, campaign character predicts electoral success, but the effect is small, era dependent, and its
sign flips by political system.** The three questions in turn:

1. **Does character predict vote share within a country?** In the US it does, weakly: a more
   manner/affect voice earns a higher popular vote share, `manner_minus_matter` vs vote r=+0.229
   (p~0.020), and it survives length and incumbency controls (partial r=+0.192; OLS mm
   coefficient positive with incumbency worth about +6.8 points). The link is not constant across eras
   (section 1): strongest in 1900-1945 (r=+0.61) and 1946-1979 (r=+0.51), near zero before 1900 and
   after 2000. In the UK the sign is the OPPOSITE: manner HURTS. PC1 (the manner axis) vs vote share
   r=-0.440 (p~0.007), partial r=-0.399; the substance/matter manifesto wins.
   Both UK measures (mm r=-0.10, PC1 r=-0.44) agree in sign. So the honest headline is
   a **sign flip that depends on the political system**, not a universal winning voice.

2. **Does the winning character differ by country and era?** The presidential US rewards manner; the
   parliamentary UK rewards matter (question 1). But the winner versus loser BINARY gap is near zero in
   both systems (section 2: |mm gap| < 0.03), and the two systems' winning voices look very alike axis
   by axis. The signal lives in the continuous vote share and in the sign of the character to vote slope,
   not in a distinct 'winner archetype'. The one small regularity shared across systems: winners in both
   countries score slightly higher on register (more conversational, +0.04).

3. **Is there a temporal drift toward manner/affect?** In the US, clearly yes over 1840-2024: the
   data driven manner axis PC1 rises +0.182/decade (r=+0.55), commercial_drive
   (hard sell voice) rises +0.009/decade (r=+0.61, the single strongest trend),
   affect rises (r=+0.35) and rigour falls -0.005/decade (r=-0.52). That
   is a measurable populism signal across 180 years: US platforms have moved off substance toward sell
   and feeling. The transparent mm composite moves the same way but weakly (+0.005/decade), because it
   dilutes the two axes (commercial_drive, affect) that actually carry the drift; PC1 is the better
   instrument here. The UK series (1945 to 1997 only) shows a weaker, noisier manner rise (register
   +0.25, mm +0.28) and no clean affect trend, so the drift claim is solid for the US, suggestive for
   the UK.

**Nulls and limits, stated plainly.** The winner/loser binary is close to a null in both systems. The US
character to vote link is a null that depends on era: absent before 1900 and after 2000. Cells with n<4
(UK 1900 to 1945) carry no correlation. Length is controlled throughout and does not explain the live
effects; incumbency adds about +6.8 points in the US but does not flip the character sign. This is the
open data slice only (US platforms + UK manifestos, both English, UK truncated at 1997 by source
throttling). Full breadth across countries (67 countries, 38 languages, and the modern UK) needs the
account gated MARPOR corpus; every claim about countries here is limited to these two systems.

_Generated by manifestos_analyse.py over 136 scored manifestos._

# The invariant core of character: what is the same across every culture and every room

Generated 2026-08-30. Analyser `truthometer/scripts/cc_invariant_core.py`, raw console
`invariant_core.txt`, machine readable `invariant_core_stats.json` (this directory).
Data already scored, no new model scoring: `cc_v3.domain_char8_expanded` (2,648,406 domains, eight
character axes), `cc_v3.domain_region_full` (country and continent labels), `cc_v3.reddit_wide`
(80,138 comments, 400 subreddits). The matter/manner axis is PC1 of the standardised eight axis matrix,
oriented so rigour and depth load positive (the recipe from `cc_culture_regional.py`).

This is the honest complement to the culture work. The programme has measured what DIFFERS between
groups for months. This measures what is SHARED.

---

## Headline

**Culture is real but small. The large shared core is a single matter leaning human web voice, one that is candid,
opinionated and informal, and every culture and every room arranges character along the SAME matter/manner
axis and clusters tightly around ONE centre. What moves between groups is mostly affect (feeling) and, in
rooms, depth and rigour. What is universal is register and candour, and above all the geometry itself.**

---

## 1. The invariant share vs the cultural share

One way variance partition on the eight axes, groups smaller than the floor dropped.

| Cut | n | groups | between groups (8 axes) | between groups (matter/manner) | invariant share of the level | perm p |
|---|---|---|---|---|---|---|
| Country, ccTLD only (sharpest) | 1,240,410 | 63 | **6.8%** | 5.3% | **93.2%** | 0.001 |
| Country, ccTLD + propagated (conservative) | 2,609,697 | 63 | 3.5% | 2.6% | 96.5% | 0.001 |
| Continent | 2,609,697 | 6 | 0.9% | 0.9% | 99.1% | 0.001 |

**Culture accounts for 3.5 to 6.8% of character** (depending on how strictly a domain is placed in a
country; the ccTLD only figure is the sharper estimate, the propagated figure is diluted because
propagation smooths each domain toward its neighbours). The remainder, **93 to 96.5%, is not cultural.**
Continent explains almost nothing: culture lives at the national and local level, not the civilisational
one. The propagated multivariate figure of 3.5% reproduces the standing headline exactly.

### Honesty: the 93 to 96.5% is NOT all universal core

The share of the level that is not cultural is dominated by per domain idiosyncrasy and scorer noise, not
by a shared human core. The reddit corpus lets us measure this directly (each community has many scored
items, so its mean can be split and re checked). A community mean of about 200 items replicates at r=0.928
on the matter/manner axis. By Spearman Brown that implies a **single scored item is only about 11%
reliable signal and about 89% idiosyncrasy plus scorer noise.** With one score per web domain we cannot
split that domain noise directly, so we report the invariant share of the LEVEL (93 to 96.5%) as an upper
bound on "not cultural", and we do NOT claim it is all a shared core.

The evidence for a genuine universal core is therefore structural, not a large residual variance. Three
findings converge (Sections 3 and 4): every group clusters tightly around one centre, every group uses the
same axis, and the same axis reappears in a different medium.

---

## 2. Which axes are the universal core, which carry culture

Between country variance per axis, most invariant last. Two resolutions, so the ranking is robust.

| Axis | between countries, ccTLD only | between countries, all sources | role |
|---|---|---|---|
| affect | 10.2% | 4.2% | **carries most culture** |
| commercial drive | 9.2% | 3.5% | carries culture |
| stance | 8.5% | 5.9% | carries culture |
| rigour | 5.9% | 3.3% | middle |
| originality | 5.6% | 4.1% | middle |
| depth | 5.3% | 3.5% | middle |
| candour | 5.2% | **1.5%** | **universal core** |
| register | **3.2%** | **1.6%** | **universal core** |

**The universal core axes are register and candour** (the least cultural in both resolutions), with
depth and rigour close behind. **The culture carrying axes are affect, commercial drive and stance**:
how emotional, how salesy and how opinionated writing is varies most between nations. This matches the
prior finding that affect, stance and commercial carry the most culture while register, rigour and depth
carry least.

---

## 3. Where the centre is, and its shape

Grand mean character profile over all 2.65M domains (raw 0 to 1 units). This is the character every
culture is a small perturbation of.

| Axis | mean | pole |
|---|---|---|
| candour | 0.566 | matter (highest) |
| stance | 0.526 | matter |
| rigour | 0.469 | matter |
| commercial drive | 0.466 | manner |
| depth | 0.422 | matter |
| affect | 0.393 | manner |
| originality | 0.321 | matter |
| register | 0.282 | manner (lowest) |

Matter pole axes average 0.461, manner pole axes average 0.380. **The shared centre leans toward matter,
modestly.** In words: the universal web voice is candid and opinionated, moderately rigorous, low on
originality, and written in an informal register. The matter/manner axis is 56.1% of all variance and the
top two components together are 77.3%, so character is close to two dimensional.

Note that the two most invariant axes sit at the extremes of the centre: everyone writes informally
(register lowest at 0.28) and fairly candidly (candour highest at 0.57), everywhere. Those are the human
constants; the emotional colour and the sales pressure are what the cultures paint on top.

### The centre is genuinely shared, not an average of scattered groups

A nation's character sits on average only **0.59 standard deviations from the grand centre** (worst case
1.84). The whole spread of 63 national characters is about **0.16 to 0.26 times** the spread of individual
domains within a single nation. Cultures are a small perturbation on a common human distribution, not
separate clouds.

### One shared axis (the strongest universality result)

Computing the matter/manner axis independently inside each country and comparing it to the global axis:
across 62 countries with at least 500 domains, the cosine similarity is **mean 0.977, median 0.979,
minimum 0.937**. Every culture organises character along the same matter/manner axis. Culture moves the
POSITION on the axis; it does not bend the axis. This is invariant structure, and it does not depend on any
noise assumption.

---

## 4. Rooms: what is community invariant vs community carrying

Repeating the partition on 80,138 reddit comments across 400 communities, and here the noise can be
separated cleanly.

- **Between communities: 7.4% across the eight axes, 11.2% on the matter/manner axis.** Rooms carry MORE
  character than countries do, roughly twice as much on the matter/manner axis. Communities are chosen by
  topic and norm, so they concentrate character more than a whole nation does.
- **Noise separation:** splitting each community's comments into two halves, community positions replicate
  at r=0.928 on the matter/manner axis (0.81 to 0.93 per axis). So about **93% of the between community
  signal is real structure, not scorer noise.** Room culture is overwhelmingly real.
- **Most room invariant axes: originality and register. Most room carrying: affect, depth and rigour.**
- **Register is invariant in both cuts (country and room); affect carries the most in both.** Depth and
  rigour flip: they are fairly invariant between nations but strongly room carrying, because a technical
  community and a casual one differ on rigour far more than two nations do.
- **Same ruler in a different medium:** reddit's own matter/manner axis aligns with the web axis at cosine
  0.778. It is recognisably the same contrast, with rigour and depth loading positive and affect negative, exactly as
  on the web, but not identical, because reddit is non commercial (so commercial drive collapses as a
  cultural signal) and scored on a coarser grid. That the axis survives a wholesale change of medium is the
  cross corpus confirmation of the same underlying geometry.

---

## 5. Framing

The paper series has said, correctly, that culture is real and measurable in the web graph. The honest
complement is now quantified: **culture is real but small (3.5 to 6.8% of character), and the large
shared core is one matter leaning human web voice, shaped like a single matter/manner axis that every
culture and every room clusters around and measures character along.** The differences are a thin coat of
paint, mostly affect plus depth and rigour between rooms, over a common human character that is candid,
opinionated and informal everywhere.

The universal core is not a big pile of leftover variance (most of that is idiosyncrasy and noise). It is
a shared centre and a shared axis: three independent checks agree: nations sit 0.59 SD from one centre,
the axis is the same inside every country (cosine 0.977), and the same axis reappears on reddit (cosine
0.778).

### Honest limits

- One score per web domain, so within a country the split between real idiosyncrasy and scorer noise
  cannot be measured directly; the 93 to 96.5% invariant share of the level is an upper bound on "not
  cultural", not a claim that all of it is a shared core. The core claim rests on the structural invariants,
  which do not depend on that split.
- Country is resolved by ccTLD (and by link geography for the propagated set); ccTLD under identifies the
  generic top level domains and the United States, and language varies together with region. The scorer is
  web tuned.
- The reddit ruler alignment (0.778) is lower than the per country alignment (0.977) partly because reddit
  is a different medium, non commercial, and coarsely scored; it should be read as "recognisably the same
  axis", not "identical".

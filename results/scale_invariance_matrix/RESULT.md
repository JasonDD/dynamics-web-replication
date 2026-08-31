# Scale invariance matrix: is character structure fractal?

**Track:** PUBLIC. **Kind:** analysis only, no new scoring. **Date:** 2026-08-31.
**Scripts:** `truthometer/scripts/cc_scale_invariance.py` (the matrix),
`truthometer/scripts/cc_scale_agg_control.py` (the aggregation control).
**Artefacts:** `scale_invariance.json`, `scale_agg_control.json` (this directory).

## Question

Paper 4 raised the fractal self similarity idea: does the two dimensional matter/manner
character structure hold at every SCALE, or does it change as you coarsen? We test it as a
matrix on already scored data at four nested aggregation scales, across two substrates.

| Substrate | Fine scale | Coarse scale |
|---|---|---|
| Reddit | POST, individual scored posts (`cc_v3.reddit_wide.char`, 80,138) | COMMUNITY, per subreddit means (400 subreddits, ~200 posts each) |
| Web | DOMAIN, scored web domains (`cc_v3.domain_char8_expanded`, 2,648,406) | CORPUS, atlas segment means (2,070 topic/genre/quality/authority cells) + 17 curated corpus means |

Note on the operator brief: the reddit set is 80,138 scored POSTS across exactly 400 subreddits
(the "78k / community means" figure was the post count). Method: at each scale, standardise the
8 axes WITHIN that scale, run SVD, orient PC1 toward matter (rigour plus depth positive), then
compare directions and dimensionality across scales. Standardising within scale absorbs absolute
level differences between substrates, so only the correlation geometry, the shape, is compared.

## Scale x structure

| Scale | n | PC1% | PC2% | PC1+2% | eff. dim | #comp for 90% | matter/manner sign match |
|---|---:|---:|---:|---:|---:|---:|---:|
| POST (reddit posts) | 80,138 | 30.2% | 18.4% | 48.6% | 5.63 | 6 | 75% |
| COMMUNITY (subreddit means) | 400 | 39.0% | 19.9% | 58.9% | 4.19 | 5 | 50% |
| DOMAIN (web domains) | 2,648,406 | 56.1% | 21.2% | 77.3% | 2.61 | 3 | 100% |
| CORPUS (atlas segments) | 2,070 | 71.6% | 16.6% | 88.2% | 1.83 | 3 | 100% |
| CORPUS (curated corpora) | 17 | 47.6% | 24.2% | 71.8% | 3.25 | 4 | 88% |

Effective dimensionality is the participation ratio, (sum of eigenvalues) squared over sum of
eigenvalues squared: how many axes really carry the variance. Sign match is the share of the 8
axes whose PC1 pole agrees with the web reference pattern (matter pole: rigour, depth, originality,
candour, stance; manner pole: affect, commercial drive, register).

### PC1 loadings (matter oriented)

| Scale | rigo | dept | orig | cand | affe | comm | stan | regi |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| POST | +0.60 | +0.58 | +0.12 | +0.19 | -0.44 | +0.06 | +0.21 | +0.11 |
| COMMUNITY | +0.53 | +0.49 | -0.18 | -0.05 | -0.51 | +0.09 | +0.29 | +0.29 |
| DOMAIN | +0.44 | +0.40 | +0.23 | +0.39 | -0.35 | -0.26 | +0.37 | -0.34 |
| CORPUS (atlas) | +0.41 | +0.37 | +0.27 | +0.37 | -0.31 | -0.36 | +0.35 | -0.37 |
| CORPUS (curated) | +0.47 | +0.48 | +0.28 | +0.31 | -0.21 | -0.28 | +0.28 | +0.41 |

### Cross scale PC1 cosine (|cos| of the matter oriented loading vectors)

|  | POST | COMMUNITY | DOMAIN | CORPUS atlas | CORPUS cur |
|---|---:|---:|---:|---:|---:|
| **POST** | 1.000 | 0.896 | 0.778 | 0.713 | 0.837 |
| **COMMUNITY** | 0.896 | 1.000 | 0.535 | 0.452 | 0.707 |
| **DOMAIN** | 0.778 | 0.535 | 1.000 | 0.991 | 0.692 |
| **CORPUS atlas** | 0.713 | 0.452 | 0.991 | 1.000 | 0.672 |
| **CORPUS cur** | 0.837 | 0.707 | 0.692 | 0.672 | 1.000 |

Minimum pairwise PC1 cosine across scales = 0.452. Effective dimensionality range 1.83 to 5.63.

## Is the collapse real, or just averaging?

The obvious worry: coarse aggregates average over items and over length, so PC1 could rise for
purely mechanical reasons. We ran the control directly. Take the 80,138 posts and group them into
400 RANDOM groups of ~200 (matching the 400 real subreddits), then compare.

| Grouping | PC1% | PC2% | eff. dim |
|---|---:|---:|---:|
| POST (no grouping) | 30.2% | 18.4% | 5.63 |
| RANDOM 400 groups | 30.3% | 18.2% | 5.62 |
| REAL subreddits (400) | 39.0% | 19.9% | 4.19 |

Random grouping does not move PC1 at all (+0.1pp; eff. dim 5.63 to 5.62). Because standardising
per column rescales every column's between group variance by the same factor, random aggregation
preserves the correlation geometry exactly. Real subreddit grouping raises PC1 by +8.7pp and drops
a full effective dimension. So the coarse scale collapse is GENUINE between community structure, not
an artefact of averaging. Communities and corpora sit on a flatter, more matter/manner concentrated
manifold than the individual items inside them do.

## Verdict: directionally fractal, not fully scale invariant

**1. The leading axis is scale invariant within a substrate.** On the web, the domain axis and the
atlas segment axis are the SAME matter/manner axis to within measurement noise (cosine 0.991, both
100% sign match, near identical loadings). The rigour plus depth versus affect backbone is present
at every scale in every substrate. In direction, the structure is self similar: the same ruler
reads at post, community, domain and corpus scale.

**2. The dimensionality is NOT scale invariant: the space flattens as you coarsen.** PC1 share
climbs monotonically 30% (post) to 39% (community) to 56% (domain) to 72% (atlas), and effective
dimensionality falls 5.63 to 4.19 to 2.61 to 1.83. Fine items fill a rich roughly 5 dimensional
character space; coarse aggregates live on a nearly 1 dimensional matter/manner line. The control
above shows this is real, not mechanical. A strict fractal would keep the SAME 2D shape at every
scale; character does not. It keeps the same leading DIRECTION while collapsing toward a line.

**3. Across substrates the axis rotates.** Reddit PC1 is a narrower "effort" axis, rigour and
depth against affect, where candour, register and commercial drive do NOT join the manner pole the
way they do on the web (POST sign match 75%, COMMUNITY 50%; cosine to DOMAIN 0.78 and 0.54). So the
axis is not universal across platforms; it takes a substrate specific flavour, which agrees with the
community residual and distinct fields results. The web ladder (domain to corpus) is far more self
similar than the reddit to web comparison.

### Honest caveats

- The reddit and web ladders are different substrates measured by the same 7B instrument; the
  clean within substrate nesting is domain to atlas (cosine 0.991) and post to community (0.896),
  not the reddit to web pairs.
- The atlas segments are binned partly BY quality and authority, which themselves track matter/manner,
  so some of the atlas collapse to 1.83 dimensions is by construction: those bins are chosen to
  separate the very thing PC1 measures. The domain scale (2.6M unbinned domains, eff. dim 2.61) is
  the cleaner coarse web number and already shows the collapse.
- Length is confounded with scale: coarser aggregates average over longer and more varied text. The
  random grouping control removes the pure averaging component, but not a genuine length to character
  correlation, which the length mechanism result handles separately.
- The 17 curated corpora are a small, deliberately spread set (troll text to old bailey to scripture);
  their axis (cosine ~0.69 to the web) sits between reddit and web, consistent with the field structure
  finding that a curated small corpus is not the 2.6M web.

**One line:** character structure is DIRECTIONALLY fractal: the matter/manner axis is the same at
every scale within a substrate, but it is NOT fully scale invariant: the space genuinely collapses
from about five effective dimensions at the item level to roughly one at the corpus level, and the
axis takes a substrate specific flavour across platforms.

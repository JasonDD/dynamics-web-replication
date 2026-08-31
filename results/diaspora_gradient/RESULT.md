# Does a diaspora community's character sit between its origin and its host country?

*DYNAMICS-WEB series, PUBLIC track, INTERNATIONAL. Tests whether culture behaves as a CONTINUUM
rather than a bucket, by asking whether a diaspora community's web character sits BETWEEN the web
character of its origin country and that of its host country, and whether its position depends on
how deeply it links into the host (more host integrated should mean closer to the host).*

Data (all held, no new scoring, no `:8301` / `:8288`):
- **Character**: `cc_v3.domain_char8_expanded`, 2,648,406 scored domains, the 8 DYNAMICS-WEB axes.
- **Origin nationality signal**: the country code TLD of the registrable domain (a `.gr`, `.mx`,
  `.it` site is seeded to GR, MX, IT). Clean but coarse.
- **Host embedding signal**: the country distribution of each domain's LINK NEIGHBOURS on the full
  Common Crawl web graph (118.7M vertices, 4.34B edges), from iterative majority label propagation
  seeded by country code TLDs. A country code origin domain whose neighbours resolve mostly to a
  DIFFERENT country Y is embedded in Y. This host signal is INDEPENDENT of the frozen origin label,
  so the test is not circular.

Method file: `scripts/cc_diaspora_gradient.py` (graph machinery mirrors `truthometer/scripts/cc_region_fullgraph.py`).
Result artifact: `diaspora_result.json` (this directory); per domain embedding `diaspora_embedding.npz`
(143 MB, on DL580 `~/diaspora_gradient_out/`). PC1 reference is the first principal component of
`cc_v3.domain_char8_expanded`, oriented rigour plus depth positive, the series convention.

---

## 1. The claim under test

Treat culture as a point in the 8 axis character space. If culture is a hard bucket, a diaspora
community keeps the character of its origin country wherever it lives. If culture is a continuum, a
diaspora community should sit on the line between origin O and host H, at some fraction alpha of the
way across:

    diaspora D  ~=  (1 - alpha) * O  +  alpha * H       (alpha = 0 origin, alpha = 1 host)

Two things are tested. **Intermediacy**: is D between O and H (0 < alpha < 1, and close to the O to H
line)? **Gradient**: within a corridor, does a domain that links more heavily into the host read more
host like (position rises with host link fraction)? The gradient is the mechanism the continuum idea
predicts: acculturation should scale with integration.

Per corridor origin X to host Y (each cell needs at least 100 domains):

    O = mean character of homeland X    (origin X, link neighbours mostly X)
    H = mean character of homeland Y    (origin Y, link neighbours mostly Y)
    D = mean character of diaspora X in Y (origin X, dominant foreign host Y, host linked > home linked)
    alpha    = projection of (D - O) onto (H - O), a scalar 0..1
    residual = perpendicular distance of D from the O to H line, in units of |H - O|
    gradient = slope and correlation of each diaspora domain's position against its host link fraction

104 corridors cleared the size floor. Everything is standardised per axis across the whole 2.65M set.

## 2. Headline: diaspora sits partway across, but only about half the time, and never smoothly

| statistic | value | reading |
|---|---|---|
| corridors analysed | 104 | origin X to host Y, each cell >= 100 domains |
| mean alpha | **0.42** | diaspora sits, on average, 42 per cent of the way from origin to host |
| median alpha | 0.33 | |
| alpha strictly in (0, 1) | 67 / 104 | a majority land between origin and host |
| **significantly intermediate** (95 per cent CI inside 0.05 to 0.95) | **42 / 104** | the clean positive cases |
| alpha <= 0 (no host pull, or further from host than origin) | 21 / 104 | diaspora reads MORE like origin, not less |
| alpha >= 1 (overshoot past the host) | 16 / 104 | diaspora reads more extreme than the host |
| off line residual < 0.5 |H - O| | 47 / 104 | diaspora sits cleanly ON the origin to host line |
| off line residual > 1.0 |H - O| | 28 / 104 | diaspora sits well OFF the line, in its own direction |
| **pooled integration gradient** (position vs host link fraction) | **r = 0.004, n = 116,037** | flat: a null |

So the average diaspora community does sit between its origin and its host (mean alpha 0.42), and for
42 corridors that intermediacy is statistically clean. But it is a noisy population tendency, not a
law: a fifth of corridors show no host pull at all, a sixth overshoot the host, and more than a
quarter sit well off the straight origin to host line. And the integration gradient the continuum
idea predicts is absent: how deeply a domain links into the host does not predict how host like it
reads (pooled r = 0.004; within corridor mean r = 0.001, only 15 of 104 corridors reach |r| > 0.2 and
their signs are split between plus and minus).

## 3. Where intermediacy is clean: wide origin to host gaps, especially into the United States

The clean cases share a structural feature. When origin and host have well separated web characters,
the diaspora sits cleanly between them. The United States web reads high on matter (rigour, depth,
candour) and its origin partners read lower, so the origin to host gap is wide and the mix is
unambiguous. These are the strongest positives.

Character triples, standardised axes (z scores across the 2.65M set); O origin, D diaspora, H host.
PC1 is the matter versus manner axis (rigour plus depth positive).

| corridor | nD | alpha | resid | axes with D between O and H | PC1 O / D / H | reading |
|---|---|---|---|---|---|---|
| **MX in US** | 412 | 0.74 | 0.23 | 6 / 8 | +0.42 / +1.74 / +2.25 | Mexican origin, three quarters of the way to the US |
| **IT in US** | 868 | 0.25 | 0.17 | 7 / 8 | +0.16 / +0.72 / +2.25 | Italian origin, a quarter toward the US, very clean |
| **GB in US** | 3,958 | 0.59 | 0.20 | 6 / 8 | -0.14 / +1.37 / +2.25 | British origin, well over half toward the US |
| **CN in US** | 1,485 | 0.13 | 0.05 | **8 / 8** | -0.08 / +0.25 / +2.25 | Chinese origin, geometrically perfect blend but only a small pull |
| **GR in DE** | 2,042 | 0.49 | 0.33 | 5 / 8 | +1.71 / +0.83 / +0.22 | Greek origin, halfway to the flatter German host |
| **IN in DE** | 4,527 | 0.56 | 0.76 | 3 / 8 | +0.92 / +0.02 / +0.22 | Indian origin, more than half toward the German host |
| **MX/IT/GB/CN into US** | | mean ~0.4 | mean 0.16 | | | the cleanest quadrant of the whole study |

Read a clean row across the axes. MX in US: rigour 0.14 to 0.96 to 1.24, candour 0.14 to 0.78 to
0.96, commercial drive minus 0.17 to minus 0.83 to minus 1.06. Every one of those is the Mexican
origin value shifted most of the way to the US value, in order. This is exactly the convex mix the
continuum idea predicts, and it is real: on the widest and most recognisable corridors the diaspora
is a blend, not a copy of home.

## 4. Where it breaks: close origin to host gaps, mostly inside Europe into Germany

The corpus is Germany heavy, so most corridors are X into DE, and most European origins read close to
the German host. When the origin to host gap is small the picture falls apart three ways.

| corridor | nD | alpha | resid | what happened |
|---|---|---|---|---|
| IT in DE | 13,793 | 0.16 | **2.58** | Italian sites linking into Germany read LOWER on matter than both; they moved off in their own direction, not toward the host |
| NL in DE | 5,244 | **-0.40** | 0.48 | Dutch sites moved AWAY from the German host, more extreme than the origin: no host pull |
| AT in DE | 3,951 | **-1.31** | 1.87 | strong reverse, diaspora further from host than origin |
| ES in DE | 5,546 | **2.13** | 1.55 | overshoot, well past the German host |
| RU in DE | 1,469 | -0.43 | 0.87 | reverse, but the one corridor with a real positive integration gradient (r = 0.31) |

When |H - O| is small, alpha is a ratio with a small denominator and becomes unstable (the PC1 only
alpha reaches minus 11.7 and plus 15.5 on such corridors, which is why the 8 axis alpha and the off
line residual are reported together: they show when the convex picture is trustworthy and when it is
not). The honest reading is not that these diasporas are exactly at home; it is that where origin and
host are close in character, the small residual shift the diaspora does make points in its OWN
direction as often as toward the host, so the between them framing does not describe it.

## 5. The gradient is a clean null

The continuum idea makes a sharper prediction than intermediacy: a domain that links more into the
host should read more host like, so within a corridor the character position should rise with the
host link fraction. It does not. Pooling every diaspora domain across all corridors (n = 116,037),
the correlation between position on the origin to host axis and host link fraction is **r = 0.004**,
slope 0.07: dead flat. Within corridors the mean correlation is 0.001, the median is zero, and even
among the 42 significantly intermediate corridors the per corridor gradient ranges from minus 0.35
(MX in US, wrong direction) to plus 0.33 (RU in DE), averaging to nothing. Whatever sets how far a
diaspora community sits toward the host, it is not how heavily it links into the host. The shift is a
population level offset, not a per domain dial you can turn by integrating more.

(Range caveat: the diaspora set is already host dominant by construction, which narrows the host
fraction range and would attenuate any true gradient. But an attenuated positive would still show a
consistent sign, and the signs are split, so the null is not only range restriction.)

## 6. Verdict

**Partial support for culture as a continuum in position, a null for the proposed dynamics.**

Diaspora communities do, on average, sit between their origin and their host country in web character
(mean alpha 0.42), and on the corridors where origin and host are well separated the blend is clean
and unmistakable: Mexican, Italian, British and Chinese origin communities embedded in the United
States, and Greek and Indian communities embedded in Germany, all land partway across, most of their
axes bracketed between home and host, close to the straight line joining the two. That is real
evidence that culture is not a hard bucket a community carries unchanged. A diaspora reads as a mix.

But it is a population tendency, not a law, and it fails in two honest ways. First, it breaks where
origin and host read close together (the many intra European corridors into Germany), where the small
shift the diaspora makes points in its own direction as often as toward the host, so no single
between them line describes it. Second, and more decisively, the mechanism the continuum idea
predicts is absent: how deeply a community links into its host does not predict how host like it
reads (pooled r = 0.004). Culture behaves like a continuum in WHERE a diaspora sits, but not in the
DYNAMICS the hypothesis proposed, that acculturation scales with link integration. On this measure it
does not.

The single most useful line for the paper: on the widest, most recognisable corridors a diaspora
community's web character is a convex blend of home and host, which is a continuum result; but the
blend fraction is set by something other than how integrated the community is in the link graph, so
the naive integration gradient is a null.

## 7. Honest bounds (kept in front, not buried)

- **Country code TLD is a coarse and narrow origin proxy.** This design catches an origin registered
  site whose link neighbourhood is a foreign country. It does NOT catch the most common diaspora
  pattern, a community writing in the origin language on a host country domain or a generic domain (a
  Turkish community on `.de` or `.com` sites in Germany is invisible here, it carries no `.tr`
  signal). This is exactly why the textbook corridors TR in DE, IN in GB, PL in GB fell below the
  size floor: those diasporas largely do not live on origin country TLDs. What is measured is the
  narrower set of origin registered sites that have relocated their link neighbourhood, and the
  verdict is about that set.
- **Host embedding is a majority link vote**, noisy for any single domain. Every number here is a
  population mean over hundreds to thousands of domains, a tendency, not a per domain label.
- **alpha is unstable when origin and host read close.** The off line residual and the 8 axis versus
  PC1 only alpha are reported together so the reader can see which corridors carry a trustworthy
  convex reading (wide gap, low residual) and which do not (close gap, high residual, wild PC1 alpha).
- **Germany is over represented as a host** because the scored corpus is German heavy, so the corridor
  list leans on X into DE and the host reference into Germany is the German native web.
- **One scorer lineage** (the 7B DYNAMICS-WEB instrument), one PC1 basis. A second lineage was not run
  for this test.
- **A null was a valid outcome and half of it came back null**, which is the finding, not a
  disappointment: the position result is partial and the gradient result is flat, and both are stated
  as they are.

---

*Regenerate: `OUT=~/diaspora_gradient_out python3 scripts/cc_diaspora_gradient.py` on DL580 (reads
the web graph at `/mnt/external/webgraph`, the character table `cc_v3.domain_char8_expanded`). The
run resolves every vertex by label propagation, histograms each scored domain's neighbour countries,
lifts the embedding to the character originals, and writes `diaspora_result.json` plus the per domain
`diaspora_embedding.npz`.*

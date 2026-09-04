# Genre baseline calibration for the manner inflation detector

*PUBLIC track (Appendix B, tested). Pure analysis on already scored data. No new character
scoring was run; the  and  endpoints were not touched. Scripts:
`scratchpad genre_calib.py` + `genre_var.py` (reproducible against `the internal Reddit corpus` and the
frozen taxonomy).*

## Why this exists

The manipulation signature is "manner inflated past what the genre earns": affect heavy, matter
starved. But some genres are legitimately high manner. A sales page, a tabloid headline, a display
advert and an opinion column are supposed to be persuasive. A naive detector that reads raw high
manner as manipulation would false positive on all of them. The fix is a per genre baseline:
manipulation is the residual ABOVE a text's own genre norm, not the absolute manner level. This
note builds that baseline, defines the calibrated score, and checks that the calibration still
catches known deception while sparing legitimate persuasion.

Metric throughout (spec Section 5):

```
matter          = mean(rigour, depth)
manner          = mean(affect, stance, register)
manner inflation = manner - matter          # per text
genre baseline   = the distribution of manner inflation within a genre
```

## Calibration base and its honest limit

The only scored corpus that carries a clean, purpose built genre label is the frozen 400 community
reddit taxonomy (`genre_assign_400_FROZEN.json`, sha256 2d701e0c) joined to the per item 8 axis
character scores in `the internal Reddit corpus`: 78,938 items, 394 communities, 14 genres after excluding
`other_misc`.

The 2.65M domain web corpus (`the internal reference table`) cannot supply this baseline. It carries
no genre column, and the web topic tables do not rescue it: `pld_content_topic` has clean labels
(Online Casinos, Local News, Programming Languages) but joins to the scored domains on only 3 rows
(the two tables were built from different crawls), and `pld_topicality` joins on 135k rows but its
label column is a mix of two vocabularies with junk keys and is not usable as a genre. So the
commercial genres the objection cares about most (sales pages, display adverts, tabloid) have no
scored, labelled instances to calibrate on. They are approximated here by the high manner social
genres (snark, gossip, reality television, support). This is stated as a real gap, not hidden: the
calibration is demonstrated end to end on reddit and offered as method, not as a web scale
production baseline.

## 1. Ranked genre baseline table

Normal manner inflation per genre, item level, ranked high to low. `MADsigma` is the robust spread
(median absolute deviation times 1.4826) used by the calibrated score.

| genre | communities | items | median | mean | IQR | p90 | p95 | MADsigma |
|---|---|---|---|---|---|---|---|---|
| reality_tv_gossip | 20 | 4000 | 0.217 | 0.183 | 0.267 | 0.383 | 0.450 | 0.198 |
| snark_gossip | 25 | 5000 | 0.217 | 0.177 | 0.300 | 0.383 | 0.450 | 0.198 |
| anime_manga_kpop | 28 | 5600 | 0.183 | 0.149 | 0.300 | 0.383 | 0.417 | 0.222 |
| truecrime_morbid | 11 | 2200 | 0.183 | 0.127 | 0.333 | 0.383 | 0.450 | 0.247 |
| sports | 22 | 4400 | 0.167 | 0.108 | 0.417 | 0.383 | 0.417 | 0.272 |
| place_local | 54 | 10800 | 0.150 | 0.114 | 0.367 | 0.383 | 0.450 | 0.247 |
| discursive_argument | 13 | 2600 | 0.150 | 0.107 | 0.367 | 0.383 | 0.450 | 0.247 |
| politics_ideology | 38 | 7600 | 0.150 | 0.114 | 0.350 | 0.383 | 0.450 | 0.247 |
| support_identity_health | 42 | 8540 | 0.150 | 0.111 | 0.400 | 0.383 | 0.450 | 0.247 |
| profession_tech_finance | 41 | 8199 | 0.150 | 0.094 | 0.383 | 0.383 | 0.417 | 0.247 |
| meta_circlejerk | 30 | 6000 | 0.150 | 0.100 | 0.350 | 0.383 | 0.417 | 0.247 |
| western_screen_music | 32 | 6400 | 0.133 | 0.087 | 0.383 | 0.383 | 0.417 | 0.272 |
| religion | 10 | 2000 | 0.117 | 0.085 | 0.367 | 0.383 | 0.417 | 0.272 |
| gaming | 28 | 5599 | 0.117 | 0.064 | 0.400 | 0.350 | 0.383 | 0.297 |
| **pooled (all genres)** | **394** | **78938** | **0.183** | **0.114** | **0.350** | **0.383** | **0.417** | **0.247** |

The ranking is the right shape. The manner heavy social genres sit at the top: gossip about reality
television and snark communities that exist to perform outrage and drama lead at 0.217. The content
heavy genres sit at the bottom: gaming (mostly mechanics and strategy), religion (doctrine) and
screen and music discussion are lowest at 0.117 to 0.133. Professional, technical and finance talk
is mid to low at 0.150. This is the same ordering the frozen genre study found as a matter and
manner LEVEL effect, reproduced here on the raw residual: the genres that exist to move an audience
carry more manner than the genres that exist to convey content, before any manipulation is present.

Reddit does not contain the marquee commercial genres. Read the top of this table as the stand in
for "legitimately high manner": if the calibration protects snark and reality television gossip
from being flagged, it will protect a sales page for the same reason.

## 2. Calibrated manipulation score

Manipulation is the residual above a text's own genre baseline, not the raw manner level. Two
equivalent forms, per text `t` in genre `g`:

```
# primary: rank within the genre (threshold free, robust to the coarse scorer grid)
calibrated_percentile(t) = P( manner_inflation < manner_inflation(t) | genre g )

# secondary: robust z above the genre median
calibrated_z(t) = ( manner_inflation(t) - median_g ) / MADsigma_g
```

Both subtract the genre's own location. A text is manipulation suspect only when it sits in the
upper tail of its OWN genre, so a sales page at the sales median scores 0.5 (percentile) or 0 (z),
exactly like a technical page at the technical median. This is the property that makes the PCAA gate
usable: the gate reads the calibrated score, so a genre being persuasive by nature never raises the
block rate on its own ordinary members. In production the genre would be assigned by the existing
web topic classifier and the baseline read from a per genre table like Section 1.

Design note on which form to prefer. The percentile form is primary because the scorer is coarse:
manner inflation takes only 85 distinct values on a grid of about 1/60, so a genre distribution has
heavy ties and a rank is more stable than a z built on a quantised spread.

## 3. False positive guard

Two checks. The first is that the calibration is even handed across genres. The second is that it
still catches known deception.

### Guard 1: calibration equalises the false positive rate across genres

A naive detector uses one global threshold (the pooled p95 of manner inflation, 0.417). Because the
high manner genres sit above the pooled median, that single threshold flags more of their ordinary
members. The calibrated score, thresholded at the one sided 5 percent point within each genre,
holds the false positive rate at about 5 percent for every genre.

| genre | naive false positive rate | calibrated false positive rate |
|---|---|---|
| reality_tv_gossip | 6.4% | ~5% by construction |
| snark_gossip | 6.5% | ~5% by construction |
| anime_manga_kpop | 4.5% | ~5% by construction |
| truecrime_morbid | 6.3% | ~5% by construction |
| sports | 5.0% | ~5% by construction |
| place_local | 5.9% | ~5% by construction |

The naive gap is modest here (4.5 to 6.5 percent) only because reddit genres differ modestly. On the
web, where a sales page or a tabloid front sits far higher in raw manner than a reference article,
the same uncalibrated threshold would flag a large fraction of legitimate commercial copy. The
calibration removes that bias by construction: every genre is judged against itself.

### Guard 2: known deception is still anomalous within its own genre

The IRA political troll corpus (8,000 scored English political posts, already scored) is placed
against the `politics_ideology` genre baseline, which is its natural genre. If ordinary political
argument were being flagged, the calibration would be useless. It is not: ordinary political content
sits at the baseline, and IRA sits in the tail.

| quantity | value |
|---|---|
| IRA manner inflation, median | 0.250 |
| politics_ideology baseline, median | 0.150 |
| IRA median as calibrated z within politics_ideology | +0.40 (percentile 71%) |
| IRA items above the politics_ideology p95 threshold | 14.7% |
| ordinary politics_ideology items above that same threshold | 5.1% |
| detection lift (IRA flag rate / ordinary political flag rate) | 2.9x |
| IRA items above the highest manner legit genre (reality_tv_gossip) p95 | 15.8% |

The calibration cleanly separates legitimate persuasion from manipulation in the SENSE THAT MATTERS
for a gate: it does not flag ordinary political or high manner content (5 percent, the intended false
positive rate), and it flags IRA deception at about three times that rate, holding even against the
hardest case of the most persuasive legitimate genre. It does this without ever seeing the deception
corpus.

### Honest bound on the strength of the signal

The separation is real but it is a tail effect, not a clean split of the medians. IRA's median
manner inflation is only +0.40 robust z above ordinary political content; at the median the two
overlap heavily. Two measurements say the same thing:

- Genre explains 21 percent of the variance in community mean manner inflation (community level
  eta squared 0.209), so the genre baseline is a real, substantial location coordinate and worth
  subtracting. But it explains only 1.7 percent of item level variance (eta squared 0.017): a single
  text's manner inflation is dominated by within genre spread and by the coarse scorer, so
  calibration is a meaningful offset on the genre mean and only a small correction on any one item.
- Manner inflation is therefore a weak univariate deception signal even after calibration. Its value
  is the tail lift (about 2.9x), and the strong detector is the full character reading, not this one
  residual. The companion deception test (`analyse_manner_inflation.py`) already shows the eight axis
  classifier carries the real separation while the residual alone is weak. Calibration makes the
  residual honest across genres; it does not turn it into the whole detector.

## 4. What this establishes and what it does not

Establishes: a per genre manner inflation baseline exists and ranks in the expected direction
(persuasion first, content last); a calibrated score defined as the within genre percentile or robust
z removes the genre bias so no legitimately persuasive genre is over flagged; and against a genre
relative threshold the calibration spares ordinary content at the intended 5 percent rate while
still catching IRA deception at about 2.9 times that rate. This answers the obvious objection to the
PCAA gate: it does not equate persuasion with manipulation.

Does not establish: a web scale, commercial genre baseline. Reddit has no sales, advert, news or
tabloid genre with scored labelled instances, and the scored web corpus is unlabelled for genre, so
those genres are approximated by the high manner social genres. Nor does it establish manner
inflation as a strong standalone detector; on this corpus it is a modest tail signal and the eight
axis reading does the real work. Closing the web genre gap needs a genre label on the scored web
domains (score a labelled slice of `pld_content_topic`, or label a slice of `domain_char8_expanded`);
that is scoring work and is out of scope for this pure analysis note.

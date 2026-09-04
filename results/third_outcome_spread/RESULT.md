# The persuasion funnel's third outcome: does character predict what SPREADS?

**Programme:** DYNAMICS-WEB. **Track:** public. **Question:** Paper 4B measures two of the
three persuasion funnel outcomes. ATTENTION, does a message get looked at, from Upworthy
headline clicks and UK petition signatures. CONVICTION, does it change a mind, from
ChangeMyView deltas and StackExchange accepted answers. The third distinct outcome is SPREAD,
what travels, what an audience amplifies. This test asks whether the eight axis character of a
message predicts how far it spreads, and whether the character profile of spread is genuinely
different from the profile that wins attention and the profile that wins conviction.

**Verdict: character predicts spread, weakly but robustly, and spread has its own signature.**
On 80,138 reddit comments across 400 communities, holding the community and the thread fixed
and clustering by author, three axes move spread with high confidence: novelty
(originality **+0.084**), feeling (affect **+0.051**) and substance (depth **+0.045**), all in
outcome SD per one SD of the axis, all p < 0.001. Formality (register **-0.027**) and self
promotion (commercial_drive **-0.012**) travel LESS. The prediction going in was that spread is
affect and stance driven, emotional and polemical content travelling even harder than attention
does, with matter not helping. That is half right and half wrong. Affect does help spread, but
no more than it helps attention, and the strongest single driver of spread is not affect at all,
it is NOVELTY. Stance, the polemical axis, does not move spread. And matter as a pole does not
help spread, yet one matter axis, depth, clearly does. So spread is not the pure emotional or
polemical signal that was predicted, and it is not the manner pole. It is its own thing: what is
new, felt and substantial travels, what is formal or salesy does not.

---

## 1. What SPREAD is measured on, and why reddit not the troll dump

Spread needs a real amplification count on already scored content. The corpus is
`the internal Reddit corpus`: 80,138 reddit comments that already carry an eight axis character score and
a **score** (net upvotes), the canonical reddit virality proxy. A highly upvoted comment is
surfaced to more readers by the ranking, so it travels. The corpus spans 400 subreddits, 47,515
authors and 30,935 threads, median 62 words per comment. An independent 18,000 comment sample
(`an internal table`) is used as a replication.

Score is heavily skewed and can be negative (minimum -230, tenth percentile 1, median 4,
ninetieth percentile 25, ninety ninth percentile 121, maximum 2,293). The outcome is therefore
the **fractional rank of score within the community** (robust, uniform, immune to the tail and
to negatives), with a signed logarithm of score reported as a robustness check.

The task brief suggested IRA troll retweet counts as a second spread corpus. They do not exist:
the FiveThirtyEight IRA dump carries no per post retweet or favourite count. Its `retweet`
column is a zero or one flag for whether the post itself is a retweet, and `followers`,
`following` and `updates` are account level running totals, none of them a spread count for the
individual post. So the IRA corpus cannot supply a spread OUTCOME and is not used here. Reddit
score is the genuine per item amplification signal in the already scored data.

## 2. Method, matched to Paper 4B

Pure analysis on already scored character. No new scoring, nothing sent to the scoring endpoint.

Per corpus the eight axes are standardised, matter is the mean of rigour and depth, manner the
mean of affect, stance and register, and PC1 is the single matter versus manner axis of the web
character space (`the internal reference table`, 2.65M domains, oriented so rigour and depth are
positive). PC1 is fit once on that external reference and reused everywhere, so it is defined
independently of any outcome corpus. Outcome, axes and log length are demeaned within a design
group, then the standardised outcome is regressed on the eight axes and log word count with
cluster robust standard errors. For spread the design group is the SUBREDDIT (community and
topic held fixed) and the cluster is the AUTHOR, with the subreddit reported as a second, more
conservative cluster. Every coefficient is in outcome SD per predictor SD, comparable across
corpora and across the three funnel stages.

The attention and conviction corpora are the same five as Paper 4B, re run here at the per axis
level for the contrast: Upworthy clicks and UK petition signatures (attention), ChangeMyView
deltas and StackExchange accepted answers (conviction).

---

## 3. The character of spread

reddit_wide, 80,138 comments, demeaned within subreddit, clustered by author.

| axis | beta (spread) | p (author) | p (subreddit) |
|---|---:|---|---|
| **originality** | **+0.084** | *** | *** |
| **affect** | **+0.051** | *** | *** |
| **depth** | **+0.045** | *** | *** |
| stance | +0.012 | ns | * |
| rigour | -0.008 | ns | ns |
| commercial_drive | -0.012 | * | * |
| **candour** | **-0.027** | *** | *** |
| **register** | **-0.027** | *** | *** |
| log word count | -0.012 | ns | |
| matter (pole) | +0.011 | ns | |
| manner (pole) | -0.002 | ns | |
| PC1 (matter vs manner) | +0.021 | ** | |

Read the top of the table as the character of virality. What spreads on reddit is, in order,
**novel** (originality is the single strongest axis), **felt** (affect), and **substantial**
(depth). What spreads less is **formal or performed** writing (register negative) and **salesy**
writing (commercial_drive negative), with candour also slightly negative. Length does not move
spread once the axes are in. The two poles are both flat: neither matter nor manner as an
aggregate predicts how far a comment travels, and the matter versus manner PC1 is essentially
nil (+0.021). Spread does not live on the matter or the manner side of the character space, it
lives on a different combination of axes.

**Robustness.** The profile is stable under every honest control:

| variant | originality | affect | depth | register |
|---|---:|---:|---:|---:|
| primary (rank, within subreddit, cluster author) | +0.084*** | +0.051*** | +0.045*** | -0.027*** |
| signed log score outcome | +0.075*** | +0.037** | +0.045*** | -0.013* |
| within THREAD (30,935 threads held fixed) | +0.055*** | +0.034*** | +0.039*** | -0.031*** |

The within thread column is the strong test: comparing comments inside the same reddit thread,
against the same original post at the same moment, so thread visibility, topic and timing are
all removed. The novelty, feeling and substance rewards survive it (the within thread eight axis
profile correlates with the primary profile at r = 0.98). Whatever character earns spread, it is
not an artefact of which thread a comment happened to land in.

The independent reddit_char sample agrees on the shape but with only 12 communities its within
group control is weak, so it is a directional check, not a second clean estimate. It puts manner
slightly negative (-0.035) and matter slightly positive, reinforcing the one firm point that
spread is not manner driven.

---

## 4. Contrast: spread against attention and conviction

Per axis standardised beta, the three funnel stages side by side (headline corpora).

| axis | SPREAD (reddit) | ATTENTION (upworthy) | CONVICTION (cmv) | CONVICTION (se) |
|---|---:|---:|---:|---:|
| rigour | -0.008 | +0.004 | -0.031* | +0.064*** |
| depth | +0.045*** | -0.025 | +0.045*** | +0.007 |
| originality | +0.084*** | +0.087*** | -0.039*** | -0.021*** |
| candour | -0.027*** | -0.023 | +0.021* | -0.020*** |
| affect | +0.051*** | +0.049*** | +0.046*** | -0.008 |
| commercial_drive | -0.012* | +0.037** | -0.017 | +0.015** |
| stance | +0.012 | -0.014 | -0.117*** | -0.040*** |
| register | -0.027*** | +0.026* | -0.010 | +0.064*** |
| matter (pole) | +0.011 | -0.030** | -0.043*** | +0.073*** |
| manner (pole) | -0.002 | +0.023* | -0.064*** | +0.007 |
| PC1 (matter vs manner) | +0.021** | -0.048*** | -0.049*** | +0.012** |

Profile similarity (Pearson correlation of the eight axis beta vectors):

| pair | r |
|---|---:|
| spread vs attention (upworthy) | **+0.52** |
| spread vs conviction (cmv) | +0.09 |
| spread vs conviction (se) | **-0.46** |
| attention vs conviction (cmv) | -0.02 |
| the two conviction corpora (cmv vs se) | +0.20 |

Three things fall out.

**Spread is closest to attention, but not the same as attention.** They share the top of the
funnel: both reward originality (spread +0.084, attention +0.087) and both reward affect (both
about +0.05). That is why their profiles correlate at +0.52, the highest of any pair. But they
part on two axes. Attention leans to the MANNER pole (its PC1 is -0.048, manner positive, matter
negative): a headline earns the click by being performed, and depth does nothing for it
(-0.025, not significant). Spread is pole neutral and additionally rewards DEPTH (+0.045): a
comment travels further for having substance, which a headline does not. And where attention
rewards commercial_drive and register (a punchy, promotional headline), spread punishes both.
So spread is attention plus a substance reward and minus the salesmanship, on a longer medium
where there is room for the substance to matter.

**Spread is nearly orthogonal to conviction, and opposed to one form of it.** Against CMV it
correlates at +0.09, essentially unrelated. Against StackExchange it is -0.46, actively opposed:
what earns an accepted answer there is rigour and register (the marks of a careful, formal
technical reply), and those are exactly the two axes that do not spread. The one thing spread
shares with conviction is that neither is polemical: stance kills conviction (CMV -0.117, the
single largest coefficient anywhere in the table) and does nothing for spread.

**The predicted signature is refuted.** The going in prediction was affect and stance driven
spread, emotional and polemical content travelling harder than attention, with matter not
helping. Affect does travel, but no harder than it earns attention (+0.051 vs +0.049), so the
"even more than attention" claim fails. Stance, the polemical axis, does not move spread at all
(+0.012, not significant once authors are clustered). And while matter as a pole indeed does not
help (+0.011, not significant), that pole average hides a real and significant depth reward
(+0.045); it is only rigour that is inert. So the emotional intuition is partly right, feeling
does carry, but the dominant fact about spread is NOVELTY, which the prediction did not name,
and the polemical half of the prediction is wrong.

---

## 5. Verdict

**Does character predict virality? Yes, distinctly, but modestly.** On a heavy tailed spread
outcome with the community, the thread, length and the author all controlled, several character
axes move spread at p < 0.001 on 80,000 comments, and the effect survives every robustness
swap. The spread profile is genuinely its own: it correlates +0.52 with attention, +0.09 and
-0.46 with the two conviction corpora, so it is neither a copy of the attention profile nor of
either conviction profile. The persuasion funnel has three character signatures, not two.

The character of spread, stated plainly: **what is new, felt and substantial travels; what is
formal or salesy does not.** Novelty (originality) is the strongest single driver, feeling
(affect) and substance (depth) follow, and the two axes that spread least are register
(performed formality) and commercial_drive (self promotion). This is close to but distinct from
the character of attention, which shares the novelty and feeling but trades substance for
performance, and it is close to opposite the character that wins a formal technical answer.

The honest size caveat: these are small coefficients, the largest is 0.084 of an outcome SD per
SD of an axis. Character is a real and measurable slice of what makes content spread, but only a
slice. Virality is dominated by things this instrument does not see, timing, who posts it, where
it is seeded and the shape of the network, and no reading here should be taken to say novelty
plus feeling plus substance is sufficient for a comment to go far, only that, holding the
audience and the thread fixed, those are the axes that consistently tilt it that way.

---

## 6. Honest limits

- **One platform, one amplification mechanism.** Spread is reddit upvote rank. Upvotes are an
  endorsement and ranking signal, the closest per item amplification count in the already scored
  data, but they are not a forward or a retweet. A true share or retweet count on a second
  platform would test whether the novelty and substance rewards are a reddit fact or a general
  spread fact. The absence of a per post count in the IRA dump is why that second platform is not
  here.
- **Small effect sizes on a hard outcome.** Spread is heavy tailed and mostly driven by factors
  outside character. The coefficients are small by construction and are significant because the
  sample is large and the controls are tight, not because character explains most of the
  variance. It explains a little, reliably.
- **The scorer.** The eight axis instrument is web tuned and applied to social comments, off its
  fitting distribution, quantised to 0.1 steps, the same caveat that runs through the series.
- **Petitions is underpowered** (381 opened petitions, most singletons after demeaning) and its
  per axis attention numbers are directional only; the attention contrast leans on Upworthy.
- **reddit_char has only 12 communities**, so its within group control is weak; it is a
  directional replication, not a clean second estimate.
- **StackExchange and CMV disagree on matter** (matter +0.073 on SE, -0.043 on CMV), as Paper 4B
  already noted, so "conviction" is not one profile; the spread contrast is drawn against each
  separately, and spread is unlike both.

---

### Reproduction

- Analysis: `scripts/third_outcome_spread.py` in this directory. numpy, scipy and psycopg2 only:
  fractional rank within group, within group demeaning, cluster robust (author and subreddit)
  regression. Runs on the internal host, pure read, no scoring, scoring endpoints not touched.
- Spread: `the internal Reddit corpus` (`char`, `score`, `subreddit`, `author`, `link_id`, `body`),
  80,138 rows with character; replication `an internal table`.
- Attention and conviction: the five Paper 4B corpora (Upworthy `~/kc-dwpaper`, petitions, CMV,
  StackExchange, on the internal store).
- PC1 reference: `the internal reference table` (2.65M domains), rigour and depth oriented
  positive, fit independently of every outcome corpus.
- Results: `results.json` in this directory (PC1 loading plus every coefficient).

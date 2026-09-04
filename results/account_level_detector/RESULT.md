# Can you catch a manipulative account from the shape of its posts, when the posts look clean?

**Programme:** DYNAMICS-WEB. **Track:** public. **Question:** platforms ban accounts, not
posts. The flagship manipulation result showed that the Internet Research Agency's non political
accounts sit at the same manner pole as its political trolls (PC1 around -1.7 either way), so the
signature belongs to the whole account pool, not just the obviously political posts. This test
asks the operational follow on: can a manipulative account be detected from the DISTRIBUTION of
its posts' eight axis character, and is that account level detector stronger and more robust than
scoring one post at a time, even when many of the account's individual posts look innocuous?

**Verdict: yes, decisively, and the account is far easier to catch than any single post.** On the
same accounts, a single post separates state trolls from real users at cross validated AUC
**0.878**; the account, described by the mean and the spread of its posts' character, separates at
AUC **0.996**. The signal that makes the difference is not the average post, it is the VARIANCE of
the character across the account's posts, which no single post can show. Even when the detector is
fed only the troll posts that individually look organic, the account is still flagged at AUC
**0.822**. And the IRA's innocuous accounts (news feed, commercial, hashtag games) are, if
anything, the easiest of all to catch at the account level (AUC **1.000**), which is exactly the
robustness a real platform needs.

---

## 1. What is compared, and why this is a fair comparison

Two units, one instrument.

- **Post level.** One post, its eight axis character vector, classify troll versus organic. Unit
  is the post.
- **Account level.** One account, described by the mean of each of the eight axes over its posts,
  the standard deviation of each axis (the spread), the share of its posts on the manner pole
  (PC1 below zero), and its mean PC1. Eighteen aggregate features. Unit is the account.

The manipulative class is IRA accounts, per post scores joined back to the account handle through
the raw corpus (`author`, `tweet_id`). The organic class is real reddit accounts from
`the internal Reddit corpus`, per post scores grouped by `author`, bots removed. Both classes are scored on
the identical eight axis instrument, so the account versus post comparison is internal: any
distribution difference between tweets and reddit comments (length, platform) sits under both units
equally, and the honest quantity is the DELTA between them, not the absolute number.

Author leakage is controlled at the post level by grouping the cross validation folds on the
author, so a classifier cannot score well simply by memorising which handle a post came from.

Groups:

| Class | Source | Accounts | Posts |
|---|---|---|---|
| MANIP | IRA accounts (all categories), joined to handle | 206 | 9,000 |
| ORGANIC | reddit accounts (`the internal Reddit corpus`, bots removed) | 47,513 | 77,083 |

The matter versus manner axis (PC1) is the first principal component of the web character space
(`the internal reference table`, 2.65M domains), oriented so rigour and depth are positive, the
same reference the flagship used.

---

## 2. Account level versus post level

| Detector | Unit | AUC | Accuracy |
|---|---|---|---|
| Single post (grouped CV by author) | post | 0.878 +/- 0.015 | 0.792 |
| Account, 18 aggregate features (>= 5 posts) | account | **0.994 +/- 0.005** | 0.970 |

Head to head on the **identical set of accounts** (those with at least five posts, 151 troll and
151 organic, balanced):

| Method | Account AUC |
|---|---|
| Single post character | 0.878 |
| Post vote: mean of the account's per post troll probabilities | 0.984 |
| Account aggregate: the 18 distribution features | **0.996** |

Two things fall out. First, just averaging the post detector over an account (post vote) already
lifts AUC from 0.878 to 0.984, because noise averages out. Second, the distribution shape detector
still beats that averaging, 0.996 against 0.984, so there is real account level signal that no
amount of pooling the per post scores recovers. That extra signal is the spread.

---

## 3. The spread is the tell

The account level classifier's largest weights are not the means, they are the standard deviations.

| Feature | Standardised weight |
|---|---|
| std_register | +1.63 |
| mean_candour | -1.62 |
| mean_register | -1.50 |
| std_commercial_drive | +1.21 |
| std_affect | +0.98 |
| std_depth | -0.92 |
| std_candour | +0.76 |
| mean_originality | -0.75 |

The positive std weights say a manipulative account swings WIDELY across register, commercial
drive and affect from post to post, far more than a real person does. A genuine user has a
consistent voice; the spread of their character is narrow. An IRA account is an operation running
one handle across news, commercial filler, hashtag games and political attack, so its character
distribution is broad and lumpy. That heterogeneity is invisible in any single post and is exactly
what an account level view exposes. The mean features still contribute in the expected direction
(lower candour, lower register, lower originality), consistent with the flagship, but the variance
features are what carry the account beyond post pooling.

---

## 4. How few posts do you need

Sample exactly k posts per account, rebuild the aggregate features, balance and cross validate,
average over eight resamples.

| Posts per account | IRA accounts | Organic accounts | Account AUC |
|---|---|---|---|
| 1 | 206 | 47,513 | 0.865 |
| 2 | 190 | 12,573 | 0.934 |
| 3 | 175 | 5,537 | 0.961 |
| 5 | 151 | 1,919 | 0.980 |
| 8 | 134 | 691 | 0.990 |
| 10 | 124 | 385 | 0.985 |
| 15 | 105 | 173 | 0.990 |
| 20 | 89 | 82 | 0.997 |

At k = 1 the aggregate collapses to a single post (no spread to measure) and lands at 0.865, in
line with the post level number. Two posts already reach 0.934, three reach 0.961, and by five the
detector is at 0.980 and essentially flat thereafter. The practical reading: **three to five posts
per account is enough to flag it reliably.** The reason the curve climbs so fast is that the second
and third post are what first let the variance features exist.

(The organic account count shrinks steeply with k because the median reddit user in the store has
a single scored comment, so the high post accounts are the more engaged tail. This is a mild
selection effect on the baseline, noted in section 6, and does not touch the internal account
versus post delta which uses one fixed set.)

---

## 5. When the posts look clean

The sharp test. Take the post level model, score every IRA post, and call a post "clean looking"
when the model would classify it as organic (probability below one half). **18.8 per cent of
individual IRA posts look clean by this measure** and would slip a post level filter. Now build the
account features from ONLY those clean looking posts (organic accounts keep all their posts) and
re run the account detector.

| Detector | Account AUC |
|---|---|
| Account, all posts | 0.994 |
| Account, only individually clean looking posts | **0.822** |

The number drops but stays well clear of chance. Sixty eight IRA accounts have five or more clean
looking posts, and the account is still caught at 0.822 from those alone. So the answer to the
headline question is yes: an account whose every visible post reads as innocuous still betrays
itself in the aggregate, because the collection of "clean" posts is drawn from a different
character distribution than a real person's, even when each one passes on its own.

---

## 6. The IRA's innocuous accounts are the easiest to catch

Splitting the manipulative class by IRA category, against the same organic baseline, at five posts
minimum:

| IRA category | Accounts | Account AUC |
|---|---|---|
| Political trolls (RightTroll, LeftTroll, Fearmonger) | 132 | 0.997 |
| Innocuous (NewsFeed, Commercial, HashtagGamer) | 19 | 1.000 |

This is the operationally important line. The accounts that were built to look benign, the news
feeds and hashtag games, are not harder at the account level, they are trivial, because their
character distribution is even further from an organic user's than the political trolls'. A post
level filter, which sees each of their bland posts in isolation, would wave them through. The
account view does not. (The innocuous set is only nineteen accounts, so read 1.000 as "cleanly
separable at this sample size", not as a claim of zero error at scale.)

---

## 7. Honest confounds

1. **One actor, one operation.** All manipulative accounts are IRA, 2015 to 2018, Twitter,
   English. The variance signature may partly reflect how this one operation ran many content types
   through single handles, and need not transfer unchanged to a different influence operation. What
   generalises is the method, aggregate the character distribution per account, not this exact set
   of weights.
2. **Cross platform baseline.** Manipulative is tweets, organic is reddit comments. The two media
   differ in length and norms. This is why the load bearing result is the internal delta (account
   0.996 versus post 0.878 on one fixed set, same media on both sides of that comparison), not the
   raw AUC. A same platform organic Twitter baseline would tighten the absolute numbers.
3. **Baseline selection at high k.** Requiring many posts per organic account keeps the engaged
   tail of reddit users. More engaged users have more consistent voices, which could flatter the
   spread signal. The clean post test in section 5, which holds the organic side fixed and only
   thins the troll side, is the check that the effect is not an artefact of this.
4. **Scorer.** The eight axis instrument is a web tuned model applied to social posts, off its
   fitting distribution. Consistent with the flagship's caveat.
5. **Small innocuous cell.** Nineteen IRA_OTHER accounts. Directional, not a precise error rate.

---

## 8. Bottom line

Accounts are detectable from aggregate character, and the account is a far better unit than the
post. On one fixed set of accounts the discrimination rises from 0.878 per post to 0.996 per
account, and the lift comes specifically from the spread of character across posts, a quantity that
does not exist for a single post. Three to five posts are enough. Most importantly for a real
platform, the account is still caught when every one of its posts looks clean (0.822 from clean
posts only) and the accounts built to look most innocuous are the easiest of all to flag (1.000).
This is the empirical case for account level moderation: ban the pool, not the post, because the
pool is what gives itself away.

---

### Reproduction

- Analysis: `truthometer/scripts/account_analyse.py` (numpy only: logistic, grouped CV, AUC).
- IRA per post scores: `the internal corpus store/ira_troll/work/scored.jsonl`, joined to
  `author` and `account_category` through `IRAhandle_tweets_{1,2}.csv` on `tweet_id`.
- Organic per post scores: `the internal Reddit corpus` (`author`, `char`), bots removed.
- PC1 reference: `the internal reference table` (2.65M domains), rigour and depth oriented positive.
- Seed 1729. Scores reused, nothing rescored (scoring endpoint 8301 not touched).

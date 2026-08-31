# Character synchrony as a coordinated inauthentic behaviour (CIB) signal

DYNAMICS-WEB series, PUBLIC track. Pure analysis on already scored 8 axis character.
No new model scoring. Script `synchrony.py`, raw run `synchrony_output.txt`, both in this folder.

## Question

State manipulation is not one account, it is a coordinated network. If coordinated
inauthentic accounts converge on the same character profile, at the same time, on the same
topic, in a way that independent organic accounts do not, then character synchrony is a novel
CIB detector. This tests that claim directly.

## Data

| Pool | Source | Posts | Accounts | Metadata used |
|---|---|---|---|---|
| COORDINATED | IRA political trolls (Clemson/FiveThirtyEight handle dump), scored 8 axis | 9,000 | 206 | author, publish date, account_category, all English |
| ORGANIC | Reddit ChangeMyView winning args comments, scored 8 axis | 18,964 | 6,197 | author, timestamp, thread root (= shared topic) |

Both are already scored on `rigour, depth, originality, candour, affect, commercial_drive,
stance, register`. IRA scores join to the raw metadata by tweet id at 100%. CMV scores join
to the ConvoKit utterances by comment id at 100%. Character was standardised on the union of
the two pools; PC1 (matter versus manner, 51% variance in the reference, rigour and depth on
the positive pole) was taken from an SVD on that same union.

The IRA operation is the ideal positive: a known state network with many accounts and
timestamps. CMV is a strong organic negative: thousands of independent authors, each thread a
naturally topic constrained unit, no coordination.

## Three metrics and what they found

### A. Account identity index (the domain fair test)

Within one pool, are the accounts statistically interchangeable (the naive picture of a troll
farm, everybody the same) or do they carry individual character identity (organic)? For
accounts with at least k posts, each subsampled to exactly k, measure the dispersion of the
account centroids around the pool centroid, then compare it against a within pool shuffle that
reassigns posts to accounts at random. `I = observed dispersion / shuffled dispersion`.
`I ~ 1` means accounts are interchangeable; `I >> 1` means distinct individuals. Because each
pool is compared to its own shuffle, platform, text length and mean character all cancel, so
this is the one metric that is not contaminated by the Twitter versus Reddit domain gap.

```
IRA  k=5   accts=151   I=1.205   p<0.001
CMV  k=5   accts=1001  I=1.286   p<0.001
IRA  k=10  accts=124   I=1.440   p<0.001
CMV  k=10  accts=257   I=1.421   p<0.001
```

**IRA accounts are not more interchangeable than organic accounts.** The identity index is
essentially the same in both pools (organic is marginally higher at k=5, IRA marginally higher
at k=10). The naive "coordinated accounts are clones of one another" hypothesis is false. Per
axis, the difference is in shape not amount: organic authors differ most on rigour and depth
(the matter axes carry individual voice, ratio 2.2 and 2.1), IRA accounts differ most on affect
(1.9), consistent with a network that varies emotional pitch by persona while holding a common
low substance register.

### B. Cross pool clustering tightness (matched k, matched pool size, bootstrap null)

Draw organic pools of the same size and posts per account as the IRA pool, 1,000 times, and see
where the IRA account dispersion falls.

```
k=5    IRA_D=1.558   organic null D=1.240 ± 0.034   z=+9.4   IRA at 100th percentile
k=10   IRA_D=1.314   organic null D=0.930 ± 0.027   z=+14.0  IRA at 100th percentile
```

The sign is the opposite of the hypothesis. **IRA accounts are more spread out in character
space than organic pools, not tighter.** The reason is visible in the metadata: the IRA network
deliberately ran divergent personas (124 RightTroll accounts, 46 LeftTroll, 13 Fearmonger, plus
NewsFeed, HashtagGamer, Commercial). A competent operation diversifies character on purpose, so
static cross account clustering points the wrong way. (This particular number is also inflated by
the domain gap, hence metric A as the clean control; but even the clean control shows no tightening.)

### C. Topic and time conditioned synchrony (cross account variance in a shared context)

Within a shared context (an IRA day, or a CMV thread, or a CMV day), how much do the accounts
vary? Low variance in a shared context is the synchrony claim.

```
affect  cross account SD:  IRA/day 0.769   CMV/thread 0.623   CMV/day 0.736
        Cohen d IRA-day vs CMV-day = +0.29   AUC (low SD => coordinated) = 0.464
PC1     cross account SD:  IRA/day 0.701   CMV/thread 0.870   CMV/day 1.058
        Cohen d IRA-day vs CMV-day = -1.16   AUC (low SD => coordinated) = 0.781
```

On affect, IRA is not lower than organic within a shared context (AUC 0.46, i.e. no separation).
On PC1 (the matter versus manner register) IRA accounts do sit closer together within a day than
organic authors within a day (AUC 0.781). But that PC1 result is exactly what the length work in
this series predicts as an artefact: tweets are short, matter needs bandwidth, so short text
compresses the rigour and depth axes and lowers their spread for reasons that have nothing to do
with coordination. It cannot be claimed as a synchrony signal on its own.

### The one place synchrony is real: temporal affect bursts

The average day does not separate the pools. The tail does. Ranking IRA busy days (at least 10
active accounts) by lowest affect spread surfaces a tight cluster in August 2017:

```
2017-08-12  52 accounts  mean affect(z) +1.03  cross account SD 0.345
2017-08-14  38 accounts  mean affect(z) +1.12  cross account SD 0.251
2017-08-16  40 accounts  mean affect(z) +1.07  cross account SD 0.323
2017-08-17  48 accounts  mean affect(z) +1.10  cross account SD 0.344
2017-08-18  54 accounts  mean affect(z) +1.08  cross account SD 0.303
```

Dozens of accounts spiking to the same high affect on the same day with very little spread. A
combined burst detector (a day with at least 10 accounts, mean affect above the organic 90th
percentile, and cross account spread below the organic 10th percentile) flags:

```
IRA busy days: 48.7% are convergent affect bursts   (n=39)
CMV busy days:  0.5%                                 (n=573)
```

Roughly a hundredfold enrichment. This is a usable signal, with an important honesty caveat below.

## Confounds, stated plainly

1. **Shared brief is the signal, not a nuisance.** IRA accounts share a house style because they
   are coordinated. Where synchrony appears (the register convergence, the affect bursts) the
   confound and the phenomenon are the same thing. That is fine for a detector, but it means
   synchrony is not measuring anything independent of "these accounts follow one playbook".
2. **The burst detector rides on the known single account signature.** Most of the 48.7% versus
   0.5% gap comes from the affect mean being high (IRA busy day mean affect +0.76 versus organic
   -0.36), which is the already established single account manipulation signature (affect is the
   discriminator, AUC 0.925 versus LIAR, fabric #19286). The synchrony specific part, low spread
   conditional on a busy day, adds only a modest lift (IRA busy day affect SD median 0.606 versus
   organic 0.736). Synchrony is a co timing amplifier on top of the affect signature, not a
   standalone axis.
3. **Domain gap.** IRA is Twitter, CMV is Reddit essays. Length and register differ. Metric A
   controls this by construction (each pool versus its own shuffle) and still shows no tightening;
   the PC1 result in metric C is contaminated by length and is discounted for that reason.
4. **Topic units are not perfectly matched.** A CMV thread is one topic; an IRA day is a mix of
   topics. The IRA day versus CMV day comparison is the matched pair and is the one relied on.

## Verdict

**Character synchrony as a static cross account property is not a usable CIB signal, and taken
naively it is misleading.** A competent operation diversifies its personas, so coordinated
accounts are more spread in character space, not less, and the account identity index shows they
are no more interchangeable than independent organic accounts. Anyone hunting troll farms by
looking for a tight character cluster will point their detector the wrong way.

**Character synchrony over time, specifically coordinated affect bursts, is a real and usable
signal**, flagging about half of IRA high activity days against a 0.5% organic rate. But it is a
temporal co movement detector, not a character clustering one, and most of its power is inherited
from the single account affect signature; the pure low variance component is modest. The honest
framing for the paper and for a platform: character alone does not catch coordination, but
character change measured across accounts and across time does, as an amplifier on the affect
signature. The synchrony axis to build is temporal (who spikes together, when), not spatial (who
looks alike).

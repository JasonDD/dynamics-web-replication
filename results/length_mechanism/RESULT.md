# Length as the mechanism behind matter and manner

**Hypothesis under test.** "Matter needs bandwidth, manner is instant." Text length is
the mechanism behind the matter/manner axis. Matter axes (rigour, depth) can only
express their variance once a text is long enough to build an argument; manner axes
(affect, stance, register) saturate almost immediately in a phrase.

**Axes.** matter pole = rigour + depth. manner pole = affect + stance + register.
matter/manner PC1 = SVD on `the internal reference table` (n=2,648,406), standardised,
oriented rigour+depth positive. PC1 loadings confirm the axis: rigour +0.44, depth +0.40,
candour +0.39, stance +0.37 on the positive (matter) side; affect -0.35, register -0.34,
commercial_drive -0.26 on the negative (manner) side.

**Data.** Already scored 8 axis character on four corpora, each with a recoverable word
count. No new scoring was run.

| source | n | wc p10 | wc p50 | wc p90 | wc max | role |
|---|---|---|---|---|---|---|
| ira (troll tweets) | 8,558 | 8 | 13 | 20 | 46 | short end |
| cmv (Reddit change my view args) | 19,430 | 34 | 120 | 382 | 1,749 | wide, single genre |
| parlamint (parliament speeches) | 1,675 | 95 | 243 | 634 | 899 | mid to long, single genre |
| oldbailey (trial proceedings) | 568 | 53 | 272 | 1,456 | 53,433 | very wide, single genre |

Method: bin by word count (0-20, 20-50, 50-100, 100-300, 300-1000, 1000+). Per bin,
per axis, compute the mean and the variance. Test whether the spread of the matter axes
rises with length while the manner axes stay flat or saturate early. Repeat within each
single source to rule out a composition artefact.

---

## Verdict

**Partly holds, and in a sharper form than stated.** The claim is true on the MEAN and
at the SHORT END of the variance, for the rigour/depth versus affect contrast. It is false
as a simple "matter variance keeps rising with length" claim, and the manner pole is not
uniform.

Three findings, in order of strength.

### 1. Matter is a length effect on the mean (strong, robust in every source)

Rigour and depth climb monotonically with word count in every corpus. You cannot score
high on rigour in a twelve word tweet; the score rises as the text gains room.

Per bin mean rigour, depth (pooled): 0.25, 0.32 at 0-20 words rising to 0.71, 0.68 at
300-1000 words. Correlation of per bin mean with log length: rigour +0.97, depth +0.96
pooled; the same sign and size within cmv (+0.97, +0.98), parlamint (+0.83, +0.91) and
oldbailey (+0.95, +0.96). Item level Spearman of the axis value against word count within
cmv: rigour 0.45, depth 0.52.

The matter/manner PC1 itself is substantially a length axis. Pooled mean PC1 by bin:

| bin | n | mean PC1 |
|---|---|---|
| 0-20 | 8,259 | -1.79 |
| 20-50 | 3,848 | -0.14 |
| 50-100 | 5,130 | +2.46 |
| 100-300 | 9,062 | +4.04 |
| 300-1000 | 3,835 | +5.17 |
| 1000+ | 219 | +4.69 |

Item level Spearman of PC1 against word count is 0.55 within cmv, 0.33 within parlamint,
0.41 within oldbailey. A large slice of what the matter/manner axis measures is simply
how long the text is.

### 2. Affect is the instant manner axis (confirmed); the manner pole is not uniform

Affect is fully expressed in the shortest texts and if anything fades as length grows.
Pooled mean affect: 0.74 at 0-20 words, falling to 0.52 by 300-1000 words (r with log
length = -0.84). The short end mean shift for affect is -0.20. This is exactly "manner is
instant": a phrase carries all the affect it will ever carry, and longer analytical text
cools it.

But stance and register do not behave like affect. Stance mean rises with length in most
sources (pooled r +0.90, cmv +0.94, oldbailey +0.98): a longer text stakes a clearer
position, so stance needs some bandwidth. Register is flat to mixed (cmv +0.03, parlamint
-0.94). So "manner is instant" is an AFFECT story, not a whole pole story. The clean
contrast is rigour and depth versus affect.

### 3. The variance switches on at the short end, then converges (not a monotone rise)

The stated variance mechanism ("matter spread rises with length") is FALSE as a monotone
claim. Past about 100 words the variance of every axis, matter and manner alike, shrinks
as texts converge. A single linear slope of variance against length is negative for almost
every axis.

The real effect lives at the short end. Crossing from a twelve word phrase (0-20 bin) to a
seventy word passage (50-100 bin), the spread of the matter axes OPENS UP while the manner
axes, already at their maximum spread, only converge.

**Short end switch on, var(50-100) / var(0-20), pooled:**

| axis | pole | var 0-20 | var 50-100 | ratio | mean shift |
|---|---|---|---|---|---|
| rigour | MATTER | 0.014 | 0.042 | 3.05 | +0.29 |
| depth | MATTER | 0.014 | 0.017 | 1.20 | +0.23 |
| affect | MANNER | 0.037 | 0.034 | 0.90 | -0.20 |
| stance | MANNER | 0.093 | 0.047 | 0.50 | +0.12 |
| register | MANNER | 0.074 | 0.041 | 0.56 | +0.19 |

MATTER mean switch on ratio 2.13, MANNER 0.65. Matter spread more than doubles crossing
into passage length; manner spread is already maxed in the phrase and only falls. The same
direction holds within cmv on its own (MATTER 1.23, MANNER 0.79). The picture for matter is
an inverted U: variance is near zero at 0-20 words (everything floored low, no room to
vary), peaks at 50-100 words, then converges high. Manner variance is a plain decline from a
high starting point.

### Within source check and the coverage caveat

The pooled short end result reproduces within cmv, which spans 10 to 1,749 words in one
genre. It cannot be tested within parlamint or oldbailey because neither corpus has sub
twenty word items (parlamint starts near 80 words, oldbailey near 45). Both sit entirely
PAST the switch on point, so within them every axis only converges and the naive linear
variance slope is negative for matter as well as manner (matter minus manner variance slope
gap -0.63 parlamint, -0.25 oldbailey). This is a coverage artefact, not a refutation: their
MEAN trajectories still confirm matter rising with length (r_mean 0.83 to 0.96). The pooled
"matter beats manner on the variance slope" number (+0.35) is real but flattering, because
manner variance falls even faster than matter variance from a higher start; the honest test
is the short end ratio and the mean trajectory, both of which hold.

---

## What it reframes, if you accept the mean and short end forms

The persuasion funnel reads as a length story. Manner, and affect in particular, is
available instantly in short form and earns attention. Matter (rigour, depth) requires
bandwidth to be present at all and is what earns conviction. This explains two things the
series has seen elsewhere.

- **Manipulation lives in short form.** In a phrase, matter cannot be present (rigour and
  depth are floored, with near zero spread), while affect is already at full strength. Short
  form is structurally an affect only channel, which is exactly where state sponsored troll
  content sits. The IRA tweets in this set have a median of 13 words: matter cannot express
  there even in principle.
- **Manner survives translation.** Affect is content light and does not depend on building an
  argument, so it carries across a rewrite or a translation; rigour and depth are bound to
  the argument structure that a short or translated fragment may not preserve.

## Honest limits

- The variance form of the claim as literally stated (matter spread rises with length) is
  false; the true effect is a short end switch on plus convergence.
- The manner pole is not homogeneous. Affect fits "instant"; stance needs some bandwidth;
  register is flat. The clean contrast is rigour/depth versus affect, not matter pole versus
  manner pole.
- Scores are quantised to 0.1 steps by a single web tuned scorer, so bin variances are
  discrete. Floor and ceiling effects at the extremes shape the inverted U for matter.
- ParlaMint and Old Bailey cannot see the short end regime; the switch on rests on the pooled
  and cmv evidence.

## Reproduce

`scripts/length_mechanism.py` in this directory. Runs on the internal host (Postgres for the PC1
reference, internal store for the four corpora). Pure read, no scoring, no  or  calls.

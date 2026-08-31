<!-- generated 2026-08-30T23:35Z by results/crossplatform_identity/scripts/crossplatform_identity.py against cc_v3.crosssite_authorship (tfs, DL580), 7B char_dweb scores. Read only. -->

# Cross platform identity linkage from writing alone

**Track:** PUBLIC. **Question:** given two pieces of writing from two different platforms, can we
decide whether the same pseudonymous person wrote both, from the text alone? This is the core
capability the intelligence pipeline needs: probabilistic entity resolution across sites, a prior
or lead, never a certain match. We measure how far the 8 axis character instrument and classic
stylometry get us, and which of the two is actually carrying identity.

## Ground truth

`cc_v3.crosssite_authorship` links pseudonyms across sites by a shared identity key (gravatar email
hash, disqus id, rel=me, profile URL) recovered from Common Crawl. A key that appears on two or more
distinct domains is the **same person seen on two or more platforms**. The table already carries the
8 axis DYNAMICS-WEB character vector (`char_dweb`, 7B scorer): depth, affect, rigour, stance, candour,
register, originality, commercial_drive. Nothing was scored again here.

We aggregate to person on platform **units** = (identity key, domain). Each unit gets a mean 8 axis
character vector over its rows and a pooled block of its raw text (min 200 characters, capped at 8000).
A **positive pair** is two units of the same person on two different platforms. A **negative pair** is
two units of two different people, also on different platforms so domain style cannot leak the answer.
Pairs are balanced 50/50 and drawn only from the 7B scored subset (the 27B column is too sparse, 2,841
rows, to reach cross platform pairs).

| quantity | value |
|---|---:|
| scored rows loaded | 369,383 |
| person on platform units | 91,683 |
| people spanning 2+ platforms (usable) | 22,896 |
| positive pairs / negative pairs | 44,180 / 44,180 |
| stylometry features | 512 |

The identity keys are overwhelmingly gravatar (same email hash reused across sites), with a small
disqus, profile and rel=me tail. No real individual is named or deanonymised; the analysis works over
opaque keys and aggregate statistics only.

## The two signals

**Character.** Similarity of the two units' mean 8 axis character vectors. Score is negative Euclidean
distance (this beat cosine, so it is the primary character score).

**Stylometry.** Classic authorship features computed directly from the pooled text: function word
relative frequencies (a fixed 150 word closed class list), punctuation rates, sentence length mean and
standard deviation, the 300 most frequent character trigrams, type token ratio and mean word length.
Every feature is z scored across the unit population. Similarity is the cosine of the two z vectors
(this beat negative Burrows Delta, so it is the primary stylometry score).

**Combined.** A numpy L2 logistic fusion of the two primary scores, scored out of fold over 5 folds.
AUC is rank based (Mann Whitney U); 95% intervals are 1,000 sample bootstraps over the pairs.

## Linkage AUC

| signal | AUC | 95% CI |
|---|---:|---|
| character, negative Euclidean | 0.799 | 0.797 to 0.802 |
| character, cosine | 0.781 | 0.778 to 0.784 |
| stylometry, cosine | **0.924** | 0.922 to 0.926 |
| stylometry, negative Delta | 0.807 | 0.804 to 0.809 |
| **combined (character + stylometry)** | **0.928** | 0.927 to 0.930 |

## The decomposition: stylometry does the work

The point of the test is which signal carries identity. It is stylometry, decisively.

- Character alone links the same person across platforms at **AUC 0.799**, well above the 0.5 chance
  floor. Character is not noise: how a person writes on the 8 axes is a real, if soft, fingerprint.
- Stylometry alone reaches **AUC 0.924**, far ahead of character.
- The combined model is **0.928**, only **+0.005 over stylometry alone**. Character adds almost
  nothing once you already have the words.
- The reverse is large: stylometry adds **+0.129 over character alone**.
- The two scores correlate **r = 0.57**. They are not independent views of the person; character is
  largely a lower resolution shadow of the same authorial signal stylometry reads off the surface text
  directly. This is expected: the 8 axis vector is itself derived from the writing, so it cannot hold
  identity information the writing does not already carry, and it throws most of it away by compressing
  to 8 numbers.

**Verdict on the signals:** character re identifies people across platforms at a real but modest level;
stylometry is the stronger instrument and effectively subsumes it. For a linkage product, stylometry is
the workhorse and character is a small, mostly redundant prior, useful for interpretability or as a
cheap first filter, not as the deciding evidence.

## Precision at a high confidence threshold

On the balanced evaluation set, using the combined score:

| operating point | precision | recall | false positive rate |
|---|---:|---:|---:|
| 95% specificity | 0.935 | 0.721 | 0.050 |
| 99% specificity | 0.980 | 0.481 | 0.010 |
| 99.9% specificity | 0.997 | 0.293 | 0.0010 |

At the strict setting the linker is right 99.7% of the time on a balanced set, but only recovers 29% of
true cross platform pairs. It is a high precision, low recall lead generator, exactly the shape you want
for a prior that a human then checks.

## The honest framing: false link risk at real base rates

A balanced 50/50 test flatters any linker, because in the field the true base rate of same person is
tiny. When you compare one pseudonym against a large candidate pool, genuine matches might be 1 in 1,000
or 1 in 10,000. Precision then follows the base rate, not the balanced number. Holding the strict 99.9%
specificity operating point (true positive rate 0.293, false positive rate 0.00102):

| true base rate of same person | precision (99.9% spec) | precision (99% spec) |
|---|---:|---:|
| 1 in 100 | 0.744 | 0.327 |
| 1 in 1,000 | 0.223 | 0.046 |
| 1 in 10,000 | 0.028 | 0.005 |
| 1 in 100,000 | 0.003 | 0.0005 |

At a 1 in 1,000 base rate, even the strict threshold is wrong roughly four times out of five when it
fires. This is the defining property of probabilistic entity resolution: a strong ranked prior that
narrows a large field to a short candidate list, never a certain identification. It links pseudonyms
probabilistically. It is not proof of identity, and any downstream use must treat a hit as a lead to be
corroborated, with a base rate aware confidence attached, not as a match.

## Verdict

Writing alone re identifies the same pseudonymous person across platforms at **AUC 0.93**. Stylometry
is doing the work (0.924); the 8 axis character vector links at a real but weaker 0.799 and adds only
+0.005 once stylometry is present, because it is a compressed, partly redundant view of the same
authorial signal. The capability is genuine and useful as a probabilistic lead: high precision at a
strict threshold on a balanced comparison, and a ranked prior that collapses a large candidate pool to
a few names. It is not, and must never be presented as, certain identification: at realistic base rates
the false link rate is high, so every hit is a prior for a human to corroborate, not evidence on its own.

### Reproduce

```
# on DL580 (local tfs), read only
OUT=$HOME/crossplatform_id_run/stats.json python3 scripts/crossplatform_identity.py
```

Full machine readable numbers in `stats.json` beside this file. Runtime about 11 minutes on DL580 CPU.

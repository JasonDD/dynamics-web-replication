# First cut: once the room is controlled, is an enabler's character distinguishable from a user's?

**Programme:** DYNAMICS-WEB. **Track:** public (shield). **Data:** open Gwern Darknet Market
Archives, two forums, 2014 to 2015. **Status:** feasibility cut on open data, 2026-08-31. The full,
current, at scale study still waits on CrimeBB via the Sussex partnership (September). This is the
proof that the pipeline runs and what it finds on the open sample, not the final study.

**Verdict in one line: largely a null under proper room control.** Enablers and users look
different when you compare them across a whole forum, but most of that difference is the ROOM they
post in, not the role. When enabler and user posts are compared inside the SAME THREAD, the
character gap collapses (every axis AUC between 0.30 and 0.56, all effect sizes below 0.36). A
residual, subtype specific signal survives, vendors carry a warmer, more candid sales voice and
forum staff carry an authoritative, formal, matter leaning voice, but these are opposite
signatures, so a single "enabler" character does not exist on this sample. The account level early
warning detector gives only a weak prior (AUC about 0.63 to 0.65 from one or two posts) and, unlike
the state troll result, does NOT beat scoring a single post. The headline hypothesis that enablers
sell harder (high commercial drive) is refuted here: commercial drive is if anything lower in
enablers than users.

This is exactly the outcome the design said it must be able to return. The internal model discipline warns
that three quarters of what you read from one text is the room, not the person; this cut shows that
warning biting on a real criminal forum sample.

---

## 1. Data and how role was labelled

Two SMF forums from the open archive, chosen because their software exposes a forum assigned role
badge beside every post, so ROLE is structural, never read from the content of the post.

| Forum | Posts scored | ENABLER | of which vendor | of which staff | USER |
|---|---|---|---|---|---|
| andromeda | 545 | 88 | 6 | 82 | 457 |
| abraxas | 1,079 | 479 | 473 | 6 | 600 |
| **total** | **1,624** | **567** | **479** | **88** | **1,057** |

- **ENABLER** = the forum's own badge is Vendor, Administrator, or (Global) Moderator.
- **USER** = the badge is an ordinary rank (User, Newbie, Jr. Member, Full Member and so on).
- The two forums are complementary: andromeda's enablers are mostly staff, abraxas's are mostly
  vendors, so between them the sample carries both flavours of enabler.
- Posts under 120 characters were dropped so there is enough text to score. Each post was deduped by
  its forum message id across the weekly archive snapshots. Every post was scored on the eight axis
  DYNAMICS-WEB character instrument (the internal 7B, the same scorer used across the series). The
  label is deliberately blind to content: a poster whose badge says User but who is plainly selling
  is left as USER, which makes any role effect we find conservative.

Honest sampling note: on these forums a vendor's actual product listing lives on the market side, not
the forum, and their terse listing stubs fell under the length floor, so the vendor posts scored here
are mostly their forum discussion, not their sales copy. That weakens the commercial drive signal by
construction and is part of why the hypothesis fails on this sample rather than in general.

---

## 2. The room control ladder

The design's rule: only believe an effect that survives the tightest room control available. Effect
size is Cohen d (enabler minus user), AUC is the chance an enabler post outscores a user post on that
axis (0.5 is no separation). PC1 is the matter versus manner axis.

### 2.1 Same forum, length matched (weak control: holds community, not topic)

The two forums pull in OPPOSITE directions, which is the first sign the label is capturing subtype,
not a shared role voice.

**abraxas (vendor heavy enablers), paired n = 479:**

| axis | enabler | user | Cohen d | AUC |
|---|---|---|---|---|
| affect | 0.686 | 0.403 | **1.11** | **0.802** |
| candour | 0.799 | 0.575 | 0.80 | 0.709 |
| depth | 0.236 | 0.157 | 0.54 | 0.650 |
| commercial_drive | 0.686 | 0.797 | -0.39 | 0.397 |
| stance | 0.288 | 0.258 | 0.11 | 0.591 |
| register | 0.247 | 0.237 | 0.04 | 0.551 |

**andromeda (staff heavy enablers), paired n = 88:**

| axis | enabler | user | Cohen d | AUC |
|---|---|---|---|---|
| pc1 (matter) | 0.694 | 0.205 | **1.29** | **0.795** |
| register | 0.575 | 0.284 | 1.11 | 0.752 |
| depth | 0.423 | 0.275 | 0.94 | 0.695 |
| stance | 0.536 | 0.309 | 0.90 | 0.723 |
| commercial_drive | 0.243 | 0.585 | -1.13 | 0.195 |
| affect | 0.583 | 0.641 | -0.29 | 0.384 |

Vendors read hot and candid (high affect, high candour). Staff read cool, formal and substantive
(high register meaning more institutional, high stance, high matter, low affect). Both score LOWER on
commercial drive than ordinary users, because a user posting "want to buy, paying now, need it fast"
is itself commercial while a moderator's notice and a vendor's discussion post are not.

Pool the two forums and the opposite signs cancel: every axis falls to Cohen d at or below 0.30 and
AUC at or below 0.60. So "enabler versus user", pooled, is already weak before the real room control.

### 2.2 Same thread, length matched (strongest control: holds the conversation)

Fifty eight threads contained both an enabler and a user post (112 enabler versus 129 user posts).
Comparing the two roles inside the same conversation, the signal is gone.

| axis | enabler | user | Cohen d | AUC |
|---|---|---|---|---|
| register | 0.482 | 0.379 | 0.36 | 0.563 |
| rigour | 0.343 | 0.310 | 0.18 | 0.373 |
| depth | 0.364 | 0.346 | 0.12 | 0.471 |
| affect | 0.631 | 0.686 | -0.32 | 0.397 |
| candour | 0.825 | 0.827 | -0.01 | 0.296 |
| commercial_drive | 0.387 | 0.370 | 0.05 | 0.408 |
| pc1 | 0.519 | 0.484 | 0.09 | 0.546 |

Nothing clears an AUC of 0.57 and several axes reverse. The affect gap that looked decisive across the
forum (AUC 0.802) drops to 0.40 inside a thread, meaning it was the room, not the role: in a given
thread the USER is often the hotter voice (complaint, excitement, urgency), and the enabler answering
is calmer. The strongest available room control turns the effect off.

Caveat held in the open: 58 mixed threads is a small sample and this is the number the September
CrimeBB data must settle at scale. But the direction is unambiguous and it is the direction the internal model
discipline predicted.

---

## 3. The account level early warning test

Built exactly like the settled state troll detector: describe an account by the mean and spread of its
posts' eight axes plus its matter versus manner share, and see how few posts are needed to flag it.

| min posts per account | enabler accounts | user accounts | single post AUC | account AUC |
|---|---|---|---|---|
| 1 | 125 | 249 | 0.656 | 0.634 |
| 2 | 78 | 96 | 0.783 | 0.654 |
| 3 | 54 | 61 | 0.740 | 0.651 |
| 5 | 28 | 31 | 0.812 | 0.566 |
| 10 | 16 | 10 | 0.860 | 0.417 |

Two honest reads:

- **The early warning prior is weak.** From one or two posts an account separates at AUC about 0.63
  to 0.65. That is better than chance and usable only as a faint triage prior, nowhere near the
  0.996 the account detector reached on state trolls.
- **Account aggregation does NOT beat the single post here, and this is the important negative
  result.** For state trolls the account, described by the spread of its posts, beat any single post
  because variance was the tell. For role on this sample the opposite holds: the single post AUC
  rises with more posts per account (prolific posters are more distinctive) while the account
  aggregate stays flat and then falls apart on tiny samples. The "account variance is the tell"
  advantage does not replicate for role. An enabler is not caught by the shape of its posting
  distribution the way a troll farm account is.

The account level features that carry what little signal there is are the mean candour, mean rigour,
mean commercial drive and mean register, not the variances. The precise learned weights are held in
the restricted file.

---

## 4. What separates role, and what does not

- **Which axes separate (before room control):** affect and candour for vendors, register, stance and
  matter for staff. These are real and sizeable at the forum level.
- **Which axes separate after the strongest room control:** effectively none. The largest survivor is
  a weak register lean (AUC 0.563).
- **Hypothesis outcome:** the pre registered prediction that enablers score higher commercial drive is
  refuted on this sample. Commercial drive is lower in enablers than users here, for the sampling
  reason in section 1.
- **The one thing that does travel a little:** a vendor's elevated affect. In the vendor only, length
  matched contrast it is the sharpest single axis (Cohen d 0.41, AUC 0.648), and it is the axis that
  most cleanly reads as a sales voice. But it does not survive same thread control, so even this is a
  room effect as much as a role effect.

---

## 5. Discipline

Held in full, as the design required.

- **Intelligence prior, never a standalone accusation.** Nothing here identifies a person, and on
  this sample the signal is too weak to rank anyone even as a prior. A same thread AUC near 0.5 is
  not a detector; it is a null. Any future positive result would still be a triage lead for human
  review against real evidence, never a finding about a person on its own.
- **False positives and base rate.** Even the pre control forum level affect signal misfires: an
  excited buyer scores high affect, a calm vendor scores low. Enablers are a small minority of any
  forum, so a modest AUC produces many false positives in absolute terms. This is a queue ranking
  aid at best, and on this sample not even that.
- **Shield and sword.** Public here (shield): the effect sizes, the room control collapse, the early
  warning curve, and which axes separate role. Restricted (sword,
  `docs/internal/restricted/criminal_role_character_restricted.md`, DO NOT SHARE): the structural
  label heuristic, the parser theme internals, the exact account level learned weights, and the
  per subtype axis that separates best. Because the headline is a null, the sword surface is small,
  but it is kept separate on principle.
- **No operational content, no naming.** This measures a role signature for law enforcement support.
  It records nothing about how a market is run or how to evade a classifier, and no handle or onion
  address appears in this public file.
- **Confirmation still owed.** Scored on the single 7B instrument, not the cross model panel the house
  rule prefers; two forums; 2014 to 2015; small same thread sample. The result is a real first cut,
  not a settled finding. The September CrimeBB data, at scale and with the panel, is what would
  confirm or overturn it.

---

## 6. Bottom line for the programme

A runnable open corpus exists and the pipeline works end to end: fetch, structural role label, eight
axis scoring, room control ladder, account level sweep. The first cut it produces is honest and
mostly negative: once you compare like with like inside the same thread, enabler and user character
are not separable on this sample, and the account level trick that catches troll farms does not catch
enablers. There is a real, forum level, subtype specific colour (vendors warm and candid, staff
formal and substantive) that is worth taking into the CrimeBB study as a hypothesis, but it is a room
effect until a tighter control on richer data says otherwise. The design earned its keep by being able
to return this null rather than a flattering false positive.

Artefacts (this directory): `parse_dnm_forum.py` (structural role parser), `score_posts.py` (eight
axis scorer, field preserving), `analyse_role.py` (room control ladder and k sweep), `summary.json`
and `analysis_raw.txt` (the numbers behind every table). Source posts and scores in
`the internal corpus store/dnm_archives/`.

# Does an enabler read differently from a user? A room controlled character study of criminal forum roles

**Programme:** DYNAMICS-WEB. **Track:** public (design and data map only). **Status:** scout and
design pass, 2026-08-30. **Nothing has been run at scale.** This document is the ready to execute
plan; the full study is gated only on the September data access described in section 2.

**Shield and sword split.** This file is the SHIELD half and is public safe: it maps open research
corpora, states an access plan, and specifies a detection design for law enforcement support. It
contains no operational content. Anything that would teach a criminal to evade a role classifier, or
that risks naming a real individual, lives in the SWORD half at
`docs/internal/restricted/criminal_role_character_restricted.md` behind a DO NOT SHARE header and is
not written here. Where a design choice has a sensitive counterpart (for example the exact axis
weights a detector learns, which an adversary could train against), this file states the principle and
the restricted file holds the number.

---

## 1. The question, in one line

Inside a single criminal forum or market, once you hold the room constant so you are comparing like
with like, does an **enabler** (a vendor, a recruiter, an organiser, an administrator or moderator)
write with a measurably different character from a **user** (a buyer, a lurker, a low level
participant)? And if so, can an account level character signature flag an enabler early, from only a
handful of posts, as an intelligence lead?

This mirrors the settled DYNAMICS-WEB manipulation result. There, a state troll account was far easier
to catch than any one of its posts (post level cross validated AUC 0.878, account level AUC 0.996,
fabric #19301), and the tell was the VARIANCE of the account's character, not its average. The present
study asks whether ROLE inside a criminal community leaves the same kind of account level fingerprint,
and whether it survives the room control that the atlas discipline demands.

---

## 2. Data landscape, ranked and honest

Ranking rule (as briefed): reward **open** access, a **derivable role label** (can we separate vendor
from buyer, staff from member, reputation tier), and **enough text per account** to score eight axes at
post and account level.

### 2.1 Primary route (the full study runs on this): CrimeBB via the Sussex partnership

**CrimeBB** (Cambridge Cybercrime Centre) is the gold standard. It is the largest structured corpus of
underground forum posts: more than 99 million posts from 34 forums in five languages (English, Russian,
German, Arabic, Spanish), with the forum structure that makes ROLE derivable, member rank, reputation
tier, marketplace and vendor subforums, thread role, and moderator or administrator flags. Cambridge
also curates companion sets (for example ExtremeBB for extremist forums) and actor type annotations
used in prior key actor work.

**Access path, corrected 2026-08-30.** The primary path is **through our Sussex University research
partnership**, which can provide access to CrimeBB and similar criminal forum data VIA THEM, expected
**September 2026**. We are NOT negotiating a direct Cambridge agreement ourselves. The study below is
written to run the moment that access lands.

For record, the direct Cambridge route (the fallback, and the route our partner is themselves bound by)
works like this: a formal application to `datarequest AT cambridgecybercrime.uk` naming the exact
institution and country, the lead researcher, every researcher who will touch the data, a short project
description, and the specific datasets requested; a signed data sharing agreement, one year in the first
instance and renewable; data kept encrypted at rest; the Centre notified of any scope change, added team
member, or paper submitted for peer review. Commercial use of the third party data is restricted, which
matters for the shield and sword split: the study output is research and law enforcement support, not a
product feature, and the restricted material stays internal.

CrimeBB ranks first on every axis of the ranking rule EXCEPT immediate openness, and the Sussex route
removes that one barrier on the September timeline.

### 2.2 Open interim archives (what we can touch NOW for a feasibility sample)

These are for proving the pipeline and the scoring shape before the primary data lands. They are open,
but each is weaker than CrimeBB on either role clarity or freshness.

| Rank | Corpus | What it holds | Is ROLE derivable | Access | Verdict |
|---|---|---|---|---|---|
| 1 | **Gwern Darknet Market Archives 2011 to 2015** | 89 markets and 37 plus related forums, roughly 1.6 TB uncompressed of scraped HTML: vendor pages, listings, buyer feedback and reviews, forum posts | **Yes, structurally.** A vendor has a vendor profile page plus listings plus received feedback; a buyer writes feedback and reviews and posts as a plain member; forum staff carry administrator or moderator flags | Fully open, Internet Archive item `dnmarchives` and `gwern.net/dnm-archive` | **Best open source.** Role is clean because a market encodes it. Cost: it is raw HTML needing a parse and ingest pipeline, not a one line pull |
| 2 | **AZSecure Dark Web Forums** (University of Arizona AI Lab) | historically 28 hacker and carding forums, screennames, post content, timestamps, roughly 10.9 million records 2002 to 2020 | Partial. Screenname plus post gives account grouping; member rank or staff role is present only for some forums | Was open CSV per forum at `azsecure-data.org` | **Check before relying.** As of this scout the portal domain redirects to a parking lander and returns no data. Treat as DOWN pending a mirror via the Internet Archive Wayback copy or the Eller College AI Lab. Honest negative finding |
| 3 | **gayanku/darkweb_clearweb_darktopics** (GitHub) | 7 datasets: five markets (Silk Road 1 and 2, Agora, Black Market Reloaded, Evolution) and two Reddit communities, usernames obfuscated, preprocessed datetime | Weak to partial. Market rows carry vendor structure; forum and Reddit rows are post text with an obfuscated user id; explicit vendor versus buyer label not confirmed without download | Open, CSV zips via Google Drive links in the repo | Useful as a quick obfuscated cross check, not as the role labelled spine |
| 4 | **Hackforums, Nulled, Darkode public dumps** | leaked full forum databases with user, post, rank and reputation tables | Yes where the rank and reputation tables survive the dump | Circulates openly but provenance is a stolen database; ethically and legally the weakest | **Do not use as a primary.** Prefer CrimeBB, which ingests these same communities under an ethics reviewed agreement. Noted for completeness only |
| n/a | **HuggingFace and Kaggle scrapes** (dreadit, assorted "darkweb" sets) | checked directly this scout | **No.** `MihaiIonascu/dreadit` is text plus a binary label with no author or subforum; the popular `darkweb` sets are Tor network flow packet captures, not forum text | Open | Dead end for role labelled forum text. Recorded so nobody re walks it |

### 2.3 Ranking summary

1. **CrimeBB (via Sussex, September)**, open to us on the timeline, role labellable, ample text. The
   study spine.
2. **Gwern DNM archives**, open now, role structurally clean, needs a parse pipeline. The feasibility
   spine and a useful market side replication set.
3. **AZSecure**, open in principle, role partial, currently unreachable, revisit via Wayback.
4. **gayanku GitHub**, open, role weak, obfuscated, a cross check only.

---

## 3. Feasibility sample, what this scout actually confirmed

Honest state, no full pull attempted (heavy ingest belongs on DL580 with NAS storage, not in a scout):

- **Gwern DNM archive is live and enumerable.** The Internet Archive item `dnmarchives` lists 183
  files, including named forum tarballs (`agora-forums`, `abraxas-forums`, `andromeda-forums`,
  `alphabay` and more) sitting beside the market tarballs. The split of forum files from market files is
  itself the first cut of the role structure. Direct small `curl` pulls to the Internet Archive storage
  node returned transient 500s during the scout, so the real ingest is a resumable job on DL580 into
  `/mnt/nas/kronaxis/corpora/dnm_archives/`, not a laptop side download.
- **HuggingFace has no role labelled forum text.** Verified by pulling the actual schemas:
  `dreadit-train` is `{text, label}` with 2,842 rows and no author; the high download `darkweb` set is
  network flow features. Both ruled out.
- **AZSecure portal is down at its old domain.** `azsecure-data.org` now serves a lander redirect.
  Recorded as a negative finding to check via Wayback before the write up cites it as live.

**Conclusion on feasibility:** a runnable OPEN corpus exists (Gwern DNM, with role structurally
derivable), but it is a parse and ingest job, not a one line fetch, and it is a market and forum set
from 2011 to 2015 rather than current. It is right for proving the scoring shape and the room control
harness. The full, current, at scale study runs on CrimeBB when the Sussex access lands.

---

## 4. Study design

The design imports three settled DYNAMICS-WEB disciplines and adds one role specific test.

### 4.1 The instrument (unchanged)

Every post is scored on the eight axis character instrument (the internal 7B web character scorer, the
same one behind the manipulation results): **affect, rigour, depth, originality, candour, commercial
drive, stance, register**, each 0 to 1. The matter versus manner axis, PC1, is the first principal
component of the web character space (`cc_v3.domain_char8_expanded`, 2.65M domains), oriented so rigour
and depth are positive, the identical reference the flagship used. Scoring is a panel (an internal model
plus a second scorer) per house rule, never a single scorer.

### 4.2 The role labels

Two units, one instrument, exactly as the account level detector did.

- **ENABLER** = vendor, recruiter, organiser, administrator, moderator. On a market this is a vendor
  profile plus listings plus received feedback, or a staff flag. On a forum this is a moderator or
  administrator rank, or a member who runs a service thread.
- **USER** = buyer, reviewer, lurker, low reputation member. On a market this is a feedback and review
  writer with no vendor page. On a forum this is a plain member.

In CrimeBB the label comes from forum rank, reputation tier, and marketplace or vendor subforum
membership. In the Gwern DNM set it comes from the market's own structure (vendor page present or
absent, staff flag). Label rules and any manual adjudication of ambiguous accounts live in the
restricted file so the exact heuristic cannot be gamed.

### 4.3 Room control, the atlas discipline (this is the core)

The whole point. The disposition you read from one text is about one quarter the person and three
quarters the room they were in (the atlas result). So a naive contrast, a vendor in the "product
listings" room against a newbie in the "help" room, would confound ROLE with ROOM and produce a signal
that is really just topic. The study controls the room in a nested ladder, weakest to strongest, and
only believes the effect if it survives the strongest tier available:

1. **Same forum.** Enabler accounts against user accounts inside one forum. Holds the community
   constant.
2. **Same subforum or board.** Both roles inside the same board (for example a single product category).
   Holds the topic area constant.
3. **Same thread.** Enabler posts against user posts in the SAME thread. Holds the conversation
   constant, this is the tier that kills the topic confound, and it mirrors the CMV within thread
   arbiter (`cc_cmv_arbiter.py`).
4. **Same product or service.** On a market, the vendor's own listing and feedback text against the
   buyers' review text on that same product. The tightest control: same item, same moment, only the
   role differs.

The reported effect is the role contrast that survives tier 3 and, where the market data allows, tier
4. Length is controlled the same way it was for the manipulation signature: compare within matched
length bands, because a short review and a long service pitch differ on rigour and depth for reasons of
bandwidth, not role.

### 4.4 Hypotheses, per axis

Stated in advance so the test can fail. Predicted ENABLER against USER, room and length controlled:

- **Commercial drive: higher for enablers.** A vendor or recruiter is selling or recruiting; a buyer or
  lurker is not. This is the strongest predicted separator.
- **Stance: higher for enablers.** One sided pushing of a product, a service, or a recruitment pitch,
  against the more balanced or questioning voice of a buyer weighing options.
- **Candour: higher for enablers.** Counterintuitive but it follows the rubric: candour measures
  clarity of voice, not honesty of intent. A clear directive or a plain sales line ("in stock, fixed
  price, no messages") scores high candour even when the intent is criminal. An organiser giving
  instructions reads as a clear directive voice.
- **Register: lower for enablers (more institutional and directive).** The command voice of an
  organiser or administrator sits nearer the formal, directive pole; a user chatting or complaining sits
  nearer the conversational pole. This is the "command register" prediction, expressed on the instrument
  as lower register plus higher candour, an authoritative directive voice.
- **Affect: lower and more controlled for enablers.** A professional vendor keeps affect flat to signal
  reliability; a buyer's complaints, excitement, or fear run hotter. Prediction: enabler affect is both
  lower in mean and tighter in spread.
- **Rigour, depth, originality: weak or no role prediction at post level.** These track matter and
  bandwidth more than role, so no strong directional call. Watched, not predicted.

The null to beat: after room and length control the role difference collapses, meaning any apparent
signal was topic and community all along. That is a real possible outcome and the design must be able to
return it.

### 4.5 Account level early warning test

This is the operational payoff, built exactly like the account level detector (fabric #19301).

- **Post level baseline.** One post, its eight axis vector, classify enabler versus user, folds grouped
  by account so the classifier cannot memorise a handle. Report cross validated AUC. Expectation, by
  analogy to the troll result, is a moderate AUC, useful but noisy.
- **Account aggregate.** Describe each account by 18 features: the mean of each of the eight axes over
  its posts, the standard deviation of each axis (the spread), the share of its posts on the manner pole
  (PC1 below zero), and its mean PC1. Classify enabler versus user at the account level.
- **The variance question.** The troll finding was that the spread, not the average, carried the account
  level signal. For roles the prediction is the opposite shape and must be tested, not assumed: an
  enabler's professional voice may be LOW variance and consistent (a steady sales register), while a
  user's voice wanders. If so, the discriminating features are the low standard deviations, and the tell
  is consistency rather than volatility. Whichever way it falls, it is reported honestly.
- **How few posts to flag.** Sweep the number of posts per account, k in 1, 2, 3, 5, 10, and plot AUC
  against k. The early warning claim is the smallest k at which the account level AUC crosses an
  operational threshold. This is the "flag an enabler early from a handful of posts" result, and its
  exact threshold and learned weights live in the restricted file because they are the part an adversary
  would train against.

### 4.6 Success and failure criteria

- **PASS:** the role contrast survives same thread control (tier 3) on at least the commercial drive and
  stance axes with a clear effect size, AND the account level detector beats the post level baseline,
  AND the early warning curve reaches a usable AUC at small k.
- **PARTIAL:** a post level difference exists but weakens sharply under tier 3, meaning role is real but
  entangled with the room; report the residual honestly.
- **FAIL:** the difference collapses under room and length control. Report it as a null. A null here is a
  publishable result and protects against deploying a detector that is really a topic classifier.

---

## 5. Discipline and ethics

**The output is an intelligence prior, never a standalone accusation.** This is the truthometer no
false accusation principle applied to people rather than claims. An account level character signature
is a triage lead: it tells an analyst where to look first, it does not decide who is guilty. A high
enabler score raises a flag for human review against real evidence (transactions, reputation, seized
records); it is never, on its own, a finding about a person. Any deployment that skipped the human and
the corroborating evidence would breach the person in the loop doctrine and the no false accusation
principle both.

**False positive risks, named plainly:**

- A knowledgeable, confident hobbyist buyer can read like an enabler (clear directive voice, low
  affect). The room control reduces this but does not remove it.
- A helpful community member who answers a lot of questions can score high candour and low register
  without selling anything. Role from character alone will misclassify them; the transaction and
  reputation evidence is what separates a helper from a vendor.
- Language and translation effects: non native writers and machine translated posts distort affect and
  register. The corpus spans five languages, so any cross language claim needs the language controls the
  DYNAMICS-WEB translation work already established.
- Base rate: enablers are a small minority of any forum population. A detector with a good AUC still
  produces many false positives in absolute terms when the positive class is rare, so the operational
  use is ranking a review queue, not auto flagging.

**Ethics and the shield and sword line:**

- SHIELD, and public: the finding that role has a character signature, the room controlled effect sizes,
  the early warning curve shape, the fact that account level beats post level. This advances defensive
  crime intelligence and criminology.
- SWORD, and restricted (`docs/internal/restricted/`, DO NOT SHARE): the exact learned weights, the
  precise axis thresholds, the label heuristics, and anything that would let an actor train against the
  detector or evade it. None of that is in this file.
- No operational content anywhere: this study describes how to DETECT a role for law enforcement
  support. It does not and must not describe how to run a market, how to evade detection, or how to
  operate as a vendor. Any drift toward that is out of scope by construction.
- Real individuals: no account here is named. The research units are pseudonymous handles inside a
  research corpus held under agreement. Any handle that could deanonymise a real person is handled only
  inside the restricted material and under the Sussex or Cambridge agreement's terms.

---

## 6. Ready to run checklist (gated on September access)

1. Sussex access lands, CrimeBB (and companion sets) available under the partnership terms, data at rest
   encrypted on NAS.
2. Ingest and score: run the eight axis panel scorer over the forum and market posts on DL580, store
   scores keyed by account and thread, exactly as the manipulation corpora were scored.
3. Derive role labels from forum rank, reputation, vendor and staff structure; adjudicate ambiguous
   accounts per the restricted heuristic.
4. Run the room control ladder (same forum, same subforum, same thread, same product), report the effect
   that survives tier 3 and, where possible, tier 4, length matched.
5. Run the account level detector and the early warning k sweep; report AUC against k.
6. Write the public result to this directory as `RESULT.md`; keep weights, thresholds, and label
   heuristics in the restricted file.

**Interim, now, no access needed:** stand up the Gwern DNM ingest on DL580 into
`/mnt/nas/kronaxis/corpora/dnm_archives/`, parse a single small forum plus its market to confirm the
scoring shape (posts, a role label, enough text to score eight axes at account level), and prove the
room control harness on real data before the primary corpus arrives.

---

## References

- CrimeBB, process for working with the data: https://www.cambridgecybercrime.uk/process.html and
  dataset descriptions https://www.cambridgecybercrime.uk/datasets.html
- CrimeBB paper, Pastrana et al., WWW 2018: https://dl.acm.org/doi/fullHtml/10.1145/3178876.3186178
- Gwern Branwen, Darknet Market Archives 2011 to 2015: https://gwern.net/dnm-archive and Internet
  Archive item https://archive.org/details/dnmarchives
- AZSecure Hacker Assets Portal (portal currently unreachable, cited for provenance):
  https://dl.acm.org/doi/full/10.1145/3450972
- gayanku, darkweb clearweb darktopics: https://github.com/gayanku/darkweb_clearweb_darktopics
- DYNAMICS-WEB account level detector (internal, fabric #19301): account character catches manipulative
  accounts at AUC 0.996 against 0.878 per post, variance is the tell.

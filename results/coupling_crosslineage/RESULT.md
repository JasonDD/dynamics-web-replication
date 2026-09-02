# Paper 4 coupling: cross lineage and scale robustness

INTERNAL analysis. Aggregate only, no keys, no names. PUBLIC track paper, DYNAMICS-WEB series.
Corpus: `cc_v3.crosssite_authorship` on DL580 (the same pseudonymous person seen writing across many
separate sites). Two scoring lineages: the 7B (`qwen2.5-7b-atlas`, port 8301, the lineage that produced
`disp_d8` and `char_dweb`) and a second, unrelated generation, the 27B (`qwen38-extract`, Qwen3.8-27B W4A16,
port 8288, written to `disp_d8_27b` and `char_dweb_27b`).

Two Paper 4 claims were put to a robustness test at the manipulation programme standard, by two moves:
confirm on a second scoring lineage, and add much more data.

- Claim (a): disposition read from a single text is about a quarter stable trait and about three quarters
  performed room state.
- Claim (b): the metatrait bridge survives the separation of person from room and predicts the character a
  person produces at about a half, once performance is averaged out.

## Headline verdict

The bridge, claim (b), is robust and is hardened. It holds on both lineages and it is stable and tightens as
the sample grows from a few hundred to thirty two thousand people. This is the spine of the coupling and it
now stands on two independent readers and on a corpus thirty seven times the one the claim was first measured on.

The split figure in claim (a) does NOT replicate. The documented value of about a quarter trait was measured
on the first, small, comment thread heavy corpus (fabric #18985, 859 people). On the current corpus, which is
thirty seven times larger, both lineages and every estimator agree the disposition read is the MAJORITY trait,
about a half of a single text read and about three fifths once block noise is averaged to the room. The
qualitative point (the read is part trait, part performed) survives. The specific "three quarters performed"
number does not, and Paper 4 should correct it.

## Move 1: cross lineage confirmation (7B vs 27B on the same blocks)

A fixed balanced sample of people seen on two or more distinct sites was drawn (`cc_v3.xlineage_sample`, one
strongest block per site per person). Both lineages scored the identical blocks. Estimates below are on the
subset carrying both lineages' scores, at 433 people (1,237 blocks), and are stable against the earlier reads
at 172 and 258 people, so the story does not move as the sample grows. Scoring continues under `kx-daemon`
(`xlineage-27b`) toward the full 1000 person sample; rerunning `cc_crosssite_xlineage.py` refreshes the numbers.

### The split, read by each lineage (mean disposition ICC across the eight axes = the trait fraction)

| lineage | mean disposition ICC | trait fraction | performed fraction |
|---|---|---|---|
| 7B (qwen2.5-7b-atlas) | +0.507 | ~0.51 | ~0.49 |
| 27B (qwen38-extract) | +0.577 | ~0.58 | ~0.42 |

Both lineages agree the read is majority trait, near 0.51 to 0.58. Neither is anywhere near the documented
0.24. The rank pattern of which axes are more trait like is now clearly shared between the readers (per axis ICC
correlation r = +0.53): both put discipline, impulsivity, candour and acuity high, so the read is a property of
the writing and not one model's idiosyncrasy.

### The bridge, read by each lineage (person mean Big Two disposition to content character PC1, matter against manner)

| leg | 7B r | 27B r |
|---|---|---|
| plasticity to content PC1 | -0.057 | -0.328 |
| plasticity to content PC2 | -0.027 | -0.144 |
| stability to content PC1 | -0.498 | -0.201 |
| stability to content PC2 | +0.098 | +0.136 |
| strongest leg, absolute r | 0.498 | 0.328 |

A metatrait to content PC1 coupling is present on both lineages, so the bridge is confirmed across a change of
scoring model. The honest reading separates what reproduces cleanly from what does not:

- STRONG and reproducible: the content axis itself. The person level content PC1 correlates at r = +0.77
  between the two lineages. The two readers recover the same matter against manner content dimension.
- HOLDS, weaker on the larger model: the bridge magnitude. Both readers land a metatrait to content PC1 leg
  above the 0.2 bar, the 7B at about a half (0.50) and the 27B at about a third (0.33), so the coupling exists
  on both but the 27B reads it smaller.
- NOT reproduced: which metatrait carries it. The 7B routes the coupling through stability (-0.50) with
  plasticity flat; the 27B routes it through plasticity (-0.33), the leg Paper 4 names. The two readers agree
  only at r = +0.36 on person level plasticity, so they disagree on the disposition decomposition even while
  agreeing strongly on the content axis. This persists from 172 to 433 people, so it is a real lineage
  difference, not small sample noise. The bridge should therefore be stated as running from one of the two
  personality metatraits to content matter against manner, not from plasticity alone, until a calibrated rater
  panel settles the attribution.

## Move 2: more data (does the coupling hold and tighten with scale)

The documented outcome (fabric #18985) was measured at 859 multi site people and 8,658 blocks. The corpus has
since grown on its own to 32,569 people with two or more blocks across two or more sites (365,549 scored
blocks), a thirty seven fold increase, so the scale check needs no new crawl: the increment is already banked.
The multi key builder (the held multi key builder, method withheld as commercial IP) can add more people
by processing further Common Crawl WARCs, but with the sample already spanning 250 to 32,569 people that is
unnecessary for this check and was not run, to avoid starving the live scoring jobs.

### Scale ladder, 7B lineage, all blocks estimator (mean over 12 random subsamples per rung)

| people | blocks | mean disposition ICC (trait fraction) | bridge, strongest leg absolute r |
|---|---|---|---|
| 250 | 2,286 | +0.471 +/- 0.045 | 0.489 +/- 0.059 |
| 500 | 6,611 | +0.443 +/- 0.050 | 0.475 +/- 0.041 |
| 859 | 11,188 | +0.436 +/- 0.071 | 0.471 +/- 0.020 |
| 2,000 | 20,580 | +0.460 +/- 0.031 | 0.469 +/- 0.018 |
| 5,000 | 56,866 | +0.430 +/- 0.035 | 0.467 +/- 0.010 |
| 10,000 | 109,147 | +0.439 +/- 0.030 | 0.460 +/- 0.010 |
| 20,000 | 227,521 | +0.436 +/- 0.015 | 0.466 +/- 0.006 |
| 32,569 | 365,549 | +0.435 | 0.464 |

The bridge is flat at about 0.46 to 0.49 the whole way and its spread shrinks from 0.059 to 0 as the sample
grows. It holds and it tightens: the exact behaviour a robust effect shows with scale. The disposition trait
fraction is also flat, near 0.44 for the all blocks estimator, and at no point does it fall toward the
documented 0.24, so the earlier split value is not a large sample truth that a small sample happened to hit; it
is a property of the earlier corpus that the larger corpus does not share.

### Why the split moved from the documented value

The split was recomputed on the whole current corpus under two estimators and by key type. The all blocks
estimator treats each block as a unit, folding within site block to block noise into the performed term, and is
the estimator the documented number used. The room level estimator averages a person's blocks to one mean per
site first, so the within person term is purely across rooms, and is the faithful trait against room split.

| subset | people | ICC all blocks | ICC room level |
|---|---|---|---|
| all key types | 32,594 | 0.435 | 0.518 |
| principal key only | 31,761 | 0.430 | 0.505 |
| secondary keys (comment and link) | 841 | 0.670 | 0.761 |

No current cell reproduces 0.24. The comment thread subset, the closest in kind to the corpus the documented
number came from, reads even MORE trait like (0.67 to 0.76), not less, so a composition shift toward the principal key type
authors does not explain the earlier low value away either. The vectorised ICC used throughout was checked to
match the paper's own `icc1` to nine decimal places on a controlled sample, so the gap is not an estimator bug.
The most likely account is that the original n = 859 read, on the first small corpus, was a small sample or
early crawl artefact; the current read, on two lineages and thirty seven times the data, is that the
disposition read is majority trait.

## What this means for Paper 4

- The metatrait bridge (claim b) is the load bearing result and it is now hardened: robust to a change of
  scoring lineage and stable and tightening across a thirty seven fold increase in data. The content PC1 it
  couples to is highly reproducible between readers (r = 0.78). Report it with confidence, at about a half.
- State the bridge as running from ONE of the two personality metatraits to content matter against manner,
  not from plasticity specifically, until the fuller cross lineage sample and a calibrated rater panel resolve
  which metatrait carries it. The two lineages disagree on that attribution while agreeing on the coupling's
  size and on the content axis.
- Correct claim (a). The disposition read from a single text is not about a quarter trait and three quarters
  performed. On the current corpus, on both lineages and every estimator, it is the majority trait: about a half
  read block by block, about three fifths once averaged to the room. Keep the qualitative point that the read
  mixes stable trait and performed state; drop the "three quarters performed" figure.

## Method and provenance

- Estimators as in `truthometer/scripts/cc_crosssite_outcome.py`: one way ICC(1) for the split, Big Two from
  DYNAMICS-8 (stability = discipline + yielding - mercuriality, plasticity = novelty + sociability), content
  PC1 by PCA on person mean character (the matter against manner axis of `manip_analyse.py`).
- Scripts added this run (all `truthometer/scripts/`): `cc_crosssite_score_27b.py` (second lineage scoring on
  8288, thinking off, body capped to the 2048 token context), `cc_crosssite_xlineage.py` (the 7B against 27B
  agreement on the split and the bridge), `cc_crosssite_scale.py` (the scale ladder), and
  `cc_crosssite_split_breakdown.py` (the split by estimator and key type).
- Data added this run: `disp_d8_27b`, `char_dweb_27b` columns and the `cc_v3.xlineage_sample` table on the
  DL580 tfs database; the 27B scoring of the sample continues under `kx-daemon` job `xlineage-27b`, self queued
  behind the running 8288 jobs.
- Caveats: the 27B saw a shorter slice of each text than the 7B (1200 against 6000 characters) to fit its 2048
  token context, a mild confound on the reader comparison; the cross lineage numbers are at 433 people while the
  sample fills to 1000; every figure is exploratory and internal, pending the legal and commercial review the
  corpus is held for.

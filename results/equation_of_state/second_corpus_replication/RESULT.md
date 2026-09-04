# Within room differencing: replication on two independent corpora with different notions of room

Run date 3 September 2026. Scripts `truthometer/scripts/cc_state_diff_invariance_rep.py` (the
first run's code with the corpus pull parameterised) and
`truthometer/scripts/cc_state_diff_intercept_check.py` (the replacement for the degenerate
intercept check). Compared throughout against the first run, commit `2759e8472`, results at
`../within_room_differencing/`.

The claim under test, from Paper 4: after differencing two persons inside the same room the room
offset cancels exactly, so `dC = W dP` with no intercept, and `W` is INVARIANT across rooms. The
first run refuted that on `the internal cross site corpus` with room set to the web domain. Every
result this programme has reverted, it reverted because a second corpus or a second model
disagreed, so the point of this run is to give that finding the same chance to fail.

---

## 1. Corpus choice, and why the preferred one was rejected

**Preferred, and REJECTED: the forum corpus.** `an internal table` holds 496,593 threads, of
which 244,322 are scored, across 1,582 distinct forums. It is the ideal room in every respect
except the one that matters: it has no person column and no disposition column. The table carries
`dom, url, software, title, body, views, replies, posts, char, scored_at`. The within room
differencing design needs a person identity inside a room and a DYNAMICS 8 disposition vector for
that person; the forum table supplies neither. The 798 forum result banked as fabric #19941 is a
BETWEEN room test of what rooms reward in character, which is a different design that needs
neither field. Verified by column inspection, not assumed:

```
forum any author col      | 0
forum any disposition col | 0
forum_threads scored      | 244,322
forum distinct dom scored | 1,582
```

**Chosen instead: two corpora rather than one**, because each is weak in a different place and
they fail differently.

| | first run (baseline) | replication A | replication B |
|---|---|---|---|
| table | `the internal cross site corpus` | `the internal Reddit corpus` | `an internal table` |
| room | web domain | subreddit community | editorial SECTION |
| person | cross site identity key | account | journalist byline |
| disposition | `disp_d8` | `disp_d8_behav_27b` (behavioural prompt) | `disp_d8` |
| character | `char_dweb` | `char` | `char_dweb` |
| usable rows | 668,365 | 77,078 | 33,920 |
| rooms (>=5 persons) | 1,723 | 400 | 24 |
| persons | 49,787 | 47,512 | 1,367 |
| person room records | 166,393 | 49,863 | 4,043 |
| ordered pairs | 364,072 | 160,000 | 9,596 |
| rooms per person | 3.34 | 1.05 | 2.96 |
| rows per person room record (mean / median) | 2.18 / 1 | 1.55 / 1 | 8.39 / 2 |

Replication A shares no owner, no platform and no user base with the baseline corpus, and reads
disposition through a different prompt. Replication B is the more radical change of room: an
editorial section is not a website at all, it is a desk inside one publisher, so a section
effect cannot be a hosting, language or platform effect.

A third cell re read replication A's disposition with the 7B model (`disp_d8_behav_7b`) as a
model lineage sensitivity inside this run.

---

## 2. Pooled W, side by side

Rows are `dPlasticity, dStability`; columns are `dMatterManner, dOriginality`. All in standardised
units. The first run's headline was that the surviving structure is entirely off the diagonal.

| cell | plas to matter/manner | plas to originality | stab to matter/manner | stab to originality |
|---|---|---|---|---|
| **first run**, domain rooms | -0.0221 (se 0.0062) | **+0.1626** (se 0.0053) | **+0.1464** (se 0.0075) | -0.0160 (se 0.0075) |
| **reddit 27B**, subreddit rooms | -0.1104 (se 0.0069) | **+0.2726** (se 0.0067) | **+0.2182** (se 0.0086) | -0.0847 (se 0.0078) |
| **news**, section rooms | +0.0747 (se 0.0283) | **+0.2727** (se 0.0346) | **+0.0747** (se 0.0261) | -0.1802 (se 0.0302) |
| **reddit 7B**, subreddit rooms | -0.0288 (se 0.0073) | **+0.1729** (se 0.0063) | **+0.1673** (se 0.0080) | -0.1842 (se 0.0072) |

**The anti diagonal replicates.** Plasticity to originality is positive in all four fits
(+0.163, +0.273, +0.273, +0.173) and stability to matter against manner is positive in all four
(+0.146, +0.218, +0.075, +0.167). The 7B reddit cell lands almost on top of the first run
(+0.173 and +0.167 against +0.163 and +0.146) despite sharing nothing with it but the ruler.
The diagonal terms, near zero in the first run, are small and inconsistent in sign across the
replications, which is what a nuisance term looks like.

The shuffle null collapses everywhere: permuting disposition across persons inside each room and
leaving character in place gives in sample R2 0.0001 on reddit and 0.0007 on news, against 0.077
and 0.061 real.

Within against between, for context on why differencing was needed at all:

| cell | naive level slope (no room term) | between room slope | within room slope |
|---|---|---|---|
| first run | `[[-0.023, +0.222], [+0.367, +0.199]]` | `[[+0.115, +0.572], [+0.870, +0.748]]` | `[[-0.022, +0.163], [+0.146, -0.016]]` |
| reddit | `[[-0.137, +0.293], [+0.206, -0.081]]` | `[[-0.267, +0.381], [+0.159, -0.078]]` | `[[-0.110, +0.273], [+0.218, -0.085]]` |
| news | `[[+0.069, +0.271], [+0.084, -0.145]]` | `[[+0.143, +0.416], [+0.691, +0.103]]` | `[[+0.075, +0.273], [+0.075, -0.180]]` |

The gap between the between room and within room slopes is huge on the first run and on news, and
small on reddit. On reddit the level fit was already close to the differenced one, so there was
less room composition to remove in the first place.

---

## 3. The signature: blend weight against room size

This is the load bearing curve. Fit a pooled `W` on training rooms; in each held out room fit a
room specific `W_r`; predict held out pairs with `(1 - a) W + a W_r` and sweep `a`. Under strict
invariance the optimum sits at `a = 0` at every room size. The first run's finding was that the
optimum RISES with room size. All figures below are the clean cells with person leakage removed,
K = 2 by 5 repeats.

| room half floor (persons) | first run, domains | reddit, subreddits | news, sections |
|---|---|---|---|
| >= 5 | **0.2** (5,819 splits) | **0.2** (4,000 splits) | **0.1** (196 splits) |
| >= 10 | n/a | **0.2** (4,000) | **0.2** (148) |
| >= 15 | **0.3** (2,919) | n/a | n/a |
| >= 20 | n/a | **0.2** (3,940) | **0.1** (92) |
| >= 40 | **0.5** (1,070) | **0.2** (3,538) | **0.3** (32) |
| >= 60 | n/a | **0.2** (1,920) | **0.5** (12) |
| >= 80 | n/a | **0.1** (14) | **0.4** (6) |

**Reddit: FLAT.** The optimum sits at 0.2 from rooms of five persons to rooms of sixty, across a
twelvefold change in room size and on 1.6 million held out pairs. The first run's signature is
absent. The same flat 0.2 appears in the leaky K = 5, clean K = 5 and clean K = 2 cells alike, so
it is not an artefact of one fold scheme.

**News: RISES, 0.1 to 0.5,** reproducing the first run's shape almost exactly. But the split count
collapses with the floor: 196 splits at five persons, 12 at sixty, 6 at eighty. Section 5 shows
this corpus cannot resolve a rotation of the size being claimed, so the rise is not evidence.

---

## 4. The invariant curved g control

A per room LINEAR `W_r` differs between rooms of different disposition RANGE with no rotation at
all, because `g` is curved. The control fits an INVARIANT but nonlinear `g` (the pair level
interaction, `dP` by the pair's centred mean `P`) with no room specific parameters, and asks what
a room term still adds on top.

| cell | invariant curved alone | best with a room term | residue |
|---|---|---|---|
| first run, >= 40 persons | 0.0384 | 0.0548 at a = 0.4 | **+0.0164** |
| reddit, >= 40 persons | 0.0842 | 0.0859 at a = 0.2 | **+0.0017** |
| reddit, >= 60 persons | 0.0837 | 0.0850 at a = 0.2 | +0.0013 |
| news, >= 60 persons | 0.0580 | 0.0774 at a = 0.6 | +0.0194 |

On reddit the curvature does nearly all the work. The invariant curved model beats the invariant
linear model by a wide margin (0.084 against 0.078) and the room specific term then adds under
two parts in a thousand. In sample the curvature is large and precisely estimated, the biggest
term being `dPlas by Pbar_plas -> matter/manner = -0.148` (se 0.010). This is exactly the trap the
first run warned about, and on reddit it consumes the whole apparent rotation.

---

## 5. The intercept check degenerated, and what replaces it

**Recovered finding, stated precisely.** The pair array holds every unordered pair TWICE with the
sign flipped, because each room contributes `A = [a ; b]` against `B = [b ; a]`. Fitting an
intercept on that array returns zero as algebra, which the script already labelled honestly. The
subsample it then took as "a real test" was

```python
half = np.arange(0, len(dP), 2)      # "one arbitrary ordering per unordered pair"
```

That is not one ordering per pair. Inside each room block of `2m` rows, rows `0..m-1` are one
ordering and rows `m..2m-1` are the reverse of the SAME pairs in the SAME order. When the pair cap
binds, `m = 200`, every block starts at an even offset, and the stride 2 selection picks pair
indices 0, 2, 4, ... out of BOTH halves. The subsample is therefore still exactly antisymmetric
and its intercept is still zero by construction. Measured on these corpora:

| corpus | both orderings | every second row (the original check) | one random ordering per pair |
|---|---|---|---|
| reddit | `[+5.6e-19, -3.3e-18]` | `[+7.9e-19, -2.0e-19]` se `[0.0042, 0.0047]` | `[-0.0074, -0.0061]` se `[0.0046, 0.0051]` |
| news | `[-2.3e-18, +9.4e-18]` | `[-3.2e-18, +2.4e-18]` se `[0.019, 0.021]` | small, se `[0.019, 0.021]` |

Zero to machine precision, not to sampling error. Note that on the FIRST run's corpus the same
code returned `-0.00037` (se 0.0022), a real number, because on `crosssite_authorship` most rooms
sit under the pair cap so `m` is often odd and the antisymmetry breaks. The check partly worked
there and fully degenerated here, which is why it went unnoticed.

**It cannot be rescued.** Taking one genuine ordering per pair with the direction drawn at random
gives a real number, but its expectation is zero under EVERY model, because the direction rule
carries no information about `dC`. An intercept on differenced data is zero as a matter of algebra.
No version of the check can fail, so no version of it is a test.

**Replacement, two controls with real failure modes.** The intercept was standing in for the claim
that differencing removes the room term exactly. That claim is now demonstrated on the actual data
rather than asserted, and the test's power is calibrated against a known injected effect.

*Control 1, location injection.* Inject a random room location shift into level character,
`C := C + u_room` with `u_room ~ N(0, s^2)` for `s` in 0.5, 1, 2. PASS if the within room `W` is
unchanged while a level fit moves.

| corpus | max change in within room W | max change in the naive level slope | verdict |
|---|---|---|---|
| reddit | 1.1e-16 | 0.033 | **PASS** |
| news | < 1e-16 | 0.033 | **PASS** |

*Control 2, rotation injection, the power calibration.* Inject a per room rotation,
`C := C + M_room P` with `M_room` entries drawn at a stated `tau`. PASS if the dispersion test then
beats the wild bootstrap null in at least three of four cells AND the blend weight rises.

| corpus | tau = 0.06 (the size actually claimed) | tau = 0.15 | verdict |
|---|---|---|---|
| reddit | **DETECTED**: dispersion p = 0.005 in all four cells, blend a rises 0.2 to 0.3 | DETECTED, a rises to 0.6 | **has power** |
| news | **NOT DETECTED**: p = 0.26, 0.01, 0.44, 0.15; blend a moves 0.4 to 0.3, the wrong way | DETECTED, p = 0.005 in all four, a rises to 0.6 | **underpowered at the claimed size** |

The simplified control reproduces the main script's numbers on the untouched reddit data (blend
optimum 0.2; dispersion excess 0.063, 0.055, 0.089, 0.073 against the main script's 0.062, 0.054,
0.089, 0.074), so the two are measuring the same quantity.

This is the decisive pair of rows in the whole run. Reddit CAN see a rotation of the claimed size
and reports none. News CANNOT see one and reports one.

---

## 6. Dispersion of the per room W against the wild bootstrap null

The null fixes each room's own design matrix, hence its own disposition spread and its own
reliability, and its own residual scale, flipping only residual signs with the coupling held at
the pooled `W`. A record permutation null is not used, because it would wrongly blame rooms with a
narrow spread of disposition, whose `W_r` is genuinely noisier.

**First run**, 478 rooms of 60 or more persons, 77,780 persons: all four cells p = 0.005, excess
0.078 to 0.162, and ALL FOUR survive the control that divides observed and null alike by per room
reliability (p 0.005 to 0.015).

**Reddit**, 387 rooms of 60 or more persons, 49,235 persons:

| cell | mean W | sd observed | sd wild null | p | excess | after reliability control |
|---|---|---|---|---|---|---|
| plas to matter/manner | -0.107 | 0.1197 | 0.1022 | 0.005 | 0.062 | p = 0.71, **dies** |
| plas to originality | +0.273 | 0.1192 | 0.1061 | 0.010 | 0.054 | p = 0.97, **dies** |
| stab to matter/manner | +0.220 | 0.1382 | 0.1059 | 0.005 | 0.089 | p = 0.005, survives |
| stab to originality | -0.093 | 0.1356 | 0.1140 | 0.005 | 0.074 | p = 0.005, survives |

**News**, 20 rooms of 60 or more persons, 2,981 persons:

| cell | mean W | sd observed | sd wild null | p | excess | after reliability control |
|---|---|---|---|---|---|---|
| plas to matter/manner | +0.072 | 0.1254 | 0.1102 | 0.194 | 0.060 | p = 0.055 |
| plas to originality | +0.279 | 0.1705 | 0.1167 | 0.010 | 0.124 | p = 0.124 |
| stab to matter/manner | +0.050 | 0.1035 | 0.1067 | 0.522 | 0.000 | p = 0.403 |
| stab to originality | -0.165 | 0.1283 | 0.1114 | 0.199 | 0.064 | p = 0.562 |

So reddit does carry genuine room to room variation in `W`, but only in the stability row, and it
does not grow with room size. News carries one raw cell at p = 0.010 and nothing after reliability
control, on twenty rooms.

The room's mean posting volume does not explain the per room `W`: the correlation of
`log(mean rows per person)` with each `W_r` entry is between -0.06 and +0.07 on reddit and between
-0.22 and +0.10 on news.

---

## 7. Reliability, disattenuation and person leakage

Regression dilution is measured, not assumed, from the within person room variance components.

| cell | lambda plasticity | lambda stability | disattenuated W |
|---|---|---|---|
| first run | 0.395 | 0.469 | `[[-0.089, +0.414], [+0.315, -0.062]]` |
| reddit 27B | 0.219 | 0.290 | `[[-0.524, +1.280], [+0.714, -0.200]]` |
| news | 0.329 | 0.320 | `[[+0.290, +0.745], [+0.296, -0.404]]` |
| reddit 7B | 0.162 | 0.149 | `[[-0.262, +1.173], [+1.149, -1.328]]` |

Attenuation is worse on both replications than on the baseline, because a reddit person room
record rests on a median of ONE post. The disattenuated anti diagonal is large everywhere, which is
the same conclusion the first run reached: attenuation makes a coupling look small, it does not
make a rotation look present.

**Person leakage, and how it was handled.** Every held out room drops every person who appears in
any training room, in all figures quoted above.

- reddit: 49,863 person room records over 47,512 persons, 1.05 rooms per person. Almost nobody in
  this slice writes in two subreddits, so the removal costs nothing and the held out pair mass
  stays at 100 per cent. The reddit replication is leak free by construction, which is a strength.
- news: 4,043 records over 1,367 journalists, 2.96 sections each. Heavy leakage. Removal costs
  78 per cent of the held out pair mass at K = 5 (22.3 per cent kept) and 31 per cent at K = 2
  (69.0 per cent kept). The clean K = 5 cell goes negative purely because 2,482 pairs remain; the
  clean K = 2 cell is the one quoted.
- first run: 58,826 of 59,084 persons wrote on two or more domains; the same removal kept 57.5 per
  cent at K = 2.

**Circularity check**, disposition read ONLY from the person's other rooms and character from this
room, so no shared text can produce the coupling:

| cell | plas to originality kept | stab to matter/manner kept | n records |
|---|---|---|---|
| first run | +0.114 of +0.163 = 70% | +0.118 of +0.146 = 81% | 163,582 in 1,503 rooms |
| reddit | +0.167 of +0.273 = 61% | -0.004 of +0.218 = **collapses** | 3,914 in 302 rooms |
| news | +0.155 of +0.273 = 57% | -0.020 of +0.075 = **collapses** | 4,031 in 24 rooms |

The plasticity to originality leg survives the circularity check on all three corpora at 57 to 70
per cent. The stability to matter against manner leg survives only on the first. On news that
verdict is well founded, since the check uses 4,031 of the 4,043 records; on reddit it rests on the
5 per cent of accounts that cross subreddits, so it is weak evidence there.

---

## 8. Verdict

**The rotation does NOT replicate.** It is absent where the test is demonstrably powered and
present only where the test is demonstrably underpowered.

- On reddit, 400 subreddit rooms and 47,512 persons, an injected rotation of exactly the size
  claimed (`tau = 0.06`) is detected in all four cells, so the design has power. On the real data
  the blend weight is FLAT at 0.2 from rooms of five to rooms of sixty, and the invariant curved
  `g` absorbs nearly the whole gain, leaving a room specific residue of +0.0017. Two of four
  dispersion cells do survive the reliability control, so some real room to room variation in `W`
  exists, but it does not grow with room size and it does not carry the first run's signature.
- On news, 24 editorial sections and 1,367 journalists, the blend weight does rise 0.1 to 0.5 in
  the first run's shape. The same injected rotation at `tau = 0.06` is NOT detected on this corpus,
  and the rise rests on 12 splits at the sixty person floor. It is not evidence.
- What DOES replicate is the anti diagonal coupling itself: plasticity to originality and stability
  to matter against manner are positive in all four fits, on corpora that share no owner, platform,
  user base or disposition prompt. Plasticity to originality also survives the circularity check
  everywhere.

**One sentence.** The anti diagonal coupling replicates on two independent corpora, but the
rotation does not: it is absent on the powered corpus and appears only on the corpus that cannot
resolve it, so Paper 4's invariance claim should be treated as damaged rather than refuted, and
settling it needs a corpus with roughly 300 or more rooms of 100 or more persons with SEVERAL rows
per person room record, which is the first run's own power calculation of 320 rooms at 162 persons
plus enough text per person to lift lambda above 0.4.

### What this does and does not do to the first run

It does not overturn it. The first run's corpus has 1,723 rooms and the largest sample here, its
dispersion survives the reliability control in all four cells where reddit's survives in two, and
its circularity check holds both legs where the replications hold one. What this run establishes
is that the rotation is NOT a general property of rooms: it does not appear when the room is a
community with its own membership, on a corpus where an effect of the claimed size would have been
seen. The honest reading is that the first run's "room" (a web domain) is doing something that a
subreddit is not, which is precisely the question the attribution run (topic, language and platform
controls) was launched to answer.

---

## 9. Reproduction

```bash
# on the internal host, three cells plus the room size sweep
OUTDIR=the internal corpus store/exp_diff_invariance_rep
TABLE=reddit_wide PERSONCOL=author ROOMCOL=subreddit DISPCOL=disp_d8_behav_27b CHARCOL=char \
  EXTRA_WHERE="AND author NOT IN ('[deleted]','AutoModerator')" DISPMIN=60 DISPCAPP=200 \
  HMINS="5,10,20,40,60,80" OUT="$OUTDIR/panel_reddit_sweep.json" \
  python3 truthometer/scripts/cc_state_diff_invariance_rep.py

TABLE=news_topic PERSONCOL=author ROOMCOL=topic DISPCOL=disp_d8 CHARCOL=char_dweb \
  DISPMIN=60 DISPCAPP=200 HMINS="5,10,20,40,60,80" OUT="$OUTDIR/panel_news_sweep.json" \
  python3 truthometer/scripts/cc_state_diff_invariance_rep.py

# the replacement intercept controls
TABLE=reddit_wide PERSONCOL=author ROOMCOL=subreddit DISPCOL=disp_d8_behav_27b CHARCOL=char \
  EXTRA_WHERE="AND author NOT IN ('[deleted]','AutoModerator')" PANELMIN=60 \
  OUT="$OUTDIR/icheck_reddit.json" \
  python3 truthometer/scripts/cc_state_diff_intercept_check.py
```

Artefacts in this directory: `panel_*_sweep.json` (the room size sweeps), `panel_*_large.json`
(the single threshold cells), `panel_reddit_small_7b.json` (the 7B disposition lineage cell),
`icheck_*.json` and `intercept_controls.log` (the replacement controls), and the run logs
`sweep.log`, `reddit_all.log`, `news_large.log`.

Aggregate output only. No keys, no names, no per person figures.

# RESONANCE = fit between content character (DYNAMICS-WEB) and audience disposition (DYNAMICS-8)

PUBLIC track. Analysis only. No fresh scoring: reuses the held DYNAMICS-WEB character scores and DYNAMICS-8
disposition scores already on `cc_v3.reddit_wide` (DL580).

## The question

Does the fit between a piece of content and the audience it lands in predict engagement better than the
content's own character (DW) or the audience's own disposition (D8) taken separately? If it does, then
**resonance** is a real and usable quantity: a single scalar for the coupling between a person and a piece
of content.

## Definition

For content `i` with DW character vector `x_i` (eight axes: rigour, depth, originality, candour, affect,
commercial_drive, stance, register) landing in community `c`:

```
RESONANCE(i, c) = x_i . g_c
```

where `g_c` is the community's **rewarded character direction**, the ridge slope of the community's own
vote rank on the eight DW axes (the reward gradient over DW). A piece of content resonates when its
character points the way its audience rewards.

Two forms of `g_c`, both built so a comment's resonance never sees that comment's own vote:

- **`resonance_emp`** (empirical): `g_c` learned from a disjoint half A of the community's comments, then
  resonance measured on the other half B. Community specific, but it references only the room's own revealed
  votes, not its members' disposition.
- **`resonance_d8`** (the true DW by D8 coupling): a map from disposition to gradient is trained on the
  OTHER communities, leaving each community out in turn, then that community's rewarded direction is
  predicted from its D8 disposition alone (`g_hat_c`), never from its votes. `resonance_d8 = x_i . g_hat_c`.
  This is the honest, generalisable form: a room's taste guessed from who is in it.

## Data

- 77,078 comments carrying both a DW character score and a D8 disposition score (`disp_d8_behav_27b`),
  across 400 communities. 398 communities pass the floor of 150 comments.
- Outcome: vote rank inside the community (rank of `score` within `c`, centred). This controls for the
  community (it removes the huge between room differences in scale) and asks the sharp question: within a
  room, does resonant content win the votes?
- Evaluation on the 38,516 comments in the disjoint half B. Out of sample R2 from five fold cross
  validation. `x` standardised on a single global scale so an axis unit means the same everywhere.

## Result

Within community vote rank `z`, out of sample R2 on the evaluation half:

| model | what it asks | R2 | r |
|---|---|---:|---:|
| DW alone (global eight axis) | is there a universally rewarded character | +0.0083 | +0.090 |
| D8 alone (community disposition) | does audience type rank content in its own room | -0.0004 | ~0 |
| `resonance_emp` alone | content fit to the room's own revealed taste | +0.0044 | +0.066 |
| `resonance_d8` alone | content fit to taste guessed from disposition | +0.0077 | +0.088 |
| DW + `resonance_emp` | fit ON TOP of universal character | +0.0103 | incremental **+0.0017** |
| DW + `resonance_d8` | fit ON TOP of universal character | +0.0088 | incremental **+0.0005** |

Within a room, high resonance content wins more votes than low resonance content in 68% of rooms for
`resonance_emp` (mean rank gap +0.15 SD, top vs bottom tercile) and 78% for `resonance_d8` (gap +0.20 SD).

At first read `resonance_d8` looks like the winner. It is not. Three checks show why.

1. **The disposition to gradient map is null.** Predicting a room's rewarded direction from its D8
   disposition, leaving that room out, recovers nothing: pooled r = **-0.003** over the eight axes. The
   predicted gradients `g_hat_c` barely vary by room. Their cosine with the single average gradient across
   all rooms is **+0.79**, and `resonance_d8` correlates **+0.81** with `x . average_gradient`. So
   `resonance_d8` is not a person to content coupling. It is the one universal good content direction
   re expressed as a scalar. It scores well alone only because it repackages the universal DW signal, which
   is why it adds almost nothing over the DW main effects (+0.0005).

2. **Room shuffle separates the two forms.** Reassign each room's predicted gradient to the WRONG room and
   recompute. `resonance_d8` survives (r on `z` goes +0.087 to +0.074, essentially unchanged): it is not
   room specific. `resonance_emp` collapses (r goes +0.065 to +0.023): it genuinely carries the room's own
   taste.

3. **The one honest increment is `resonance_emp`, and it is tiny.** Its lift over the universal DW model is
   +0.0017 R2, real against a room shuffle null (+/- 0.00006, p = 0.005) but about a fifth of a percent of
   the within room variance. And it is partly mechanical, the caveat the brief called out: matching a room's
   own revealed votes is close to matching the room's norm.

## Verdict

**DW by D8 resonance is not yet a real, usable quantity as a person to content coupling.** Two honest
findings and one clean negative:

- There is a weak universal reward for character (DW alone, R2 = 0.008, r = 0.09). Content quality, as the
  eight DW axes measure it, is a real but small signal in noisy public votes.
- A room's fit to its OWN revealed taste (`resonance_emp`) adds a small, statistically real increment over
  universal character (+0.0017 R2, p = 0.005) and out engages the room's low fit content in 68% of rooms.
  This is genuine community specificity, but it needs the room's own vote history and is partly mechanical.
- The form that matters for the claim, taste predicted from the audience's disposition and never from its
  votes, **fails**. The disposition to gradient map is null (r = -0.003), so `resonance_d8` is only the
  universal quality direction wearing a coupling's clothes, and it adds ~0 over DW main effects. You cannot
  yet predict what a room will reward from who is in it well enough for resonance to beat content character
  on its own.

This sits exactly where the rest of the series left the reward channel: the reward gradient is endogenous to
the room, not recoverable from disposition or from the community graph. The clean, strong coupling in this
data is the opposite direction, disposition to PRODUCED character (audience persona predicts what its members
write, r = 0.74 at N = 400, a separate result), not disposition to what the room REWARDS. Resonance as
defined here rides the reward channel, and the reward channel does not carry the person to content coupling.

Honest bound. This is ecological and correlational: audiences self select into rooms, votes are noisy, and
the empirical form of resonance is partly the mechanical fact that content matching a room's norm scores
well. The negative on `resonance_d8` is the informative part and it is robust: it holds under a leave one
community out map, a room shuffle null, and control for the universal DW main effects.

## Reproduce

- `truthometer/scripts/resonance_dwxd8.py` — the four models and the within room out engagement contrast.
- `truthometer/scripts/resonance_confirm.py` — the collapse, room shuffle, and increment permutation checks.
- Both read `cc_v3.reddit_wide` on DL580 (`char`, `disp_d8_behav_27b`, `score`). Run on DL580.

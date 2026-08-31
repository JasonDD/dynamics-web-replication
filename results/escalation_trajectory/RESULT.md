# Escalation trajectory: does manipulation escalate within a conversation?

DYNAMICS-WEB series, PUBLIC track. Question: a manipulative approach is theorised to earn
trust first (high candour, low affect) then pivot to the exploit (candour falls, affect
rises). If that pivot has a within conversation signature, a detector could flag the exact
turn a benign chat turns predatory. This is the single most valuable primitive for a dating
app or any platform shielding a vulnerable user.

## Verdict

**No true manipulation conversation corpus is held**, so the literal test (does a benign chat
turn predatory, and can we catch the turn) cannot be run on real data. Stated plainly, as the
feasibility gate demands.

**The CMV escalation proxy runs and gives a clear, significant result.** Ordering each arguer's
turns within a thread and comparing threads the arguer WON (earned a delta) against threads they
LOST, the trajectory shape is real and discriminative, but it is **not the predicted predatory
signature**. Winning persuasion is loaded with matter at the front and then softens toward
manner across the turns (rigour, depth and stance fall sharply; affect rises weakly), while
**candour stays flat and high throughout**. Losing persuasion has the same directions at roughly
a third to a fifth of the slope. The one axis the predatory theory hangs on, candour falling as
the exploit begins, **does not move**, in winners or losers.

So the proxy delivers the *benign persuasion baseline shape* the real detector would be measured
against, and shows that the discriminating question (does candour collapse at the pivot?) is
exactly the one CMV cannot answer, because CMV winning is sincere mind change, not predation.

## Feasibility gate: what conversational data we actually hold

The test needs threaded data with turn order where a manipulative party engages a target across
multiple turns toward an exploit, with a ground truth outcome. Audit of the NAS corpora and
fabric:

| Corpus | Threaded / turns? | Manipulation ground truth? | Usable for this test? |
|---|---|---|---|
| `cmv_winning_args` (ChangeMyView, Tan 2016) | YES, 293,297 utterances, reply chains + timestamps, 3,051 threads | Persuasion outcome (delta), **sincere** not predatory | YES, as a proxy, used here |
| `opspam_deceptive` (deceptive hotel reviews) | NO, single reviews | YES (deceptive vs truthful) | No, no turns |
| `phishing_email` | NO, single messages | YES (phishing) | No, no turns |
| `dark_patterns` (Mathur) | NO, single UI strings | YES (dark pattern vs not) | No, no turns |
| `ira_troll` (IRA state trolls) | NO, single posts | YES (state manipulation) | No, no conversation |
| `human_persuasion/persuasionforgood` | Dir holds only a classifier sub repo; no dialogue data present | Would be donation dialogues | No, data not on disk |
| `iq2`, `ddo` (debates) | YES, multi speaker turns + pre/post vote outcome | Debate persuasion, not predation | Proxy candidate, not scored here |

Conclusion: we hold rich **deception** data (single shot) and rich **persuasion dialogue** data
(CMV, debates), but **zero multi turn predatory transcripts** (grooming, romance scam, social
engineering) with the predator labelled and an exploit outcome. CMV is the cleanest proxy and is
already scored on the same 8 axis scale used across the series, so it is the partial we run.

## Method (CMV escalation proxy)

- Reconstruct every thread from `utterances.jsonl` via the `reply-to` field and `timestamp`.
- For each non OP arguer with 3 to 8 turns in a thread, order their turns by time. Label the
  chain **WON** if that arguer earned a delta (`meta.success == 1`) anywhere in the thread, else
  **LOST**. 23,288 arguer chains have 3+ turns.
- Balanced sample: 900 WON + 900 LOST (stable hash order). Score each turn's 8 axis character
  with the identical rubric and free 7B teacher used across the series (`qwen2.5-7b-atlas` on
  :8301), self queued at 4 workers behind the running jobs so it did not starve them. Existing
  root reply scores reused where ids overlapped; 6,045 new turns scored.
- Usable chains (every turn scored): **1,387 (705 WON, 682 LOST)**.
- Per chain, ordinary least squares slope of each axis and of PC1 (matter vs manner, same SVD
  recipe as `manip_analyse.py`) against turn index. Mean slope per class with bootstrap 95%
  confidence intervals (5,000 draws over chains); permutation p (20,000) on the WON minus LOST
  slope difference.

## Result: trajectory slopes (per turn change)

| axis | WON slope [95% CI] | LOST slope [95% CI] | perm p (diff) |
|---|---|---|---|
| rigour | -0.0346 [-0.0412, -0.0280] | -0.0069 [-0.0144, +0.0004] | 0.0000 |
| depth | -0.0255 [-0.0304, -0.0206] | -0.0082 [-0.0132, -0.0033] | 0.0000 |
| originality | -0.0156 [-0.0212, -0.0100] | -0.0058 [-0.0123, +0.0004] | 0.0220 |
| candour | -0.0017 [-0.0037, +0.0004] | -0.0003 [-0.0029, +0.0023] | 0.3983 |
| affect | +0.0123 [+0.0066, +0.0182] | +0.0018 [-0.0041, +0.0080] | 0.0143 |
| commercial_drive | -0.0097 [-0.0136, -0.0059] | -0.0026 [-0.0064, +0.0012] | 0.0130 |
| stance | -0.0390 [-0.0465, -0.0317] | -0.0115 [-0.0199, -0.0031] | 0.0000 |
| register | +0.0059 [-0.0003, +0.0120] | +0.0073 [-0.0005, +0.0154] | 0.7912 |
| **PC1 matter/manner** | **-0.6593 [-0.7655, -0.5510]** | **-0.1964 [-0.3045, -0.0853]** | **0.0000** |

Endpoint means (first turn to last turn):

| axis | WON t0 | WON tN | LOST t0 | LOST tN |
|---|---|---|---|---|
| rigour | 0.672 | 0.563 | 0.546 | 0.521 |
| depth | 0.644 | 0.558 | 0.557 | 0.530 |
| stance | 0.665 | 0.544 | 0.617 | 0.567 |
| affect | 0.498 | 0.538 | 0.538 | 0.543 |
| candour | 0.858 | 0.852 | 0.847 | 0.847 |

## Reading the shape

1. **Winning persuasion moves from matter to manner across the conversation.** PC1 falls at
   -0.66 per turn in winners, more than three times the -0.20 in losers (p < 0.0001). Rigour,
   depth and stance all fall two to five times faster in winners. The winning arguer opens
   strong and sourced (rigour 0.67, stance 0.67) and softens turn by turn.

2. **Affect rises, weakly, and only in winners** (+0.012 per turn, p = 0.014). So half of the
   predicted predatory signature, affect up, is present, but small.

3. **Candour does not move.** Flat in both classes (p = 0.40), held high near 0.85 throughout.
   The other half of the predatory theory, candour collapsing as the exploit begins, is
   **absent**. In sincere persuasion the arguer never stops being transparent.

4. **The gradient discriminates; a single pivot does not.** The largest single turn affect jump
   sits about two thirds of the way through the chain in **both** WON and LOST, at almost equal
   magnitude (0.216 vs 0.206). A one turn pivot detector on affect alone would not separate
   winning from losing. The continuous slope (matter falling plus affect rising) is what carries
   the signal, and it is three to five times steeper in winners.

Bottom line for the product thesis: within a conversation the character trajectory is real,
significant and measurable on the 8 axis instrument, the instrument can track a voice moving
across turns. But the specific predatory pattern the detector would sell on (trust first, then
candour drops as affect spikes) is **not what benign persuasion looks like**, which is the
encouraging half: the benign baseline holds candour constant. Whether predation actually breaks
that candour line is the open question, and it needs the data below.

## The real test: exact missing data

To answer the literal question (flag the turn a benign chat turns predatory) we need multi turn
transcripts where:

- **turn order and speaker identity are preserved** (who said what, in sequence);
- **the predatory party is labelled**, and ideally the target's vulnerability is known;
- **a ground truth exploit outcome exists** (money sent, credential handed over, meeting
  arranged, disclosure obtained) with, where possible, the **turn at which the ask lands** so a
  pivot detector can be scored against a real changepoint.

Candidate sources (none currently held at usable n): labelled romance scam chat logs
(for example the scam baiting archives), social engineering red team transcripts, grooming case
transcripts released in research settings (for example the PAN / PJ datasets), and consumer
fraud call transcripts. Each carries governance weight and would sit on the INTERNAL track, not
this PUBLIC one.

Design once such data exists: identical pipeline, order the predator's turns, score the 8 axes
per turn, fit the candour and affect trajectory, and test two things the CMV proxy has now
calibrated the benign baseline for: (a) does candour **fall** across a predatory chain where it
stays flat in a benign one, and (b) is there a **discriminative changepoint** (unlike CMV, where
the affect pivot was present but not discriminative). The CMV result gives the null shape to beat.

## Untapped proxies short of true data

`iq2` (Intelligence Squared, multi speaker debate turns with pre and post audience vote) and
`ddo` (debate.org rounds) are both held and offer a second and third persuasion outcome with
turn structure. Neither is predatory, so they extend the benign baseline rather than test
predation. Note and park unless a cross proxy replication of the matter to manner gradient is
wanted.

## Artefacts and reproduction

- Scorer: `truthometer/scripts/cc_cmv_escalation.py` (`prep` sizes, `score` runs).
- Analysis: `truthometer/scripts/cc_cmv_escalation_analyse.py`.
- Per turn scores: `/mnt/nas/kronaxis/corpora/cmv_winning_args/cmv_escalation_scores.jsonl` (NAS).
- Summary JSON: `docs/papers/dynamics_web_series/results/escalation_trajectory/cmv_escalation_summary.json`.
- Reproduce: `NCHAINS=900 python3 truthometer/scripts/cc_cmv_escalation_analyse.py` on DL580
  (needs the DB for the PC1 reference and the two score files on the NAS).

Data: ChangeMyView Winning Arguments corpus, Tan et al. 2016, Cornell ConvoKit (CC attributed,
public). Scored on the free internal 7B teacher; no third party model, no PII.

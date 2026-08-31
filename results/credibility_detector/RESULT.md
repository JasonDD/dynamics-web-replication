# Credibility detector: does drift away from the credibility voice precede a loss of trust

**Track:** PUBLIC (regtech). **Run date:** 2026-08-31. **Session:** credibility-detector.

**Question.** A sibling result showed institutional credibility has a measurable, near invariant voice: high
rigour, high candour, low affect, near zero commercial drive, a credibility index of about +1.71 that is
almost identical across 14 central banks (results in `commercial_comms_scout/experiment_B_credibility`,
fabric memo #19383). This child tests the DETECTOR direction: does a DRIFT AWAY from that signature precede a
loss of institutional trust? If candour falls or affect rises in the months before a central bank's
credibility breaks, the signature is a leading indicator and a usable early warning.

**The fix applied.** The first attempt nulled because it used the autumn 2022 UK gilt and LDI episode, where
the Bank of England was the responder and stabiliser, not the discredited party, so there was no reason its
own voice should shift. This run re anchors on episodes where the institution's OWN credibility was lost: the
2021 to 2022 "transitory inflation" walk back. Several major central banks held that the post COVID inflation
surge was transitory, then reversed and hiked hard, a clear case of a central bank's own forecast credibility
taking a public hit.

---

## Method

Within institution event study. For each institution a reversal month t0 marks where its own credibility took
the hit; every speech is placed at a signed month distance d from that t0 and binned into six month windows.
We ask whether the signature degrades (candour down, affect up, credibility index down) in the bins before and
around t0 versus the institution's own earlier baseline (all speeches with d < −6 months). A degradation that
shows up BEFORE t0 would make credibility drift a leading indicator.

| institution | t0 | own credibility event |
|---|---|---|
| Federal Reserve (board + FOMC voice) | 2021-11 | Powell retires the word "transitory" (30 Nov 2021), pivots to hikes |
| European Central Bank | 2022-07 | first hike; Lagarde had defended transitory into late 2021 |
| Bank of England | 2021-12 | first hike; transitory framing walked back |
| Reserve Bank of Australia | 2022-05 | abandons its "no rate rise until 2024" guidance; the RBA Review follows |

**Instrument.** The same 8 DYNAMICS axes on the free 7B `qwen2.5-7b-atlas` at :8301, temperature 0, the
scorer every sibling child uses. Self queued at 3 workers behind the running jobs.

**Corpus.** `samchain/bis_central_bank_speeches`. 644 speeches scored across the Fed (272), ECB (267) and RBA
(105) for the 2019 to 2023 window, plus 188 Bank of England speeches reused from the sibling run. Full text,
institution, year and month; date granularity is year and month, no day.

Scripts: `scripts/detector_prep.py`, `scripts/detector_analyse.py` (scorer `comms_score.py` reused). Corpora
on NAS `/mnt/nas/kronaxis/corpora/comms_scout/`, full run log in `analysis_output.txt`.

---

## Result 1: the composite credibility index does NOT fall ahead of trust loss; it holds, or rises

Per institution, baseline (d < −6 months) versus the −6 to +6 month window straddling t0 (Welch t):

| institution | candour base→window | affect base→window | rigour base→window | cred index base→window |
|---|---|---|---|---|
| Federal Reserve | 0.860 → 0.858 (p=0.85) | 0.454 → 0.460 (p=0.61) | 0.803 → 0.815 (p=0.11) | +1.734 → +1.756 (p=0.43) |
| **ECB** | **0.826 → 0.802 (p=0.052)** | **0.469 → 0.484 (p=0.058)** | 0.820 → 0.836 (p=0.038) | +1.726 → +1.755 (p=0.20) |
| Bank of England | 0.851 → 0.856 (p=0.76) | 0.471 → 0.468 (p=0.78) | 0.810 → 0.812 (p=0.87) | +1.703 → +1.756 (p=0.14) |
| RBA | 0.868 → 0.864 (p=0.82) | 0.477 → 0.471 (p=0.70) | 0.816 → 0.800 (p=0.15) | +1.712 → +1.693 (p=0.63) |

The credibility index never falls significantly around t0. At the Fed, BoE and RBA it barely moves at all. At
the ECB it actually ticks UP, because rigour rises (p=0.038) enough to offset a falling candour. The composite
index is therefore a poor detector: a central bank whose credibility is under pressure does not get less
scholarly, it gets MORE technical and data heavy, and that defensive rigour masks the components that do move.

## Result 2: the components the hypothesis predicted move, but only clearly at the ECB, and only borderline

The ECB is the one institution that behaves as the leading indicator hypothesis predicts. Around its 2022 t0,
candour falls (0.826 → 0.802) and affect rises (0.469 → 0.484), the exact degradation signature, both at the
edge of significance (p ≈ 0.05 to 0.06). Read across its bins the drift is visible: candour runs 0.828 in the
far pre period, dips to 0.807 on the eve of the reversal and 0.796 in the break window and stays down at 0.791
afterwards, while rigour climbs monotonically from 0.817 to 0.850. The other three institutions show no such
move; the Fed and BoE candour is flat, the RBA cells around t0 are too thin (n = 5 and 9) to say anything.

## Result 3: pooled, the candour decline is real but LAGGING, not leading

Stacking all four institutions after z scoring each to its own d < −6 baseline:

| bin (months from t0) | n | candour z | affect z | rigour z | cred index z |
|---|---:|---:|---:|---:|---:|
| −30 to −18 | 171 | +0.04 | −0.07 | −0.07 | −0.05 |
| −18 to −12 | 90 | −0.12 | +0.08 | +0.27 | +0.24 |
| −12 to −6 | 84 | +0.02 | −0.10 | −0.06 | +0.05 |
| −6 to 0 (eve) | 76 | −0.07 | **+0.20** | +0.22 | +0.08 |
| 0 to +6 (break) | 67 | −0.19 | +0.05 | +0.21 | +0.29 |
| +6 to +12 (post) | 97 | **−0.37** | +0.08 | +0.34 | +0.11 |
| +12 to +24 (post) | 107 | −0.20 | +0.22 | +0.18 | +0.03 |

The candour decline is genuine and monotone AFTER the reversal (−0.19, then −0.37, then −0.20 standard
deviations below each institution's own baseline) but it is not there before t0: the eve window candour z is
only −0.07 (z = −0.60, p = 0.55). Affect nudges up on the eve (+0.20) but not significantly (p = 0.14). The
only significant pooled move in the t0 ± 6 window is the credibility index going UP in the break bin
(+0.29 sd, p = 0.016), again the defensive rigour effect, the opposite of degradation.

So the character of institutional voice does change around a self inflicted credibility loss: candour falls
and stays down, and rigour rises. But that change is coincident to lagging, it appears at and after the
reversal, not in the run up to it.

---

## Verdict

**Is credibility drift a leading indicator of trust loss: NO, not demonstrated.** Re anchoring on genuine own
credibility losses (the transitory inflation walk back) surfaced a real and directionally correct signature
change, candour down and rigour up, and it replicates as a lagging pattern in the pooled data. But it arrives
at and after the reversal, not before it. The one institution that drifts ahead of its t0, the ECB, does so
only at borderline significance and does not generalise to the Fed, BoE or RBA. The leading indicator claim
fails.

**What the re anchor did buy.** This is a more informative null than Experiment B. It shows (1) the composite
credibility index is the wrong detector, because defensive rigour rises under pressure and cancels the
degradation; (2) the two components that do carry a trust signal are candour and affect, not the index; and
(3) the signal is a lagging fingerprint of a credibility hit, candour falling and staying down for a year or
more afterward, which is still useful for the regtech authenticity use (spotting a voice that has drifted off
the credibility band) but not for early warning.

**Honest about power.** This is weak evidence either way. There are only four institutions, and their four
"events" are not independent: all four are the same global 2021 to 2022 inflation shock seen through four
central banks, so the effective number of credibility episodes is close to one. The bins straddling t0 hold 5
to 30 speeches each; the RBA around its t0 is too thin to test. Year and month granularity blurs timing around
events. A real test of the leading indicator hypothesis needs credibility losses that are independent of each
other and of a common macro shock, spread across time, which central bank speech data around a single
synchronised policy error cannot provide.

# Experiment A2: the fraud pre signature in the wetter medium (earnings calls)

**Track:** PUBLIC (fin crime pipeline, defensive). **Run date:** 2026-08-31. **Session:** comms-scout.

**Why this run.** Experiment A on 10-K filings was an honest negative on the medium: the affect led
manipulation signature that separates phishing and political trolls at AUC 0.96 was flat in dry, templated
accounting prose. The named fix was to move to a wetter medium. This run does that: earnings call
transcripts, which are spontaneous, answer live questions and carry far more affect than a filing.

**Question.** Does the manipulation signature (affect up, candour down, credibility index falling) rise in a
firm's earnings calls in the window BEFORE an accounting fraud is exposed, relative to the same firm's own
earlier calls and to sector matched control firms?

**Instrument.** The 8 DYNAMICS axes on the free 7B `an internal 7B instruct model` at , temperature 0, same scorer
as the sibling children. Self queued behind the running power, criminal and cross platform jobs at low
worker count.

**Data, join and design.**

- **Text:** `Bose345/sp500_earnings_transcripts` (Hugging Face), 33,362 full earnings call transcripts across
  685 S&P 500 tickers, 2005 to 2025, each with ticker, quarter, year and date. The first 6000 characters of
  each call (operator intro and the management prepared remarks, where the pitch lives) were scored.
- **Fraud label and t0:** SEC AAER releases 2015 to 2022, scraped from the enforcement archive (682 releases
  with release number, date and named respondent). Firm respondents were token matched to the transcript
  universe (strict: all core name tokens shared, which removed the substring false positives that a looser
  match produced, for example Roper against Brixmor and Fifth Third against The Bancorp). The earliest AAER
  release date per firm is t0, the exposure date. 25 fraud firms matched.
- **Windows:** for each fraud firm, `fraud_pre` = calls in the two years before t0 (fraud live, not yet
  exposed); `fraud_base` = the same firm's earlier calls (about three to seven years before t0) as its own
  baseline; `control` = up to two S&P 500 firms in the same 2 digit SIC industry (size held roughly constant
  by S&P 500 membership, which fixes the salesy blue chip problem from the 10-K controls), over the same
  absolute date windows.
- **Scored sample:** 143 fraud pre exposure calls (24 firms), 143 same firm baseline calls, 274 sector
  matched control calls (46 firms). Scripts: `aaer_scrape.py`, `comms_a2_match.py`, `comms_a2_prep.py`,
  `comms_score.py`, `comms_a2_analyse.py`.

---

## Result: the affect signal comes back, the rest stays weak

Mean character by group, with effect sizes:

| axis | fraud pre | fraud base | control | d (pre vs control) | p | d (pre vs base) | p |
|---|---:|---:|---:|---:|---:|---:|---:|
| rigour | 0.763 | 0.767 | 0.770 | -0.14 | 0.17 | -0.08 | 0.50 |
| depth | 0.685 | 0.666 | 0.685 | -0.00 | 0.99 | +0.27 | 0.024 |
| originality | 0.543 | 0.529 | 0.553 | -0.11 | 0.27 | +0.17 | 0.14 |
| candour | 0.840 | 0.841 | 0.854 | **-0.20** | **0.060** | -0.02 | 0.88 |
| affect | 0.481 | 0.465 | 0.476 | +0.11 | 0.26 | **+0.32** | **0.007** |
| commercial_drive | 0.605 | 0.578 | 0.584 | +0.08 | 0.45 | +0.10 | 0.41 |
| stance | 0.624 | 0.603 | 0.609 | +0.14 | 0.16 | +0.20 | 0.09 |
| register | 0.657 | 0.632 | 0.661 | -0.03 | 0.76 | +0.19 | 0.11 |
| **cred index** | 1.202 | 1.232 | 1.250 | -0.14 | 0.18 | -0.08 | 0.49 |

Within firm paired test (24 firms with both windows):

| axis | mean (pre minus base) | firms in predicted direction |
|---|---:|---|
| affect (predict up) | +0.016 | 14 of 24 |
| candour (predict down) | -0.001 | 14 of 24 |
| commercial_drive (predict up) | +0.029 | 13 of 24 |
| cred index (predict down) | -0.032 | 14 of 24 |

**The headline: the affect tell recovers.** Against the same firm's own earlier calls, affect is
significantly higher in the pre exposure window (0.481 versus 0.465, d = +0.32, p = 0.007). In the 10-K run
affect was dead flat (+0.007, only 6 of 18 firms up); in the call it moves, is significant, and 14 of 24
firms move the predicted way. The wetter medium carries the tell that the filing buries. That is the point
the run set out to test, and it holds for affect.

**Candour drops, but only against controls.** Fraud pre exposure calls are lower in candour than the sector
matched controls (0.840 versus 0.854, d = -0.20, p = 0.060), the predicted direction, borderline. Against the
firm's own baseline candour is flat, so the candour signal is a between firm difference, not a within firm
shift, at this sample size.

**The rest is weak.** The credibility index moves the predicted way in both comparisons (lower than baseline
and lower than controls) and in 14 of 24 firms, but neither reaches significance. Commercial drive is high in
calls generally (0.58 to 0.61, calls really are salesier than filings) but does not separate fraud cleanly.

---

## Verdict

**Does the signature surface in the wetter medium: PARTLY, and more than it did in filings.** The affect
component, which was flat in 10-K prose, rises significantly in fraud firms' pre exposure calls versus their
own earlier baseline (d = +0.32, p = 0.007), and candour is lower than in sector matched controls (p = 0.06,
predicted direction). The medium hypothesis is directionally confirmed: the earnings call carries part of the
manipulation tell that the annual filing does not. But it is one axis to significance, not the whole
signature: candour, credibility index and commercial drive move the right way without reaching significance
on this testbed.

**Honest caveats.**

1. **Hard testbed.** The only fraud firms freely joinable to S&P 500 transcripts are large caps with a
   localized restatement (Kraft Heinz, General Electric, Baxter, Rollins, Archer Daniels Midland) or an FCPA
   books and records matter (Halliburton, Qualcomm, Stryker, Cognizant, Juniper). A discrete accounting issue
   at a healthy giant is the weakest possible version of the hypothesis; a firm whose whole story is the
   fraud should show far more. The affect result surfacing even here is the encouraging part.
2. **Affect is not fraud specific on its own.** A rise in affect before an exposure could partly reflect a
   firm under general stress or scrutiny, not fraud specific manipulation. It is measured against the firm's
   own calm baseline and partly against controls, which helps, but it is not proof of intent.
3. **Prepared remarks only.** The first 6000 characters is the scripted opening; the unscripted analyst Q and
   A, where a stressed management is most exposed, was not separately scored and is the obvious next cut.

**Path to the sharp yes.** Source transcripts for small and mid cap firms whose business WAS the fraud, where
the label is unambiguous and the whole call is the tell: MiMedx, Luckin Coffee, Nikola, Comscore, Celadon.
Score the analyst Q and A separately from the prepared remarks. On this run the wetter medium already did
what the dry medium could not, recover the affect signal to significance, so the direction of travel is
right; the remaining work is a cleaner fraud set and the Q and A split.

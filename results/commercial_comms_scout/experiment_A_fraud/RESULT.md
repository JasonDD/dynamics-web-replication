# Experiment A: the manipulation signature before a fraud breaks

**Track:** PUBLIC (fin crime pipeline, defensive). **Run date:** 2026-08-31. **Session:** comms-scout.

**Question.** Does a company's communication character carry the manipulation signature (affect up, candour
down) in the filings issued while a fraud is live, BEFORE the fraud is exposed, relative to the same firm's
clean years and to control firms?

**Instrument.** The 8 DYNAMICS axes on the free 7B `qwen2.5-7b-atlas` at :8301, temperature 0, same scorer
as the sibling children. Self queued behind the running jobs at low worker count.

**Data and join.**

- **Text:** SEC EDGAR 10-K filings, fetched from the submissions and archive APIs, primary document narrative
  (Management discussion and analysis and risk factors), capped at 6000 characters per filing.
- **Fraud label:** Bao, Ke, Li, Yu and Zhang (2020), `JarFraud/FraudDetection`. The per firm per year
  `misstate` flag marks fraud active fiscal years; `AAER_firm_year.csv` supplies the CIK that joins the label
  to EDGAR text. 210 fraud firms had a CIK and at least one misstatement fiscal year in the EDGAR full text
  era (2001 onward); the 45 with the most usable filings were taken.
- **Design.** For each fraud firm, its 10-K filings for misstatement fiscal years are the fraud active,
  pre exposure filings; its 10-K filings for clean fiscal years are the same firm's own baseline. A set of 12
  large cap firms never in the Bao AAER set supplies an external control. This within firm design needs no
  paid gvkey to CIK crosswalk.
- **t0 note.** The event anchor here is the misstatement fiscal year (the fraud is live but not yet charged),
  not the exact AAER release date. That is the pragmatic feasibility anchor; the AAER release date refinement
  is discussed below.

**Scored sample.** 90 fraud active filings, 31 same firm clean filings (22 distinct fraud firms), 44 control
filings (12 firms). Scripts: `comms_a_prep.py`, `comms_a_controls.py`, `comms_score.py`, `comms_a_analyse.py`.

---

## Result: the signal is weak and not significant in filing prose

Mean character by group:

| axis | fraud active | same firm clean | control | Cohen d (fraud vs clean) | p |
|---|---:|---:|---:|---:|---:|
| rigour | 0.816 | 0.819 | 0.807 | -0.07 | 0.68 |
| depth | 0.709 | 0.710 | 0.689 | -0.01 | 0.95 |
| originality | 0.566 | 0.568 | 0.518 | -0.03 | 0.88 |
| candour | 0.824 | 0.839 | 0.827 | -0.15 | 0.48 |
| affect | 0.478 | 0.474 | 0.448 | +0.08 | 0.73 |
| commercial_drive | 0.499 | 0.435 | 0.591 | +0.26 | 0.18 |
| stance | 0.541 | 0.542 | 0.525 | -0.01 | 0.96 |
| register | 0.690 | 0.706 | 0.682 | -0.17 | 0.33 |
| **cred index** | **1.372** | **1.458** | 1.284 | **-0.33** | **0.10** |

Within firm paired test (18 firms that have both fraud and clean filings), mean of (fraud minus clean):

| axis | mean diff | firms with predicted direction |
|---|---:|---|
| affect (predict up) | +0.007 | 6 of 18 up |
| candour (predict down) | -0.005 | 11 of 18 down |
| commercial_drive (predict up) | +0.061 | 12 of 18 up |
| cred index (predict down) | -0.077 | 13 of 18 down |

**What holds, weakly.** The credibility index is lower in fraud active years than in the same firms' clean
years (1.372 versus 1.458, d = -0.33, p = 0.10), and 13 of 18 firms move that way. Commercial drive is higher
in fraud years (12 of 18 firms, group gap +0.06). Both are the predicted direction: firms committing fraud
write filings that are a touch less transparent and a touch more of a sell. Candour is directionally down in
11 of 18 firms.

**What does not hold.** None of it reaches significance at this sample size, and the two axes the signature
leans on hardest elsewhere are flat: affect barely moves (+0.007, only 6 of 18 firms up) and candour as a
group mean is essentially unchanged. The loud affect driven manipulation signature that separates phishing
and political trolls at AUC 0.96 is not visible in 10-K prose.

**Why (the honest caveats).**

1. **10-K prose is dry and templated.** Affect sits in a narrow 0.45 to 0.48 band across all three groups.
   Risk factors and MD&A are lawyer reviewed boilerplate, the worst possible medium for an affect led tell.
2. **The control set was a poor honest baseline.** Large consumer brands (Apple, Coca Cola, Home Depot) have
   genuinely salesy filings (commercial_drive 0.591, higher than the fraud firms), so they pull the wrong way
   and confound the between firm comparison. Controls should be industry and size matched, not blue chips.
3. **The anchor is the misstatement year, not the AAER release date.** The sharpest event study takes t0 as
   the enforcement date and reads the run of filings in the two years before it; that is a cleaner "before
   exposure" window than the misstatement year, which can start years earlier.
4. **Feasibility scale.** 22 fraud firms and 18 paired firms is enough to see a direction, not to certify one.

---

## Verdict

**Does the manipulation signature precede fraud exposure in corporate filings: NOT SHOWN in 10-K text.** The
direction is partially right (lower credibility index and higher commercial drive in fraud active years, for
about two thirds of firms) but weak and not significant, and the affect and candour tells that carry the
signature in other domains are muted by the dryness of accounting prose.

This is a real negative on the medium, not on the idea. The path to yes is specific and cheap:

- **Switch the text to earnings call transcripts.** Calls are spontaneous, affect rich and answer live
  questions, the opposite of templated filings. The scout already located free transcript sets; joining them
  to the Bao and AAER firm list by ticker is the next build. This is where the signature should show if it
  shows anywhere in corporate comms.
- **Anchor on the AAER release date** as t0 and take the two years of filings and calls before it, rather
  than the misstatement fiscal year.
- **Match controls on industry and size**, drawn from the Bao non fraud universe, not blue chip names.

The join, the label, the dates and the scoring pipeline are all proven and free; the result says the affect
led signature needs a wetter medium than the 10-K to surface.

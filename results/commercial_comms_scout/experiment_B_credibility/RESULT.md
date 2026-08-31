# Experiment B: does credibility have a voice

**Track:** PUBLIC (regtech). **Run date:** 2026-08-31. **Session:** comms-scout.

**Question.** Is institutional credibility a stable character signature (high rigour, high candour, low
affect), and does a shift in that signature precede a loss of trust?

**Instrument.** The 8 DYNAMICS axes (rigour, depth, originality, candour, affect, commercial_drive, stance,
register), scored on the free 7B `qwen2.5-7b-atlas` at :8301, temperature 0, the same scorer the sibling
children use. Self queued behind the running D8 and coupling jobs at low worker count.

**Corpus.** `samchain/bis_central_bank_speeches` (Hugging Face, 19,376 central bank speeches, each with
institution, Year, Month and full text). Two samples drawn:

- **Signature sample:** 465 speeches scored, stratified across 14 major central banks (about 35 each): the
  Federal Reserve (board and the FOMC voice), ECB, Bank of England, Bundesbank, Bank of Japan, Reserve Bank
  of India, Bank of Canada, Reserve Bank of Australia, Swiss National Bank, Bank of France, Bank of Italy,
  Reserve Bank of New Zealand and the BIS itself.
- **Bank of England timeline:** 247 BoE speeches scored, 2018 to 2025, to bracket the autumn 2022 gilt and
  liability driven investment episode as a trust loss anchor (t0 = 2022 Q3).

Scripts: `comms_b_prep.py`, `comms_score.py`, `comms_b_analyse.py` (staged on DL580 `/tmp`, corpora on NAS
`/mnt/nas/kronaxis/corpora/comms_scout/`).

---

## Result 1: credibility is a measurable voice, and it is the same voice everywhere

Mean character across 465 central bank speeches:

| axis | mean | sd |
|---|---:|---:|
| rigour | **0.816** | 0.045 |
| depth | 0.755 | 0.084 |
| originality | 0.600 | 0.038 |
| candour | **0.828** | 0.081 |
| affect | **0.462** | 0.053 |
| commercial_drive | **0.223** | 0.091 |
| stance | 0.578 | 0.095 |
| register | 0.713 | 0.095 |

The prediction was high rigour, high candour, low affect. Confirmed on all three: rigour 0.82 and candour
0.83 are the two highest axes, affect 0.46 sits below the midpoint, and commercial_drive 0.22 is near the
floor. This is the near exact inverse of the manipulation pole the detector children isolated (affect high,
candour low, commercial_drive high). Institutional credibility reads as a distinct, recognisable voice:
scholarly, transparent, unsensational, selling nothing.

**It is near invariant across institutions.** A credibility index (candour + rigour + depth minus affect
minus commercial_drive) sits at +1.71 overall with a standard deviation of only 0.16, and every one of the
14 banks falls in the band +1.63 to +1.79:

| bank | n | rigour | candour | affect | cred index |
|---|---:|---:|---:|---:|---:|
| Bank of Canada | 35 | 0.84 | 0.83 | 0.47 | +1.79 |
| Board of Governors (Fed) | 35 | 0.83 | 0.81 | 0.46 | +1.76 |
| European Central Bank | 34 | 0.83 | 0.80 | 0.44 | +1.76 |
| Bank of Italy | 35 | 0.84 | 0.81 | 0.46 | +1.74 |
| Bank for International Settlements | 17 | 0.80 | 0.79 | 0.44 | +1.74 |
| Swiss National Bank | 35 | 0.82 | 0.86 | 0.45 | +1.73 |
| Federal Reserve (speeches) | 35 | 0.81 | 0.85 | 0.46 | +1.72 |
| Reserve Bank of Australia | 34 | 0.81 | 0.86 | 0.46 | +1.72 |
| Reserve Bank of New Zealand | 35 | 0.81 | 0.85 | 0.46 | +1.70 |
| Bank of France | 34 | 0.81 | 0.80 | 0.45 | +1.70 |
| Deutsche Bundesbank | 31 | 0.81 | 0.83 | 0.46 | +1.70 |
| Bank of England | 35 | 0.80 | 0.81 | 0.47 | +1.67 |
| Bank of Japan | 35 | 0.82 | 0.84 | 0.48 | +1.65 |
| Reserve Bank of India | 35 | 0.80 | 0.84 | 0.49 | +1.63 |

Different countries, languages of origin and mandates, one voice. The credibility signature is an
institutional property, not a national one. For a regtech product this is the useful finding: a document
that claims institutional authority but scores off this tight band is reading as something other than a
central bank, which is exactly the tell a verification tool wants.

## Result 2: a shift preceding trust loss is NOT shown at this anchor

Bank of England, per year, around the autumn 2022 gilt and LDI episode (t0 = 2022 Q3):

| year | n | rigour | candour | affect | commercial | cred index |
|---|---:|---:|---:|---:|---:|---:|
| 2018 | 44 | 0.818 | 0.841 | 0.466 | 0.223 | 1.720 |
| 2019 | 48 | 0.808 | 0.858 | 0.475 | 0.231 | 1.702 |
| 2020 | 32 | 0.819 | 0.828 | 0.475 | 0.237 | 1.684 |
| 2021 | 40 | 0.805 | 0.870 | 0.467 | 0.212 | 1.730 |
| **2022** | 34 | 0.806 | 0.821 | 0.462 | 0.215 | 1.724 |
| 2023 | 34 | 0.809 | 0.826 | 0.482 | 0.241 | 1.674 |
| 2024 | 13 | 0.808 | 0.792 | 0.523 | 0.215 | 1.631 |

Baseline 2018 to 2021 versus the 2022 crisis year (Welch t):

| axis | baseline | 2022 | 2023 | 2022 vs baseline |
|---|---:|---:|---:|---|
| affect | 0.471 | 0.462 | 0.482 | t = -0.87, p = 0.39 |
| candour | 0.851 | 0.821 | 0.826 | t = -1.94, p = 0.052 |
| rigour | 0.812 | 0.806 | 0.809 | t = -0.79, p = 0.43 |
| cred index | +1.710 | +1.724 | +1.674 | t = +0.41, p = 0.68 |

There is a small dip in candour in 2022 (0.821 versus 0.851 baseline), directionally consistent with a voice
under pressure, but it is only borderline (p = 0.052) and it is not joined by the expected rise in affect
(affect actually ticks down). The credibility index does not move in 2022. The largest drift in the whole
window is in 2024 (affect 0.523, candour 0.792, cred index 1.631), a year and a half AFTER the crisis and on
a small sample of 13, so it is a lagging wobble, not a leading indicator.

**Honest read of the null.** The gilt and LDI episode was a poor anchor for this question. It was a fiscal
event (the September 2022 mini budget) in which the Bank of England was the responder and stabiliser, not
the institution whose own credibility was in question, so there is no strong reason its own speech character
should shift ahead of it. The leading indicator hypothesis needs an anchor where the institution's OWN
credibility is what gets lost: the "transitory" inflation misjudgement of 2021 to 2022 (both the Fed and the
BoE later walked it back), a forecast miss followed by a public mea culpa, or a governor credibility event.
The instrument and the timeline machinery are proven here; the anchor was wrong.

---

## Verdict

**Does credibility have a voice: YES, clearly and measurably.** High rigour, high candour, low affect, near
zero commercial drive, and the signature is tight and near invariant across 14 central banks in different
countries. It sits at the opposite pole to the manipulation signature, which makes it directly usable as a
regtech authenticity check.

**Does a shift precede a loss of trust: NOT demonstrated here.** The autumn 2022 BoE anchor gives only a
borderline candour dip and no affect rise; the largest character move is a lagging one in 2024. This is a
null at a badly chosen anchor, not evidence against the hypothesis. Next run: re anchor on an episode where
the central bank's own credibility is the thing lost (the transitory inflation walk back), across several
institutions, before making any claim about the leading indicator.

**Caveats.** Dataset date granularity is year and month, no day, so intra year timing around a Q3 event is
coarse. Some bank samples are capped at about 35 speeches for queue politeness; the signature is stable
enough that this is ample for Result 1, but the yearly BoE cells (especially 2024, n = 13) are thin for the
timeline test.

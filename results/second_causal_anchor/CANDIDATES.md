# A second causal anchor for Paper 4B: data hunt and feasibility

*DYNAMICS-WEB, PUBLIC track. Compiled 30 August 2026. Purpose: close the biggest remaining hole in
Paper 4B (What Moves a Person). Its causal effect side rests on a SINGLE randomised dataset, the Upworthy
Research Archive (headline A/B tests to clicks). We want a SECOND dataset of the same shape so the
persuasion claim does not stand on one corpus: text that was randomised or experimentally varied, paired
with a real human outcome that was measured, so the effect of character on the outcome is causal rather
than ecological.*

## Verdict up front

**A free second causal anchor exists.** The behavioural science megastudies of Milkman and colleagues
are the same shape as Upworthy: many message texts assigned to people at random, each arm carrying its own
real behavioural outcome, with the wordings published and the per arm data free to download. The
vaccination megastudy (osf.io/tucjs) is fetch confirmed below. It upgrades the outcome from a click to a
real health action, which strengthens the funnel argument of Paper 4B section 5. Its one weakness against
Upworthy is scale of text variation: roughly nineteen arms, not tens of thousands, so it is a coarse but
genuinely causal corroboration, not a like for like replacement.

A larger causal text bank is available from the Coppock, Hill and Vavreck political advertising
experiments (roughly forty nine real ads tested in randomised survey experiments, favourability outcome,
data free on Dataverse), but the message text there is inside video ads and must be transcribed, so the
text is available with work rather than as a ready column.

No clean open dataset matches Upworthy's scale of many randomised texts. Email marketing subject line A/B
data at the level of individual messages is proprietary (confirmed by search). If the programme wants a
second anchor at Upworthy scale it must run its own, and the minimal costed A/B is specified at the end.

## What we already hold (checked first, to avoid a duplicate hunt)

The held corpus index and the free persuasion catalogue were both read. Of the fifteen decision corpora on
disk, exactly ONE is randomised and causal: Upworthy. Everything else (ChangeMyView, debate.org DDO,
petitions, DonorsChoose, Old Bailey, Kickstarter, Persuasion for Good, ECHR, IQ2, TED) is ecological, so it
carries the confounds of topic, self selection and platform. That is why the hole is real: the whole
causal leg is one dataset. This document only lists candidates NOT already held in randomised form.

## Ranked candidates

Ranked by the three criteria in order: (a) genuinely causal, (b) message text available to score on the
eight axes, (c) free and accessible.

| # | Source | What was randomised | Outcome | Size | Text available to score? | Licence / access | Causal? |
|---|---|---|---|---|---|---|---|
| 1 | Milkman et al. 2021, PNAS: vaccination megastudy (Penn Medicine + Geisinger) | 19 SMS nudge texts vs usual care, patients assigned at random | flu vaccination taken (electronic health record), per arm uplift | N = 47,306 patients; 19 arms + control | **Yes**: wordings in the paper and web appendix; also 12 human coded attributes per message by 2,214 Prolific raters | Aggregated per arm data + appendix + scripts FREE on OSF osf.io/tucjs; individual rows behind a medical NDA (not needed) | **Yes, randomised** |
| 2 | Milkman et al. 2022, Nature: Walmart pharmacy megastudy | 22 SMS reminder texts vs business as usual, customers assigned at random | pharmacy vaccination, per arm uplift | N = 689,693; 22 arms + control | **Yes**: wordings published; companion design to #1 | Aggregated summary data FREE on OSF; individual rows not public | **Yes, randomised** |
| 3 | Coppock, Hill & Vavreck 2020, Science Advances | ~49 real political ads shown vs a placebo car advert, viewers assigned at random | candidate favourability (survey), per ad effect | ~34,000 people, 59 experiments | **With work**: text is the ad script inside a video; needs transcription or a codebook, not a ready column | Replication data FREE on Yale Dataverse doi 10.60600/YU/OGTYGY and Harvard Dataverse; code on GitHub | **Yes, randomised** |
| 4 | Gerber, Green & Larimer 2008: social pressure mailers | 4 to 5 mailer texts vs control, households assigned at random | validated turnout from the voter file | large N, but only ~4 to 5 distinct texts | Yes, the few mailer texts are printed | Dataverse / ICPSR, FREE | Yes, but too few texts to score eight axes; a single causal data point, not an anchor |
| 5 | Bond et al. 2012: 61 million person Facebook experiment | 2 to 3 message conditions (social vs informational) | validated turnout | ~61,000,000, 2 to 3 texts | The handful of texts are described | Aggregate published; row data walled | Yes, but two or three texts only; same limitation as #4 |

### Not viable / walled (recorded so the negative is honest)
- **Email marketing subject line A/B (open rate, click rate).** The clean shape we want, but individual
  message level data is proprietary. Vendors publish aggregate benchmarks (MailerLite, Yesware) and one
  academic study models open rate on 1.2 million emails, but no free row level randomised dataset with the
  message text and its own outcome was found. Confirmed by search on 30 August 2026.
- **IQ2 debates, TED persuasiveness ratings, ChangeMyView, petitions, DonorsChoose, GoFundMe.** Real
  outcomes but the text was NOT randomised, so they stay ecological. Several are already held.

## Fetch confirmation of the top candidate (candidate 1)

The Milkman 2021 paper PDF was fetched and its text extracted on 30 August 2026. Confirmed directly from
the paper:

- **19 experimental conditions** delivered by text message, plus a usual care control, N = 47,306,
  patients assigned at random.
- **Per arm outcome exists.** Figure 1 reports the regression estimated increase in flu vaccinations for
  each of the 19 interventions against the usual care control, with confidence intervals. The aggregated
  version of this is the free OSF deposit.
- **Message text is available and quoted.** Example wordings recovered from the paper: the reminder
  "that a flu vaccine has been reserved for your appointment" (the top performing arm, sent 72 hours then
  24 hours before the visit); an earlier text telling the patient "a vaccine reminder" would be sent
  before the appointment. The full set of wordings is in the paper and web appendix.
- **Bonus for instrument validation.** The authors already had 2,214 Prolific workers code every message
  on twelve subjective attributes (for example casualness) plus objective attributes (word count), then ran
  principal components analysis. So our eight axis scores can be cross checked against an independent human
  coded attribute space on the very same texts.

Shape proven: usable text plus a real randomised outcome, free at the level we need. Full scoring was not
run (out of scope for a data hunt); this only proves the corpus is fit to become the second anchor.

## How to use it (feasibility note, not a run)

Score the 19 (candidate 1) and 22 (candidate 2) message texts on the eight character axes with the same
instrument used on Upworthy. Pool the two megastudies for roughly forty one causal texts, then regress per
arm outcome (vaccination uplift, weighted by arm N and precision) on the axis scores, between arms. Because
assignment was random within each study, a surviving axis coefficient is causal. Expect low power from the
small number of arms, so the honest reading is directional corroboration: does the character that raises a
real health action agree in sign with, or differ from, the character that raises a click on Upworthy? Under
the Paper 4B thesis (no single character persuades; the winning character is a function of the outcome) the
interesting result is either outcome. Adding candidate 3 (transcribe the ad scripts) would lift the causal
text bank to about ninety, at the cost of the transcription step, and swaps a real action for an attitude
measure, which widens the funnel across outcome types.

## If a like for like Upworthy twin were wanted: the minimal A/B to run

A free open dataset at Upworthy scale of many randomised texts does not exist, so a same scale second anchor
would have to be run in house. The minimal viable design:

- **Vary:** the message text only, along the two load bearing axes, matter against manner and stance
  (measured against one sided), holding the ask and the offer fixed. Author or draft variants at chosen
  points in the axis space, the way the Section 3 manipulation did, but at bank scale rather than a handful.
- **Outcome:** a real click or open, the closest cheap analogue of Upworthy. Subject lines in the
  company's own regulated outreach are the obvious carrier, since the outcome (open, click) is logged and
  the send is already randomisable by the platform.
- **Smallest viable N:** aim for at least 40 to 60 distinct texts so an eight axis regression has room,
  each arm sized for a detectable difference in click rate. At a base rate near a few percent and a target
  lift of one to two points, that is on the order of a few thousand recipients per arm, so low tens of
  thousands of sends in total across the bank. This is within the reach of the existing outreach list and
  needs no external panel.
- **Why this and not a paid crowd panel:** it produces a randomised text to real behaviour anchor on our
  own infrastructure, at Upworthy's shape, for the cost of sends we already make, and it sidesteps the
  model author and model reader lineage concern named in Paper 4B section 7.

## Sources

- Milkman et al. 2021, PNAS, vaccination megastudy: https://www.pnas.org/doi/10.1073/pnas.2101165118 ;
  data OSF https://osf.io/tucjs/ ; lab page https://bcfg.wharton.upenn.edu/vaccination/
- Milkman et al. 2022, Nature, Walmart pharmacy megastudy: https://www.nature.com/articles/s41586-022-04526-2
  (open access mirror academia.edu/104219687); data OSF (aggregated).
- Coppock, Hill & Vavreck 2020, Science Advances: https://www.science.org/doi/10.1126/sciadv.abc4046 ;
  author page https://alexandercoppock.com/coppock_hill_vavreck_2020.html ; Yale Dataverse doi
  10.60600/YU/OGTYGY ; ISPS https://isps.yale.edu/research/publications/isps20-018
- Gerber, Green & Larimer 2008 social pressure mailers: Harvard Dataverse / ICPSR (search
  "social pressure and voting field experiment").
- Bond et al. 2012 Facebook 61 million person experiment: https://www.nature.com/articles/nature11421
- Upworthy Research Archive (the first anchor, held): OSF osf.io/jd64p.

# Commercial character experiments: corpus scout and feasibility

**Track:** PUBLIC. **Scout date:** 2026-08-30. **Author session:** comms-scout.

> **UPDATE 2026-08-31: both experiments have now been run on the free data.** Results:
> `experiment_B_credibility/RESULT.md` (credibility IS a measurable voice, tight and near invariant across
> 14 central banks; the trust loss leading indicator is a null at the autumn 2022 anchor, which was the wrong
> anchor) and `experiment_A_fraud/RESULT.md` (the manipulation signature does NOT clearly rise before fraud
> exposure in dry 10-K prose; weak partial direction only; earnings call transcripts are the next medium).
>
> **UPDATE 2026-08-31 (later): the fraud path to yes has now been run on the wetter medium.**
> `experiment_A2_earnings_calls/RESULT.md`: SEC AAER firms (25) joined to S&P 500 earnings call transcripts
> by ticker, t0 = AAER release date, sector matched (same SIC) controls. The affect tell, dead flat in
> 10-Ks, RECOVERS in calls: fraud pre exposure calls are significantly higher in affect than the same firms'
> own earlier calls (d = +0.32, p = 0.007), and candour is lower than controls (p = 0.06). Partial, one axis
> to significance on a hard large cap testbed, but the medium hypothesis holds. Next: small cap built on
> fraud firms and the analyst Q and A split.

Two commercial experiments that point the character instrument at money with no human study. For each,
the corpora that exist free, how to reach them, a live feasibility pull that proves the data carries text
plus the label or date the study needs, and a verdict on whether it runs now or needs a named acquisition.

The instrument reads the 8 DYNAMICS axes (rigour, depth, originality, candour, affect, commercial_drive,
stance, register) off any text, the same 7B scorer the sibling children use. The scout does not run the
study; it proves the shape.

---

## EXPERIMENT A: the manipulation signature in corporate comms before a fraud breaks

**Question.** Does a company's communication character shift (affect up, candour down, the manipulation
signature the detector children already isolated) in the filings and calls issued *before* an accounting
fraud is exposed, relative to its own clean baseline and to matched honest firms? A before versus after
event study anchored on the enforcement or restatement date.

**What the study needs.** Company text with a date, plus a fraud label with an exposure date, joinable by a
stable firm key. All three exist free.

### A ranking

| Rank | Corpus | Open | Text | Label | Date | Join key | Verdict |
|---|---|---|---|---|---|---|---|
| A1 | SEC EDGAR 10-K / 10-Q full text + Bao 2020 fraud labels + AAER dates | yes | yes, prose | yes | yes | CIK, gvkey, fiscal year | **RUNS NOW** |
| A2 | Earnings call transcripts (jlh-ibm CC0; lamini 860k) joined to AAER by ticker | yes | yes, high affect | via join | yes | ticker, date | partial, label join owed |
| A3 | Stanford Securities Class Action Clearinghouse (SCAC) | browse only | index | yes | filing date | ticker, company name | secondary label, scraping blocked |

### A1: EDGAR text + Bao labels + AAER dates (the runnable stack)

**Text source: SEC EDGAR full text search and archives.** Free, no key. The search index returns filing
date, form type and CIK; the archive serves the document.

- Full text search API (2001 onward): `https://efts.sec.gov/LATEST/search-index?q=...&forms=10-K`
  Live pull returned 7,441 hits for a plain query, each row carrying `ciks`, `period_ending`, `display_names`,
  form and accession. The top hit for a fraud query was MIMEDX GROUP (MDXG), itself a real accounting
  enforcement case, which is a good sign the text and the label sets overlap.
- Submissions API: `https://data.sec.gov/submissions/CIK{10digit}.json` lists every 10-K and 10-Q with its
  filing date and primary document name.
- Archive document: `https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{doc}` serves the filing.

**Feasibility pull (proves text plus date).** MiMedx (CIK 1376339). Submissions API returned, among others:

    10-K  filed 2026-02-25  accession 0001376339-26-000011  doc mdxg-20251231.htm
    10-Q  filed 2026-07-29  accession 0001376339-26-000071  doc mdxg-20260630.htm

Fetching the 10-K and stripping tags yielded clean risk and business prose, the exact candour and affect
signal the instrument reads:

  > "we may not be able to successfully execute our priorities. If we do not successfully execute our
  > priorities, or if actual results vary significantly from our assumptions, our business, operating
  > results and financial condition could be adversely impacted. We are in a highly competitive and evolving
  > field..."

So the text carries a per filing date and readable prose. Confirmed.

**Label source: Bao, Ke, Li, Yu and Zhang (2020), Journal of Accounting Research.** GitHub
`JarFraud/FraudDetection`, free, no key. This is the canonical machine readable accounting fraud panel,
built from the USC Marshall AAER database.

- `data_FraudDetection_JAR2020.csv` (47.8 MB): one row per firm per fiscal year with `fyear`, `gvkey`,
  `p_aaer`, and the binary `misstate` label, plus the raw financial features. Header confirmed live:
  `fyear,gvkey,p_aaer,misstate,act,ap,at,ceq,che,cogs,...`
- `AAER_firm_year.csv` (33 KB): the fraud firm years keyed by `P_AAER, CIK, YEARA, UNDERSTATEMENT`. Head
  confirmed live (`2,47059,1978,0` ...). **This file carries CIK, which is the direct join to EDGAR text.**
- `identifiers.csv` (1.6 MB): `fyear,gvkey` crosswalk for the full panel.

**Exposure date source: SEC AAER release pages.** Free, browsable, dated. Annual archives at
`https://www.sec.gov/divisions/enforce/friactions/friactions{YYYY}.shtml` (current landing page
`https://www.sec.gov/enforcement-litigation/accounting-auditing-enforcement-releases`). Live pull of the
2016 archive returned dated, named releases:

    AAER-3840  Dec. 29, 2016  General Cable Corporation
    AAER-3839  Dec. 27, 2016  David A. Loppert
    AAER-3838  Dec. 27, 2016  Philip Greifeld, CPA

So the fraud break has an exact public date and a named entity. Confirmed.

**The minimal join.** Bao `misstate` gives which firm years are fraudulent (label); `AAER_firm_year.csv`
gives the CIK for those firms; EDGAR gives the dated filings by CIK; the AAER archive gives the enforcement
date that marks "before" from "after". `gvkey` to `CIK` for the clean control firms comes from the Bao
`p_aaer` linkage plus the SEC ticker to CIK map (`https://www.sec.gov/files/company_tickers.json`, free).
No paid data. WRDS or Compustat is optional, only if you want their pre linked gvkey to CIK bridge for the
whole universe rather than deriving it.

**Verdict A1: RUNS NOW.** Open text, open label, open dates, all keys free. The one build cost is the
gvkey to CIK crosswalk for control firms, which is a small free join, not an acquisition.

### A2: earnings call transcripts (the higher affect text)

Calls carry far more affect and manner than a 10-K, so they are the better place to see the signature move.
Free options confirmed on Hugging Face:

- `jlh-ibm/earnings_call` (CC0). Transcripts named by date and ticker, for example
  `data/transcripts/AAPL/2016-Apr-26-AAPL.txt`, paired with per company daily `stock_prices` CSVs. Excellent
  shape for a text to market reaction study, but only about ten large technology firms and **no fraud case in
  the set**, so it cannot supply Experiment A's label on its own.
- `lamini/earnings-calls-qa` (860k rows), `jdecim/pit-earnings-call-qa` (448k rows): far wider coverage, but
  packaged as question and answer pairs, so the speaker turns and the call date need reassembling before use.

**Verdict A2: partial.** Text is free and rich; the fraud label is not in these sets. To use calls for A you
must join transcript dates to the Bao or AAER firm list by ticker, and confirm a given fraud firm has calls
in the free set. Runnable as a second wave after A1, not the first cut.

### A3: Stanford Securities Class Action Clearinghouse

Dated securities fraud litigation events (filing date, defendant company), a complementary label to AAER
that catches market fraud the SEC did not itself charge. Free to browse at `securities.stanford.edu`, but the
site returned HTTP 403 to an automated request, so a bulk pull needs either a polite paced fetch, a manual
export, or the anti bot override the operator grants on cleared commercial targets. Bao plus AAER is the
cleaner free label, so SCAC is a secondary widening of the event set, not a dependency.

---

## EXPERIMENT B: does credibility have a voice

**Question.** Is institutional credibility a stable character signature (high rigour, high candour, low
affect), and does a shift in that signature precede a loss of trust? Central bank and regulator communications
are the purest place to measure it, because the institution's whole product is credibility.

**What the study needs.** Dated institutional text over a long enough span to see drift, and optional trust
loss anchors (a currency or gilt episode, a forecast miss, a governor credibility event) to test the "shift
precedes the loss" leg. No classification label is needed to measure the signature itself; the axes are read
directly.

### B ranking

| Rank | Corpus | Open | Text | Date | Span | Verdict |
|---|---|---|---|---|---|---|
| B1 | BIS central bankers' speeches archive | yes | yes | yes, per speech | ~1997 to now, 21,492 speeches | **RUNS NOW** |
| B2 | Federal Reserve FOMC statements and minutes | yes | yes | yes, per meeting | 1994 to now | **RUNS NOW** |
| B3 | Bank of England speeches | yes | yes | yes, per speech | multi year | **RUNS NOW** |

### B1: BIS central bankers' speeches (flagship)

`https://www.bis.org/cbspeeches/index.htm`, with a dedicated export at `.../cbspeeches/download.htm` and a
feed at `https://www.bis.org/doclist/cbspeeches.rss`. Live check confirmed the collection reports 21,492
speeches, each individually dated (most recent shown 17 Aug 2026), spanning many countries and central banks.
Most full texts sit on the originating central bank site and are linked from the BIS record, and the BIS also
mirrors the text. This is the widest dated institutional credibility corpus that exists free, and it is
cross country, which lets the study ask whether the credibility signature is the same voice in every central
bank or varies by institution.

**Feasibility.** Index and RSS both reachable (HTTP 200). Each entry carries a title, a delivery date and a
link to the text. Confirmed dated and textual.

### B2: Federal Reserve FOMC statements and minutes

`https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`. Live check confirmed statements and
minutes in both HTML and PDF, each individually dated by meeting, minutes released three weeks after the
decision, with an advanced search and a link to full historical transcripts. The recent calendar covers
2021 to 2027; the statement archive runs back to 1994. This is the tightest single institution time series,
ideal for the drift and the trust anchor legs (for example the character of statements around a policy
credibility episode).

### B3: Bank of England speeches

`https://www.bankofengland.co.uk/news/speeches`. Page reachable via a normal client (HTTP 200), listing
speeches by speaker and date across recent years; older speeches are in the same archive. The links render
through the site's own script, so a pull uses the site listing or its search rather than a raw HTML scrape.
The natural UK trust loss anchor is the autumn 2022 gilt and pension episode, a clean before versus after
window on the same institution's voice.

**Verdict B: RUNS NOW on all three.** Pure dated text, no label join at all to measure the signature. The
only optional acquisition is a small hand list of dated trust loss events to test the leading indicator leg,
which is public record, not a dataset purchase.

---

## Overall verdict

Both experiments run now on free data.

- **Experiment B is the cleaner immediate run.** BIS, FOMC and Bank of England give dated institutional text
  with no label to acquire. The credibility signature can be measured this week; the "shift precedes trust
  loss" leg needs only a short public list of trust events.
- **Experiment A also runs now** on SEC EDGAR text joined to the Bao 2020 fraud labels and AAER enforcement
  dates, all free and all proven reachable in this scout. Its one build cost is a free gvkey to CIK crosswalk
  for control firms. Earnings call transcripts (A2) are a strong second wave for the affect signal once their
  fraud labels are joined by ticker; Stanford SCAC (A3) is an optional widening of the event set that needs a
  paced or manual pull because the site blocks automated requests.

Nothing here needs a paid acquisition. The only items that are not a one command fetch are the SCAC index
(blocked to bots) and the gvkey to CIK control crosswalk (a free join), and neither blocks the first cut of
either experiment.

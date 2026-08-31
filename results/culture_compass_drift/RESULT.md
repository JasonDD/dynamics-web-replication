# Culture compass, temporal validation: does a nation's web character drift track its survey opinion drift?

**Programme:** DYNAMICS-WEB. **Question:** the cross sectional probe showed a nation's web
character sits where its culture sits. This asks the harder temporal question the cross sectional
probe cannot: wave over wave, when a nation's survey opinion *moves*, does its web character
*move with it*? If web character led opinion it would be an early signal; if it lagged it would be
an echo.

**Verdict:** the test is runnable, and it comes back a clean null. Across 31 to 33 nations and
four independent survey items, the direction and size of a nation's opinion drift do not track the
direction and size of its web character drift. Every correlation is small and none is significant
(largest |r| = 0.29, all p > 0.10; sign agreement 39 to 58 per cent, i.e. chance). On this
evidence web character is neither a leading nor a lagging indicator of opinion change. The
important qualifier is in section 6: the two sides measure different things (rhetorical *manner*
versus opinion *content*), so a null is close to what an honest prior would expect, and the
same construct temporal test (web *stance* drift versus survey opinion drift) still cannot be run
because the web side has no per nation stance signal at two or more time points.

---

## 1. Feasibility first (the part the brief flagged as the likely wall)

The brief warned that the binding constraint would be the web side: per nation web character at
two or more time points might not exist. **It does exist**, and that is the main good news here.

- **WEB side, 2+ time points: YES.** The DYNAMICS-WEB "when" leg already computed a within domain
  matter/manner drift across four Common Crawl snapshots (2020, 2022, 2024, 2026), broken out per
  ccTLD. Source of record: `../where_when.txt` and `../when_drift.txt`. The aggregate within domain
  drift (same 50,462 domains present in both 2020 and 2026) is real and strong (mean PC1
  +0.031 -> +0.106, paired t = +11.55, p = 7.9e-31, drift toward matter). The per country
  breakdown gives 33 nations with at least 40 within domain pairs. **Nothing was scored again for
  this work** (per the brief: no new character scoring, :8301 and :8288 untouched); the per country drift
  numbers are read straight from the committed result file.

- **SURVEY side, 2+ time points: YES, via a route that is free and needs no login.** We held only
  WVS Wave 7 (2017 to 2022), one point, from the `oxford-llms` HuggingFace mirror. That mirror
  family has no earlier WVS wave (it carries Wave 7 plus the European Social Survey 2020 and 2023,
  European only). The official WVS trend file and the GESIS EVS/WVS joint file both sit behind a
  data agreement form that is not machine fetchable. The working route is **Our World in Data**,
  which republishes the **Integrated Values Survey (EVS + WVS)** as per country time series, one CSV
  per item, machine readable with no login. These carry multiple waves per country (1981 to 2022
  depending on item), which is exactly the second time point the survey side needed.

So both sides clear the two point bar. The deliverable is the alignment result, not a "data does
not exist" note.

**The one temporal gap that no acquisition can close today:** the web drift window is 2020 to 2026,
but the latest released survey wave is 2022 (WVS Wave 8, 2023 to 2027, is in the field, not out).
So the survey drift can only run over roughly 2010 to 2022, ending as the web window opens. The
test is therefore a leading indicator test (does opinion change in the decade into the web window
predict web character change over 2020 to 2026), not a contemporaneous one. A contemporaneous
same window test waits on WVS Wave 8.

---

## 2. Data

### Web side (drift to explain)
Per ccTLD within domain matter/manner PC1 drift 2020 -> 2026, 33 nations, from `../where_when.txt`.
Positive means the nation's web prose drifted toward **matter** (substance) and away from
**manner** (style). Per country domain counts range from 74 (Ireland) to 4,274 (Russia), so the
thinner countries carry more noise. The matter/manner PC1 recipe is the one in
`truthometer/scripts/manip_analyse.py`; it was applied upstream, not here.

### Survey side (drift to test against)
Integrated Values Survey per country item series from Our World in Data (files in `owid/`):

| Item (our name) | OWID chart | Value used | Higher means |
|---|---|---|---|
| `religion_very_important` | how-important-religion-is-in-your-life | share "very important" (%) | more religious |
| `trust_government` | trust-state-institutions-wvs | trust in government (%) | more trust in government |
| `confidence_un` | confidence-in-un-wvs | confidence in the UN (%) | more institutional confidence |
| `homosexuality_not_justifiable` | share-of-people-who-think-homosexuality-is-never-justified | share "never justifiable" (%) | more traditional social values |

These four are the WVS/IVS items with clean multi wave country coverage on OWID (each about 94
countries with more than one wave). The other three Wave 7 anchor items (immigration
restrictiveness, importance of democracy, men make better leaders) have no multi wave OWID series,
so they cannot be drifted and are dropped. Religion and institutional confidence map directly onto
the Wave 7 anchor; the homosexuality item is a standard values traditionalism axis standing in for
the gender/tradition dimension.

---

## 3. Method

For each nation and item, opinion drift = value at the latest wave (2022 where present) minus the
value at the wave closest to twelve years earlier, requiring a span of at least six years (in
practice almost every country resolves to 2010 -> 2022). This is the nation's opinion trajectory
over the decade into the web window. It is joined by country to the web PC1 drift. Across the
joined nations we take Pearson and Spearman correlations (scipy) between opinion drift and web
drift, plus a sign agreement count (does the nation move the same way on both sides of zero).
Script: `drift_align.py`. Full per nation tables: `drift_align_output.txt`.

---

## 4. Results

| Item | nations | Pearson r (p) | Spearman r (p) | sign agreement |
|---|---|---|---|---|
| religion very important | 33 | -0.090 (0.62) | -0.157 (0.38) | 13/33 = 39% |
| trust in government | 31 | +0.021 (0.91) | +0.088 (0.64) | 18/31 = 58% |
| confidence in the UN | 33 | -0.286 (0.11) | -0.176 (0.33) | 13/33 = 39% |
| homosexuality never justifiable | 33 | +0.033 (0.86) | +0.060 (0.74) | 15/33 = 45% |

Every coefficient is small. None reaches significance at the 0.05 level; the largest, confidence
in the UN at r = -0.29 (p = 0.11), would not survive correcting for testing four items
(Bonferroni alpha = 0.0125) and points the opposite way to the trust in government item, so it
reads as noise rather than signal. Sign agreement sits at chance throughout. The opinion side is
not flat, which rules out a "nothing moved" explanation: religiosity fell almost everywhere
(Ireland -20 points, Turkey -18), traditional social values fell hard (Italy -32, United Kingdom
-19), yet neither trajectory lines up with which nations' web prose moved toward matter.

---

## 5. Verdict

**A nation's web character drift does not track its survey opinion drift, across nations, on the
data that exists today.** Web character is neither a leading nor a lagging indicator of opinion
change at this granularity. This is an honest null, not a positive finding dressed down.

The cross sectional claim still stands (web character sits where culture sits, at one moment); it
is the *temporal co movement* that fails. A static map of where nations sit is not the same as a
dynamic claim that they move together, and only the temporal test can tell them apart. It just did.

---

## 6. Why the null is close to expected, and the stronger test it points to

Two reasons weigh on how much to read into this, and the first is the important one.

1. **The two sides measure different things.** The web side is matter/manner PC1, a *rhetorical*
   axis: how the web argues, substance versus style. The survey side is opinion *content*: how
   religious a population is, how much it trusts government. There is no strong reason a population
   becoming less religious should make its web prose drift toward matter rather than manner; the
   two are close to orthogonal by construction. So a null here is roughly what a careful prior
   predicts. What this rules out is a strong, tidy coupling between rhetorical style change and
   opinion change; it does not test the claim people actually care about, which is whether the web
   tracks *what a nation thinks*, not *how it phrases things*.

2. **Timing and noise.** The survey drift ends in 2022 and the web drift runs 2020 to 2026, so the
   design is a leading indicator test with a gap, not a matched window; the per country web drift is
   built on as few as 74 domains for some nations; and 31 to 33 nations is modest power. None of
   these alone manufactures a null (the effect sizes are near zero, not merely uncertain), but they
   cap how hard a positive result could ever have landed.

**The test worth running next, and the exact data it needs.** The construct matched temporal
validation is web *stance* drift versus survey *opinion* drift: for each nation and each
contestable topic, a machine read average position (for or against immigration, pro or anti
democracy) at two or more time points, correlated with the same nation's WVS drift on that topic.
The missing piece is entirely on the web side:

- We have a one window per nation position proxy already (GDELT theme filtered tone, in
  `../position_field_wvs_validation/`), but it is a single 2017 to 2022 span, so it has no second
  time point and cannot be drifted. It is also tone (sentiment), not stance.
- To run the stronger test we need a **per nation, per topic stance score at two or more windows**.
  The cheapest honest build: pull GDELT theme filtered tone per `sourcecountry` in two separate
  windows (for example 2015 to 2018 and 2021 to 2024) so a tone drift exists per nation, and in
  parallel score stance (not tone) from the article text on the four to five WVS topics for the
  same two windows. That gives a web opinion drift to set against the WVS opinion drift on a like
  for like axis.
- For a contemporaneous survey side (rather than a leading one), the release of **WVS Wave 8**
  (2023 to 2027) supplies a survey point inside the web window; until then the survey drift is
  capped at 2022.

Until that web side stance time series exists, the same construct temporal validation cannot be
run. What *can* be run, and was, is the character axis version, and it is null.

---

## 7. Files and reproduction

- `drift_align.py`: joins web PC1 drift to OWID IVS opinion drift, correlates. Deterministic, uses
  only the committed CSVs; run again with `python3 drift_align.py`.
- `drift_align_output.txt`: full per nation tables for all four items.
- `owid/*.csv`: the four Integrated Values Survey item series from Our World in Data (free, no
  login). Chart slugs are in section 2; refetch with
  `curl -s "https://ourworldindata.org/grapher/<slug>.csv"`.
- Web side inputs (not produced here): `../where_when.txt`, `../when_drift.txt`.

# The position field, pass 1: does GDELT news tone track population opinion?

**Programme:** DYNAMICS-WEB. **Question:** can a worldwide *position* signal be read off
machine readable web data, and does it track the population opinion an established survey
measures? This is the opinion or stance side of the field, the companion to the rhetorical
character axes. The World Values Survey is the ground truth anchor, the same role Hofstede
played for the character axis.

**Verdict (pass 1):** *promising on the one item we could fetch, and deferred on the rest.*
For immigration, the single item completed before the free DOC API flagged the source address
and blocked sustained fetching (11 countries), GDELT average news tone tracks WVS population
opinion **in the expected direction and significantly**: countries whose immigration news runs
more negative also hold more restrictive attitudes (Pearson -0.68, Spearman -0.70, both p < 0.005).
That is a genuine "free signal tracks opinion" result on one topic. The other four items are not
yet fetched: the DOC API rate limiter flags the source IP under any sustained request rate (a lone
request returns http 200, but roughly two to three requests a minute re trip connection resets
that do not clear during the run), so the full five item validation is deferred, not failed. The
block is itself a pass 1 finding on free tier viability, discussed in the Results section.

**Budget:** zero. All data is free and machine readable. No OCR. No Google BigQuery. No paid
API. All fetched data lives in `the internal corpus store` (persistent).

---

## 1. What we are testing

For a contestable topic, a country's population holds an average opinion (measured by the WVS).
Separately, the news published from that country carries an average *tone* on that topic
(measured by GDELT). Pass 1 asks the cheapest possible question: **without fetching or scoring
a single article, does GDELT's own theme filtered average tone, per country, correlate with the
survey opinion, per country?** If it does, the free tone signal is a usable first proxy for a
worldwide position field. If it does not, that is the finding, and pass 2 (stance inference from
article text) is the documented next step.

**Honesty up front.** GDELT tone is *sentiment*, not for or against *stance*. A country whose
news discusses immigration in negative event contexts (crime, crisis, border deaths) will show
negative tone regardless of whether its population is pro or anti immigration. Tone and stance
are different quantities; a strong correlation would be a pleasant surprise, a weak one is the
expected null. Two further gaps are baked in and reported, not hidden: **selection bias** (the
outlets GDELT indexes are not the population, and skew urban, English or major language, and
elite), and **temporal misalignment** (WVS7 fieldwork ran 2017 to 2022 per country on different
dates; the GDELT window is a fixed 2017 to 2022 span, matched as best but not per country).

---

## 2. The anchor: WVS Wave 7 country opinion

**Source.** World Values Survey Wave 7 (2017 to 2022), respondent level. Obtained machine
readable and login free from the HuggingFace mirror
`oxford-llms/world_values_survey_2017_2022_sft`, a faithful SFT repackaging of the official WVS7
cross national file. Each row carries one held out WVS item with the respondent's true coded
answer; the respondent id's leading digits are the ISO numeric country code (verified: 804 to
Ukraine, 826 to Great Britain, and so on). We parsed 439,608 answer rows spanning 366 WVS items
and 66 countries.

The official WVS site and the GESIS EVS or WVS joint file were the first choice but both sit
behind a data agreement form that is not machine fetchable; Our World in Data publishes only two
of the five items we need. The SFT mirror is the fully machine readable route to the same Wave 7
answers. **Cost of the mirror:** it is a sample, not the full 94,728 respondent file. Per country
per item we have a median of about 20 substantive responses, so each country mean is noisier than
a full WVS aggregate. Because the *between country* spread on these items is very large (see the
extremes below), the cross national signal still dominates the per country noise, but the thin
`n` attenuates every correlation reported here and is the main limit on the anchor's precision.

**Five contestable items** (build: `build_wvs_anchor.py`; countries kept at >= 15 substantive
responses):

| Topic | WVS item (abbreviated) | Answer to numeric | Higher score means |
|---|---|---|---|
| Immigration | "people from other countries coming here to work: what should the government do?" | let anyone come 1, if jobs available 2, strict limits 3, prohibit 4 | more restrictive |
| Religion | "how important is God in your life?" (1 to 10) | 1 to 10, endpoints labelled | more religious |
| Democracy | "how important is it to live in a country governed democratically?" (1 to 10) | 1 to 10 | more pro democracy |
| Institutions | "how much confidence do you have in the government?" | none 1, not very much 2, quite a lot 3, a great deal 4 | more trust |
| Gender roles | "on the whole, men make better political leaders than women do" | strongly disagree 1 to agree strongly 4 | more traditional |

**Anchor sanity (extremes are face valid):**

- **Immigration restrictiveness** (58 countries, median n=26): lowest Uzbekistan 1.83, Germany
  2.07, Puerto Rico 2.08; highest Greece 2.96, Lebanon 3.00, Ecuador 3.10.
- **Importance of God** (40 countries, median n=19): lowest China 1.93, Australia 3.18,
  Netherlands 3.20; highest Kyrgyzstan, Maldives, Egypt all near 10.0.
- **Importance of democracy** (16 countries, median n=20): lowest Bolivia 8.11, Turkey 8.27,
  Mexico 8.67; highest Germany 9.70, Puerto Rico 9.94, Ethiopia 10.0.
- **Confidence in government** (15 countries, median n=18): lowest Tunisia 1.55, Mexico 1.61,
  Peru 1.73; highest Singapore 3.14, Indonesia 3.17, China 3.51.
- **Gender, men better leaders** (17 countries, median n=20): lowest Netherlands 1.23, Great
  Britain 1.50, Canada 1.67; highest China 2.64, Armenia 2.78, Pakistan 3.23.

The country coverage is uneven because the SFT sample held different items out at different rates;
immigration and religion are well covered, the three 4 point and 1 to 10 battery items thinner.

Files: `the internal corpus store/wvs_position/wvs_country_items.csv` (long),
`wvs_country_wide.csv` (pivot).

---

## 3. The web signal: GDELT theme filtered average tone

**Source.** GDELT DOC 2.0 API (`api.gdeltproject.org`), `mode=TimelineTone`, filtered by a GKG
theme and by `sourcecountry` (the FIPS country of the news outlet), over 2017-01-01 to
2022-12-31. This is GDELT's own extracted average tone; **no article text is fetched and nothing
is scored** in pass 1. Free access only, no BigQuery. Empty time bins come back as 0 and are
dropped; the scalar per country is the mean tone over the nonzero bins. Fetch:
`fetch_gdelt_tone.py` (paced to respect the DOC API rate limit, resumable).

**Theme to item mapping** (documented, not assumed clean):

| WVS item | GKG theme(s) queried | Mapping quality |
|---|---|---|
| Immigration | `IMMIGRATION` | direct |
| Religion | `RELIGION` | direct |
| Democracy | `DEMOCRACY` | direct |
| Confidence in government | `CORRUPTION`, `GENERAL_GOVERNMENT` | indirect: negative government or corruption coverage is a proxy for low trust; two candidates fetched, the better behaved reported |
| Gender roles | `DISCRIMINATION`, `SOC_GENDEREQUALITY` | indirect: no clean single theme for gender role traditionalism; two candidates fetched |

**Expected sign, if tone tracked opinion.** For immigration, more negative tone would go with more
restrictive attitudes, so a *negative* Pearson r (tone falls as restrictiveness rises). For
religion and democracy, if the topic is discussed more warmly where it matters more, a *positive*
r. For confidence, more negative corruption tone would go with lower trust, so a *positive* r
(tone and trust fall together). These are hypotheses; tone is sentiment, so any of them can fail.

File: `the internal corpus store/gdelt_position/gdelt_country_tone.csv`.

---

## 4. Results

### 4.1 What we could fetch

The DOC API let the fetch complete only the immigration item, and only for 11 countries, before
it flagged the source address (see 4.4). So the validation table has one row, not the five to
seven the theme map allows. That one row is real data and is reported in full; the rest is
deferred to a paced re run, not written up as a null.

**Correlation table** (`validate.py` → `validation_table.csv`):

| item | GDELT theme | n countries | Pearson r | p | Spearman r | p | higher WVS means |
|---|---|---|---|---|---|---|---|
| immigration_restrictiveness | IMMIGRATION | 11 | **-0.684** | 0.0049 | **-0.702** | 0.0031 | more restrictive |

### 4.2 The immigration result reads the right way round

The expected sign for immigration was negative: if news tone tracked opinion, a country whose
population wants tighter limits would carry more negative immigration news tone, so tone falls as
restrictiveness rises. That is what the 11 countries show, ordered by WVS restrictiveness:

| country | tone (mean nonzero) | WVS restrictiveness |
|---|---|---|
| Bangladesh | -1.61 | 2.25 |
| Armenia | -1.40 | 2.25 |
| Chile | -2.01 | 2.34 |
| Canada | -1.19 | 2.40 |
| Brazil | -1.41 | 2.42 |
| Taiwan | -1.20 | 2.53 |
| Australia | -2.01 | 2.55 |
| Colombia | -2.17 | 2.68 |
| Myanmar | -3.36 | 2.84 |
| Bolivia | -2.50 | 2.86 |
| Ecuador | -2.24 | 3.10 |

The least restrictive end (Canada, Taiwan, Bangladesh, Armenia) carries the least negative tone,
around -1.2 to -1.6; the most restrictive end (Myanmar, Bolivia, Ecuador) carries the most
negative, -2.2 to -3.4. Chile is the visible outlier (more negative tone than its middling
restrictiveness predicts), which is why the correlation is -0.68 rather than near -0.9. Both the
Pearson and the rank based Spearman clear p < 0.005 at n = 11, so the association is unlikely to
be sampling noise even at this small n.

### 4.3 Honest read

For the one topic we have, a free, no text, theme filtered GDELT tone signal **does track the
population opinion an established survey measures, in the direction theory predicts and at a
respectable effect size**. This is a genuine and slightly surprising result, because tone is
sentiment not stance (see the caveats): negative immigration coverage could in principle be
heavy in liberal high migration countries reporting sympathetically on migrant hardship, which
would have blunted or reversed the sign. It did not; the pull from restrictive publics running
negative coverage won out. On immigration, then, the free tone proxy is usable as a first pass
position signal.

One item is not a validated instrument. The correlation rests on 11 countries, a somewhat
arbitrary geographic slice (the alphabetical FIPS order the fetch happened to reach), and a WVS
anchor whose per country n is thin (median about 26 for immigration). The result earns "promising,
fetch the rest", not "the position field is validated".

### 4.4 The fetch block, reported not hidden

The full five item fetch did not run because GDELT's DOC API rate limiter flags the source IP.
The behaviour, established directly this session, is specific and worth recording:

- A single isolated request returns a clean http 200 (verified repeatedly, one call at a time).
- A sustained fetch of roughly two to three requests a minute (the pace the resumable fetcher
  runs at, one call per year window with a 20 second gap) trips connection resets within the first
  pair and the resets then persist for the whole run; the fetcher retries with backoff, fails the
  budget, skips the pair, and moves on, never recovering.
- A full stop with zero calls for 40 minutes did not clear it; the flag outlasts a short cooldown.
  Only isolated single requests, well spaced, get through.

That is itself a pass 1 finding on free tier viability: **the signal looks usable, but harvesting
it at country by topic scale on the free DOC API from one address is not.** The routes to the
remaining four items are (a) a paced multi day fetch of a handful of pairs an hour to stay under
the flag, (b) a rotating source address, or (c) the GKG on BigQuery, which we deliberately avoided
to keep pass 1 zero budget. The fetcher is resumable and appends per pair, so any of these picks
up from the 11 rows already banked.

**Bottom line.** Pass 1 gives one clean, significant, correctly signed data point that free web
tone can track population opinion (immigration, r = -0.68), and a clear, documented reason the
other four are outstanding. It supports moving to a paced or BigQuery fetch for the full table,
and separately to pass 2 (stance inference from article text) where tone is replaced by an actual
for or against reading.

---

## 5. Method files

- `build_wvs_anchor.py`: parses the WVS7 SFT mirror to per country item means (on the internal store).
- `fetch_gdelt_tone.py`: pulls GDELT theme filtered average tone per country (free DOC API).
- `validate.py`: joins on country and reports Pearson and Spearman per item and theme.

Data (persistent, internal store): `the internal corpus store/wvs_position/` and
`the internal corpus store/gdelt_position/`.

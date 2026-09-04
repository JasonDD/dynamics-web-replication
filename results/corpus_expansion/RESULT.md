# Corpus universe expansion: new coordinates for the empty map regions

*PUBLIC track. Built 2026-08-31 on the internal host (the box with internet; the control laptop is sandboxed). This pass
expands the corpus universe beyond what the character internal model already holds, to give the instrument new
coordinates where the map was empty. It finds, fetches (free, machine readable, login free, sampled) and
sample scores new corpora that fill the biggest gaps, and adds every one to the ledger. Held index before this
pass: `../../MASTER_CORPUS_INDEX.md` (~64 corpus directories) and `../../DATASET_ACQUISITION_LEDGER.md`.*

## What the gaps were

The held index was thin or empty in three ways. Under covered **languages and regions**: Southeast Asia
(parliaments PDF only), Central Asia and the Caucasus (Leipzig news and floor only), the **Pacific** (marked
ABSENT, floor only, no depth source), and the Horn of Africa. **Platforms** we lacked: the index carried
almost no social media voice beyond Weibo (Chinese) and the Reddit / StackExchange / darknet forums, so no
Twitter/X, no Mastodon, no Telegram, no YouTube comments. **Eras**: US press bulk (already held via
AmericanStories) and Project Gutenberg literary breadth (not held in English).

Breadth was the priority: one new language or platform beats more of one we already have.

## How it was fetched (login free, no `datasets` dependency)

The `datasets` library is not installed on the box, so nothing here depends on it. Languages come from
**FineWeb-2** (`HuggingFaceFW/fineweb-2`, ungated) read one parquet **row group at a time over HfFileSystem**:
a few megabytes per language, no full shard download. Platform and era sets come from their own parquet, jsonl
or csv files streamed to the sample size. Every row is normalised to `{id, text, region, platform, era,
source}` so the standard 8 axis scorer consumes it unchanged. Fetch script:
`../../acq_fetch_expansion.py` (runtime copy `the internal corpus store/fetch_expansion.py`). All data lives on
the internal store at `the internal corpus store/<name>/` per the house rule.

Every fetched corpus was verified real: 500 rows each, first record inspected to confirm it is native text and
not an HTML error page (short form platforms use a 40 character floor, web and books a 120 character floor).

## What was fetched (16 new corpora, 500 rows each)

| corpus | region / platform / era | source | rows | first record (confirmed real) |
|---|---|---|---|---|
| fw2_indonesian | Southeast Asia (Indonesia), web | FineWeb-2 `ind_Latn` | 500 | Indonesian film synopsis |
| fw2_thai | Southeast Asia (Thailand), web | FineWeb-2 `tha_Thai` | 500 | Thai social network commentary |
| fw2_vietnamese | Southeast Asia (Vietnam), web | FineWeb-2 `vie_Latn` | 500 | Vietnamese sales team note |
| fw2_filipino | Southeast Asia (Philippines), web | FineWeb-2 `fil_Latn` | 500 | Tagalog/English electronics forum |
| fw2_kazakh | Central Asia (Kazakhstan), web | FineWeb-2 `kaz_Cyrl` | 500 | Kazakh Red Cross/Red Crescent text |
| fw2_uzbek | Central Asia (Uzbekistan), web | FineWeb-2 `uzn_Latn` | 500 | Uzbek higher education news |
| fw2_samoan | Pacific (Samoa), web, was ABSENT | FineWeb-2 `smo_Latn` | 500 | Samoan development notice |
| fw2_maori | Pacific (Aotearoa NZ, te reo), web | FineWeb-2 `mri_Latn` | 500 | te reo Maori machine text notice |
| fw2_fijian | Pacific (Fiji), web, was ABSENT | FineWeb-2 `fij_Latn` | 500 | Fijian narrative |
| fw2_amharic | Horn of Africa (Ethiopia), web | FineWeb-2 `amh_Ethi` | 500 | Amharic history (Sumer, Ge'ez script) |
| fw2_somali | Horn of Africa (Somalia), web | FineWeb-2 `som_Latn` | 500 | Somali parliament news |
| twitter_sentiment140 | Twitter/X platform, 2009 | stanfordnlp/sentiment140 | 500 | classic tweet with @mention + link |
| mastodon_toots | Mastodon (fediverse) platform, 2024 | reapxdev/mastodon-scraper | 500 | political toot (HTML stripped) |
| telegram_channels | Telegram platform, 2022-2024 | Meduzka/telegram_data_war_in_ukraine | 500 | Russian language channel broadcast |
| youtube_comments | YouTube platform, 2024 | DinoResearch/YouTube-Comment-Master-2024-v1 | 500 | video comment |
| gutenberg_english | deep time literary (book era) | sedthh/gutenberg_english | 500 | US Bill of Rights text |

## The new coordinates (8 axis sample scored means)

Scored on the same instrument as the whole series: the free an internal model on ``, same system prompt and
vocabulary line as `score_turns.py`, self queued behind the running job at 6 workers. Each mean is over up to
150 sampled records per corpus. Axes: **rigour** (unsourced to scholarly), **depth** (superficial to expert),
**originality** (rehashed to primary source), **candour** (opaque to transparent), **affect** (neutral to
sensational), **commercial_drive** (reference to hard sell), **stance** (balanced to polemical), **register**
(institutional to conversational).

| corpus | region / platform / era | n | rig | dep | ori | can | aff | com | sta | reg | character reading |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fw2_indonesian | Indonesia / web | 150 | 0.54 | 0.52 | 0.39 | 0.80 | 0.56 | 0.44 | 0.51 | 0.50 | measured web prose |
| fw2_thai | Thailand / web | 149 | 0.60 | 0.56 | 0.42 | 0.82 | 0.53 | 0.51 | 0.50 | 0.52 | measured, fairly rigorous web prose |
| fw2_vietnamese | Vietnam / web | 150 | 0.61 | 0.59 | 0.45 | 0.78 | 0.55 | 0.42 | 0.54 | 0.48 | rigorous, expository web prose |
| fw2_filipino | Philippines / web | 150 | 0.37 | 0.40 | 0.49 | 0.82 | 0.72 | 0.39 | 0.47 | 0.42 | casual, affective forum voice |
| fw2_kazakh | Kazakhstan / web | 132 | 0.67 | 0.62 | 0.43 | 0.80 | 0.48 | 0.26 | 0.52 | 0.54 | formal, encyclopedic, low sell |
| fw2_uzbek | Uzbekistan / web | 150 | 0.69 | 0.67 | 0.49 | 0.81 | 0.50 | 0.29 | 0.54 | 0.55 | most rigorous of the new languages, low sell |
| fw2_samoan | Pacific Samoa / web | 150 | 0.48 | 0.54 | 0.38 | 0.75 | 0.64 | 0.47 | 0.65 | 0.44 | affective and notably polemical |
| fw2_maori | Pacific Aotearoa, te reo / web | 150 | 0.51 | 0.53 | 0.40 | 0.76 | 0.58 | 0.32 | 0.58 | 0.43 | affective, engaged stance |
| fw2_fijian | Pacific Fiji / web | 150 | 0.46 | 0.49 | 0.35 | 0.69 | 0.67 | 0.37 | 0.55 | 0.39 | affective, conversational, low rigour |
| fw2_amharic | Ethiopia Horn / web | 112 | 0.51 | 0.52 | 0.43 | 0.77 | 0.57 | 0.44 | 0.58 | 0.40 | engaged, polemical, institutional register |
| fw2_somali | Somalia Horn / web | 150 | 0.56 | 0.58 | 0.42 | 0.79 | 0.52 | 0.32 | 0.58 | 0.47 | engaged news voice, polemical |
| twitter_sentiment140 | Twitter/X / 2009 | 150 | 0.23 | 0.29 | 0.46 | 0.87 | 0.78 | 0.12 | 0.19 | 0.20 | emotive, low rigour, conversational blurt |
| mastodon_toots | Mastodon fediverse / 2024 | 150 | 0.39 | 0.44 | 0.62 | 0.81 | 0.66 | 0.28 | 0.37 | 0.32 | personal, high originality, opinionated |
| telegram_channels | Telegram channels / 2022-2024 | 150 | 0.49 | 0.50 | 0.48 | 0.73 | 0.50 | 0.25 | 0.56 | 0.44 | broadcast, polemical, moderate rigour |
| youtube_comments | YouTube / 2024 | 150 | 0.14 | 0.16 | 0.59 | 0.80 | 0.84 | 0.13 | 0.13 | 0.13 | the sensational corner: lowest rigour+depth, highest affect |
| gutenberg_english | book / deep time literary | 150 | 0.72 | 0.66 | 0.47 | 0.78 | 0.50 | 0.20 | 0.47 | 0.43 | the scholarly corner: highest rigour+depth, low sell |

**What the new coordinates reveal.** The platforms and the book era stake out the two ends of the map the
held corpus was thin on. **YouTube comments** and **Twitter/X** land in the sensational corner: lowest rigour
(0.14, 0.23) and depth, highest affect (0.84, 0.78), lowest commercial drive and most conversational register.
**Gutenberg** anchors the opposite scholarly corner: highest rigour (0.72) and depth (0.66). **Mastodon** sits
apart with the highest originality (0.62), reading as personal first hand opinion rather than rehash. The
eleven native web languages cluster in the measured middle, with two real spreads worth noting: Central Asian
web (Kazakh, Uzbek) reads most rigorous and least commercial of the languages, while the Pacific and Horn
languages (Fijian, Samoan, Filipino, Amharic) read more affective and more polemical. Every one of the sixteen
is a position the map did not have before.


**Honest caveat on cross lingual scoring.** The 7B scorer is strongest in English and the higher resource
languages. For the low resource Pacific and Horn languages (Samoan, Fijian, Maori, Amharic, Somali) the axis
reads are noisier, exactly as the series' existing cross lingual work already assumes. The coordinate is a
real position on the map, read with a wider error bar, not a precise point. This is stated, not hidden.

## What remains blocked (the wall named)

- **Southeast Asian parliaments** (Indonesia DPR, Philippines Congress, Vietnam, Thailand): PDF only, no clean
  bulk text. The FineWeb-2 native web corpora above are the realistic decision free substitute; the *decision*
  corpus for the region stays blocked.
- **Pacific parliaments**: no open dump found. The Pacific now has a native web coordinate (Samoan, Fijian,
  Maori) but still no decision corpus, genuinely floor only for parliamentary voice.
- **Trove (Australia)**: needs a free API key (401 keyless). Papers Past NZ fills the Australasia OCR role.
- **Central Asian / Caucasus parliaments**: none open; the region moves off floor only for native web
  (Kazakh, Uzbek) but has no decision corpus.
- **Change.org, Meta Ad Library, Yelp, GoFundMe**: login / identity / ToS walls (unchanged from prior passes).

## Biggest remaining gaps after this pass

1. **Decision corpora for the newly added regions.** Southeast Asia, Central Asia and the Pacific now have
   native *discourse* (web/social) but no *decision* corpus (a real human choice tied to a text). The
   parliaments are PDF only and the petition platforms are login walled. This is the sharpest remaining gap.
2. **The Pacific parliamentary voice.** Web text now exists; Hansard does not, in open form.
3. **Deep time outside the Anglosphere and Europe.** Latin America (Peru 1821-1979 debates), the Caribbean
   (Jamaica Hansard is catalogue only) and Central Asia have no open deep time source.
4. **More platforms still absent**: Discord, WhatsApp (private by nature), TikTok comments, and non English
   Twitter/X at scale.

## Files

- Fetch: `../../acq_fetch_expansion.py`
- Scorer (canonical, unchanged): `../../results/knesset_attribute/score_turns.py` (runtime copy
  `the internal corpus store/score_turns.py`)
- Scoring orchestrator: `the internal corpus store/score_expansion.sh`
- Means: `the internal corpus store/expansion_means.json`
- Per corpus data + scores: `the internal corpus store/<name>/{<name>.jsonl,char.jsonl}`
- Ledger rows: `../../DATASET_ACQUISITION_LEDGER.md` (fifth pass); index: `../../MASTER_CORPUS_INDEX.md`

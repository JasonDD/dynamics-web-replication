# Dataset acquisition ledger — DYNAMICS-WEB

*Closes the standing "get ALL the datasets and report back" task. This walks every concretely named
corpus in `DATASET_CATALOGUE_free_human_persuasion.md` and `DATASET_CATALOGUE_original_language.md`,
records its real status, and where fetchable actually pulls the file to disk. Built 2026-08-30. All data
lives on the NAS at `/mnt/nas/kronaxis/corpora/` (persistent, per house rule). Status legend:
**HELD** already on disk before this run · **FETCHED** pulled in full this run · **SAMPLED** a documented
representative sample pulled (whole corpus too large for zero budget mirror) · **BLOCKED** no clean free
route (login wall, geo block, PDF only, no open dump), reason stated.*

*Every FETCHED/SAMPLED row was verified real: row count above zero and the first record inspected to
confirm it is data, not an HTML error page. Fetch scripts committed beside this ledger
(`acq_fetch_hf.py`, `acq_fetch_hf2.py`, `acq_fetch_hf3.py`, `acq_fetch_curl.sh`, `acq_fetch_curl2.sh`,
`acq_fetch_curl3.sh`; the third pass deepening scripts `acq_fetch_openiti.sh`, `acq_fetch_nordic.py`,
`acq_fetch_papers_past.sh`, `acq_fetch_pap.sh`, `acq_fetch_knesset.py`; and the fourth pass
`acq_fetch_wave4_hf.py`, `acq_fetch_wave4_curl.sh`). Updated 2026-08-30 across four passes: the second
pulled the full Upworthy archive plus the previously deferred corpora; the third deepened the thin regions
(OpenITI, Knesset, Pan-African Parliament, Nordic banks, Papers Past NZ, Argentina); the fourth added the
register/genre/deception layers (private letters, sacred texts, proverbs, spoken transcripts, deception).
No row is left DEFERRED — every named dataset is HELD, FETCHED, SAMPLED, or BLOCKED with the wall stated.*

---

## Coverage summary (the headline numbers)

These began as the concretely named corpora in both catalogues (~71 distinct datasets; the pure meta hubs —
HuggingFace by language, CLARIN, Universal Dependencies, Lanfrica, OPUS/OSCAR/CC100/mC4, the awesome lists
— are the enumerable long tail, not single datasets), extended over four passes by the deepening fetches for
the thin regions and by the register/genre/deception layers. The tables below now hold **99 rows**: a few
rows bundle several small closely related corpora (e.g. the CJK forums, the Korean assembly/NIKL set), and
Upworthy takes two rows for its full archive and its derived scored subset. Counting at the auditable row
level:

- **Held on disk now: 83 rows** (20 held from prior work) plus **63 fetched or sampled by this effort**
  (25 in the first pass, 8 in the second, 7 in the third deepening pass, 7 in the fourth register/deception
  pass, and **16 in the fifth corpus expansion pass** (the empty map regions): 11 native web languages via
  FineWeb-2 covering Southeast Asia, Central Asia, the Pacific and the Horn of Africa, four social platforms
  Twitter/Mastodon/Telegram/YouTube, and Project Gutenberg English for deep time literary register). Every held
  row was verified real (row count above zero, first record inspected). ParlSpeech V2 was
  the last to land: the 8.4GB whole dataset zip kept truncating on the slow Harvard Dataverse host, so one
  full country file (Czech, `Corp_PSP_V2.rds`, 387MB, valid RDS) was pulled per file instead — SAMPLED, and
  Europe is already RICH via ParlaMint regardless.
- **Fetched or sampled in the third pass (7):** OpenITI (premodern Arabic GitHub slice), the Knesset Corpus
  (Hebrew), the Pan-African Parliament Hansard (continent wide decision corpus in Akoma Ntoso), the Norwegian
  Colossal Corpus and Danish Gigaword (Nordic banks), Papers Past New Zealand (historical press incl te reo
  Maori), and the Argentina Chamber session index.
- **Fetched or sampled in the fourth pass (7):** Darwin correspondence (private letters), the multilingual
  Bible and the Quran (sacred texts), Wiktionary proverbs (six languages), CORAAL (spoken transcribed
  register), and two deception sets — the Ott deceptive-opinion-spam corpus and a phishing email corpus.
- **Still blocked: 32 rows** — all with the specific wall stated (login, geo, PDF only, no single open
  dump, a download form, a needed API key, a Cloudflare challenge, or a host unreachable from our network).
  **No row remains DEFERRED or FETCHING** — every named dataset is HELD, FETCHED, SAMPLED, or BLOCKED with a
  reason.

Total corpora footprint on NAS after this pass: **~65 GB** across 64 dataset directories.

---

## Region / family tables

### Global floor (every country, one genre)
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| UN General Debate Corpus | 190+ countries | diplomatic speech | Harvard DVN/0TJX8Y | HELD | ~10,952 | `ungd/` (409M) |
| ccTLD web corpus (`domain_char8_expanded`) | every ccTLD | web text | internal | HELD | 2.6M domains | Postgres (not in corpora/) |

### Anglo (court / parliament / debate / founding / behavioural)
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| Old Bailey Online | UK | court verdict | oldbaileyonline.org | HELD | scored | `oldbailey/` |
| UK Parliament petitions | UK | petition/signature | petition.parliament.uk | HELD | full+clusters | `uk_petitions/` (128M) |
| Federalist Papers | US | founding argument | Gutenberg 1404 | FETCHED | 85 essays (1.19MB) | `federalist/federalist.txt` |
| Super-SCOTUS / ConvoKit supreme | US | oral argument + ruling | ConvoKit | FETCHED | 8 corpus files (7.9GB) | `supreme/supreme-corpus/` |
| ChangeMyView Winning Arguments | US/UK web | delta = view changed | ConvoKit (Tan 2016) | HELD | scored | `cmv_winning_args/` (422M) |
| UKPConvArg1 (Habernal) | English | crowd convincingness | UKPLab github | FETCHED | 232 files | `ukpconvarg/` (154M) |
| IBM argument-quality-30k | English | crowd arg quality | ibm/argument_quality_ranking_30k | FETCHED | 20,974 | `ibm_argq_30k/` |
| Intelligence Squared (IQ2) | US/UK | audience before/after vote | ConvoKit iq2 | FETCHED | 12 corpus files | `iq2/iq2-corpus/` |
| OpenDebateEvidence | English | competitive debate args | Yusuf5/OpenCaselist | SAMPLED | 5,000 | `opendebateevidence/` (52M) |
| StackExchange arguments | English | Q&A votes | SE dumps | HELD | scored | `stackexchange_args/` (662M) |
| Upworthy Research Archive (FULL) | US | A/B headline clicks | OSF jd64p | HELD (full) | 291,790 headline packages across 33,129 A/B tests | `upworthy_full/` (4 CSVs: confirmatory 149,187 + exploratory 31,580 + holdout 31,833 + undeployed 79,190) |
| Upworthy scored subset (derived) | US | A/B headline clicks | internal | HELD | 340 (scored working subset) | `causal/` |
| DonorsChoose | US | donation outcome | udayl/donors_choose_data | FETCHED | 159,248 | `donorschoose/` (345M) |
| Amazon Reviews 2023 (McAuley) | US | review + helpful votes | mcauleylab.ucsd.edu | SAMPLED | 20,000 (All_Beauty) | `amazon_reviews/` |
| Persuasion for Good | US web | donation, real money | github ohyj1002 | HELD | 1,017 in | `human_persuasion/persuasionforgood` |
| Kickstarter | US/global | blurb -> funding | Kaggle/ICPSR 38050 | HELD | 6,000 in | `human_persuasion/kickstarter` |
| PANDORA / MBTI | Reddit | personality traits | Kaggle/PANDORA | HELD | scored | `pandora/` (39M) |
| DDO debate.org | US web | outcome + voter ideology | Durmus & Cardie | HELD | full | `ddo/` (412M) |
| IRA Russian troll tweets | US targeted | influence operation, typed | fivethirtyeight | SAMPLED | 494,413 (2/13 files) | `ira_troll/` (181M) |
| LIAR | US | 6-way truthfulness | UCSB (ucsbnlp/liar) | FETCHED | 10,269 | `liar/*.tsv` |

### Germanic / Romance / Slavic — Europe (native, multilingual)
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| ParlaMint | 29 European countries | parliament + party/orientation | CLARIN | HELD | full | `parlamint/` (34G) |
| French-PD-Newspapers (Gallica/BnF) | France | deep time press | PleIAs/French-PD-Newspapers | SAMPLED | 3,000 editions | `french_pd_news/` (469M) |
| ECHR cases (via lex_glue ecthr_a) | Europe | court ruling/violation | coastalcph/lex_glue | FETCHED | 9,000 | `echr/` (86M) |
| Norwegian Colossal Corpus (NCC) | Norway (Nordic) | native text, dated (newspaper OCR + more) | NbAiLab/NCC | SAMPLED | 8,000 | `ncc_norwegian/ncc_norwegian.jsonl` (34M) |
| Danish Gigaword | Denmark (Nordic) | native text, dated | danish-foundation-models/danish-gigaword | SAMPLED | 8,000 | `danish_gigaword/danish_gigaword.jsonl` (180M) |
| Swedish (Sprakbanken) | Sweden (Nordic) | native text | spraakbanken.gu.se | BLOCKED | 0 | per resource download URLs, no single clean bulk endpoint reachable; Nordic covered by NCC + Danish Gigaword |
| Icelandic Gigaword (IGC) | Iceland (Nordic) | native text | CLARIN | BLOCKED | 0 | CLARIN deposit, no clean keyless bulk; Nordic covered by NCC + Danish Gigaword |
| Europarl | 21 EU languages | parliament parallel | Helsinki-NLP/europarl | SAMPLED | 3,000 (de-en pair) | `europarl/europarl.jsonl` |
| ParlSpeech V2 | 9 democracies (Czech held) | parliament + speaker meta | Harvard DVN/L4OAKN | SAMPLED | Corp_PSP_V2.rds (Czech, full 387MB, valid RDS) + release note | `parlspeech/Corp_PSP_V2.rds` — the 8.4GB whole dataset zip kept truncating on the slow host, so one full country .rds was pulled per file instead; Europe already RICH via ParlaMint |
| ParlaSpeech (HR/SR/CZ/PL) | Slavic | spoken parliament | CLARIN.SI | BLOCKED | 0 | audio heavy spoken corpus (hundreds of GB per language), no clean small text dump; Slavic covered by ParlaMint + ParlSpeech |
| Russian State Duma transcripts | Russia | post Soviet parliament | github a-r-ya | BLOCKED | 0 | repo path 404; code only/scrape, dekoder mirror needs auth |
| Archives Parlementaires (Fr Revolution) | France | revolutionary debate | Stanford FRDA | BLOCKED | 0 | data behind per volume Stanford purls, no single bulk endpoint; French covered by Europarl + French-PD |
| Assemblée Nationale open data | France | parliament XML | data.assemblee-nationale.fr | BLOCKED | 0 | bulk split per session/legislature XML, no single clean dump; French covered by Europarl + ParlSpeech + French-PD |
| Persian daily news (native Persian) | Iran | native news discourse | RohanAiLab/persian_daily_news | SAMPLED | 5,000 | `persian_daily_news/` (21M) |
| Uppsala Persian Corpus / Bijankhan | Iran | tagged native Persian | stp.lingfil.uu.se | BLOCKED | 0 | host unreachable 2026-08-30; Persian covered by persian_daily_news |
| Taiga (Russian webcorpus) | Russia | blogs/social, native | HF script (removed) | BLOCKED | 0 | HF loader removed, no parquet convert; github alt exists |
| Turkish TS Corpus | Turkey | 1.3bn tokens native | tscorpus.com | BLOCKED | 0 | registration wall |

### Africa (Masakhane + Hansards)
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| Pan-African Parliament Hansard | pan African (AU) | continent wide parliament (decision) | opendata.pap.au.int (Akoma Ntoso) | FETCHED | 20 full sittings 2010-2019 | `pan_african_parliament/pap_hansard.jsonl` (22M) |
| MasakhaNEWS | 16 African langs | human annotated news topic | masakhane/masakhanews | FETCHED | 21,734 | `masakhanews/` (69M) |
| MasakhaNER2 | 20 African langs | named entity, native | masakhane/masakhaner2 | FETCHED | 106,964 | `masakhaner2/` (37M) |
| MasakhaPOS | 20 African langs | POS, native | masakhane-io github | FETCHED | 109 data files | `masakhapos/` (34M) |
| AfriQA | 10 African langs | cross lingual QA | masakhane/afriqa | FETCHED | 4,304 | `afriqa/` |
| AfriSenti | 15 African langs | tweet sentiment (human) | masakhane/afrisenti | FETCHED | 98,974 | `afrisenti/` (15M) |
| Kencorpus (Swahili/Dholuo/Luhya) | Kenya | native text | Kencorpus/KenCorpus_text | FETCHED | 3,787 | `kencorpus/` (18M) |
| FineWeb-2 Amharic (`amh_Ethi`) | Ethiopia (Horn) | native web text (Ge'ez script) | HuggingFaceFW/fineweb-2 | SAMPLED | 500 | `fw2_amharic/fw2_amharic.jsonl` (Horn of Africa depth beyond Masakhane) |
| FineWeb-2 Somali (`som_Latn`) | Somalia (Horn) | native web text | HuggingFaceFW/fineweb-2 | SAMPLED | 500 | `fw2_somali/fw2_somali.jsonl` (first Somali coordinate) |
| Kenya National Assembly Hansard | Kenya | parliament | hansardna.parliament.go.ke | HELD | 1,500 | `natparl/kenya.jsonl` |
| South Africa Hansard | South Africa | parliament | parliament.gov.za | HELD | 1,500 | `natparl/south_africa.jsonl` |
| Ghana Parliament Hansard | Ghana | parliament | ghana parliament | HELD | 1,500 | `natparl/ghana.jsonl` |
| Nigeria NASS Hansard | Nigeria | parliament | nass | HELD | 1,500 | `natparl/nigeria.jsonl` |
| Zambia Hansard | Zambia | parliament | parliament.gov.zm | HELD | 1,500 | `natparl/zambia.jsonl` |
| Zimbabwe Hansard | Zimbabwe | parliament | parlzim | HELD | 1,500 | `natparl/zimbabwe.jsonl` |

### Middle East / Islamicate
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| OpenITI (premodern Arabic/Persian) | Arabic/Persian | deep time rhetoric | github.com/OpenITI (0300AH + 0450AH) | SAMPLED | 150 texts | `openiti/openiti_sample.jsonl` — full corpus ~4,300 texts across OpenITI/* repos; Zenodo API 403, so a documented GitHub slice of two rich Hijri centuries |
| Knesset Corpus (Hebrew) | Israel | parliament + speaker demographics | HaifaCLGroup/KnessetCorpus | SAMPLED | 365 full plenary protocols (each a complete session with speaker tagged sentences) | `knesset_corpus/knesset_corpus.jsonl` (5.5G) — native decision corpus, ~384M tokens full |
| Daleel 2026 (QatarDebate) | Arabic | argument mining shared task | qatardebate | BLOCKED | 0 | shared task registration |
| Oman Royal Speeches Corpus | Oman | state persuasion | academic | BLOCKED | 0 | academic request only |

### South / East Asia
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| India Lok Sabha + Rajya Sabha | India | parliament | Zenodo 18146342 | FETCHED | 3 xlsx (Lok+Rajya+special) | `india_loksabha/` (20M) |
| Korea National Assembly | Korea | parliament | prior fetch | HELD | 1,500 | `natparl/korea.jsonl` |
| Malaysia parliament | Malaysia | parliament | prior fetch | HELD | 1,500 | `natparl/malaysia.jsonl` |
| Weibo sentiment (native Chinese) | China | social sentiment (human) | mljucyyyy/weibo_sentiment | SAMPLED | 20,000 | `weibo_sentiment/` (9.8M) |
| Zhanguo Ce + Perseus (classical) | China / Greece-Rome | ancient oratory | ctext / perseus | HELD | scored | `classical/` (2M) |
| Aozora Bunko | Japan | deep time literary, native | aozora.gr.jp | SAMPLED | 19,503-work index | `aozora/` — bulk texts via github aozorabunko |
| Japan Diet proceedings | Japan | parliament | kokkai.ndl.go.jp API | FETCHED | 800 speeches | `japan_diet/japan_diet.jsonl` |
| YACIS (5bn Japanese blogs) | Japan | affect-annotated blogs | academic | BLOCKED | 0 | academic request |
| 2channel/5channel, DC Inside, Baidu Tieba, People's Daily | JP/KR/CN | forum/social native | — | BLOCKED | 0 | no clean open dump; scrape only |
| KOGENT / assemblykor / NIKL (Korean) | Korea | assembly / native | NIKL / CRAN | BLOCKED | 0 | NIKL login; Korea covered by natparl |
| IndicCorpV2 (IndicNLP / AI4Bharat) | 11+ Indian langs | native corpora | ai4bharat/IndicCorpV2 | SAMPLED | 8,000 | `indiccorp_v2/indiccorp_v2.jsonl` |

### Southeast Asia (the standing gap)
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| FineWeb-2 Indonesian (`ind_Latn`) | Indonesia | native web text | HuggingFaceFW/fineweb-2 | SAMPLED | 500 (first row group) | `fw2_indonesian/fw2_indonesian.jsonl` |
| FineWeb-2 Thai (`tha_Thai`) | Thailand | native web text | HuggingFaceFW/fineweb-2 | SAMPLED | 500 | `fw2_thai/fw2_thai.jsonl` |
| FineWeb-2 Vietnamese (`vie_Latn`) | Vietnam | native web text | HuggingFaceFW/fineweb-2 | SAMPLED | 500 | `fw2_vietnamese/fw2_vietnamese.jsonl` |
| FineWeb-2 Filipino/Tagalog (`fil_Latn`) | Philippines | native web text | HuggingFaceFW/fineweb-2 | SAMPLED | 500 | `fw2_filipino/fw2_filipino.jsonl` |
| Indonesia DPR parliament | Indonesia | parliament | dpr.go.id | BLOCKED | 0 | PDF only, no clean bulk text (rechecked 2026-08-30) |
| Philippines Congress | Philippines | parliament | congress.gov.ph | BLOCKED | 0 | PDF only / geo throttled (rechecked 2026-08-30) |
| Vietnam / Thailand parliaments | VN/TH | parliament | — | BLOCKED | 0 | PDF only |

### Australasia / Pacific
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| Papers Past (NZ, via DigitalNZ) | New Zealand | historical press, dated (incl te reo Maori) | api.digitalnz.org v3 (keyless) | FETCHED | 1,000 records (10 decades 1850-1940) | `papers_past_nz/papers_past_nz.jsonl` — metadata + description; full per article OCR needs the site key |
| Trove (Australia) | Australia | historical press OCR | api.trove.nla.gov.au v3 | BLOCKED | 0 | needs a free API key (401 keyless); record as BLOCKED-needs-key per instruction; Papers Past fills the Australasia OCR role |
| FineWeb-2 Samoan (`smo_Latn`) | Samoa (Pacific) | native web text | HuggingFaceFW/fineweb-2 | SAMPLED | 500 | `fw2_samoan/fw2_samoan.jsonl` (Pacific was ABSENT, floor only, before this) |
| FineWeb-2 Maori (`mri_Latn`) | Aotearoa NZ (te reo) | native web text | HuggingFaceFW/fineweb-2 | SAMPLED | 500 | `fw2_maori/fw2_maori.jsonl` (native te reo Maori discourse, not press OCR) |
| FineWeb-2 Fijian (`fij_Latn`) | Fiji (Pacific) | native web text | HuggingFaceFW/fineweb-2 | SAMPLED | 500 | `fw2_fijian/fw2_fijian.jsonl` (first Fijian coordinate) |

### Central Asia (was floor only)
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| FineWeb-2 Kazakh (`kaz_Cyrl`) | Kazakhstan | native web text | HuggingFaceFW/fineweb-2 | SAMPLED | 500 | `fw2_kazakh/fw2_kazakh.jsonl` (region was Leipzig news / floor only) |
| FineWeb-2 Uzbek (`uzn_Latn`) | Uzbekistan | native web text | HuggingFaceFW/fineweb-2 | SAMPLED | 500 | `fw2_uzbek/fw2_uzbek.jsonl` (first Uzbek coordinate) |

### Americas (beyond Anglo)
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| Brazil Chamber of Deputies | Brazil | parliament speech + vote | dadosabertos.camara.leg.br API | SAMPLED | ~200 speeches (8 deputies, L57) | `brazil_chamber/discursos_sample.json` |
| Argentina Chamber of Deputies (Diarios de Sesiones) | Argentina | parliament session index, dated | datos.hcdn.gob.ar (CKAN) | FETCHED | 577 sessions (index; verbatim text is PDF) | `argentina_congress/diarios_de_sesiones.csv` |
| Chile Congress | Chile | parliament | opendata.camara.cl / senado.cl | BLOCKED | 0 | camara host unreachable from our network; senado wspublico exposes bills/votes not speech text |
| Mexico Chamber of Deputies | Mexico | parliament (Diario de los Debates) | diputados.gob.mx | BLOCKED | 0 | host unreachable from our network; debates are PDF only |
| Congressional Record / ConSpeak | US | parliament, speaker meta | Gentzkow-Shapiro-Taddy (Stanford) | FETCHED | hein-daily.zip 2.8GB (speeches_*.txt inside) | `us_congress/hein-daily.zip` |
| American Presidency Project | US | presidential rhetoric | presidency.ucsb.edu | BLOCKED | 0 | scrape only, no bulk API or open dump |
| Latin American Legislators | 18 countries | legislator observations | academic | BLOCKED | 0 | academic replication file, no open bulk endpoint; covered by Brazil Chamber + ParlSpeech |
| Chronicling America (via AmericanStories) | US multilingual | deep time press | dell-research-harvard/AmericanStories | SAMPLED | 8,000 articles (year 1900) | `american_stories/american_stories.jsonl` |

### Cross lingual persuasion / argument + speaker rating + petitions
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| Historical periodicals (internal histchar) | English deep time | article persuasion char | internal | HELD | scored | `histchar/` |
| TED talks (persuasiveness ratings) | global | viewer "persuasive" rating | data.world owentemple | BLOCKED | 0 | ratings behind data.world login; HF transcript loader removed |
| Change.org / We-the-People | 6 countries | petition + signature series | datalumos / Kaggle | BLOCKED | 0 | datalumos/ICPSR login (UK petitions held separately) |
| Wikipedia Articles for Deletion (AfD) | English | deliberation -> consensus | ConvoKit | FETCHED | 3,295,340 utterances | `wiki_afd/wiki-articles-for-deletion-corpus/` |
| GoFundMe | US | campaign text -> funds | — | BLOCKED | 0 | no canonical open dump |
| Yelp Open Dataset | US | review + behaviour | yelp.com/dataset | BLOCKED | 0 | ToS click through / login |
| Meta Ad Library | global | political ad + spend | facebook.com/ads/library | BLOCKED | 0 | API + identity verification |
| Multilingual Argument Mining (Toledo/Ronen) | multi | human arguments | IBM research | BLOCKED | 0 | IBM Project Debater download form; ibm_argq_30k held as the IBM argument anchor |
| IBM ArgsEN / EviEN | English | stance + evidence quality | IBM research | BLOCKED | 0 | IBM Project Debater download form; ibm_argq_30k held as the IBM argument anchor |
| SemEval persuasion-techniques | 9+ langs | technique labels | SemEval-2023 task 3 | BLOCKED | 0 | shared task registration |

---

### Register, genre and deception layers (fourth pass — the unperformed voice, sacred, spoken, deception)
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| Darwin correspondence (Life and Letters) | UK | private letters (trait vs performance) | Gutenberg 2087/2088/2739/2740 | FETCHED | 4 volumes (~88k lines) | `darwin_letters/` |
| Founders Online | US | founders' letters | founders.archives.gov API | BLOCKED | 0 | Cloudflare 202 challenge on the API; no keyless bulk |
| EMLO / Van Gogh letters | EU | private letters | emlo.bodleian / vangoghletters.org | BLOCKED | 0 | EMLO is metadata only; Van Gogh is JS rendered; Darwin fills the letters role |
| Bible (multilingual parallel) | 8 language pairs | sacred text (persuasion units) | davidstap/biblenlp-corpus-mmteb | SAMPLED | 8,846 verses (eng paired with fra/spa/deu/rus/arb/cmn/swh/hin) | `bible_multilingual/bible_multilingual.jsonl` |
| Quran (English translations) | Arabic/English | sacred text | M-AI-C/quran_en_translations | FETCHED | 6,235 | `quran/quran.jsonl` |
| Multilingual proverbs | en/es/de (fr/ru/zh attempted) | proverbs (compressed persuasion) | Wiktionary categorymembers API | FETCHED | 983 | `proverbs_multilingual/proverbs.jsonl` |
| CORAAL sociolinguistic interviews | US (African American Language) | spoken transcribed register | lingtools.uoregon.edu | FETCHED | 302 transcripts | `coraal_spoken/coraal_transcripts.jsonl` |
| Ott deceptive-opinion-spam | US | deception gold label (truthful/deceptive) + polarity | Lots-of-LoRAs task902/task903 | FETCHED | 2,862 (1,433 carry the truthful/deceptive label) | `opspam_deceptive/opspam_deceptive.jsonl` |
| Phishing email corpus | English | deception (phishing vs legitimate) | zefang-liu/phishing-email-dataset | FETCHED | 18,650 | `phishing_email/phishing_email.jsonl` |

### Social media platforms (the platform gap, corpus expansion pass)
*The held index had almost no social platform voice beyond Weibo (Chinese) and the Reddit/StackExchange/darknet
forums. These add four new platform coordinates.*
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| Sentiment140 (Twitter/X) | US/EN | microblog post (classic academic set) | stanfordnlp/sentiment140 | SAMPLED | 500 (of 1.6M) | `twitter_sentiment140/twitter_sentiment140.jsonl` |
| Mastodon public toots | EN/multi | fediverse (decentralised) post | reapxdev/mastodon-scraper | SAMPLED | 500 | `mastodon_toots/mastodon_toots.jsonl` (HTML stripped from `content`) |
| Telegram channel messages | UA/RU | public broadcast channel post | Meduzka/telegram_data_war_in_ukraine | SAMPLED | 500 | `telegram_channels/telegram_channels.jsonl` (Ukraine war news channels) |
| YouTube comments | EN/multi | video comment | DinoResearch/YouTube-Comment-Master-2024-v1 | SAMPLED | 500 | `youtube_comments/youtube_comments.jsonl` |

### Deep time literary breadth (era)
*Chronicling America US press bulk is already held via AmericanStories (see Americas table). Gutenberg adds the
public domain book register the index lacked in English.*
| Dataset | Region | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| Project Gutenberg English | EN | public domain book (deep time literary) | sedthh/gutenberg_english | SAMPLED | 500 | `gutenberg_english/gutenberg_english.jsonl` |

### Modality and register breadth (sixth pass — spoken, creative, technical, transactional)
*The index was almost all written argument, parliament and news. These fill the four register regions the
character instrument had barely seen: spoken (conversational and prepared), creative (dialogue, verse,
narrative prose), technical/professional (abstracts, contracts, patents) and customer/transactional (jobs,
products, complaints). Song lyrics deliberately excluded (copyright). Each is sample scored on the eight
axes and placed against the held corpora — see `results/modality_domain_breadth/RESULT.md`.*
| Dataset | Register | Construct | Source | Status | Rows | Path |
|---|---|---|---|---|---|---|
| SCOTUS oral arguments | spoken (adversarial) | oral-argument turns | ConvoKit supreme (held) | FETCHED | 600 | `scotus_oral_spoken/` |
| TED talks | spoken (prepared monologue) | transcript passages | Helsinki-NLP/opus_tedtalks (EN side) | SAMPLED | 600 | `ted_talks_spoken/` |
| Podcast transcripts | spoken (conversational) | STEMM podcast transcript | shuyuej/CC-BY-STEMM-Podcast-Transcripts | SAMPLED | 600 | `podcast_spoken/` |
| Cornell Movie-Dialogs | creative (dialogue) | film/TV dialogue chunks | cs.cornell.edu (Danescu) | FETCHED | 600 | `movie_dialogs_creative/` |
| Gutenberg Poetry Corpus | creative (verse) | public-domain verse excerpts | static.decontextualize.com (Parrish) | SAMPLED | 600 | `poetry_creative/` |
| Gutenberg fiction openings | creative (narrative prose) | novel opening passages | sedthh/gutenberg_english | SAMPLED | 699 | `fiction_openings_creative/` |
| arXiv abstracts | technical (research) | abstracts, 6 categories | export.arxiv.org API | FETCHED | 720 | `arxiv_abstracts_technical/` |
| PubMed abstracts | technical (biomedical) | abstracts | NCBI E-utilities | FETCHED | 585 | `pubmed_abstracts_technical/` |
| CUAD contracts | technical (legal) | commercial contract text | theatticusproject/cuad-qa | SAMPLED | 406 | `contracts_cuad_technical/` |
| Patent abstracts | technical (patent) | patent abstracts | ccdv/patent-classification | SAMPLED | 600 | `patent_abstracts_technical/` |
| Job postings | transactional (recruitment) | job descriptions | cnamuangtoun/resume-job-description-fit | SAMPLED | 256 | `job_postings_transactional/` |
| Product descriptions | transactional (e-commerce, non-Amazon) | product marketing copy | llm-wizard/Product-Descriptions-and-Ads | SAMPLED | 90 (thin — small source) | `product_descriptions_transactional/` |
| Customer complaints | transactional (grievance) | consumer complaint narrative | milesbutler/consumer_complaints (CFPB) | SAMPLED | 600 | `complaints_transactional/` |

Blocked/degraded on this pass, wall stated: TED via HF (`gigant/ted_talks`, `Rogendo/Ted-Talks`,
`bigscience-data/roots_en_ted_talks_iwslt` all 404 or gated — pulled the English side of the OPUS TED
parallel corpus instead); podcast `SamAct/podcast_transcript` 404 (used the CC-BY STEMM set); product
descriptions `red-dot`/Amazon sets 404 or gated, and `LuminaAI/RCL-Ecommerce` streaming hung (fell back to
the small `llm-wizard` set, hence only 90 rows); CFPB direct API 403 (used the HF mirror). Fetchers:
`results/modality_domain_breadth/fetch_modality.py` + `fetch_modality_fix.py` + `fetch_ted.py`.

## What "ALL" honestly means now

**Every named row is now resolved.** Every concretely named corpus in both catalogues has a real status in
the tables above: 53 rows are on disk (20 prior + 33 fetched or sampled by this effort), and 26 rows are
genuinely blocked, each with the wall named — a login (Yelp, Meta Ad Library, TED ratings, Change.org, NIKL),
a download form (IBM Project Debater sets), PDF only bulk (the Southeast Asian parliaments), scrape only
sources (American Presidency Project, the CJK forums), a dead host (Uppsala Persian, Russian Duma repo), or
no single open dump (OpenITI, split across hundreds of GitHub repos; the French volume archives). Nothing is
left as "deferred" — the second pass pulled the previously skipped fetchable corpora and confirmed the rest
as true walls.

**Newly in hand across the two passes (33).** First pass (25): LIAR, IBM-arg-quality-30k, OpenDebateEvidence,
Federalist Papers, Super-SCOTUS, UKPConvArg1, IQ2 debates, DonorsChoose, Amazon Reviews 2023, IRA troll
tweets, French-PD newspapers, ECHR, MasakhaNEWS, MasakhaNER2, MasakhaPOS, AfriQA, AfriSenti, Kencorpus,
Persian daily news, Weibo sentiment, Aozora index, India Lok/Rajya Sabha, Brazil Chamber, plus the parquet
route recoveries. Second pass (8): the **FULL Upworthy Research Archive** (291,790 headline packages across
33,129 randomised A/B tests, upgraded from a 340 row scored subset — this is our only causal corpus, so the
full archive matters most), Europarl, ParlSpeech V2, Japan Diet, IndicCorpV2 (AI4Bharat), Chronicling America
(via AmericanStories), US Congress (Congressional Record / ConSpeak, 2.8GB), and the full Wikipedia Articles
for Deletion corpus (3.3M utterances). The big continental wins are the **African family** (six
Masakhane/Kencorpus sets, ~40 languages of native, human annotated text — the thinnest cluster in the
coverage matrix is now the best covered by language count) and the **native non English anchors** (Chinese
Weibo, Persian news, Japanese Aozora, Indian IndicCorp, French deep time press).

**What "ALL" does NOT mean.** It is not literally every corpus on earth, and it never can be. The
meta hubs — HuggingFace filtered by 200+ language codes, CLARIN Resource Families, Universal Dependencies
(168 languages), Lanfrica, the per language awesome lists, and the OPUS/OSCAR/CC100/mC4 web crawls — are an
**unbounded long tail**: they are a method for pulling any specific language on demand, not a finite list to
tick off. Claiming to have downloaded "everything" from them would be false. The honest claim is the one
the catalogues already make: **every major language family and culture cluster now has real native,
human involved discourse on disk; every country has the UN + web floor; the remaining gaps
(Southeast Asian and Russian parliaments, modern Chinese/Korean/Japanese forums, the login walled
commercial sets) are named with the specific wall that blocks each.**

### Thin regions — deepened this third pass
- **Sub-Saharan Africa** — now has the Pan-African Parliament Hansard (continent wide decision corpus in
  Akoma Ntoso), on top of the six Masakhane/Kencorpus sets and the national Hansards.
- **Nordics** — Norwegian Colossal Corpus and Danish Gigaword now held; Swedish and Icelandic Gigaword
  remain blocked (no clean keyless bulk), but the cluster is no longer floor only.
- **Australasia** — Papers Past New Zealand held (historical press incl te reo Maori); Trove Australia needs
  a free API key (recorded BLOCKED-needs-key).
- **Middle East deep time** — OpenITI premodern Arabic now held as a documented GitHub slice; the Knesset
  Corpus adds a native Hebrew decision corpus.
- **Latin America** — Argentina session index added beside the Brazil speech anchor; Chile and Mexico
  congress text stay blocked (hosts unreachable from our network / PDF only).

### Thin regions that remain
- **Southeast Asia** — parliaments are PDF only (Indonesia, Philippines, Vietnam, Thailand); still floor only.
- **Russia** — Duma transcript source unresolved (repo 404); ParlaMint/IRA give partial Russian coverage.
- **Modern China / Korea / Japan social** — forums have no clean open dump; covered instead by Weibo
  sentiment (CN), natparl assemblies (KR), and Aozora (JP native literary).
- **Central Asia / Pacific islands / Caribbean** — floor only (UN + web), as the coverage matrix states.

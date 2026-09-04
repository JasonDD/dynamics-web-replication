# Master corpus index — DYNAMICS-WEB

*The single place to see every corpus we hold and where the gaps are. Compiled 30 August 2026 from the definitive
on disk state at the internal corpus store on the internal host. Per dataset URLs, row counts and blocked reasons live in
DATASET_ACQUISITION_LEDGER.md; per region source depth in REGION_COVERAGE_MAP.md. 80 corpus directories, ~66 GB (82 held ledger rows across five acquisition passes; the fifth was the corpus universe expansion adding 16 new coordinates for the empty map regions).*

## Decision corpora (a real human choice tied to a text)
| corpus | decision | causal? | region | size |
|---|---|---|---|---|
| upworthy_full | click a headline | **RANDOMISED/causal** (291,790 pkgs / 33,129 A/B tests) | US | 123M |
| cmv_winning_args | change my view (delta) | ecological | EN | 422M |
| wiki_afd | keep vs delete verdict | ecological | EN | 1.7G |
| pan_african_parliament | continent wide Hansard (AU) | ecological (decision) | pan African | 22M |
| knesset_corpus | Israeli parliament + demographics | ecological (decision) | IL | 5.5G (365 full protocols) |
| opspam_deceptive | truthful vs deceptive hotel review | gold labelled deception | US | 2,862 |
| phishing_email | phishing vs legitimate | gold labelled deception | EN | 18,650 |
| uk_petitions | sign | ecological | UK | 128M |
| ddo | debate vote | ecological (our result: null) | EN | 412M |
| stackexchange_args | accepted answer | ecological | EN | 662M |
| human_persuasion | fund / donate | ecological | EN | 1.9G |
| donorschoose | donate | ecological | US | 345M |
| echr | court judgment | ecological | EU | 86M |
| oldbailey | jury verdict (1700s-1900s) | ecological | UK | 156K |
| liar | fact check verdict | ecological | US | 2.9M |

## Argument / quality (human rated — instrument validation)
ibm_argq_30k (5.5M), opendebateevidence (52M), ukpconvarg (154M), iq2 (32M), federalist (1.2M, authorship).

## Parliamentary / political (character by nation; several party labelled)
parlamint (34G, 29 countries), parlspeech (Czech Corp_PSP_V2.rds 387M, 1 of 9 democracies; zip truncated so pulled per file), europarl (1.1M, 21 langs),
us_congress (2.7G), supreme/SCOTUS (7.9G), india_loksabha (20M), brazil_chamber (496K),
argentina_congress (27K — Diarios de Sesiones index, 577 sittings), natparl (47M — Ghana/Kenya/South Africa/
Zambia/Zimbabwe/Malaysia/Korea), japan_diet (2.5M), pan_african_parliament (22M — continent wide Hansard),
knesset_corpus (5.5G — Hebrew, 365 full plenary protocols, speaker demographics).

## News / discourse (position & character by region, dated)
ungd (409M — UN General Debate, every country 1946-2022), ira_troll (181M — influence ops, RU),
weibo_sentiment (9.4M, CN), persian_daily_news (21M, IR), french_pd_news (469M, FR historical),
american_stories (6.8M, US historical press), ncc_norwegian (34M, NO dated OCR), danish_gigaword (180M, DK),
papers_past_nz (NZ historical press, 1850-1940, incl te reo Maori).

## African NLP family
masakhanews (69M), masakhaner2 (37M), masakhapos (34M), afrisenti (15M), kencorpus (18M), afriqa (1.3M) —
16-20 African languages.

## Deep time proxies (transcribed / OCR)
classical (2.0M — Zhanguo Ce Chinese + Perseus Greek/Latin), aozora (17M — Japanese literary),
histchar (1.1M — periodicals 1810-1960), american_stories (US press 1900), openiti (premodern Arabic/Persian,
150 texts sampled from OpenITI 0300AH+0450AH), papers_past_nz (NZ press 1850-1940), french_pd_news (FR press), darwin_letters (Darwin correspondence, the unperformed private voice),
gutenberg_english (Project Gutenberg public domain books, deep time literary register breadth).
Broader now than the old "only 4"; still deepest in Europe/East Asia.

## Person side / multilingual
pandora (39M — MBTI/Big-Five from Reddit), indiccorp_v2 (2.9M — Indian languages), amazon_reviews (11M — review
helpfulness, multi locale), bible_multilingual (8,846 verses, 8 language pairs), quran (6,235),
proverbs_multilingual (983, 6 languages), coraal_spoken (302 sociolinguistic interview transcripts — spoken register).

## Native web by language (corpus expansion, new regional coordinates)
FineWeb-2 native web samples (500 rows each, first row group) filling regions the index had thin or empty.
Southeast Asia: fw2_indonesian (`ind_Latn`), fw2_thai (`tha_Thai`), fw2_vietnamese (`vie_Latn`),
fw2_filipino (`fil_Latn`). Central Asia (was floor only): fw2_kazakh (`kaz_Cyrl`), fw2_uzbek (`uzn_Latn`).
Pacific (was ABSENT): fw2_samoan (`smo_Latn`), fw2_fijian (`fij_Latn`), fw2_maori (`mri_Latn`, te reo).
Horn of Africa: fw2_amharic (`amh_Ethi`, Ge'ez script), fw2_somali (`som_Latn`). Each sample scored on the 8
axes; see `results/corpus_expansion/RESULT.md`.

## Social media platforms (new platform coordinates)
The index had almost no social voice beyond Weibo and the forum corpora. Added (500 rows each):
twitter_sentiment140 (Twitter/X, Stanford Sentiment140), mastodon_toots (Mastodon fediverse),
telegram_channels (public Telegram channels), youtube_comments (YouTube). Sample scored on the 8 axes.

## FAILED / empty (needs refetch)
- **russia_duma** — 16K, source 404'd (still the one open refetch).

## Not held (named, blocked — wall stated)
Indonesia + Philippines parliaments (PDF only, OCR hill), Zhihu/Baidu/People's Daily/YACIS/2channel (no clean
dump), TED/Yelp/GoFundMe/Change.org/SemEval (login walled), Trove AU (needs a free API key),
Chile + Mexico congresses (hosts unreachable from our network / PDF only), Swedish + Icelandic Gigaword
(no clean keyless bulk; Nordic covered by NCC + Danish Gigaword), OpenITI full (~4,300 texts; a GitHub
slice of 150 is held, the full corpus has no single dump).

## Global breadth layer (queried live, not a dataset dir)
GDELT (100+ languages, every country, since 1979), Common Crawl by language (OSCAR/CC100/mC4/FineWeb-2),
World Values Survey + Eurobarometer + Pew (opinion validation anchors). These give worldwide BREADTH by
construction; the corpora above give DEPTH where it exists.

## The honest shape
Rich: Western Europe, US, East Asia. Decent: Sub-Saharan Africa (now with the Pan-African Parliament decision
corpus), Latin America (Brazil speech + Argentina session index). Newly deepened: Nordics (NCC + Danish
Gigaword held), Australasia (Papers Past NZ held; Trove needs a key), Middle East deep time (OpenITI slice +
Knesset). Deep time proxies broader than before but still deepest in Europe/East Asia. The fifth expansion
pass added native web for the Pacific (Samoan/Fijian/Maori), Central Asia (Kazakh/Uzbek), the Horn of Africa
(Amharic/Somali) and Southeast Asia, plus four social platforms (Twitter/Mastodon/Telegram/YouTube). Still
genuinely data poor for a *decision* corpus: Pacific islands, Caribbean, parts of Central Asia (native web now
exists there, but no open parliament or petition dump). Still open: russia_duma refetch, Chile/Mexico congress
text (PDF/unreachable), Trove key, full OpenITI, plus sub national and diaspora dimensions.

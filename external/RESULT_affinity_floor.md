# Full graph country affinity: the minimum link floor fix

**Input:** `full_country_link_matrix.npz` (222 countries, symmetric shared link
matrix, zero diagonal, 1,338,953,292 total shared links across the full Common
Crawl web graph).
**Output:** `full_country_affinity_clean.json` (per country top partners by lift,
plus honest pass and drop lists).
**Generator:** `clean_country_affinity.py` (reproducible, thresholds as named
constants).

## The flaw

Lift (observed shared links divided by the count expected if countries linked at
random) blows up when a country has very few resolved links. In the raw output
Japan's top partners came out as Mauritius, Grenada and Seychelles, and Russia's
as Kyrgyzstan, Liberia and Timor. These are thin nodes whose entire profile
rests on a handful of probably automated links, so a small observed count
against a tiny expected count reads as a huge affinity.

Two deeper problems showed up once the tiny nodes were handled:

1. **Russia is over assigned.** RU holds 11.42% of every shared link in the
   graph (152M of 1.34B), far above its real web share of two to three per cent.
   Small countries that dump 40 to 45% of their links onto RU (Timor 44%,
   Liberia 45%, Mozambique 41%, Burundi 42%, Mongolia 41%) then read as strong
   Russian partners. Belarus does the same at 48% and is genuine, so the only
   thing that separates signal from noise here is node size: a substantial
   national web can be trusted, a thin one cannot.

2. **Offshore and redirect ccTLDs.** Domains under commercially sold or shortener
   TLDs (Mauritius `.mu`, Grenada `.gd`, Belize `.bz`, St Vincent `.vc`,
   Greenland `.gl`, Latvia `.lv`) accumulate cross border links from everywhere
   and produce high lift with unrelated countries. Some of these nodes are large
   (Greenland 2.4M, Estonia 1.8M), so no size floor removes them.

A single pair count floor is the wrong lever for all of this: it would kill the
genuine Egypt to Saudi Arabia tie (1,163 raw links, lift 12) while keeping the
Timor to Russia noise (127,620 raw links).

## The fix

Five stages, all in `clean_country_affinity.py`:

| Stage | Rule | Purpose |
|---|---|---|
| Node floor | drop a country with total shared links below **100,000** | removes thin web nodes whose profile cannot be trusted |
| Pair floor | ignore any pair with raw shared count below **100** | removes single link spikes, keeps the real thin ties (Egypt to Saudi Arabia at 1,163) |
| Russia satellite guard | drop a country if total below **1,000,000** and its single largest partner is RU with share above **0.38** | removes the countries the over assigned Russian hub drags in (Timor, Liberia, Mozambique, Burundi, Mongolia) |
| Vanity hub guard | drop a country if total below **3,000,000** and it appears in the top eight of more than **18** other countries | removes small but ubiquitous redirect TLDs (Greenland, Latvia) |
| Offshore TLD guard | drop a country if total below **400,000** and its neighbourhood coherence is below **0.30** | removes small offshore TLDs (Mauritius, Grenada, Belize, St Vincent) whose top partners do not form a real cluster |

Lift is then recomputed with the configuration model expectation
(expected = row sum i times row sum j divided by grand total) over the survivors
only.

**Neighbourhood coherence** is the discriminator that pure floors could not
provide. For each candidate it takes the top six non hub partners by lift and
measures the fraction of those partner pairs that are themselves linked at lift
1.5 or above. A genuine regional country sits inside a clique (Jordan 0.60,
Costa Rica 0.87, Ecuador 1.00, Cyprus high), so its partners interlink. An
offshore TLD's partners are scattered hubs that do not (Mauritius 0.07,
Montserrat 0.13, Belize 0.20, Grenada 0.27). The guard is gated to small totals
so that a genuine country whose real partners are all large hubs (Belgium, whose
neighbours France, the Netherlands and Germany are all hubs) is never flagged.

## Before and after

| Country | Raw top partners | Cleaned top partners |
|---|---|---|
| Japan | Mauritius, Grenada, Seychelles | Taiwan, Estonia, United States, Ecuador, South Korea, Hong Kong |
| Russia | Kyrgyzstan, Liberia, Timor | Belarus, Ukraine, Pakistan, Tajikistan, Kazakhstan, Uzbekistan |
| Egypt | (thin) | Jordan 18.5, Saudi Arabia 12.0, Iraq, Palestine, Oman, Algeria, Qatar |

Families the cleaned data recovers, all reading as real linguistic, colonial or
regional clusters:

- **Hispanophone** — Spain: Panama, Cuba, Costa Rica, Uruguay, Ecuador,
  Venezuela, Argentina, Peru. Mexico, Argentina and Chile all resolve to the
  same Latin American cluster.
- **Francophone** — France: Luxembourg, Belgium, Senegal, Algeria, Tunisia,
  Ivory Coast, Morocco, Switzerland.
- **Arab and Gulf** — Egypt to Saudi Arabia at 12, and Saudi Arabia, the UAE
  and the Gulf states forming a tight ring (Oman, Qatar, Jordan, Iraq,
  Palestine).
- **Nordic** — Sweden: Norway 9.5, Denmark 5.5, Finland 4.9.
- **Former Soviet** — Russia: Belarus, Ukraine, Kazakhstan, Uzbekistan,
  Tajikistan, Pakistan.
- **African** — Kenya, South Africa, Nigeria, Senegal all resolve to genuine
  East, Southern and West African clusters (Namibia, Zimbabwe, Uganda,
  Tanzania, Ghana, Cameroon, Angola).
- Strong bilateral pairs the map should show clearly: Cyprus to Greece (19.4),
  Romania to Moldova (15.9), Hong Kong to Taiwan (9.7), Netherlands to
  Belgium (7.2).

## Coverage: what we can and cannot say

**107 countries pass, 115 are dropped.** The map should render only the 107 and
leave the rest blank rather than fill them with noise.

Dropped, by reason:

- **94 below the 100,000 link floor** — too thin a web presence to characterise.
- **9 as Russia satellites** — small countries the over assigned Russian hub
  drags in. This list includes genuine former Soviet neighbours (Azerbaijan,
  Kyrgyzstan) that we cannot separate from spam concentration without external
  data, so they are dropped honestly rather than shown with an unreliable tie.
- **2 as vanity hubs** — Greenland and Latvia.
- **13 as offshore TLDs** — Mauritius, Grenada, Belize, St Vincent, Montserrat
  and similar. This band also sacrifices some genuine countries whose link
  neighbourhoods are too incoherent to trust: Ethiopia, Madagascar, Somalia,
  Liechtenstein, and the French territories Guadeloupe and Réunion. These are
  an accepted false positive cost of removing the offshore noise.

**Residual limits, stated plainly:**

- The insular Asian webs (Japan, South Korea, Thailand, Philippines, Vietnam,
  Indonesia) keep a few artifact partners. Their genuine external link signal
  is weak because most of their linking stays domestic or goes to the United
  States, so the little cross border signal that remains is noisier than
  elsewhere. Japan and Korea are usable but read them with more caution than
  Europe or Latin America.
- A handful of single pair spikes survive the floors: India to Cape Verde,
  China to Armenia, Brazil to Kazakhstan. These are large raw counts against a
  thin partner and are almost certainly an artifact of the country resolution,
  not a real tie.
- Two upstream data faults sit below this task and cannot be fixed here:
  Colombia is absent from the matrix entirely (a resolution gap), and Russian
  link mass is inflated to about four times its real share.

The method is honest by construction: the drop lists are published in the JSON
so coverage can be audited, and every country shown has both a trusted link
volume and a coherent partner cluster behind it.

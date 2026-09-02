# Paper 4 public journalist proxy: the coupling on a public substrate

PUBLIC tier. Aggregate only, no individual named. PUBLIC track paper, DYNAMICS-WEB series.

Paper 4's two core results were first measured on the internally held cross site
authorship corpus (`cc_v3.crosssite_authorship`, the pseudonymous person seen writing
across many separate sites), which is a held asset (tier two) and is not distributed.
For reviewability this experiment runs the identical two analyses on a public reviewable
substitute: journalists seen writing across several editorial sections of the press. One
byline is one person, one editorial section is one room, so the trait against performed
state decomposition and the metatrait bridge apply unchanged, on a public corpus and with
no identity resolution.

## The boundary that keeps this in the public tier

The proxy identifies a person by the published byline in the news corpus. It never uses
the held cross site linkage mechanism (withheld as commercial intellectual property); that linkage method is the factory and is not in this pack.
The byline proxy is the recipe: a reviewer reproduces the coupling geometry without it. No
production scorer weights, no training corpus, no operational calibration is present here.

## The two analyses

- **A. Trait versus performance split (ICC).** Each DYNAMICS-8 disposition axis is
  decomposed into a between author share (stable trait) and a within author across sections
  share (performed room state) by a one way random effects intraclass correlation, ICC(1).
  The between author share is the trait fraction.
- **B. Metatrait bridge (person level).** Person level plasticity and stability metatraits
  (the DeYoung Big Two read from disposition: plasticity = sociability + novelty, stability
  = discipline + yielding minus mercuriality) against the produced character (matter versus
  manner, and originality), with each author averaged over their sections so performed state
  cancels.

## Headline result (reproduced on DL580, 2 September 2026)

Corpus `cc_v3.news_topic`: 33,920 scored articles, 1,367 authors; 1,355 authors seen across
two or more distinct sections (33,785 articles).

- **Trait fraction (mean disposition ICC): about 0.12** (0.116 article level, 0.122 section
  mean level). Read from a single article, a journalist's disposition is mostly performed
  section state, a minority stable trait. This agrees in direction with the held corpus read
  (disposition is part trait, part performed).
- **plasticity to originality: r = +0.390, n = 1,355, p < 1e-3** (person level). The
  metatrait bridge reproduces on the public proxy: more plastic authors produce more
  original content once performed state is averaged out. This is the spine of the coupling.
- Supporting person level reads: stability to originality r = minus 0.225; stability to
  matter versus manner r = +0.127; plasticity to matter versus manner is a null
  (r = +0.014). At article level the bridge attenuates as expected (plasticity to
  originality r = +0.178), because the single article read is dominated by performed state.

## How to reproduce

`paper4_public_proxy.py` in this directory (and committed in the main repository at
`docs/papers/dynamics_web_series/repro/paper4_public_proxy.py`). It needs python3 with numpy
and psycopg2, read access to the `cc_v3` schema, and the DB password read from `~/.pgpass`
(no secret in the script). Run it, and it prints the ICC table, the person level bridge, and
the article level contrast. `run_output.txt` here is the captured run. `cc_v3.news_topic` is
a held crawl derivative (tier two); a reviewer with a comparable public news corpus scored by
the shared apparatus (the character scorer `cc_found_human_score.py` and the disposition
scorer `pandora_d8_score.py`) reproduces the same coupling.

## Bounds

The proxy is a substitute, not the held corpus: journalists across sections is a narrower and
more professional register than the general cross site population, so the trait fraction sits
a little below the held corpus figure and the register is less varied. The qualitative claims
carry across, the point estimates are the proxy's own. The result stands as a public,
reviewable demonstration that the coupling is real and reproducible without the held asset.

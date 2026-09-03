# Paper 4A reproducibility, public journalist proxy

This directory holds the PUBLIC reproduction scripts for Paper 4A (the person to
content coupling). Public tier only: the recipe, not the factory. The scripts
here reconstruct the shared measuring apparatus and re run the coupling on a
public substrate. They do not carry the production scorer weights, the training
corpus, the operational calibration, or the cross site linkage method, all of
which are held (see `../../REPLICATION_PACK.md` §6 and §7).

## `paper4_public_proxy.py`

Paper 4A's two core results were first measured on an internally held cross site
authorship corpus, the pseudonymous person seen writing across many separate
sites. That corpus is a held asset and is not distributed. This script runs the
same two analyses on a public reviewable substitute: journalists seen writing
across several editorial sections of the press. One byline is one person, one
section is one room, so the same trait against performed state decomposition and
the same metatrait bridge apply, with a public corpus and no identity resolution.

The important boundary: this proxy identifies a person by the published byline
in a news corpus. It never uses the held cross site linkage mechanism (the avatar
hash join that resolves one pseudonymous person across unrelated sites). The
linkage method is the factory and stays out of the public tier. The byline proxy
is the recipe: a reviewer reproduces the coupling geometry without it.

### Two analyses

- **A. Trait versus performance split (ICC).** Each DYNAMICS-8 disposition axis
  is decomposed into a between author share (the stable trait) and a within
  author across sections share (the performed room state), by a one way random
  effects intraclass correlation. The between author share is the trait fraction.
- **B. Metatrait bridge (person level).** Person level plasticity and stability
  metatraits (the DeYoung Big Two read from disposition) against the character a
  person produces (matter versus manner, and originality), with each author
  averaged over their sections so the performed state cancels.

### Result (reproduced on DL580, 2 September 2026)

Corpus `cc_v3.news_topic`: 33,920 scored articles, 1,367 authors; 1,355 authors
seen across two or more distinct sections (33,785 articles).

- **Trait fraction (mean disposition ICC): about 0.12** (0.116 at article level,
  0.122 at section mean level). Read from a single article, a journalist's
  disposition is mostly performed section state, a minority stable trait.
- **plasticity to originality: r = +0.390, n = 1,355, p < 1e-3** (person level).
  The metatrait bridge reproduces on the public proxy: the more plastic authors
  produce the more original content, once performed state is averaged out.
- Supporting person level reads: stability to originality r = minus 0.225;
  stability to matter versus manner r = +0.127; plasticity to matter versus
  manner is a null (r = +0.014). At article level the bridge attenuates as
  expected (plasticity to originality r = +0.178), because the single article
  read is dominated by performed state.

The headline for the paper: the coupling that Paper 4A measures on the held cross
site corpus reproduces on a public journalist corpus, plasticity to originality
r about +0.39, trait fraction about 0.12.

### How to run

```bash
# needs: python3 with numpy and psycopg2; read access to the cc_v3 schema;
# the DB password read from ~/.pgpass (no secret in the script).
python3 paper4_public_proxy.py
```

It prints the ICC table, the person level bridge, and the article level contrast.
The numbers are deterministic given the same scored corpus. `cc_v3.news_topic` is
a held crawl derivative (tier two, reported not released, see the pack): a
reviewer with a comparable public news corpus scored by the shared apparatus
(`../../../../truthometer/scripts/cc_found_human_score.py` and
`pandora_d8_score.py`) reproduces the same coupling.

## Related committed experiment scripts

- `../../../../scripts/fullgraph_propagate.py` materialises authority (indegree,
  pagerank) and the eight axis character across the full Common Crawl link graph
  (118.76M vertices), so any linked domain carries a score. The propagation method
  is the recipe and is public; the pre computed national and sector maps it
  produces are the commercial asset and are held (pack §7 item 2).

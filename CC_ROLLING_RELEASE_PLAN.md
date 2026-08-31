# The web character map: rolling release plan and cost

*How to map the character of the Common Crawl web on every release, at a bounded recurring cost, and release it behind the live position so the aged map is public and the current map stays the commercial edge. Companion to the release tiers and commercial protection layer of `REPLICATION_PACK.md` (Sections 6 and 7). Compiled 31 August 2026.*

## 1. The release model

Release behind the live position, the way a credit bureau or a satellite imagery firm sells the aged tier and holds the live one.

- **United Kingdom, current, released in full.** The home market and the demonstration. The current UK domain map (the full UK namespace, link derived) is what a customer touches and what proves the capability; the moat cost of releasing it live is low.
- **The world, current, held.** The live global character map is the commercial edge and is one of the five commercial holds named in the replication pack: disclose existence, hold coordinates.
- **The world, released at a twelve month lag.** The public and the lower tier get a real, rich global map, a year old. The current world stays the moat. The rule "disclose existence, hold coordinates" becomes "disclose last year, hold this year."

This slots straight into the four axis release governance: the aged world map is publishable, the current world map is the held asset.

## 2. How the map is made, and where we stand

Directly scoring every domain is astronomical and is not the method. The method, already built, is to score a seed on the eight axis instrument and propagate character across the Common Crawl web graph, whose correlation length is about two hops.

Current position:
- about 2.6 million domains directly scored (`cc_v3.domain_char8_expanded`);
- the full web graph, 118.7 million domains and 4.34 billion links;
- character propagated across it to about 75 million domains;
- the United Kingdom corpus is the full UK namespace, link derived, of which a slice is directly scored and the rest propagated.

A release map is the seed scores plus the propagated field over one crawl's graph.

## 3. The per release cost, measured

Common Crawl publishes roughly monthly. The scorer throughput was measured on the current hardware: a single request stream reaches about 3.6 per second on a short prompt and about 1.6 per second on the full scoring prompt, but the endpoint scales hard under concurrency, reaching about 25 per second at concurrency 8 and about 35 per second at concurrency 24 on short prompts. Applying the same tenfold concurrency scaling to the full scoring prompt gives an effective real scoring rate of roughly 10 to 15 domains per second on one endpoint, and about double that across both GPUs.

From that measured rate:
- **A full re score of the 2.6 million seed** takes about 1 to 2 days on one endpoint, about half that across both GPUs. This is the worst case and is not what a release needs.
- **A delta re score**, only the domains that are new or materially changed since the last crawl, is the real per release cost. At an estimated 15 to 20 per cent churn that is about 400 to 520 thousand domains, roughly 5 to 12 hours of scoring depending on GPU count.
- **Propagation** across the 118 million vertex, 4.34 billion edge graph ran in hours in the prior run with the ping pong buffer that fixed the earlier out of memory failure.
- **Storage.** The domain character map is tens of gigabytes per release; the page lake is terabyte scale and stays as Parquet on the NAS, never in Postgres.

**Net per monthly release: on the order of one day of compute end to end, dominated by the delta re score and the propagation, well within the box.** It is a recurring batch job, not a moon shot, and it gets cheaper as delta scoring replaces full re scoring.

Two numbers are estimates rather than measurements and should be pinned before the pipeline is trusted to a schedule: the actual crawl to crawl domain churn (needs a diff of two consecutive crawl domain lists) and the propagation wall time on the current graph (needs one timed run). The scoring throughput above is measured, not estimated.

## 4. The pipeline

A rolling release is this loop, run per crawl:

1. **Fetch** the new crawl's web graph (domains and links) and domain list.
2. **Delta detect.** Diff the domain list and the content hashes against the last release; emit the set of new and materially changed domains.
3. **Score the delta** on the eight axis instrument at concurrency (10 to 15 per second per endpoint), writing to the seed table.
4. **Propagate** character across the new graph from the refreshed seed.
5. **Snapshot** the resulting domain character map, dated and immutable.
6. **Publish on embargo.** The UK slice of the current snapshot publishes now; the world slice of the snapshot from twelve months ago publishes now; the current world snapshot is held.

Steps 2 and 6 are the two that are not yet built: delta detection, and the embargo mechanism that enforces the twelve month lag by construction rather than by promise.

## 5. Retention and the lag

Keep a grandfather father son retention: every monthly snapshot for the last twelve months (needed so that in twelve months each becomes the public world release), then one snapshot per quarter for the previous two years, then one per year. The twelve month embargo is enforced by the publish step selecting the snapshot dated exactly twelve months back for the world tier, and the current snapshot for the UK tier only; the current world snapshot is never selected for publication.

## 6. Honest bounds and what to build

- **Propagated character is not directly scored character.** The released map carries wider error bars away from the seed; the release must say so, and the seed should be refreshed toward the regions a customer cares about.
- **The lag must be a mechanism, not a promise.** The embargo has to be enforced by the publish step and the retention store, so that the current world map cannot be released by accident.
- **Delta detection is the efficiency.** Full re scoring every month is affordable but wasteful; the pipeline is only cheap once delta detection is built, which is the main new engineering.
- **A few weeks of engineering** turns the current manual re run into a true rolling product: the fetch and delta step, the embargoed publish step, the retention store, and the scheduler. The scoring and propagation halves already exist.

## 7. Next steps to pin the cost exactly

- Diff two consecutive Common Crawl domain lists to measure real churn, replacing the 15 to 20 per cent estimate.
- Run one full propagation on the current graph under a timer to measure its wall time exactly.
- With those two numbers and the measured scoring rate, the per release cost becomes a single figure and the release cadence can be scheduled.

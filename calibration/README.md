# DYNAMICS-WEB calibration sample (1,000 domains)

This is the released calibration sample for the eight axis character instrument used across the Distinct
Fields papers. It exists so that a reader who does not wish to trust the closed scorer can build an
independent scorer from the published axis definitions and check it against ours, and then rerun any
downstream finding on their own instrument. Any result that survives a rebuilt instrument is validated
independently of our infrastructure; any that does not is a result against us that this file lets a reader
produce.

## What is here

`dynamics_web_calibration_1000.csv` — 1,000 web domains, each with our score on the eight axes and the
first principal component index.

| column | meaning |
|---|---|
| `domain` | the web domain (public, from Common Crawl) |
| `rigour` ... `register` | the eight axis scores, each 0 to 1, as read by the instrument |
| `character_index_pc1_sd` | the first principal component of the eight axes, in standard deviation units |

The axes are rigour, depth, originality, candour, affect, commercial drive, stance and register, each reading
the voice a page projects rather than its subject.

## How the sample was drawn

800 domains stratified across the ten deciles of the character index (80 per decile), plus 200 domains at the
axis extremes (the twelve highest and thirteen lowest on each of the eight axes). The stratification spans the
index range and the axis extremes deliberately, so a rebuilt scorer is tested where the instrument is easy and
where it is hard, not only in the middle. Selection seed 20260904.

## The axis definitions and the scorer

The axis definitions in the operational form the raters received, together with the scoring prompt,
vocabulary and parser, are in `scripts/cc_found_human_score.py` in this repository. Those definitions plus
this sample are enough to build an independent scorer.

## What is not here, and why

The trained scoring model and its weights, the full calibration set beyond this sample, and the full per
domain scores across the whole panel are held. Publishing the full per domain scores would let the instrument
be distilled; this is an intellectual property hold, not a safety one. A private, identically stratified twin
of this sample is retained so that claimed reproductions can be verified on domains the claimant has not seen.

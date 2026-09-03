# Character map rebuild: held out validation of the two hop propagation

*DYNAMICS-WEB series, 3 September 2026. Script `char_propagate_2hop.py` (copy in this directory), run
on DL580 against the 118,760,321 vertex, 4,343,610,896 edge Common Crawl host graph. Pass mark fixed
before the run: mean held out r above 0.36 AND the calibrated estimate beats the seed mean on both
MAE and RMSE on every axis. Seeds: 3,136,616 scored domains; 10% (313,662) masked and held out.*

## Why this exists

The first full propagation failed its held out test (deep propagation was ten times worse than
predicting the mean; one hop r=0.36). Two faults, both read from the code: the normaliser summed
ALL inbound weight while the accumulator only received seeded neighbours, so every inferred value
was dragged toward zero; and the seeds were 2.6% of the graph so the drag compounded with depth.
The operator's ruling: the experiment was flawed, ignore its results, document it, rerun it properly.
"2 hops, good. Till the end, noise!"

The rebuild propagates evidence only, normalises only over neighbours that carry a value, stops at
two hops, and records how many valued neighbours each estimate rests on so a consumer gets an error
bar with the number.

## The answer

| Direction | Estimator | Coverage of held out | Mean r | Calibrated MAE (seed mean) | RMSE (seed mean) | R² against the mean | Bar |
|---|---|---|---|---|---|---|---|
| in links only | hop 1 | 60.5% | **0.361** | 0.0730 (0.0794) | 0.0928 (0.1001) | +0.137 | **PASS** |
| in links only | hop 2 | 81.0% | 0.342 | 0.0734 (0.0789) | 0.0931 (0.0993) | +0.120 | fails r |
| in links only | cascade | 81.0% | 0.333 | 0.0736 (0.0789) | 0.0934 (0.0993) | +0.114 | fails r |
| both directions | hop 1 | 82.8% | 0.333 | 0.0735 (0.0787) | 0.0932 (0.0991) | +0.115 | fails r |
| **both directions** | **hop 2** | **99.5%** | **0.423** | **0.0701 (0.0785)** | **0.0894 (0.0989)** | **+0.181** | **PASS** |
| both directions | cascade | 99.5% | 0.337 | 0.0732 (0.0785) | 0.0929 (0.0989) | +0.117 | fails r |

Graph coverage (all 118.8M vertices): in links only defines 38.0% at hop 1 and 77.9% at hop 2; both
directions 45.5% and 93.6%. Every estimator beats the seed mean on all eight axes on both error
measures; the bar that separates them is the correlation.

**The recipe is two hops over both link directions.** Out links carry evidence about a domain's
character as well as in links, and using both lifts the held out correlation from 0.36 to 0.42 while
covering nearly every masked domain instead of six in ten. Per axis at hop 2 both directions:
rigour r=0.47 (12.6% MAE gain on the mean), depth 0.42, and the rest between.

## The honest reading of why it wins

At equal evidence it does not. Read the confidence bands: a domain with 10 to 49 valued neighbours
gets r=0.52 from one hop of truth (in only) and r=0.40 from two hops (both), because a second hop
neighbour carries an inferred value, not a scored one. The both direction two hop estimator wins on
the MEAN because it moves nearly every domain into a rich evidence band: 149,669 held out domains
sit at 10 to 49 valued neighbours and 90,198 at 50 or more, against 32,239 and 10,732 for one hop in.
More evidence per domain, not deeper inference, is what the gain is. Beyond two hops the evidence is
inference stacked on inference and the correlation falls again (the cascade row), which is the
operator's "till the end, noise" in numbers.

Confidence bands, both directions hop 2 (what a consumer should attach to each estimate):

| Valued neighbours | Held out n | Mean r | Raw RMSE |
|---|---|---|---|
| 1 | 6,811 | 0.26 | 0.111 |
| 2 | 5,728 | 0.30 | 0.103 |
| 3 to 9 | 59,760 | 0.33 | 0.099 |
| 10 to 49 | 149,669 | 0.40 | 0.094 |
| 50 or more | 90,198 | 0.57 | 0.081 |

## What was built from it

The full build (`--mode full --dirs both`) writes `cc_v3.domain_char8_2hop` (domain, eight axes,
hop reached, number of valued contributors, total weight). Seeds keep their scored value at hop 0.
The protected tables (`domain_char8_full`, `domain_char8_scored`, `domain_indegree_full`,
`domain_ranks_cc`, `domain_char8_holdout`) are untouched. The failed first build's values are not
used anywhere.

Files: `validate_in.json`, `validate_both.json` (per axis grades, calibration slopes and intercepts,
confidence bands), `calibration_in.json`, `calibration_both.json`, run logs on DL580 at
`~/.kx-daemon/char2hop-val-in.log`, `char2hop-val-both.log`, `char2hop-full-both.log`.

## The map, sized by evidence (full build, 3 September 2026)

`cc_v3.domain_char8_2hop` holds 111,269,676 valued domains of the 118,760,321 in the host graph; 7,490,645
have no valued neighbour within two hops and carry no value. By the evidence each value rests on, with the
held out correlation of that band from the validation above:

| Valued neighbours | Domains | Held out r |
|---|---|---|
| scored directly (seed, hop 0) | 3,136,616 | the measurement itself |
| 50 or more | 1,381,692 | 0.57 |
| 10 to 49 | 6,623,215 | 0.40 |
| 3 to 9 | 22,379,195 | 0.33 |
| 2 | 16,286,343 | 0.30 |
| 1 | 61,462,615 | 0.26 |

Read plainly: about eight million domains carry a value good enough to use one domain at a time (r 0.40
or better), 1.4 million of them at 0.57; the remaining hundred million carry a value that is honest only as
a population signal, which is why the contributor count ships on every row. The validation bands were
measured on masked scored domains, which are the better linked part of the graph; the full map's mass sits
in the one neighbour band, so the headline coverage figure should never be quoted without this table.

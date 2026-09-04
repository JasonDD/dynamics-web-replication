# Analysis result artifacts

Saved outputs of the analysers behind the figures in the series. Each file carries a header stamping the
generation time and the data state it was run against (some corpora were still scoring). Regenerate any of
these with `truthometer/scripts/run_all_results.sh`. Source scores live on the internal store
(`the internal corpus store`); source tables in the internal schema (tfs). These files are the saved artifact so every
paper figure is recoverable without a re-run.

| File | Analyser | What it holds |
|---|---|---|
| coordination_synchrony/RESULT.md | coordination_synchrony/synchrony.py | character synchrony as a CIB signal (IRA vs CMV): static clustering FAILS (personas diversify), account identity index equal to organic, temporal affect bursts flag 49% of IRA busy days vs 0.5% organic |
| culture_map_global.txt | cc_culture_map_global.py | per-country character map (ccTLD), clustering, 2D coords, anglosphere affinity |
| invariant_core/RESULT.md | cc_invariant_core.py | the INVARIANT core: cultural vs shared share (culture 3.5-6.8%), most-invariant axes (register+candour), shared centre shape (matter-leaning), per-country PC1 cosine 0.977, room version w/ split-half noise separation |
| when_drift.txt | cc_when_drift.py | digital-era within-domain matter/manner drift 2020-2026, per country |
| fractal_dim.txt | cc_fractal_dim.py | correlation-dimension self-similarity vs matched-Gaussian + one-factor nulls |
| cmv_within_pair.txt | cc_cmv_analyse.py | CMV winner-vs-control per-axis paired test |
| cmv_arbiter.txt | cc_cmv_arbiter.py | CMV room-vs-person (within-thread / same-user / OP-disposition) |
| se_arbiter_where.txt | cc_cmv_arbiter.py (SE) | Stack Exchange cross-room where test |
| se_when_drift.txt | cc_se_when.py | SE per-room winning-norm drift across years |
| causal_claude.txt | cc_causal_analyse.py | causal persuadee panel (balance/matter-manner/interaction) |
| causal_manip_check.txt | cc_causal_check.py | manipulation check that the authored stimuli sit at their coordinates |

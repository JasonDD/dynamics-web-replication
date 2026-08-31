# PF-4B-GENRE-20260829-REV-1 — frozen pre-registration artefact

Genre as a state coordinate in the disposition to character coupling. Frozen BEFORE any coupling number,
correlation or BLUP is inspected (no-peeking rule).

## Audit chain (all reproducible)
- community name list: `subreddits_400.txt` — sha256 ef32436d6d1b154839926ad1e59a39378d535fd5534b7e690232d8284621c32c
- classifier code: `truthometer/scripts/reddit_genre_tag.py` (committed) — name-based only, blind to all scores
- FROZEN assignment: `genre_assign_400_FROZEN.json` — sha256 2d701e0c6af217bc1ae2fef3b4fe2fa7497fecf37d4191f0a49371d45660cfd1

## Taxonomy (15 buckets; other_misc excluded from the primary test)
place_local 54 · support_identity_health 42 · profession_tech_finance 41 · politics_ideology 38 ·
western_screen_music 32 · meta_circlejerk 30 · gaming 28 · anime_manga_kpop 28 · snark_gossip 25 ·
sports 22 · reality_tv_gossip 20 · discursive_argument 13 · truecrime_morbid 11 (low power) ·
religion 10 (low power) · other_misc 6 (EXCLUDED).

## Boundary rule (reality_tv_gossip vs snark_gossip), frozen
A community is snark_gossip if its NAME marks it as existing to mock or critique a subject (contains 'snark',
or a known critique community, e.g. DuggarsSnark, FundieSnarkUncensored, illnessfakers). The subject's own
fandom is reality_tv_gossip (e.g. BravoRealHousewives, thebachelor, 90dayfianceuncensored).

## Model (locked, one row per community, n=400)
Model A (state):     c_k ~ disp_k + (1 + disp_k | genre)          [no community intercept: 1 row/community]
Model B (nuisance):  c_k ~ disp_k + genre_fixed_effect
disp_k = community mean audience PLASTICITY (D8 metatrait, half A). Stability = secondary run.
c in {matter, manner (primary), originality, stance (asymmetry test)}, fit separately.
PRIMARY outcome: leave-one-genre-out CV, within-held-genre RMSE, Model A vs Model B.
SECONDARY: Var(genre random slopes) tau^2_1, LRT + BLUP order (supporting, low genre count).
other_misc and n<12 strata: retained in fixed-effect/CV; BLUPs descriptive only.
Tooling: statsmodels MixedLM (primary) + lme4::lmer cross-check. One pass, no model selection.

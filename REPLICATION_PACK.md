# Replication pack, the Distinct Fields experiments

*One place from which every experiment in the programme can be reproduced: the shared measuring apparatus, the boundary between what is externally reproducible and what is held under review, a manifest of every experiment with its data source, scripts and headline result, and the recipe to regenerate the scored data that is not committed. Compiled 31 August 2026, current as of the equation of state thread. Supersedes the partial REPRODUCIBILITY note of 1 August, which predated the unification, the international corpus work and the equation of state.*

Every result directory named below lives at `docs/papers/dynamics_web_series/results/<name>/` and carries its own `RESULT.md` with the method, the numbers and the honest bounds. Scripts named below live in `truthometer/scripts/` unless the result directory carries its own. All are committed on `ops/gh-treasure-discovery`.

---

## 1. The shared measuring apparatus (every experiment depends on this)

**The character instrument (DYNAMICS-WEB, eight axes).** Each text is scored on rigour, depth, originality, candour, affect, commercial drive, stance, register, each 0 to 1, reading the voice a text projects rather than its topic. The canonical scoring prompt, vocabulary and parser are in `truthometer/scripts/cc_found_human_score.py`; that same prompt and parser are reused by every character scoring script. The score is produced by a served 7B instruct model (the character scorer); the heavier lineage used for the cross model confirmations is a served 27B extract model. Model identities are recorded in the internal reference, not here, so this pack does not pin an external vendor.

**The disposition instrument (DYNAMICS-8, eight axes).** discipline, yielding, novelty, acuity, mercuriality, impulsivity, candour, sociability, read from a person's own writing. Scoring prompt and parser in `truthometer/scripts/pandora_d8_score.py` (and the cross site variant `cc_crosssite_score_27b.py`). The DeYoung Big Two metatraits used in the coupling and equation of state work are Plasticity = sociability + novelty and Stability = the complement.

**The matter versus manner axis (PC1).** The single ruler used throughout is the first principal component of the eight axis character space, computed by singular value decomposition of the reference table `cc_v3.domain_char8_expanded` (about 2.65 million domains), oriented so rigour plus depth is positive. Every script that needs the ruler rebuilds it the same way; the recipe is identical across `manip_analyse.py`, `cc_genre_state_fit.py`, `cc_state_fit_multi.py` and the reduction scripts.

**Where the data lives.** Public benchmark corpora and the internal crawl derivatives sit either on the NAS at `/mnt/nas/kronaxis/corpora/<name>/` or in the `cc_v3` schema of the internal Postgres (`cc_v3.domain_char8_expanded`, `cc_v3.reddit_wide`, `cc_v3.crosssite_authorship`, and the labelled tables named per experiment). The reference ruler table and the internal crawl tables are the internal hold set (Section 2).

**Environment.** python3 with numpy, scipy, statsmodels, pandas, psycopg2, pyarrow; the two scorer endpoints served locally; the Postgres reachable on the internal host. Heavy scoring runs under `kx-daemon` (write as you go, self healing). Nothing needs a GPU at analysis time; scoring does.

---

## 2. What is externally reproducible, and what is held under review

**Externally reproducible now.** Every experiment whose corpus is public: the IRA troll set, LIAR, IBM ArgQ, Europarl, Old Bailey, ParlaMint, the Federalist papers, MasakhaNEWS and AfriSenti, the multilingual Bible and Gutenberg, the UN General Debate, the Mathur dark pattern set, Enron, MasakhaNEWS, and the news and legislative corpora. For these, the pack gives the source, the fetch or build script and the analysis script; a reader re fetches, re scores with the shared apparatus, and reproduces the number.

**Held under review, reported not released.** Three assets rest on an internal web crawl and are not releasable: the 2.65 million domain character reference (`cc_v3.domain_char8_*`), the cross site pseudonymous authorship corpus (`cc_v3.crosssite_authorship`, the coupling and equation of state substrate), and the reddit wide corpus with per author disposition (`cc_v3.reddit_wide`). Experiments resting on these report their numbers and commit their scripts, so they are reproducible in principle by anyone with a comparable crawl and the same apparatus, but the raw corpus is not distributed. Every such result says so in its own bounds.

**Two honest gaps in coverage.** `commercial_comms_scout` keeps its result in a subdirectory (the earnings call fraud run) rather than a top level `RESULT.md`; `modality_domain_breadth` has scripts but no `RESULT.md` because its scoring was still running when its run stopped. Both are noted so the manifest count (54 of 56) is honest.

---

## 3. Regenerating the scored data that is not committed

Nine scored `.jsonl` files under result directories are gitignored because of size, so those experiments are committed as scripts plus `RESULT.md`, not scripts plus data. To regenerate any of them: run the experiment's fetch or build script (named `acq_fetch_*`, `build_*`, `fetch_*`, `prep_*` in its row) to assemble the input, then score it with the shared character scorer (`cc_found_human_score.py`) or disposition scorer (`pandora_d8_score.py`) writing to the path the analysis script reads, then run the analysis script. The scored file is deterministic given the same model and prompt, so the regenerated file reproduces the committed numbers within scorer noise (the cross model work quantifies that noise).

---

## 4. The experiment manifest

One row per experiment: the data source, the scripts, and the headline result. Full method and bounds in each `results/<name>/RESULT.md`.

| experiment | data source | scripts | headline result |
|---|---|---|---|
| `manipulation_character` | IRA, LIAR, CMV, reddit | manip_analyse.py | The affect on starved matter signature survives the length matched control comfortably (area under the curve about 0.925). |
| `manner_inflation_deception` | IRA, LIAR, Mathur, reddit | prep_deception.py, analyse_manner_inflation.py | Deception has a partly domain independent character signature; affect minus matter beats generic manner in every domain. |
| `reduction_crossmodel_27b` | IBM ArgQ, reddit | elm_27b.py, biber_27b.py, fleeson_27b.py | All three reductions hold in sign on the heavier lineage; the two correlation legs attenuate to about half magnitude. |
| `reduction_crossmodel_claude` | IBM ArgQ, reddit | elm_crossmodel.py, biber_crossmodel.py | The decisive independent family check: ELM holds (central pair +0.219 versus +0.159), Biber holds in direction; neither collapses. |
| `reduction_elm` | IBM ArgQ | elm_reduction.py | Supported: the matter core is the central route to argument quality (partial rho +0.159), affect the only negative axis. |
| `reduction_biber` | reddit_wide | biber_reduction.py | Our matter versus manner axis recovers Biber Dimension 1 at the genre centroid at r = minus 0.60, item level minus 0.14. |
| `reduction_fleeson` | crosssite_authorship | cc_crosssite_fleeson.py | The coupling reproduces Fleeson's roughly half and half trait against situation split, room level trait share 0.516. |
| `coupling_crosslineage` | crosssite_authorship | cc_crosssite_score_27b.py, cc_crosssite_scale.py | The metatrait bridge is robust and hardened, holds on both lineages, and is stable and tightens with scale. |
| `crossplatform_identity` | crosssite_authorship | crossplatform_identity.py | Writing re identifies the same pseudonymous person across platforms at area under the curve 0.93; stylometry stronger, character a prior. |
| `d8_validation` | pandora, reddit | pandora_d8_score.py, pandora_d8_analyse.py | DYNAMICS-8 validates for the four inherited factors this corpus can test, at person level and proper power. |
| `equation_of_state` | crosssite, reddit, Enron | cc_state_fit_multi.py, cc_state_rank.py, cc_state_closure.py | Genre, site and language enter as location offsets, none rotates the coupling, and the state displacement is of effective rank about two. |
| `controlled_edit_causal` | controlled edit set, reddit | cc_controlled_edit_prep.py, cc_controlled_edit_analyse.py | All three claims pass: the instrument responds to the edit, in the right direction, not to its length. |
| `account_level_detector` | IRA, reddit | account_analyse.py | Account level detection reaches area under the curve about 0.996; the variance of the character spread is the tell; it survives camouflage. |
| `detector_robustness` | IRA | (in dir) | Evasion of the gate is easy and total but not free: it de targets the persona the manipulation was for. |
| `manipulation_vs_toxicity` | IRA, reddit | detox_score.py, analyse_manip_vs_tox.py | Manipulation is near orthogonal to toxicity; the detector catches the quadrant toxicity tools structurally miss. |
| `crossdomain_transfer` | IRA, LIAR, reddit | crossdomain_transfer.py | The manipulation signature is domain general for text based persuasion and fraud, separable for interface dark patterns. |
| `crosslingual_manipulation` | Europarl, IRA | build_crosslingual.py, analyse_crosslingual.py | The affect on starved matter separation is large in every one of six languages, Persian the strongest. |
| `truth_prior` | IRA, LIAR | truth_prior_analyse.py | A fact checked lie carries only a weak trace of the manipulation signature; a false claim is not the same act as a manipulative one. |
| `candour_ethical_line` | IRA, LIAR, Mathur | analyse_candour.py | Candour is not the ethical line; it is the weakest separator and even inverts on dark patterns. |
| `temporal_manner_inflation` | Common Crawl | analyse_temporal_manner_inflation.py | The affect heavy matter starved share is stable to slightly falling; the web is not getting more manipulative. |
| `radicalisation_signature` | reddit | cc_radicalisation_analyse.py | Radicalising content is the manipulation signature with a monotone dose response up the pathway, milder than trolls; a triage prior. |
| `criminal_role_character` | darknet market archives | parse_dnm_forum.py, analyse_role.py | Under room control, enabler and user character do not separate; a weak prior only. |
| `escalation_trajectory` | CMV, IRA, Mathur | cc_cmv_escalation_analyse.py | No true manipulation conversation corpus is held, so the within conversation trajectory is design only here. |
| `coordination_synchrony` | IRA, reddit | synchrony.py | Character synchrony as a static cross account property is not a usable coordinated behaviour signal on its own. |
| `axis_covariance_matrix` | IRA, LIAR, ParlaMint, UNGD | cc_axis_covariance.py | The internal grammar of character is partly universal, partly context dependent, split along the matter versus manner line. |
| `scale_invariance_matrix` | Old Bailey, reddit | cc_scale_invariance.py | Directionally fractal: the axis is scale invariant within a substrate, but the dimensionality collapses from about five to one. |
| `field_structure_crosslineage` | IRA, LIAR, reddit | field_crosslineage.py | The core field structure replicates on the 27B lineage; the first principal component is the same. |
| `decision_outcome_matrix` | Old Bailey, reddit | third_outcome_spread.py, matrix_aux.py | Across eleven human decisions on one ruler, no character axis wins them all; the matter versus manner axis disagrees in sign. |
| `second_causal_anchor` | Upworthy megastudy | analyse_megastudy.py | A second causal anchor: the manner heavy heading causally wins the click, the cleaner half of the funnel. |
| `funnel_by_medium` | Old Bailey, reddit | funnel_by_medium.py | Split by pole: attention and conviction are earned by opposite characters, neither clean headline alone. |
| `third_outcome_spread` | IRA, reddit | third_outcome_spread.py | On 80,138 comments across 400 communities, novelty and affect travel and polemic does not, holding the room fixed. |
| `character_of_power` | ParlaMint | cc_power_build.py, cc_power_analyse.py | Gaining office de escalates a politician's character the same way across 23 countries; a within person natural experiment. |
| `knesset_attribute` | Knesset | (in dir) | On ground truth demographics, speaker sex carries no character signature once the sitting is fixed; position and age do. |
| `manifestos_elections` | manifestos, elections | manifestos_analyse.py | Campaign character predicts vote share, small and era dependent, and the sign flips between the US and UK systems. |
| `legal_systems_matrix` | Old Bailey, SCOTUS, ECHR, ParlaMint | analyse_matrix.py | Traditions occupy distinct character regions; winning character is system dependent, the strong half inquisitorial. |
| `sacred_secular` | Bible, ECHR, Old Bailey | build_sacred.py, analyse_sacred_secular.py | No universal voice of command; a clean split by authority type, two within type universals. |
| `global_legislature_matrix` | ParlaMint, SCOTUS, UNGD | build.py, score.py, analyse.py | The universal parliamentary voice wins; not a clean heritage clustering; language of record is a scorer confound. |
| `historical_press_drift` | world press, IRA | prep_worldpress.py, analyse_press_drift.py | Within a title, press voice is stable 1800 to 1960; affect flat everywhere; the matter rise is a web era property. |
| `federalist_authorship` | Federalist, Gutenberg | parse_federalist.py, stylometry.py | Stylometry resolves the disputed papers to Madison with the consensus; the character read is a weaker prior. |
| `biographical_arc` | Darwin letters, Gutenberg | clean_darwin.py, analyse_bioarc.py | The person is close to a fixed point; the biographical drift toward matter is mostly the room, collapsing under a correspondent control. |
| `translator_fingerprint` | Bible, Europarl | build_bible_input.py, fingerprint_analyse.py | Each target language stamps a consistent character offset, family structured, replicating across corpora, but a minority signal. |
| `translation_culture_vs_language` | Europarl | build_multiway.py, analyse_multiway.py | The between version character signal is overwhelmingly content and language, a tenth of the systematic signal is language. |
| `african_character_matrix` | MasakhaNEWS, AfriSenti | build_african.py, analyse_african.py | The leading axis reproduces in every African language, but as a substance factor, with a Geez script scorer boundary. |
| `invariant_core` | reddit, domain region | cc_invariant_core.py, cc_culture_regional.py | Culture accounts for 3.5 to 6.8 per cent of character; every national web organises along the same matter versus manner axis. |
| `diaspora_gradient` | Common Crawl | cc_diaspora_gradient.py, cc_region_fullgraph.py | Culture as a continuum in position (42 of 104 corridors intermediate) but the integration dynamics a clean null. |
| `culture_compass_drift` | Common Crawl | drift_align.py | Web character drift does not track survey opinion drift, a clean null across 31 to 33 nations. |
| `position_field_wvs_validation` | GDELT, WVS | fetch_gdelt_tone.py, validate.py | Promising on the one item fetched, deferred on the rest, on GDELT rate limits. |
| `universal_is_trait` | crosssite_authorship | cc_universal_is_trait.py | The hypothesis fails: culture share and within person trait stability are essentially uncorrelated. |
| `resonance_dwxd8` | reddit_wide | resonance_dwxd8.py | DW by D8 resonance is not yet a usable person to content coupling; two honest nulls. |
| `credibility_detector` | comms scout | detector_prep.py, detector_analyse.py | Credibility drift is not a demonstrated leading indicator of trust loss. |
| `crisis_barometer` | UCDP, UNGD | ungd_score.py, ungd_crisis_barometer.py | National discourse character is a real but modest crisis barometer. |
| `truthometer_eval` | IRA, LIAR, company registers | eval_truthometer.py | A precise verifier of register checkable claims, disciplined, that correctly abstains on the unfalsifiable. |
| `length_mechanism` | IRA, Old Bailey, ParlaMint, reddit | length_mechanism.py | Matter needs bandwidth and manner is instant, true on the mean and sharper than stated. |
| `corpus_expansion` | multiple, HF | acq_fetch_expansion.py, score_turns.py | Sixteen new corpus coordinates added across the map, with an eight axis means table. |

Owed rows: `commercial_comms_scout` (earnings call fraud, result in a subdirectory) and `modality_domain_breadth` (scripts present, result run incomplete).

## 4a. Experiments and analyses outside the main results directory

The 54 above are the experiments packaged with their own `results/<name>/RESULT.md`. A further set of real analyses lives in `truthometer/results/` and in the top level of the results directory; they are part of the programme and belong in the pack. Two of them are load bearing and a reviewer will ask for them first.

| experiment | location | data source | scripts | headline result |
|---|---|---|---|---|
| **external validity** | `truthometer/results/instrument_external_validity/` | ASAP essay scores, IBM ArgQ, PERSUADE | cc_extval_prep.py, cc_extval_analyse.py | The substance axes have external validity against human quality labels: rigour and depth correlate positively with every human quality measure, holding after the length control (partial +0.18 to +0.23 on PERSUADE); length dominates the raw essay correlation and the partial is the honest, smaller number. |
| **genre state pre registration** | `truthometer/results/prereg_genre_PF-4B/` | reddit communities, frozen genre taxonomy (hash 2d701e0c) | cc_genre_state_fit.py | The first pinned term of the equation of state: on a pre registered, frozen genre assignment with leave communities out cross validation, genre enters as a strong level effect (a location), confirmed on the 27B lineage. This is the foundation the equation of state thread builds on. |
| country affinity floor | `truthometer/results/RESULT_affinity_floor.md` | the scored web, web graph | clean_country_affinity.py | Per country link affinity partners by lift, with honest pass and drop lists; the national link neighbourhoods recover linguistic and historical families. |
| character to personality | `truthometer/results/pandora_character_personality.txt` | Kaggle MBTI fallback (PANDORA gated) | pandora_character_score.py | The eight axes carry a weak but real, directionally sensible trace of author disposition; recoverable signal, not recovery. |
| Upworthy causal anchor | `results/upworthy_causal_character.txt` | Upworthy megastudy | (see results README) | The manner heavy heading causally raises the click across the randomised headline experiments; the causal half of the persuasion funnel. |

**The analyser outputs behind the figures.** The top level of `docs/papers/dynamics_web_series/results/` holds about thirty three saved analyser output files (the `.txt` artifacts named in `results/README.md`), which are the exact numbers behind the figures in the papers: the where and when analyses (`where_when`, `se_when_drift`, `ungd_where_when`, `parlamint_where_who`), the deep time within source proofs (`within_source_*`), the ChangeMyView arbiter analyses, the culture map and its controls, the classical and ancient persuasion read, the fractal dimension, the link earning regularity, and more. These are committed as artifacts, each stamped with its generation time and data state, and all of them regenerate with one script, `truthometer/scripts/run_all_results.sh`, against the scores on the NAS and the `cc_v3` tables. They are analyses that feed the papers rather than standalone packaged experiments, which is why they are artifacts and a regeneration script rather than 33 separate manifest rows.

**So the honest total.** About 90 distinct analyses underlie the programme: the 54 packaged experiments above, the five further studies in this section, and the roughly 33 figure output analyses regenerable from one script. The 54 was the count of one directory, not of the whole; the external validity study and the genre pre registration in particular are central, not peripheral, and are now in the pack.

---

## 5. How to reproduce a single experiment, worked example

Take `reduction_elm`. Its data is IBM ArgQ (public). Fetch or locate the held character scores of ArgQ; if regenerating, score the ArgQ texts with `cc_found_human_score.py`. Build the matter versus manner ruler by singular value decomposition of `cc_v3.domain_char8_expanded` oriented rigour plus depth positive (the script does this). Run `results/reduction_elm/scripts/elm_reduction.py`. Expected: the central pair (rigour plus depth) partial Spearman correlation against the human argument quality label, controlling length, near +0.159, with affect the only negative axis. That pattern is the reduction. Every other row follows the same shape: locate or regenerate the data, rebuild the ruler, run the named analysis script, compare to the headline result.

---

## 6. Release tiers: the cut between public, held, and restricted to the government recipient

Three tiers. A public release of the programme ships tier one only. Tiers two and three never leave with it.

**Tier one, PUBLIC, releasable with the papers.** The shared apparatus of Section 1, every one of the 54 experiment results and their analysis scripts in the manifest, and the papers themselves. This is the science: the instrument and its causal validation, the unification reductions, the coupling geometry as a result, the manipulation signature and its detection, the equation of state, and every international and cross domain finding. All of it is written to be released and carries its own honest bounds.

**Tier two, HELD UNDER REVIEW, reported not released, an intellectual property and privacy hold rather than a security one.** The three internal crawl derivatives: the character reference of about 2.65 million domains (`cc_v3.domain_char8_*`), the cross site pseudonymous authorship corpus (`cc_v3.crosssite_authorship`), and the reddit corpus with per author disposition (`cc_v3.reddit_wide`). Their results and scripts are public in tier one; the raw corpora are not distributed, because they rest on an internal crawl and carry pseudonymous personal data. Anyone with a comparable crawl and the tier one scripts can reproduce the findings. This tier is not government specific; it is simply not published.

**Tier three, RESTRICTED, for the named United Kingdom Government recipient only, never public.** The entire `docs/internal/restricted/` tree, the sword half of the dual use work. It must be cut out of any public release in full. Its inventory:

- `obsidian_coupling/`, the targeting compass (which manipulation pattern lands on which audience disposition, `RESULT.md` and the coupling grids), the evasion surface (the prompts and evasive exemplars that defeat the detector, `EVASION_RESULT.md`, `evasion_generate.py`, `evasion_generated.jsonl`), the inoculation defence expressed through the named vulnerable persona (`INOCULATION_RESULT.md`), and the consolidated deployment manual (`RED_TEAM_MANUAL_UKGOV.md`).
- `radicalisation_signature/DO_NOT_SHARE.md`, the thresholds, weights and tier map that would turn the radicalisation signature into a targeting or blocking tool.
- `criminal_role_character_restricted.md`, the operational specifics of the criminal role work.

**The experiments that have both a public shield half and a restricted sword half, named so the cut is unambiguous:**

| topic | public shield (tier one) | restricted sword (tier three) |
|---|---|---|
| manipulation coupling | `manipulation_character`, `manner_inflation_deception`, `detector_robustness` (the signature, the detector, the honest evasion verdict) | `obsidian_coupling/` (the targeting map, the evasion recipe, the persona level inoculation) |
| radicalisation | `radicalisation_signature/RESULT.md` (the signature, the dose response, the triage prior) | `radicalisation_signature/DO_NOT_SHARE.md` (the thresholds and tier map) |
| criminal roles | `criminal_role_character/RESULT.md` (the honest null under room control) | `criminal_role_character_restricted.md` (the operational specifics) |

**The rule, stated once.** The public tier says a manipulation signature exists and can be detected, that the detector is evadable but evasion costs the attacker its reach, and that these rest on a validated instrument. It never says which manipulation lands on which disposition, never prints an evasion prompt or exemplar, and never gives a threshold that turns a diagnostic into a targeting tool. Those three things are the sword, they live only in tier three, and they go to the government recipient alone. The public half arms defenders and costs attackers nothing they do not already know; the restricted half is the responsible disclosure line and the programme's trade secret. When a public release is assembled, exclude the whole of `docs/internal/restricted/` and do not distribute the tier two corpora; ship the papers, the shared apparatus, and the tier one results and scripts.

---

## 7. Commercial protection: the moat, a fourth axis over the release tiers

The three tiers above govern release for credibility and for national security. Commercial protection is a different question over the same material: what keeps the business defensible. The answer, stated plainly, is that the moat is neither the science nor the sword. The science is published on purpose, because reproducibility is the credibility asset; the sword goes to the government. What a competitor cannot cheaply copy, and what therefore stays held for the business, is the deployed asset. The rule is the one the programme already uses: disclose existence, hold coordinates; the built asset is the method to survey a new region, not the map.

Five things are held for commercial protection, and none of them is in the papers or in this pack:

1. **The production scorer as an artefact.** The papers describe the instrument and release a calibration sample; the runnable production quality scorer stays proprietary, meaning the calibrated model weights, the full calibration set beyond the released sample, and the training and distillation pipeline. A reader has the rubric; they do not have the tuned scorer that makes it work at scale.
2. **The pre computed maps and corpora as assets.** The character reference over the whole scored web, the full web graph, the cross site coupling corpus, and the demand and coupling maps at deployable resolution. The method to build such a map for a new region is published; the pre computed national and sector maps are the near term revenue asset and are held. These overlap the tier two hold, but the commercial reason to keep them is the moat, not only consent.
3. **The operational coordinates.** The papers state that the coupling exists and give its shape; the deployable lookup, which exact character moves which exact audience or decision at production granularity, is the product and is held. Disclose existence, hold coordinates.
4. **The platform and the engineering.** The cost routing layer, the caching work, the memory fabric, the scoring infrastructure and the per vertical pipelines. There is no scientific content in these; they are pure commercial engineering and are never published.
5. **The acquisition strategy.** The gap list and the compass that says where to extend coverage next. Knowing where to expand is itself an edge and appears in no paper.

The tension this resolves. Making the science reproducible for reviewers does not thin the moat, because a reviewer who reproduces a headline on a public benchmark obtains none of the five: not the production scorer, not the scored web, not the coordinates, not the platform, not the roadmap. Publishing the science is therefore safe for the business exactly as long as those five stay held. This pack ships reproducible science and holds all five by construction; a release decision should weigh all four axes at once, public science, privacy held data, government sword, and commercial moat, and confirm that the five commercial holds remain out of whatever is shipped.


### Addendum, later 3 September 2026: the keystone re-survey

- `results/ashlar_atlas/` the full eight by eight disposition to character coupling (the Ashlar map), within room differenced, with a per cell interval and two cross reader legs; richer than the single matter against manner slice and stable across a reader swap.
- `results/d8_robustness/` the disposition instrument's reliability: split half per axis and two reader agreement across model families, with the four reader dependent axes named.
- `results/scale_invariance_matrix/` the four scale test behind the directionally fractal verdict.

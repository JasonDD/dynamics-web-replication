# Global Legislature Character Matrix

DYNAMICS-WEB series, PUBLIC track, INTERNATIONAL. Result written 2026-08-31 (session global-legislature-matrix).

Question. Where does each national legislature sit in the eight axis character space, and does the character of democratic deliberation cluster by region, by colonial or legal heritage (Westminster versus Napoleonic versus other), by democracy age, or by language? And is there a universal parliamentary voice, a shared institutional register across all democracies, with only national deviations, mirroring the invariant core finding elsewhere in the series?

## Verdict

The universal parliamentary voice is the strong result. It is not a clean clustering by heritage or region.

Across 39 legislatures on five continents (13 newly scored world parliaments, the 26 European ParlaMint chambers as reference, and the United Nations general debate as a global diplomatic reference) every legislature's mean character vector points the same way. The cosine between each legislature mean and the shared centre runs from 0.981 to 0.999, mean 0.996. There is one institutional register and its signature is stable everywhere: high candour (0.81, the most invariant axis), high polemical stance (0.70, the second most invariant), a moderate conversational register, and a matter leaning analytic core. Candour and stance are the institutional invariants: an assembly speaks openly and takes sides, wherever it sits.

National differences are real but small. Region and heritage each explain only about six percent of the variance in the matter versus manner axis (region eta squared 0.064, heritage eta squared 0.066). The clean separation by colonial or legal lineage that was the target did not appear as the dominant structure. The strong null, one shared voice, is what the data support, and the task named that outcome as itself a strong finding.

## What the deviations order by, and the honest caveats

The two largest apparent separators are language of record and democracy age, both stronger in the ANOVA than heritage or region. Neither is a clean substantive story:

- Language of record is a measurement confound, not a fact about parliaments. The instrument reads native English, English translation, and non English text differently: native English legislatures average PC1 minus 2.70, the English translated European set minus 1.63, and the three non English chambers minus 0.99. Some of the "matter" the model reads into the translated European and the non English speeches is the flattening effect of translation and the model's own bias on languages it scores unevenly.
- Democracy age is entangled with that same axis. The old democracies in this set are the European chambers scored through translation; the young ones are the African legislatures in native English. So the age effect and the language effect are largely the same confound wearing two labels.

Heritage does cluster, weakly but consistently. In the full eight dimensional space all four legal families (Westminster, Napoleonic and civil, Nordic, post Soviet) have a smaller mean distance within the family than to the rest of the set, with the post Soviet chambers tightest. The direction is interpretable: Westminster chambers sit toward the manner and oratorical end, Napoleonic and civil law chambers toward the matter and analytic end. But the effect is small and confounded with both language and speech length, so it is a second order signal, not the headline.

The most robust cross cutting pattern in the matrix. The African Westminster parliaments (Ghana, Kenya, Nigeria, Zambia, Zimbabwe, South Africa) together with Malaysia are the most manner heavy assemblies anywhere in the set: high register, high candour, more affect, and shorter denser procedural turns. The East Asian chambers (Japan, Korea) and the older or judicial bodies (the United States Supreme Court) are the most matter heavy. This oratorical Africa versus analytic East Asia split is the clearest visible gradient, and it survives the length matched subsample in direction.

## Controls

Length. Longer speeches read as more matter (speech level correlation of length with PC1 is plus 0.209). This is a genuine confound, because hansard turn length differs by chamber: the African hansard sampled here is short procedural exchange, while the Japanese Diet and Supreme Court transcripts are longer. The length matched band (1000 to 3000 characters) keeps the broad order, African Westminster at the manner floor and Japan and the Supreme Court at the matter ceiling, but several cells in that band are tiny (Kenya one speech, Zambia two), so the length matched ranking is only indicative for those chambers.

Translation. The three non English chambers (Japan, Korea, Brazil) were scored in their own language on the multilingual 7B. The Japanese Diet reading as the single most matter legislature in the whole matrix is the most suspect number here and is most likely a translation or language artefact rather than a real institutional fact. The non English rows should be read as a sensitivity check, not as anchor points.

Excluded. Argentina and India were on the target list but their held corpora are session indexes and metadata only, with no speech text (the Argentine file is a table of sitting dates; the Indian Lok Sabha and Rajya Sabha files carry debate titles and links to PDFs, not the debate text). They could not be scored and are flagged here rather than silently dropped.

## Bottom line

The target was a clean clustering by heritage or region. That is not what the data show. What the data show, at global scale and across five continents, is the invariant core result: one shared parliamentary voice, cosine 0.996 to the common centre, with candour and polemical stance as the institutional invariants, and only weak heritage and regional deviations along a single matter versus manner axis, themselves partly confounded by translation and speech length. The universal reading is the strong, honest finding; the heritage and regional structure is real but secondary and entangled with the instrument.

## Reproduce

All on DL580, corpora on the NAS, scored on the on box 7B at :8301 (self queued behind the other scorers), identical prompt and contract to the held ParlaMint and UNGD scoring.

- `build.py` builds the length banded balanced sample (55 speeches per legislature, 400 to 6000 characters) to `/mnt/nas/kronaxis/corpora/results/global_legislature_matrix/sample.jsonl`.
- `score.py` scores the eight axes via :8301 (temperature 0, resumable) to `sample_scored.jsonl` (committed here).
- `analyse.py` builds the matrix, the universal voice check, the clustering tests, and the length and translation controls; its full output is `analysis_out.txt` (committed here, reproduced below).

## Appendix: full analyser output

```text
# Global Legislature Character Matrix — RESULT

Instrument: 8-axis DYNAMICS-WEB character, scored on the on-box 7B (qwen2.5-7b-atlas, :8301, temp 0),
identical prompt/contract to the held ParlaMint + UNGD scoring. PC1 (+ = MATTER, - = MANNER).
PC1 loadings: rigour+0.49  depth+0.55  originality+0.55  candour+0.29  affect-0.03  commercial_drive+0.26  stance+0.11  register+0.07

Speeches scored: new legislatures n=713 (13 legislatures); references ParlaMint n=1675 (26 EU), UNGD n=10556.
EXCLUDED (held corpus is metadata/index only, no speech text): Argentina_Congress, India_LokSabha.

## 1. Legislature x axis matrix (mean per axis; PC1 = matter/manner)

legislature                n   rigo  dept  orig  cand  affe  comm  stan  regi   PC1   heritage/region
-----------------------------------------------------------------------------------------------------
Malaysia_DewanRakyat       55  0.41  0.47  0.30  0.79  0.57  0.17  0.62  0.48  -3.80  Westminster/SE_Asia/mid/en
Zimbabwe_Parliament        55  0.46  0.48  0.30  0.81  0.51  0.15  0.62  0.63  -3.51  Westminster/Southern_Africa/young/en
Zambia_NA                  55  0.51  0.51  0.31  0.82  0.48  0.16  0.66  0.62  -3.01  Westminster/Southern_Africa/young/en
Kenya_Parliament           55  0.53  0.53  0.33  0.82  0.51  0.16  0.68  0.59  -2.69  Westminster/E_Africa/young/en
Nigeria_NASS               55  0.62  0.52  0.29  0.84  0.43  0.13  0.61  0.63  -2.65  Westminster/W_Africa/young/en
Ghana_Parliament           55  0.60  0.53  0.30  0.84  0.47  0.13  0.66  0.71  -2.54  Westminster/W_Africa/young/en
Pan_African_Parliament     55  0.61  0.55  0.35  0.81  0.48  0.19  0.60  0.59  -2.17  Supranational/Africa_Supra/supra/en/SUPRA
Brazil_Chamber             53  0.51  0.54  0.42  0.82  0.70  0.23  0.77  0.55  -2.15  Napoleonic_Civil/S_America/young/native
US_Congress                55  0.61  0.57  0.39  0.83  0.59  0.19  0.73  0.59  -1.73  CommonLaw_Presidential/N_America/old/en
SouthAfrica_NA             55  0.61  0.56  0.40  0.81  0.49  0.22  0.70  0.63  -1.69  Westminster/Southern_Africa/young/en
Korea_NationalAssembly     55  0.68  0.60  0.41  0.84  0.50  0.22  0.64  0.47  -1.14  Civil_Presidential/E_Asia/young/native
SCOTUS                     55  0.75  0.65  0.45  0.83  0.42  0.18  0.64  0.64  -0.49  CommonLaw_Court/N_America/old/en/COURT
Japan_Diet                 55  0.78  0.68  0.51  0.84  0.39  0.23  0.63  0.74  +0.27  Civil_Parliamentary/E_Asia/mid/native

EU ParlaMint reference rows (>=15 speeches), by PC1:
ParlaMint_TR               55  0.39  0.47  0.36  0.75  0.68  0.16  0.75  0.47  -3.70  Other/Europe/old/en_tr
ParlaMint_IS               55  0.47  0.49  0.35  0.76  0.54  0.18  0.65  0.47  -3.30  Nordic/Europe/old/en_tr
ParlaMint_BA               55  0.52  0.51  0.34  0.81  0.51  0.16  0.67  0.53  -2.88  PostCommunist/Europe/young/en_tr
ParlaMint_DK               55  0.50  0.52  0.35  0.79  0.54  0.20  0.69  0.51  -2.75  Nordic/Europe/old/en_tr
ParlaMint_UA               55  0.56  0.52  0.35  0.79  0.47  0.14  0.68  0.58  -2.71  PostCommunist/Europe/young/en_tr
ParlaMint_BG               55  0.57  0.52  0.33  0.81  0.44  0.12  0.66  0.59  -2.70  PostCommunist/Europe/young/en_tr
ParlaMint_HR               55  0.54  0.52  0.39  0.79  0.49  0.17  0.70  0.51  -2.49  PostCommunist/Europe/young/en_tr
ParlaMint_PL               55  0.59  0.54  0.35  0.81  0.51  0.16  0.64  0.56  -2.39  PostCommunist/Europe/young/en_tr
ParlaMint_PT               55  0.59  0.55  0.36  0.78  0.49  0.17  0.82  0.61  -2.13  Napoleonic_Civil/Europe/old/en_tr
ParlaMint_CZ               55  0.56  0.55  0.42  0.82  0.54  0.15  0.67  0.51  -2.11  PostCommunist/Europe/young/en_tr
ParlaMint_RS               55  0.57  0.57  0.39  0.83  0.53  0.15  0.75  0.58  -2.01  PostCommunist/Europe/young/en_tr
ParlaMint_HU               55  0.58  0.56  0.43  0.81  0.62  0.17  0.76  0.49  -1.87  PostCommunist/Europe/young/en_tr
ParlaMint_FI               55  0.60  0.58  0.40  0.81  0.46  0.17  0.67  0.52  -1.86  Nordic/Europe/old/en_tr
ParlaMint_GR               55  0.57  0.59  0.43  0.81  0.60  0.19  0.78  0.57  -1.65  Napoleonic_Civil/Europe/old/en_tr
ParlaMint_SI               55  0.67  0.57  0.37  0.83  0.41  0.15  0.69  0.68  -1.65  PostCommunist/Europe/young/en_tr
ParlaMint_EE               55  0.65  0.58  0.41  0.83  0.47  0.19  0.64  0.58  -1.51  PostCommunist/Europe/young/en_tr
ParlaMint_LV               55  0.65  0.59  0.41  0.83  0.49  0.17  0.78  0.61  -1.39  PostCommunist/Europe/young/en_tr
ParlaMint_AT               55  0.64  0.59  0.41  0.80  0.53  0.21  0.79  0.55  -1.37  Germanic_Civil/Europe/old/en_tr
ParlaMint_SE               55  0.64  0.59  0.43  0.82  0.49  0.21  0.77  0.58  -1.27  Nordic/Europe/old/en_tr
ParlaMint_NL               55  0.65  0.60  0.45  0.83  0.50  0.21  0.76  0.57  -1.03  Napoleonic_Civil/Europe/old/en_tr
ParlaMint_GB               300  0.71  0.61  0.44  0.84  0.45  0.21  0.70  0.68  -0.79  Westminster/Europe/old/en_tr
ParlaMint_FR               55  0.69  0.62  0.47  0.81  0.46  0.23  0.69  0.57  -0.74  Napoleonic_Civil/Europe/old/en_tr
ParlaMint_NO               55  0.68  0.62  0.47  0.82  0.53  0.26  0.80  0.51  -0.61  Nordic/Europe/old/en_tr
ParlaMint_ES               55  0.70  0.65  0.47  0.83  0.51  0.17  0.74  0.63  -0.56  Napoleonic_Civil/Europe/old/en_tr
ParlaMint_BE               55  0.72  0.64  0.47  0.84  0.48  0.20  0.69  0.65  -0.43  Napoleonic_Civil/Europe/old/en_tr
ParlaMint_IT               55  0.69  0.65  0.51  0.85  0.57  0.19  0.80  0.60  -0.33  Napoleonic_Civil/Europe/old/en_tr

UNGD diplomatic reference (n=10556): 0.79 0.69 0.54 0.83 0.45 0.22 0.70 0.60  PC1 +0.40

## 2. Universal-parliamentary-voice check

Shared centre (mean over all national legislatures), per axis:
  rigour=0.60  depth=0.56  originality=0.39  candour=0.81  affect=0.51  commercial_drive=0.18  stance=0.70  register=0.58

Per-axis between-legislature vs within-legislature variance (ICC-like: high ICC = nationally
distinctive; low ICC = institutional invariant shared across all parliaments):
  rigour           between/total eta2=0.177  centre=0.60  -> mixed
  depth            between/total eta2=0.166  centre=0.56  -> mixed
  originality      between/total eta2=0.151  centre=0.39  -> mixed
  candour          between/total eta2=0.073  centre=0.81  -> INVARIANT
  affect           between/total eta2=0.139  centre=0.51  -> mixed
  commercial_drive between/total eta2=0.102  centre=0.18  -> mixed
  stance           between/total eta2=0.092  centre=0.70  -> INVARIANT
  register         between/total eta2=0.124  centre=0.58  -> mixed

Cosine(legislature mean, shared centre): min=0.981 mean=0.996 max=0.999
  (all high -> one shared parliamentary voice with small national deviations)

## 3. What does character cluster by? (PC1 one-way ANOVA + eta^2 over legislatures)

[heritage] one-way ANOVA of PC1 across 9 groups: F=20.10 eta2=0.066
    Other                  n=  55 PC1 -3.70
    PostCommunist          n= 605 PC1 -2.15
    Nordic                 n= 275 PC1 -1.96
    Westminster            n= 685 PC1 -1.94
    CommonLaw_Presidential n=  55 PC1 -1.73
    Germanic_Civil         n=  55 PC1 -1.37
    Civil_Presidential     n=  55 PC1 -1.14
    Napoleonic_Civil       n= 438 PC1 -1.12
    Civil_Parliamentary    n=  55 PC1 +0.27

[region] one-way ANOVA of PC1 across 8 groups: F=22.00 eta2=0.064
    SE_Asia                n=  55 PC1 -3.80
    Southern_Africa        n= 165 PC1 -2.74
    E_Africa               n=  55 PC1 -2.69
    W_Africa               n= 110 PC1 -2.59
    S_America              n=  53 PC1 -2.15
    N_America              n=  55 PC1 -1.73
    Europe                 n=1675 PC1 -1.63
    E_Asia                 n= 110 PC1 -0.43

[age] one-way ANOVA of PC1 across 3 groups: F=45.72 eta2=0.039
    young                  n=1043 PC1 -2.27
    mid                    n= 110 PC1 -1.76
    old                    n=1125 PC1 -1.36

[language] one-way ANOVA of PC1 across 3 groups: F=52.45 eta2=0.044
    en_native              n= 440 PC1 -2.70
    en_translated          n=1675 PC1 -1.63
    native_nonEN           n= 163 PC1 -0.99

## 4. Heritage affinity test (within-heritage vs to-rest mean distance, standardised 8D)

  Westminster        (n=8): within=3.38 to-rest=4.04 -> CLUSTERS
  Napoleonic_Civil   (n=8): within=3.28 to-rest=4.05 -> CLUSTERS
  Nordic             (n=5): within=3.67 to-rest=3.79 -> CLUSTERS
  PostCommunist      (n=11): within=2.59 to-rest=3.59 -> CLUSTERS

## 5. Length control

  speech-level corr(n_chars, PC1) over new legislatures = +0.209  (n=713)
  length-matched (1000-3000 chars, n=228) legislature PC1 rank:
    Zimbabwe_Parliament        n= 5 PC1 -4.49
    Malaysia_DewanRakyat       n=24 PC1 -3.40
    Ghana_Parliament           n=20 PC1 -2.76
    Nigeria_NASS               n=25 PC1 -2.52
    Pan_African_Parliament     n=55 PC1 -2.17
    US_Congress                n=30 PC1 -1.70
    Zambia_NA                  n= 2 PC1 -1.62
    Brazil_Chamber             n=35 PC1 -1.60
    Kenya_Parliament           n= 1 PC1 -1.07
    Korea_NationalAssembly     n= 7 PC1 +0.18
    SCOTUS                     n=12 PC1 +0.36
    Japan_Diet                 n=12 PC1 +0.91

## 6. Translation / language control

  native-non-English legislatures (7B scores these unevenly -> confound):
    Korea_NationalAssembly     PC1 -1.14  (native_nonEN)
    Japan_Diet                 PC1 +0.27  (native_nonEN)
    Brazil_Chamber             PC1 -2.15  (native_nonEN)
  mean PC1: en_native=-2.70  en_translated(EU)=-1.78  native_nonEN=-1.01

(verdict written in RESULT.md prose)

```

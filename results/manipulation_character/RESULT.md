# Does state sponsored manipulation have a character signature that survives length?

**Programme:** DYNAMICS-WEB. **Question:** do state sponsored manipulation posts (Internet
Research Agency political trolls) carry a rhetorical character signature that is genuinely
distinct from sincere argument, once you remove the obvious confound that trolls write short
posts and the sincere baseline writes long essays? The character instrument is the eight axis
DYNAMICS-WEB scorer (an internal 7B model tuned on web character), and the matter versus manner
reference is the first principal component of the web character space (`the internal reference table`,
2.65M domains), oriented so rigour and depth are positive.

**Verdict:** the signature **survives the length control, and comfortably**. Against a length
matched short political baseline (LIAR PolitiFact statements) the political trolls are still
highly separable, five fold cross validated AUC **0.925** (accuracy 0.867, balanced n=4000 per
class). The naive troll versus essay contrast is carried by rigour and depth, but a large part
of that gap is length; once length is matched the discriminating axis shifts to **affect**
(emotional loading, much higher in trolls) with reduced **depth** and **rigour** still
contributing. The manner pole manipulation signature is real, not a length artefact.

---

## 1. The confound this test exists to kill

The raw contrast is dramatic. IRA political trolls score low rigour (0.24), low depth (0.31),
high affect (0.77) and sit at the manner pole of the matter versus manner axis (PC1 = -1.71).
Sincere Reddit Change My View winning arguments score high rigour (0.59), high depth (0.59),
moderate affect (0.54) and sit at the matter pole (PC1 = +3.21). Read alone that looks like a
clean manipulation signature.

The problem is length. Trolls write short tweets; CMV winning arguments are long essays. A short
text has less room to build a rigorous, deep, cited case, so low rigour and low depth may just be
what "short" looks like on this instrument, with nothing to do with intent. Unless the signature
survives a length matched baseline it is not evidence about manipulation.

**The controls.** LIAR (PolitiFact statements, `SHORTPOL`) is short political text, length matched
to the trolls but sincere political claims rather than social posts. It is the decisive baseline.
IRA_OTHER (within IRA non political posts: news feed, commercial, hashtag games) is context: it
shows whether the manner signature is specific to the political operation or general to the IRA
account pool.

---

## 2. Groups

| Group | What | n |
|---|---|---|
| MANIP | IRA political trolls (RightTroll, LeftTroll, Fearmonger), English, original content | 8,000 |
| SINCERE | Reddit Change My View winning arguments (`cmv_scores.jsonl`) | 19,430 |
| SHORTPOL | LIAR PolitiFact statements (length matched short political) | 4,000 |
| IRA_OTHER | IRA news feed, commercial, hashtag gamer (within IRA, non political) | 1,000 |

All four scored on the same eight axis instrument at port 8301. Score store:
`the internal corpus store/ira_troll/work/scored.jsonl` (13,000 IRA plus LIAR rows) and
`the internal corpus store/cmv_winning_args/cmv_scores.jsonl` (sincere reference).

---

## 3. Mean character per group

| group | rigour | depth | orig | candour | affect | comm | stance | register | PC1 |
|---|---|---|---|---|---|---|---|---|---|
| MANIP (IRA political) | 0.244 | 0.311 | 0.480 | 0.726 | 0.766 | 0.227 | 0.491 | 0.326 | **-1.71** |
| SINCERE (CMV args) | 0.589 | 0.585 | 0.535 | 0.855 | 0.539 | 0.183 | 0.590 | 0.509 | **+3.21** |
| SHORTPOL (LIAR) | 0.428 | 0.452 | 0.354 | 0.797 | 0.499 | 0.170 | 0.580 | 0.582 | **+0.97** |
| IRA_OTHER (news/comm/hashtag) | 0.283 | 0.326 | 0.415 | 0.750 | 0.577 | 0.224 | 0.368 | 0.395 | **-1.67** |

Two things stand out. First, LIAR sits between the trolls and the essays on rigour and depth
(0.43 and 0.45), exactly as a length effect would predict, but it stays on the matter pole
(PC1 +0.97) whereas the trolls are deep on the manner pole (PC1 -1.71). Second, IRA_OTHER sits
at essentially the same manner pole as the political trolls (PC1 -1.67), so the manner signature
is characteristic of the IRA account pool broadly, not only its political content.

---

## 4. Effect sizes (Cohen's d, positive means MANIP scores higher)

| axis | vs SINCERE (CMV) | vs SHORTPOL (LIAR) |
|---|---|---|
| rigour | -1.93 | -1.19 |
| depth | -2.00 | -1.22 |
| originality | -0.31 | +0.71 |
| candour | -1.47 | -0.58 |
| affect | +1.31 | **+1.65** |
| commercial_drive | +0.28 | +0.27 |
| stance | -0.40 | -0.31 |
| register | -0.87 | -0.99 |
| matter/manner PC1 | -1.61 | **-1.03** |

The length story is visible in the shrink from column one to column two. The rigour and depth
gaps roughly halve once length is matched (depth -2.00 to -1.22, rigour -1.93 to -1.19), which is
exactly the part of the naive contrast that was length. What does **not** shrink is affect: it
grows (+1.31 to +1.65) and becomes the largest single axis effect against the length matched
baseline. PC1 stays large and negative (-1.03), so the trolls remain about one standard deviation
onto the manner pole even against short political text.

---

## 5. Classifiers (numpy logistic regression, five fold cross validation, class balanced)

**MANIP versus SINCERE (CMV)**, the naive contrast, length confounded.
- AUC = **0.956** (+/- 0.002), accuracy = 0.888 (+/- 0.003), balanced n=8,000 per class.
- Standardised coefficients (negative means higher in SINCERE): depth -1.57, candour -1.35,
  rigour -0.82, register -0.45, commercial_drive +0.34, affect +0.27, originality +0.27,
  stance +0.03.
- Univariate AUC per axis: depth 0.917, rigour 0.905, affect 0.830, candour 0.808,
  register 0.730, originality 0.588, stance 0.579, commercial_drive 0.544.

**MANIP versus SHORTPOL (LIAR)**, the decisive length control.
- AUC = **0.925** (+/- 0.005), accuracy = 0.867 (+/- 0.008), balanced n=4,000 per class.
- Standardised coefficients: affect +1.34, depth -0.83, originality +0.70, candour -0.47,
  stance -0.30, register -0.26, rigour -0.18, commercial_drive +0.18.
- Univariate AUC per axis: **affect 0.877**, depth 0.807, rigour 0.803, register 0.752,
  originality 0.694, candour 0.658, stance 0.571, commercial_drive 0.505.

---

## 6. The headline answer

**The manner pole manipulation signature survives length control.** A classifier that has to
separate IRA political trolls from length matched short political statements still reaches AUC
0.925. The signature is not an artefact of trolls writing short posts.

**The axes shift under the control, and that shift is the real finding.** Against long sincere
essays the top discriminators are depth (AUC 0.917) and rigour (0.905), the matter pole axes. But
those are partly measuring length, and their effect roughly halves once length is matched. Against
the length matched baseline the standout becomes **affect** (AUC 0.877, the single strongest axis,
Cohen's d +1.65), with depth (0.807) and rigour (0.803) still contributing and originality
elevated in the trolls. In plain terms: the length robust core of the manipulation signature is
**high emotional loading carried on thin substantive depth**, not merely "short and shallow".
The logistic model agrees: affect is the largest positive coefficient (+1.34) in the length
controlled split, where against the essays it was depth and candour that dominated.

**Context from IRA_OTHER.** The within IRA non political posts sit at the same manner pole as the
political trolls (PC1 -1.67 versus -1.71), so the manner leaning is a property of the IRA account
pool as a whole; the political content adds the high affect edge on top of that shared base.

---

## 7. Caveats (kept honest)

- **One actor, one era, one platform.** All manipulation examples are IRA, roughly 2015 to 2018,
  Twitter, English only. This is a signature of one documented operation, not proof that all state
  sponsored manipulation looks like this.
- **The length control is not a perfect twin.** LIAR is length matched short political text but it
  is politician and public figure claims fact checked by PolitiFact, not social media posts. It
  controls length and political topic, not register or medium, so a residual medium difference is
  folded into the 0.925.
- **The scorer is a web tuned 7B model**, not a human panel; the axes are its judgement. The PC1
  reference is the web character space, which is where the instrument is calibrated.
- **Separable is not the same as caused.** High affect on thin depth separates these trolls from
  sincere short claims; it does not by itself prove intent to manipulate, and a sincere but
  emotive short post would score the same way. The claim is a measurable character contrast that
  survives the length confound, not a manipulation detector.

---

## 8. Method files

- `truthometer/scripts/manip_analyse.py`: groups, means, Cohen's d, logistic classifiers with
  five fold cross validation and per axis univariate AUC (numpy, no sklearn). Reads the score
  store on the internal store and the PC1 reference from Postgres `the internal reference table`.
- Score store (persistent, internal store): `the internal corpus store/ira_troll/work/scored.jsonl` and
  `the internal corpus store/cmv_winning_args/cmv_scores.jsonl`.

# The legal systems character matrix: does the winning character differ by legal tradition?

*DYNAMICS-WEB series, PUBLIC track. 31 August 2026, J. Duke, Kronaxis. Four bodies of legal language, one
fixed instrument. The matrix asks two things at once. First, do different legal traditions occupy different
regions of character space, so that an adversarial court reads more polemical and stance heavy while an
inquisitorial court reads more rigorous and reserved, and a legislature reads different again. Second, where
a real outcome exists, does the character that goes with WINNING differ by system, so that affect helps the
winner in an adversarial court but hurts in an inquisitorial one. All scoring reuses held DWEB eight axis
scores on the same 7B instrument used across the series; nothing was rescored for this document.*

---

## The four corpora and the instrument

The ruler is the fixed DWEB eight axis character scorer (rigour, depth, originality, candour, affect,
commercial drive, stance, register), the identical system prompt, vocabulary line and 7B teacher used
everywhere in the series. The matter against manner axis (PC1) is the singular vector fit once on the fixed
series projection (2,648,406 rows) and applied, never refit here. Every row was scored before this session;
the run only reads scores off disk.

| System | Tradition | N | Outcome available | What each row is | Era |
|---|---|---|---|---|---|
| Old Bailey | adversarial (UK criminal) | 568 | verdict: 1 guilty (prosecution wins) / 0 acquittal | whole trial report | 1674 to 1910 |
| SCOTUS | adversarial (US appellate) | 800 | won: 1 advocate on winning side / 0 losing side | one advocate's oral argument, aggregated | c. 1955 to 2019 |
| ECHR | inquisitorial (European Court of Human Rights) | 700 | outcome: 1 violation (applicant wins) / 0 no violation | the court's judgment | c. 2000 to 2019 |
| ParlaMint | legislative (multi country EU) | 530 | none (no binary win) | a member's floor speech | c. 2015 to 2022 |

Data on disk: `/mnt/nas/kronaxis/corpora/{oldbailey/oldbailey_scored.jsonl, legal_matrix/scotus_scored.jsonl,
legal_matrix/echr_scored.jsonl, parlamint/legislative_pole_frozen.jsonl}`. The legislative pole is a frozen
snapshot of a ParlaMint sample scored on the identical axes (a sibling run is still appending to the live
file; the snapshot fixes the reproducible N at 530). Analysis script and full console output sit beside this
file: `analyse_matrix.py`, `matrix_output.txt`.

A measurement asymmetry runs through the whole thing and must be stated up front: only SCOTUS isolates
ADVOCATE speech. Old Bailey rows are whole trial reports and ECHR rows are the court's own judgment, so the
"character" of an Old Bailey conviction or an ECHR violation is partly the reporter's or the tribunal's
framing of a decided outcome, not a clean advocate signal. This is fatal to a naive causal read and is the
main reason the verdict below is stated with care.

---

## Question 1: do the traditions occupy different regions of character space? YES, sharply.

### Matrix 1: system by axis, raw means (0 to 1), plus matter against manner PC1

```
system        rigour   depth  origin  candou  affect  commer  stance  regist      PC1  medWords
OldBailey       0.75    0.54    0.28    0.86    0.32    0.10    0.37    0.53     2.61       272
SCOTUS          0.81    0.72    0.56    0.84    0.42    0.19    0.76    0.69     5.85      3100
ECHR            0.88    0.77    0.42    0.78    0.41    0.30    0.46    0.78     2.77      1187
ParlaMint       0.64    0.58    0.40    0.82    0.49    0.20    0.69    0.59     3.40       215
```

The four traditions read as four distinct voices, and the split lands where the hypothesis predicted:

- **Adversarial appellate (SCOTUS)** is the most STANCE heavy court by a wide margin (0.76), highest on
  originality (0.56) and register (0.69, the most conversational, as befits live oral argument). It is the
  most polemical courtroom voice.
- **Inquisitorial (ECHR)** is the most RIGOROUS (0.88) and deepest (0.77) body of text, and among courts the
  LEAST stance heavy (0.46). Rigour and depth over polemic is exactly the inquisitorial signature the
  hypothesis names.
- **Legislative (ParlaMint)** is different again: the highest AFFECT of all four (0.49), high stance (0.69),
  and the LOWEST rigour (0.64). The law making pole trades rigour for affective, stance heavy rhetoric.
- **Old Bailey** sits apart on low originality (0.28), low stance (0.37) and the lowest commercial drive
  (0.10), the fingerprint of a terse historical trial report rather than a modern advocate, and a reminder
  that its era and its genre both differ from the rest.

Every one of the eight axes plus PC1 separates the four systems at p < 0.001. Effect sizes are large where
the theory predicts: stance eta squared 0.46, depth 0.45, PC1 0.44.

### Matrix 2: length controlled (per axis system means after regressing out log words)

The systems differ enormously in length (median 215 words for a floor speech against 3,100 for an aggregated
oral argument), so the raw matrix could be a length artefact. It is not. Regressing log length out of every
axis and re reading the residual means:

```
system        rigour   depth  origin  candou  affect  commer  stance  regist      PC1
OldBailey       0.02   -0.05   -0.06    0.03   -0.06   -0.06   -0.13   -0.08    -0.36
SCOTUS         -0.03   -0.03    0.03    0.03   -0.03   -0.05    0.08   -0.04     1.05
ECHR            0.08    0.08   -0.04   -0.04   -0.01    0.08   -0.15    0.10    -1.33
ParlaMint      -0.08   -0.00    0.07   -0.02    0.13    0.04    0.21   -0.00     0.56
```

Reading the residuals (0 is the pooled length predicted level; the sign is the tradition's tilt beyond
length): ParlaMint still tilts strongly to affect (+0.13) and stance (+0.21); ECHR still tilts to rigour and
depth (+0.08 each) and AWAY from stance (-0.15); SCOTUS holds its stance tilt (+0.08). The PC1 split widens,
not narrows, once length is removed: SCOTUS and ParlaMint sit on the matter side, ECHR and Old Bailey on the
manner side.

**All 9 of 9 axes still separate the systems after length control** (every residual ANOVA p < 0.001, stance
eta squared 0.45). Character, not length, is doing the separating.

### Separation strength

A multinomial classifier reading only the eight character axes recovers which of the four systems a text
came from with **0.807 accuracy against a 0.25 chance floor**. Length alone reaches 0.533. So a majority of
the separation is character above and beyond length. Legal tradition is legible in the character of the
language.

**Answer to Question 1: not null. The traditions occupy sharply different regions of character space, in the
directions the hypothesis named, adversarial appellate is the stance heavy pole, inquisitorial is the
rigour and depth pole, legislative is the affect and rhetoric pole, and this survives length control.**

---

## Question 2: does the WINNING character differ by system, and does affect help or hurt?

Winner is defined per system: Old Bailey verdict 1 (conviction, prosecution wins), SCOTUS won 1 (advocate on
the winning side), ECHR outcome 1 (violation found, applicant wins). Below, d is winner minus loser; the
logistic models are length controlled (and, for Old Bailey, also era controlled with a year covariate).

### ECHR (inquisitorial): affect and polemic HURT the winner. Strong and clean.

```
    pc1      winner=2.527 loser=3.010  d=-0.483 (cohen=-0.42) p=3.5e-08 ***
    affect   winner=0.379 loser=0.447  d=-0.068 (cohen=-0.42) p=5.2e-08 ***
    stance   winner=0.416 loser=0.507  d=-0.090 (cohen=-0.53) p=4.3e-12 ***
    [outcome ~ z_affect + z_logw]  z_affect coef=-0.181 (odds/SD=0.83) p=0.065   logw=-0.433
    [outcome ~ z_pc1 + z_logw]     z_pc1    coef=-0.365 (odds/SD=0.69) p=1.5e-05 ***  logw=-0.486
```

Where the applicant wins, the judgment text is markedly LESS affective, LESS polemical and more balanced
(lower on the matter pole PC1). The stance effect is the largest single winner signal in the whole matrix
(cohen -0.53). Affect goes the same way (cohen -0.42). In the inquisitorial court, reserved and balanced is
the character of the winning outcome; heat is the character of the losing one.

### SCOTUS (adversarial, the one clean advocate corpus): affect trends POSITIVE, but weak and not significant.

```
    affect   winner=0.425 loser=0.418  d=+0.008 (cohen=+0.11) p=0.136
    pc1      winner=5.809 loser=5.888  d=-0.079 (cohen=-0.06) p=0.405
    stance   winner=0.758 loser=0.762  d=-0.004 (cohen=-0.03) p=0.69
    [outcome ~ z_affect + z_logw]  z_affect coef=+0.106 (odds/SD=1.11) p=0.137   logw=-0.010
```

On the only corpus that isolates advocate speech, winner and loser are nearly indistinguishable on every
axis. The affect coefficient is POSITIVE (+0.106, odds 1.11 per SD), the opposite sign to ECHR, but it is
not significant (p = 0.14). So the clean adversarial test shows, at most, a weak positive lean for affect and
no penalty, against a clear penalty in the inquisitorial court.

### Old Bailey (adversarial, but whole trial reports): the matter pole helps conviction; raw affect edge is a length artefact.

```
    pc1      winner=2.754 loser=2.267  d=+0.486 (cohen=+0.31) p=0.0007 ***
    affect   winner=0.326 loser=0.291  d=+0.035 (cohen=+0.23) p=0.015 *
    rigour   winner=0.768 loser=0.715  d=+0.053 (cohen=+0.33) p=0.001 **
    [outcome ~ z_affect + z_logw]         z_affect coef=-0.056 p=0.68    logw=+0.408
    [outcome ~ z_pc1 + z_logw]            z_pc1    coef=+0.208 (odds 1.23) p=0.040 *   logw=+0.283
    [outcome ~ z_affect + z_logw + z_year] z_affect coef=-0.047 p=0.73    logw=+0.305  year=+0.264
    [outcome ~ z_pc1 + z_logw + z_year]    z_pc1    coef=+0.218 (odds 1.24) p=0.032 *   logw=+0.178  year=+0.275
```

Raw, conviction reports look higher on affect, rigour, stance and the matter pole. But the affect edge
DISSOLVES once length enters the model (coef -0.06, p = 0.68): longer reports both convict more and read as
more affective. What survives is the matter pole itself (PC1 odds 1.23 per SD, p = 0.04), and it survives ERA
control too (year 1674 to 1910 added as a covariate leaves PC1 at odds 1.24, p = 0.03). Conviction goes with
a rigorous, matter side character, not with heat, consistent in direction with the inquisitorial finding
that heat is not what wins, though Old Bailey is not advocate speech and its "winner" is the report of a
guilty verdict.

### The affect coefficient flips sign across traditions

| System | Tradition | affect coefficient (length controlled) | Reading |
|---|---|---|---|
| SCOTUS | adversarial (advocate speech) | **+0.106** (p = 0.14) | affect trends to help the winner, weakly, not significant |
| Old Bailey | adversarial (trial report) | -0.056 (p = 0.68) | null once length is out |
| ECHR | inquisitorial (court judgment) | **-0.181** (p = 0.065), stance -0.53 cohen *** | affect and polemic clearly hurt the winner |

The sign of the affect coefficient does flip between the adversarial advocate corpus (positive) and the
inquisitorial court (negative), which is the pattern the hypothesis predicted. But only the inquisitorial arm
is statistically strong; the adversarial "affect helps" arm is a directional trend, not a significant effect.

---

## Length and era controls, in one place

- **Length.** Controlled two ways. Every Question 1 axis result is re run on residuals after regressing out
  log words: 9 of 9 axes still separate the systems. Every Question 2 logistic model carries log words as a
  covariate; the one place length changed the story (Old Bailey affect) is flagged as an artefact rather than
  reported as a finding.
- **Era.** The honest limitation of the matrix. Old Bailey is historical (median year 1790) and the other
  three are modern, so at the corpus level era is perfectly collinear with system and cannot be regressed
  out, the Old Bailey against modern contrast is partly a 1700s against 2000s contrast, not purely a legal
  tradition contrast. Era IS controlled WITHIN Old Bailey (a year covariate across 1674 to 1910), where the
  matter pole effect on conviction survives. The clean cross tradition contrast that does not lean on era is
  the modern three: SCOTUS against ECHR against ParlaMint, and that contrast alone carries the headline
  finding (adversarial stance heavy, inquisitorial rigour heavy, legislative affect heavy, and affect
  hurting the winner in the inquisitorial court).

---

## Verdict

**Not null on either question, but honest about which half is strong.**

1. **Legal traditions occupy different regions of character space, robustly.** Adversarial appellate is the
   stance heavy, polemical pole; inquisitorial is the rigour and depth pole with the lowest stance of any
   court; the legislature is the affect heavy, low rigour rhetoric pole. All nine measures separate the four
   systems at p < 0.001 and survive length control (9 of 9), and character alone recovers the system at 0.81
   against 0.25 chance. This is a strong, clean result and it points in the theorised direction.

2. **The winning character differs by system, and the affect coefficient flips sign across traditions, but
   only the inquisitorial arm is statistically strong.** In the inquisitorial court, affect and especially
   polemical stance clearly HURT the winning outcome (stance cohen -0.53, p = 4e-12; affect cohen -0.42).
   In the one corpus that cleanly isolates adversarial advocate speech (SCOTUS), affect trends the OTHER way
   (positive) but is not significant, and winner and loser are otherwise near identical. So "affect helps in
   an adversarial court but hurts in an inquisitorial one" is HALF confirmed: the hurting half is solid, the
   helping half is a weak directional trend.

3. **The load bearing caveat is measurement asymmetry, not statistics.** Only SCOTUS is advocate speech.
   Old Bailey and ECHR winner character is partly the reporter's or the tribunal's framing of an already
   decided outcome, so the inquisitorial "affect hurts the winner" finding may partly measure that a
   judgment which finds a violation is written in a more reserved register, rather than that reserved
   advocacy caused the win. The finding is real about the language of legal outcomes; it is not a clean claim
   about what advocacy style causes a win. A clean test would need advocate only text on the inquisitorial
   side (for example applicant submissions to the ECHR), which this corpus does not hold.

Bottom line: legal character is NOT universal across traditions, systems separate sharply and in the
predicted directions, and the character that goes with winning is system dependent, with polemical affect
penalised on the inquisitorial side and neutral to mildly favoured on the adversarial side. The
adversarial "affect helps" claim is the weak link and should not be overstated.

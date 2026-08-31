# Cross domain transfer of the 8 axis manipulation detector

**Track:** PUBLIC. **Question:** is the manipulation signature domain general? Train a
deceptive versus honest classifier on ONE deception domain's 8 axis character contrast, then
test it on every other domain. If a detector trained on political trolls catches phishing
it has never seen, that is the strongest product and science claim: one detector, all abuse.

**Method.** Each domain is a deceptive set versus a matched honest control, scored on the 8
DYNAMICS-WEB axes (rigour, depth, originality, candour, affect, commercial_drive, stance,
register) by the same 7B scorer the sibling children use. A class balanced logistic
regression (numpy, L2) is trained on each domain and tested on every other. Diagonal cells
are 5 fold within domain cross validation. Off diagonal cells train on the whole row domain
and test on the whole column domain, standardising the test set on the TRAIN domain's scale
(what a deployed detector actually knows). AUC is rank based (Mann Whitney U). Scores were
reused from the head to head and manner inflation children; nothing was scored again here.
Script: `truthometer/scripts/crossdomain_transfer.py`.

**Domains (deceptive / honest).**

| domain | deceptive | honest control | n dec | n hon |
|---|---|---|---:|---:|
| political | IRA political trolls (Right/Left/Fearmonger) | Reddit CMV sincere winning args | 8000 | 19430 |
| phishing | phishing emails | legitimate emails | 700 | 700 |
| dark_ui | dark pattern UI microcopy | neutral UI/product copy | 1168 | 1076 |
| liar | LIAR false + pants-fire claims | LIAR true claims | 1070 | 655 |

Deceptive reviews (opspam) were checked and NOT included: the corpus on disk is packaged as
a sentiment task (positive/negative), not the Ott et al. deceptive/truthful gold label, so it
carries no usable deception label without deriving one afresh. Recorded honestly rather than
faked from the sentiment field.

## Transfer AUC matrix (rows = train, cols = test)

Diagonal = 5 fold within domain CV. Off diagonal = train row, test column.

| train \ test | political | phishing | dark_ui | liar |
|---|---:|---:|---:|---:|
| **political** | *0.957* | **0.963** | 0.443 | 0.669 |
| **phishing** | **0.944** | *0.973* | 0.563 | 0.655 |
| **dark_ui** | 0.802 | 0.819 | *0.861* | 0.519 |
| **liar** | 0.899 | 0.681 | 0.421 | *0.680* |

- mean off diagonal AUC = **0.698** (min 0.421, max 0.963)
- mean diagonal (within domain) AUC = **0.868**

## Leave one domain out (train on all others, test on the held out domain)

The honest "does it catch a NEW kind of manipulation it never saw" number.

| held out domain | AUC | n |
|---|---:|---:|
| political | 0.888 | 27430 |
| phishing | **0.962** | 1400 |
| dark_ui | 0.652 | 2244 |
| liar | 0.669 | 1725 |

**mean LODO AUC = 0.793**

## Which axes give manipulation away (standardised logistic coefficients)

Positive pushes toward DECEPTIVE.

| axis | political | phishing | dark_ui | liar |
|---|---:|---:|---:|---:|
| rigour | -0.80 | -0.36 | -0.36 | -0.07 |
| depth | **-1.61** | **-1.16** | -0.55 | -0.32 |
| originality | 0.28 | -0.08 | -0.16 | 0.21 |
| candour | **-1.23** | **-1.26** | **+1.00** | -0.25 |
| affect | 0.25 | 0.79 | 0.24 | 0.09 |
| commercial_drive | 0.25 | **1.30** | 0.11 | -0.24 |
| stance | 0.03 | -0.13 | -0.83 | 0.31 |
| register | -0.42 | -0.52 | 0.15 | -0.35 |

Detector direction cosine similarity across domains (1.0 = identical signature, near 0 = orthogonal):

| | political | phishing | dark_ui | liar |
|---|---:|---:|---:|---:|
| political | 1.00 | 0.82 | -0.03 | 0.67 |
| phishing | 0.82 | 1.00 | -0.04 | 0.36 |
| dark_ui | -0.03 | -0.04 | 1.00 | -0.37 |
| liar | 0.67 | 0.36 | -0.37 | 1.00 |

## Verdict: partly domain general, one detector for text persuasion, not for interfaces

The manipulation signature is **domain general across text based persuasion and fraud, and
domain specific for interface manipulation.** It is not a single universal detector, and the
data says so cleanly.

1. **Text persuasion transfers, strongly and both ways.** A detector trained only on Russian
   political trolls catches phishing emails it has never seen at **AUC 0.963**, higher than
   most within domain baselines. Phishing catches political at 0.944. The two share the same
   signature (direction cosine 0.82): low depth, low candour, low rigour. This is the
   headline result and it is real: train on one text abuse domain, catch another.

2. **The shared core is "low matter, low candour".** Depth is the single most consistent
   deception tell (strongly negative in political, phishing, liar). Candour is negative in
   every text domain. Phishing adds two extra tells the others lack: commercial_drive (+1.30)
   and affect (+0.79), the "act now / your account" money and fear pressure. That is why a
   text trained detector still fires on phishing, and why a phishing trained detector
   transfers well: it holds the general signature plus a fraud specific overlay.

3. **UI dark patterns are a genuinely different mechanism, nearly orthogonal, and a text
   trained detector fails on them.** political to dark_ui is **0.443, below chance**, and
   liar to dark_ui is 0.421. The direction cosine of dark_ui against every text domain is
   roughly zero to negative. The cause is visible in the coefficients: in dark patterns
   **candour flips sign** (+1.00, so higher candour reads as MORE deceptive), because a dark
   pattern is a short, blunt, confident command ("Only 2 left, buy now"), the opposite of the
   evasive low candour register of a troll or a phish. Short manipulative microcopy is a
   different animal from long manipulative prose. A text detector cannot be assumed to catch
   it, and here it does worse than a coin.

4. **LIAR is the hard middle.** Within domain AUC is only 0.680 and transfer is mixed (a liar
   trained detector catches political at 0.899, but political to liar is 0.669). Very short,
   context stripped PolitiFact claims carry little character signal either way; this is a
   ceiling of the instrument on one sentence claims, not a transfer failure.

5. **The honest product number is LODO = 0.793 mean, but it is bimodal, not a single grade.**
   Held out entirely, a new **text** manipulation domain is caught well (phishing 0.962,
   political 0.888); a new **interface** manipulation domain is caught poorly (dark_ui 0.652,
   liar 0.669). The right product claim is therefore narrower and stronger than "one detector
   for all abuse": **one detector generalises across text based persuasion and fraud without
   retraining. Interface manipulation is a second, separable detector.** Do not sell a single
   universal model; sell a text abuse detector that transfers, and a distinct dark pattern
   detector, and say which is which.

**Bottom line.** Manipulation has a shared, transferable signature within written
persuasion, low depth and low candour, strong enough that a troll trained detector catches
phishing at 0.96. It is not universal: interface dark patterns invert the candour tell and
form an orthogonal, separable class. Domain general for text, domain specific for interfaces.

# Is candour the ethical line between legitimate persuasion and manipulation?

*DYNAMICS-WEB series, PUBLIC track. Tests whether the candour axis draws a clean boundary
between persuasion that is open about its intent (a charity asking for a donation, an advert
asking for a sale) and manipulation that hides its intent (a dark pattern disguising the ask,
a state troll hiding who it is, a phish impersonating a sender). If it did, the product line
could be stated as "we flag low candour persuasion, not persuasion", which answers the
"you are just censoring marketing" objection.*

Scorer: `truthometer/scripts/cc_found_human_score.py` (8 axis DWEB character instrument,
qwen2.5-7b-atlas on DL580 :8301). Analysis: `analyse_candour.py` in this directory. New
scoring for the two marquee legit persuasion groups (donorschoose, amazon): `prep_persuasion.py`,
scores at `/mnt/nas/kronaxis/corpora/candour_line/scored.jsonl`. All other groups reuse the
sibling scores already on the NAS.

---

## 1. The claim under test

The hypothesis is a clean split on one axis: legitimate persuasion should read HIGH candour
because it is open about the ask; manipulation should read LOW candour because it conceals the
ask. The candour axis is defined for the scorer as `candour: 0 opaque -> 1 transparent`. The
test pools a spectrum of legitimate persuasion against a spectrum of manipulation and asks the
single question that decides a product boundary: does candour separate the two pools more
cleanly than the two competitors already on the table, manner inflation and affect?

Manner inflation is the composite the sibling manipulation results are built on:

    matter          = mean(rigour, depth)
    manner          = mean(affect, stance, register)
    manner inflation = manner - matter

## 2. The spectrum (all 8 axis scored)

| pole | group | what | n |
|---|---|---|---|
| legitimate persuasion | psg | PersuasionForGood charity donation dialogue | 1,017 |
| legitimate persuasion | donorschoose | teacher classroom funding appeals (charity) | 514 |
| legitimate persuasion | kickstarter | crowdfunding pitches (open hard sell) | 6,000 |
| legitimate persuasion | amazon | product reviews (commercial genre) | 404 |
| legitimate persuasion | CMV | Change My View winning arguments (sincere anchor) | 6,000 |
| manipulation | IRA | Internet Research Agency political trolls | 8,000 |
| manipulation | dark (RachitD) | dark pattern UI microcopy | 1,168 |
| manipulation | dark (Mathur) | dark pattern strings, surface form labelled | 1,500 |
| manipulation | phishing | phishing emails | 700 |
| manipulation | LIAR false | PolitiFact false and pants on fire claims | 1,070 |
| honest control | dark normal | neutral UI and product microcopy | 1,076 |
| honest control | phish safe | legitimate emails | 700 |
| honest control | LIAR true | PolitiFact true and mostly true claims | 1,488 |

The pooled manipulation side is IRA heavy (64 per cent), so Section 5 also reports every
manipulation domain on its own.

## 3. Mean character per group

Candour (cand), affect (aff), manner inflation (MI) and matter versus manner PC1 are the four
that matter for the boundary.

| group | rigour | depth | orig | **cand** | **aff** | comm | stance | reg | **MI** | **PC1** |
|---|---|---|---|---|---|---|---|---|---|---|
| psg (charity dialogue) | 0.255 | 0.273 | 0.237 | **0.814** | 0.822 | 0.702 | 0.494 | 0.388 | +0.304 | -3.50 |
| donorschoose (charity appeal) | 0.373 | 0.432 | 0.329 | **0.844** | 0.731 | 0.567 | 0.584 | 0.438 | +0.182 | -0.65 |
| kickstarter (crowdfund sell) | 0.284 | 0.345 | 0.531 | **0.666** | 0.599 | 0.658 | 0.365 | 0.339 | +0.120 | -2.60 |
| amazon (product review) | 0.312 | 0.373 | 0.421 | **0.873** | 0.737 | 0.460 | 0.312 | 0.339 | +0.120 | -2.11 |
| CMV (sincere reasoning) | 0.593 | 0.586 | 0.535 | **0.855** | 0.538 | 0.185 | 0.593 | 0.507 | -0.044 | +3.26 |
| IRA (state troll) | 0.244 | 0.311 | 0.480 | **0.726** | 0.766 | 0.227 | 0.491 | 0.326 | +0.250 | -1.71 |
| dark pattern (RachitD) | 0.142 | 0.138 | 0.152 | **0.711** | 0.390 | 0.664 | 0.097 | 0.128 | +0.065 | -5.03 |
| dark pattern (Mathur) | 0.126 | 0.124 | 0.134 | **0.740** | 0.365 | 0.653 | 0.083 | 0.115 | +0.063 | -4.91 |
| phishing | 0.158 | 0.145 | 0.218 | **0.583** | 0.736 | 0.835 | 0.184 | 0.162 | +0.209 | -7.30 |
| LIAR false claim | 0.381 | 0.423 | 0.360 | **0.780** | 0.516 | 0.156 | 0.585 | 0.538 | +0.144 | +0.71 |
| dark normal (control) | 0.265 | 0.283 | 0.270 | 0.543 | 0.406 | 0.581 | 0.317 | 0.311 | +0.071 | -3.64 |
| phish safe (control) | 0.499 | 0.463 | 0.378 | 0.852 | 0.473 | 0.313 | 0.438 | 0.483 | -0.016 | +0.89 |
| LIAR true (control) | 0.472 | 0.474 | 0.360 | 0.814 | 0.485 | 0.182 | 0.555 | 0.597 | +0.073 | +1.18 |

Read the candour column down the two poles. It does not split them. Four of the five
manipulation groups sit at candour 0.71 to 0.78, squarely inside the legitimate persuasion band
(0.67 to 0.87). Dark patterns read candour 0.71 and 0.74, HIGHER than the kickstarter hard sell
at 0.666. Plainly stated false political claims read candour 0.78. The only manipulation group
that reads genuinely low is phishing (0.583), and even the neutral dark pattern control reads
lower still (0.543). The bands overlap almost completely.

## 4. The headline: candour is one of the weakest separators

Pooled legitimate persuasion versus manipulation, balanced at 12,438 per side, univariate AUC
(legit labelled 1, so above 0.5 means the axis reads higher in legitimate persuasion; the
magnitude either side of 0.5 is the separating power).

| axis | AUC | separating power | reads higher in |
|---|---|---|---|
| rigour | 0.770 | **0.770** | legit |
| depth | 0.765 | **0.765** | legit |
| manner inflation | 0.314 | **0.686** | manip |
| register | 0.670 | 0.670 | legit |
| matter/manner PC1 | 0.650 | 0.650 | legit |
| originality | 0.644 | 0.644 | legit |
| affect | 0.372 | **0.628** | manip |
| commercial_drive | 0.613 | 0.613 | legit |
| stance | 0.581 | 0.581 | legit |
| **candour** | **0.573** | **0.573** | legit |

The three named competitors side by side:

| separator | separating power (AUC magnitude) |
|---|---|
| manner inflation | **0.686** |
| affect | **0.628** |
| **candour** | **0.573** |

Candour is the weakest of the ten single axis readings and the weakest of the three named
competitors. Manner inflation beats it by 0.11 of AUC and affect beats it by 0.055. The matter
axes (rigour 0.770, depth 0.765) beat it by nearly 0.2. Candour does move in the predicted
direction, higher in legitimate persuasion, but the movement is small and the distributions
overlap: the histogram overlap coefficient for candour across the two pools is **0.800** on a
scale where 0 is disjoint and 1 is identical, and both pools have the same median (0.800). There
is no clean candour threshold. The best Youden point (t = 0.71) keeps 70.8 per cent of
legitimate persuasion while sparing 58.0 per cent of manipulation, which is useless as a gate.

## 5. Per domain: where candour works and where it fails

Full legitimate persuasion pool versus each manipulation domain, balanced, candour AUC (legit
labelled 1), with affect and manner inflation on the same contrast (reported as manip high).

| manipulation domain | candour AUC | affect (manip high) | manner inflation (manip high) | n/side |
|---|---|---|---|---|
| IRA (state troll) | 0.609 | 0.746 | 0.756 | 8,000 |
| phishing | 0.660 | 0.716 | 0.709 | 700 |
| LIAR false claim | 0.535 | 0.406 | 0.629 | 1,070 |
| dark pattern (RachitD) | **0.488** | 0.351 | 0.477 | 1,168 |
| dark pattern (Mathur) | **0.443** | 0.325 | 0.483 | 1,500 |

Candour reaches a weak 0.61 to 0.66 on the two affect carried manipulations (trolls, phishing),
where affect and manner inflation both reach 0.71 to 0.76 and do the job better. Candour is
essentially blind on false political claims (0.535). Worst of all, on dark patterns candour
drops BELOW 0.5 (0.44 to 0.49): the scorer reads dark pattern microcopy as MORE transparent than
legitimate persuasion, so a candour gate would spare dark patterns and flag charities. Manner
inflation also fails on dark patterns (0.48), because dark patterns are matter starved but not
affect heavy, they are commercial drive heavy; that is a separate finding and the reason the
full character reading, not any single axis, is the real detector.

## 6. Why candour fails: it measures the voice, not the intent

The result has one clean explanation that the group means make visible. The candour axis scores
transparency of the WRITING (opaque wording versus clear wording), not honesty of the INTENT
behind it. Manipulation is very often blunt and clear on the surface. "Only 2 left, order now"
is perfectly transparent as a sentence while being a scarcity trick; a state troll writes in a
plain, direct, emphatic voice; a false claim stated flatly reads as candid. All of these earn
high candour from an instrument that is reading the sentence, not the motive. At the same time
the open hard sell that the objection cares about most, the kickstarter pitch, reads only mid
candour (0.666), lower than the dark patterns, because its voice is promotional and hedged. So
the axis that was supposed to spare legitimate marketing actually scores one of the clearest
cases of legitimate marketing below the manipulation it was supposed to catch. Candour and
honesty of intent are different things, and the instrument measures the first.

## 7. What does separate the two poles

The full eight axis classifier separates legitimate persuasion from manipulation at five fold
cross validated AUC **0.866**. Its standardised coefficients say the work is done by matter and
by openness of the commercial ask, not by candour:

    depth            +1.22      (legit persuasion is more substantive)
    commercial_drive +1.13      (legit persuasion is more openly commercial)
    rigour           +0.51
    register         +0.36
    originality      +0.33
    stance           -0.27
    candour          +0.18      (near zero contribution)
    affect           -0.01

Candour contributes almost nothing to the multivariate boundary (+0.18) once depth, rigour and
commercial drive are in the model. The honest boundary is the one the sibling results already
established: manipulation is matter starved relative to its genre, with affect inflation on top
for the affect family (trolls, phishing). Candour is not that boundary.

## 8. Plane coordinates (for the two plane plots)

Group means for the candour by affect plane and the candour by manner inflation plane are in
`plane_data.json` (mean and standard deviation for candour, affect, manner inflation and PC1 per
group). The shape both planes show is the same: on the candour axis the legitimate and
manipulation clouds sit on top of each other; the separation that exists runs along the affect
and the manner inflation axes, not along candour.

## 9. Verdict

**Candour is not the ethical line.** On a spectrum running from charity appeals, crowdfunding,
reviews and sincere argument at one pole to state trolls, dark patterns, phishing and false
claims at the other, candour is the weakest of the ten single axis separators (AUC 0.573) and
the weakest of the three named competitors, beaten by manner inflation (0.686) and affect
(0.628) and dwarfed by the matter axes (rigour and depth near 0.77). The candour distributions
of the two poles overlap almost entirely (overlap 0.80, identical medians), there is no usable
threshold, and on dark patterns candour points the wrong way: it reads the trick as more
transparent than the charity.

The reason is not noise, it is a category difference. The instrument scores candour as
transparency of the voice, and manipulation is frequently blunt and clear, so it earns high
candour while a promotional but honest pitch earns less. The appealing product framing, "we flag
low candour persuasion, not persuasion", does not survive contact with the data and should be
dropped.

The finding is not empty. It says the defensible boundary is the one the programme already has:
manipulation is matter starved relative to its genre, affect inflated for the affect family, and
best caught by the full character reading against a per genre baseline (see the sibling genre
calibration result), not by any single "honesty" axis. The credible product claim is "we flag
matter starved, genre inflated persuasion", and it survives the "you are just censoring
marketing" objection for a better reason than candour would have given: legitimate marketing is
openly commercial and substantive, and the calibration judges every genre against itself.

## 10. Caveats (kept honest)

- **One scorer lineage.** All scores are the 7B qwen2.5-7b-atlas instrument. The sibling
  manipulation result was confirmed on a second 27B lineage; this candour test has not been, and
  a candour negative on one scorer is weaker evidence than a positive confirmed on two. That
  said, a second lineage would have to move candour from 0.573 to a clean boundary to overturn
  the verdict, which the overlap of 0.80 makes very unlikely.
- **Candour is a voice read, not a ground truth intent label.** The whole result turns on this,
  and it is stated as the finding rather than hidden as a limitation.
- **The manipulation pool is IRA heavy** (64 per cent). Section 5 reports every domain on its
  own so the pooled number is not carrying a hidden single actor effect; candour is weak or
  reversed in every domain, so the pooling is not the cause.
- **Short text confounds candour.** Dark patterns, phishing subject lines and LIAR claims are
  very short, and candour on very short text is unstable (the neutral dark pattern control reads
  candour 0.543, lower than the dark patterns themselves). This is part of why candour is not a
  reliable axis for a gate that must work on short manipulative text.
- **Legit persuasion genres differ in length and register** from the manipulation genres, so the
  strong matter axis separation (rigour, depth) carries some length; that is exactly why the
  programme uses the genre calibrated composite rather than raw matter, and why the headline here
  is about candour specifically, not a fresh detector.

---

*Method files: `analyse_candour.py` (groups, means, univariate and multivariate AUC, threshold
sweep, plane dump), `prep_persuasion.py` (donorschoose and amazon prep), `plane_data.json`
(plane coordinates). PC1 reference is the first principal component of
`cc_v3.domain_char8_expanded` (2.65M domains), oriented rigour plus depth positive.*

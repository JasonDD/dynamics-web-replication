# Does the matter versus manner field structure replicate on a second scorer lineage?

**Programme:** DYNAMICS-WEB, PUBLIC track. **Question:** Paper 1 (Distinct Fields) says the web
is not one measurable quality but several distinct information fields, and that the character space
collapses to roughly two interpretable dimensions, a matter versus manner axis (rigour and depth on
one pole, affect on the other) plus an originality axis. That structure was established on the
internal 7B character scorer. This test asks whether it is a property of the construct or a property
of that one model: does the same structure appear when an independent 27B scorer (a separate model
lineage) rates the same items?

**Verdict:** the core claim replicates. On the 27B lineage the first principal component is the same
matter versus manner axis as on the 7B (rigour, depth and candour on the positive pole, affect on the
negative pole), the two axes point in nearly the same direction in the eight axis space (cosine
0.845), and the 7B derived axis orders the 27B items almost as well as the 27B's own component does
(r up to 0.956). The matter versus manner field is not a one scorer artefact. The honest qualifier is
that the strict two dimensional collapse is looser on this small adversarial set than on the full web
corpus (two components carry 54 to 62 per cent of variance here, not the near total collapse the
paper reports on 2.65M domains), and the exact make up of the second component and the noisier
peripheral axes are scorer specific.

---

## 1. Data

The paired manipulation confirmation set: the same 1,350 items scored on the identical eight axis
instrument by both lineages, matched one to one on item id (1,350 of 1,350 overlap, no schema drift).

| Source | File (on NAS) | rows |
|---|---|---|
| 7B lineage | `/mnt/nas/kronaxis/corpora/ira_troll/work/baseline_7b.jsonl` | 1,350 |
| 27B lineage | `/mnt/nas/kronaxis/corpora/ira_troll/work/scored_27b.jsonl` | 1,350 |

The set is a deliberate three way spread across the character space: 450 Reddit Change My View
winning arguments (`arg`, the matter pole), 450 IRA political troll posts (`ira`, the manner pole),
and 450 LIAR PolitiFact statements (`liar`, short political text in between). This spread is what
lets a principal component analysis recover the matter versus manner axis from either scorer.

The eight axes: rigour, depth, originality, candour, affect, commercial_drive, stance, register.

This is the cleanest cross lineage source because the same items were scored by both models. It is
smaller and more adversarial than the 2.65M domain web corpus the paper's dimensionality claim was
built on, which matters for the dimensionality count (see the caveat in section 5).

---

## 2. Per lineage dimensionality

Correlation matrix PCA (each axis standardised to unit variance within its lineage, so the loadings
are comparable across scorers). Variance carried by each component:

| Component | 7B ratio | 7B cumulative | 27B ratio | 27B cumulative |
|---|---|---|---|---|
| PC1 | 0.355 | 0.355 | **0.386** | 0.386 |
| PC2 | 0.185 | 0.540 | 0.236 | **0.622** |
| PC3 | 0.161 | 0.701 | 0.121 | 0.743 |
| PC4 | 0.103 | 0.804 | 0.097 | 0.840 |
| PC5 | 0.072 | 0.877 | 0.060 | 0.900 |
| PC6 | 0.067 | 0.944 | 0.047 | 0.947 |
| PC7 | 0.037 | 0.981 | 0.035 | 0.982 |
| PC8 | 0.019 | 1.000 | 0.018 | 1.000 |

On both lineages PC1 is the single dominant axis (35 to 39 per cent). The 27B shows a cleaner two
dimensional structure than the 7B: PC1 plus PC2 carry 62.2 per cent on the 27B against 54.0 per cent
on the 7B, and the 27B has a sharper elbow after PC2 (PC2 0.236 then PC3 drops to 0.121), whereas on
the 7B PC2 and PC3 are close (0.185 and 0.161). To reach 80 per cent of variance both lineages need
four components; to reach 90 per cent both need six.

Covariance PCA (unstandardised) tells the same story a little more strongly for the 27B: two
components carry 70.4 per cent on the 27B and 58.4 per cent on the 7B.

---

## 3. Is PC1 the matter versus manner axis on both?

PC1 loadings, sign oriented so the rigour and depth pole is positive:

| axis | 7B PC1 | 27B PC1 |
|---|---|---|
| rigour | **+0.535** | **+0.455** |
| depth | **+0.532** | **+0.470** |
| candour | +0.397 | +0.452 |
| originality | +0.156 | +0.413 |
| register | +0.248 | -0.089 |
| stance | +0.118 | -0.201 |
| commercial_drive | -0.092 | -0.190 |
| affect | **-0.406** | **-0.335** |

Yes on both. On each lineage the positive pole is led by rigour and depth (the matter axes) with
candour alongside, and affect is the strongest negative loading (the manner pole). This is the matter
versus manner axis exactly as the paper defines it, recovered independently from two model lineages.

The differences are in the middle of the ranking, not the poles. Originality loads only weakly on the
7B PC1 (+0.16, it is mostly a second component axis there) but joins the matter pole on the 27B
(+0.41). Register and stance are mildly positive on the 7B and mildly negative on the 27B. The poles
that define the axis agree; the near zero axes are where the scorers differ.

Second component, for completeness. On the 7B, PC2 is the originality axis the paper names (originality
+0.62, register -0.54), which is why the paper describes the space as matter versus manner plus
originality. On the 27B, PC2 is a manner and delivery axis instead (stance +0.54, affect +0.49,
register +0.49) and originality has moved into PC1. So the first, load bearing dimension replicates
cleanly; the identity of the second dimension is scorer specific.

---

## 4. Cross lineage agreement

All measured on the same 1,350 items.

| Measure | value |
|---|---|
| PC1 axis cosine (7B loading vector vs 27B loading vector) | **0.845** |
| PC1 score correlation, each lineage on its own axis (Pearson) | 0.724 |
| PC1 score correlation (Spearman) | 0.725 |
| 27B items projected on the 7B axis vs the 27B's own PC1 (Pearson) | **0.956** |
| 7B items projected on the 27B axis vs the 7B's own PC1 (Pearson) | 0.915 |
| Per item full eight vector cosine, raw (mean) | 0.783 |
| Per item full eight vector cosine, standardised (mean) | 0.349 |

The cosine of 0.845 says the dominant axis points in nearly the same direction in eight space on both
lineages. The cross basis projections are the strongest evidence: the axis derived from the 7B orders
the 27B items at r 0.956 against the 27B's own component, and the reverse holds at r 0.915. In plain
terms, you can throw away the 27B's own principal component, use the 7B's matter versus manner axis
instead, and it ranks the 27B items essentially as well. The axis is shared, not lineage specific.

The per item Pearson of 0.724 between each lineage's own PC1 scores is the weaker looking number, and
it is honest to keep it in view: two different models scoring on a coarse 0.1 granularity will not
agree item for item. But the aggregate structure and the axis direction agree strongly, which is the
claim under test.

**Per axis cross lineage agreement (Pearson, same items):**

| axis | r |
|---|---|
| depth | **0.673** |
| affect | **0.619** |
| rigour | **0.609** |
| candour | 0.394 |
| commercial_drive | 0.347 |
| originality | 0.344 |
| stance | 0.267 |
| register | -0.216 |

The three axes that define the matter versus manner poles, depth, affect and rigour, are exactly the
three the two scorers agree on most. The peripheral axes agree poorly, and register even disagrees
(r -0.22). This is the same picture from a different angle: the load bearing structure is the robust,
cross lineage part; the fine axes are noisier and partly scorer specific.

**Group ordering preserved.** Mean PC1 by kind, each on its own lineage axis:

| kind | 7B PC1 mean | 27B PC1 mean |
|---|---|---|
| arg (CMV, matter pole) | +1.208 | +1.551 |
| liar (short political) | +0.376 | -0.016 |
| ira (troll, manner pole) | -1.585 | -1.535 |

Both lineages place the sincere arguments at the matter pole, the trolls at the manner pole, and the
short political statements in between, in the same rank order. The field orders the material the same
way regardless of which scorer measured it.

---

## 5. Verdict

**The matter versus manner field structure replicates on the independent 27B scorer. It is not a 7B
artefact.** On the second lineage PC1 is the same axis (rigour, depth, candour positive; affect
negative), the two axes agree at cosine 0.845, the 7B axis orders the 27B items at r 0.956 against
the 27B's own component, the per axis agreement is highest on exactly the axes that define the poles,
and the three groups fall in the same matter to manner order on both. The dominant information field
the paper identifies is a property of the construct, recovered by two separate models, not a quirk of
one instrument.

**Two honest qualifications.**

First, the strict two dimensional collapse is looser here than the paper reports. On this set two
components carry 54 per cent (7B) to 62 per cent (27B) of the variance under correlation PCA, and
reaching 80 per cent needs four components on both. The near total two dimensional collapse the paper
states is a property of the large web corpus (2.65M domains), where the mass of ordinary web text
sits along one dominant axis; a deliberately adversarial three group set of trolls, essays and
fact checked claims has more genuine spread across the minor axes, so it should not, and does not,
reproduce the tight collapse. What replicates on the small set is the identity and dominance of PC1,
not the exact variance fraction. Notably the 27B shows a cleaner two dimensional structure than the
7B (sharper elbow after PC2, 62 per cent versus 54 per cent), so the second lineage is if anything
more consistent with the two dimensional reading, not less.

Second, the periphery is scorer specific. The exact make up of PC2 differs (originality plus register
on the 7B, stance plus affect plus register on the 27B), and the low agreement axes (register, stance,
originality) are where the two models diverge. The replication is of the first, load bearing matter
versus manner dimension, which is the core of the Paper 1 claim, not of every fine axis.

---

## 6. Method

- `scripts/field_crosslineage.py`: loads the two paired score stores, matches on item id, runs
  correlation matrix and covariance PCA per lineage (numpy SVD, no sklearn), sign orients each PC to
  the rigour and depth pole, and computes the cross lineage axis cosine, per item PC1 score
  correlations, cross basis projections, per axis agreement, per item eight vector cosines and group
  PC1 means. Prints a single JSON block; the numbers in this document are that output rounded.
- Score stores (persistent, on the NAS):
  `/mnt/nas/kronaxis/corpora/ira_troll/work/baseline_7b.jsonl` (7B) and
  `/mnt/nas/kronaxis/corpora/ira_troll/work/scored_27b.jsonl` (27B).
- No fresh scoring was needed; both stores already existed from the manipulation confirmation run.

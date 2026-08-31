# Truthometer held out evaluation: precision, recall, F1, coverage

**Track:** PUBLIC (Papers 5 and 6 robustness pass).
**Date:** 30 August 2026. **Branch:** `ops/gh-treasure-discovery`.
**Reproduce:** `eval_truthometer.py` in this folder, read only against `tfs` on DL580; raw
output frozen in `eval_raw_output.json`.

## What was measured, and against what gold

The truthometer settles a claim by joining it to the public record. The pivot the paper
rests on is that the register check *is* the ground truth: a stated company number either
appears in Companies House or it does not, and there is no opinion in that. This pass turns
the engineering system into a measured claim by scoring it on data it never trained on,
against three independent sources of truth.

| Gold source | Rows | Role |
|---|---|---|
| `cc_v3.claim_label_train` (gold claim type `klass`) | 66,957 | which claims are even checkable |
| `cc_v3.claimreview_claim` (ClaimReview / PolitiFact gold `rating`) | 92,357 | the public fact check corpus, LIAR family |
| `cc_v3.ch_company` (5.70M live) + `cc_v3.ch_dissolved` (1.90M) | 7.60M | the register that settles the checkable slice |

The verifier under test is the deployed FACT verdict (`run_verdict.sql` +
`verdict.go`): it reads a company number a site states about itself and returns MATCH,
DISSOLVED or NONEXISTENT against Companies House, plus a founded year check. The withheld
slice is a fixed 20 per cent split taken by stable hash of the domain and number, so the
same rows are held aside on every run.

The headline is a two stage story, and the two numbers must never be blended:
**coverage** (what fraction of claims the verifier can settle at all) is reported
apart from **accuracy** (whether it is right on the ones it does settle).

---

## Leg A. Coverage: what the truthometer can verify at all

An independent scope detector (regex plus the checksum validators ported from
`checks.go`: Luhn, ISO 7064 MOD 97-10, the HMRC VAT method, and the Companies House number
form) was run over both public fact check corpora. A claim is countable only when it carries
a public register key the truthometer can settle.

| Corpus | Register checkable | Coverage |
|---|---|---|
| `claim_label_train` (66,957) | 2 | 0.003% |
| `claimreview_claim` (92,357) | 0 | 0.000% |

Broken out by gold claim type, even the claims a fact checker calls a verifiable fact almost
never carry a register key:

| Gold `klass` | n | register checkable |
|---|---|---|
| EMPIRICAL | 36,724 | 0 |
| VERIFIABLE_FACT | 19,234 | 2 |
| OPINION | 7,369 | 0 |
| FALSIFIABLE_SUPERLATIVE | 1,970 | 0 |
| PUFFERY | 1,370 | 0 |
| TRIVIAL | 266 | 0 |

**Reading.** On the standard public fact check corpora, essentially none of the claims are
settleable by a register join, because they are political statements, viral misinformation
and opinion ("the KKK officially endorses Trump 2020", "Florida is now the only state to tax
commercial leases"). The truthometer abstains on all of them. That is correct behaviour, not
a miss: a company register cannot and should not adjudicate a political claim. The gap between
"verifiable in principle" (the fact checker's 19,234 verifiable facts) and "checkable against a
register" (2 of them) is the honest bound on the whole method. The truthometer is a verifier of
claims a site states about its own registered identity, not a universal truth oracle.

---

## Leg B. The verifiability gate as a classifier

Before the truthometer can be right or wrong it has to decide, per claim, whether it can settle
it. That gate is itself a classifier and can be scored. The positive test set is the deployed
verifier's own register key claims (every row in the verdict table carries a stated company
number); the negative test set is the two public fact check corpora, where the gate should
abstain. None of these labels were used to tune the detector.

| | fresh gold: register key | fresh gold: not a register claim |
|---|---|---|
| gate says checkable | TP = 40,347 | FP = 2 |
| gate says abstain | FN = 12 | TN = 159,312 |

| Metric | Value |
|---|---|
| Precision | 1.0000 |
| Recall | 0.9997 |
| F1 | 0.9998 |
| Specificity | 0.99999 |

**Reading.** The gate separates checkable from not checkable almost perfectly: two false
positives in roughly 159,000 negatives, twelve missed keys in about 40,000. The decision about
what the truthometer is allowed to touch is reliable, which is the precondition for trusting the
abstention as a designed choice rather than a shrug.

---

## Leg C. Verdict accuracy on the checkable slice, versus Companies House

On the withheld 20 per cent of company number verdicts (7,994 rows), every stated number was
re checked against a fresh authoritative lookup in the live and dissolved registers, and the
deployed verdict was compared to that fresh check.

Confusion matrix, deployed verdict (rows) against a fresh Companies House lookup (columns):

| | fresh MATCH | fresh DISSOLVED | fresh NONEXISTENT |
|---|---|---|---|
| verdict MATCH | 7,281 | 0 | 0 |
| verdict DISSOLVED | 0 | 103 | 0 |
| verdict NONEXISTENT | 0 | 0 | 610 |

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| MATCH | 1.000 | 1.000 | 1.000 | 7,281 |
| DISSOLVED | 1.000 | 1.000 | 1.000 | 103 |
| NONEXISTENT | 1.000 | 1.000 | 1.000 | 610 |

**Overall agreement: 100.00% over 7,994 withheld verdicts.**

**Reading, stated honestly.** What this measures is register join fidelity: the claim
"the stated number X is a live, dissolved, or absent Companies House company" reproduces exactly
against an independent authoritative lookup, with no bug and no stale snapshot. The join is
deterministic, so a perfect score here is expected and its value is a guarantee, not a surprise:
the verifier does exactly what it says against the register, every time, on data held aside. It
does **not** measure whether the number was read correctly off the page (extraction), nor whether
the site is entitled to state it (the entity bridge). Those are separate error sources, treated
next, and the paper must never let this 100 per cent stand in for them.

### The two honest bounds

**1. The entity bridge is the real ceiling, and the design already knows it.**
A MATCH means the number resolves to a real registered company. It does **not** mean the site
displaying it is that company. On the withheld MATCH rows, the domain shares a token with the
registered company name in only **17.0%** of cases (1,239 of 7,281). Examples from the data:
`infinics.co` states company number 08469555, which resolves to BULB ENERGY LTD;
`glaziersnorthwood.co.uk` states a number registered to VIABL LTD. The truthometer is not wrong
in these cases, because at the KEY_RESOLVES tier it claims only that the number resolves, never
that the site owns it. The 17 per cent is a lower bound on true ownership, since trading names
diverge from registered names, but it establishes the point the tier system is built around: a
key resolving is not the site being who it says it is. Any accusatory reading needs the
ENTITY_MATCHES tier and corroboration, and `verdict.go` enforces exactly that at the type level.

**2. A NONEXISTENT is not a fraud finding on its own.**
610 withheld numbers were absent from both registers. Absence is not proof of fabrication: the
number can be foreign, newer than the loaded snapshot, or a single digit typo. The stated
identity tiering shows why the design refuses to accuse on this signal alone: of the full stated
identity set the largest tier is `number_name_mismatch` (17,087), which is mostly legitimate
trading name variance rather than a lie, against only 4,142 `number_not_found` and 7,225
`corroborated`. Consistent with the prior hand audit, name corroboration confirmed only 18 of
1,114 candidate typos as genuine. The verdict engine therefore treats an uncorroborated mismatch
or nonexistent as an abstention that widens the band, not as a gate on the Veracity Score. The
accusatory precision of a bare NONEXISTENT is low, and the system is built not to assert it.

---

## Verdict

The truthometer is a **precise verifier of register checkable claims and a disciplined
abstainer on everything else.** Measured on withheld data:

- On the claim it actually makes ("this stated company number is a live, dissolved, or absent
  Companies House record"), precision, recall and F1 are 1.00 against an independent
  authoritative re check of 7,994 verdicts. The register join is exact.
- The verifiability gate that decides what it may touch scores F1 0.9998, so its abstentions are
  a designed choice, not noise.
- Coverage is the binding constraint and the honest headline: on standard public fact check
  corpora (ClaimReview and PolitiFact, the LIAR family), 0.00 to 0.003 per cent of claims carry a
  register key, so the truthometer verifies almost none of them, and that is correct. It is not a
  universal fact checker and does not pretend to be one.
- The precision ceiling for any accusatory use is the entity bridge, not the register join. A key
  resolving is not ownership (17.0 per cent domain to name overlap on MATCH), and a missing key is
  not fraud (mismatch is mostly legitimate trading name variance). The tier system and the
  corroboration gate in `verdict.go` are built to hold the line exactly there.

**The honest bound, in one line.** The truthometer is a verifier of record checkable claims with
a proven exact register join, not a truth oracle for arbitrary statements; its power is that it
knows precisely which claims it can settle, and abstains, loudly and correctly, on the rest.

## Limitations and what is not yet measured

- Extraction precision (was the right number read off the page) is not measured here; it needs a
  page level audit of the harvest against the raw crawl. Register join fidelity and the bridge
  floor are measured; extraction sits between them and is the next audit.
- The withheld split is drawn from the deployed UK company number verdicts. The founded year
  ENTITY_MATCHES tier is tiny (54 rows total) and is not scored as a separate matrix.
- Coverage is measured against English and multilingual fact check corpora that happen to hold
  almost no register keys. A corpus of company self descriptions (which is what the truthometer is
  for) would show high coverage by construction; the point of Leg A is precisely that the general
  fact check task is out of the register's scope.

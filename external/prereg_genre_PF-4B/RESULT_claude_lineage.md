# PF-4B-GENRE — CLAUDE second-lineage replication attempt: INCONCLUSIVE (reported honestly)

Operator chose Claude as the independent disposition scorer (vs 7B) because the 27B an internal model teacher is blocked
by disk corruption (~/.cache/flashinfer I/O error, needs fsck). Claude read 112 communities (8 per genre x 14),
6 longest comments each, and scored community PLASTICITY (Extraversion+Openness) BLIND to matter/manner and to
the 7B scores (claude_plasticity_scores.json). Character = existing instrument community-mean (canonical PC1).
Script cc_genre_state_fit_claude.py.

## Outcome: INCONCLUSIVE, does not confirm or refute the 7B "genre is location" result.
- corr(Claude plasticity, matter/manner) = +0.145, p=0.13 (NOT significant). Holistic community-level reads are
  coarse and low-variance (scores 0.40-0.62) vs the 7B's per-comment scoring, so little coupling signal to test.
- Held-out RMSE (leave-communities-out 5-fold):
  matter_manner: Null 0.997, B(genre FE) 0.9995, A(genre slope) 0.955
  originality:   Null 0.963, B 0.998, A 0.951
  stance:        Null 1.011, B 0.884, A 0.877
- At 8 communities/genre, Model B (unshrunk genre FE) OVERFITS -> B worse than Null on matter/manner. Model A
  beats B, but that is SHRINKAGE beating overfitting, NOT genre modulating the coupling. Do NOT read A<B as a
  state signal at this N. The 7B run (394 communities) is the trustworthy one.

## The one cross-lineage agreement: STANCE.
On stance, "genre is a location" replicates in BOTH lineages (genre level cuts held-out RMSE: 7B 0.977->0.876;
Claude 1.011->0.884). That single dimension is the only robust cross-model point here.

## Verdict
Genre-is-location stays FIRM on the 7B lineage, NOT upgraded to settled. A proper cross-lineage confirmation
needs either (a) per-comment Claude disposition scoring (thousands of judgments, not a holistic community read)
on more comments/communities, or (b) the 27B pass once the flashinfer disk fault is fixed (fsck). The quick
Claude check revealed that the disposition->character coupling is subtle enough to require fine-grained
per-comment scoring; a coarse holistic read cannot adjudicate it.

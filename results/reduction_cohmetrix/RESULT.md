# Coh-Metrix reduction: does the character instrument recover reading comprehension science?

*DYNAMICS-WEB series, 3 September 2026. Script `cohmetrix_reduction.py`. Analysis only, CPU and DB, on the
77,182 held `cc_v3.reddit_wide` comments already scored on the eight axis instrument (body at least 200
characters, 30 words, across 400 subreddits). The licensed Coh-Metrix tool is replaced by the free
equivalents of its constructs (the TAALES and TAACO indices) computed from surface text with no model in
the loop. Each index is correlated with the matter against manner PC1 at the item level, within a subreddit
(both demeaned by room), and within room disattenuated by the single read reliability of the ruler (0.421,
from the Biber within unit run).*

## matter against manner PC1 versus each index

| Index | item | within room | within, disattenuated |
|---|---|---|---|
| Flesch-Kincaid grade | +0.263 | +0.234 | **+0.360** |
| Flesch reading ease | −0.270 | −0.235 | −0.361 |
| type token ratio | −0.288 | −0.294 | −0.453 |
| words per sentence | +0.183 | +0.175 | +0.270 |
| polysyllable rate | +0.208 | +0.163 | +0.252 |
| mean word length | +0.210 | +0.158 | +0.244 |
| subordinator rate | +0.093 | +0.098 | +0.152 |
| referential cohesion (adjacent sentence overlap) | +0.069 | +0.063 | +0.097 |
| connective rate | −0.033 | −0.008 | −0.012 |
| causal connective | −0.047 | −0.026 | −0.040 |
| logical connective | +0.010 | +0.023 | +0.035 |

Depth and rigour mirror the PC1 row (item r): depth against Flesch-Kincaid grade +0.278, words per sentence
+0.210, polysyllables +0.196, type token −0.321; rigour against grade +0.228, word length +0.203,
polysyllables +0.205.

## Reading

The matter axis, and depth and rigour specifically, recover the **complexity and sophistication** side of
Coh-Metrix at a real size, disattenuated correlations of a quarter to a half within a room: matter heavy
writing reads at a higher grade level, in longer sentences, with longer and more polysyllabic words, and
repeats its key terms (low type token, the density of argument, the same sign the Biber run found). It does
**not** recover the **cohesion** side, connective density and adjacent sentence overlap are near zero. So
the honest statement is that character depth is cognitive load real rather than surface style, on the
complexity constructs of the reading science, and the cohesion constructs are not recovered here. English
only, one reader lineage; a length control is the natural next step given the tie to sentence length.

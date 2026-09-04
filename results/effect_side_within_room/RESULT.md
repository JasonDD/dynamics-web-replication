# Does the effect side survive person grouped and within room controls?

*DYNAMICS-WEB series, 3 September 2026. The composition confound test the production side has just
been through, run on the effect side: the five clauses of Paper 4B. Scripts in `scripts/`, run on
the internal host against the held corpora and the internal schema. Every figure below is recomputed here, not copied.*

## Why this exists

On the production side (how a person's disposition shows in their own writing) a within room
differencing test found that a large part of what had been reported as a PERSON level effect was
who gathers where. Between room slopes ran up to six times the within room ones, one flipped sign,
and a headline coupling of 0.48 went to roughly zero once people were compared inside the same
room. Memos #20180 and #20181, commit `2759e8472`.

The effect side, Paper 4B's five clauses of what moves a person, had never been through that test.
The operator asked for it and an external advisor made it their first recommendation. This is that
test. WHO and WHEN were named as the ones to press hardest, and they are treated first and at
length. The traps carried over from the production side run are all four of them: the curvature
control, so a bend cannot pose as a turn; the person leakage check, stated explicitly for every
outcome; a wild bootstrap null that fixes each room's own design and residual scale rather than a
record permutation; and reliability measured from repeated observations rather than assumed, with
raw and corrected numbers side by side.

## The answer in one table

| # | Effect side claim | Corpus and n | Between room | Within room | Class |
|---|---|---|---|---|---|
| 1 | **WHO** a legislator's left to right position tracks their matter against manner character | ParlaMint, 1,675 speeches, 1,520 with a position, 780 speakers, 26 countries, 190 country party cells | standardised slope **+0.003**, r=+0.003, p=0.99 over 26 country means | standardised slope **−0.118**, country clustered t=−3.31 **p=0.0028**, party clustered p=0.0003, wild cluster bootstrap **p=0.0075**; corrected for measured reliability r=−0.168 | **1 SURVIVES** |
| 2 | **WHO** the same position tracks their **stance** | as above | standardised slope **−0.339** | standardised slope **−0.049**, country clustered p=0.30, wild bootstrap p=0.31 | **3 COMPOSITION** |
| 3 | **WHO** the reader's disposition predicts which character wins their thread | ChangeMyView, 19,430 scored arguments, 4,263 matched strata, 3,044 threads with a scored asker, 2,613 distinct askers | only **0.8%** of the winning direction variance is between topic rooms | held out r **+0.068** person grouped (p=0.002), **+0.058** topic grouped (p=0.005), **+0.055** within topic and person grouped (p=0.005), against **+0.064** for the published design | **1 SURVIVES** |
| 4 | **WHO** the manner advantage depends on the reader's disposition (authored panel) | 5 views x 4 coordinates x 4 personas; 240 judgements on one lineage, 80 on the other | the contrast is **entirely** between person by construction; disposition is constant inside a persona | one lineage −0.143 (wild bootstrap over views p=0.0002), the other **−0.028, p=0.32**; plasticity null on both | **4 INSUFFICIENT** |
| 5 | **WHO** the person carries a winning character across rooms (the two clean tests already in the record) | 262 recurring askers on ChangeMyView; 269 on the questions and answers network | not applicable | within person cohesion **+0.602 against a null of +0.614, p=0.879**; and **+0.568 against +0.573, p=0.702** | **3 COMPOSITION** |
| 6 | **WHERE** forums have their own character, roughly half the matter against manner variance sitting between them | `an internal table`, now 244,322 scored threads, 1,096 forums with at least 50 | **48.4%** between forum (published 49.3%) | **47.8%** after a topic room is taken out; the topic instrument is weak, see the bound below | **2 ATTENUATED BUT SURVIVES** |
| 7 | **WHERE** forums differ in the character they reward | 327 forums with a usable reward gradient | mean gradient +0.060 | spread of the per room gradients **0.195** raw, **0.194** topic controlled, **0.215** curvature controlled, against a wild bootstrap null whose own spread is **0.082** (95th percentile 0.088), **p=0.0025** | **1 SURVIVES** |
| 8 | **WHERE** two unrelated forum families reward opposite characters | 2 rooms; and the 5 room within platform version | the flip **is** the between room contrast, n=2 | within one platform, 5 rooms, F=1.45, **perm p=0.0905** (`results/se_arbiter_where.txt`) | **2 ATTENUATED BUT SURVIVES** |
| 9 | **HOW** a balanced argument beats a one sided one | authored panel, 5 views, 4 personas, two scoring lineages | view paired +0.098 and +0.066 | positive **inside every one of the four personas** on both lineages (+0.124, +0.105, +0.032, +0.129 and +0.133, +0.013, +0.113, +0.003) | **1 SURVIVES** |
| 10 | **WHAT** a manner heavy heading causally raises the click | Upworthy, 2,599 usable randomised tests, 11,098 arms | standardised slope **−0.006**, r=−0.006, **p=0.75** across tests | standardised slope **−0.051** within test, cluster t=−4.53 over 2,599 tests; adding a curvature term moves it from −0.000101 to −0.000099 | **1 SURVIVES** |
| 11 | **WHEN** the web drifts toward matter | 4 crawl snapshots, 50,462 domains present in both 2020 and 2026 | pooled cross section **−0.008/yr, the opposite sign** | same domains +0.075 over six years, paired t=+11.55, **p=8e-31** (`results/when_drift.txt`) | **1 SURVIVES** |
| 12 | **WHEN** United Nations diplomacy drifts toward matter | UN general debate, now 10,556 scored speeches, 200 countries, 1946 to 2022; 180 countries with at least 6 speeches over a 30 year span | strict between country **−0.0143/yr**, r=−0.221, p=0.003, **the opposite sign**; pooled cross section +0.0020/yr p=0.017 | within country mean **+0.0049/yr**, t=+2.34, p=0.020, **110 of 180** countries toward matter (sign p=0.0035), wild bootstrap over countries p=0.0160; with a curvature term in year +0.0057/yr p=0.009 | **2 ATTENUATED BUT SURVIVES** |
| 13 | **WHEN** the deep history of the periodical press drifts toward matter | 454 English article issues, 16 titles; 103 French titles; 3 Norwegian | archive cross section −0.026/yr p=5e-07, **toward manner** | within title **−0.0236/yr, p=0.013, wild bootstrap p=0.010, 15 of 16 titles toward MANNER** on the series ruler; France flat (−0.0009, p=0.87) | **3 the claim as written is refuted** |

Classes: 1 survives, 2 attenuated but survives, 3 explained by composition or confounding,
4 insufficient data.

## WHO, in plain English

WHO is the clause everybody expected to fall, because it is the only one that is a claim about a
person and person level claims are exactly where the production side lost most of its effect. It
did not fall. It came out of the test in better shape than it went in, and a different piece of it
fell than the one that was being watched.

**The legislator result survives, and it is a pure within country effect.** Paper 4B says that
across roughly fourteen hundred European legislators a speaker's left to right position correlates
with their character. The published number is a single pooled correlation across twenty six
countries with no country control at all, which is precisely the shape of thing the production side
test broke. Split it and the split runs the other way from the fear. Comparing whole countries
against each other there is nothing: the correlation between a country's average political position
and its average character is +0.003, which is zero. Everything the result has is inside countries.
Comparing two legislators who sit in the same chamber, speak the same language and are read by the
same scorer, the further right one is measurably further toward manner: a standardised slope of
−0.118, still there at t=−3.31 when the standard error is clustered on the twenty six countries,
and still there at p=0.0075 under a bootstrap that gives every country back its own political
spread and its own noise. Correct for how noisily a single speech measures a speaker, which we
measured at 0.49 rather than assumed, and it is −0.168.

Three further checks all come back clean. No speaker appears in more than one country, so there is
no person leakage to argue about. The pair differencing form, which cancels the country term exactly
instead of estimating it, gives the same answer, −0.186. And the curvature control, the trap that
caught the production side, finds nothing here: adding the bend term moves the slope from −0.186 to
−0.181 and the bend itself is not distinguishable from zero. The relationship is a straight line and
it is the same straight line in every country: the spread of the per country slopes, 0.320, is
exactly what the bootstrap says it should be if there were one slope everywhere, 0.312, p=0.42.
Where the production side found a real turn from room to room, the WHO relationship does not turn.

**But the stance half of the same result is composition, and it should be dropped.** The original
run reported two significant links, one on matter against manner and one on stance, both at p below
0.001. The stance one does not survive: between countries its standardised slope is −0.339, within
countries it is −0.049 and not significant at any clustering (p=0.30), a between over within ratio
of seven. Worse, stance is the outcome whose per country slope genuinely does vary more than chance
allows (p=0.007) while having no reliable average effect, which is the signature of a relationship
that exists differently in different places rather than one that exists everywhere. Affect was
already reported as null and stays null. So the honest version of the legislator sentence names one
axis, matter against manner, and drops the stance one.

**The reader side of WHO survives too, for a reason worth stating.** The ChangeMyView coupling fork
predicts a thread's winning character direction from the disposition of the person being argued
with. The published run used plain folds, so the same asker could sit in training and in test, and
there was no topic control. Fixing both barely moves it: held out r goes from +0.064 to +0.068 when
every thread of an asker is kept together, to +0.058 when whole topic rooms are held out, and to
+0.055 when the outcome is demeaned inside its topic room as well. All well outside the fold to fold
noise of 0.006. The reason it survives is measured rather than asserted: only 0.8 per cent of the
winning direction's variance sits between topic rooms, so on this corpus there is almost no room
composition available to confound it with. The honest bound is that the effect is genuinely small,
r near 0.06, on one platform and one scoring lineage.

**The panel interaction cannot be tested at all, and its two lineages disagree.** The authored
manipulation panel is where Paper 4B says steady dispositions are moved by evidence and reactive
ones by style. Disposition is constant inside a persona, so there is no within person version of
that contrast to run; it is a between person comparison of two personas against two, by
construction, whatever the judgement count. Run against a bootstrap that fixes each view's own
design, the frontier lineage gives −0.143 (p=0.0002) and the other lineage gives −0.028 (p=0.32).
The plasticity version is null on both. A claim that appears on one scoring lineage and not the
other is exactly what the paper's own cross lineage guard exists to catch, so this leg should be
described as owed, not as evidence.

**And the only two tests in the whole record that hold the person fixed and let the room vary are
both null.** On ChangeMyView, 262 people who started threads on several different topics show no
more consistency in the character that wins them over than random people do (+0.602 against a null
of +0.614, p=0.879). On the questions and answers network the same test on 269 people gives the same
answer (+0.568 against +0.573, p=0.702). Those two are already in the repository and were already
read correctly at the time: the room arbitrates, the person does not carry a fixed taste from room
to room.

**Putting it together.** WHO survives as a real but small association between a person's disposition
and the character they write in, and between a person's disposition and what wins in their thread.
It does not survive as a claim that a person carries a portable taste across rooms, and that is the
version a reader is most likely to hear in the sentence "who you say it to". The referee defensible
form is narrower than the paper's: a reader's disposition shifts the odds a little, inside a room,
and the room still dominates.

One further honesty point that has nothing to do with composition. The legislator result is a
writer measured on their own writing. It belongs to the production side of the coupling and is used
in Paper 4B as a proxy for the effect side. That is a validity gap independent of everything tested
here and it should be stated where the sentence appears.

## WHEN, in plain English, and the press artefact resolved

**The discrepancy is the ruler's axis set. It is not a filter, and it is not the standardisation
base the source document blames.**

Three artefacts read the same English periodical archive and disagree. The two that matter run on
the same held file of 454 article issues across 16 titles. `within_source_articles_proof.txt` gets
−0.0236 per year, p=0.013, with 1 of 16 titles moving toward matter. `historical_press_drift`
gets −0.0062 per year, p=0.18, with 6 of 16. Its RESULT.md explains the gap as "a ruler standardised
on the English archive alone". That explanation is wrong twice: the earlier script standardises on
the 2.65 million domain web corpus, not on the English archive, and the standardisation base turns
out not to matter at all.

Recomputing every ruler on one set of rows settles it. A ruler here has two parts, the axis weights
and the base the axes are standardised on, and the two scripts differ in both. Crossing them:

| ruler | axis weights | standardised on | mean within title slope | p | toward matter |
|---|---|---|--:|--:|--:|
| R1 | web PC1, all eight axes (**the series ruler**) | 2.65M web domains | **−0.0236 /yr** | 0.013 | **1 of 16** |
| R4 | web PC1, all eight axes | the press corpus | −0.0101 /yr | 0.011 | 1 of 16 |
| R6 | web PC1, all eight axes | English issues only | −0.0092 /yr | 0.014 | 1 of 16 |
| R2 | five axis hand contrast (**the press drift script**) | the press corpus | −0.0062 /yr | 0.176 | 6 of 16 |
| R3 | five axis hand contrast | 2.65M web domains | −0.0041 /yr | 0.705 | 7 of 16 |
| R5 | five axis hand contrast | English issues only | −0.0047 /yr | 0.297 | 8 of 16 |

Identical results at both title filters (six issues and thirty years, four issues and forty years),
so the filter is not it either. Read down the table: hold the axis weights fixed and change the
standardisation base three ways and the sign count never moves off 1 of 16 and the p value never
leaves the 0.01 band; the three readings correlate at r=0.99 and above. Change the axis weights and
everything moves. The two rulers correlate only r=0.57 on the very same 454 issues, and r=0.15 in
the web standardised pairing. The five axis contrast drops originality, candour and commercial
drive, three of the eight axes, one of which (commercial drive) is the axis that rises hardest in
the English press. That is the whole disagreement.

**Which means the press leg is not a null pointing the wrong way. On the series ruler it is a
significant result pointing the wrong way.** The ruler used by every other result in the programme,
the web PC1 the web drift leg, the United Nations leg, the Upworthy leg, the ChangeMyView leg and
the legislator leg all use, says the English periodical press moved toward MANNER at 0.0236 per
year, p=0.013, wild bootstrap over titles p=0.010, with 15 of the 16 titles going that way (sign
test p=0.0005). France, the deepest panel, is flat (−0.0009, p=0.87). Norway is three titles from
1940 and cannot speak to the period.

This is not a composition artefact either, and that is worth saying because the programme's instinct
would be to reach for one. Under the series ruler the archive wide cross section is −0.0262 per year
and the strict between title component, title average character against title average date, is
−0.0052 with p=0.85. The between title term is nothing; the drift is real and it is inside the
titles.

A footnote on the third artefact. `within_source_proof.txt` reported 636 issues across 17 titles at
−0.0237 per year, p=0.012, 5 of 17. Its source file has since grown to 705 issues; recomputed on the
current file under the same ruler and filter it gives −0.0173 per year, p=0.074, 6 of 19. Same
direction, significance now marginal. The 5 of 17 against 1 of 16 gap between the first two
artefacts is the index and supplement volumes and the post 1960 issues that the articles only file
removes, which is a real and documented filter difference; the 1 of 16 against 6 of 16 gap, the one
the audit flagged, is the ruler.

**So what does WHEN actually rest on?** Not three corroborating sources. Two, plus a fourth the
paper does not currently cite, and one source that contradicts.

- The web leg is firm and it is already a within room test. The same 50,462 domains present in both
  2020 and 2026 drift toward matter, paired t=+11.55, p=8e-31, while the pooled cross section over
  the growing crawl drifts the other way at −0.008 per year. Between and within disagree in sign and
  the within one is the trustworthy one. This is the cleanest WHEN evidence in the programme.
- The United Nations leg survives, and on a much larger corpus than the one the artefact was
  written on: 10,556 scored speeches against 1,594. Within a country the drift toward matter is
  +0.0049 per year, t=+2.34, p=0.020, and the sign test that failed on the small corpus now clears,
  110 of 180 countries, p=0.0035; the wild bootstrap over countries agrees at p=0.0160. Allowing
  the trend to bend inside a country and reading only its straight line part strengthens it slightly
  (+0.0057, p=0.009), so this is not a curve misread as a line. And the composition here runs
  against the finding rather than making it: comparing whole countries, the ones with later average
  dates sit further toward manner, −0.0143 per year, p=0.003, the opposite sign to the within
  country drift. That is the decolonisation membership effect the artefact named, and taking it out
  is what the within country design does. The bound is that the effect is small and the corpus is
  translated diplomatic register with a high manner floor.
- The press leg does not corroborate. On the programme's own ruler it contradicts.
- A fourth leg the paper does not use: the questions and answers network's winning character drifts
  within each of its five rooms, pooled +0.0225 per year, p<0.0001, three of the five rooms
  individually significant (`results/se_when_drift.txt`). That is a within room temporal drift on a
  persuasion outcome rather than on ambient text, which is closer to what the WHEN clause actually
  claims than either of the two the paper leans on.

The sentence in Paper 4B §5, "the temporal term is now read in the web, in the deep history of the
periodical press, and in diplomacy, all three pointing the same way", and its echo in the abstract,
"the when gathers three independent corroborations", cannot stand. Neither can the comparison block
at the foot of `results/ungd_where_when.txt`, which still cites "deep-time print (1800-2020): toward
MATTER (r=0.79)", the archive wide cross section the programme itself retired.

## WHERE, HOW and WHAT

**WHERE holds and one of its two numbers is now better than it was.** The between forum share of
matter against manner variance reproduces on a corpus that has grown from 170,507 threads to
244,322: 48.4 per cent against the published 49.3. The source RESULT.md called that an upper bound
because there was no topic control. Adding one, a forty cluster lexical clustering of the thread
titles, takes it to 47.8 per cent. The honest bound must be restated rather than removed, because
the topic instrument is weak: those clusters carry only 0.8 per cent of the character variance
themselves, so they are close to orthogonal to the forum partition and they are not a strong test of
the subject confound. What can now be said is that a coarse topic control removes essentially none
of the room effect; what cannot yet be said is that a good one would.

The reward gradient result, the cleaner of the two because it is a slope inside a room rather than a
level, comes through the harder null intact. On 327 forums with enough engagement variance to yield
a gradient, the spread of the per room gradients is 0.195. The published null was a shuffle of the
room labels; replacing it with a wild bootstrap that gives every room back its own character spread
and its own residual scale, which is the null the production side test showed you have to use,
raises the null spread only to 0.082 with a 95th percentile of 0.088. The observed spread is more
than twice that, p=0.0025, the same p the published run reported against the weaker null. The topic
control takes the observed spread to 0.194 and the curvature control, which allows the reward
relationship to bend inside each room and reports only its straight line part, takes it to 0.215.
Neither dents it. Rooms really do reward different characters, and unlike the production side
coupling this heterogeneity is the claim rather than the confound.

The two forum family flip that opens the clause is, read strictly, a between room contrast on two
rooms, and the within platform version of it on five rooms of one network does not clear
(F=1.45, permutation p=0.0905). The clause is carried by the 798 forum population, not by the
two family illustration, and the paper should lean on the former.

**HOW is the cleanest thing in the paper and this test does not touch it.** Balance beating one
sidedness is positive inside every single persona on both scoring lineages, so it survives holding
the person fixed, and it is view paired, so it survives holding the room fixed. On the frontier
lineage all four persona level effects are significant on their own; on the other lineage all four
are positive and two of four reach significance at five views each. Its bound is unchanged and has
nothing to do with composition: the readers are model personas and there are five views.

**WHAT is randomised, so the within room design was already the published one, and the split is the
cleanest illustration in this whole document of what the test is for.** Within a test, where two
headings for the same item are shown to people at random, the manner heavy heading raises the click:
standardised slope −0.051 on the matter against manner axis, cluster robust t=−4.53 across 2,599
tests. Compare whole tests against each other, which is not randomised and is pure composition, and
there is nothing at all: −0.006, p=0.75. The between over within ratio is 0.12. On the production
side the between room number was up to six times the within room one; here it is an eighth, because
randomisation put it there. Adding a curvature term inside the test does not move the linear
estimate (−0.000099 against −0.000101), so the effect is not a bend misread as a line. The stated
sample size in Paper 4B, "some thirty two thousand randomised headline experiments", is still the
archive size rather than the analysis size and remains a separate correction owed (memo #20174).

## What a referee can still be told

- **HOW** stands as it did. Causal, two lineages, and it holds inside every reader as well as inside
  every topic.
- **WHAT** stands as it did, on the randomisation.
- **WHERE** stands and is the firmest of the five, on 798 independent forums across six software
  families, with the caveat on the variance share restated rather than removed.
- **WHO** stands in a narrower form than the paper states it: a person's disposition is really
  associated with their own character, entirely within room, and really shifts the odds a little in
  their own thread. It does not stand as a portable personal taste; the two clean tests of that are
  null. The stance half of the legislator result should be dropped, and the panel interaction should
  be described as owed because the two lineages disagree.
- **WHEN** cannot be told as three corroborations. It is one firm within domain result on the web,
  one weaker within country result in diplomacy, a within room drift on a persuasion outcome that
  the paper is not yet using, and a periodical press leg that on the programme's own ruler points
  the other way and should be reported as a disagreement rather than quietly rulered into a null.

## Reproduce

- `scripts/effect_who_legislator_within_room.py`, the WHO legislator test: between and within
  country, three clusterings, the wild cluster bootstrap, the pair differencing form with the
  antisymmetric curvature term, measured reliability, the person leakage check and the per country
  slope heterogeneity test.
- `scripts/effect_who_reader_grouped.py`, the ChangeMyView coupling fork under person grouped,
  topic grouped and within topic folds, and the authored panel's disposition interaction and balance
  main effect within and between persona, on both lineages.
- `scripts/effect_when_press_ruler.py`, the six ruler crossing that resolves the press artefact
  discrepancy, the within against between title split for each, and the wild bootstrap over titles.
- `scripts/effect_where_what_when_rooms.py`, the forum variance decomposition with a topic room,
  the reward gradients with topic and curvature controls against a wild bootstrap null, the Upworthy
  between test against within test split, and the United Nations within country drift.
- `scripts/effect_when_ungd_within_country.py`, the diplomacy leg: within country against
  between country, the curvature term in year, and the wild bootstrap over countries.
- Run logs and JSON on the internal host at `/home/jason/effect_confound/`.

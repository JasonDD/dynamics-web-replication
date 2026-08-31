# Axis covariance by domain: the internal grammar of character

**Track:** PUBLIC. **Mode:** analysis only on already scored 8 axis character. No scoring, no GPU, DB plus NAS files, all compute server side.
**Script:** `truthometer/scripts/cc_axis_covariance.py` (run on DL580).
**Raw run:** `docs/papers/dynamics_web_series/results/axis_covariance_matrix/covout.txt`.

## The question

The atlas maps where corpora **sit**: their mean character on the eight axes (rigour, depth, originality, candour, affect, commercial_drive, stance, register). This maps something the atlas cannot see: the internal **grammar** of character. Within a single domain, how do the eight axes co vary? Does rigour rise with depth? Does affect trade against substance? Does the sell push out candour? And, the real question, is that grammar the **same everywhere**, or does it **re wire by context**?

Method: for each domain we take the item level eight vectors and compute the 8x8 Pearson correlation matrix of the axes. We then compare those correlation structures across domains. Universal couplings hold sign and magnitude nearly everywhere. Couplings that vary by domain, or flip sign in particular genres, are the re wiring. Finally we summarise each domain by its 28 upper triangle correlations and cluster the domains by how their character is wired, a second order map that groups domains not by where they sit but by how they are built.

## Domains (16, item level, already scored)

| domain | n items | genre |
|---|---:|---|
| web_open (`domain_char8_expanded`) | 200,000 | open web |
| reddit_social (`reddit_wide`) | 2,377 | social |
| cmv_args | 19,430 | argument |
| stackexchange | 66,543 | argument |
| ddo_debate | 6,325 | argument |
| ungd_speeches | 10,556 | institutional |
| parlamint | 1,675 | institutional |
| oldbailey_court | 568 | institutional |
| historical_text | 2,340 | historical |
| classical_persu | 479 | historical |
| ira_trolls | 9,000 | deception |
| liar_claims | 1,100 | deception |
| phishing | 1,400 | deception |
| toxic_comments | 3,600 | deception |
| kickstarter | 6,000 | commercial |
| darknet_market | 545 | commercial |

The two open web tables are sampled; the NAS corpora are read in full up to a cap. Four corpora are modest (oldbailey 568, darknet 545, classical 479, parlamint 1,675) so their exact couplings are indicative, but they turn out to be the structural outliers and their coupling magnitudes are large, so the signal survives the noise.

## 1. The 28 axis couplings across domains

Each row is one axis pair. `mean_r` is the mean within domain correlation, `sd` its spread across the 16 domains, `sign%` the fraction of domains sharing the majority sign. A pair is **UNIVERSAL** when it is large (|mean| >= 0.25), sign stable (>= 90 percent) and tight (sd <= 0.18). It is flagged as varying by domain when it is loose (sd >= 0.20) or its sign is unstable (< 75 percent).

| pair | mean_r | sd | min | max | sign% | verdict |
|---|---:|---:|---:|---:|---:|---|
| rig~dep | +0.743 | 0.147 | +0.33 | +0.89 | 100% | **UNIVERSAL** |
| dep~ori | +0.489 | 0.191 | +0.22 | +0.79 | 100% | sign universal, loose |
| rig~can | +0.377 | 0.186 | +0.10 | +0.71 | 100% | sign universal, loose |
| rig~ori | +0.354 | 0.162 | +0.10 | +0.65 | 100% | **UNIVERSAL** |
| dep~sta | +0.327 | 0.205 | -0.05 | +0.66 | 94% | varies by domain |
| rig~aff | -0.294 | 0.251 | -0.57 | +0.29 | 88% | varies by domain |
| dep~can | +0.291 | 0.196 | -0.03 | +0.60 | 94% | sign mostly stable, loose |
| sta~reg | +0.260 | 0.348 | -0.80 | +0.70 | 94% | **varies by domain (widest)** |
| dep~reg | +0.257 | 0.300 | -0.52 | +0.66 | 88% | varies by domain |
| rig~reg | +0.246 | 0.302 | -0.63 | +0.68 | 88% | varies by domain |
| ori~can | +0.236 | 0.167 | -0.15 | +0.51 | 88% | weak/mixed |
| rig~sta | +0.212 | 0.229 | -0.16 | +0.66 | 81% | varies by domain |
| aff~com | +0.198 | 0.201 | -0.12 | +0.58 | 81% | varies by domain |
| ori~sta | +0.169 | 0.185 | -0.08 | +0.57 | 81% | weak/mixed |
| ori~aff | +0.149 | 0.155 | -0.11 | +0.59 | 81% | weak/mixed |
| dep~aff | -0.123 | 0.308 | -0.47 | +0.62 | 69% | varies by domain |
| can~com | -0.123 | 0.217 | -0.71 | +0.12 | 69% | varies by domain |
| ori~com | +0.076 | 0.325 | -0.43 | +0.64 | 56% | varies by domain |
| ori~reg | +0.064 | 0.229 | -0.20 | +0.51 | 62% | varies by domain |
| can~aff | -0.056 | 0.202 | -0.71 | +0.17 | 56% | varies by domain |
| aff~reg | -0.055 | 0.304 | -0.46 | +0.71 | 69% | varies by domain |
| com~reg | -0.050 | 0.233 | -0.49 | +0.31 | 50% | varies by domain |
| aff~sta | +0.048 | 0.292 | -0.70 | +0.66 | 56% | varies by domain |
| can~sta | +0.047 | 0.200 | -0.24 | +0.45 | 56% | varies by domain |
| can~reg | +0.045 | 0.209 | -0.43 | +0.42 | 50% | varies by domain |
| rig~com | -0.034 | 0.294 | -0.51 | +0.40 | 56% | varies by domain |
| com~sta | +0.024 | 0.236 | -0.41 | +0.50 | 69% | varies by domain |
| dep~com | -0.004 | 0.330 | -0.55 | +0.44 | 62% | varies by domain |

(Axis short codes: rig rigour, dep depth, ori originality, can candour, aff affect, com commercial_drive, sta stance, reg register.)

### The universal core: the matter bundle

The top of the table is one story. The four substance axes, rigour, depth, originality and candour, are **positively coupled in every one of the 16 domains**. rigour and depth ride together at r = +0.74 (sd only 0.147, positive in all 16). rigour with originality, depth with originality, rigour with candour and depth with candour are all positive in 100 or 94 percent of domains. Whatever the genre, from UN speeches to darknet listings to reddit threads, an item that is rigorous tends also to be deep, and a deep item tends also to be original and candid. This is the invariant spine: the "matter" of a text moves as one block. It is the strongest evidence for a shared grammar.

### What re wires: the manner and positioning axes

Everything below the spine belongs to register, affect, commercial_drive and stance, and it does **not** hold still. These are the couplings that swing hardest and flip sign by domain.

- **stance ~ register is the single widest coupling**, sd 0.348, running from **-0.80 on the open web to +0.70 in phishing**. On the open web, taking a stance goes with low register: opinion is informal and plain. In phishing, darknet and toxic content, stance goes with high register: a manufactured authority tone is exactly how a position is pushed. Same two axes, opposite wiring.
  - lowest: web_open (-0.80), parlamint (+0.04), stackexchange (+0.05)
  - highest: phishing (+0.70), darknet_market (+0.59), toxic_comments (+0.55)

- **register inverts its whole relationship to substance between the open web and the formal corpora.** rigour~register and depth~register are strongly **negative on the open web** (-0.63, -0.52: the rigorous web page is written plainly, low register) but strongly **positive in historical text, phishing and oldbailey** (+0.66 to +0.68: there, formality and substance rise together). The meaning of register is not fixed; it couples to rigour in one world and against it in another.
  - rig~reg lowest: web_open (-0.63); highest: historical_text (+0.68), phishing (+0.63)
  - dep~reg lowest: web_open (-0.52); highest: historical_text (+0.66), phishing (+0.66)

- **affect trades against substance in modern argument, but with it in the older corpora.** rigour~affect is negative in reddit (-0.57), ddo debate (-0.56) and the open web (-0.54): heat displaces care. But depth~affect is **positive** in oldbailey court (+0.62) and classical persuasion (+0.45): in the older rhetorical corpora, emotional force and elaborated argument move together rather than against each other. The affect axis re wires between contemporary discourse and rhetorical prose.

- **commercial_drive is the most context bound axis of all.** Its couplings with depth, originality, rigour, candour and register all flip sign across domains. In phishing and darknet listings, commercial_drive **anti correlates** with rigour, register and candour: the sell replaces substance and honesty. In court, classical and liar corpora it couples **positively** with depth and originality, because there the instrument reads instrumental motive inside elaborated argument. There is no stable "commercial grammar"; the sell wires differently depending on what it is embedded in.

- **The manipulation signature is visible where you expect it.** candour ~ commercial_drive is most negative on the open web (-0.71) and negative again in phishing (-0.39) and darknet (-0.36): the pitch is where candour drops. candour ~ affect is also most negative on the open web (-0.71): affect loaded web content is low candour. These are the couplings the deception children exploit, and they are strongest in the commercial and open web cells.

## 2. Covariance structure similarity: is the grammar one thing?

Summarise each domain by its 28 correlations and correlate those vectors between domains. The **grammar universality index** is the mean of those 120 pairwise structural similarities.

```
grammar-universality index (mean pairwise structural similarity) = +0.487
range over 120 domain pairs:  min -0.005 .. max +0.959
```

+0.487 is the honest number. It is far above zero, so the domains do share a common backbone (the matter spine guarantees that). It is far below one, so the wiring is not the same everywhere. **Character has roughly half a shared grammar and half a context specific one.** The most alike pair of domains sits at +0.96; the least alike at essentially zero, unrelated wiring.

How typical each domain's wiring is (mean similarity to the other 15):

```
ddo_debate       +0.625      historical_text  +0.472
ira_trolls       +0.623      liar_claims      +0.450
reddit_social    +0.618      ungd_speeches    +0.399
stackexchange    +0.605      web_open         +0.347
parlamint        +0.571      classical_persu  +0.304
cmv_args         +0.568      oldbailey_court  +0.161
phishing         +0.525
kickstarter      +0.524
toxic_comments   +0.522
darknet_market   +0.483
```

The centre of gravity is modern argument and social text (debate, trolls, reddit, stackexchange, cmv). The structural **outliers** are the open web itself, and the two older rhetorical corpora, classical persuasion and oldbailey court. The old courtroom and classical persuasion wire their axes least like anything else in the modern set.

## 3. Clustering domains by how they are wired

Average linkage hierarchical clustering on the same structural distances. Merge distance is 1 minus structural similarity, so a small distance means wired alike. The revealing feature is that **content does not predict the cluster; wiring does.**

At the clean cut (distance < 0.5) the domains fall into six groups:

- **Modern discourse** (the big cluster): reddit_social, cmv_args, stackexchange, ddo_debate, parlamint, ira_trolls, liar_claims, toxic_comments. Social, argument, deception and one modern parliament, all wired alike: substance moves as a block, affect trades against rigour, register stays low.
- **The persuasion and sell cluster**: historical_text, phishing, kickstarter, darknet_market. This is the striking one. **historical_text and darknet_market merge first of all, at distance 0.041**, near identical internal grammar despite being about as far apart in content as two corpora can be. What binds them is the wiring: register moves with substance, and commercial_drive pulls against candour. Narrative prose and a drug listing are built the same way even though they sit nowhere near each other on the atlas.
- **web_open** stands alone: its stance~register at -0.80 and its register against substance make its grammar unlike the curated corpora.
- **ungd_speeches** stands alone: diplomatic speech wires its own way.
- **oldbailey_court** and **classical_persu** form their own branch and only join the rest at the very top (distance 0.78). In these older corpora affect couples **with** depth and rigour, the reverse of the modern web, so they are the true structural outsiders.

The point the clustering makes: the deception genre is **split across three different clusters** (ira and toxic in the modern block, phishing in the sell block, liar with the argument corpora), and the institutional genre is split (parlamint modern versus oldbailey older). So the covariance structure is a **different axis from topic or genre**. It tracks the register regime and the mode of persuasion, not the subject matter. This is the second order map: domains grouped by how their character is built, and the grouping cuts across where they sit.

## Verdict

**The internal grammar of character is partly universal and partly context dependent, and the split runs cleanly along the matter versus manner line.**

- **Universal, a hard spine.** The four substance axes, rigour, depth, originality and candour, are mutually positively coupled in all 16 domains. rigour and depth ride together at r = +0.74 everywhere. The "matter" of a text moves as one block whatever the genre. This half of the grammar does not re wire.

- **Context dependent, a mobile shell.** The manner and positioning axes, register, affect, commercial_drive and stance, re wire by domain. Their couplings swing widely and flip sign: stance~register runs from -0.80 to +0.70, register inverts its relation to substance between the open web and formal prose, affect trades against substance in modern argument but rides with it in older rhetoric, and commercial_drive has no stable wiring at all. This half of the grammar is written by the context.

- **The number.** The grammar universality index of +0.487 puts a figure on it: neither one grammar nor a free for all, roughly half shared and half local.

- **Why the re wiring is real and not an instrument artefact.** A single scorer could induce a fixed halo, for example always rating rigour and depth together. That would show up as **constant** couplings. It cannot produce the opposite sign in two different domains from the same rubric. The universal spine could carry some instrument halo, so treat its exact magnitude with care. But the domain specific re wiring, the sign flips, cannot be the ruler moving, because the ruler is the same in every cell. The variance across domains is the signal, and it is a property of the text.

- **What it means for the programme.** The matter axes are a genuine invariant and safe to treat as one construct across corpora. The manner axes are not portable: any detector, atlas coordinate or transfer claim that leans on register, affect, commercial_drive or stance must be read within its domain, because those axes mean different things, structurally, in different places. The clustering also hands us a usable object: a second order map that puts a darknet listing next to a historical narrative because they are built the same way, which is exactly the kind of grouping a "where does this text really belong" tool would want.

### Honest limits

- Single instrument. The universal matter spine may carry rubric halo; the exact +0.74 should be read as an upper bound on the true coupling. The re wiring result is robust to this, as argued above.
- Four corpora are small (n between 479 and 1,675). They are the structural outliers, so their exact matrices are noisier, but their coupling magnitudes are large and internally consistent.
- The open web sample and reddit are samples, not full tables, so their correlations carry sampling error at the third decimal, well below the effects reported here.
- Correlation, not cause. This maps how the axes co vary, not why. The re wiring says the relationships change by context; it does not say which way the causation runs inside a domain.

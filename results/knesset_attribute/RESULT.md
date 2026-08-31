# Does real speaker gender carry a character signature once the room is held fixed? (Knesset)

**DYNAMICS-WEB, PUBLIC track. Verdict: NO for gender. The who signal that survives the room is political position and age, not sex.**

Almost all person side work in the programme scores an *inferred* disposition. This result tests the who leg on **ground truth speaker demographics**: the Knesset Corpus records each member's real gender, party, coalition or opposition status, nationality and date of birth. We ask the atlas question directly. Within the same plenary sitting (same day, same order paper, same chamber temperature), and length matched, does the eight axis character of a speech differ by the speaker's real attribute?

---

## Data

- **Corpus**: Knesset Corpus (HaifaCLGroup on Hugging Face), the 365 full plenary protocols we hold on the NAS. Every protocol in the held slice is the **13th Knesset (1993 to 1996)**, in Hebrew.
- **Turns**: a speaking turn is all sentences sharing `turn_num_in_protocol`, attributed to one member. We keep numeric `speaker_id` only (it equals `PersonID`; UUID speaker ids are non member guests and officials, dropped), require a valid speaker, drop chairman turns (procedural moderation, a role confound), and require at least 300 characters. **56,408 scoreable turns.**
- **Real demographics joined by PersonID**: gender (`GenderDesc`), party and faction per Knesset (date window matched), coalition versus opposition per Knesset (`factions_coalition_opposition_membership`), nationality, and age from `DateOfBirth`. Coverage in the turn pool: gender 50,799 male / 5,609 female; coalition 29,096 / opposition 26,857; nationality 52,830 Jewish / 2,081 Arab / 959 Druze / 538 Bedouin; party on 56,079; age on all. **351 of the 365 sittings contain both a male and a female speaking turn**, so the room control is available for gender across the whole term.
- **Scored sample**: to stay polite on the shared GPU we scored a room balanced set of **3,604 turns, exactly 1,802 female and 1,802 male**, where each female turn is paired to a male turn drawn from the **same sitting** and the **same length bucket**. Every scored turn still carries party, position, nationality and age, so the same run feeds the secondary legs.
- **Instrument**: `qwen2.5-7b-atlas` on port 8301, the identical eight axis prompt, vocabulary and parse used across the whole series (rigour, depth, originality, candour, affect, commercial drive, stance, register). PC1 is fit by PCA on the eight standardised axes and oriented matter positive; `mm` is the matter minus manner composite (a robust proxy for the matter versus manner pole).
- **The room** is the protocol (one sitting). Every test below is inside a room. We never compare a speaker in one sitting to a speaker in another.

---

## Gender (the headline): no signature survives the room

Female minus male, 1,802 length matched pairs across 304 rooms. `p_perm` is a within pair sign flip permutation (2000 draws); `roomcons` is the share of rooms whose own mean difference points the same way as the pooled effect (chance = 0.50).

| axis | diff (F−M) | 95% CI | paired d | p_perm | roomcons |
|---|---|---|---|---|---|
| rigour | +0.027 | [0.018, 0.036] | 0.14 | .0005 | 0.59 |
| depth | +0.006 | [−0.001, 0.013] | 0.04 | .11 | 0.51 |
| originality | −0.001 | [−0.010, 0.007] | −0.01 | .81 | 0.49 |
| candour | +0.013 | [0.009, 0.017] | 0.14 | .0005 | 0.54 |
| affect | −0.010 | [−0.022, 0.001] | −0.04 | .07 | 0.53 |
| commercial drive | −0.023 | [−0.029, −0.017] | −0.17 | .0005 | 0.60 |
| stance | −0.012 | [−0.023, −0.002] | −0.06 | .02 | 0.49 |
| register | +0.032 | [0.020, 0.043] | 0.12 | .0005 | 0.61 |
| **PC1** | **−0.024** | **[−0.113, 0.061]** | **−0.01** | **.60** | **0.48** |
| mm | +0.015 | [0.008, 0.022] | 0.10 | .0005 | 0.59 |

Read this honestly. Several axes are "significant" only because 1,802 pairs give enormous power to resolve a trivial gap: the largest effect is commercial drive at Cohen's d = −0.17, and every axis sits below |d| = 0.17, that is one to three percent of the zero to one scale. The principal character dimension, **PC1, is a clean null** (d = −0.01, p = 0.60). Room consistency runs from 0.48 to 0.61, at or barely above chance, so even the significant axes do not point the same way from one sitting to the next. If pressed for the faint pattern: women's floor speech is a shade higher on rigour, candour and conversational register and a shade lower on commercial drive and polemical stance. It is not a character.

**Real speaker gender does not carry a character signature in floor speech once the sitting is held fixed and length is matched.**

---

## What does survive the room: political position, and age

The same scoring run, the same rooms and the same statistical power **do** resolve other real attributes, which is the internal control for the gender null: the instrument is plainly not blind to a within room "who" difference, it simply does not find one for sex.

### Coalition versus opposition (1,235 pairs, 301 rooms): a real, room consistent signature

Opposition minus coalition:

| axis | diff (opp−coal) | paired d | p_perm | roomcons |
|---|---|---|---|---|
| affect | +0.084 | 0.34 | .0005 | **0.77** |
| stance | +0.053 | 0.24 | .0005 | **0.71** |
| register | −0.074 | −0.29 | .0005 | **0.73** |
| rigour | −0.039 | −0.20 | .0005 | 0.63 |
| originality | +0.023 | 0.12 | .0005 | 0.59 |
| PC1 | +0.29 | 0.15 | .0005 | 0.64 |
| mm | −0.021 | −0.15 | .0005 | 0.61 |

Opposition speech runs hotter (affect, d = 0.34), more polemical (stance, d = 0.24), more institutional in register, slightly less rigorous, and leans to manner over matter (mm negative). Effects are small to moderate but, unlike gender, they are **consistent across rooms** (0.71 to 0.77 on the top axes). This is a genuine person side signal that survives the atlas control, and it is a **political role**, not a sex.

### Age (room demeaned, length controlled): a small but coherent gradient

Slope per decade of age within a room: older speakers show lower affect (−0.016, t = −4.5), lower polemical stance (−0.020, t = −6.3), higher conversational register (+0.017, t = +4.5), and lean more to matter (mm +0.007, t = +3.1; PC1 −0.058, t = −2.1). Small per decade, but coherent and significant: **age carries a clearer character gradient than gender does.**

### Party and nationality

- **Party** (within room, eleven parties, one way variance of the room demeaned axis): every eta squared is at most 0.073 (affect 0.073, register 0.057, PC1 0.048). Party explains at most about seven percent of within room variance, and most of that tracks position rather than a distinct party voice.
- **Nationality** (Arab minus Jewish, only 59 pairs across 53 rooms): underpowered. Only affect reaches significance (+0.073, d = 0.33, p = .019); PC1 is +0.38 but its interval crosses zero. Suggestive of higher affect for Arab members, not conclusive on this slice.

---

## Robustness and honesty

- **Internal control for the null**: the gender null is measured on the same turns, rooms, instrument and sample size that resolve position (d = 0.34) and age (t = 6.3). The scorer is not blind to a within room difference; there simply is not one for sex.
- **Cross lineage panel not achieved**: the intended second scorer (a Qwen 27B on port 8288) degenerated on truncated Hebrew, returning the schema's default 0.5 on every axis (72 of 600 parsed, all degenerate). We report this rather than manufacture agreement. A proper second scorer needs a Hebrew capable model with enough context to read a full turn; that is the follow up before this goes to print.
- **Confounds stated**: one institution, one term (the 13th Knesset, 1993 to 1996), one language scored by a multilingual seven billion parameter model. Women were about ten percent of speaking turns in this term, so gender is entangled with era and with committee and seniority structure. Within room length matching removes the room and the length; the age leg removes part of the seniority story; we cannot fully separate committee assignment. Chairman turns are removed. Gender is binary in the source, no third category is recorded.

---

## Verdict

Measured on **ground truth speaker demographics** rather than inferred disposition, **real speaker sex carries no character signature in Knesset floor speech once the sitting is held fixed and length is matched**. The principal character dimension is a clean null and every axis effect is below d = 0.17 with near chance room consistency. What reads as a person side "who" signal in this legislature is **political position** (opposition speaks hotter and more polemical, room consistent at d = 0.34) and **age** (older speech is calmer and more matter leaning), not gender. This is the strong, publishable null the who leg needed: the room is the character, the speaker's sex is not.

*One institution, one language, one term; a Hebrew capable second scorer would harden it. Scripts and the scored summary sit alongside this file.*

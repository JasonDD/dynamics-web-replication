# Can an attacker evade the manipulation detector, and what does evasion cost?

**Programme:** DYNAMICS-WEB. **Question:** every buyer asks whether an adaptive attacker can adapt. So we
red teamed our own detector. Can a language model be prompted to write text that still pursues a
manipulative goal but reads as calm, rigorous and high candour, so it evades the affect inflated matter
starved signature the detector fires on? And if it can, does evading cost the attacker anything?

**Verdict:** evasion is **easy and total as a gate problem, and it is not free**. A model told to sound
calm and evidence led evades the detector on every attempt (100 percent), and no single axis holds it back.
But evasion is not cosmetic. To drop below the detector the text has to move from the manner pole to the
matter pole, and by our audience coupling map that move de targets the very readers the manipulation was
built to exploit. The detector is not an adversarially robust filter. It is a diagnostic whose signature
coincides with the manipulation's channel to the susceptible reader, so the honest product claim is a risk
signal, not a gate.

---

## 1. Method

Thirty overtly manipulative goals, fifteen commercial dark patterns (scarcity, urgency, social proof,
misdirection, confirmshaming, hidden fees, forced continuity, fake authority, drip pricing, sunk cost,
review pressure, bait and switch, guilt upsell, health scare, loss aversion) and fifteen troll persuasion
goals (outrage, us versus them, conspiracy, fear, grievance, wedge, doomerism, whataboutism,
disinformation, false flag, purity spiral, scapegoat, health distrust, astroturf, pile on).

For each goal a local model wrote one **overt** version (told to be maximally manipulative) and two
**evasive** rewrites of the same goal, each told what the detector keys on and asked to defeat it while
still steering the reader to the same action. One evasive style is a calm evidence led analyst voice with a
concrete number, a named source and an honest caveat; the other is plain high candour consumer copy that
states costs openly and sounds balanced. Ninety texts in total.

The detector is the real one: a full eight axis character classifier fitted on real corpora, state
sponsored political trolls against sincere long form argument and length matched short political claims,
balanced cross validated area under the curve 0.947, decision at probability 0.5. Two single axis rules
were included for the ablation, both set to their best operating point on the same real data: an affect
only rule and a manner inflation residual rule (the residual is emotional and rhetorical loading minus
substantive rigour and depth). All ninety texts were scored on the same eight axis instrument used
throughout the series.

**Persuasive power** is read through the audience coupling gradient used elsewhere in the programme:
projection of a text's character onto the reward pattern of the affect valuing audience (the vulnerable
persona these patterns target) and, for contrast, the rigour valuing audience. This is a disposition level
proxy, not measured behaviour.

## 2. Evasion rate

| Detector | overt caught | evasion rate |
|---|---|---|
| Full eight axis | 26 of 30 | **100 percent** |
| Affect axis alone | 30 of 30 | **100 percent** |
| Residual alone | 29 of 30 | **100 percent** |

Every evasive rewrite whose overt twin the detector had caught fell below threshold. This is true of the
full eight axis classifier and of both single axis rules. As a binary gate the detector is fully evadable
by a model instructed to sound calm and rigorous.

## 3. Which axes hold up

None, as a gate. Calm rigorous rewriting is a **global** move: it lowers affect and raises rigour, depth and
register at the same time, so the full classifier and the single axis rules all fail together. Against this
attack the eight axis reading buys no extra robustness over a single axis. The worth of the full instrument
is diagnostic richness and the coupling read, not marginal resistance to this rewrite.

The axis movements show why. To evade, the model had to drop **affect** by 0.42 and lift **rigour** by 0.54
and **depth** by 0.34. Most other manipulative markers could be dressed up, and candour and originality even
rose slightly. The one marker the attacker could not keep was affect, and affect is what binds the message
to the audience it targets.

## 4. Does evasion cost persuasive power?

Yes, on the coupling proxy, and the cost is large.

- The manner inflation residual falls from +0.38 to -0.16 and flips sign: the evasive text stops presenting
  as feeling over substance at all.
- Coupling to the **vulnerable** affect valuing audience falls from +0.09 to -0.05.
- Coupling to the **resistant** rigour valuing audience rises from -0.37 to +0.18.

This is the inoculation result read from the attacker's side. The signature the detector fires on is the
same thing that couples the message to the susceptible reader. Removing it to hide from the detector removes
the persuasive channel to that reader and re aims the text at the audience least moved by manipulation. The
attacker can evade the detector or keep the punch against the vulnerable audience, but the same axis governs
both, so not both at once.

## 5. What this means for the product

- **Do not sell the detector as a filter that stops an adaptive attacker.** As a 0.5 gate it is fully
  evadable. State this plainly.
- **Sell it as a risk signal, and read two signals not one.** An evasive text scores near zero on
  manipulation but also near zero on coupling to the vulnerable audience. Effective manipulation cannot sit
  in both low boxes. A read that pairs the manipulation score with the audience coupling separates evaded
  and defanged text from live manipulation in a way the gate alone cannot.
- **The evasion is the defence.** Forcing a manipulator onto the matter pole to escape detection is exactly
  the inoculation move that de targets the vulnerable reader. The detector and the fix point at the same
  axis.

## 6. Honest caveats

- **We cannot fully separate evaded while still manipulative from evaded by becoming honest.** At high
  rigour, high candour and moderate affect the evasive rewrites read as genuine balanced advice. Forcing
  matter and candour probably converts much of the manipulation into legitimate persuasion, which is the
  cost, but a human rating of whether each evasive text still achieves its goal is the confirmation still
  owed.
- **The persuasive power figure is a disposition level coupling proxy**, not a real shopper or reader and
  not measured behaviour. The clean test is a partnered persuasion trial of overt against evasive text on
  real susceptible readers.
- **One generator, one detector, short texts.** A stronger attacker model, or one that adds real substance
  rather than surface markers of it, is the open threat this test does not close.
- **The 100 percent figure is against a fixed 0.5 gate.** It is a statement about the gate, not about the
  two signal read in section 5.

---

*The evasion prompts and the generated evasive exemplars are held in a restricted internal store under
responsible disclosure and are deliberately not reproduced here: this file publishes the robustness verdict,
never the recipe.*

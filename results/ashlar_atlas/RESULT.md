# The Ashlar atlas: the full 8x8 disposition to character map, re-surveyed

*DYNAMICS-WEB series, 3 September 2026. Script `cc_ashlar_atlas.py`. Ashlar is the keystone, the map from
the eight disposition axes (DYNAMICS-8) to the eight character axes of the writing (DYNAMICS-WEB). The
equation of state work reduced that map to a single matter against manner ruler; this re-surveys the whole
of it, cell by cell, so the trade secret is measured rather than represented by one slice. Method: within
room differencing on the cross site corpus (the room offset cancels exactly, dC = W dP, no intercept),
room block bootstrap for a per cell interval, on three reader legs to break circularity, A (both axes one
reader), and the two cross legs Xpb (disposition and character by different families) and Xpa (the swap).*

## The map holds and it is richer than the single ruler

- **Full corpus (leg A):** 668,365 rows, 40,774 rooms, 1,723 with five or more persons, 364,052 within
  room pairs. 60 of the 64 cells clear zero (the sample is large), so the readable object is the pattern of
  the strong cells, not the count.
- **It survives a reader swap.** The whole 8x8 map correlates 0.83 between A and the disposition swap, and
  0.63 between A and the character swap; 7 of the 8 strongest cells keep their sign across both independent
  model families. The map is a property of the texts, not of one scorer. The character reader matters more
  to the map than the disposition reader (the character swap weakens it more), which is worth noting.

## The strongest cells (leg A; those that keep sign on both cross legs marked robust)

| Disposition | Character | weight | cross reader |
|---|---|---|---|
| candour | commercial drive | −0.25 | robust (−0.26, −0.24) |
| candour | candour | +0.22 | robust (+0.17, +0.25) |
| discipline | rigour | +0.21 | robust (+0.16, +0.28) |
| novelty | originality | +0.21 | robust (+0.16, +0.11) |
| impulsivity | depth | −0.22 | robust (−0.09, −0.17) |
| sociability | affect | +0.24 | holds on the disposition swap |
| candour | affect | +0.27 | washes out on the character swap |
| discipline | register | +0.17, affect −0.17, commercial drive +0.16 | |

The reading a single matter against manner ruler could not give: a candid person writes with transparency
and low sell; a disciplined person writes rigorously and institutionally; novelty seeking shows as
originality; impulsivity shows as shallowness. These are specific disposition to character routes that the
principal component collapse hid.

## Reconciliation with the equation of state

Projected onto the two metatraits and the matter against manner and originality pair, the atlas gives the
same off diagonal coupling the equation of state found, on all three legs: plasticity to originality
(+0.098 / +0.055 / +0.041 across A, Xpb, Xpa) and stability to matter against manner (+0.101 / +0.036 /
+0.089), with the diagonal near zero. So the equation of state is the two metatrait shadow of this atlas,
and the atlas is the object the coupling paper should carry, with matter against manner as its leading
slice rather than its whole.

## Bounds

Effect sizes are modest, 0.1 to 0.27; some strong rows involve disposition axes that two readers agree on
less well (yielding, impulsivity), so those routes are softer than the candour, discipline, novelty and
sociability ones and are read with the reliability table in `../d8_robustness/`. Cross site corpus, the
room is the domain, one differencing design.

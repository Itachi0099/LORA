# Task 2.12 — `score/phrase.py`: phrase offset

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.4
**Status:** done
**Depends on:** 2.5

## Objective
Compute where the incoming track's first downbeat lands relative to the outgoing
track's 32-bar phrase grid.

## Steps
- Assume 4/4, 32-bar phrases (holds for nearly all four-to-the-floor dance music, per §4.4).
- Build the outgoing track's phrase grid from the downbeat grid (2.5).
- `phrase_offset_bars = incoming_first_downbeat_bar mod 32`.
- Report the raw number only — no "good/bad" verdict. 0 and 16 are common/intentional;
  anything else is usually a mistake, but that judgement is left to the reader.

## Done when
- Given a synthetic downbeat grid and a known incoming-track offset, `phrase_offset_bars`
  returns the correct value mod 32.
- No verdict/label is emitted alongside the number.

## Notes / Risks
This module is gate-measured (phrase offset exact-match ≥ 0.80) — get the mod-32 math
exactly right; an off-by-one here silently fails the gate metric without an obvious cause.

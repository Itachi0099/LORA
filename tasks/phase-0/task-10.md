# Task 0.10 — Overlap-feasibility & fallback decision

- [x] Done

**Phase:** 0 — Environment & notebook prototype
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.3, §Known risks 2
**Status:** done, provisional — see notebooks/SYNTHETIC_VALIDATION.md
**Depends on:** 0.7

## Objective
Decide, before building `/analyzer/`, whether overlap boundaries can be recovered from
timbre stabilisation — and commit to the fallback if not.

## Steps
- Prototype searching outward from a novelty peak for where the timbre feature vector
  stabilises on each side (last stable outgoing / first stable incoming frame).
- Assess reliability against the hand labels on the 3 mixes.
- Make the call: recover `overlap_bars`, OR fall back to reporting transition points +
  `confidence` only and drop `overlap_bars` from output.

## Done when
- A documented decision: overlap estimation IN, or points-only fallback.
- The chosen path is what Phase 2 task 2.11 will implement.

## Notes / Risks
Known Risk 2: "Decide the fallback before building, not after it fails." This is the whole
point of the task — do not defer it.

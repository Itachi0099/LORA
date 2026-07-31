# Task 2.11 — `detect/overlap.py`: overlap boundary estimation

- [x] Done

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.3
**Status:** done
**Depends on:** 2.5, 2.10, 0.10

## Objective
For each merged candidate, estimate the overlap span — or apply the points-only fallback
decided in Task 0.10, whichever that task concluded.

## Steps
- Implement whichever path Task 0.10 committed to:
  - **If overlap recovery is IN:** search outward from the candidate peak for where the
    timbre feature vector stabilises on each side (last stable outgoing / first stable
    incoming frame); convert the span to bars via the 2.5 downbeat grid → `overlap_bars`.
  - **If fallback:** report the transition point + `confidence` only, and omit
    `overlap_bars` from the candidate's output entirely — do not emit a placeholder or
    guessed value.
- Whichever path is taken, make it explicit in code/docstring which Task 0.10 decision
  this implements.

## Done when
- Output matches whichever contract 0.10 specified.
- If `overlap_bars` is fallback-omitted, downstream code (2.13 eval, later Step 3 scoring)
  handles its absence rather than assuming it's always present.

## Notes / Risks
This is the single task most likely to be blocked by an unresolved 0.10 — do not start
this until that decision is actually recorded, not assumed.

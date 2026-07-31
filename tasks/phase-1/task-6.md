# Task 1.6 — Document labelling method & tolerance

**Phase:** 1 — Ground truth set
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §Validation
**Status:** blocked (needs user-supplied mixes; see notes)
**Depends on:** 1.4

## Objective
Write a short fixtures README documenting how labels were produced and the tolerance
convention, so the ground truth is reproducible and auditable.

## Steps
- Describe the listening/marking method for start/end times.
- State the ±2s centre-match tolerance used by the gate.
- Note genre/blend tag definitions and any judgement calls made.

## Done when
- A `tests/fixtures/README` (or section) documents method + tolerance.

## Notes / Risks
Undocumented labelling turns gate disputes into guesswork — this makes the ground truth
defensible when detection numbers are close to the threshold.

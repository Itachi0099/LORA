# Task 2.17 — Record gate numbers in the README

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §Validation
**Status:** blocked (needs Phase 1 ground-truth set — labels.json)
**Depends on:** 2.15, 2.16

## Objective
Make the current gate status visible in the repo README, and keep it current on every
detection change.

## Steps
- Add a section to `README.md` with the four gate metrics, current values, and pass/fail
  against the thresholds (Recall ≥0.90, Precision ≥0.85, overlap median ≤4 bars, phrase
  exact ≥0.80).
- Note the date/commit the numbers were last measured.
- Re-run `--eval` (2.14) and update this section on every subsequent change to
  `detect/`, `features/`, or the tuned config values.

## Done when
- README has a gate-status section with real numbers from the tuned run (2.15).
- The convention ("re-run on every detection change") is stated in the README itself,
  not just followed ad hoc.

## Notes / Risks
This table is what task **G** (gate check) reads to decide whether Step 3 can start —
keep it honest; a stale or cherry-picked number here defeats the entire point of the gate.

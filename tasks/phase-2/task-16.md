# Task 2.16 — Tests: detection, merge, phrase offset

- [x] Done

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §6
**Status:** done
**Depends on:** 2.8, 2.9, 2.10, 2.12

## Objective
Add unit test coverage for the detection and phrase-offset logic per the §6 test layout,
independent of the full-mix `--eval` run.

## Steps
- `tests/test_detect.py`: novelty peak-picking, changepoint detection, and `merge.py`'s
  union/collapse/confidence logic, each on small synthetic feature matrices.
- `tests/test_phrase.py`: `phrase_offset_bars` mod-32 math on constructed downbeat grids,
  including edge cases (offset exactly 0, exactly 16, wrap-around near 32).

## Done when
- Both test files exist and pass.
- Merge collapse-window and phrase mod-32 edge cases are explicitly covered, not just
  the happy path.

## Notes / Risks
`test_metrics.py` (§6) covers Step 3 scoring metrics — out of scope here; don't pull it
forward before scoring code exists.

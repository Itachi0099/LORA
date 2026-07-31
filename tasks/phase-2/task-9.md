# Task 2.9 — `detect/changepoint.py`: `ruptures` PELT + RBF

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.2-B
**Status:** done
**Depends on:** 2.4, 2.6

## Objective
Port the Task 0.8 changepoint prototype into the package as the second, independent
candidate detector, catching slow drifts novelty smooths over.

## Steps
- Run `ruptures` PELT with RBF cost over the same stacked feature matrix as `novelty.py`.
- Read the penalty from `config.py` (2.2) rather than hardcoding it — it gets tuned in 2.15.
- Return changepoint locations in a form `merge.py` can union with novelty peaks.

## Done when
- Matches the Task 0.8 notebook's changepoints on the same input.
- Penalty is config-driven, not a literal in this module.

## Notes / Risks
The two detectors are meant to be complementary (confirmed in Task 0.8), not redundant —
don't tune this one to mimic `novelty.py`'s hits; preserve whatever independent signal it
was catching in the prototype (hard cuts vs. slow drifts).

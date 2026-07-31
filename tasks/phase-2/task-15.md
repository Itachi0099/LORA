# Task 2.15 — Tune detector penalty/threshold, biased toward recall

- [ ] Blocked

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §Validation
**Status:** blocked — needs real ground truth to tune against
**Depends on:** 2.14

## Objective
Tune `ruptures` PELT penalty and the novelty adaptive threshold against the validation
set until the gate metrics move toward passing — explicitly biased toward recall.

## Steps
- Sweep `changepoint.py`'s penalty and `novelty.py`'s threshold (both config-driven, 2.2).
- Re-run `--eval` (2.14) after each change; track all four numbers, not just recall.
- Where a tradeoff exists, favor recall over precision — a missed transition is a silent
  tool failure; a spurious one costs five seconds of listening (§Validation).

## Done when
- A tuned config value set is committed for both detectors.
- The four gate numbers from the tuned run are recorded (feeds directly into 2.17).

## Notes / Risks
This is iterative — expect to revisit 2.8/2.9/2.10 logic, not just config values, if
tuning alone can't close the gap. Don't over-fit thresholds to the 20-mix set at the
expense of generalizing; the set is meant to be representative, not a target to overfit.

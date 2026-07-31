# Task 0.8 — Prototype ruptures changepoint detection

- [x] Done

**Phase:** 0 — Environment & notebook prototype
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.2-B
**Status:** done — see notebooks/SYNTHETIC_VALIDATION.md
**Depends on:** 0.7

## Objective
Prototype the second, independent detector: `ruptures` PELT with an RBF cost on the
feature stream, to catch slow drifts novelty smooths over.

## Steps
- Run `ruptures` PELT + RBF over the same feature matrix from 0.7.
- Sweep the penalty; observe how breakpoints track the labelled transitions.
- Compare changepoint hits vs novelty hits — note where each wins.

## Done when
- Changepoints plotted against labels for all 3 mixes.
- Notes on which detector catches which transition types (hard cuts vs slow drifts).

## Notes / Risks
The two detectors are meant to be unioned later — the value here is confirming they're
complementary, not redundant.

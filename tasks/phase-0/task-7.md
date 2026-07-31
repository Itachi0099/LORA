# Task 0.7 — Prototype Foote novelty detection

- [x] Done

**Phase:** 0 — Environment & notebook prototype
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.1, §4.2-A
**Status:** done — see notebooks/SYNTHETIC_VALIDATION.md
**Depends on:** 0.4, 0.6

## Objective
Prototype the detection pipeline: decode → stacked feature matrix → Foote novelty, and
eyeball peaks against the hand labels.

## Steps
- Decode a mix to 22050 Hz mono (hop 512).
- Build a stacked feature matrix: MFCC (20 + deltas) + spectral contrast + band RMS.
- Compute Foote self-similarity novelty with a checkerboard kernel sized ≈ 16 bars.
- Peak-pick with an adaptive threshold; overlay peaks against 0.6 labels.

## Done when
- Novelty curve + detected peaks plotted against labels for all 3 mixes.
- A qualitative read on hit/miss is recorded in the notebook.

## Notes / Risks
Detection should target the overlap region, not a sharp boundary — expect blends to
show as broad novelty humps, not spikes.

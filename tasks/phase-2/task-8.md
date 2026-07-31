# Task 2.8 — `detect/novelty.py`: Foote self-similarity novelty

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.2-A
**Status:** done
**Depends on:** 2.4, 2.6, 2.7

## Objective
Port the Task 0.7 novelty prototype into the package as the first of the two candidate
detectors, with peak prominence exposed for downstream confidence scoring.

## Steps
- Build the stacked feature matrix (MFCC + deltas, spectral contrast, band RMS, chroma CENS).
- Checkerboard kernel sized to ≈16 bars (use the downbeat grid from 2.5 to convert bars → frames).
- Adaptive-threshold peak picking over the novelty curve.
- Return each peak's location *and* prominence (needed by `merge.py` for confidence).

## Done when
- Matches the Task 0.7 notebook's novelty curve shape on the same input.
- Peak list includes prominence, not just location.

## Notes / Risks
Detection targets the overlap region, not a sharp boundary (§3) — expect broad humps.
Don't tighten peak-picking to expect spikes; that regresses exactly the behavior §3 warns about.

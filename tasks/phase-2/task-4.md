# Task 2.4 — `features/timbre.py`: MFCC + spectral contrast

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.1
**Status:** done
**Depends on:** 2.1, 2.2, 2.3

## Objective
Port the Task 0.7 prototype's timbre feature extraction into the package, as the first
piece of the stacked feature matrix.

## Steps
- `mfcc(y, sr) -> np.ndarray`: 20 coefficients + deltas (librosa), hop size from `config.py`.
- `spectral_contrast(y, sr) -> np.ndarray`, same hop size.
- Match the exact framing (`hop_length=512`) used everywhere else so feature streams
  stack without resampling.

## Done when
- Both functions return frame-aligned arrays on a known test signal.
- Output matches the notebook prototype's MFCC/contrast values on the same input (sanity
  check against Task 0.7's notebook cell).

## Notes / Risks
Keep this a straight port from the notebook — Phase 0 already proved the feature choice;
this task is packaging, not re-design.

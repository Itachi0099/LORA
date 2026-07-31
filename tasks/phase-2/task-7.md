# Task 2.7 — Add Chroma CENS to the feature set

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.1
**Status:** done
**Depends on:** 2.4

## Objective
Add the harmonic-change cue (Chroma CENS) to the stacked feature matrix — weak signal on
its own, but non-zero, and cheap to include.

## Steps
- `chroma_cens(y, sr) -> np.ndarray` via librosa, frame-aligned to the same hop size.
- Add it to whichever module builds the stacked matrix consumed by `detect/novelty.py`
  and `detect/changepoint.py` (either `timbre.py` or a shared assembly point — pick one
  and keep it consistent).

## Done when
- Chroma CENS output is frame-aligned with MFCC/contrast/band-RMS from 2.4/2.6.
- The stacked matrix used by detection includes it without shape mismatches.

## Notes / Risks
§3 is explicit that chroma is "near useless" on genre-homogeneous material — don't let it
dominate the stack; it's an additive weak cue, not a primary feature.

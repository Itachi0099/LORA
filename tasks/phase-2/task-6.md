# Task 2.6 — `features/spectral.py`: band RMS & stereo width

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.1, §3
**Status:** done
**Depends on:** 2.1, 2.2, 2.3

## Objective
Port the band-RMS prototype (Task 0.7) and add stereo width — the two cues most likely
to survive on the homogeneous worst case (§3.3, Known Risk 1) when timbre contrast fails.

## Steps
- `band_rms(y, sr, bands) -> np.ndarray`: low/mid/high energy per frame, same band splits
  used in the Task 0.7/0.9 prototype.
- `stereo_width(y_stereo) -> np.ndarray`: mid/side ratio per frame, using the stereo
  44.1k handle from `io.decode_stereo`, widens during a blend.
- Frame-align both to the same hop size as `timbre.py` / `rhythm.py`.

## Done when
- Both functions run on a test signal and produce frame-aligned output.
- Stereo width shows a measurable rise on a synthetic two-source overlap (basic sanity
  check, doesn't need real mixes).

## Notes / Risks
If Task 0.9 found timbre contrast collapsing on homogeneous sets, these two features are
the fallback signal (per that task's Notes/Risks) — treat them as first-class, not optional.

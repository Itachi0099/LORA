# Task 2.2 — `config.py`: thresholds & feature params

- [x] Done

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.1, §5.3
**Status:** done
**Depends on:** 2.1

## Objective
Centralise every tunable constant — hop size, sample rates, detector penalties, flag
thresholds — in one module, documented as opinions rather than facts.

## Steps
- `HOP_LENGTH = 512`.
- `SR_ANALYSIS = 22050` (mono analysis), `SR_STEREO = 44100` (loudness/width handle).
- Feature params: MFCC coeff count (20), spectral contrast bands, band-RMS split points.
- Detector params: Foote checkerboard kernel size (~16 bars), `ruptures` PELT penalty,
  merge-collapse window (8 bars).
- Placeholders for the §5.3 flag thresholds (`bass_stacking` > 3.0 dB, `dead_air` > 400ms,
  etc.) even though flags themselves are Step 3 — the numbers belong in one place from the start.

## Done when
- A single import of `analyzer.config` exposes every constant used by features/detect modules.
- Each constant has a one-line comment stating it's a tunable opinion, not a derived fact.

## Notes / Risks
This is the "single source of truth" module called out in §4.5 — resist scattering a
magic number into `novelty.py` or `changepoint.py` "just this once."

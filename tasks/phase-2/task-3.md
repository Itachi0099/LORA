# Task 2.3 — `io.py`: decode & source metadata

- [x] Done

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.1, §6
**Status:** done
**Depends on:** 2.1, 2.2

## Objective
Turn the Task 0.2 ffmpeg decode check into a real module: decode any accepted input
format to the two handles the rest of the pipeline needs, plus source identity metadata.

## Steps
- `decode_mono(path) -> np.ndarray` at `config.SR_ANALYSIS`, using the ffmpeg command
  verified in Task 0.2 (`notebooks/ENVIRONMENT.md` has the exact invocation).
- `decode_stereo(path) -> np.ndarray` at `config.SR_STEREO`, unresampled, for loudness/width.
- Handle WAV, FLAC, MP3, AIFF explicitly; raise a clear error on anything else.
- Compute `sha256` and `duration_s` for the source file (same fields the labels schema
  uses — Task 1.1 — so a mix and its label entry can be cross-checked).

## Done when
- Both decode paths work on all four formats.
- `sha256`/`duration_s` match what a labels.json entry would expect for the same file.

## Notes / Risks
Reuse the exact ffmpeg invocations already verified in Task 0.2 rather than re-deriving
them — that check exists precisely to avoid surprises here.

# Task 0.2 — Verify ffmpeg decode

**Phase:** 0 — Environment & notebook prototype
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.1
**Status:** done
**Depends on:** —

## Objective
Confirm `ffmpeg` is available and can decode every input format the analyzer accepts.

## Steps
- Verify `ffmpeg` is on PATH (`ffmpeg -version`).
- Decode a sample of each format: WAV, FLAC, MP3, AIFF.
- Confirm decode to 22050 Hz mono works, and a stereo 44.1k handle is retrievable.

## Done when
- All four formats decode without error.
- A one-liner decode command is captured for reuse in the prototype.

## Notes / Risks
This underpins `io.py` later; catching format/codec gaps now avoids surprises in Phase 2.

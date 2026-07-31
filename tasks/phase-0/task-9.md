# Task 0.9 — Stress-test the homogeneous worst case

**Phase:** 0 — Environment & notebook prototype
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §Known risks 1, §3.3
**Status:** blocked (needs user-supplied mixes; see notes)
**Depends on:** 0.7, 0.8

## Objective
Test detection on a minimal/industrial techno set — the worst case where timbre contrast
nearly vanishes — before trusting the approach.

## Steps
- Run the 0.7/0.8 pipeline on a homogeneous minimal-techno passage.
- Check whether ANY feature (spectral contrast, band RMS ratios, stereo width) still
  separates transitions from steady state.
- Record whether detection survives or collapses on this case.

## Done when
- A clear yes/no on whether usable contrast survives is documented.
- If no: note which alternative cues (stereo width, low-band ratio) to lean on.

## Notes / Risks
Known Risk 1 and a very common real-world case. If this fails, the kill gate is at risk —
better to learn it now than after building the package.

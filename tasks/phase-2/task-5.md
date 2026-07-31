# Task 2.5 — `features/rhythm.py`: beats, downbeats, tempo curve

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.1, §4.4
**Status:** done
**Depends on:** 2.1, 2.2, 2.3

## Objective
Provide the bar grid (beats + downbeats) and a windowed tempo curve that overlap
estimation (2.11) and phrase alignment (2.12) both depend on.

## Steps
- Wrap madmom `DBNDownBeatTracker` (pinned in Task 0.1) behind a small interface, e.g.
  `track_downbeats(y, sr) -> DownbeatGrid`.
- Compute a windowed tempo curve (librosa or madmom) to expose drift/tempo changepoints.
- Wire the Task 0.1 fallback decision behind the *same* interface: if madmom is
  unavailable in a given environment, swap in `librosa.beat.beat_track` without changing
  any caller. Per `notebooks/ENVIRONMENT.md`, madmom worked in the pinned env, so this
  fallback path can be a documented no-op stub for now rather than a fully built branch.

## Done when
- `track_downbeats` returns a usable bar grid on a test signal.
- The fallback interface exists (even if unexercised) so a future swap doesn't ripple
  into `overlap.py` / `phrase.py`.

## Notes / Risks
Known Risk 5 territory — keep the madmom-specific bits isolated to this module so any
future interpreter/dependency upgrade that breaks madmom again is a one-file fix.

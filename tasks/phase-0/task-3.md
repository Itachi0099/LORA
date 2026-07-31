# Task 0.3 — Install analysis dependencies

- [x] Done

**Phase:** 0 — Environment & notebook prototype
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4
**Status:** done
**Depends on:** 0.1

## Objective
Install the analysis stack needed for the prototype.

## Steps
- Install `librosa`, `numpy`, `scipy`, `ruptures`, `madmom` (from 0.1), and the notebook stack.
- Confirm imports load cleanly together (watch for numpy/scipy ABI conflicts with madmom).
- Freeze the resolved versions.

## Done when
- A single import cell loads all libraries without error.
- Resolved versions are frozen to an env/lock file.

## Notes / Risks
`ruptures` and `madmom` can pull conflicting numpy pins — resolve here, not in the notebook.

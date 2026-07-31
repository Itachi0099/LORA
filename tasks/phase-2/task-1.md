# Task 2.1 — Scaffold the repo

- [x] Done

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §6
**Status:** done
**Depends on:** —

## Objective
Lay down the `/analyzer` package skeleton per the §6 repo structure, so feature/detect/score
modules have a fixed home before any detection code is written.

## Steps
- Create `pyproject.toml` (or extend the Phase 0 one) at repo root.
- Create `/analyzer/__init__.py`, `/analyzer/config.py`, `/analyzer/io.py`.
- Create `/analyzer/features/__init__.py` (for `timbre.py`, `rhythm.py`, `spectral.py`).
- Create `/analyzer/detect/__init__.py` (for `novelty.py`, `changepoint.py`, `merge.py`, `overlap.py`).
- Create `/analyzer/score/__init__.py` with `phrase.py` (loudness/metrics/flags are Step 3,
  out of scope here — see TASKS.md "Out of scope").
- Create `/tests/` alongside the existing `/tests/fixtures/`.

## Done when
- The full module tree from §6 exists (empty modules are fine at this point).
- `python -c "import analyzer"` succeeds from repo root.

## Notes / Risks
Keep this a pure scaffold — no detection logic yet. Nothing outside Phase 2 gets built
until the gate is green (TASKS.md), so resist the urge to stub `score/loudness.py` or
`report.py` here even though they're in the §6 tree; add them only when Step 3 starts.

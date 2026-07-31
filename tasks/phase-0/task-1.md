# Task 0.1 — Set up Python env & pin madmom

- [x] Done

**Phase:** 0 — Environment & notebook prototype
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §Known risks 5
**Status:** done
**Depends on:** —

## Objective
Create a reproducible Python environment with a pinned `madmom` + compatible Python
version, so beat/downbeat tracking is available without install friction.

## Steps
- Create an isolated env (venv/conda/uv).
- Pin a Python version known to build `madmom` cleanly.
- Pin `madmom` to a working release; record the exact versions.
- Prototype and document a `librosa` / `basic_pitch` beat-tracking fallback path in
  case the pin fights the interpreter.

## Done when
- `python -c "import madmom"` succeeds in the env.
- Pinned versions are written down (env file / README note).
- Fallback beat-tracker decision is recorded.

## Notes / Risks
madmom install friction is Known Risk 5 — historically painful on newer Python.
Budget time here rather than discovering it mid-prototype.

# Task 2.14 — Minimal `--eval` path

- [x] Done

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §6, §Validation
**Status:** done
**Depends on:** 2.13

## Objective
Provide a runnable entry point (CLI flag or notebook cell — whichever is faster to stand
up first) that runs the full pipeline against `labels.json` and prints the four gate numbers.

## Steps
- Run detection (2.1–2.12) across every mix listed in `labels.json`.
- Feed results into the eval module (2.13).
- Print recall, precision, overlap-length median error, phrase-offset exact-match rate —
  plus the homogeneous-set breakdown.
- A bare-bones `djx analyze mix.wav --labels tests/fixtures/labels.json --eval` argparse
  stub is fine here; the full CLI (`cli.py`, output schema, terminal summary) is Step 3/4,
  out of scope for this phase.

## Done when
- Running the eval path against `labels.json` prints all four numbers without manual steps.

## Notes / Risks
Keep this minimal — a full `cli.py` isn't warranted until Step 4. The only requirement
here is "one command prints the four numbers," not a polished CLI.

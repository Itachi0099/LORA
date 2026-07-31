# Task 1.1 — Define the label schema

**Phase:** 1 — Ground truth set
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §7 Step 1, §Validation
**Status:** done
**Depends on:** —

## Objective
Define the JSON schema for hand-labelled ground truth stored at `tests/fixtures/labels.json`.

## Steps
- Per transition: `start_s`, `end_s`, derived `center_s`.
- Per transition tags: `genre`, `blend_style` (e.g. long-blend, short-blend, hard-cut).
- Per mix: `path`, `sha256`, `duration_s`, plus its transition list.
- Keep it loadable by both the notebook and the future `--eval` harness.

## Done when
- A documented schema (with an example entry) exists.
- The four gate metrics (recall, precision, overlap error, phrase exact) are all
  computable from these fields.

## Notes / Risks
Overlap-length error is a gate metric — the schema MUST carry both `start_s` and `end_s`,
not just a centre.

# Task 1.5 — Write labels.json

**Phase:** 1 — Ground truth set
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §6, §7 Step 1
**Status:** blocked (needs user-supplied mixes; see notes)
**Depends on:** 1.4

## Objective
Serialise the completed labels to `/tests/fixtures/labels.json` in the 1.1 schema.

## Steps
- Write all 20 mixes' labels to `tests/fixtures/labels.json`.
- Validate it parses and conforms to the schema.
- Commit it as the canonical ground-truth fixture.

## Done when
- `tests/fixtures/labels.json` exists, parses, and covers all 20 mixes.
- Loadable by the future `--eval` harness.

## Notes / Risks
This file is the reference the kill gate runs against — treat changes to it as changes to
the evaluation contract.

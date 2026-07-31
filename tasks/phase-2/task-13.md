# Task 2.13 — Eval module: gate metrics

- [x] Done

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §Validation
**Status:** done
**Depends on:** 2.10, 2.11, 2.12, 1.5

## Objective
Compute the four kill-gate metrics by matching detected candidates against
`tests/fixtures/labels.json` (Task 1.5), using the schema from Task 1.1.

## Steps
- Match rule: a detected candidate matches a labelled transition if its estimated
  centre is within ±2s of the label's `center_s` (per `labels.schema.json`).
- **Recall:** fraction of labelled transitions with a matching candidate.
- **Precision:** fraction of detected candidates with a matching label.
- **Overlap-length median error:** median `|detected overlap_bars - (end_s - start_s in bars)|`
  over matched pairs that have `overlap_bars` (skip pairs where 2.11's fallback omitted it,
  and report how many were skipped).
- **Phrase-offset exact-match rate:** fraction of matched pairs where detected
  `phrase_offset_bars` exactly equals the ground-truth value.
- Support per-tag breakdown (by `genre` / `blend_style` / `homogeneous_worst_case`) so the
  homogeneous set (Task 1.3) can be inspected separately from the aggregate.

## Done when
- All four metrics compute correctly on a small hand-constructed candidate/label fixture.
- Homogeneous-flagged mixes can be filtered out for a separate report.

## Notes / Risks
False negatives are worse than false positives here (§Validation) — this module is the
referee, not a tuning knob; keep matching logic simple and exactly spec-compliant rather
than adding leniency that would make the gate easier to pass without the detector improving.

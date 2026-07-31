# Task 1.4 — Hand-label all 20 mixes (start + end)

- [ ] Blocked

**Phase:** 1 — Ground truth set
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §7 Step 1, §Validation
**Status:** blocked — needs real recorded mixes
**Depends on:** 1.1, 1.2

## Objective
Produce precise transition labels for all 20 mixes with both start and end times.

## Steps
- Listen through each mix; mark each transition's `start_s` and `end_s` by ear.
- Derive `center_s`; apply the ±2s centre tolerance convention used by the gate.
- Fill in `genre` / `blend_style` tags per transition.
- Count bars from the outgoing track's phrase grid to the incoming track's first
  downbeat; record as `phrase_offset_bars_truth` (added to the schema during Phase 2
  task 2.13 — the phrase-exact-match gate metric has nothing to compare against
  without it). Leave `null` where this can't be confidently determined by ear.

## Done when
- All 20 mixes fully labelled per the 1.1 schema (as amended by 2.13).
- Start AND end captured for every transition (needed for overlap-length error).
- `phrase_offset_bars_truth` filled in (or explicitly left `null`) for every transition.

## Notes / Risks
Labelling quality caps achievable precision/recall — inconsistent centres will show up as
false gate failures. Be systematic.

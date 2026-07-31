# Task G — Gate check

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §Validation
**Status:** blocked (needs Phase 1 ground-truth set — labels.json)
**Depends on:** 2.17

## Objective
Make the explicit go/no-go call: do the four recorded gate numbers clear their
thresholds, and if so, is the project cleared to proceed to Step 3?

## Steps
- Read the current numbers from the README (2.17).
- Check all four independently:
  - Recall ≥ 0.90
  - Precision ≥ 0.85
  - Overlap-length median error ≤ 4 bars
  - Phrase-offset exact match ≥ 0.80
- All four green → proceed to Step 3 (scoring/report — tracked separately, out of this
  task list per TASKS.md).
- Any red → do not build scoring/report/CLI. Return to iterating 2b–2d (detection,
  merge, overlap/phrase, eval/tuning) instead.

## Done when
- A recorded, dated decision: gate passed (proceed to Step 3) or gate failed (iterate).
- If failed, which specific metric(s) missed and by how much is documented, so the next
  iteration has a concrete target rather than "try again."

## Notes / Risks
This is the kill gate itself (base.md header: "Kill gate: segmentation accuracy on
hand-labelled mixes"). If recall can't clear 0.90, base.md is explicit: "the product does
not exist." Do not soften this into a judgment call — it's a threshold check, not a discussion.

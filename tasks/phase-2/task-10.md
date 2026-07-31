# Task 2.10 — `detect/merge.py`: union & confidence

**Phase:** 2 — Detection to gate (Step 2)
**Source:** [TASKS.md](../../TASKS.md) · [base.md](../../base.md) §4.2
**Status:** done
**Depends on:** 2.8, 2.9

## Objective
Union the novelty peaks (2.8) and changepoints (2.9) into a single candidate list, with a
confidence score per candidate.

## Steps
- Merge rule: candidates within 8 bars of each other collapse to one (bars → frames via
  the downbeat grid from 2.5).
- `confidence` from how many detectors fired on a given candidate plus peak prominence
  (from 2.8's exposed prominence values).
- Preserve enough per-candidate metadata (which detector(s) fired, prominence) for the
  eval harness (2.13) and later scoring (Step 3) to consume.

## Done when
- Given synthetic novelty-peak and changepoint lists, the merge produces the expected
  collapsed candidates and confidence values on a few hand-constructed cases.

## Notes / Risks
This is where "two independent detectors" (§4.2) becomes "one candidate list" — the 8-bar
collapse window is a config value (2.2), not a literal here.

# `labels.json` schema (Task 1.1)

Ground truth for the detection kill gate (base.md §Validation). Machine schema lives in
[`labels.schema.json`](labels.schema.json); this file explains the fields and shows how
each gate metric is computed from them. Labelling method + tolerance convention will be
documented in a `README` alongside this file once the real labelling pass (Task 1.6) happens.

## Shape

```json
{
  "schema_version": 1,
  "mixes": [
    {
      "path": "mixes/warehouse-2026-07.wav",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "duration_s": 4382.6,
      "homogeneous_worst_case": false,
      "transitions": [
        {
          "start_s": 408.0,
          "end_s": 417.6,
          "center_s": 412.8,
          "genre": "techno",
          "blend_style": "long-blend",
          "phrase_offset_bars_truth": 0
        },
        {
          "start_s": 738.0,
          "end_s": 738.0,
          "center_s": 738.0,
          "genre": "techno",
          "blend_style": "hard-cut",
          "phrase_offset_bars_truth": null
        }
      ]
    }
  ]
}
```

## Field notes

- **`start_s` / `end_s`** are both required, even though a hard cut has `start_s == end_s`.
  The overlap-length gate metric needs both edges — a centre-only schema can't produce it.
- **`center_s`** is derived (`(start_s + end_s) / 2`) but stored, not recomputed at load
  time, so the ±2s tolerance is always checked against a fixed, auditable number rather
  than something that could silently drift if the derivation formula ever changes.
- **`sha256`** guards against a mix file being swapped, re-encoded, or re-trimmed without
  the labels being redone — a mismatch should be treated as "labels invalid," not ignored.
- **`homogeneous_worst_case`** is how Task 1.3's mandatory minimal/industrial-techno set
  gets flagged, so `--eval` can report its numbers separately from the rest of the gate.
- **`phrase_offset_bars_truth`** (added while building the Phase 2 eval module, task
  2.13): a manual bar count of where the incoming track's downbeat lands on the
  outgoing track's phrase grid. This wasn't in the original 1.1 schema — it was missed
  because `start_s`/`end_s` alone are enough for recall/precision/overlap-error, but
  the phrase-exact-match gate metric has nothing to compare against without it.
  Nullable: a labeller who can't confidently place it should leave it `null` rather
  than guess, and such transitions are excluded from that metric's denominator.

## Gate metrics ← schema fields

| Gate metric (base.md §Validation) | Computed from |
|---|---|
| Recall ≥ 0.90 | For each labelled `center_s`, is there a detected candidate within ±2s? |
| Precision ≥ 0.85 | For each detected candidate, is there a labelled `center_s` within ±2s? |
| Overlap length error, median ≤ 4 bars | `end_s - start_s` (converted to bars via the downbeat grid) vs. detector's `overlap_bars` |
| Phrase offset exact match ≥ 0.80 | Detected `phrase_offset_bars` (score/phrase.py) compared exactly against labelled `phrase_offset_bars_truth`, over the subset where the latter isn't `null` |

All four are computable from `start_s`, `end_s`, and `center_s` alone; `genre` and
`blend_style` exist so `--eval` can break results down by category (e.g. "recall on
hard-cuts" vs. "recall on long-blends") without touching the metric definitions.

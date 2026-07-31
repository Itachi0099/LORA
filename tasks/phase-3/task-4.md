# Task 3.4 — Extend the report schema with streaming matches

**Phase:** 3 — Streaming app connectivity (deferred, see [phase-3/README.md](README.md))
**Source:** User decision 2026-08-01 (full OAuth account linking) · [base.md](../../base.md) §5.1
**Status:** todo
**Depends on:** 3.1, 3.3

## Objective
Add matched streaming metadata to the `<mixname>.analysis.json` schema (base.md §5.1)
as an additive, optional block — existing local-only consumers must not break.

## Steps
- Add an optional per-transition field, e.g. `streaming_matches: [{provider, track_id,
  title, artist, confidence}]` — plural and confidence-scored, since a beatmatched
  overlap may not resolve to a single confident match (see phase-3/README.md's note on
  fingerprinting during active overlaps being harder than on a clean track).
- Schema version bump (`schema_version`) if the addition isn't purely additive for
  existing parsers.
- No matches / no linked account → field is simply absent, not null or empty-with-error.

## Done when
- Schema documented with an example entry that includes and excludes the new field.
- `ui/src/types.ts`'s `AnalysisReport` type (the existing FE/BE contract) can add this
  as an optional field without breaking current rendering of `sample.analysis.json`.

## Notes / Risks
This is the one piece of Phase 3 that touches the existing, working local-only report
contract — keep it strictly additive and optional.

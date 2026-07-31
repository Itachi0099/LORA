# Task 3.7 — Match-accuracy gate (second kill gate)

**Phase:** 3 — Streaming app connectivity (deferred, see [phase-3/README.md](README.md))
**Source:** User decision 2026-08-01 (full OAuth account linking) · [base.md](../../base.md) §1
**Status:** todo
**Depends on:** 3.4, 3.6

## Objective
Decide whether streaming-match accuracy is good enough to ship, using the same
philosophy as the core product: don't report a number a DJ can't verify by ear in five
seconds (base.md §1).

## Steps
- Run track-ID matching (3.1's chosen feature) against a sample of real detected
  transitions from the Phase 2 ground-truth mixes (once they exist).
- Measure match precision specifically *during the overlap region*, not just on clean
  isolated audio — per phase-3/README.md, fingerprinting two beatmatched, EQ'd tracks
  playing simultaneously is a materially harder problem than matching a single track.
- Decide a threshold below which a low-confidence match is simply omitted rather than
  shown and likely wrong.

## Done when
- A recorded precision number on real transitions, and an explicit go/no-go: ship
  enrichment as-is, ship with a stricter confidence cutoff, or hold the feature.

## Notes / Risks
This is a second, independent kill gate — a working OAuth flow (3.3) proves nothing
about whether the matches it returns are trustworthy. Do not let "the API call works"
substitute for "the DJ can trust what's shown."

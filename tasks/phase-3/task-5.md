# Task 3.5 — Render streaming matches in the existing UI

- [ ] Todo

**Phase:** 3 — Streaming app connectivity (deferred, see [phase-3/README.md](README.md))
**Source:** User decision 2026-08-01 (full OAuth account linking)
**Status:** todo — deferred, see phase-3/README.md
**Depends on:** 3.4

## Objective
Surface the new optional metadata in `ui/` (the existing Vite+React frontend) without
disrupting its current fully-local, no-account rendering path.

## Steps
- Extend the transitions table / detail drawer (`ui/src/App.tsx`) to show matched
  track name/artist/link when `streaming_matches` is present on a transition.
- No visual change at all when the field is absent — this must render identically to
  today's `sample.analysis.json` for a report with no streaming data.
- Any "connect your account" UI lives behind an explicit, clearly-optional entry point
  (e.g. a settings panel), never blocking the default view.

## Done when
- `ui/src/sample.analysis.json` (unmodified) still renders exactly as it does today.
- A second sample report with `streaming_matches` populated renders the enrichment
  correctly.

## Notes / Risks
`ui/README.md` currently describes a Tauri shell not yet wired up (`Rust/cargo are not
installed on this machine yet`) — this task's UI changes should work in the existing
standalone-browser dev mode (`npm run dev`) without assuming Tauri exists yet.

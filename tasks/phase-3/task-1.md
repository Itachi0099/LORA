# Task 3.1 — Decide provider, auth model, and which "linking" feature

- [x] Decided 2026-08-04 (see Notes) — **enrichment only, no OAuth/account linking**
- [ ] Implementation started ahead of the Phase 2 gate (see Notes — flagged, not ideal)

**Phase:** 3 — Streaming app connectivity (deferred, see [phase-3/README.md](README.md))
**Source:** User decision 2026-08-01 (full OAuth account linking) · [base.md](../../base.md) §1 scope
**Status:** decided — narrower than originally scoped; see Notes before reading 3.2–3.6
**Depends on:** Phase 2 gate green (see root `README.md` Gate status) — **not honored**,
see Notes

## Objective
Force the concrete decisions "link to Spotify and other music apps" is currently
hiding, before any auth code exists.

## Steps
- Pick the first provider. Spotify (mature Web API, PKCE flow for installed apps, no
  client secret required) is the likely starting point — Apple Music and SoundCloud
  have different auth models and should each get their own follow-on task, not a
  shared abstraction guessed at now.
- Decide which feature is actually being built first:
  - **Track ID enrichment** (read-only): identify the two tracks in a detected
    transition, attach names/artists/links to the existing local report. Additive,
    no write scopes, no playlist import.
  - **Playlist/tracklist export or import** (read+write): push a recovered tracklist
    to a new Spotify playlist, or import an existing playlist for comparison. This is
    what "account linking" usually implies, and needs write scopes + a real "connect
    your account" flow.
- Document the choice and why, in this task's Notes on completion.

## Done when
- A written decision: provider, auth grant type, and enrichment-vs-export scope.
- The decision explicitly updates base.md §1's "Out (explicitly, for now): ... Any
  upload, server, or account" line — this phase cannot proceed on a stale scope doc.

## Notes / Risks

**Decision (2026-08-04):** Track ID enrichment (option 1), not playlist export/import.
Provider is **AudD** (audio fingerprinting), not a direct Spotify OAuth integration —
AudD resolves a matched track to Spotify/Apple Music metadata in the same response, so
no user account, no OAuth grant, no token storage, and no client-side "connect your
account" flow exist anywhere in this path. That sidesteps most of what 3.2 (keychain
token storage), 3.3 (OAuth prototype), 3.5 (Tauri UI wiring for a linked account), and
3.6 (token revocation/privacy review) were scoped for — those tasks stay relevant only
if a *write* feature (playlist export) or Spotify's own OAuth API is added later, not
for this read-only, tokenless-to-the-user path. Task 3.4 (schema extension) and 3.7
(match-accuracy gate) still apply as originally scoped.

Implemented: `analyzer/identify.py`, `tests/test_identify.py`, `scripts/identify_transitions.py`
(standalone — not wired into a CLI or the `ui/` frontend; see README.md §Track
identification).

**Process gap, flagged rather than hidden:** this phase's own README says *"Status:
scoped, not started. Do not begin before the Phase 2 gate is green"* — the gate is
still unmeasured (root README's Gate status table). The module above was built anyway,
at the requesting user's direction, before that gate. It's kept strictly additive and
outside `analyzer/eval.py`'s gate computation for exactly this reason, but the
sequencing call in phase-3/README.md was knowingly overridden here, not forgotten.

**base.md scope:** this still counts as touching base.md §1's "Out (explicitly, for
now): ... Any upload, server, or account" line — a clip *is* uploaded to a third-party
service (AudD) even without a user account. base.md has been given a narrow, explicit
carve-out for this rather than left silently stale (see base.md's Scope section).

**Still open, carried over from the original task list below:** don't let a future
"add Spotify integration" request default back to building the OAuth/export path
(3.2/3.3/3.5/3.6) without a fresh explicit decision — those remain real scope reversals
if picked up later. Also carried over: fingerprinting a *blend* (two tracks
simultaneously beatmatched) is a harder identification problem than a clean track;
`identify.py` currently samples fixed offsets before/after each transition's peak
(`DEFAULT_TRANSITION_GAP_S = 5.0`) rather than using estimated overlap boundaries
(`analyzer/detect/overlap.py`, itself gated on Task 0.10) — accuracy on real, blended
transitions is unverified (Task 3.7 still applies, unstarted).

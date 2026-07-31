# Task 3.1 — Decide provider, auth model, and which "linking" feature

- [ ] Todo

**Phase:** 3 — Streaming app connectivity (deferred, see [phase-3/README.md](README.md))
**Source:** User decision 2026-08-01 (full OAuth account linking) · [base.md](../../base.md) §1 scope
**Status:** todo — deferred, see phase-3/README.md
**Depends on:** Phase 2 gate green (see root `README.md` Gate status)

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
Don't let "Spotify integration" default to building both features at once — enrichment
and export have completely different scope, risk, and auth requirements.

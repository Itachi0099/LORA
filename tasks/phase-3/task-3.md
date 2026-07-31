# Task 3.3 — Prototype the OAuth flow standalone

**Phase:** 3 — Streaming app connectivity (deferred, see [phase-3/README.md](README.md))
**Source:** User decision 2026-08-01 (full OAuth account linking)
**Status:** todo
**Depends on:** 3.1, 3.2

## Objective
Prove the auth flow works end-to-end against the single provider chosen in 3.1,
outside the main app, before wiring it into the Tauri shell or CLI.

## Steps
- Implement PKCE + loopback redirect (`http://localhost:<port>/callback`) in an
  isolated script — decide explicitly whether this needs any persistent server
  component or if the loopback listener only needs to live for the duration of the
  auth handshake.
- Exchange the auth code for a token; store it via the 3.2 mechanism.
- Confirm token refresh works without re-prompting the user for login.

## Done when
- A standalone script/prototype completes the full auth handshake and a token refresh,
  independent of the analyzer or UI code.

## Notes / Risks
Keep this isolated deliberately — an auth bug discovered while also debugging UI wiring
is much harder to isolate than one found in a 50-line standalone script.

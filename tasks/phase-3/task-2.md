# Task 3.2 — Token storage & scope minimization

- [ ] Todo

**Phase:** 3 — Streaming app connectivity (deferred, see [phase-3/README.md](README.md))
**Source:** User decision 2026-08-01 (full OAuth account linking)
**Status:** todo — deferred, see phase-3/README.md
**Depends on:** 3.1

## Objective
Decide how a refresh token is stored on a user's machine, and request the minimum
scope the 3.1 decision actually needs.

## Steps
- Use OS keychain storage (Tauri has a keychain/stronghold plugin) — never a
  plaintext file or unencrypted config, since this app is desktop-installed and the
  token grants ongoing account access.
- Request read-only scopes (`user-read-private`, search/metadata) unless 3.1 chose the
  export/import feature, which needs playlist write scopes explicitly.
- Design the revocation path: how a user disconnects the linked account, and confirm
  the app still works in fully-local mode with no account connected (this must never
  become a required login).

## Done when
- A documented storage mechanism (keychain, not plaintext) and the exact scope list
  requested, tied to the 3.1 feature choice.
- Confirmed: the analyzer's core local-file flow works with zero account connected.

## Notes / Risks
"Nobody records their sets" (Known Risk 3) already threatens demand — do not compound
it by making the tool feel like it needs a login. The account link must be strictly
optional and additive.

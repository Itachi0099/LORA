# Task 3.6 — Privacy/security review

- [ ] Todo

**Phase:** 3 — Streaming app connectivity (deferred, see [phase-3/README.md](README.md))
**Source:** User decision 2026-08-01 (full OAuth account linking)
**Status:** todo — deferred, see phase-3/README.md
**Depends on:** 3.2, 3.3

## Objective
Formal review of the account-linking surface before it ships to anyone — this is the
first time the project holds a credential to a third-party account.

## Steps
- Confirm token revocation actually revokes provider-side access, not just local deletion.
- Confirm no token or account identifier is ever written into the
  `<mixname>.analysis.json` report itself (that file is meant to be shareable/postable —
  base.md §7 Step 4 mentions posting to r/Beatmatch and r/DJs).
- Confirm the app functions fully offline / with no linked account (re-check 3.2's
  "must never become a required login" requirement holds after all UI/wiring changes).
- Check scope creep: are the requested OAuth scopes still the minimum for whichever
  feature (enrichment vs. export) 3.1 chose, or did later tasks quietly need more?

## Done when
- A written sign-off covering revocation, report-file safety, offline operation, and
  scope minimization — treat any "no" as a blocker, not a note for later.

## Notes / Risks
An analysis report is designed to be shared (posted, sent to a friend) — a credential
or account identifier leaking into that file would be a real privacy incident, not a
cosmetic bug.

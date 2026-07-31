# Phase 3 — Streaming app connectivity (deferred)

**Status: scoped, not started. Do not begin before the Phase 2 gate is green.**

This phase does not exist in [base.md](../../base.md) or [TASKS.md](../../TASKS.md) as
originally written — base.md's scope section is explicit: *"Out (explicitly, for now):
... Any upload, server, or account."* Full OAuth account linking to Spotify/Apple
Music/SoundCloud (confirmed direction, 2026-08-01) is a deliberate reversal of that
line, not an extension of it. Recording that reversal here rather than quietly
building around it.

## Why this is sequenced last, not next

base.md's own build order (§7) already establishes the pattern: *"Only after step 4
does the Tauri UI question become worth asking."* The same logic applies more
strongly here:

- There is no working detection yet (Phase 2 gate unmeasured — see root `README.md`).
  A connectivity feature bolted onto an unvalidated analyzer just adds surface area to
  a product that doesn't yet do its one job.
- There is no CLI (`cli.py` is a `--eval`-only stub) and no shipped UI for an OAuth
  flow to live in. `ui/` is a static-JSON-rendering frontend today, per
  `ui/README.md` — it has no backend to hold a token.
- Known Risk 3 (base.md): *"Nobody records their sets... ask before step 4, not
  after."* Streaming connectivity is a bigger commitment than the Tauri shell and
  should not be built ahead of learning whether anyone uses the core tool at all.

## What "full account linking" needs to actually decide, before any code

- **Which provider first, and why.** Spotify has the most mature Web API + a
  documented PKCE flow for installed desktop apps (no client secret needed) — the
  likely first target. Apple Music (MusicKit JS/native) and SoundCloud have very
  different auth models; treat each as its own task, not a shared abstraction
  guessed at up front.
- **What "linking" produces.** Two very different features hide under one phrase:
  1. *Track ID enrichment* — after a transition is detected, identify the two
     tracks (fingerprint match or metadata search) and attach names/artists/links to
     the report. Additive to the existing local-file model; no import needed.
  2. *Playlist/tracklist export* — push a recovered tracklist back to a Spotify
     playlist, or import a mix's source playlist for comparison. This is the actual
     "account linking" ask and implies write scopes, not just read/search.
  Task 3.1 below forces this choice explicitly rather than building toward both at once.
- **Where the token lives.** A desktop app holding a refresh token needs OS keychain
  storage (Tauri has a keychain plugin), not a plaintext file — this is a real
  security surface that base.md's current architecture has never had to consider.
- **Whether a server is actually needed.** PKCE + loopback redirect (`http://localhost:PORT/callback`)
  avoids a real backend for auth itself, but decide this explicitly (Task 3.1) rather
  than defaulting to "we need a server" because the word "account" implies one.

## Task list

- **3.1** — Decide provider(s), auth grant type, and which of the two "linking"
  features (enrichment vs. export) is actually being built first.
- **3.2** — Design token storage (OS keychain via Tauri) and scope minimization
  (read-only search/metadata scopes unless export is in scope).
- **3.3** — Prototype the OAuth flow against the single provider chosen in 3.1,
  outside the main app, before wiring it into anything.
- **3.4** — Extend the `<mixname>.analysis.json` schema (base.md §5.1) with an
  optional per-transition block for matched streaming metadata — additive, so
  existing local-only consumers of the schema don't break.
- **3.5** — Wire the matched metadata into the existing Tauri frontend
  (`ui/src/types.ts`'s `AnalysisReport` contract) as an optional rendered field.
- **3.6** — Privacy/security pass: token revocation path, what happens offline/without
  a linked account (must degrade to today's fully-local behavior, not require login).
- **3.7** — Re-evaluate: does fingerprint/metadata match accuracy across real mixes
  justify shipping this, or does it produce enough wrong matches to undermine the
  "only report what a DJ can verify by ear in five seconds" principle (base.md §1)?

## Notes / Risks

- This directly touches base.md's scope section — if this phase proceeds, base.md's
  "Out (explicitly, for now)" list needs an explicit edit (removing "any account"),
  not silent drift.
- Fingerprinting/metadata matching for a *blended, beatmatched* transition (two
  tracks playing simultaneously) is a much harder identification problem than
  matching a single clean track — don't assume off-the-shelf fingerprinting (e.g.
  Shazam-style) works during an active overlap the way it does on a clean track.
- Task 3.7 is a second, separate kill gate — do not let this phase ship on the
  strength of "the OAuth flow works" alone; match *accuracy* is the actual bar.

# Synthetic mix validation (Tasks 0.5–0.10 stand-in)

**Scope caveat, upfront:** everything below runs on *synthetic* audio
(`scripts/synth_mixes.py`), generated instead of sourcing real recorded mixes to avoid
copyright/ToS exposure (decision recorded 2026-08-01). This is not the real Task 0.5/0.6
deliverable (real recorded mixes, hand-labelled by ear) and does **not** satisfy Task
1.2–1.4 (the real 20-mix ground truth set) — those still require real audio. Treat
everything here as "does the pipeline run and roughly behave as expected," not as a
substitute for the real kill gate. Do **not** tune Task 2.15's thresholds against this
set as if it were the real gate — synthesized drum patterns are periodic in a way real
music isn't, and overfitting to that periodicity would not generalize.

## Method

Four mixes generated via `python scripts/synth_mixes.py` into `data/synthetic-mixes/`
(gitignored, regenerable, not committed):

| Mix | Genre(s) | Blend style | Duration | Transitions |
|---|---|---|---|---|
| `01-techno-long-blend` | techno | long-blend (24, 16 bars) | 147.7s | 2 |
| `02-house-short-blend` | house | short-blend (8, 12 bars) | 147.1s | 2 |
| `03-hard-cut-set` | industrial/breakbeat/house (alternating) | hard-cut (0 bars) | 169.4s | 3 |
| `04-homogeneous-minimal-techno` | minimal techno (near-identical across "tracks") | long-blend (16, 16 bars) | 150.0s | 2 |

Each track is synthesized 16th-note drum pattern (kick/hat/snare) + optional chord
stab/bass, not pure tones — real percussive transients for madmom's beat/downbeat
tracker to lock onto. Ground truth (`start_s`/`end_s`/`center_s`/`phrase_offset_bars_truth`)
is derived analytically from the construction, not estimated — exact by definition.

Run via the existing eval harness: `python -m analyzer.cli --eval data/synthetic-mixes/labels_synthetic.json`.

## Headline result: hard cuts work, blends don't

| Subset | Recall | Precision | Phrase exact |
|---|---|---|---|
| Hard-cut mix only (`03`) | **1.00** (3/3) | **1.00** (3/3) | 0.33 (1/3) |
| Blend mixes only (`01`, `02`, `04` combined) | **0.17** (1/6) | **0.07** (1/15) | 0.00 |
| All four mixes | 0.44 (4/9) | 0.22 (4/18) | 0.25 |

This is exactly the failure mode base.md's Core Problem section (§3) predicts:
*"Standard novelty detection expects a sharp boundary and finds nothing"* for a blend.
Both detectors (novelty + changepoint) agree tightly and confidently (0.98–1.0) on every
hard-cut transition. On blends, candidates are frequent (15 candidates for 6 true
blend transitions) but don't reliably land within ±2s of the labelled centre — see the
per-mix detail below.

## Per-mix detail

```
01-techno-long-blend    label centers: 36.92, 103.39   candidates: 9.29, 54.33, 94.04, 130.03
02-house-short-blend    label centers: 54.19, 96.77    candidates: 0.23, 22.52, 46.21, 81.04, 107.74, 145.82
03-hard-cut-set         label centers: 42.35, 84.71, 127.06   candidates: 41.80, 84.52, 126.66  (all matched)
04-homogeneous-minimal  label centers: 45.00, 105.00   candidates: 28.79, 60.37, 84.52, 104.95, 125.85
```

Some blend candidates land close to the labelled *edges* rather than the *centre* (e.g.
mix 02's `46.21` is 0.24s from that transition's `start_s` of 46.45; mix 04's `104.95` is
0.05s from that transition's true centre, `60.37` is 0.37s from that transition's `end_s`).
The pattern isn't perfectly clean across all candidates — there are also unexplained
extras — but it's consistent with Foote novelty/changepoint reacting to the fade-in/
fade-out edges of a blend (where the "other" track's texture enters/exits the local
similarity window) rather than to the steady-state middle of an overlap, which is
locally self-similar once both tracks have been present for a while.

## Task 0.9 — homogeneous worst case

Mix `04` (minimal techno, near-identical pattern across all three "tracks") did **not**
score categorically worse than the higher-contrast techno/house blends — all three blend
mixes cluster in the same poor range. This is inconclusive on Known Risk 1 specifically:
blend-centre localization is already unreliable even with strong timbral contrast present
(distinct kick pitch, chord stabs in house), so this synthetic evidence can't yet isolate
whether genre homogeneity is an *additional* penalty on top of that, or just along for
the ride. Real audio is needed to actually test Known Risk 1 in isolation.

## Task 0.10 — overlap-feasibility decision

**Provisional decision, synthetic-evidence-informed: not yet.** `config.OVERLAP_ESTIMATION_ENABLED`
should stay `False` (its current default). Recovering an overlap *span* is a strictly
harder problem than localizing the transition *point* first, and point localization on
blends is currently unreliable (17% recall) — attempting span recovery on top of an
unreliable point estimate would compound error, not fix it. This isn't a final call (that
needs real mixes per Task 0.10's own text), but it's no longer a guess — there's now a
concrete reason not to flip the flag yet.

## Secondary finding: phrase-offset ±1 bar sensitivity near boundaries

On the hard-cut mix, all three transitions were detected within ~0.5s of truth
(effectively perfect), yet phrase-exact-match was only 1/3 — the other two computed
`phrase_offset_bars` one bar higher than truth (25 vs. 24). Root cause looks like grid
drift, not a `score/phrase.py` bug (already unit-tested against constructed grids):
madmom's tracked bar length (1.7600s) vs. the exact synthetic bar length (60/136*4 =
1.7647s) drifts by ~0.3–0.4s by the third transition (~72 bars in), which is enough to
flip a bar-index computation when the detected time sits close to a bar boundary. Worth
watching once real audio is in play — real-world downbeat tracking will drift more than
a synthesized click-tight drum pattern does.

## Recommended next step (not implemented here — needs a design decision)

`merge.py`'s collapse window is a fixed `MERGE_COLLAPSE_BARS = 8`. For a long blend, the
two "edge" candidates a detector produces can legitimately be more than 8 bars apart
(e.g. a 24-bar blend), so they survive as two separate, off-target candidates instead of
collapsing into one well-placed one. Two options worth weighing, neither implemented
here since both are real design tradeoffs (Task 0.10/2.15 territory, not a quick patch):

1. Make the merge/collapse window scale with a plausible overlap span instead of a fixed
   bar count, so wide-apart edges of one blend can still reunite into a single candidate.
2. Change `eval.py`'s matching semantics for non-hard-cut transitions to check whether a
   candidate falls anywhere inside the labelled `[start_s, end_s]` span, not only within
   ±2s of the single `center_s` point.

Either changes real behavior and deserves validation against real mixes, not further
synthetic tuning — flagging it here so it's not lost, not fixing it speculatively now.

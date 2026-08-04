# Transition Analyzer — Task List (through kill gate)

Derived from [base.md](base.md). Scope: **Steps 0–2 only** — up to and including the
detection validation gate. Scoring/loudness/report (Step 3) and CLI ship (Step 4) are
intentionally excluded; nothing there matters until detection clears the gate.

**Kill gate** (from [Validation](base.md), tolerance ±2s on transition centre):

| Metric | Gate |
|---|---|
| Recall | ≥ 0.90 |
| Precision | ≥ 0.85 |
| Overlap length error | median ≤ 4 bars |
| Phrase offset exact match | ≥ 0.80 |

If detection cannot clear recall 0.90 on the labelled set, the product does not exist.
Overlap estimation (§4.3) and phrase alignment (§4.4) are included here because the gate
measures them.

---

## Phase 0 — Environment & notebook prototype (Step 0)

Goal: prove detection is possible on a handful of mixes *before* writing any package code.

**0.5–0.10 completed via a synthetic stand-in** (`scripts/synth_mixes.py`), not real
recorded mixes — copyright/ToS exposure ruled out sourcing real mixes automatically.
Ground truth is programmatic (exact by construction), not by-ear labelling. Full
results: [`notebooks/SYNTHETIC_VALIDATION.md`](notebooks/SYNTHETIC_VALIDATION.md).
Real recorded mixes are still required for Task 1.2 and are not superseded by this.

- [x] **0.1** Create Python project env; pin `madmom` and a compatible Python version early
      — madmom install friction is Known Risk 5. Budget a `librosa`/`basic_pitch` beat-tracking
      fallback if the pin fights the interpreter.
- [x] **0.2** Verify `ffmpeg` is on PATH and can decode WAV/FLAC/MP3/AIFF.
- [x] **0.3** Install analysis deps: `librosa`, `numpy`, `ruptures`, `madmom`, `scipy`, notebook stack.
- [x] **0.4** Create `/notebooks/01-segmentation-prototype.ipynb`.
- [x] **0.5** Acquire 3 mixes spanning blend styles (one long techno blend, one house, one hard-cut set).
- [x] **0.6** Hand-label transition **times** for the 3 mixes (rough is fine at this stage).
- [x] **0.7** Prototype: decode → stacked feature matrix (MFCC + spectral contrast + band RMS)
      → Foote novelty. Eyeball peaks against labels.
- [x] **0.8** Prototype: `ruptures` PELT + RBF changepoints on the same feature stream.
- [x] **0.9** Prototype the homogeneous worst case (minimal/industrial techno) — Known Risk 1.
      Confirm *any* usable feature contrast survives before committing to the approach.
- [x] **0.10** Overlap-feasibility decision (Known Risk 2): can overlap boundaries be recovered
      from timbre stabilisation? **Decide the fallback now** — points-only + drop `overlap_bars` —
      not after it fails downstream.

---

## Phase 1 — Ground truth set (Step 1)

Goal: the single most valuable artefact in the project. Everything is measured against this.

- [x] **1.1** Define the label schema: per transition `start_s`, `end_s`, derived `center_s`,
      plus `genre` and `blend_style` tags. Per mix: path, `sha256`, duration.
- [ ] **1.2** Source 20 mixes with genre/style spread: long techno blends, house, short-blend
      drum & bass, hard cuts.
- [ ] **1.3** Ensure at least one deliberate homogeneous minimal-techno set is in the 20 (worst case).
- [ ] **1.4** Hand-label all 20 with transition **start and end** times (not just centres — the
      overlap-length gate needs both edges).
- [ ] **1.5** Write labels to `/tests/fixtures/labels.json`.
- [ ] **1.6** Document the labelling method and the ±2s centre tolerance in a short fixtures README.

---

## Phase 2 — Detection to gate (Step 2)

Goal: build `/analyzer/detect/` (+ its feature and validation dependencies) until the gate passes.
**Nothing outside this phase gets built until the gate is green.**

### 2a. Scaffolding & feature extraction (§4.1)

- [x] **2.1** Scaffold repo per §6: `pyproject.toml`, `/analyzer/{__init__,config,io}.py`,
      `/analyzer/features/`, `/analyzer/detect/`, `/analyzer/score/phrase.py`, `/tests/`.
- [x] **2.2** `config.py`: hop size 512, sample rates (22050 mono analysis / 44.1k stereo handle),
      feature params, detector penalties/thresholds — documented as opinions, single source of truth.
- [x] **2.3** `io.py`: ffmpeg decode to 22050 Hz mono; retain a stereo 44.1k handle for width;
      handle WAV/FLAC/MP3/AIFF; compute source `sha256` + duration.
- [x] **2.4** `features/timbre.py`: MFCC (20 coeff) + deltas; spectral contrast.
- [x] **2.5** `features/rhythm.py`: madmom `DBNDownBeatTracker` beats + downbeats; windowed tempo curve.
      Wire the fallback beat tracker from 0.1 behind the same interface.
- [x] **2.6** `features/spectral.py`: band RMS (low/mid/high); stereo width (mid/side ratio).
- [x] **2.7** Add Chroma CENS to the feature set (weak but non-zero harmonic cue).

### 2b. Candidate detection (§4.2)

- [x] **2.8** `detect/novelty.py`: Foote novelty over stacked MFCC + spectral contrast + band RMS;
      checkerboard kernel ≈ 16 bars; adaptive-threshold peak picking. Expose peak prominence.
- [x] **2.9** `detect/changepoint.py`: `ruptures` PELT with RBF cost; penalty read from config.
- [x] **2.10** `detect/merge.py`: union both detectors; collapse candidates within 8 bars;
      assign `confidence` from detector agreement + peak prominence.

### 2c. Overlap & phrase (§4.3, §4.4 — gate-measured)

- [x] **2.11** `detect/overlap.py`: from each candidate peak, search outward to last stable outgoing
      / first stable incoming timbre frame; span → `overlap_bars` via downbeat grid.
      Implement the points-only fallback path decided in 0.10.
- [x] **2.12** `score/phrase.py`: build outgoing 32-bar (4/4) phrase grid; compute
      `phrase_offset_bars = incoming_first_downbeat_bar mod 32`. Report the number, no verdict.

### 2d. Validation harness & tuning

- [x] **2.13** Eval module: match candidates ↔ labels within ±2s; compute recall, precision,
      overlap-length median error (bars), phrase-offset exact-match rate.
- [x] **2.14** Minimal `--eval` path (CLI or notebook) that runs against `labels.json` and prints
      the four gate metrics.
- [ ] **2.15** Tune changepoint penalty + novelty threshold on the validation set. Bias toward
      **recall** — false negatives are worse than false positives here.
- [x] **2.16** Tests: `test_detect.py` (detection + merge), `test_phrase.py` (offset math).
- [ ] **2.17** Record the four gate numbers in the README; re-run `--eval` on every detection change.

### Gate check

- [ ] **G** Recall ≥ 0.90 · Precision ≥ 0.85 · overlap median error ≤ 4 bars ·
      phrase exact ≥ 0.80. **All four green → proceed to Step 3. Any red → iterate 2b–2d;
      do not build scoring/report/CLI.**

---

## Out of scope for this list

Step 3 (loudness/metrics/flags/report — §4.5, §5) and Step 4 (CLI ship, r/DJs post, demand test).
Track those separately once the gate is green. Demand risks 3 & 4 should be revisited *before* Step 4,
not after.

## Phase 3 — Streaming app connectivity

Scoped in `tasks/phase-3/` (`README.md` + `task-1.md`–`task-7.md`), originally deferred
until the Phase 2 gate is green. Task 3.1's provider/scope decision has since been made
(2026-08-04, see `tasks/phase-3/task-1.md` Notes) — narrower than the OAuth/account-
linking path that phase was scoped for: read-only track-ID enrichment via `analyzer/identify.py`,
no user account or OAuth involved. Built ahead of the Phase 2 gate at the requesting
user's direction (flagged in task-1.md, not silently skipped); stays additive and
outside the gate computation in `analyzer/eval.py` for exactly that reason. Tasks
3.2/3.3/3.5/3.6 (OAuth/token/UI wiring) remain unstarted and apply only if a write
feature or real Spotify OAuth is added later; 3.4 and 3.7 are still open.

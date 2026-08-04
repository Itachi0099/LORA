x# Transition Analyzer

Post-set transition analysis for DJ mixes. One recorded mix in, one report out.

**Status:** spec, pre-code
**Kill gate:** segmentation accuracy on hand-labelled mixes (see [Validation](#validation))

---

## 1. Scope

### In

- Input: a single recorded mix file (WAV, FLAC, MP3, AIFF), 20 to 180 minutes
- Detect where each track change happens
- Score each transition on objectively measurable properties
- Emit JSON plus a terminal summary

### Out (explicitly, for now)

- Library management, tagging, crates
- Key detection, energy scores, mood labels
- Two-track "will these mix" comparison
- Any upload, server, or account, **except:** short (~12s) clips around a detected
  transition may be sent to a third-party fingerprinting service (AudD) for read-only
  track identification, opt-in via `AUDD_API_TOKEN` — no user account, OAuth, or
  streaming-service login involved. See `tasks/phase-3/task-1.md` for the decision
  record and `analyzer/identify.py`. Playlist export/import and full account linking
  remain out of scope.
- GUI

Nothing ships until a CLI run on a real mix produces a transition list that survives listening back.

---

## 2. Why this and not the rest

Every adjacent product does prep. Lexicon does library conversion, tags, smart playlists, cue generation, beatgrid fixing across all six major DJ apps, with a free tier. Mixed In Key owns key. Rekordbox owns prep-to-CDJ.

Nobody analyses the recorded output. A DJ finishes a set, knows something dragged, and has no tool that says where. That is the gap.

The constraint that keeps this honest: only report things a DJ can verify by ear within five seconds of clicking. No score they cannot check is allowed in the output.

---

## 3. Core problem

A DJ mix is a continuous audio stream with no metadata about its constituent tracks. The analyzer must recover structure that was never recorded.

Three things make this harder than generic music segmentation:

1. **Transitions are regions, not points.** A blend can run 8 to 64 bars. Both tracks are present and beat-aligned throughout. Standard novelty detection expects a sharp boundary and finds nothing.
2. **Beatmatching removes the tempo cue.** Two tracks at the same BPM, phase-locked, look like one track to a tempo-based segmenter.
3. **Genre homogeneity removes the timbre cue.** A two-hour industrial techno set is 130 minutes of kick, hat, and noise. Chroma is near useless. MFCC deltas are small.

The signal that does survive: during an overlap, spectral density and stereo width rise, harmonic content becomes more complex, and the low end is usually EQ'd such that band energy ratios shift in a characteristic way. Detection should target the overlap region itself, not the boundary.

---

## 4. Approach

### 4.1 Feature extraction

Decode to 22050 Hz mono via ffmpeg for analysis, keep a stereo 44.1k handle for loudness and width. Hop size 512.

| Feature | Library | Purpose |
|---|---|---|
| MFCC (20 coeff) + deltas | librosa | timbre change |
| Chroma CENS | librosa | harmonic change, weak but non-zero |
| Spectral contrast | librosa | density during overlap |
| Band RMS (low/mid/high) | librosa | EQ moves, kick swap detection |
| Stereo width (mid/side ratio) | numpy | widens during blend |
| Beats + downbeats | madmom `DBNDownBeatTracker` | bar grid, phrase alignment |
| Windowed tempo | librosa / madmom | drift, tempo change points |

### 4.2 Candidate detection

Two independent detectors, unioned, then merged:

**A. Novelty on self-similarity.** Foote novelty over a stacked MFCC + spectral contrast + band RMS feature matrix, checkerboard kernel sized to roughly 16 bars. Peak picking with adaptive threshold. Catches hard cuts and short blends.

**B. Change point detection on the feature stream.** `ruptures` with PELT and an RBF cost, penalty tuned on the validation set. Catches slow drifts that novelty smooths over.

Merge rule: candidates within 8 bars of each other collapse to one. Each surviving candidate gets a confidence from how many detectors fired and their peak prominence.

### 4.3 Overlap boundary estimation

For each candidate, search outward from the peak to find where the timbre feature vector stabilises on each side. The overlap region is the span between the last stable outgoing frame and the first stable incoming frame. Convert to bars using the downbeat grid.

This is the part most likely to fail. If overlap boundaries are unreliable, fall back to reporting transition points with confidence only, and drop `overlap_bars` from the output rather than shipping a number that is wrong.

### 4.4 Phrase alignment

Using the madmom downbeat grid, establish the outgoing track's phrase grid (assume 4/4, 32-bar phrases, which holds for nearly all four-to-the-floor dance music). Compute where the incoming track's first downbeat lands relative to that grid.

```
phrase_offset_bars = incoming_first_downbeat_bar mod 32
```

0 is on-phrase. 16 is a half-phrase offset, common and often intentional. Anything else is usually a mistake. Report the number, not a verdict.

### 4.5 Per-transition scoring

Every metric below is objective. No model, no learned score.

| Metric | Definition |
|---|---|
| `overlap_bars` | length of the blend in bars |
| `phrase_offset_bars` | 0 to 31, incoming downbeat vs outgoing 32-bar grid |
| `peak_dbtp` | true peak during overlap, dBTP |
| `clipped_samples` | count of samples at or above 0 dBFS during overlap |
| `lufs_delta` | short-term LUFS at overlap centre minus mix median |
| `low_band_sum_db` | low band energy during overlap vs mean of the two tracks, flags un-EQ'd bass stacking |
| `dead_air_ms` | longest sub-threshold gap inside the overlap |
| `abruptness` | novelty peak prominence, normalised 0 to 1 |
| `confidence` | detector agreement, 0 to 1 |

No composite "transition quality" score. Composites hide which metric fired and are the exact kind of unverifiable number this product exists to avoid.

---

## 5. Output

### 5.1 JSON schema

Written to `<mixname>.analysis.json`.

```json
{
  "schema_version": 1,
  "source": {
    "path": "/Users/saurav/mixes/warehouse-2026-07.wav",
    "duration_s": 4382.6,
    "sample_rate": 44100,
    "sha256": "…"
  },
  "mix": {
    "integrated_lufs": -8.2,
    "true_peak_dbtp": 0.4,
    "clipped_samples": 1832,
    "tempo_median_bpm": 138.0,
    "tempo_drift_bpm": 2.1
  },
  "transitions": [
    {
      "index": 1,
      "at_s": 412.8,
      "at_bar": 178,
      "overlap_bars": 32,
      "phrase_offset_bars": 0,
      "peak_dbtp": -0.9,
      "clipped_samples": 0,
      "lufs_delta": 1.4,
      "low_band_sum_db": 4.8,
      "dead_air_ms": 0,
      "abruptness": 0.22,
      "confidence": 0.91,
      "flags": ["bass_stacking"]
    }
  ],
  "warnings": [
    "tempo grid unstable between 1820s and 1960s, transitions in this range are low confidence"
  ]
}
```

### 5.2 Terminal summary

```
warehouse-2026-07.wav   73:02   138 BPM median   -8.2 LUFS

12 transitions detected

  #   TIME     BARS  PHRASE  ISSUE
  1   06:52      32      +0  -
  2   12:18       8     +11  off-phrase
  3   19:40      16      +0  bass stacking (+4.8 dB low)
  4   24:05       0      -   hard cut
  ...
  9   51:33      24      +0  clipping (312 samples, +0.4 dBTP)

3 flagged. Run with --json for full metrics.
```

### 5.3 Flag vocabulary

Fixed set, each tied to one threshold on one metric:

- `off_phrase` — `phrase_offset_bars` not in {0, 16}
- `bass_stacking` — `low_band_sum_db` > 3.0
- `clipping` — `clipped_samples` > 0
- `dead_air` — `dead_air_ms` > 400
- `hard_cut` — `overlap_bars` == 0 and `abruptness` > 0.7
- `level_jump` — `abs(lufs_delta)` > 3.0

Thresholds live in one config module and are documented as opinions, not facts.

---

## 6. Repo structure

```
/dj-transition-analyzer
  pyproject.toml
  README.md
  /analyzer
    __init__.py
    cli.py                  entrypoint, argparse
    config.py               thresholds, feature params
    io.py                   ffmpeg decode, format handling
    /features
      __init__.py
      timbre.py             MFCC, spectral contrast
      rhythm.py             madmom beats + downbeats, tempo curve
      spectral.py           band RMS, stereo width
    /detect
      __init__.py
      novelty.py            Foote self-similarity novelty
      changepoint.py        ruptures PELT
      merge.py              candidate union, confidence
      overlap.py            overlap boundary estimation
    /score
      __init__.py
      phrase.py             phrase offset
      loudness.py           ffmpeg ebur128, true peak, clipping
      metrics.py            per-transition metric assembly
      flags.py              threshold application
    report.py               JSON schema + terminal renderer
  /tests
    /fixtures
      labels.json           hand-labelled ground truth
    test_detect.py
    test_phrase.py
    test_metrics.py
  /notebooks
    01-segmentation-prototype.ipynb
```

CLI:

```bash
djx analyze mix.wav
djx analyze mix.wav --json out.json --min-confidence 0.5
djx analyze mix.wav --labels tests/fixtures/labels.json --eval
```

---

## 7. Build order

**Step 0. Notebook prototype.** `/notebooks/01-segmentation-prototype.ipynb`. Three mixes, hand-labelled transition times. Get detection working before writing a package. Do not skip this into the repo structure above.

**Step 1. Ground truth set.** 20 mixes, hand-labelled with transition start and end times. Mix of genres and blend styles: long techno blends, house, short-blend drum and bass, hard cuts. This is the single most valuable artefact in the project and the only way to know if anything works.

**Step 2. Detection to gate.** Build `/analyzer/detect/` until validation metrics pass. Nothing else until then.

**Step 3. Scoring and report.** Loudness and phrase metrics are the easy part, roughly two days once detection is solid.

**Step 4. Ship the CLI.** Post to r/Beatmatch and r/DJs. Measure whether anyone runs it twice.

Only after step 4 does the Tauri UI question become worth asking.

---

## Validation

Run against `/tests/fixtures/labels.json`, tolerance ±2 seconds on transition centre.

| Metric | Gate |
|---|---|
| Recall | ≥ 0.90 |
| Precision | ≥ 0.85 |
| Overlap length error | median ≤ 4 bars |
| Phrase offset exact match | ≥ 0.80 |

If detection cannot clear recall 0.90 on the labelled set, the product does not exist. False negatives are worse than false positives here: a missed transition means the tool silently fails at its only job, whereas a spurious one costs the DJ five seconds of listening.

Re-run `--eval` on every change to detection. Track the numbers in the README.

---

## Known risks

1. **Homogeneous sets defeat timbre detection.** A long minimal techno set may have no usable feature contrast. Test this case early, it is the worst case and also a very common one.
2. **Overlap boundaries may be unrecoverable.** Fallback is transition points only. Decide the fallback before building, not after it fails.
3. **Nobody records their sets.** Bedroom DJs frequently do not. This kills demand regardless of how well the analysis works. Ask before step 4, not after.
4. **Pioneer ships it.** Rekordbox already stores performance history. Post-set analytics is an obvious extension. Argues for shipping narrow and fast.
5. **madmom install friction.** It has historically been painful to install on newer Python versions. Pin versions early or budget time for a `basic_pitch` / `librosa` beat tracking fallback.
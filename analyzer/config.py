"""Thresholds and feature parameters. Single source of truth (base.md §4.5).

Every value here is a documented opinion, not a derived fact — see base.md §5.3.
"""

# --- Sample rates & framing (base.md §4.1) ---------------------------------

SR_ANALYSIS = 22050
"""Mono decode rate used for all detection features."""

SR_STEREO = 44100
"""Stereo decode rate, kept for loudness/width — not resampled to SR_ANALYSIS."""

HOP_LENGTH = 512
"""Frame hop at SR_ANALYSIS. Opinion: matches librosa/madmom defaults."""

HOP_LENGTH_STEREO = HOP_LENGTH * (SR_STEREO // SR_ANALYSIS)
"""Frame hop at SR_STEREO, scaled so stereo-derived frames (e.g. stereo width)
land on the same frame grid as SR_ANALYSIS features without resampling."""

# --- Timbre features (base.md §4.1) ----------------------------------------

N_MFCC = 20
"""MFCC coefficient count. Opinion: base.md §4.1 spec'd value."""

BAND_SPLITS_HZ = ((20, 200), (200, 2000), (2000, 8000))
"""Low/mid/high band edges for band-RMS (EQ move / kick-swap detection). Opinion."""

# --- Candidate detection (base.md §4.2) -------------------------------------

NOVELTY_KERNEL_BARS = 16
"""Foote checkerboard kernel size, in bars. Opinion: base.md §4.2-A."""

NOVELTY_PEAK_MIN_DISTANCE_S = 20.0
"""Minimum spacing between novelty peaks, to avoid double-counting one blend as two hits."""

NOVELTY_FRAME_AGGREGATION = 10
"""Mean-pool this many raw (HOP_LENGTH) frames together before running Foote novelty.
Opinion: keeps the O(n * kernel_radius^2) novelty computation tractable on full-length
(20-180 min) mixes — raw hop-512 framing alone would make the local similarity window
too expensive to compute per frame on a multi-hour mix."""

CHANGEPOINT_PENALTY = 10.0
"""ruptures PELT penalty. Opinion — tuned against labels.json in Phase 2 task 2.15."""

MERGE_COLLAPSE_BARS = 8
"""Candidates within this many bars of each other collapse to one (base.md §4.2)."""

OVERLAP_ESTIMATION_ENABLED = False
"""Task 0.10 (overlap-feasibility decision) is still blocked — it requires validating
timbre-stabilisation search against real, hand-labelled mixes, which don't exist in
this repo yet (tasks/phase-0/task-10.md). Until that decision is actually made with
real data, default to the documented fallback: omit `overlap_bars` from output rather
than ship an unverified number (base.md §4.3). Flip this on only after 0.10 is resolved."""

# --- Phrase alignment (base.md §4.4) ----------------------------------------

PHRASE_LENGTH_BARS = 32
"""Assumed phrase length, 4/4. Holds for nearly all four-to-the-floor dance music."""

# --- Validation gate (base.md §Validation) ----------------------------------

EVAL_CENTER_TOLERANCE_S = 2.0
GATE_RECALL_MIN = 0.90
GATE_PRECISION_MIN = 0.85
GATE_OVERLAP_MEDIAN_ERROR_BARS_MAX = 4.0
GATE_PHRASE_EXACT_MATCH_MIN = 0.80

# --- Flag thresholds (base.md §5.3) -----------------------------------------
# Step 3 (scoring/flags) is out of scope for Phase 2, but the thresholds are fixed here
# now so there is exactly one place they will ever need to change.

FLAG_BASS_STACKING_DB = 3.0
FLAG_DEAD_AIR_MS = 400
FLAG_LEVEL_JUMP_LUFS = 3.0
FLAG_HARD_CUT_ABRUPTNESS_MIN = 0.7

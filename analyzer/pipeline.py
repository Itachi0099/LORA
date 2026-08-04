"""End-to-end glue: decode -> features -> detect -> merge -> overlap/phrase (Task 2.14).

Not part of the §6 module list (`report.py` is Step 3's job) — this is the minimal
glue needed to run `--eval`, kept separate from `cli.py` so both the CLI and any
future eval script can call it directly.
"""

from __future__ import annotations

import subprocess
import warnings
from pathlib import Path

from analyzer import config, io
from analyzer.detect import changepoint, merge, novelty, overlap
from analyzer.features import build_feature_matrix
from analyzer.features.rhythm import track_downbeats
from analyzer.score import phrase


def analyze_mix(path: Path):
    """Run the full detection pipeline on one mix. Returns `(candidates, downbeat_grid)`.

    Each candidate dict always has `at_s`, `confidence`, `phrase_offset_bars`;
    `overlap_bars` (+ span) only if `config.OVERLAP_ESTIMATION_ENABLED` (Task 0.10
    fallback otherwise). The grid is returned too since eval.py needs it to convert
    ground-truth `start_s`/`end_s` into comparable bar counts.
    """
    y_mono = io.decode_mono(path)
    try:
        y_stereo = io.decode_stereo(path)
    except subprocess.CalledProcessError as e:
        warnings.warn(
            f"stereo decode failed for {path} ({e}); continuing mono-only, "
            "stereo-width feature will be dropped from the feature matrix."
        )
        y_stereo = None

    features = build_feature_matrix(y_mono, y_stereo)
    base_hop_s = config.HOP_LENGTH / config.SR_ANALYSIS

    grid = track_downbeats(path)

    novelty_candidates = novelty.detect(features, grid, base_hop_s)
    changepoint_candidates = changepoint.detect(features, base_hop_s)
    merged = merge.merge(novelty_candidates + changepoint_candidates, grid)
    merged.sort(key=lambda c: c.time_s)

    results = []
    for i, cand in enumerate(merged):
        entry = overlap.attach_overlap(cand, features, base_hop_s, grid)

        segment_start_s = merged[i - 1].time_s if i > 0 else 0.0
        upcoming_downbeats = grid.downbeat_times_s[grid.downbeat_times_s >= cand.time_s]
        incoming_first_downbeat_s = float(upcoming_downbeats[0]) if len(upcoming_downbeats) else cand.time_s
        entry["phrase_offset_bars"] = phrase.phrase_offset_bars(grid, segment_start_s, incoming_first_downbeat_s)

        results.append(entry)

    return results, grid

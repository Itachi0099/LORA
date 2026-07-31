"""Overlap boundary estimation (base.md §4.3, Task 2.11).

Task 0.10 (overlap-feasibility decision) is still blocked on real, hand-labelled mixes
(tasks/phase-0/task-10.md) — nobody has verified whether timbre-stabilisation search
actually recovers usable overlap boundaries yet. The estimation mechanism below is
implemented so it's ready the moment 0.10 is resolved, but `attach_overlap` defaults to
the points-only fallback (`config.OVERLAP_ESTIMATION_ENABLED = False`) per base.md §4.3:
"drop overlap_bars from the output rather than shipping a number that is wrong."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from analyzer import config
from analyzer.detect.merge import MergedCandidate
from analyzer.features.rhythm import DownbeatGrid


@dataclass
class OverlapEstimate:
    start_s: float
    end_s: float
    overlap_bars: float


def _frame_is_stable(features: np.ndarray, frame: int, window: int, threshold: float) -> bool:
    """Heuristic: local feature variance below `threshold` means this frame belongs
    to one steady-state track rather than an active blend."""
    lo = max(0, frame - window)
    hi = min(features.shape[1], frame + window)
    if hi - lo < 2:
        return False
    local = features[:, lo:hi]
    return float(np.mean(np.var(local, axis=1))) < threshold


def _search_outward(
    features: np.ndarray, peak_frame: int, direction: int, window: int, threshold: float, max_steps: int
) -> int:
    """Walk from `peak_frame` in `direction` (+1 or -1) for the first stable frame."""
    frame = peak_frame
    n = features.shape[1]
    for _ in range(max_steps):
        if not (0 <= frame < n):
            break
        if _frame_is_stable(features, frame, window, threshold):
            return frame
        frame += direction
    return max(0, min(frame, n - 1))


def estimate_overlap(
    features: np.ndarray,
    peak_frame: int,
    frame_hop_s: float,
    downbeat_grid: DownbeatGrid,
    stability_window_frames: int = 5,
    variance_threshold: Optional[float] = None,
    max_search_bars: float = 32.0,
) -> OverlapEstimate:
    """Search outward from a candidate's peak frame for where the timbre feature
    vector stabilises on each side. The overlap region is the span between the last
    stable outgoing frame and the first stable incoming frame (base.md §4.3).
    """
    if variance_threshold is None:
        variance_threshold = float(np.median(np.var(features, axis=1))) * 0.5

    max_steps = int(max_search_bars * downbeat_grid.median_bar_length_s / frame_hop_s)

    start_frame = _search_outward(features, peak_frame, -1, stability_window_frames, variance_threshold, max_steps)
    end_frame = _search_outward(features, peak_frame, +1, stability_window_frames, variance_threshold, max_steps)

    start_s = start_frame * frame_hop_s
    end_s = end_frame * frame_hop_s
    return OverlapEstimate(start_s=start_s, end_s=end_s, overlap_bars=downbeat_grid.bars_between(start_s, end_s))


def attach_overlap(
    candidate: MergedCandidate,
    features: np.ndarray,
    frame_hop_s: float,
    downbeat_grid: DownbeatGrid,
) -> dict:
    """Points-only by default — see module docstring. Only attaches `overlap_bars`
    (plus the estimated span) once `config.OVERLAP_ESTIMATION_ENABLED` is flipped on
    after Task 0.10 is actually resolved with real data.
    """
    result = {"at_s": candidate.time_s, "confidence": candidate.confidence}
    if not config.OVERLAP_ESTIMATION_ENABLED:
        return result

    peak_frame = int(round(candidate.time_s / frame_hop_s))
    estimate = estimate_overlap(features, peak_frame, frame_hop_s, downbeat_grid)
    result["overlap_bars"] = estimate.overlap_bars
    result["overlap_start_s"] = estimate.start_s
    result["overlap_end_s"] = estimate.end_s
    return result

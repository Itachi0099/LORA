"""ruptures PELT + RBF changepoint detection (base.md §4.2-B, Task 2.9). Independent
of novelty.py — catches slow drifts novelty's local windowing smooths over."""

from __future__ import annotations

import numpy as np
import ruptures as rpt

from analyzer import config
from analyzer.detect import Candidate
from analyzer.detect.novelty import aggregate_frames


def detect_changepoints(features: np.ndarray, penalty: float = config.CHANGEPOINT_PENALTY) -> list:
    """Raw breakpoint frame indices (in `features`' own frame grid)."""
    algo = rpt.Pelt(model="rbf").fit(features.T)
    breakpoints = algo.predict(pen=penalty)
    # ruptures includes len(features) as a trailing "breakpoint" by convention — drop it.
    return [b for b in breakpoints if b < features.shape[1]]


def _jump_magnitude(features: np.ndarray, frame: int, window: int) -> float:
    """Feature-mean shift across `frame`, as a stand-in for novelty's peak
    prominence — ruptures doesn't expose one natively."""
    lo = max(0, frame - window)
    hi = min(features.shape[1], frame + window)
    if frame - lo < 1 or hi - frame < 1:
        return 0.0
    before = features[:, lo:frame].mean(axis=1)
    after = features[:, frame:hi].mean(axis=1)
    return float(np.linalg.norm(after - before))


def detect(
    features: np.ndarray,
    base_frame_hop_s: float,
    frame_aggregation: int = config.NOVELTY_FRAME_AGGREGATION,
    penalty: float = config.CHANGEPOINT_PENALTY,
    jump_window_frames: int = 10,
) -> list:
    """End-to-end: aggregate frames (same scheme as novelty.py, so both detectors run
    on the same feature stream per base.md §4.2-B) -> PELT/RBF changepoints ->
    Candidate list with a jump-magnitude prominence analog.
    """
    agg_features = aggregate_frames(features, frame_aggregation)
    agg_hop_s = base_frame_hop_s * frame_aggregation

    breakpoints = detect_changepoints(agg_features, penalty)
    jumps = [_jump_magnitude(agg_features, b, jump_window_frames) for b in breakpoints]
    max_jump = max(jumps) if jumps else 1.0
    max_jump = max_jump or 1.0

    return [
        Candidate(
            frame=int(b),
            time_s=float(b * agg_hop_s),
            prominence=float(j / max_jump),
            source="changepoint",
        )
        for b, j in zip(breakpoints, jumps)
    ]

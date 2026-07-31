"""Union candidates, collapse duplicates, assign confidence (base.md §4.2, Task 2.10)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from analyzer import config
from analyzer.detect import Candidate
from analyzer.features.rhythm import DownbeatGrid


@dataclass
class MergedCandidate:
    """One surviving transition candidate after union + collapse."""

    time_s: float
    confidence: float
    sources: list = field(default_factory=list)
    """Which detector(s) contributed: subset of {"novelty", "changepoint"}."""
    prominence: float = 0.0
    """Max prominence among the candidates collapsed into this one."""


def merge(
    candidates: list,
    downbeat_grid: DownbeatGrid,
    collapse_bars: float = config.MERGE_COLLAPSE_BARS,
) -> list:
    """Union novelty + changepoint candidates (already-sorted or not); collapse
    candidates within `collapse_bars` bars of each other into one. Confidence comes
    from detector agreement (both detectors firing counts for more than one) plus
    peak prominence (base.md §4.2)."""
    if not candidates:
        return []

    collapse_window_s = collapse_bars * downbeat_grid.median_bar_length_s
    ordered = sorted(candidates, key=lambda c: c.time_s)

    groups = [[ordered[0]]]
    for cand in ordered[1:]:
        if cand.time_s - groups[-1][-1].time_s <= collapse_window_s:
            groups[-1].append(cand)
        else:
            groups.append([cand])

    merged = []
    for group in groups:
        sources = sorted({c.source for c in group})
        avg_time = float(np.mean([c.time_s for c in group]))
        max_prom = float(max(c.prominence for c in group))
        agreement = len(sources) / 2.0  # 0.5 if one detector fired, 1.0 if both agree
        confidence = float(np.clip(0.5 * agreement + 0.5 * max_prom, 0.0, 1.0))
        merged.append(
            MergedCandidate(time_s=avg_time, confidence=confidence, sources=sources, prominence=max_prom)
        )

    return merged

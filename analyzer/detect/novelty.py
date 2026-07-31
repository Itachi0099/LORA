"""Foote self-similarity novelty (base.md §4.2-A, Task 2.8)."""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks

from analyzer import config
from analyzer.detect import Candidate
from analyzer.features.rhythm import DownbeatGrid


def aggregate_frames(features: np.ndarray, factor: int) -> np.ndarray:
    """Mean-pool every `factor` frames together. Keeps Foote novelty's local-window
    cost tractable on full-length (20-180 min) mixes — see
    config.NOVELTY_FRAME_AGGREGATION."""
    if factor <= 1:
        return features
    n = features.shape[1]
    usable = n - (n % factor)
    trimmed = features[:, :usable]
    return trimmed.reshape(trimmed.shape[0], -1, factor).mean(axis=2)


def checkerboard_kernel(radius: int) -> np.ndarray:
    if radius < 1:
        raise ValueError("kernel radius must be >= 1")
    axis = np.arange(-radius, radius)
    gaussian = np.exp(-0.5 * (axis / (radius / 2)) ** 2)
    kernel = np.outer(gaussian, gaussian)
    sign = np.sign(np.outer(axis, axis))
    sign[sign == 0] = 1.0
    return kernel * sign


def foote_novelty(features: np.ndarray, kernel_radius: int) -> np.ndarray:
    """Self-similarity novelty curve. Each frame's value comes from a local window
    around it (not the full N x N similarity matrix), so cost stays O(n * radius^2)
    instead of O(n^2) — required to run on multi-hour mixes at all.
    """
    n = features.shape[1]
    kernel_radius = min(kernel_radius, max(n // 2 - 1, 1))
    kernel = checkerboard_kernel(kernel_radius)

    norms = np.linalg.norm(features, axis=0) + 1e-8
    normed = features / norms

    novelty = np.zeros(n)
    for i in range(n):
        lo = max(0, i - kernel_radius)
        hi = min(n, i + kernel_radius)
        window = normed[:, lo:hi]
        sim_block = window.T @ window
        k_lo = kernel_radius - (i - lo)
        k_hi = kernel_radius + (hi - i)
        novelty[i] = np.sum(sim_block * kernel[k_lo:k_hi, k_lo:k_hi])

    novelty -= novelty.min()
    peak = novelty.max()
    if peak > 0:
        novelty /= peak
    return novelty


def frames_per_bar(downbeat_grid: DownbeatGrid, frame_hop_s: float) -> float:
    """`downbeat_grid`'s median bar length expressed in frames at `frame_hop_s`."""
    return downbeat_grid.median_bar_length_s / frame_hop_s


def pick_peaks(
    novelty: np.ndarray,
    frame_hop_s: float,
    min_distance_s: float = config.NOVELTY_PEAK_MIN_DISTANCE_S,
) -> list:
    """Adaptive-threshold peak picking (base.md §4.2-A), with prominence exposed for
    merge.py's confidence calculation (Task 2.10)."""
    distance = max(1, int(round(min_distance_s / frame_hop_s)))
    threshold = novelty.mean() + 0.5 * novelty.std()
    peaks, props = find_peaks(novelty, height=threshold, distance=distance, prominence=0)
    return [
        Candidate(frame=int(p), time_s=float(p * frame_hop_s), prominence=float(prom), source="novelty")
        for p, prom in zip(peaks, props["prominences"])
    ]


def detect(
    features: np.ndarray,
    downbeat_grid: DownbeatGrid,
    base_frame_hop_s: float,
    frame_aggregation: int = config.NOVELTY_FRAME_AGGREGATION,
    kernel_bars: float = config.NOVELTY_KERNEL_BARS,
) -> list:
    """End-to-end: aggregate frames -> checkerboard novelty -> peak-pick. Kernel size
    is converted from bars to (aggregated) frames via the downbeat grid, per base.md §4.2-A.
    """
    agg_features = aggregate_frames(features, frame_aggregation)
    agg_hop_s = base_frame_hop_s * frame_aggregation

    fpb = frames_per_bar(downbeat_grid, agg_hop_s)
    kernel_radius = max(1, int(round(kernel_bars * fpb / 2)))

    novelty = foote_novelty(agg_features, kernel_radius)
    return pick_peaks(novelty, agg_hop_s)

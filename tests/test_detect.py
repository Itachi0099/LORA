"""Tests for detect/novelty.py, detect/changepoint.py, detect/merge.py (Task 2.16)."""

import numpy as np
import pytest

from analyzer.detect import Candidate, changepoint, merge, novelty
from analyzer.features.rhythm import DownbeatGrid


def _synthetic_two_segment_features(d=10, n=1000, shift=5.0, seed=0):
    rng = np.random.default_rng(seed)
    a = rng.normal(loc=0.0, scale=1.0, size=(d, n // 2))
    b = rng.normal(loc=shift, scale=1.0, size=(d, n // 2))
    return np.hstack([a, b])


def _grid(bar_length_s=2.0, duration_s=60.0):
    downbeats = np.arange(0, duration_s, bar_length_s)
    beats = np.arange(0, duration_s, bar_length_s / 4)
    return DownbeatGrid(beat_times_s=beats, downbeat_times_s=downbeats, beats_per_bar=4)


class TestNovelty:
    def test_checkerboard_kernel_is_quadrant_signed(self):
        kernel = novelty.checkerboard_kernel(4)
        assert kernel.shape == (8, 8)
        assert kernel[0, 0] > 0
        assert kernel[-1, -1] > 0
        assert kernel[0, -1] < 0
        assert kernel[-1, 0] < 0

    def test_checkerboard_kernel_rejects_invalid_radius(self):
        with pytest.raises(ValueError):
            novelty.checkerboard_kernel(0)

    def test_foote_novelty_peaks_near_segment_boundary(self):
        features = _synthetic_two_segment_features()
        curve = novelty.foote_novelty(features, kernel_radius=20)
        assert curve.shape == (features.shape[1],)
        peak_frame = int(np.argmax(curve))
        assert abs(peak_frame - features.shape[1] // 2) <= 5

    def test_pick_peaks_returns_candidates_with_prominence(self):
        features = _synthetic_two_segment_features()
        curve = novelty.foote_novelty(features, kernel_radius=20)
        peaks = novelty.pick_peaks(curve, frame_hop_s=0.1, min_distance_s=1.0)
        assert len(peaks) >= 1
        assert all(isinstance(p, Candidate) for p in peaks)
        assert all(p.source == "novelty" for p in peaks)
        assert all(p.prominence >= 0 for p in peaks)

    def test_aggregate_frames_reduces_length_by_factor(self):
        features = np.arange(40).reshape(2, 20).astype(float)
        agg = novelty.aggregate_frames(features, factor=4)
        assert agg.shape == (2, 5)

    def test_aggregate_frames_noop_for_factor_one(self):
        features = _synthetic_two_segment_features(n=100)
        agg = novelty.aggregate_frames(features, factor=1)
        assert agg.shape == features.shape


class TestChangepoint:
    def test_detects_the_synthetic_shift(self):
        features = _synthetic_two_segment_features(n=800)
        candidates = changepoint.detect(features, base_frame_hop_s=0.1, penalty=3.0)
        assert len(candidates) >= 1
        mid_s = (features.shape[1] * 0.1) / 2
        assert any(abs(c.time_s - mid_s) < 5.0 for c in candidates)
        assert all(c.source == "changepoint" for c in candidates)


class TestMerge:
    def test_collapses_candidates_within_window(self):
        grid = _grid(bar_length_s=2.0)  # 8-bar collapse window default = 16s
        cands = [
            Candidate(frame=0, time_s=10.0, prominence=0.5, source="novelty"),
            Candidate(frame=0, time_s=12.0, prominence=0.8, source="changepoint"),
        ]
        merged = merge.merge(cands, grid)
        assert len(merged) == 1
        assert set(merged[0].sources) == {"novelty", "changepoint"}
        assert merged[0].prominence == 0.8

    def test_keeps_candidates_outside_window_separate(self):
        grid = _grid(bar_length_s=2.0)  # collapse window = 8 * 2s = 16s
        cands = [
            Candidate(frame=0, time_s=10.0, prominence=0.5, source="novelty"),
            Candidate(frame=0, time_s=200.0, prominence=0.5, source="novelty"),
        ]
        merged = merge.merge(cands, grid)
        assert len(merged) == 2

    def test_confidence_higher_with_detector_agreement(self):
        grid = _grid(bar_length_s=2.0)
        agree = merge.merge(
            [
                Candidate(frame=0, time_s=10.0, prominence=0.5, source="novelty"),
                Candidate(frame=0, time_s=10.5, prominence=0.5, source="changepoint"),
            ],
            grid,
        )[0]
        disagree = merge.merge(
            [Candidate(frame=0, time_s=10.0, prominence=0.5, source="novelty")], grid
        )[0]
        assert agree.confidence > disagree.confidence

    def test_empty_input_returns_empty_list(self):
        assert merge.merge([], _grid()) == []

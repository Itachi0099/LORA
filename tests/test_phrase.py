"""Tests for score/phrase.py phrase-offset math (Task 2.16)."""

import numpy as np

from analyzer.features.rhythm import DownbeatGrid
from analyzer.score import phrase


def _grid(bar_length_s=2.0, n_bars=40):
    downbeats = np.arange(0, n_bars * bar_length_s, bar_length_s)
    return DownbeatGrid(beat_times_s=downbeats, downbeat_times_s=downbeats, beats_per_bar=4)


def test_zero_offset_on_phrase_boundary():
    grid = _grid(bar_length_s=2.0)
    offset = phrase.phrase_offset_bars(grid, segment_start_s=0.0, incoming_first_downbeat_s=32 * 2.0)
    assert offset == 0


def test_half_phrase_offset():
    grid = _grid(bar_length_s=2.0)
    offset = phrase.phrase_offset_bars(grid, segment_start_s=0.0, incoming_first_downbeat_s=16 * 2.0)
    assert offset == 16


def test_offset_wraps_around_32():
    grid = _grid(bar_length_s=2.0)
    offset = phrase.phrase_offset_bars(grid, segment_start_s=0.0, incoming_first_downbeat_s=33 * 2.0)
    assert offset == 1


def test_offset_relative_to_nonzero_segment_start():
    grid = _grid(bar_length_s=2.0)
    # outgoing track's own phrase started at bar 10; incoming downbeat at bar 26 -> 16 bars in
    offset = phrase.phrase_offset_bars(grid, segment_start_s=10 * 2.0, incoming_first_downbeat_s=26 * 2.0)
    assert offset == 16


def test_offset_never_negative_when_incoming_precedes_start():
    grid = _grid(bar_length_s=2.0)
    # pathological ordering guard: mod arithmetic should still land in [0, 32)
    offset = phrase.phrase_offset_bars(grid, segment_start_s=20 * 2.0, incoming_first_downbeat_s=18 * 2.0)
    assert 0 <= offset < 32


def test_custom_phrase_length():
    grid = _grid(bar_length_s=2.0)
    offset = phrase.phrase_offset_bars(
        grid, segment_start_s=0.0, incoming_first_downbeat_s=20 * 2.0, phrase_length_bars=16
    )
    assert offset == 4

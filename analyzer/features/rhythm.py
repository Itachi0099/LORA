"""Beats, downbeats, tempo curve (base.md §4.1, §4.4, Task 2.5).

madmom's `DBNDownBeatTrackingProcessor` is the primary tracker (pinned per Task 0.1 —
see notebooks/ENVIRONMENT.md for the exact version/interpreter pins that make it
importable). A librosa-only fallback is wired behind the same `track_downbeats`
interface per the Task 0.1 decision, so a future madmom breakage is a one-file fix
rather than a ripple through `overlap.py` / `score/phrase.py` callers.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from analyzer import config


@dataclass
class DownbeatGrid:
    beat_times_s: np.ndarray
    """All tracked beat times, seconds."""
    downbeat_times_s: np.ndarray
    """Subset of beat_times_s that are bar-starts (downbeats)."""
    beats_per_bar: int
    """Time signature numerator used for tracking (4 for nearly all four-to-the-floor
    dance music, per base.md §4.4)."""

    @property
    def median_bar_length_s(self) -> float:
        """Median inter-downbeat interval. Documented default of 2.0s (120 BPM, 4/4)
        when there are fewer than two downbeats to measure from (beat tracking failed
        or the mix is too short), rather than raising mid-pipeline."""
        if len(self.downbeat_times_s) < 2:
            return 2.0
        return float(np.median(np.diff(self.downbeat_times_s)))

    def bar_index_at(self, time_s: float) -> int:
        """0-indexed bar number containing `time_s`."""
        if len(self.downbeat_times_s) == 0:
            return 0
        idx = int(np.searchsorted(self.downbeat_times_s, time_s, side="right")) - 1
        return max(idx, 0)

    def bars_between(self, start_s: float, end_s: float) -> float:
        """Span between two times, in bars, via the downbeat grid (base.md §4.3)."""
        return self.bar_index_at(end_s) - self.bar_index_at(start_s)


def track_downbeats(
    path: Path, beats_per_bar: Sequence[int] = (3, 4)
) -> DownbeatGrid:
    """Beats + downbeats for `path`. madmom decodes the file itself (its pretrained
    model expects its own internal sample rate/framing) — this does not reuse
    `io.decode_mono`.
    """
    try:
        return _track_downbeats_madmom(path, beats_per_bar)
    except ImportError:
        warnings.warn(
            "madmom unavailable; falling back to librosa.beat (beats only — no true "
            "downbeat detection, so bar-start times are an assumed every-4th-beat "
            "approximation). See notebooks/ENVIRONMENT.md fallback decision (Task 0.1)."
        )
        return _track_downbeats_librosa_fallback(path)


def _track_downbeats_madmom(path: Path, beats_per_bar: Sequence[int]) -> DownbeatGrid:
    from madmom.features.downbeats import DBNDownBeatTrackingProcessor, RNNDownBeatProcessor

    activations = RNNDownBeatProcessor()(str(path))
    proc = DBNDownBeatTrackingProcessor(beats_per_bar=list(beats_per_bar), fps=100)
    result = proc(activations)  # (n, 2): [time_s, beat_position_in_bar (1-indexed)]

    if len(result) == 0:
        return DownbeatGrid(np.zeros(0), np.zeros(0), beats_per_bar=4)

    beat_times = result[:, 0]
    downbeat_mask = result[:, 1] == 1
    downbeat_times = beat_times[downbeat_mask]
    return DownbeatGrid(
        beat_times_s=beat_times,
        downbeat_times_s=downbeat_times,
        beats_per_bar=int(result[:, 1].max()),
    )


def _track_downbeats_librosa_fallback(path: Path, sr: int = config.SR_ANALYSIS) -> DownbeatGrid:
    import librosa

    y, sr = librosa.load(str(path), sr=sr, mono=True)
    _, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=config.HOP_LENGTH)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=config.HOP_LENGTH)
    # No true downbeat model available in the fallback path — assume 4/4 and every
    # 4th tracked beat is a bar-start starting from the first. Documented
    # approximation (base.md §4.4 assumes 4/4 anyway), not a claim of equal accuracy
    # to the madmom path.
    downbeat_times = beat_times[::4]
    return DownbeatGrid(beat_times_s=beat_times, downbeat_times_s=downbeat_times, beats_per_bar=4)


def tempo_curve(
    path: Path, sr: int = config.SR_ANALYSIS, window_s: float = 30.0, hop_s: float = 15.0
) -> tuple[np.ndarray, np.ndarray]:
    """Windowed tempo estimate (BPM) over time — surfaces drift/tempo changepoints
    (base.md §4.1) that a single mix-wide tempo estimate would smooth over."""
    import librosa

    y, sr = librosa.load(str(path), sr=sr, mono=True)
    window = int(window_s * sr)
    hop = int(hop_s * sr)

    times, bpms = [], []
    for start in range(0, max(len(y) - window, 0) + 1, hop):
        chunk = y[start : start + window]
        if len(chunk) < sr:
            continue
        tempo = librosa.feature.tempo(y=chunk, sr=sr, hop_length=config.HOP_LENGTH)[0]
        times.append(start / sr + window_s / 2)
        bpms.append(float(tempo))
    return np.array(times), np.array(bpms)

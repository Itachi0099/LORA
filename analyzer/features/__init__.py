"""Feature extraction. `build_feature_matrix` is the shared assembly point consumed by
both `detect/novelty.py` and `detect/changepoint.py` (Task 2.7)."""

from __future__ import annotations

from typing import Optional

import numpy as np

from analyzer import config
from analyzer.features import spectral, timbre


def build_feature_matrix(
    y_mono: np.ndarray,
    y_stereo: Optional[np.ndarray] = None,
    sr: int = config.SR_ANALYSIS,
) -> np.ndarray:
    """Stack MFCC(20)+deltas, spectral contrast, chroma CENS, band RMS, and (if a
    stereo handle is given) stereo width. Frame-aligned by trimming to the shortest
    stream, then z-scored per row. This is the feature matrix both candidate
    detectors (novelty, changepoint) run on.
    """
    streams = [
        timbre.mfcc_with_deltas(y_mono, sr),
        timbre.spectral_contrast(y_mono, sr),
        timbre.chroma_cens(y_mono, sr),
        spectral.band_rms(y_mono, sr),
    ]
    if y_stereo is not None:
        streams.append(spectral.stereo_width(y_stereo).reshape(1, -1))

    n = min(s.shape[-1] for s in streams)
    stacked = np.vstack([s[..., :n] for s in streams])

    mean = stacked.mean(axis=1, keepdims=True)
    std = stacked.std(axis=1, keepdims=True) + 1e-8
    return (stacked - mean) / std

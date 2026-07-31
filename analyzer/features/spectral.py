"""Band RMS + stereo width (base.md §4.1, Task 2.6). The two cues most likely to
survive when timbre contrast collapses on homogeneous material (Known Risk 1)."""

from __future__ import annotations

import librosa
import numpy as np

from analyzer import config


def band_rms(
    y: np.ndarray,
    sr: int = config.SR_ANALYSIS,
    bands=config.BAND_SPLITS_HZ,
    hop_length: int = config.HOP_LENGTH,
) -> np.ndarray:
    """(n_bands, n_frames) RMS energy per band — EQ moves, kick-swap detection."""
    S = np.abs(librosa.stft(y, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=(S.shape[0] - 1) * 2)
    out = []
    for lo, hi in bands:
        mask = (freqs >= lo) & (freqs < hi)
        out.append(np.sqrt(np.mean(S[mask, :] ** 2, axis=0) + 1e-12))
    return np.vstack(out)


def stereo_width(
    y_stereo: np.ndarray, hop_length: int = config.HOP_LENGTH_STEREO
) -> np.ndarray:
    """Mid/side RMS ratio per frame from a (2, n_samples) stereo signal, framed at
    `HOP_LENGTH_STEREO` so frames land on the same grid as SR_ANALYSIS features
    without resampling (config.py). Widens during a blend (base.md §3)."""
    left, right = y_stereo[0], y_stereo[1]
    mid = (left + right) / 2
    side = (left - right) / 2

    n_frames = 1 + (len(mid) - hop_length) // hop_length
    if n_frames < 1:
        return np.zeros(0)

    mid_frames = librosa.util.frame(mid, frame_length=hop_length, hop_length=hop_length)
    side_frames = librosa.util.frame(side, frame_length=hop_length, hop_length=hop_length)

    mid_rms = np.sqrt(np.mean(mid_frames ** 2, axis=0) + 1e-12)
    side_rms = np.sqrt(np.mean(side_frames ** 2, axis=0) + 1e-12)
    return side_rms / (mid_rms + 1e-12)

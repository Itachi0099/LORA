"""MFCC + deltas, spectral contrast, chroma CENS (base.md §4.1, Tasks 2.4/2.7)."""

from __future__ import annotations

import librosa
import numpy as np

from analyzer import config


def mfcc_with_deltas(
    y: np.ndarray, sr: int = config.SR_ANALYSIS, hop_length: int = config.HOP_LENGTH
) -> np.ndarray:
    """(2 * N_MFCC, n_frames): MFCC stacked with its delta — the primary timbre cue."""
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=config.N_MFCC, hop_length=hop_length)
    delta = librosa.feature.delta(mfcc)
    return np.vstack([mfcc, delta])


def spectral_contrast(
    y: np.ndarray, sr: int = config.SR_ANALYSIS, hop_length: int = config.HOP_LENGTH
) -> np.ndarray:
    """Spectral density cue — rises during overlap (base.md §3)."""
    return librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop_length)


def chroma_cens(
    y: np.ndarray, sr: int = config.SR_ANALYSIS, hop_length: int = config.HOP_LENGTH
) -> np.ndarray:
    """Harmonic-change cue. Weak but non-zero (base.md §4.1) — near useless on
    genre-homogeneous material (base.md §3), included as an additive signal only."""
    return librosa.feature.chroma_cens(y=y, sr=sr, hop_length=hop_length)

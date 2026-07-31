"""ffmpeg decode + source identity. Reuses the exact decode paths verified in Task 0.2
(see notebooks/ENVIRONMENT.md) rather than re-deriving them via a Python audio backend.
"""

import hashlib
import subprocess
from pathlib import Path

import numpy as np

from analyzer import config

SUPPORTED_EXTENSIONS = {".wav", ".flac", ".mp3", ".aiff", ".aif"}


class UnsupportedFormatError(ValueError):
    pass


def _check_supported(path: Path) -> None:
    ext = Path(path).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFormatError(
            f"unsupported input format {ext!r}; expected one of {sorted(SUPPORTED_EXTENSIONS)}"
        )


def _ffmpeg_decode(path: Path, sr: int, channels: int) -> np.ndarray:
    cmd = [
        "ffmpeg", "-v", "error", "-i", str(path),
        "-f", "f32le", "-acodec", "pcm_f32le",
        "-ac", str(channels), "-ar", str(sr), "-",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    audio = np.frombuffer(proc.stdout, dtype=np.float32)
    if channels > 1:
        audio = audio.reshape(-1, channels).T
    return audio


def decode_mono(path: Path, sr: int = config.SR_ANALYSIS) -> np.ndarray:
    """Decode to mono float32 at `sr` Hz — the analysis path (base.md §4.1)."""
    _check_supported(path)
    return _ffmpeg_decode(path, sr, channels=1)


def decode_stereo(path: Path, sr: int = config.SR_STEREO) -> np.ndarray:
    """Decode to stereo float32 (2, n_samples) at `sr` Hz, unresampled — the
    loudness/width path (base.md §4.1)."""
    _check_supported(path)
    return _ffmpeg_decode(path, sr, channels=2)


def sha256_of(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def probe_duration_s(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]
    out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return float(out.stdout.strip())


def source_metadata(path: Path) -> dict:
    """path/sha256/duration_s — the same fields a labels.json entry carries (Task 1.1),
    so a mix and its label entry can be cross-checked."""
    _check_supported(path)
    return {
        "path": str(path),
        "sha256": sha256_of(path),
        "duration_s": probe_duration_s(path),
    }

"""Synthetic DJ mix generator for Phase 0/1 prototyping without copyright exposure.

Real recorded mixes (Tasks 0.5, 1.2) still need to be sourced separately — nothing
here satisfies "recorded mix" in the literal sense base.md means, and genre/timbre
here is deliberately simple synthesis, not real production. What this *does* give:
audio with genuine rhythmic transients (so madmom's beat/downbeat tracker has real
onsets to lock onto, unlike a bare sine tone), known-exact transition boundaries and
phrase offsets (since the timeline is constructed, not heard), and zero licensing risk.

Each mix is built from a sequence of synthesized "tracks" (16th-note drum pattern +
optional chord/bass) at a single constant BPM, joined with equal-power crossfades of
a controlled bar length (0 bars = hard cut). Ground truth transitions are derived
analytically from the same construction — no separate hand-labelling step, and no
approximation error to account for.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

SR = 44100


# --- Sound sources ----------------------------------------------------------

def kick(sr: int, freq_start: float = 150, freq_end: float = 50,
         duration: float = 0.18, amp: float = 0.9) -> np.ndarray:
    n = int(sr * duration)
    t = np.arange(n) / sr
    freq = np.linspace(freq_start, freq_end, n)
    phase = 2 * np.pi * np.cumsum(freq) / sr
    env = np.exp(-t / (duration / 4))
    return amp * np.sin(phase) * env


def hat(sr: int, duration: float = 0.05, amp: float = 0.35, seed: int = 0,
        harsh: bool = False) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(sr * duration)
    noise = rng.uniform(-1, 1, n)
    hp = np.diff(noise, prepend=0.0)
    if harsh:
        hp = np.diff(hp, prepend=0.0)
    t = np.arange(n) / sr
    env = np.exp(-t / (duration / 6))
    return amp * hp * env


def snare(sr: int, duration: float = 0.12, amp: float = 0.5, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(sr * duration)
    noise = rng.uniform(-1, 1, n)
    tone = 0.4 * np.sin(2 * np.pi * 180 * np.arange(n) / sr)
    t = np.arange(n) / sr
    env = np.exp(-t / (duration / 5))
    return amp * (0.7 * noise + 0.3 * tone) * env


def chord_stab(sr: int, freqs: tuple, duration: float = 0.3, amp: float = 0.25) -> np.ndarray:
    n = int(sr * duration)
    t = np.arange(n) / sr
    env = np.exp(-t / (duration / 3))
    sig = sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)
    return amp * sig * env


def bass_tone(sr: int, freq: float, duration: float, amp: float = 0.5) -> np.ndarray:
    n = int(sr * duration)
    t = np.arange(n) / sr
    sig = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t)
    env = np.ones(n)
    attack = min(int(sr * 0.005), n)
    env[:attack] = np.linspace(0, 1, attack)
    return amp * sig * env / 1.3


def _place(buf: np.ndarray, sound: np.ndarray, start_sample: int) -> None:
    if start_sample >= len(buf):
        return
    end = start_sample + len(sound)
    if end > len(buf):
        sound = sound[: len(buf) - start_sample]
        end = len(buf)
    buf[start_sample:end] += sound


# --- Genre patterns (16th-note grid, 16 steps/bar, 4/4) ---------------------

GENRE_PATTERNS = {
    "techno": dict(
        kick_steps={0, 4, 8, 12}, hat_steps={2, 6, 10, 14}, snare_steps=set(),
        chord_steps=set(), bass_steps=set(), kick_freq=(150, 50), hat_amp=0.35,
        noise_bed=0.015, chord_freqs=None, bass_freq=None, seed_bias=0, harsh_hat=False,
    ),
    "house": dict(
        kick_steps={0, 4, 8, 12}, hat_steps={2, 6, 10, 14}, snare_steps=set(),
        chord_steps={0, 8}, bass_steps={0, 8}, kick_freq=(150, 55), hat_amp=0.30,
        noise_bed=0.008, chord_freqs=(293.7, 370.0, 440.0), bass_freq=55.0,
        seed_bias=1, harsh_hat=False,
    ),
    "minimal_techno": dict(
        kick_steps={0, 4, 8, 12}, hat_steps={2, 6, 10, 14}, snare_steps=set(),
        chord_steps=set(), bass_steps=set(), kick_freq=(140, 48), hat_amp=0.35,
        noise_bed=0.02, chord_freqs=None, bass_freq=None, seed_bias=2, harsh_hat=False,
    ),
    "hardcut_industrial": dict(
        kick_steps={0, 4, 8, 12}, hat_steps={2, 6, 10, 14}, snare_steps=set(),
        chord_steps=set(), bass_steps=set(), kick_freq=(120, 35), hat_amp=0.45,
        noise_bed=0.03, chord_freqs=None, bass_freq=None, seed_bias=3, harsh_hat=True,
    ),
    "hardcut_house": dict(
        kick_steps={0, 4, 8, 12}, hat_steps={2, 6, 10, 14}, snare_steps=set(),
        chord_steps={0, 8}, bass_steps={0, 8}, kick_freq=(160, 60), hat_amp=0.30,
        noise_bed=0.01, chord_freqs=(261.6, 329.6, 392.0), bass_freq=65.4,
        seed_bias=4, harsh_hat=False,
    ),
    "hardcut_breakbeat": dict(
        kick_steps={0, 6, 10}, hat_steps={2, 4, 8, 12, 14}, snare_steps={4, 12},
        chord_steps=set(), bass_steps={0}, kick_freq=(180, 70), hat_amp=0.40,
        noise_bed=0.02, chord_freqs=None, bass_freq=41.2, seed_bias=5, harsh_hat=False,
    ),
}


def build_track(bpm: float, n_bars: int, genre: str, sr: int = SR, seed: int = 0,
                 beats_per_bar: int = 4, steps_per_beat: int = 4) -> tuple:
    """Returns (mono_track_audio, bar_len_s). Track always starts on its own bar 0."""
    pattern = GENRE_PATTERNS[genre]
    bar_len_s = 60.0 / bpm * beats_per_bar
    steps_per_bar = beats_per_bar * steps_per_beat
    total_steps = n_bars * steps_per_bar
    step_len_s = bar_len_s / steps_per_bar
    n_samples = int(n_bars * bar_len_s * sr)
    buf = np.zeros(n_samples)
    rng = np.random.default_rng(seed * 97 + pattern["seed_bias"])

    for step in range(total_steps):
        local_step = step % steps_per_bar
        start_sample = int(step * step_len_s * sr)
        if local_step in pattern["kick_steps"]:
            _place(buf, kick(sr, *pattern["kick_freq"]), start_sample)
        if local_step in pattern["hat_steps"]:
            _place(buf, hat(sr, amp=pattern["hat_amp"], seed=int(rng.integers(1 << 30)),
                             harsh=pattern["harsh_hat"]), start_sample)
        if local_step in pattern["snare_steps"]:
            _place(buf, snare(sr, seed=int(rng.integers(1 << 30))), start_sample)
        if local_step in pattern["chord_steps"] and pattern["chord_freqs"]:
            _place(buf, chord_stab(sr, pattern["chord_freqs"]), start_sample)
        if local_step in pattern["bass_steps"] and pattern["bass_freq"]:
            _place(buf, bass_tone(sr, pattern["bass_freq"], step_len_s * 1.8), start_sample)

    buf += pattern["noise_bed"] * rng.uniform(-1, 1, n_samples)
    peak = np.max(np.abs(buf)) or 1.0
    buf = buf / peak * 0.9
    return buf, bar_len_s


@dataclass
class TrackSpec:
    bpm: float
    n_bars: int
    genre: str
    overlap_bars_before: float = 0.0
    """Crossfade length with the previous track, in bars. 0 = hard cut."""
    seed: int = 0


@dataclass
class SynthMix:
    name: str
    audio: np.ndarray
    sr: int
    transitions: list = field(default_factory=list)


def build_mix(name: str, specs: list, sr: int = SR) -> SynthMix:
    tracks, bar_lens = [], []
    for i, s in enumerate(specs):
        audio, bar_len_s = build_track(s.bpm, s.n_bars, s.genre, sr=sr, seed=s.seed)
        tracks.append(audio)
        bar_lens.append(bar_len_s)

    overlap_samples = [0] + [
        int(specs[i].overlap_bars_before * bar_lens[i] * sr) for i in range(1, len(specs))
    ]

    starts = [0]
    for i in range(1, len(specs)):
        starts.append(starts[i - 1] + len(tracks[i - 1]) - overlap_samples[i])

    total_len = starts[-1] + len(tracks[-1])
    mix = np.zeros(total_len)

    transitions = []
    prev_transition_time_s = 0.0  # phrase anchor: mix start, for the first track

    for i, audio in enumerate(tracks):
        gain = np.ones(len(audio))
        if i > 0 and overlap_samples[i] > 0:
            ov = overlap_samples[i]
            gain[:ov] = np.linspace(0, 1, ov) ** 0.5
        if i < len(tracks) - 1 and overlap_samples[i + 1] > 0:
            ov_next = overlap_samples[i + 1]
            gain[-ov_next:] = np.linspace(1, 0, ov_next) ** 0.5

        s0 = starts[i]
        _place(mix, audio * gain, s0)

        if i > 0:
            ov = overlap_samples[i]
            start_s = s0 / sr
            end_s = (s0 + ov) / sr if ov > 0 else start_s
            center_s = (start_s + end_s) / 2

            bar_len_s = bar_lens[i]
            incoming_bar = round(start_s / bar_len_s)
            anchor_bar = round(prev_transition_time_s / bar_len_s)
            phrase_offset_truth = int((incoming_bar - anchor_bar) % 32)

            overlap_bars_truth = specs[i].overlap_bars_before
            blend_style = (
                "hard-cut" if overlap_bars_truth == 0
                else "long-blend" if overlap_bars_truth >= 16
                else "short-blend"
            )

            transitions.append({
                "start_s": round(start_s, 3),
                "end_s": round(end_s, 3),
                "center_s": round(center_s, 3),
                "genre": specs[i].genre,
                "blend_style": blend_style,
                "phrase_offset_bars_truth": phrase_offset_truth,
                "overlap_bars_truth": overlap_bars_truth,
            })
            prev_transition_time_s = center_s

    peak = np.max(np.abs(mix)) or 1.0
    mix = mix / peak * 0.95
    return SynthMix(name=name, audio=mix, sr=sr, transitions=transitions)


def write_wav_stereo(mix: SynthMix, out_path: Path) -> None:
    """Write as 44.1k stereo via ffmpeg (keeps the whole toolchain's decode path
    exercised the same way it will be for real mixes — no direct WAV library use)."""
    import soundfile as sf

    stereo = np.stack([mix.audio, mix.audio], axis=-1)
    tmp = out_path.with_suffix(".raw.wav")
    sf.write(tmp, stereo, mix.sr, subtype="FLOAT")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-ar", str(mix.sr), "-ac", "2", str(out_path)],
        check=True,
    )
    tmp.unlink()


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --- The actual mix definitions (Task 0.5 spread + Task 0.9 worst case) -----

MIX_SPECS = {
    "01-techno-long-blend": [
        TrackSpec(bpm=130, n_bars=32, genre="techno", seed=1),
        # 56 bars so the 24-bar fade-in + 16-bar fade-out leave 16 solo bars in the
        # middle — the two blends must not overlap each other in time.
        TrackSpec(bpm=130, n_bars=56, genre="techno", overlap_bars_before=24, seed=2),
        TrackSpec(bpm=130, n_bars=32, genre="techno", overlap_bars_before=16, seed=3),
    ],
    "02-house-short-blend": [
        TrackSpec(bpm=124, n_bars=32, genre="house", seed=11),
        TrackSpec(bpm=124, n_bars=32, genre="house", overlap_bars_before=8, seed=12),
        TrackSpec(bpm=124, n_bars=32, genre="house", overlap_bars_before=12, seed=13),
    ],
    "03-hard-cut-set": [
        TrackSpec(bpm=136, n_bars=24, genre="hardcut_industrial", seed=21),
        TrackSpec(bpm=136, n_bars=24, genre="hardcut_breakbeat", overlap_bars_before=0, seed=22),
        TrackSpec(bpm=136, n_bars=24, genre="hardcut_house", overlap_bars_before=0, seed=23),
        TrackSpec(bpm=136, n_bars=24, genre="hardcut_industrial", overlap_bars_before=0, seed=24),
    ],
    "04-homogeneous-minimal-techno": [
        TrackSpec(bpm=128, n_bars=32, genre="minimal_techno", seed=31),
        # 48 bars so the two 16-bar overlaps (in + out) leave 16 solo bars, not 0.
        TrackSpec(bpm=128, n_bars=48, genre="minimal_techno", overlap_bars_before=16, seed=32),
        TrackSpec(bpm=128, n_bars=32, genre="minimal_techno", overlap_bars_before=16, seed=33),
    ],
}

MIX_TAGS = {
    "01-techno-long-blend": {"intended_blend_style": "long-blend", "genre": "techno", "homogeneous_worst_case": False},
    "02-house-short-blend": {"intended_blend_style": "short-blend", "genre": "house", "homogeneous_worst_case": False},
    "03-hard-cut-set": {"intended_blend_style": "hard-cut", "genre": "mixed", "homogeneous_worst_case": False},
    "04-homogeneous-minimal-techno": {"intended_blend_style": "long-blend", "genre": "minimal-techno", "homogeneous_worst_case": True},
}


def generate_all(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 1, "mixes": []}

    for name, specs in MIX_SPECS.items():
        mix = build_mix(name, specs)
        wav_path = out_dir / f"{name}.wav"
        write_wav_stereo(mix, wav_path)
        duration_s = len(mix.audio) / mix.sr

        manifest["mixes"].append({
            "path": wav_path.name,
            "sha256": sha256_of(wav_path),
            "duration_s": round(duration_s, 3),
            "homogeneous_worst_case": MIX_TAGS[name]["homogeneous_worst_case"],
            "synthetic": True,
            "tags": MIX_TAGS[name],
            "transitions": mix.transitions,
        })
        print(f"{name}: {duration_s:.1f}s, {len(mix.transitions)} transitions -> {wav_path}")

    return manifest


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "data" / "synthetic-mixes"
    manifest = generate_all(out_dir)
    # Co-located with the audio (not tests/fixtures/labels.json) — this is a synthetic
    # dev fixture, not the real Task 1.5 ground truth, and analyzer.cli resolves each
    # mix's "path" relative to wherever this manifest file lives.
    manifest_path = out_dir / "labels_synthetic.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nWrote manifest: {manifest_path}")

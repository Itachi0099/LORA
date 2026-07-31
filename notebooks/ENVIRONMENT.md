# Prototype environment (Task 0.1)

## Setup

```bash
uv venv --python 3.9 .venv
source .venv/bin/activate
uv pip install "numpy==1.23.5" cython "setuptools<81" wheel
uv pip install --no-build-isolation madmom
uv pip install librosa ruptures jupyter ipykernel matplotlib basic-pitch
```

Or, once `pyproject.toml` exists at repo root: `uv sync --extra notebook`.

## Pinned versions (frozen, all import together cleanly)

| Package | Version | Why pinned |
|---|---|---|
| Python | 3.9.25 | madmom 0.16.1 uses `collections.MutableSequence`, removed from `collections` (top-level) in Python 3.10. 3.9 is the newest interpreter that still has it. |
| numpy | 1.23.5 | madmom's `io/__init__.py` uses `np.float`, a deprecated alias removed in numpy 1.24. Also madmom requires numpy<2 at build time. |
| scipy | 1.13.1 | resolved transitively, compatible with numpy 1.23.5 |
| madmom | 0.16.1 | latest PyPI release (2018); built with `--no-build-isolation` since its `setup.py` imports numpy directly at build time |
| setuptools | 80.10.2 (pinned `<81`) | madmom imports `pkg_resources` at package import time; setuptools ≥81 drops it, breaking the import |
| cython | 3.2.9 | build-only dependency for madmom's `.pyx` extensions |
| librosa | 0.11.0 | feature extraction |
| ruptures | 1.1.10 | changepoint detection |
| basic-pitch | 0.4.0 | see fallback note below |

## Known Risk 5 confirmed — madmom install friction is real

Two separate incompatibilities had to be resolved, in this order:

1. **Python 3.10+ / 3.14 (system default):** `from collections import MutableSequence` in
   `madmom/processors.py` fails — that name was removed from `collections` (not
   `collections.abc`) in Python 3.10. There is no fix short of patching madmom's source;
   pinning the interpreter to 3.9 was faster than forking the package.
2. **numpy ≥ 1.24:** `madmom/io/__init__.py` does `np.float(...)`, an alias removed in
   1.24. Pinning numpy to 1.23.5 resolves it without patching.
3. **setuptools ≥ 81:** drops the bundled `pkg_resources`, which `madmom/__init__.py`
   imports unconditionally. Pinning `setuptools<81` resolves it (emits a deprecation
   warning, not an error).

None of this is visible until you actually `import madmom` — the wheel builds fine and
only fails at import/runtime. Budget for this exact sequence rather than rediscovering it.

## Fallback beat-tracker decision

**Decision: not needed for the prototype — madmom's `DBNDownBeatTrackingProcessor`
imports and instantiates successfully** once the three pins above are applied (verified
in this env; see Task 0.1 completion notes).

`basic_pitch` was installed as the nominal fallback candidate per the task list, but on
inspection it is a note/pitch transcription model (piano-roll style), not a beat/downbeat
tracker — it has no bar-grid or downbeat concept to offer as a swap-in. If madmom ever
becomes unusable in a later environment (e.g. forced onto Python ≥3.10 by another
dependency), the practical fallback is **`librosa.beat.beat_track`**: it gives beat
positions and a tempo estimate from the same onset-strength envelope already computed for
other features, but it does not give downbeats/bar position directly — that would need to
be inferred from phase (e.g. assuming 4/4 and picking the beat-grid phase that best lines
up with the strongest periodic accent). This is a real precision loss for `phrase_offset_bars`
(§4.4 of base.md) and should only be taken if the madmom pin becomes truly unworkable.

Phase 2 task 2.5 should wire whichever tracker is active behind one interface so this
swap, if ever needed, doesn't ripple through `features/rhythm.py` callers.

## ffmpeg decode (Task 0.2)

`ffmpeg 8.1.1` (Homebrew, PATH-resolved) decodes WAV, FLAC, MP3, and AIFF without error.
Verified with synthetic 44.1 kHz stereo test tones (real mixes weren't available yet —
see Task 0.5) transcoded to each container/codec, then decoded both ways:

```bash
# Analysis path: any input -> 22050 Hz mono
ffmpeg -y -i <input> -ac 1 -ar 22050 <out>.wav

# Loudness/width path: keep the original stereo 44.1k handle untouched (no resample)
ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channels <input>
```

Both confirmed: all four formats produce a clean 22050 Hz mono stream, and the stereo
44.1k stream is retrievable unmodified alongside it. This is the exact pair of paths
`io.py` (Phase 2, task 2.3) needs to implement.

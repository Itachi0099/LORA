"""Track identification via audio fingerprinting (optional, network-dependent).

Explicitly NOT part of the detection kill gate (base.md §Validation, TASKS.md) — track
ID quality is never measured by recall/precision/overlap-error/phrase-offset and must
never feed back into those numbers or the tuned thresholds in config.py. This answers
"what songs are these," which is report enrichment; the gate only cares "where do
transitions happen."

Uses AudD (https://audd.io) because one request returns both the fingerprint match and
linked Spotify/Apple Music metadata, avoiding a second API + auth flow just to resolve
titles to streaming links. Spotify's own API has no audio-fingerprint or full-track-
download endpoint, so it cannot do the recognition step itself (see base.md's out-of-
scope list — this module fetches metadata, never audio, from any streaming service).

No `AUDD_API_TOKEN` set, or any request failure: `identify_clip` returns `None` rather
than raising. Identification is best-effort enrichment layered on top of an already-
complete detection result, never a pipeline dependency.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

AUDD_ENDPOINT = "https://api.audd.io/"
DEFAULT_CLIP_DURATION_S = 12.0
DEFAULT_TRANSITION_GAP_S = 5.0
"""How far before/after a transition's `at_s` to sample the outgoing/incoming clip —
close enough to be the actual track playing, far enough to clear the blend itself."""


@dataclass
class TrackMatch:
    title: str
    artist: str
    album: Optional[str] = None
    release_date: Optional[str] = None
    spotify_url: Optional[str] = None
    apple_music_url: Optional[str] = None


def _extract_clip_wav(path: Path, at_s: float, duration_s: float = DEFAULT_CLIP_DURATION_S) -> bytes:
    """ffmpeg-extract a short mono WAV clip centred on `at_s`. Reuses the same decode
    tool `io.py` already requires rather than adding an audio-slicing dependency."""
    start = max(0.0, at_s - duration_s / 2)
    cmd = [
        "ffmpeg", "-v", "error", "-ss", f"{start}", "-t", f"{duration_s}",
        "-i", str(path), "-f", "wav", "-ac", "1", "-ar", "44100", "-",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return proc.stdout


def _build_multipart(fields: dict, file_field: str, filename: str, file_bytes: bytes) -> tuple:
    boundary = uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body += (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n"
            f"{value}\r\n"
        ).encode("utf-8")
    body += (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
        f"filename=\"{filename}\"\r\nContent-Type: audio/wav\r\n\r\n"
    ).encode("utf-8")
    body += file_bytes
    body += f"\r\n--{boundary}--\r\n".encode("utf-8")
    content_type = f"multipart/form-data; boundary={boundary}"
    return bytes(body), content_type


def _parse_audd_result(payload: dict) -> Optional[TrackMatch]:
    result = payload.get("result")
    if not result:
        return None
    spotify = result.get("spotify") or {}
    apple = result.get("apple_music") or {}
    return TrackMatch(
        title=result.get("title") or "unknown",
        artist=result.get("artist") or "unknown",
        album=result.get("album"),
        release_date=result.get("release_date"),
        spotify_url=(spotify.get("external_urls") or {}).get("spotify"),
        apple_music_url=apple.get("url"),
    )


def identify_clip(clip_wav_bytes: bytes, api_token: Optional[str] = None, timeout_s: float = 20.0) -> Optional[TrackMatch]:
    """Send one WAV clip to AudD for recognition + Spotify/Apple Music metadata.

    Returns `None` on: no token configured, no fingerprint match, or any request
    failure (network error, timeout, malformed response). Never raises — see module
    docstring on why this must stay best-effort.
    """
    token = api_token or os.environ.get("AUDD_API_TOKEN")
    if not token:
        return None

    body, content_type = _build_multipart(
        fields={"api_token": token, "return": "spotify,apple_music"},
        file_field="file", filename="clip.wav", file_bytes=clip_wav_bytes,
    )
    req = urllib.request.Request(AUDD_ENDPOINT, data=body, headers={"Content-Type": content_type})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None

    return _parse_audd_result(payload)


def identify_transition_tracks(path: Path, at_s: float, gap_s: float = DEFAULT_TRANSITION_GAP_S) -> dict:
    """Identify the outgoing track (just before a transition's `at_s`) and the
    incoming track (just after). Returns `{"outgoing": TrackMatch | None, "incoming":
    TrackMatch | None}` — either side may be `None` per `identify_clip`'s contract.
    """
    outgoing_clip = _extract_clip_wav(path, max(0.0, at_s - gap_s))
    incoming_clip = _extract_clip_wav(path, at_s + gap_s)
    return {
        "outgoing": identify_clip(outgoing_clip),
        "incoming": identify_clip(incoming_clip),
    }

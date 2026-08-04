"""Tests for identify.py. No real network calls — urlopen is monkeypatched, keeping
this suite offline/deterministic like the rest of the project (base.md's ethos: nothing
unverifiable ships). Only the request-building and response-parsing logic is exercised.
"""

from __future__ import annotations

import json
import urllib.error

import pytest

from analyzer import identify


def test_identify_clip_returns_none_without_token(monkeypatch):
    monkeypatch.delenv("AUDD_API_TOKEN", raising=False)
    assert identify.identify_clip(b"fake-wav-bytes") is None


def test_identify_clip_returns_none_on_no_match(monkeypatch):
    def fake_urlopen(req, timeout):
        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return json.dumps({"status": "success", "result": None}).encode()

        return Resp()

    monkeypatch.setattr(identify.urllib.request, "urlopen", fake_urlopen)
    match = identify.identify_clip(b"fake-wav-bytes", api_token="test-token")
    assert match is None


def test_identify_clip_parses_spotify_metadata(monkeypatch):
    payload = {
        "status": "success",
        "result": {
            "title": "Strobe",
            "artist": "deadmau5",
            "album": "For Lack of a Better Name",
            "release_date": "2009-09-25",
            "spotify": {"external_urls": {"spotify": "https://open.spotify.com/track/abc123"}},
            "apple_music": {"url": "https://music.apple.com/track/abc123"},
        },
    }

    def fake_urlopen(req, timeout):
        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return json.dumps(payload).encode()

        return Resp()

    monkeypatch.setattr(identify.urllib.request, "urlopen", fake_urlopen)
    match = identify.identify_clip(b"fake-wav-bytes", api_token="test-token")

    assert match.title == "Strobe"
    assert match.artist == "deadmau5"
    assert match.spotify_url == "https://open.spotify.com/track/abc123"
    assert match.apple_music_url == "https://music.apple.com/track/abc123"


def test_identify_clip_returns_none_on_network_error(monkeypatch):
    def fake_urlopen(req, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(identify.urllib.request, "urlopen", fake_urlopen)
    assert identify.identify_clip(b"fake-wav-bytes", api_token="test-token") is None


def test_build_multipart_includes_token_and_filename():
    body, content_type = identify._build_multipart(
        fields={"api_token": "abc", "return": "spotify"},
        file_field="file", filename="clip.wav", file_bytes=b"RIFF....",
    )
    assert b"api_token" in body
    assert b"abc" in body
    assert b'filename="clip.wav"' in body
    assert b"RIFF...." in body
    assert content_type.startswith("multipart/form-data; boundary=")


def test_identify_transition_tracks_calls_both_sides(monkeypatch, tmp_path):
    calls = []

    def fake_extract(path, at_s, duration_s=identify.DEFAULT_CLIP_DURATION_S):
        calls.append(at_s)
        return b"clip-bytes"

    def fake_identify(clip_bytes, api_token=None, timeout_s=20.0):
        return identify.TrackMatch(title="t", artist="a")

    monkeypatch.setattr(identify, "_extract_clip_wav", fake_extract)
    monkeypatch.setattr(identify, "identify_clip", fake_identify)

    result = identify.identify_transition_tracks(tmp_path / "mix.wav", at_s=100.0, gap_s=5.0)

    assert result["outgoing"].title == "t"
    assert result["incoming"].title == "t"
    assert calls == [95.0, 105.0]

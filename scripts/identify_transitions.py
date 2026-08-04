"""Run detection + track identification on one mix and print the result.

Standalone script, not wired into `analyzer.cli`, because the full `djx analyze`
command (base.md §6 CLI, `--json`/terminal summary) is Step 4 and still out of scope —
this exists so identification can be tried against a real mix without jumping ahead of
that build order. Requires `AUDD_API_TOKEN` in the environment; without it, every
transition prints with tracks as "unidentified" rather than failing (analyzer/identify.py
is best-effort by design).

Usage:
    AUDD_API_TOKEN=... python scripts/identify_transitions.py path/to/mix.wav
"""

from __future__ import annotations

import sys
from pathlib import Path

from analyzer import identify, pipeline


def _fmt(match) -> str:
    if match is None:
        return "unidentified"
    return f"{match.artist} - {match.title}" + (f" ({match.spotify_url})" if match.spotify_url else "")


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1:
        print("usage: identify_transitions.py <mix path>", file=sys.stderr)
        return 1

    mix_path = Path(argv[0])
    candidates, _grid = pipeline.analyze_mix(mix_path)
    print(f"{len(candidates)} transitions detected in {mix_path.name}\n")

    for i, cand in enumerate(candidates, start=1):
        at_s = cand["at_s"]
        tracks = identify.identify_transition_tracks(mix_path, at_s)
        mm, ss = divmod(int(at_s), 60)
        print(f"#{i:<3} {mm:02d}:{ss:02d}  confidence={cand['confidence']:.2f}")
        print(f"      out: {_fmt(tracks['outgoing'])}")
        print(f"      in:  {_fmt(tracks['incoming'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

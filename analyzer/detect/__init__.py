"""Candidate detection (base.md §4.2): two independent detectors, unioned, then merged."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Candidate:
    """A single detected transition candidate, before merge (Task 2.10)."""

    frame: int
    """Frame index in whatever frame grid produced it (may differ in hop between
    detectors until merge.py resolves everything to seconds)."""
    time_s: float
    prominence: float
    source: str
    """Which detector produced this candidate: "novelty" or "changepoint"."""

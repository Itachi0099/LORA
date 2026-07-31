"""Gate metric computation against tests/fixtures/labels.json (base.md §Validation,
Task 2.13). This module is the referee — matching logic stays exactly spec-compliant
rather than gaining leniency that would make the gate easier to pass without the
detector actually improving.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from analyzer import config
from analyzer.features.rhythm import DownbeatGrid


@dataclass
class GateResult:
    recall: float
    precision: float
    overlap_median_error_bars: Optional[float]
    phrase_exact_match_rate: Optional[float]
    n_labels: int
    n_candidates: int
    n_matched: int
    n_overlap_skipped: int
    """Matched pairs where overlap_bars was unavailable (0.10 fallback path) —
    excluded from overlap_median_error_bars, not counted as errors."""
    n_phrase_skipped: int
    """Matched pairs where phrase_offset_bars_truth was null — excluded from
    phrase_exact_match_rate, not counted as mismatches."""

    def passes_gate(self) -> bool:
        """All four thresholds green (base.md §Validation). A metric that's `None`
        because there was nothing to measure it against (e.g. overlap estimation is
        off, or no transition had a phrase truth value) fails open — it can't be
        claimed as passing without data."""
        if self.overlap_median_error_bars is None or self.phrase_exact_match_rate is None:
            return False
        return (
            self.recall >= config.GATE_RECALL_MIN
            and self.precision >= config.GATE_PRECISION_MIN
            and self.overlap_median_error_bars <= config.GATE_OVERLAP_MEDIAN_ERROR_BARS_MAX
            and self.phrase_exact_match_rate >= config.GATE_PHRASE_EXACT_MATCH_MIN
        )


def load_labels(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def _match(label_centers: np.ndarray, candidate_times: np.ndarray, tolerance_s: float) -> dict:
    """One-to-one greedy nearest-match within ±tolerance_s. Returns {label_idx: candidate_idx}."""
    if len(label_centers) == 0 or len(candidate_times) == 0:
        return {}

    pairs = []
    for li, lt in enumerate(label_centers):
        for ci, ct in enumerate(candidate_times):
            dist = abs(lt - ct)
            if dist <= tolerance_s:
                pairs.append((dist, li, ci))
    pairs.sort(key=lambda p: p[0])

    matches, used_labels, used_candidates = {}, set(), set()
    for _, li, ci in pairs:
        if li in used_labels or ci in used_candidates:
            continue
        matches[li] = ci
        used_labels.add(li)
        used_candidates.add(ci)
    return matches


def evaluate_mix(
    label_transitions: list,
    detected_candidates: list,
    downbeat_grid: Optional[DownbeatGrid] = None,
    tolerance_s: float = config.EVAL_CENTER_TOLERANCE_S,
) -> dict:
    """Match one mix's labelled transitions against its detected candidates.

    `detected_candidates` are dicts with at least `at_s`; optionally `overlap_bars`
    and `phrase_offset_bars` (both may be absent per the Task 0.10 fallback / Task
    2.12 output). `downbeat_grid` is this mix's grid, needed to convert each label's
    `start_s`/`end_s` into a ground-truth bar count comparable to detected `overlap_bars`.
    """
    label_centers = np.array([t["center_s"] for t in label_transitions])
    cand_times = np.array([c["at_s"] for c in detected_candidates])
    matches = _match(label_centers, cand_times, tolerance_s)

    label_overlap_bars = None
    if downbeat_grid is not None:
        label_overlap_bars = [
            downbeat_grid.bars_between(t["start_s"], t["end_s"]) for t in label_transitions
        ]

    return {
        "n_labels": len(label_transitions),
        "n_candidates": len(detected_candidates),
        "matches": matches,
        "labels": label_transitions,
        "candidates": detected_candidates,
        "label_overlap_bars": label_overlap_bars,
    }


def aggregate(mix_results: list) -> GateResult:
    """Combine per-mix `evaluate_mix()` outputs into the four gate metrics."""
    total_labels = sum(r["n_labels"] for r in mix_results)
    total_candidates = sum(r["n_candidates"] for r in mix_results)
    total_matched = sum(len(r["matches"]) for r in mix_results)

    recall = total_matched / total_labels if total_labels else 0.0
    precision = total_matched / total_candidates if total_candidates else 0.0

    overlap_errors, overlap_skipped = [], 0
    phrase_matches, phrase_skipped = [], 0

    for r in mix_results:
        for li, ci in r["matches"].items():
            label = r["labels"][li]
            cand = r["candidates"][ci]

            if "overlap_bars" in cand and r["label_overlap_bars"] is not None:
                overlap_errors.append(abs(cand["overlap_bars"] - r["label_overlap_bars"][li]))
            else:
                overlap_skipped += 1

            truth = label.get("phrase_offset_bars_truth")
            if truth is not None and "phrase_offset_bars" in cand:
                phrase_matches.append(cand["phrase_offset_bars"] == truth)
            else:
                phrase_skipped += 1

    return GateResult(
        recall=recall,
        precision=precision,
        overlap_median_error_bars=float(np.median(overlap_errors)) if overlap_errors else None,
        phrase_exact_match_rate=float(np.mean(phrase_matches)) if phrase_matches else None,
        n_labels=total_labels,
        n_candidates=total_candidates,
        n_matched=total_matched,
        n_overlap_skipped=overlap_skipped,
        n_phrase_skipped=phrase_skipped,
    )

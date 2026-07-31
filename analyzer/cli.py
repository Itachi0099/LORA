"""Minimal CLI entrypoint (Task 2.14).

Only `--eval` is implemented here — the full `analyze`/`--json`/terminal-summary CLI
(base.md §5, `djx analyze mix.wav`) is Step 4, out of scope for Phase 2. This exists
so the four gate metrics are one command away, not a manual notebook run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analyzer import config
from analyzer import eval as eval_module
from analyzer import pipeline


def run_eval(labels_path: Path) -> eval_module.GateResult:
    data = eval_module.load_labels(labels_path)
    mix_results = []

    for mix in data["mixes"]:
        mix_path = Path(labels_path).parent / mix["path"]
        if not mix_path.exists():
            print(f"warning: {mix_path} not found, skipping", file=sys.stderr)
            continue
        candidates, grid = pipeline.analyze_mix(mix_path)
        mix_results.append(
            eval_module.evaluate_mix(mix["transitions"], candidates, downbeat_grid=grid)
        )

    return eval_module.aggregate(mix_results)


def _print_report(result: eval_module.GateResult) -> None:
    def fmt(value, gate_str):
        return f"{value:.3f}  ({gate_str})" if value is not None else f"n/a  ({gate_str})"

    print(f"Recall:                {fmt(result.recall, f'gate >= {config.GATE_RECALL_MIN}')}")
    print(f"Precision:              {fmt(result.precision, f'gate >= {config.GATE_PRECISION_MIN}')}")
    print(
        "Overlap median error:   "
        + fmt(result.overlap_median_error_bars, f"gate <= {config.GATE_OVERLAP_MEDIAN_ERROR_BARS_MAX} bars")
    )
    print(
        "Phrase exact match:     "
        + fmt(result.phrase_exact_match_rate, f"gate >= {config.GATE_PHRASE_EXACT_MATCH_MIN}")
    )
    print()
    print(
        f"{result.n_matched}/{result.n_labels} labelled transitions matched, "
        f"{result.n_candidates} candidates detected "
        f"({result.n_overlap_skipped} matches skipped overlap-error [no overlap_bars], "
        f"{result.n_phrase_skipped} skipped phrase-match [no ground truth])"
    )
    print()
    print("GATE: " + ("PASS" if result.passes_gate() else "FAIL"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="djx")
    parser.add_argument(
        "--eval",
        metavar="LABELS_JSON",
        type=Path,
        help="Run detection against every mix in a labels.json and print the four gate metrics.",
    )
    args = parser.parse_args(argv)

    if args.eval is not None:
        result = run_eval(args.eval)
        _print_report(result)
        return 0 if result.passes_gate() else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

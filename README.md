# DJ Transition Analyzer

Post-set transition analysis for DJ mixes. See [base.md](base.md) for the full spec and
[TASKS.md](TASKS.md) for the task breakdown through the detection kill gate.

**Status:** Phase 2 (`/analyzer/detect/`) implemented against synthetic test data.
Gate metrics below are **not yet measured** — that requires the Phase 1 ground-truth
set (`tests/fixtures/labels.json`), which needs real recorded mixes and hand-labelling
(tracked in `tasks/phase-0/` and `tasks/phase-1/`, currently blocked on sourcing audio).

## Setup

```bash
uv venv --python 3.9 .venv
source .venv/bin/activate
uv sync   # or: uv pip install -e . --extra notebook
```

See [`notebooks/ENVIRONMENT.md`](notebooks/ENVIRONMENT.md) for the exact pins and the
madmom install-friction notes (Known Risk 5).

## Running the eval harness

```bash
python -m analyzer.cli --eval tests/fixtures/labels.json
```

Prints recall, precision, overlap-length median error, and phrase-offset exact-match
rate against the labelled set, and exits non-zero if the gate isn't cleared.

## Gate status

Tolerance ±2s on transition centre (base.md §Validation). Re-run `--eval` and update
this table on every change to `analyzer/detect/`, `analyzer/features/`, or the tuned
config values (Task 2.17).

| Metric | Gate | Current | Status |
|---|---|---|---|
| Recall | ≥ 0.90 | — | not yet measured (no `labels.json` fixture) |
| Precision | ≥ 0.85 | — | not yet measured |
| Overlap length error | median ≤ 4 bars | — | not yet measured; also depends on Task 0.10 (overlap estimation currently disabled by default — see `analyzer/config.py:OVERLAP_ESTIMATION_ENABLED`) |
| Phrase offset exact match | ≥ 0.80 | — | not yet measured |

**Gate:** not evaluated — Task G is blocked until real numbers exist. Nothing in Step 3
(scoring/report) or Step 4 (CLI ship) proceeds until all four are green.

## Tests

```bash
python -m pytest tests/
```

Covers detection/merge logic (`test_detect.py`) and phrase-offset arithmetic
(`test_phrase.py`) against synthetic data — this validates the code is *correct*, not
that detection *works on real mixes*. Only the gate numbers above answer that.
# LORA

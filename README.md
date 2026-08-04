# DJ Transition Analyzer

Post-set transition analysis for DJ mixes. See [base.md](base.md) for the full spec and
[TASKS.md](TASKS.md) for the task breakdown through the detection kill gate.

**Status:** Phase 0 (`tasks/phase-0/`) and Phase 2 (`/analyzer/detect/`) done — Phase 0
via a synthetic-mix stand-in, not real recordings (see below). Gate metrics are **not
yet measured** — that requires the real Phase 1 ground-truth set
(`tests/fixtures/labels.json`), which needs real recorded mixes and hand-labelling
(tracked in `tasks/phase-1/`, currently blocked on sourcing audio; [`TASKS.md`](TASKS.md)
tracks the full checklist with checkboxes, and `tasks/phase-*/` has one file per task).

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

### Synthetic smoke test (not the gate)

To exercise the pipeline before real mixes are sourced, `scripts/synth_mixes.py`
generates synthetic audio with exact, programmatically-known ground truth (no
copyright exposure, no hand-labelling):

```bash
python scripts/synth_mixes.py   # writes data/synthetic-mixes/ (gitignored, regenerable)
python -m analyzer.cli --eval data/synthetic-mixes/labels_synthetic.json
```

Full write-up: [`notebooks/SYNTHETIC_VALIDATION.md`](notebooks/SYNTHETIC_VALIDATION.md).
Headline result — hard cuts detect near-perfectly, blends do not:

| Subset | Recall | Precision |
|---|---|---|
| Hard-cut mix only | 1.00 | 1.00 |
| Blend mixes only | 0.17 | 0.07 |

This is a smoke test, not a substitute for the real gate above — do not tune Task
2.15's thresholds against it.

## Tests

```bash
python -m pytest tests/
```

Covers detection/merge logic (`test_detect.py`) and phrase-offset arithmetic
(`test_phrase.py`) against synthetic data — this validates the code is *correct*, not
that detection *works on real mixes*. Only the gate numbers above answer that.

## Track identification (optional, not gate-scoped)

`analyzer/identify.py` fingerprints short clips around each detected transition via
[AudD](https://audd.io) and resolves matches to Spotify/Apple Music metadata (title,
artist, streaming link) — no audio is fetched from any streaming service, since none of
them expose a full-track-download endpoint; this only pulls metadata for tracks already
present in your own recorded mix. Best-effort by design: no `AUDD_API_TOKEN`, no match,
or any request failure all return `None` per-clip rather than raising, so this can never
break or slow down the core (offline, deterministic) detection pipeline.

This is report enrichment, not a detection metric — it does not and must not feed into
recall/precision/overlap-error/phrase-offset or the kill gate above.

```bash
export AUDD_API_TOKEN=...
python scripts/identify_transitions.py path/to/mix.wav
```

Standalone script for now; wiring this into `djx analyze --json` output is Step 4 work
(base.md §6), tracked in `tasks/phase-3/`.
# LORA

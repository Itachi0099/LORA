# Transition Analyzer — UI

Desktop frontend for the DJ Transition Analyzer. Renders a `<mix>.analysis.json`
report (schema in [base.md](../base.md) §5.1) as a browsable GUI: mix summary,
per-transition table with flag chips, expandable full metrics, and warnings.

## Decision: Tauri (not React Native)

The analysis engine is desktop Python (`librosa` + `madmom` + `ffmpeg`) chewing on
multi-hour audio files on a laptop. React Native is mobile-first and can't host that
stack. Tauri gives a native desktop app (Mac/Win/Linux), local filesystem access, a
Rust core that can spawn the Python analyzer as a **sidecar**, and a ~600KB bundle.

## What's built now

Just the **frontend** — a Vite + React + TypeScript app. It's the exact web layer Tauri
wraps, so it runs standalone in a browser today and needs no Rust or detection backend.
It renders a bundled `src/sample.analysis.json` on load, and you can open any real
report via the file picker.

## Run

```bash
cd ui
npm install
npm run dev        # http://localhost:1420
# or
npm run build && npm run preview
```

## Adding the Tauri shell later (once Rust is installed)

Rust/cargo are **not** installed on this machine yet — that's the only thing blocking a
real Tauri package. When ready:

```bash
# 1. install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# 2. add Tauri to this project (frontendDist already points at ui/dist via vite build)
npm install -D @tauri-apps/cli
npx tauri init            # set devUrl http://localhost:1420, frontendDist ../dist
npx tauri dev
```

Then wire the analyzer: a Tauri command shells out to `djx analyze <file> --json`,
Rust reads the emitted JSON, and the frontend renders it exactly as it renders the
sample today. The `AnalysisReport` type in `src/types.ts` is the contract between them.

## Layout

```
ui/
  index.html
  package.json
  vite.config.ts          # build.outDir = dist  → Tauri frontendDist
  tsconfig.json
  src/
    main.tsx
    App.tsx                # mix card + transitions table + detail drawer + warnings
    types.ts               # AnalysisReport schema (base.md §5.1) — the FE/BE contract
    format.ts              # time / dB / phrase formatting + flag vocabulary (§5.3)
    styles.css             # dark theme
    sample.analysis.json   # example report, rendered on first load
```

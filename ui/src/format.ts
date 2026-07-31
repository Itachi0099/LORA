import type { Flag } from "./types";

/** Seconds -> "mm:ss" or "h:mm:ss" for long mixes. */
export function fmtTime(sec: number): string {
  const s = Math.max(0, Math.round(sec));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const ss = s % 60;
  const mm = h > 0 ? String(m).padStart(2, "0") : String(m);
  const pad = (n: number) => String(n).padStart(2, "0");
  return h > 0 ? `${h}:${mm}:${pad(ss)}` : `${mm}:${pad(ss)}`;
}

/** Signed phrase offset, e.g. +0, +11. Hard cuts (overlap 0) render "—". */
export function fmtPhrase(offset: number, overlapBars: number): string {
  if (overlapBars === 0) return "—";
  const sign = offset >= 0 ? "+" : "";
  return `${sign}${offset}`;
}

export function fmtDb(v: number): string {
  const sign = v >= 0 ? "+" : "";
  return `${sign}${v.toFixed(1)}`;
}

/** Human labels + severity for the fixed flag vocabulary (base.md §5.3). */
export const FLAG_META: Record<Flag, { label: string; severity: "warn" | "bad" }> = {
  off_phrase: { label: "off-phrase", severity: "warn" },
  bass_stacking: { label: "bass stacking", severity: "warn" },
  clipping: { label: "clipping", severity: "bad" },
  dead_air: { label: "dead air", severity: "bad" },
  hard_cut: { label: "hard cut", severity: "warn" },
  level_jump: { label: "level jump", severity: "warn" },
};

/** One-line "ISSUE" cell text mirroring the terminal summary in §5.2. */
export function issueSummary(t: {
  flags: Flag[];
  low_band_sum_db: number;
  clipped_samples: number;
  peak_dbtp: number;
  overlap_bars: number;
}): string {
  if (t.flags.length === 0) return "—";
  return t.flags
    .map((f) => {
      switch (f) {
        case "bass_stacking":
          return `bass stacking (${fmtDb(t.low_band_sum_db)} dB low)`;
        case "clipping":
          return `clipping (${t.clipped_samples} samples, ${fmtDb(t.peak_dbtp)} dBTP)`;
        case "hard_cut":
          return "hard cut";
        default:
          return FLAG_META[f].label;
      }
    })
    .join(", ");
}

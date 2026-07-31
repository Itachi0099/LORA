// Mirrors the analysis JSON schema in base.md §5.1 (schema_version 1).

export type Flag =
  | "off_phrase"
  | "bass_stacking"
  | "clipping"
  | "dead_air"
  | "hard_cut"
  | "level_jump";

export interface Source {
  path: string;
  duration_s: number;
  sample_rate: number;
  sha256: string;
}

export interface MixSummary {
  integrated_lufs: number;
  true_peak_dbtp: number;
  clipped_samples: number;
  tempo_median_bpm: number;
  tempo_drift_bpm: number;
}

export interface Transition {
  index: number;
  at_s: number;
  at_bar: number;
  overlap_bars: number;
  phrase_offset_bars: number;
  peak_dbtp: number;
  clipped_samples: number;
  lufs_delta: number;
  low_band_sum_db: number;
  dead_air_ms: number;
  abruptness: number;
  confidence: number;
  flags: Flag[];
}

export interface AnalysisReport {
  schema_version: number;
  source: Source;
  mix: MixSummary;
  transitions: Transition[];
  warnings: string[];
}

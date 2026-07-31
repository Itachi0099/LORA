import { useState } from "react";
import type { AnalysisReport, Transition } from "./types";
import { fmtTime, fmtPhrase, fmtDb, issueSummary, FLAG_META } from "./format";
import sample from "./sample.analysis.json";

export function App() {
  const [report, setReport] = useState<AnalysisReport>(sample as AnalysisReport);
  const [fileName, setFileName] = useState<string>("sample.analysis.json");
  const [error, setError] = useState<string | null>(null);
  const [openRow, setOpenRow] = useState<number | null>(null);

  async function onPick(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      const parsed = JSON.parse(text) as AnalysisReport;
      if (parsed.schema_version !== 1 || !Array.isArray(parsed.transitions)) {
        throw new Error("Not a schema_version 1 analysis report.");
      }
      setReport(parsed);
      setFileName(file.name);
      setError(null);
      setOpenRow(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  const baseName = report.source.path.split("/").pop() ?? report.source.path;
  const flaggedCount = report.transitions.filter((t) => t.flags.length > 0).length;

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="logo">◈</span>
          <span>Transition Analyzer</span>
        </div>
        <label className="filebtn">
          Open .analysis.json
          <input type="file" accept=".json,application/json" onChange={onPick} hidden />
        </label>
      </header>

      {error && <div className="banner error">{error}</div>}

      <section className="mixcard">
        <div className="mixname">{baseName}</div>
        <div className="stats">
          <Stat label="Duration" value={fmtTime(report.source.duration_s)} />
          <Stat label="Tempo" value={`${report.mix.tempo_median_bpm.toFixed(0)} BPM`} sub={`±${report.mix.tempo_drift_bpm.toFixed(1)} drift`} />
          <Stat label="Loudness" value={`${report.mix.integrated_lufs.toFixed(1)} LUFS`} />
          <Stat
            label="True peak"
            value={`${fmtDb(report.mix.true_peak_dbtp)} dBTP`}
            danger={report.mix.true_peak_dbtp > 0}
          />
          <Stat
            label="Clipped"
            value={report.mix.clipped_samples.toLocaleString()}
            sub="samples"
            danger={report.mix.clipped_samples > 0}
          />
        </div>
      </section>

      <section className="summaryline">
        <strong>{report.transitions.length}</strong> transitions detected
        {flaggedCount > 0 && (
          <>
            {" · "}
            <span className="flagged">{flaggedCount} flagged</span>
          </>
        )}
      </section>

      <section className="tablewrap">
        <table className="tx">
          <thead>
            <tr>
              <th className="num">#</th>
              <th>Time</th>
              <th className="num">Bars</th>
              <th className="num">Phrase</th>
              <th>Issue</th>
              <th className="num">Conf.</th>
            </tr>
          </thead>
          <tbody>
            {report.transitions.map((t) => (
              <Row
                key={t.index}
                t={t}
                open={openRow === t.index}
                onToggle={() => setOpenRow(openRow === t.index ? null : t.index)}
              />
            ))}
          </tbody>
        </table>
      </section>

      {report.warnings.length > 0 && (
        <section className="warnings">
          <h3>Warnings</h3>
          <ul>
            {report.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </section>
      )}

      <footer className="foot">
        <span>{fileName}</span>
        <span className="mono">sha256 {report.source.sha256.slice(0, 12)}…</span>
      </footer>
    </div>
  );
}

function Stat(props: { label: string; value: string; sub?: string; danger?: boolean }) {
  return (
    <div className={`stat${props.danger ? " danger" : ""}`}>
      <div className="statval">{props.value}</div>
      <div className="statlabel">
        {props.label}
        {props.sub ? <span className="statsub"> · {props.sub}</span> : null}
      </div>
    </div>
  );
}

function Row({ t, open, onToggle }: { t: Transition; open: boolean; onToggle: () => void }) {
  const flagged = t.flags.length > 0;
  return (
    <>
      <tr className={`row${flagged ? " isflagged" : ""}${open ? " isopen" : ""}`} onClick={onToggle}>
        <td className="num idx">{t.index}</td>
        <td className="mono">{fmtTime(t.at_s)}</td>
        <td className="num">{t.overlap_bars === 0 ? "—" : t.overlap_bars}</td>
        <td className="num">{fmtPhrase(t.phrase_offset_bars, t.overlap_bars)}</td>
        <td className="issue">
          {flagged ? (
            <span className="chips">
              {t.flags.map((f) => (
                <span key={f} className={`chip ${FLAG_META[f].severity}`}>
                  {FLAG_META[f].label}
                </span>
              ))}
            </span>
          ) : (
            <span className="ok">clean</span>
          )}
        </td>
        <td className="num conf">
          <ConfBar value={t.confidence} />
        </td>
      </tr>
      {open && (
        <tr className="detailrow">
          <td colSpan={6}>
            <div className="detail">
              <Metric k="Issue summary" v={issueSummary(t)} wide />
              <Metric k="At bar" v={String(t.at_bar)} />
              <Metric k="Overlap" v={`${t.overlap_bars} bars`} />
              <Metric k="Phrase offset" v={`${t.phrase_offset_bars} / 32`} />
              <Metric k="Peak dBTP" v={fmtDb(t.peak_dbtp)} danger={t.peak_dbtp > 0} />
              <Metric k="Clipped samples" v={String(t.clipped_samples)} danger={t.clipped_samples > 0} />
              <Metric k="LUFS delta" v={fmtDb(t.lufs_delta)} danger={Math.abs(t.lufs_delta) > 3} />
              <Metric k="Low-band sum" v={`${fmtDb(t.low_band_sum_db)} dB`} danger={t.low_band_sum_db > 3} />
              <Metric k="Dead air" v={`${t.dead_air_ms} ms`} danger={t.dead_air_ms > 400} />
              <Metric k="Abruptness" v={t.abruptness.toFixed(2)} />
              <Metric k="Confidence" v={t.confidence.toFixed(2)} />
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

function Metric({ k, v, danger, wide }: { k: string; v: string; danger?: boolean; wide?: boolean }) {
  return (
    <div className={`metric${wide ? " wide" : ""}${danger ? " danger" : ""}`}>
      <span className="mk">{k}</span>
      <span className="mv mono">{v}</span>
    </div>
  );
}

function ConfBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const tone = value >= 0.85 ? "hi" : value >= 0.6 ? "mid" : "lo";
  return (
    <span className={`confbar ${tone}`} title={`${pct}%`}>
      <span className="conffill" style={{ width: `${pct}%` }} />
      <span className="conftext">{value.toFixed(2)}</span>
    </span>
  );
}

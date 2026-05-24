import React, { useMemo, useState } from 'react';

const formatNumber = (value, digits = 3) => {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return '—';
  return numeric.toFixed(digits);
};

const EvidenceBreakdownTable = ({ result }) => {
  const timeline = result?.timeline || [];
  const acousticRows = result?.feature_analysis?.acoustic_features || [];
  const [chunkIndex, setChunkIndex] = useState(0);

  const agentRows = useMemo(() => {
    const chunk = timeline[chunkIndex];
    if (!chunk?.details) return [];
    return Object.entries(chunk.details).map(([name, details]) => ({
      name,
      verdict: details.verdict || 'inconclusive',
      confidence: details.adjusted_confidence ?? details.calibrated_confidence ?? 0,
      suppression: details.suppression_factor ?? 1,
    }));
  }, [timeline, chunkIndex]);

  const hasAcoustic = acousticRows.length > 0;
  const hasAgents = agentRows.length > 0;

  if (!hasAcoustic && !hasAgents) {
    return (
      <section className="explanation-section">
        <h3 className="panel-title">Evidence Breakdown</h3>
        <p className="drawer-empty">No tabular evidence breakdown available.</p>
      </section>
    );
  }

  return (
    <section className="explanation-section">
      <h3 className="panel-title">Evidence Breakdown</h3>

      {hasAcoustic && (
        <div className="evidence-table-block">
          <h4 className="evidence-table-title">Acoustic Z-Score Signals</h4>
          <table className="evidence-table">
            <thead>
              <tr>
                <th>Signal</th>
                <th>Avg Z-Score</th>
                <th>Severity</th>
                <th>Risk</th>
              </tr>
            </thead>
            <tbody>
              {acousticRows.map((row) => (
                <tr key={row.name}>
                  <td>{row.name}</td>
                  <td>{formatNumber(row.avg_z_score)}</td>
                  <td>{row.severity || 'nominal'}</td>
                  <td>{formatNumber(row.risk_score, 2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {timeline.length > 0 && (
        <div className="evidence-table-block">
          <div className="evidence-table-header-row">
            <h4 className="evidence-table-title">Chunk Agent Details</h4>
            <select
              className="drawer-select"
              value={chunkIndex}
              onChange={(e) => setChunkIndex(Number(e.target.value))}
              aria-label="Select timeline chunk"
            >
              {timeline.map((chunk, index) => (
                <option key={index} value={index}>
                  Chunk {index} ({chunk.start_time ?? 0}s–{chunk.end_time ?? 0}s)
                </option>
              ))}
            </select>
          </div>
          {hasAgents ? (
            <table className="evidence-table">
              <thead>
                <tr>
                  <th>Agent</th>
                  <th>Verdict</th>
                  <th>Adj. Confidence</th>
                  <th>Suppression</th>
                </tr>
              </thead>
              <tbody>
                {agentRows.map((row) => (
                  <tr key={row.name}>
                    <td>{row.name}</td>
                    <td className={`vote-${row.verdict}`}>{row.verdict}</td>
                    <td>{formatNumber(row.confidence, 2)}</td>
                    <td>{formatNumber(row.suppression, 2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="drawer-caption">No per-agent details for this chunk.</p>
          )}
        </div>
      )}
    </section>
  );
};

export default EvidenceBreakdownTable;

import React, { useMemo, useState } from 'react';

const CounterfactualPanel = ({ result }) => {
  const chunks = result?.xai?.counterfactuals?.chunks || [];
  const [chunkIndex, setChunkIndex] = useState(0);

  const selectedChunk = chunks[chunkIndex] || null;
  const sensitivities = selectedChunk?.sensitivities || {};
  const agentEntries = useMemo(
    () => Object.entries(sensitivities),
    [sensitivities],
  );

  if (!chunks.length) {
    return (
      <section className="drawer-section">
        <h4 className="drawer-section-title">Analytical Sensitivity</h4>
        <p className="drawer-empty">No sensitivity gradients available.</p>
      </section>
    );
  }

  return (
    <section className="drawer-section">
      <h4 className="drawer-section-title">Analytical Sensitivity</h4>
      <p className="drawer-caption sensitivity-subtitle">
        Level 1 Analytical Sensitivity — not perturbation simulation
      </p>

      <label className="drawer-field-label" htmlFor="cf-chunk-select">
        Temporal chunk
      </label>
      <select
        id="cf-chunk-select"
        className="drawer-select"
        value={chunkIndex}
        onChange={(e) => setChunkIndex(Number(e.target.value))}
      >
        {chunks.map((chunk, index) => (
          <option key={index} value={index}>
            Chunk {chunk.chunk_index ?? index} ({chunk.start_time ?? 0}s–{chunk.end_time ?? 0}s)
          </option>
        ))}
      </select>

      <div className="sensitivity-list">
        {agentEntries.map(([agent, info]) => {
          const delta = Math.min(
            20,
            Math.max(0, Math.abs(Number(info?.estimated_delta_for_10pct) || 0) * 100 || Math.abs(Number(info?.gradient) || 0) * 10),
          );
          return (
            <div key={agent} className="sensitivity-row glass">
              <div className="sensitivity-row-header">
                <strong>{agent}</strong>
                <span className={`sensitivity-direction direction-${info?.direction || 'neutral'}`}>
                  {info?.direction || 'neutral'}
                </span>
              </div>
              <input
                type="range"
                min={0}
                max={20}
                step={0.5}
                value={delta}
                readOnly
                className="sensitivity-slider"
                aria-label={`${agent} sensitivity`}
              />
              <p className="sensitivity-statement">{info?.statement || 'No sensitivity statement.'}</p>
              <p className="sensitivity-meta">
                Gradient: {Number(info?.gradient || 0).toFixed(4)}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default CounterfactualPanel;

import React, { useEffect, useMemo, useState } from 'react';
import { compressTimeline } from '../../utils/compressTimeline';
import { EVENT_LEGEND, getEventMeta, formatTimeRange } from '../../utils/forensicLabels';
import { buildChunkSuspicionSummary } from '../../utils/chunkEvidence';
import TimelinePanel from './TimelinePanel';
import TemporalHeatmap from './TemporalHeatmap';

const ChunkEvidenceExplorer = ({ result }) => {
  const timeline = useMemo(() => compressTimeline(result?.timeline || []), [result?.timeline]);
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    if (selectedIndex >= timeline.length) {
      setSelectedIndex(0);
    }
  }, [timeline.length, selectedIndex]);

  const selectedChunk = timeline[selectedIndex] || null;
  const suspicion = useMemo(
    () => buildChunkSuspicionSummary(selectedChunk, result?.consensus),
    [selectedChunk, result?.consensus],
  );
  const eventMeta = selectedChunk ? getEventMeta(selectedChunk.event_type) : null;

  return (
    <div className="chunk-evidence-explorer span-12">
      <div className="chunk-evidence-header">
        <h3 className="panel-title">Temporal evidence &amp; chunk inspector</h3>
        <p className="chunk-evidence-subtitle">
          Select a segment to view mel spectrogram, per-agent snapshot, and why it was flagged.
        </p>
      </div>

      <div className="timeline-legend-row">
        {EVENT_LEGEND.map((item) => (
          <div key={item.key} className={`timeline-legend-item ${item.className}`} title={item.description}>
            <span className="timeline-legend-swatch" />
            <span className="timeline-legend-label">{item.label}</span>
          </div>
        ))}
      </div>

      <TimelinePanel
        timeline={result?.timeline}
        selectedIndex={selectedIndex}
        onSelectChunk={setSelectedIndex}
      />

      <div className="chunk-inspector-grid">
        <div className={`chunk-suspicion-card glass severity-${suspicion.severity}`}>
          <h4>Why this chunk is suspicious</h4>
          <p className="chunk-suspicion-headline">{suspicion.headline}</p>
          <ul className="chunk-suspicion-list">
            {suspicion.bullets.map((line, i) => (
              <li key={i}>{line}</li>
            ))}
          </ul>
          {selectedChunk?.segment_count > 1 && (
            <p className="drawer-caption">
              Merged from {selectedChunk.segment_count} underlying chunk events.
            </p>
          )}
        </div>

        <div className="chunk-mel-panel glass">
          <h4>Mel spectrogram · {eventMeta?.label || 'segment'}</h4>
          <p className="drawer-caption">{formatTimeRange(selectedChunk?.start_time, selectedChunk?.end_time)}</p>
          {selectedChunk?.mel_preview_base64 ? (
            <img
              className="chunk-mel-image"
              src={`data:image/png;base64,${selectedChunk.mel_preview_base64}`}
              alt={`Mel spectrogram ${formatTimeRange(selectedChunk.start_time, selectedChunk.end_time)}`}
            />
          ) : (
            <div className="chunk-mel-empty">
              <p>No mel preview for this segment.</p>
              <p className="drawer-caption">Re-run analysis on a newer build to generate per-segment spectrograms.</p>
            </div>
          )}
        </div>

        <div className="chunk-agent-snapshot glass">
          <h4>Per-chunk agent snapshot</h4>
          {!selectedChunk?.details || !Object.keys(selectedChunk.details).length ? (
            <p className="drawer-empty">No per-agent details on this segment.</p>
          ) : (
            <table className="chunk-agent-table">
              <thead>
                <tr>
                  <th>Agent</th>
                  <th>Verdict</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(selectedChunk.details).map(([agent, info]) => (
                  <tr key={agent}>
                    <td>{agent}</td>
                    <td>{info?.verdict || info?.calibrated_verdict || '—'}</td>
                    <td>
                      {Math.round((info?.calibrated_confidence ?? info?.confidence ?? 0) * 100)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {result?.heatmap_base64 && (
        <TemporalHeatmap
          base64Image={result.heatmap_base64}
          timeline={timeline}
          selectedChunk={selectedChunk}
          onSelectChunk={(chunk) => {
            const idx = timeline.findIndex(
              (t) => t.start_time === chunk.start_time && t.end_time === chunk.end_time,
            );
            if (idx >= 0) setSelectedIndex(idx);
          }}
        />
      )}
    </div>
  );
};

export default ChunkEvidenceExplorer;

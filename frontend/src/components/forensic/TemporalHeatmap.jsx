import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { ZoomIn, ZoomOut, Maximize, ScanSearch } from 'lucide-react';
import { getEventMeta, formatTimeRange } from '../../utils/forensicLabels';

const TemporalHeatmap = ({ base64Image, timeline, selectedChunk, onSelectChunk }) => {
  const [scale, setScale] = useState(1);
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const containerRef = useRef(null);

  if (!base64Image) return null;

  const handleZoomIn = () => setScale((s) => Math.min(s + 0.5, 3));
  const handleZoomOut = () => setScale((s) => Math.max(s - 0.5, 1));
  const handleReset = () => setScale(1);

  const segments = timeline || [];
  const totalDuration = segments.length
    ? Math.max(...segments.map((t) => t.end_time || 0), 1)
    : 100;

  const activeSpot = hoveredIndex != null ? segments[hoveredIndex] : selectedChunk;

  return (
    <div className="glass p-6 heatmap-panel">
      <div className="flex items-center justify-between mb-4">
        <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-primary">
          <ScanSearch size={18} /> Interactive Spectral Heatmap
        </h3>
        <div className="flex gap-2">
          <button type="button" onClick={handleZoomOut} className="heatmap-tool-btn" aria-label="Zoom out">
            <ZoomOut size={16} />
          </button>
          <button type="button" onClick={handleReset} className="heatmap-tool-btn" aria-label="Reset zoom">
            <Maximize size={16} />
          </button>
          <button type="button" onClick={handleZoomIn} className="heatmap-tool-btn" aria-label="Zoom in">
            <ZoomIn size={16} />
          </button>
        </div>
      </div>

      {activeSpot && (
        <div className="heatmap-active-callout" role="status">
          <strong>{getEventMeta(activeSpot.event_type).label}</strong>
          <span>
            {formatTimeRange(activeSpot.start_time, activeSpot.end_time)} · {activeSpot.verdict} ·{' '}
            {Math.round((activeSpot.confidence || 0) * 100)}%
          </span>
        </div>
      )}

      <div className="heatmap-viewport" ref={containerRef}>
        <motion.div
          drag
          dragConstraints={containerRef}
          className="heatmap-drag-layer"
          animate={{ scale }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          <img
            src={`data:image/jpeg;base64,${base64Image}`}
            alt="Grad-CAM spectral heatmap"
            className="heatmap-image"
            draggable="false"
          />

          {segments.map((spot, i) => {
            const start = spot.start_time || 0;
            const end = spot.end_time || start;
            const leftPercent = (start / totalDuration) * 100;
            const widthPercent = Math.max(((end - start) / totalDuration) * 100, 0.8);
            const typeKey = getEventMeta(spot.event_type).key;
            const isActive =
              selectedChunk &&
              selectedChunk.start_time === spot.start_time &&
              selectedChunk.end_time === spot.end_time;

            return (
              <button
                key={`${start}-${end}-${i}`}
                type="button"
                className={`heatmap-band heatmap-band-${typeKey} ${isActive ? 'heatmap-band-active' : ''}`}
                style={{ left: `${leftPercent}%`, width: `${widthPercent}%` }}
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
                onFocus={() => setHoveredIndex(i)}
                onBlur={() => setHoveredIndex(null)}
                onClick={() => onSelectChunk?.(spot)}
                aria-label={`${getEventMeta(spot.event_type).label} ${formatTimeRange(start, end)}`}
              />
            );
          })}
        </motion.div>
      </div>

      <div className="heatmap-legend mt-4">
        <div className="timeline-legend-item legend-splice">
          <span className="timeline-legend-swatch" /> Splice / anomaly band
        </div>
        <div className="timeline-legend-item legend-contradiction">
          <span className="timeline-legend-swatch" /> Contradiction band
        </div>
        <span className="heatmap-legend-hint">Hover or click bands · drag image to pan</span>
      </div>
    </div>
  );
};

export default TemporalHeatmap;

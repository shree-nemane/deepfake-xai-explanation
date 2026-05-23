import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { ZoomIn, ZoomOut, Maximize, ScanSearch } from 'lucide-react';

const TemporalHeatmap = ({ base64Image, timeline }) => {
  const [scale, setScale] = useState(1);
  const containerRef = useRef(null);

  if (!base64Image) return null;

  const handleZoomIn = () => setScale((s) => Math.min(s + 0.5, 3));
  const handleZoomOut = () => setScale((s) => Math.max(s - 0.5, 1));
  const handleReset = () => setScale(1);

  const anomalySpots = timeline ? timeline.filter((t) => t.event_type !== 'NORMAL') : [];
  const totalDuration = timeline?.length
    ? Math.max(...timeline.map((t) => t.end_time || 0), 1)
    : 100;

  return (
    <div className="glass p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-primary">
          <ScanSearch size={18} /> Interactive Spectral Heatmap
        </h3>
        <div className="flex gap-2">
          <button onClick={handleZoomOut} className="p-2 hover:bg-white/5 rounded text-muted hover:text-white transition-colors"><ZoomOut size={16} /></button>
          <button onClick={handleReset} className="p-2 hover:bg-white/5 rounded text-muted hover:text-white transition-colors"><Maximize size={16} /></button>
          <button onClick={handleZoomIn} className="p-2 hover:bg-white/5 rounded text-muted hover:text-white transition-colors"><ZoomIn size={16} /></button>
        </div>
      </div>

      <div
        className="relative flex-grow overflow-hidden rounded-xl border border-white/10 bg-black/50 cursor-grab active:cursor-grabbing h-64"
        ref={containerRef}
      >
        <motion.div
          drag
          dragConstraints={containerRef}
          className="absolute inset-0 w-full h-full"
          animate={{ scale }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          <img
            src={`data:image/jpeg;base64,${base64Image}`}
            alt="Temporal Heatmap"
            className="w-full h-full object-fill opacity-80"
            draggable="false"
          />

          {anomalySpots.map((spot, i) => {
            const start = spot.start_time || 0;
            const end = spot.end_time || start;
            const leftPercent = (start / totalDuration) * 100;
            const widthPercent = Math.max(((end - start) / totalDuration) * 100, 1);
            const isContradiction = spot.event_type?.toLowerCase() === 'contradiction';

            return (
              <div
                key={i}
                className={`absolute top-0 bottom-0 border-x border-white/20 hover:bg-white/10 transition-colors group z-10 ${
                  isContradiction ? 'bg-warning/20' : 'bg-error/30'
                }`}
                style={{
                  left: `${leftPercent}%`,
                  width: `${widthPercent}%`,
                }}
              >
                <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-black/90 border border-white/10 px-3 py-2 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-20 shadow-xl">
                  <div className="font-bold mb-1 text-white">{start}s - {end}s</div>
                  <div className={`capitalize ${isContradiction ? 'text-warning' : 'text-error'}`}>
                    {spot.verdict} at {Math.round((spot.confidence || 0) * 100)}%
                  </div>
                </div>
              </div>
            );
          })}
        </motion.div>
      </div>

      <div className="mt-4 flex gap-4 text-xs text-muted justify-center">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-error/40 border border-error"></div> Anomaly Detected
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-warning/40 border border-warning"></div> Contradiction
        </div>
        <div className="flex items-center gap-2 text-gray-500">
          <Maximize size={12} /> Drag to pan, use buttons to zoom
        </div>
      </div>
    </div>
  );
};

export default TemporalHeatmap;

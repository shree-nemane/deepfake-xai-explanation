import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Volume2, Maximize2, BarChart2 } from 'lucide-react';

const ReliabilityPanel = ({ agent }) => {
  if (!agent || !agent.evidence) return null;

  const {
    snr_db,
    snr,
    clipping_ratio = 0,
    spectral_flatness = 0,
    reliability_score = agent.confidence || 0,
  } = agent.evidence;
  const snrValue = snr_db ?? snr ?? 0;
  const isReliable = agent.verdict === 'reliable';

  const getScoreColor = (val, threshold, inverse = false) => {
    if (inverse) return val > threshold ? 'text-error' : 'text-success';
    return val > threshold ? 'text-success' : 'text-error';
  };

  return (
    <div className={`glass p-6 h-full border-t-4 ${isReliable ? 'border-t-success' : 'border-t-error'}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-primary">
          <Activity size={18} /> Recording Trust Analysis
        </h3>
        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest ${
          isReliable ? 'bg-success/20 text-success' : 'bg-error/20 text-error'
        }`}>
          {isReliable ? 'Trusted' : 'Degraded'}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Composite Score */}
        <div className="col-span-2 bg-black/40 rounded-xl p-4 flex items-center justify-between border border-white/5">
          <div>
            <div className="text-xs uppercase text-muted tracking-widest mb-1">Composite Reliability Score</div>
            <div className="text-sm text-gray-400">Aggregated signal quality trust metric</div>
          </div>
          <div className={`text-3xl font-black ${getScoreColor(reliability_score, 0.5)}`}>
            {Math.round(reliability_score * 100)}%
          </div>
        </div>

        {/* SNR */}
        <div className="bg-black/40 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 text-xs uppercase text-muted tracking-widest mb-2">
            <Volume2 size={14} /> Signal-to-Noise Ratio
          </div>
          <div className="flex items-end justify-between">
            <div className={`text-2xl font-bold ${getScoreColor(snrValue, 15)}`}>
              {snrValue.toFixed(1)} <span className="text-sm text-muted">dB</span>
            </div>
            <div className="text-xs text-gray-500">{snrValue > 15 ? 'Clean' : 'Noisy'}</div>
          </div>
        </div>

        {/* Clipping */}
        <div className="bg-black/40 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 text-xs uppercase text-muted tracking-widest mb-2">
            <Maximize2 size={14} /> Clipping Ratio
          </div>
          <div className="flex items-end justify-between">
            <div className={`text-2xl font-bold ${getScoreColor(clipping_ratio, 0.01, true)}`}>
              {(clipping_ratio * 100)?.toFixed(2)} <span className="text-sm text-muted">%</span>
            </div>
            <div className="text-xs text-gray-500">{clipping_ratio > 0.01 ? 'Clipped' : 'Nominal'}</div>
          </div>
        </div>

        {/* Spectral Flatness */}
        <div className="col-span-2 bg-black/40 rounded-xl p-4 border border-white/5">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-xs uppercase text-muted tracking-widest">
              <BarChart2 size={14} /> Spectral Flatness
            </div>
            <div className={`text-lg font-bold ${getScoreColor(spectral_flatness, 0.5, true)}`}>
              {spectral_flatness?.toFixed(3)}
            </div>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-1.5 mt-2 overflow-hidden">
            <motion.div 
              className={`h-1.5 rounded-full ${spectral_flatness > 0.5 ? 'bg-error' : 'bg-success'}`}
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(spectral_flatness * 100, 100)}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </div>
          <div className="text-xs text-gray-500 mt-2 text-right">
            {spectral_flatness > 0.5 ? 'Highly compressed / noise-like' : 'Tonal content detected'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReliabilityPanel;

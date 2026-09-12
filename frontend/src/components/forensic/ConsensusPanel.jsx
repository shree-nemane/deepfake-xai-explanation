import React from 'react';
import { 
  Waves, 
  Cpu, 
  Fingerprint, 
  ShieldCheck, 
  Activity, 
  Volume2, 
  Maximize2,
  BarChart2
} from 'lucide-react';

const formatPercent = (val) => `${Math.round((Number(val) || 0) * 100)}%`;

const getVerdictClass = (verdict) => {
  const v = (verdict || '').toLowerCase();
  if (v === 'fake') return 'vote-fake';
  if (v === 'real' || v === 'reliable') return 'vote-real';
  return 'vote-inconclusive';
};

const ConsensusPanel = ({ consensus, agents }) => {
  const convnext = agents?.convnext || {};
  const wavlm = agents?.wavlm || {};
  const acoustic = agents?.acoustic || {};
  const reliability = agents?.reliability || {};

  const relEvidence = reliability?.evidence || {};
  const snrDb = relEvidence.snr_db ?? relEvidence.snr ?? 0;
  const clipping = relEvidence.clipping_ratio ?? 0;
  const flatness = relEvidence.spectral_flatness ?? 0;
  const isReliable = reliability?.verdict === 'reliable';

  return (
    <section className="consensus-bench-section">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-primary">
            <Activity size={18} /> Multi-Agent Consensus Bench
          </h3>
          <p className="text-xs text-muted mt-0.5">
            4 independent forensic specialists calibrated through dynamic signal suppression.
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="text-muted">
            Convergence: <strong className="text-white">{formatPercent(consensus?.convergence_strength)}</strong>
          </span>
          <span className="text-muted">
            Threshold: <strong className="text-white">{formatPercent(consensus?.decision_threshold || 0.6)}</strong>
          </span>
        </div>
      </div>

      {/* 4-Agent Consensus Grid */}
      <div className="grid grid-cols-4 gap-4">
        {/* Agent 01: ConvNeXt */}
        <div className={`agent-card ${convnext.verdict === 'fake' ? 'alert-fake' : convnext.verdict === 'real' ? 'alert-real' : 'alert-warning'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                <Waves size={16} className="text-primary" />
              </div>
              <span className="text-[10px] font-mono font-bold text-muted uppercase tracking-wider">
                01 / SPECTRAL
              </span>
            </div>
            <span className={`text-[11px] font-bold uppercase font-mono px-2 py-0.5 rounded ${getVerdictClass(convnext.verdict)}`}
              style={{ background: 'rgba(255,255,255,0.05)' }}>
              {convnext.verdict || 'inconclusive'}
            </span>
          </div>
          <h4 className="text-sm font-bold text-white mb-1">ConvNeXt Classifier</h4>
          <p className="text-xs text-muted mb-3" style={{ minHeight: '32px' }}>
            High-frequency spectrogram artifacts & boundary anomalies.
          </p>
          <div className="consensus-metric py-1">
            <span>Confidence</span>
            <strong>{formatPercent(convnext.confidence)}</strong>
          </div>
          <div className="consensus-metric py-1">
            <span>Uncertainty</span>
            <strong>{formatPercent(convnext.uncertainty)}</strong>
          </div>
        </div>

        {/* Agent 02: WavLM */}
        <div className={`agent-card ${wavlm.verdict === 'fake' ? 'alert-fake' : wavlm.verdict === 'real' ? 'alert-real' : 'alert-warning'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                <Cpu size={16} className="text-primary" />
              </div>
              <span className="text-[10px] font-mono font-bold text-muted uppercase tracking-wider">
                02 / PHONETIC
              </span>
            </div>
            <span className={`text-[11px] font-bold uppercase font-mono px-2 py-0.5 rounded ${getVerdictClass(wavlm.verdict)}`}
              style={{ background: 'rgba(255,255,255,0.05)' }}>
              {wavlm.verdict || 'inconclusive'}
            </span>
          </div>
          <h4 className="text-sm font-bold text-white mb-1">WavLM Embeddings</h4>
          <p className="text-xs text-muted mb-3" style={{ minHeight: '32px' }}>
            Phonetic continuity deviations & transformer temporal entropy.
          </p>
          <div className="consensus-metric py-1">
            <span>Confidence</span>
            <strong>{formatPercent(wavlm.confidence)}</strong>
          </div>
          <div className="consensus-metric py-1">
            <span>Uncertainty</span>
            <strong>{formatPercent(wavlm.uncertainty)}</strong>
          </div>
        </div>

        {/* Agent 03: Acoustic Plausibility */}
        <div className={`agent-card ${acoustic.verdict === 'fake' ? 'alert-fake' : acoustic.verdict === 'real' ? 'alert-real' : 'alert-warning'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                <Fingerprint size={16} className="text-primary" />
              </div>
              <span className="text-[10px] font-mono font-bold text-muted uppercase tracking-wider">
                03 / BIOLOGICAL
              </span>
            </div>
            <span className={`text-[11px] font-bold uppercase font-mono px-2 py-0.5 rounded ${getVerdictClass(acoustic.verdict)}`}
              style={{ background: 'rgba(255,255,255,0.05)' }}>
              {acoustic.verdict || 'inconclusive'}
            </span>
          </div>
          <h4 className="text-sm font-bold text-white mb-1">Acoustic Plausibility</h4>
          <p className="text-xs text-muted mb-3" style={{ minHeight: '32px' }}>
            Natural vocal tract baselines: pitch, jitter, and shimmer Z-scores.
          </p>
          <div className="consensus-metric py-1">
            <span>Confidence</span>
            <strong>{formatPercent(acoustic.confidence)}</strong>
          </div>
          <div className="consensus-metric py-1">
            <span>Uncertainty</span>
            <strong>{formatPercent(acoustic.uncertainty)}</strong>
          </div>
        </div>

        {/* Agent 04: Signal Reliability */}
        <div className={`agent-card ${isReliable ? 'alert-real' : 'alert-warning'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                <ShieldCheck size={16} className="text-primary" />
              </div>
              <span className="text-[10px] font-mono font-bold text-muted uppercase tracking-wider">
                04 / INTEGRITY
              </span>
            </div>
            <span className={`text-[11px] font-bold uppercase font-mono px-2 py-0.5 rounded ${isReliable ? 'vote-real' : 'vote-inconclusive'}`}
              style={{ background: 'rgba(255,255,255,0.05)' }}>
              {isReliable ? 'trusted' : 'degraded'}
            </span>
          </div>
          <h4 className="text-sm font-bold text-white mb-1">Signal Reliability</h4>
          <p className="text-xs text-muted mb-3" style={{ minHeight: '32px' }}>
            SNR, clipping, and spectral flatness calibrating agent weights.
          </p>
          <div className="consensus-metric py-1">
            <span className="flex items-center gap-1">
              <Volume2 size={12} /> SNR (HPSS)
            </span>
            <strong>{Number(snrDb).toFixed(1)} dB</strong>
          </div>
          <div className="consensus-metric py-1">
            <span className="flex items-center gap-1">
              <Maximize2 size={12} /> Clipping
            </span>
            <strong>{(Number(clipping) * 100).toFixed(2)}%</strong>
          </div>
          <div className="consensus-metric py-1">
            <span className="flex items-center gap-1">
              <BarChart2 size={12} /> Flatness
            </span>
            <strong>{Number(flatness).toFixed(3)}</strong>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ConsensusPanel;

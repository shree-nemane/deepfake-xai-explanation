import React from 'react';
import { motion } from 'framer-motion';
import { 
  ShieldCheck, 
  Cpu, 
  Waves, 
  GitCommit, 
  ArrowRight, 
  FileAudio, 
  CheckCircle2, 
  AlertTriangle 
} from 'lucide-react';

const Hero = ({ onStart, onLoadSample }) => {
  const capabilities = [
    {
      icon: Waves,
      tag: '01 / ACOUSTICS',
      title: 'Dual-Stream Signal',
      desc: 'Synchronized 48 kHz acoustic transients alongside 16 kHz neural representations, calibrated under EBU R128 loudness standards.'
    },
    {
      icon: Cpu,
      tag: '02 / CONSENSUS',
      title: 'Dynamic Suppression',
      desc: 'Panel of 4 forensic models (ConvNeXt, WavLM, ResNet, Anomaly Z-Score) with real-time SNR and clipping suppression to prevent noisy false positives.'
    },
    {
      icon: GitCommit,
      tag: '03 / EXPLAINABILITY',
      title: 'Game-Theoretic SHAP',
      desc: 'Mathematically exact Shapley coalition values and Grad-CAM spectrogram heatmaps identifying synthetic artifact clusters across time.'
    },
    {
      icon: ShieldCheck,
      tag: '04 / INTEGRITY',
      title: 'Verifiable Audit Trail',
      desc: 'Immutable report logging, contradiction threat classification (D-01 Voice Clone, D-02 Splice), and reproducible compliance trails.'
    }
  ];

  return (
    <div className="flex flex-col items-center justify-center py-8 text-center">
      {/* Forensic Intelligence Header Badge */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="status-pill mb-6"
        style={{ 
          background: 'var(--primary-soft)', 
          color: 'var(--primary-light)', 
          border: '1px solid var(--border-bright)',
          padding: '0.45rem 1.1rem'
        }}
      >
        <div className="pulse-dot" style={{ background: 'var(--primary)' }} />
        <span>Forensic Audio Intelligence · Multi-Agent Consensus</span>
      </motion.div>

      {/* Main Title & Subtitle */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.45 }}
        className="max-w-2xl mx-auto"
      >
        <h1 className="text-4xl font-semibold mb-4 tracking-tight" style={{ lineHeight: 1.2 }}>
          Deterministic Audio Authentication <br />
          <span className="text-gradient">with Multi-Agent Consensus</span>
        </h1>
        <p className="text-base text-muted max-w-xl mx-auto mb-8 leading-relaxed">
          Authenticate speech recordings against synthetic voice clones, neural conversions, and temporal splices with mathematical explainability.
        </p>
      </motion.div>

      {/* Action Buttons & Quick Specimen Bar */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.45 }}
        className="flex flex-wrap items-center justify-center gap-3 mb-12"
      >
        <button 
          onClick={onStart} 
          className="btn btn-primary px-8 py-3 text-sm font-semibold flex items-center gap-2"
        >
          <FileAudio size={16} />
          <span>Scan Evidence File</span>
          <ArrowRight size={15} />
        </button>

        {onLoadSample && (
          <div className="flex items-center gap-2 flex-wrap justify-center">
            <button 
              onClick={() => onLoadSample('fake1.wav')}
              className="specimen-btn specimen-fake"
              title="Test detection against a known synthesized voice clone"
            >
              <AlertTriangle size={14} className="text-error" />
              <span>Specimen: Synthetic Clone</span>
            </button>

            <button 
              onClick={() => onLoadSample('adi.wav')}
              className="specimen-btn specimen-real"
              title="Test authenticity verification against natural speech"
            >
              <CheckCircle2 size={14} className="text-success" />
              <span>Specimen: Authentic Human</span>
            </button>
          </div>
        )}
      </motion.div>

      {/* Architectural Capabilities Grid */}
      <div className="grid-container w-full mt-4">
        {capabilities.map((item, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 * idx + 0.25, duration: 0.4 }}
            className="span-3 glass glass-hover p-6 text-left"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
                <item.icon className="text-primary" size={20} />
              </div>
              <span className="text-[10px] font-mono tracking-widest text-muted uppercase font-bold">
                {item.tag}
              </span>
            </div>
            <h3 className="text-base font-semibold mb-2 text-white">
              {item.title}
            </h3>
            <p className="text-xs text-muted leading-relaxed">
              {item.desc}
            </p>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Hero;

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Activity, 
  Clock, 
  Waves, 
  ShieldAlert, 
  ShieldCheck,
  ArrowRight,
  Download
} from 'lucide-react';
import { RadarFeatureChart, ShapBarChart, TimelineChart } from './AnalysisCharts';
import VisualXAI from './VisualXAI';

const Dashboard = ({ result, onReset }) => {
  if (!result) return null;

  const forensicData = result.forensic_features.map(f => ({
    subject: f.feature_name.replace('_', ' ').toUpperCase(),
    A: f.anomaly_score * 100,
    fullMark: 100
  }));

  const shapData = Object.entries(result.xai.shap).map(([name, score]) => ({
    name: name.replace('_', ' ').toUpperCase(),
    score: score * 100
  })).sort((a, b) => b.score - a.score);

  const isFake = result.risk_score > 50;

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      className="flex flex-col gap-6 pb-20"
    >
      {/* 1. Refined Verdict Banner */}
      <div className={`verdict-banner glass ${isFake ? 'fake' : 'real'}`}>
        <div className="verdict-icon-container">
          {isFake ? (
            <ShieldAlert size={40} className="text-error" />
          ) : (
            <ShieldCheck size={40} className="text-success" />
          )}
        </div>
        
        <div className="flex flex-col">
          <h2 className={`verdict-title ${isFake ? 'text-error' : 'text-success'}`}>
            {isFake ? 'Manipulated Content Detected' : 'Authentic Content Verified'}
          </h2>
          <p className="verdict-subtitle">
            {isFake 
              ? 'Our system identified neural signatures and acoustic patterns consistent with AI synthesis.'
              : 'Our system verified this audio as natural. No significant forensic anomalies were detected.'}
          </p>
        </div>

        <div className="verdict-stats">
          <div className="text-center">
            <div className="text-[10px] uppercase font-bold text-muted mb-1 tracking-widest">Confidence</div>
            <div className="text-xl font-bold">
              {isFake ? (100 - Math.round(result.confidence * 100)) : Math.round(result.confidence * 100)}%
            </div>
          </div>
          <div className="text-center">
            <div className="text-[10px] uppercase font-bold text-muted mb-1 tracking-widest">Risk Level</div>
            <div className={`text-xl font-bold ${isFake ? 'text-error' : 'text-success'}`}>
              {isFake ? 'CRITICAL' : 'LOW'}
            </div>
          </div>
        </div>
      </div>

      <div className="grid-container">
        {/* Verdict Card */}
        <div className="span-4 glass p-8 flex flex-col items-center justify-center text-center">
          <h3 className="text-muted text-[10px] uppercase tracking-widest mb-6 font-bold">Forensic Verdict</h3>
          
          <div className="relative mb-8">
            <svg width="180" height="180" viewBox="0 0 160 160">
              <circle cx="80" cy="80" r="70" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="12" />
              <circle 
                cx="80" cy="80" r="70" fill="none" 
                stroke={isFake ? 'var(--error)' : 'var(--success)'} 
                strokeWidth="12" 
                strokeDasharray={440} 
                strokeDashoffset={440 - (440 * result.risk_score) / 100} 
                strokeLinecap="round" 
                className="transition-all duration-1000 ease-out"
                style={{ filter: `drop-shadow(0 0 8px ${isFake ? 'var(--error-glow)' : 'var(--success-glow)'})` }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-black">{Math.round(result.risk_score)}</span>
              <span className="text-[10px] text-muted font-bold tracking-widest">RISK SCORE</span>
            </div>
          </div>

          <div className={`flex items-center gap-2 px-6 py-2 rounded-full mb-6 ${isFake ? 'bg-error/10 text-error' : 'bg-success/10 text-success'}`}>
            {isFake ? <ShieldAlert size={20} /> : <ShieldCheck size={20} />}
            <span className="text-xl font-black uppercase tracking-tight">{result.prediction}</span>
          </div>

          <div className="grid grid-cols-2 gap-4 w-full text-xs">
            <div className="glass p-3 rounded-xl">
              <div className="text-muted mb-1 uppercase font-bold text-[9px]">Confidence</div>
              <div className="font-bold text-base">{Math.round(result.confidence * 100)}%</div>
            </div>
            <div className="glass p-3 rounded-xl">
              <div className="text-muted mb-1 uppercase font-bold text-[9px]">Uncertainty</div>
              <div className={`font-bold text-base uppercase ${result.uncertainty === 'low' ? 'text-success' : 'text-warning'}`}>
                {result.uncertainty}
              </div>
            </div>
          </div>
        </div>

        {/* Narrative Card */}
        <div className="span-8 glass p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-2 text-primary">
              <Search size={20} />
              <h3 className="text-sm uppercase tracking-widest font-bold">Investigation Narrative</h3>
            </div>
            <button className="btn btn-ghost px-4 py-2 text-xs flex items-center gap-2">
              <Download size={14} /> Export Report
            </button>
          </div>
          
          <div className="flex flex-col gap-6">
            <div className="glass bg-white/5 p-4 rounded-xl border-l-4 border-primary">
              <div className="text-[10px] text-primary uppercase font-black mb-2 flex items-center gap-2">
                <ShieldCheck size={12} /> Expert Reasoning
              </div>
              <p className="text-lg font-medium text-white italic leading-snug">
                "{result.detailed_narrative.layman_explanation}"
              </p>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="text-[10px] text-muted uppercase font-bold mb-2 tracking-widest">Acoustic Evidence</div>
                <p className="text-xs leading-relaxed text-muted">
                  {result.detailed_narrative.acoustic_evidence}
                </p>
              </div>
              <div>
                <div className="text-[10px] text-muted uppercase font-bold mb-2 tracking-widest">Neural Recognition</div>
                <p className="text-xs leading-relaxed text-muted">
                  {result.detailed_narrative.neural_evidence}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="span-12 glass p-8">
          <div className="grid grid-cols-2 gap-12">
            <div>
              <h3 className="flex items-center gap-2 mb-8 text-sm font-bold uppercase tracking-wider">
                <Activity size={18} className="text-primary" />
                Acoustic Anomaly Profile
              </h3>
              <RadarFeatureChart data={forensicData} />
            </div>
            <div>
              <h3 className="flex items-center gap-2 mb-8 text-sm font-bold uppercase tracking-wider">
                <ShieldAlert size={18} className="text-primary" />
                Feature Contribution (SHAP)
              </h3>
              <ShapBarChart data={shapData} />
            </div>
          </div>
        </div>

        {/* Timeline Row */}
        <div className="span-12 glass p-8">
          <div className="flex justify-between items-center mb-8">
            <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider">
              <Clock size={18} className="text-primary" />
              Temporal Stability Analysis
            </h3>
            <div className="flex gap-4">
              <div className="flex items-center gap-2 text-[10px] text-muted">
                <div className="w-2 h-2 rounded-full bg-primary"></div> Zero Crossing Rate
              </div>
              <div className="flex items-center gap-2 text-[10px] text-muted">
                <div className="w-2 h-2 rounded-full bg-secondary"></div> Timbre Instability
              </div>
            </div>
          </div>
          <TimelineChart data={result.timeline_data} />
        </div>

        {/* Counterfactual Suggestions */}
        <div className="span-12 glass p-8">
          <div className="flex items-center gap-2 mb-8">
            <Activity size={18} className="text-primary" />
            <h3 className="text-sm font-bold uppercase tracking-wider">Counterfactual Suggestions (What-If)</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {result.xai.counterfactuals.map((cf, i) => (
              <div key={i} className="glass bg-white/5 p-4 rounded-xl border-l-4 border-warning flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-black text-warning uppercase">{cf.feature}</span>
                  <span className="text-[10px] text-muted font-bold">Impact: {cf.impact_estimate}</span>
                </div>
                <div className="text-sm font-bold text-white">{cf.observation}</div>
                <div className="text-xs text-muted">{cf.suggestion}</div>
              </div>
            ))}
            {result.xai.counterfactuals.length === 0 && (
              <div className="span-2 text-center py-8 text-muted italic">
                No significant anomalies detected for counterfactual generation.
              </div>
            )}
          </div>
        </div>

        {/* Visual XAI Section */}
        <div className="span-12">
          <div className="flex items-center gap-2 mb-6">
            <Waves size={20} className="text-primary" />
            <h3 className="text-sm font-bold uppercase tracking-wider">Spectral Evidence & Neural Attention</h3>
          </div>
          <VisualXAI 
            gradcam={result.xai.gradcam} 
            ig={result.xai.integrated_gradients} 
          />
        </div>
      </div>

      <div className="flex justify-center mt-8">
        <button 
          className="btn glass glass-hover px-10 py-4 flex items-center gap-3 text-base font-bold"
          onClick={onReset}
        >
          <ArrowRight size={20} /> Start New Investigation
        </button>
      </div>
    </motion.div>
  );
};

export default Dashboard;

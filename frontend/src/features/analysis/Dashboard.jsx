import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, ShieldAlert, Activity, ArrowRight } from 'lucide-react';
import AgentCard from '../../components/forensic/AgentCard';
import TimelinePanel from '../../components/forensic/TimelinePanel';
import ConsensusPanel from '../../components/forensic/ConsensusPanel';
import TemporalHeatmap from '../../components/forensic/TemporalHeatmap';
import EvidenceGraph from '../../components/forensic/EvidenceGraph';
import FeatureAnalysisPanel from '../../components/forensic/FeatureAnalysisPanel';

import ReliabilityPanel from '../../components/forensic/ReliabilityPanel';

const Dashboard = ({ result, onReset }) => {
  if (!result) return null;

  const isFake = result.consensus.verdict === 'fake';
  const isInconclusive = result.consensus.verdict === 'inconclusive';

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      className="flex flex-col gap-6 pb-20"
    >
      {/* 1. Consensus Verdict Banner */}
      <div className={`verdict-banner glass ${isFake ? 'fake' : isInconclusive ? 'warning' : 'real'}`}>
        <div className="verdict-icon-container">
          {isFake || isInconclusive ? <ShieldAlert size={40} className={isFake ? 'text-error' : 'text-warning'} /> : <ShieldCheck size={40} className="text-success" />}
        </div>
        
        <div className="flex flex-col">
          <h2 className={`verdict-title ${isFake ? 'text-error' : isInconclusive ? 'text-warning' : 'text-success'}`}>
            {isFake ? 'Manipulated Content Detected' : isInconclusive ? 'Analysis Inconclusive' : 'Authentic Content Verified'}
          </h2>
          <p className="verdict-subtitle">
            Based on multi-agent consensus analysis and temporal convergence tracking.
          </p>
        </div>

        <div className="verdict-stats flex gap-8">
          <div className="text-center">
            <div className="text-[10px] uppercase font-bold text-muted mb-1 tracking-widest">Confidence</div>
            <div className="text-xl font-bold">
              {Math.round(result.consensus.confidence * 100)}%
            </div>
          </div>
          <div className="text-center">
            <div className="text-[10px] uppercase font-bold text-muted mb-1 tracking-widest">Convergence</div>
            <div className={`text-xl font-bold ${result.consensus.convergence_strength > 0.8 ? 'text-success' : 'text-warning'}`}>
              {Math.round(result.consensus.convergence_strength * 100)}%
            </div>
          </div>
        </div>
      </div>

      <div className="grid-container">
        {/* Consensus Panel */}
        <div className="span-4">
          <ConsensusPanel consensus={result.consensus} agents={result.agents} />
        </div>

        {/* Evidence Graph */}
        <div className="span-8">
          <EvidenceGraph
            agents={result.agents}
            consensus={result.consensus}
            diagnostics={result.diagnostics}
          />
        </div>

        {/* Reliability Panel */}
        {result.agents.reliability && (
          <div className="span-12 mt-4">
            <ReliabilityPanel agent={result.agents.reliability} />
          </div>
        )}

        <div className="span-12">
          <FeatureAnalysisPanel
            featureAnalysis={result.feature_analysis}
            preprocessing={result.preprocessing}
            diagnostics={result.diagnostics}
          />
        </div>

        {/* Agents Row */}
        <div className="span-12 mt-4">
          <h3 className="flex items-center gap-2 mb-4 text-sm font-bold uppercase tracking-wider text-primary">
            <Activity size={18} /> Independent Forensic Agents
          </h3>
          <div className="grid grid-cols-4 gap-6">
            {Object.entries(result.agents).filter(([key]) => key !== 'reliability').map(([key, agent], i) => (
              <AgentCard key={i} agent={agent} />
            ))}
          </div>
        </div>

        {/* Timeline Panel */}
        <div className="span-12">
          <TimelinePanel timeline={result.timeline} />
        </div>

        {/* Temporal Heatmap */}
        {result.heatmap_base64 && (
          <div className="span-12">
            <TemporalHeatmap base64Image={result.heatmap_base64} timeline={result.timeline} />
          </div>
        )}
      </div>

      <div className="flex justify-center mt-12 mb-8">
        <button 
          className="btn bg-primary hover:bg-primary/90 text-white shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:shadow-[0_0_30px_rgba(99,102,241,0.6)] px-10 py-4 flex items-center gap-3 text-base font-bold transition-all duration-300 transform hover:-translate-y-1 rounded-xl"
          onClick={onReset}
        >
          <ArrowRight size={20} /> Start New Investigation
        </button>
      </div>
    </motion.div>
  );
};

export default Dashboard;

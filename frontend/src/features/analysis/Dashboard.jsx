import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, ShieldAlert, ArrowRight, Brain, RotateCcw } from 'lucide-react';
import ConsensusPanel from '../../components/forensic/ConsensusPanel';
import ChunkEvidenceExplorer from '../../components/forensic/ChunkEvidenceExplorer';
import ReportSummaryExport from '../../components/forensic/ReportSummaryExport';
import FeatureAnalysisPanel from '../../components/forensic/FeatureAnalysisPanel';
import DashboardViewTabs from '../../components/explainability/DashboardViewTabs';
import ForensicExplanationTab from '../../components/explainability/ForensicExplanationTab';

const DashboardOverview = ({ result }) => (
  <div className="grid-container">
    {/* Tier 1: Unified 4-Agent Consensus Bench */}
    <div className="span-12">
      <ConsensusPanel 
        consensus={result.consensus} 
        agents={result.agents} 
        diagnostics={result.diagnostics} 
      />
    </div>

    {/* Tier 2: Forensic Feature Telemetry (Intake, Neural Signals, Acoustic Deviations, Notes) */}
    <div className="span-12">
      <FeatureAnalysisPanel
        featureAnalysis={result.feature_analysis}
        preprocessing={result.preprocessing}
        diagnostics={result.diagnostics}
      />
    </div>

    {/* Tier 2: Interactive Continuous Audio Timeline & Chunk Inspector */}
    <div className="span-12">
      <ChunkEvidenceExplorer result={result} />
    </div>

    {/* Tier 3: Case Dossier Export Toolbar */}
    <div className="span-12">
      <ReportSummaryExport result={result} />
    </div>
  </div>
);

const Dashboard = ({ result, onReset }) => {
  const [activeView, setActiveView] = useState('overview');

  if (!result) return null;

  const isFake = result.consensus.verdict === 'fake';
  const isInconclusive = result.consensus.verdict === 'inconclusive';

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col gap-6 pb-20"
    >
      {/* Executive Verdict Banner */}
      <div className={`verdict-banner glass ${isFake ? 'fake' : isInconclusive ? 'warning' : 'real'}`}>
        <div className="verdict-icon-container shrink-0">
          {isFake || isInconclusive ? (
            <ShieldAlert size={36} className={isFake ? 'text-error' : 'text-warning'} />
          ) : (
            <ShieldCheck size={36} className="text-success" />
          )}
        </div>

        <div className="flex flex-col flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className={`text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
              isFake ? 'bg-error/20 text-error' : isInconclusive ? 'bg-warning/20 text-warning' : 'bg-success/20 text-success'
            }`}>
              {isFake ? 'Synthesis Detected' : isInconclusive ? 'Inconclusive' : 'Authentic Human Voice'}
            </span>
            {result.filename && (
              <span className="text-[11px] font-mono text-muted">
                Evidence: <strong className="text-white">{result.filename}</strong>
              </span>
            )}
          </div>

          <h2 className={`verdict-title ${isFake ? 'text-error' : isInconclusive ? 'text-warning' : 'text-success'}`}>
            {isFake
              ? 'Manipulated Content Detected'
              : isInconclusive
                ? 'Analysis Inconclusive'
                : 'Authentic Content Verified'}
          </h2>
          <p className="verdict-subtitle">
            Evaluated by multi-agent panel with dynamic SNR suppression and temporal timeline verification.
          </p>
        </div>

        <div className="verdict-stats flex gap-6 items-center">
          <div className="text-center">
            <div className="text-[10px] uppercase font-bold text-muted mb-0.5 tracking-wider">Confidence</div>
            <div className="text-xl font-bold font-mono text-white">
              {Math.round((result.consensus?.confidence || 0) * 100)}%
            </div>
          </div>
          <div className="text-center">
            <div className="text-[10px] uppercase font-bold text-muted mb-0.5 tracking-wider">Convergence</div>
            <div className={`text-xl font-bold font-mono ${result.consensus?.convergence_strength > 0.8 ? 'text-success' : 'text-warning'}`}>
              {Math.round((result.consensus?.convergence_strength || 0) * 100)}%
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            className="btn btn-ghost text-xs flex items-center gap-1.5"
            onClick={() => setActiveView(activeView === 'overview' ? 'explanation' : 'overview')}
            title="Toggle between Overview and Forensic Explainability"
          >
            <Brain size={15} />
            <span>{activeView === 'overview' ? 'Explainability' : 'Overview'}</span>
          </button>
          <button
            type="button"
            className="btn btn-primary text-xs flex items-center gap-1.5"
            onClick={onReset}
            title="Start new evidence scan"
          >
            <RotateCcw size={14} />
            <span>New Scan</span>
          </button>
        </div>
      </div>

      {/* View Switcher: Overview vs Forensic Explanation */}
      <DashboardViewTabs activeView={activeView} onChange={setActiveView} />

      {/* Active Tab View */}
      {activeView === 'overview' ? (
        <DashboardOverview result={result} />
      ) : (
        <ForensicExplanationTab result={result} />
      )}

      {/* Bottom Action */}
      <div className="flex justify-center mt-8 mb-4">
        <button
          className="btn btn-primary px-8 py-3 flex items-center gap-2 text-sm font-semibold"
          onClick={onReset}
        >
          <ArrowRight size={16} />
          <span>Analyze Another Evidence Recording</span>
        </button>
      </div>
    </motion.div>
  );
};

export default Dashboard;

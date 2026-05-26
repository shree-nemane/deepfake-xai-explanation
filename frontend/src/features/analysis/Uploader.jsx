import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Loader2, Upload, Music, AlertCircle } from 'lucide-react';

const Uploader = ({ file, onFileChange, onAnalyze, isAnalyzing, progress, error }) => {
  const stageRows = progress?.stages?.length ? progress.stages : [];
  const progressPercent = Math.max(0, Math.min(Number(progress?.percent) || 0, 100));

  return (
    <div className="flex flex-col items-center justify-center py-12">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl"
      >
        <div 
          className={`glass glass-hover p-12 text-center cursor-pointer border-dashed border-2 ${file ? 'border-primary' : 'border-border'}`}
          onClick={() => document.getElementById('audio-input').click()}
        >
          <input 
            type="file" 
            id="audio-input" 
            hidden 
            onChange={onFileChange} 
            accept=".wav,.mp3" 
          />
          
          <div className="flex flex-col items-center">
            {file ? (
              <Music size={64} className="text-primary mb-6" />
            ) : (
              <Upload size={64} className="text-muted mb-6" />
            )}
            
            <h2 className="text-2xl font-bold mb-2">
              {file ? file.name : 'Upload Forensic Evidence'}
            </h2>
            <p className="text-muted mb-8 max-w-md mx-auto">
              Select a .wav or .mp3 file for deep neural and acoustic investigation.
            </p>
            
            {file && !isAnalyzing && (
              <button 
                className="btn btn-primary px-10 py-3"
                onClick={(e) => { e.stopPropagation(); onAnalyze(); }}
              >
                Run Forensic Scan
              </button>
            )}
          </div>
        </div>

        {isAnalyzing && (
          <div className="analysis-progress-panel mt-12" aria-busy="true" aria-live="polite">
            <div className="analysis-progress-header">
              <div className="flex justify-center">
                <div className="pulse-dot w-12 h-12 bg-primary" aria-hidden />
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">{progress?.message || 'Starting forensic analysis'}</h3>
                <p className="text-muted">
                  {progress?.status === 'queued'
                    ? 'Waiting for the backend analysis job to start.'
                    : 'Receiving live pipeline stage updates from the backend.'}
                </p>
                {!progress?.stages?.length && (
                  <p className="analysis-stage-placeholder">Pipeline stages will appear as the backend emits progress…</p>
                )}
              </div>
            </div>
            
            <div className="w-full bg-white/5 h-1 rounded-full mt-8 overflow-hidden">
              <motion.div 
                className="bg-primary h-full"
                animate={{ width: `${progressPercent}%` }}
                transition={{ duration: 0.35, ease: "easeOut" }}
              />
            </div>
            <div className="analysis-progress-percent">{Math.round(progressPercent)}%</div>

            <div className="analysis-stage-list">
              {stageRows.length > 0 ? (
                stageRows.map((stage) => (
                  <div key={stage.id} className={`analysis-stage-row stage-${stage.status}`}>
                    {stage.status === 'complete' ? (
                      <CheckCircle2 size={16} />
                    ) : stage.status === 'running' || stage.status === 'queued' ? (
                      <Loader2 size={16} className="stage-spin" />
                    ) : (
                      <Circle size={16} />
                    )}
                    <span>{stage.label}</span>
                  </div>
                ))
              ) : (
                <div className="analysis-stage-row stage-pending">
                  <Loader2 size={16} className="stage-spin" />
                  <span>Connecting to analysis stream…</span>
                </div>
              )}
            </div>
          </div>
        )}

        {error && (
          <div className="mt-8 glass p-4 border-error/20 flex items-center gap-3 text-error">
            <AlertCircle size={20} />
            <span className="text-sm font-medium">{error}</span>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Uploader;

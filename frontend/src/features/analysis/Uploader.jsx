import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle2, 
  Circle, 
  Loader2, 
  Upload, 
  AlertCircle, 
  FileAudio, 
  HardDrive,
  Cpu,
  ArrowRight,
  AlertTriangle
} from 'lucide-react';

const formatFileSize = (bytes) => {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const Uploader = ({ file, onFileChange, onAnalyze, isAnalyzing, progress, error, onLoadSample }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const stageRows = progress?.stages?.length ? progress.stages : [];
  const progressPercent = Math.max(0, Math.min(Number(progress?.percent) || 0, 100));

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      onFileChange({ target: { files: [droppedFile] } });
    }
  }, [onFileChange]);

  return (
    <div className="flex flex-col items-center justify-center py-6 w-full max-w-2xl mx-auto">
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full"
      >
        {/* Upload Drop Zone */}
        <div 
          className={`relative glass glass-hover p-10 text-center cursor-pointer ${
            isDragOver ? 'dropzone-active' : ''
          }`}
          style={{
            borderStyle: 'dashed',
            borderWidth: '2px',
            borderColor: isDragOver ? 'var(--primary)' : file ? 'var(--primary)' : 'var(--border)'
          }}
          onClick={() => !isAnalyzing && document.getElementById('audio-input').click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          role="button"
          tabIndex={0}
          aria-label="Upload audio evidence"
        >
          {/* Corner Crosshair Brackets */}
          <div className="corner-bracket corner-tl" />
          <div className="corner-bracket corner-tr" />
          <div className="corner-bracket corner-bl" />
          <div className="corner-bracket corner-br" />

          <input 
            type="file" 
            id="audio-input" 
            hidden 
            onChange={onFileChange} 
            accept=".wav,.flac,.mp3,.ogg" 
            disabled={isAnalyzing}
          />
          
          <div className="flex flex-col items-center">
            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 transition-colors ${
              file 
                ? 'bg-primary/20 text-primary' 
                : isDragOver 
                ? 'bg-primary/20 text-primary' 
                : 'bg-white/5 text-muted'
            }`}>
              {file ? <FileAudio size={32} /> : <Upload size={28} />}
            </div>
            
            <h2 className="text-xl font-bold mb-1.5 text-white">
              {isDragOver 
                ? 'Release Evidence File to Ingest' 
                : file 
                ? file.name 
                : 'Upload Forensic Audio Evidence'}
            </h2>

            {file ? (
              <div className="flex items-center gap-3 text-xs text-muted mb-6 flex-wrap justify-center">
                <span className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1 rounded border border-white/5">
                  <HardDrive size={12} className="text-primary" />
                  {formatFileSize(file.size)}
                </span>
                <span className="bg-white/5 px-2.5 py-1 rounded border border-white/5 uppercase text-white font-mono">
                  {file.name.split('.').pop() || 'AUDIO'}
                </span>
                <span className="text-primary font-medium">Ready for Analysis</span>
              </div>
            ) : (
              <p className="text-xs text-muted mb-6 max-w-md mx-auto leading-relaxed">
                Drag and drop your audio recording or click to browse. Supports high-resolution <strong className="text-white">WAV</strong>, <strong className="text-white">FLAC</strong>, <strong className="text-white">MP3</strong>, and <strong className="text-white">OGG</strong>.
              </p>
            )}

            {/* Action Buttons inside Drop Zone when file is loaded */}
            {file && !isAnalyzing && (
              <div className="flex items-center gap-3 mt-2" onClick={(e) => e.stopPropagation()}>
                <button 
                  className="btn btn-primary px-6 py-2.5 text-sm font-semibold flex items-center gap-2"
                  onClick={onAnalyze}
                >
                  <Cpu size={15} />
                  <span>Execute Forensic Analysis</span>
                  <ArrowRight size={14} />
                </button>
                <button 
                  className="btn btn-ghost px-4 py-2.5 text-xs"
                  onClick={() => document.getElementById('audio-input').click()}
                >
                  Change File
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Quick Demo Audio Specimens (Instant 1-Click Verification) */}
        {!file && !isAnalyzing && onLoadSample && (
          <div className="glass p-4 rounded-xl mt-4 flex items-center justify-between gap-3 flex-wrap">
            <div className="flex items-center gap-2">
              <div className="pulse-dot" style={{ background: 'var(--primary)' }} />
              <span className="text-xs text-muted font-medium">Quick Forensic Specimens:</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => onLoadSample('fake1.wav')}
                className="specimen-btn specimen-fake"
                title="Test detection against a known synthesized clone"
              >
                <AlertTriangle size={13} className="text-error" />
                <span>Synthetic Clone</span>
              </button>
              <button
                type="button"
                onClick={() => onLoadSample('adi.wav')}
                className="specimen-btn specimen-real"
                title="Test authenticity verification against natural speech"
              >
                <CheckCircle2 size={13} className="text-success" />
                <span>Authentic Speech</span>
              </button>
            </div>
          </div>
        )}

        {/* Error Notification */}
        <AnimatePresence>
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-6 glass p-4 border-error/20 flex items-start gap-3 text-error rounded-xl"
            >
              <AlertCircle size={18} className="shrink-0 mt-0.5" />
              <div className="flex-1 text-xs">
                <p className="font-bold mb-0.5 text-error">Forensic Ingestion Error</p>
                <p className="text-muted leading-relaxed">{error}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Multistage Pipeline Progress */}
        <AnimatePresence>
          {isAnalyzing && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="analysis-progress-panel mt-6"
              aria-busy="true"
              aria-live="polite"
            >
              <div className="analysis-progress-header">
                <div className="flex justify-center">
                  <div className="pulse-dot w-8 h-8 bg-primary" aria-hidden />
                </div>
                <div>
                  <h3 className="text-base font-bold mb-0.5 text-white">
                    {progress?.stage ? `Processing: ${progress.stage}` : progress?.message || 'Executing Forensic Analysis…'}
                  </h3>
                  <p className="text-xs text-muted">
                    {progress?.status === 'queued'
                      ? 'Waiting for the forensic worker to initialize…'
                      : progress?.message || 'Receiving live multi-agent consensus updates…'}
                  </p>
                </div>
                <div className="analysis-progress-percent">
                  {Math.round(progressPercent)}%
                </div>
              </div>

              {/* Progress Bar */}
              <div className="analysis-progress-bar">
                <motion.div 
                  className="analysis-progress-fill"
                  style={{ width: `${progressPercent}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>

              {/* Stage Checklist */}
              <div className="analysis-stage-list">
                {stageRows.length > 0 ? (
                  stageRows.map((st) => (
                    <div key={st.id} className={`analysis-stage-row stage-${st.status}`}>
                      {st.status === 'complete' ? (
                        <CheckCircle2 size={15} className="text-success" />
                      ) : st.status === 'running' || st.status === 'queued' ? (
                        <Loader2 size={15} className="stage-spin text-primary" />
                      ) : (
                        <Circle size={15} className="text-muted" />
                      )}
                      <span>{st.label}</span>
                    </div>
                  ))
                ) : (
                  <div className="analysis-stage-row stage-running">
                    <Loader2 size={15} className="stage-spin text-primary" />
                    <span>Connecting to forensic analysis stream…</span>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default Uploader;

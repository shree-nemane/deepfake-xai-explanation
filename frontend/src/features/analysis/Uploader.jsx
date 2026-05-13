import React from 'react';
import { motion } from 'framer-motion';
import { Upload, Music, AlertCircle } from 'lucide-react';

const Uploader = ({ file, onFileChange, onAnalyze, isAnalyzing, error }) => {
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
          <div className="mt-12 text-center">
            <div className="flex justify-center mb-6">
              <div className="pulse-dot w-12 h-12 bg-primary"></div>
            </div>
            <h3 className="text-xl font-bold mb-2">Analyzing Forensic Markers</h3>
            <p className="text-muted">Extracting features, calculating anomaly scores, and generating XAI maps...</p>
            
            <div className="w-full bg-white/5 h-1 rounded-full mt-8 overflow-hidden">
              <motion.div 
                className="bg-primary h-full"
                animate={{ width: ['0%', '30%', '60%', '90%', '95%'] }}
                transition={{ duration: 10, ease: "easeInOut" }}
              />
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

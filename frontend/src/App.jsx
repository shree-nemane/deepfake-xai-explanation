import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import axios from 'axios';

// Layout Components
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';

// Feature Components
import Hero from './features/analysis/Hero';
import Uploader from './features/analysis/Uploader';
import Dashboard from './features/analysis/Dashboard';
import History from './features/history/History';
import Analytics from './features/analysis/Analytics';

const API_BASE = 'http://localhost:8000';

const App = () => {
  const [activeTab, setActiveTab] = useState('investigate');
  const [file, setFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showUploader, setShowUploader] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
      setError(null);
    }
  };

  const analyzeAudio = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/analyze/`, formData);
      setResult(response.data);
      setActiveTab('dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please check if the backend is running.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleViewReport = async (report) => {
    try {
      setIsAnalyzing(true);
      const response = await axios.get(`${API_BASE}/analyze/${report.id}`);
      setResult(response.data);
      setActiveTab('dashboard');
    } catch (err) {
      console.error('Failed to fetch full report details:', err);
      setError('Could not load full report details.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetInvestigation = () => {
    setResult(null);
    setFile(null);
    setShowUploader(true);
    setActiveTab('investigate');
  };

  return (
    <div className="app-layout">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="main-content">
        <div className="content-wrapper">
          <Header title={
            activeTab === 'investigate' ? 'Forensic Investigation' :
            activeTab === 'dashboard' ? 'Analysis Dashboard' :
            activeTab === 'history' ? 'Audit History' : 'Intelligence Suite'
          } />

          <AnimatePresence mode="wait">
            {activeTab === 'investigate' && (
              <motion.div 
                key="investigate"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                {!showUploader ? (
                  <Hero onStart={() => setShowUploader(true)} />
                ) : (
                  <Uploader 
                    file={file} 
                    onFileChange={handleFileChange} 
                    onAnalyze={analyzeAudio}
                    isAnalyzing={isAnalyzing}
                    error={error}
                  />
                )}
              </motion.div>
            )}

            {activeTab === 'dashboard' && result && (
              <motion.div 
                key="dashboard"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
              >
                <Dashboard result={result} onReset={resetInvestigation} />
              </motion.div>
            )}

            {activeTab === 'history' && (
              <motion.div 
                key="history"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <History onViewReport={handleViewReport} />
              </motion.div>
            )}

            {activeTab === 'analytics' && (
              <motion.div 
                key="analytics"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Analytics />
              </motion.div>
            )}
          </AnimatePresence>

          <footer className="mt-auto pt-10 border-t border-white/5 text-center text-[10px] text-muted">
            © 2026 Deepfake Forensic AI — Professional Investigation Suite
          </footer>
        </div>
      </main>
    </div>
  );
};

export default App;

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  History as HistoryIcon, 
  ChevronRight, 
  ShieldAlert,
  ShieldCheck,
  Calendar,
  Inbox
} from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const History = ({ onViewReport }) => {
  const [reports, setReports] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${API_BASE}/analyze/history`);
        setReports(response.data);
      } catch (err) {
        console.error('Failed to fetch history:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHistory();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="pulse-dot w-8 h-8 bg-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <HistoryIcon size={24} className="text-primary" />
          Forensic Audit History
        </h2>
        <div className="flex items-center gap-2">
          <span className="status-pill" style={{ background: 'var(--primary-soft)', color: 'var(--primary-light)', border: '1px solid rgba(99,102,241,0.2)' }}>
            {reports.length} {reports.length === 1 ? 'Report' : 'Reports'}
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {reports.length === 0 ? (
          <div className="glass empty-state">
            <div className="empty-state-icon">
              <Inbox size={36} className="text-primary" style={{ opacity: 0.6 }} />
            </div>
            <h3 className="text-lg font-bold mb-2">No Investigations Yet</h3>
            <p className="text-sm text-muted max-w-md">
              Your forensic audit history is empty. Upload an audio file and run your first investigation to see results here.
            </p>
          </div>
        ) : (
          reports.map((report, i) => (
            <motion.div 
              key={report.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04 }}
              className={`glass glass-hover history-card p-4 flex items-center justify-between group cursor-pointer ${report.risk_score > 50 ? 'history-card-danger' : 'history-card-safe'}`}
              onClick={() => onViewReport(report)}
            >
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${report.risk_score > 50 ? 'bg-error/10 text-error' : 'bg-success/10 text-success'}`}>
                  {report.risk_score > 50 ? <ShieldAlert size={24} /> : <ShieldCheck size={24} />}
                </div>
                
                <div>
                  <h3 className="text-sm font-bold truncate" style={{ maxWidth: '320px' }}>{report.filename}</h3>
                  <div className="flex items-center gap-3 text-[10px] text-muted font-medium uppercase mt-1">
                    <span className="flex items-center gap-1"><Calendar size={10} /> {new Date(report.created_at).toLocaleDateString()}</span>
                    <span className="w-1 h-1 rounded-full bg-white/20"></span>
                    <span>Risk: {Math.round(report.risk_score)}%</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className={`text-xs font-black uppercase ${report.risk_score > 50 ? 'text-error' : 'text-success'}`}>
                    {report.prediction}
                  </div>
                  <div className="text-[10px] text-muted">Confidence: {Math.round(report.confidence * 100)}%</div>
                </div>
                
                <div className="w-8 h-8 flex items-center justify-center text-muted group-hover:text-primary transition-colors">
                  <ChevronRight size={20} />
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default History;

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, Activity, PieChart, BarChart3, TrendingUp, AlertTriangle } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const Analytics = () => {
  const [stats, setStats] = useState({
    total: 0,
    fakes: 0,
    real: 0,
    avgConfidence: 0,
    avgRisk: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API_BASE}/analyze/history`);
        const reports = response.data;
        
        const fakes = reports.filter(r => r.prediction.toLowerCase().includes('fake') || r.risk_score > 50).length;
        const total = reports.length;
        const avgConfidence = total > 0 ? reports.reduce((acc, r) => acc + r.confidence, 0) / total : 0;
        const avgRisk = total > 0 ? reports.reduce((acc, r) => acc + r.risk_score, 0) / total : 0;

        setStats({
          total,
          fakes,
          real: total - fakes,
          avgConfidence: Math.round(avgConfidence * 100),
          avgRisk: Math.round(avgRisk)
        });
      } catch (err) {
        console.error('Failed to fetch analytics:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="pulse-dot w-8 h-8 bg-primary"></div>
      </div>
    );
  }

  const cards = [
    { title: 'Total Scanned', value: stats.total, icon: Activity, color: 'text-primary' },
    { title: 'Manipulated Found', value: stats.fakes, icon: AlertTriangle, color: 'text-error' },
    { title: 'Authentic Verified', value: stats.real, icon: Shield, color: 'text-success' },
    { title: 'Avg. Confidence', value: `${stats.avgConfidence}%`, icon: TrendingUp, color: 'text-warning' },
  ];

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-black tracking-tight">Forensic Intelligence Summary</h2>
        <p className="text-muted">Aggregate data from the last {stats.total} forensic investigations.</p>
      </div>

      <div className="grid-container">
        {cards.map((card, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="span-3 glass p-6 flex flex-col gap-4"
          >
            <div className={`p-3 rounded-xl bg-white/5 w-fit ${card.color}`}>
              <card.icon size={24} />
            </div>
            <div>
              <div className="text-xs font-bold uppercase text-muted tracking-widest mb-1">{card.title}</div>
              <div className="text-4xl font-black">{card.value}</div>
            </div>
          </motion.div>
        ))}

        <div className="span-8 glass p-8 min-h-[300px] flex flex-col justify-center items-center text-center">
            <PieChart size={48} className="text-muted mb-4 opacity-20" />
            <h3 className="text-lg font-bold mb-2">Detection Distribution</h3>
            <p className="text-sm text-muted max-w-sm">
                Statistical breakdown of forensic verdicts across the investigative pipeline.
                (Visual chart integration pending full dataset).
            </p>
        </div>

        <div className="span-4 glass p-8 flex flex-col gap-6">
            <h3 className="text-sm font-bold uppercase tracking-widest text-primary">System Health</h3>
            <div className="flex flex-col gap-4">
                <div className="flex justify-between items-center text-xs">
                    <span className="text-muted">Engine Version</span>
                    <span className="font-mono">ConvNext-Tiny-V1</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                    <span className="text-muted">XAI Pipeline</span>
                    <span className="text-success font-bold">Operational</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                    <span className="text-muted">Persistence Engine</span>
                    <span className="text-success font-bold">Active</span>
                </div>
            </div>
            <div className="mt-auto glass bg-primary/10 p-4 rounded-xl border border-primary/20">
                <div className="text-[10px] uppercase font-black text-primary mb-1">Global Threat Level</div>
                <div className="text-xl font-black">{stats.avgRisk > 50 ? 'HIGH' : 'MODERATE'}</div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;

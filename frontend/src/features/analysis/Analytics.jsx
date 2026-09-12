import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, Activity, TrendingUp, AlertTriangle } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const CHART_COLORS = {
  real: '#10b981',
  fake: '#f43f5e',
  inconclusive: '#f59e0b',
  primary: '#6366f1',
};

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass p-3 rounded-xl shadow-lg border border-white/5" style={{ minWidth: '120px' }}>
      <p className="text-xs font-bold mb-1" style={{ color: payload[0].payload.fill || 'var(--text)' }}>
        {payload[0].name}
      </p>
      <p className="text-sm font-bold text-white">{payload[0].value}</p>
    </div>
  );
};

const Analytics = () => {
  const [stats, setStats] = useState({
    total: 0,
    fakes: 0,
    real: 0,
    inconclusive: 0,
    avgConfidence: 0,
    avgRisk: 0,
    confidenceBuckets: [],
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API_BASE}/analyze/history`);
        const reports = response.data;
        
        const fakes = reports.filter(r => r.prediction?.toLowerCase().includes('fake') || r.risk_score > 50).length;
        const total = reports.length;
        const realCount = total - fakes;
        const avgConfidence = total > 0 ? reports.reduce((acc, r) => acc + r.confidence, 0) / total : 0;
        const avgRisk = total > 0 ? reports.reduce((acc, r) => acc + r.risk_score, 0) / total : 0;

        // Build confidence distribution buckets
        const buckets = [
          { range: '0-25%', count: 0, fill: CHART_COLORS.inconclusive },
          { range: '25-50%', count: 0, fill: CHART_COLORS.inconclusive },
          { range: '50-75%', count: 0, fill: CHART_COLORS.primary },
          { range: '75-100%', count: 0, fill: CHART_COLORS.real },
        ];
        reports.forEach(r => {
          const c = (r.confidence || 0) * 100;
          if (c < 25) buckets[0].count++;
          else if (c < 50) buckets[1].count++;
          else if (c < 75) buckets[2].count++;
          else buckets[3].count++;
        });

        setStats({
          total,
          fakes,
          real: realCount,
          inconclusive: 0,
          avgConfidence: Math.round(avgConfidence * 100),
          avgRisk: Math.round(avgRisk),
          confidenceBuckets: buckets,
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

  const pieData = [
    { name: 'Authentic', value: stats.real, fill: CHART_COLORS.real },
    { name: 'Manipulated', value: stats.fakes, fill: CHART_COLORS.fake },
  ].filter(d => d.value > 0);

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
        <p className="text-muted">Aggregate data from {stats.total} forensic investigation{stats.total !== 1 ? 's' : ''}.</p>
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

        <div className="span-8 glass p-8 chart-card">
          <h3 className="text-sm font-bold uppercase tracking-widest text-primary mb-6 w-full text-left">Detection Distribution</h3>
          {stats.total > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={4}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={index} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  verticalAlign="bottom"
                  iconType="circle"
                  iconSize={8}
                  formatter={(value) => <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex flex-col items-center justify-center w-full" style={{ height: '250px' }}>
              <p className="text-sm text-muted">No data available yet. Run your first investigation.</p>
            </div>
          )}
        </div>

        <div className="span-4 glass p-8 flex flex-col gap-6">
          <h3 className="text-sm font-bold uppercase tracking-widest text-primary">System Health</h3>
          <div className="flex flex-col gap-4">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted">Engine Version</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>ConvNext-Tiny-V1</span>
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
          <div className="mt-auto glass bg-primary/10 p-4 rounded-xl border border-primary" style={{ borderColor: 'rgba(99,102,241,0.2)' }}>
            <div className="text-[10px] uppercase font-black text-primary mb-1">Global Threat Level</div>
            <div className="text-xl font-black">{stats.avgRisk > 50 ? 'HIGH' : stats.total === 0 ? 'N/A' : 'MODERATE'}</div>
          </div>
        </div>

        <div className="span-12 glass p-8">
          <h3 className="text-sm font-bold uppercase tracking-widest text-primary mb-6">Confidence Distribution</h3>
          {stats.total > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={stats.confidenceBuckets} barCategoryGap="20%">
                <XAxis
                  dataKey="range"
                  tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                  tickLine={false}
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                  tickLine={false}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                <Bar dataKey="count" name="Reports" radius={[6, 6, 0, 0]}>
                  {stats.confidenceBuckets.map((entry, index) => (
                    <Cell key={index} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center w-full" style={{ height: '220px' }}>
              <p className="text-sm text-muted">Run investigations to populate confidence distribution.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Analytics;

import React from 'react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, 
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell 
} from 'recharts';

export const RadarFeatureChart = ({ data }) => (
  <div className="chart-container">
    <ResponsiveContainer>
      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
        <PolarGrid stroke="rgba(255,255,255,0.05)" />
        <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 500 }} />
        <Radar 
          name="Anomaly Score" 
          dataKey="A" 
          stroke="var(--primary)" 
          fill="var(--primary)" 
          fillOpacity={0.3} 
        />
        <Tooltip 
          contentStyle={{ 
            background: 'rgba(17, 24, 39, 0.95)', 
            border: '1px solid rgba(255,255,255,0.1)', 
            borderRadius: '12px',
            fontSize: '12px'
          }} 
        />
      </RadarChart>
    </ResponsiveContainer>
  </div>
);

export const ShapBarChart = ({ data }) => (
  <div className="chart-container">
    <ResponsiveContainer>
      <BarChart layout="vertical" data={data} margin={{ left: 20 }}>
        <XAxis type="number" hide />
        <YAxis 
          type="category" 
          dataKey="name" 
          stroke="#94a3b8" 
          fontSize={10} 
          width={120}
          tick={{ fontWeight: 500 }}
        />
        <Tooltip 
          cursor={{ fill: 'rgba(255,255,255,0.03)' }}
          contentStyle={{ 
            background: 'rgba(17, 24, 39, 0.95)', 
            border: '1px solid rgba(255,255,255,0.1)', 
            borderRadius: '12px',
            fontSize: '12px'
          }}
        />
        <Bar dataKey="score" radius={[0, 4, 4, 0]}>
          {data.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={entry.score > 50 ? 'var(--error)' : 'var(--primary)'} 
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  </div>
);

export const TimelineChart = ({ data }) => (
  <div className="chart-container" style={{ height: '180px' }}>
    <ResponsiveContainer>
      <BarChart data={data}>
        <XAxis dataKey="time" hide />
        <Tooltip 
          contentStyle={{ 
            background: 'rgba(17, 24, 39, 0.95)', 
            border: '1px solid rgba(255,255,255,0.1)', 
            borderRadius: '12px',
            fontSize: '12px'
          }}
        />
        <Bar dataKey="zcr" fill="var(--primary)" radius={[2, 2, 0, 0]} />
        <Bar dataKey="timbre_instability" fill="var(--secondary)" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  </div>
);

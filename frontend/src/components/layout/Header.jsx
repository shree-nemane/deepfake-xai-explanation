import React from 'react';
import { Cpu } from 'lucide-react';

const Header = ({ title }) => {
  return (
    <header className="flex justify-between items-center mb-8 pb-4 border-b border-white/5">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        <p className="text-muted text-xs mt-1" style={{ letterSpacing: '0.02em' }}>
          Consensus-Based Explainable Forensic Audio Intelligence
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-[10px] text-muted" style={{ opacity: 0.6 }}>
          <Cpu size={12} />
          <span className="font-medium">4-Agent Panel</span>
        </div>
        <div className="status-pill status-online">
          <div className="pulse-dot" />
          System Live
        </div>
      </div>
    </header>
  );
};

export default Header;

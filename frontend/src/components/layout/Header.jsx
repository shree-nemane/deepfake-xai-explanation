import React from 'react';

const Header = ({ title }) => {
  return (
    <header className="flex justify-between items-center mb-8 pb-4 border-b border-white/5">
      <div>
        <h1 className="text-2xl font-bold">{title}</h1>
        <p className="text-muted text-xs">Deepfake Forensic Intelligence & XAI Dashboard</p>
      </div>

      <div className="flex items-center gap-4">
        <div className="status-pill status-online">
          <div className="pulse-dot"></div>
          System Live
        </div>
      </div>
    </header>
  );
};

export default Header;

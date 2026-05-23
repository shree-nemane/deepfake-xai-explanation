import React from 'react';

const ConsensusPanel = ({ consensus, agents }) => {
  const agentEntries = Object.entries(agents || {});

  return (
    <div className="consensus-panel glass p-6">
      <h3 className="panel-title">Forensic Consensus</h3>

      <div className="consensus-metric">
        <span>Final Verdict</span>
        <strong>{consensus?.verdict?.toUpperCase() || 'UNKNOWN'}</strong>
      </div>
      <div className="consensus-metric">
        <span>Confidence</span>
        <strong>{((consensus?.confidence || 0) * 100).toFixed(1)}%</strong>
      </div>
      <div className="consensus-metric">
        <span>Agreement</span>
        <strong>{((consensus?.convergence_strength || 0) * 100).toFixed(1)}%</strong>
      </div>
      <div className="consensus-metric">
        <span>Fake Probability</span>
        <strong>{((consensus?.fake_probability || 0) * 100).toFixed(1)}%</strong>
      </div>
      <div className="consensus-metric">
        <span>Real Probability</span>
        <strong>{((consensus?.real_probability || 0) * 100).toFixed(1)}%</strong>
      </div>
      <div className="consensus-metric">
        <span>Decision Threshold</span>
        <strong>{((consensus?.decision_threshold || 0.6) * 100).toFixed(0)}%</strong>
      </div>

      <div className="agent-vote-list">
        {agentEntries.map(([name, data]) => (
          <div key={name} className="agent-vote-row">
            <span>{data.name || name}</span>
            <b className={`vote-${data.verdict}`}>{data.verdict}</b>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConsensusPanel;

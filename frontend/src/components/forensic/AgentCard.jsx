import React from 'react';

const AgentCard = ({ agent }) => {
  const isFake = agent.verdict === 'fake';
  const isInconclusive = agent.verdict === 'inconclusive';
  
  return (
    <div className={`agent-card ${isFake ? 'alert-fake' : isInconclusive ? 'alert-warning' : 'alert-real'}`}>
      <h4>{agent.name.toUpperCase()}</h4>
      <div className="agent-stats">
        <p>Verdict: <strong>{agent.verdict.toUpperCase()}</strong></p>
        <p>Confidence: {(agent.confidence * 100).toFixed(1)}%</p>
        <p>Uncertainty: {(agent.uncertainty * 100).toFixed(1)}%</p>
      </div>
      <div className="agent-evidence">
        <h5>Key Evidence:</h5>
        <ul>
          {Object.entries(agent.evidence || {}).map(([key, value]) => (
            <li key={key}>{key}: {value.toString()}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default AgentCard;

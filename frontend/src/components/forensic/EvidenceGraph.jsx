import React from 'react';

const EvidenceGraph = ({ agents, consensus, diagnostics }) => {
  const agentEntries = Object.entries(agents || {});
  const votingEntries = agentEntries.filter(([name]) => name !== 'reliability');
  const voteCounts = votingEntries.reduce(
    (acc, [, agent]) => {
      const verdict = agent.verdict || 'inconclusive';
      acc[verdict] = (acc[verdict] || 0) + 1;
      return acc;
    },
    { fake: 0, real: 0, inconclusive: 0, reliable: 0, unreliable: 0 }
  );

  if (!agentEntries.length) {
    return <div className="evidence-graph">No evidence graph available.</div>;
  }

  return (
    <div className="evidence-graph">
      <h3>Evidence Relationship Map</h3>
      <div className="graph-summary">
        <div>
          <span>Consensus</span>
          <strong className={`vote-${consensus?.verdict}`}>{consensus?.verdict || 'unknown'}</strong>
        </div>
        <div>
          <span>Decision Reliability</span>
          <strong>{Math.round((diagnostics?.decision_reliability || 0) * 100)}%</strong>
        </div>
        <div>
          <span>Agents</span>
          <strong>{agentEntries.length}</strong>
        </div>
      </div>

      <div className="vote-pressure-grid">
        {['fake', 'real', 'inconclusive'].map((verdict) => {
          const count = voteCounts[verdict] || 0;
          const width = votingEntries.length ? (count / votingEntries.length) * 100 : 0;

          return (
            <div key={verdict} className="vote-pressure-row">
              <span>{verdict}</span>
              <div className="vote-pressure-track">
                <b className={`pressure-${verdict}`} style={{ width: `${width}%` }} />
              </div>
              <strong>{count}</strong>
            </div>
          );
        })}
      </div>

      <div className="node-list">
        {agentEntries.map(([name, agent]) => (
          <span key={name} className={`graph-node node-${agent.verdict}`}>
            {agent.name || name}: {Math.round((agent.confidence || 0) * 100)}%
          </span>
        ))}
      </div>

      {diagnostics?.warnings?.length > 0 && (
        <div className="graph-warning-strip">
          {diagnostics.warnings.length} reliability note(s) require analyst review.
        </div>
      )}
    </div>
  );
};

export default EvidenceGraph;

import React from 'react';
import NarrativeSections from './NarrativeSections';
import ContradictionAlerts from './ContradictionAlerts';
import EvidenceBreakdownTable from './EvidenceBreakdownTable';

const ForensicExplanationTab = ({ result }) => (
  <div className="forensic-explanation-tab flex flex-col gap-6">
    <NarrativeSections result={result} />
    <ContradictionAlerts result={result} />
    <EvidenceBreakdownTable result={result} />
  </div>
);

export default ForensicExplanationTab;

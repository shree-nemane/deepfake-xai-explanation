import React from 'react';
import NarrativeSections from './NarrativeSections';
import ContradictionAlerts from './ContradictionAlerts';
import ShapContributionPanel from './ShapContributionPanel';
import CounterfactualPanel from './CounterfactualPanel';

const ForensicExplanationTab = ({ result }) => (
  <div className="forensic-explanation-tab flex flex-col gap-6">
    {/* Case Narrative Sections */}
    <NarrativeSections result={result} />

    {/* Contradiction & Splice Threats */}
    <ContradictionAlerts result={result} />

    {/* Exact Game-Theoretic SHAP & Counterfactual Sensitivity */}
    <div className="grid grid-cols-2 gap-6">
      <div className="glass p-6 rounded-xl">
        <ShapContributionPanel result={result} />
      </div>
      <div className="glass p-6 rounded-xl">
        <CounterfactualPanel result={result} />
      </div>
    </div>
  </div>
);

export default ForensicExplanationTab;

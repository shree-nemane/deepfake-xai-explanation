import React from 'react';

const DashboardViewTabs = ({ activeView, onChange }) => (
  <div className="dashboard-view-tabs" role="tablist" aria-label="Dashboard views">
    <button
      type="button"
      role="tab"
      aria-selected={activeView === 'overview'}
      className={`dashboard-tab ${activeView === 'overview' ? 'dashboard-tab-active' : ''}`}
      onClick={() => onChange('overview')}
    >
      Overview
    </button>
    <button
      type="button"
      role="tab"
      aria-selected={activeView === 'explanation'}
      className={`dashboard-tab ${activeView === 'explanation' ? 'dashboard-tab-active' : ''}`}
      onClick={() => onChange('explanation')}
    >
      Forensic Explanation
    </button>
  </div>
);

export default DashboardViewTabs;

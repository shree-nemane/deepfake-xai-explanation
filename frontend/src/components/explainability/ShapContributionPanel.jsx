import React, { useMemo } from 'react';
import { ShapBarChart } from '../../features/analysis/AnalysisCharts';

const ShapContributionPanel = ({ result }) => {
  const chartData = useMemo(() => {
    const averages = result?.xai?.shap_values?.summary?.average_values;
    if (!averages || typeof averages !== 'object') return [];

    return Object.entries(averages).map(([name, value]) => ({
      name,
      score: Math.abs(Number(value) || 0) * 100,
      raw: Number(value) || 0,
    }));
  }, [result]);

  const summary = result?.xai?.shap_summary;

  return (
    <section className="drawer-section">
      <h4 className="drawer-section-title">SHAP Contributions</h4>
      {chartData.length > 0 ? (
        <>
          {summary && <p className="drawer-caption">{summary}</p>}
          <div className="drawer-chart-wrap">
            <ShapBarChart data={chartData} />
          </div>
        </>
      ) : (
        <p className="drawer-empty">No Shapley attributions available for this report.</p>
      )}
    </section>
  );
};

export default ShapContributionPanel;

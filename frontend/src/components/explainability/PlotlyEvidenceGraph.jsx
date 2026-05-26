import React, { lazy, Suspense, useMemo } from 'react';

const Plot = lazy(() => import('react-plotly.js'));

const buildLayout = (positions) => {
  const xs = Object.values(positions).map((p) => p.x);
  const ys = Object.values(positions).map((p) => p.y);
  const pad = 0.8;

  return {
    autosize: false,
    width: 440,
    height: 300,
    margin: { l: 48, r: 16, t: 16, b: 40 },
    paper_bgcolor: 'rgba(15, 23, 42, 0)',
    plot_bgcolor: 'rgba(15, 23, 42, 0)',
    font: { color: '#94a3b8', family: 'Outfit, sans-serif', size: 11 },
    xaxis: {
      showgrid: false,
      zeroline: false,
      showticklabels: false,
      range: [Math.min(...xs, 0) - pad, Math.max(...xs, 1) + pad],
      fixedrange: true,
    },
    yaxis: {
      showgrid: true,
      gridcolor: 'rgba(255,255,255,0.06)',
      zeroline: false,
      tickmode: 'array',
      tickvals: [1, 2, 3, 4, 5, 6],
      ticktext: ['L1 Input', 'L2 Prep', 'L3 Agents', 'L4 Consensus', 'L5 XAI', 'L6 Verdict'],
      range: [0.4, 6.6],
      fixedrange: true,
    },
    showlegend: false,
    hovermode: 'closest',
    hoverlabel: {
      bgcolor: '#1e293b',
      bordercolor: 'rgba(255,255,255,0.15)',
      font: { color: '#f1f5f9', size: 11 },
    },
  };
};

const PlotlyEvidenceGraph = ({ evidenceGraph }) => {
  const { data, layout } = useMemo(() => {
    const nodes = evidenceGraph?.nodes || [];
    const edges = evidenceGraph?.edges || [];

    if (!nodes.length) {
      return { data: [], layout: buildLayout({ 0: { x: 0, y: 1 } }) };
    }

    const layerBuckets = {};
    nodes.forEach((node) => {
      const layer = Number(node.layer) || 1;
      if (!layerBuckets[layer]) layerBuckets[layer] = [];
      layerBuckets[layer].push(node);
    });

    const positions = {};
    Object.entries(layerBuckets).forEach(([, layerNodes]) => {
      const count = layerNodes.length;
      layerNodes.forEach((node, index) => {
        const x = count === 1 ? 0 : index - (count - 1) / 2;
        positions[node.id] = { x, y: Number(node.layer), label: node.label, type: node.type };
      });
    });

    const nodeTrace = {
      type: 'scatter',
      mode: 'markers+text',
      x: nodes.map((n) => positions[n.id]?.x ?? 0),
      y: nodes.map((n) => positions[n.id]?.y ?? Number(n.layer)),
      text: nodes.map((n) => n.label),
      textposition: 'top center',
      textfont: { size: 9, color: '#e2e8f0' },
      marker: {
        size: 12,
        color: nodes.map((n) => {
          if (n.type === 'threat_warning') return '#f43f5e';
          if (n.layer >= 5) return '#8b5cf6';
          if (n.layer >= 3) return '#6366f1';
          return '#10b981';
        }),
        line: { color: 'rgba(255,255,255,0.2)', width: 1 },
      },
      hovertemplate: '%{text}<br>%{customdata}<extra></extra>',
      customdata: nodes.map((n) => n.type),
    };

    const edgeX = [];
    const edgeY = [];
    edges.forEach((edge) => {
      const from = positions[edge.source];
      const to = positions[edge.target];
      if (!from || !to) return;
      edgeX.push(from.x, to.x, null);
      edgeY.push(from.y, to.y, null);
    });

    const edgeTrace = {
      type: 'scatter',
      mode: 'lines',
      x: edgeX,
      y: edgeY,
      line: { color: 'rgba(148, 163, 184, 0.45)', width: 1.5 },
      hoverinfo: 'skip',
    };

    return {
      data: [edgeTrace, nodeTrace],
      layout: buildLayout(positions),
    };
  }, [evidenceGraph]);

  if (!evidenceGraph?.nodes?.length) {
    return (
      <section className="drawer-section">
        <h4 className="drawer-section-title">Evidence Graph</h4>
        <p className="drawer-empty">No evidence graph available.</p>
      </section>
    );
  }

  return (
    <section className="drawer-section">
      <h4 className="drawer-section-title">Interactive Evidence Graph</h4>
      <div className="plotly-graph-wrap">
        <Suspense fallback={<p className="drawer-caption">Loading graph…</p>}>
          <Plot
            data={data}
            layout={layout}
            config={{
              displayModeBar: false,
              responsive: false,
              scrollZoom: false,
              doubleClick: false,
            }}
            style={{ width: '100%', height: '300px' }}
          />
        </Suspense>
      </div>
    </section>
  );
};

export default PlotlyEvidenceGraph;

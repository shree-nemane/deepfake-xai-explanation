import React from 'react';
import EvidenceGraph from '../forensic/EvidenceGraph';

class DrawerErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error) {
    console.error('Explainability drawer panel failed:', error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <section className="drawer-section">
          <h4 className="drawer-section-title">Evidence Graph (fallback)</h4>
          <p className="drawer-caption">
            Interactive Plotly graph could not load. Showing the static relationship map instead.
          </p>
          <EvidenceGraph
            evidenceGraph={this.props.evidenceGraph}
            agents={this.props.agents}
            consensus={this.props.consensus}
            diagnostics={this.props.diagnostics}
          />
        </section>
      );
    }
    return this.props.children;
  }
}

export default DrawerErrorBoundary;

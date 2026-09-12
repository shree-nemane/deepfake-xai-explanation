import React from 'react';
import { AlertTriangle, BarChart2, Brain, Gauge } from 'lucide-react';
import { collectDiagnosticWarnings, warningKey } from '../../utils/diagnostics';

const formatPercent = (value) => `${Math.round((Number(value) || 0) * 100)}%`;

const formatNumber = (value, digits = 3) => {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return '0';
  return numeric.toFixed(digits);
};

const severityLabel = (severity) => {
  if (severity === 'high') return 'High';
  if (severity === 'elevated') return 'Elevated';
  if (severity === 'low') return 'Low';
  return 'Nominal';
};

const SignalRow = ({ signal }) => {
  const riskScore = Math.min(Math.max(Number(signal.risk_score) || 0, 0), 1);

  return (
    <div className={`signal-row severity-${signal.severity || 'nominal'}`}>
      <div>
        <div className="signal-name">{signal.name}</div>
        <div className="signal-meta">
          Value {formatNumber(signal.value, 4)}
          {signal.threshold !== undefined && ` / threshold ${formatNumber(signal.threshold, 3)}`}
        </div>
      </div>
      <div className="signal-meter">
        <div className="signal-meter-track">
          <span style={{ width: `${riskScore * 100}%` }} />
        </div>
        <strong>{formatPercent(riskScore)}</strong>
      </div>
    </div>
  );
};

const FeatureAnalysisPanel = ({ featureAnalysis, preprocessing, diagnostics }) => {
  if (!featureAnalysis) return null;

  const prep = preprocessing || featureAnalysis.preprocessing || {};
  const acousticFeatures = featureAnalysis.acoustic_features || [];
  const neuralSignals = featureAnalysis.neural_signals || [];
  const warnings = collectDiagnosticWarnings(diagnostics);

  return (
    <section className="feature-analysis-panel">
      <div className="feature-section-header">
        <div>
          <h3 className="panel-title">Forensic Feature Telemetry</h3>
          <p className="feature-subtitle">
            Acoustic deviations and neural feature representations extracted across active speech segments.
          </p>
        </div>
        <div className={`review-pill review-${diagnostics?.review_level || 'moderate_trust'}`}>
          {diagnostics?.review_level?.replaceAll('_', ' ') || 'moderate trust'}
        </div>
      </div>

      <div className="feature-grid">
        {/* Evidence Intake Metrics */}
        <div className="feature-card" style={{ gridColumn: 'span 4' }}>
          <div className="feature-card-title">
            <Gauge size={16} /> Evidence Intake
          </div>
          <div className="stat-list">
            <span>Original duration <b>{formatNumber(prep.original_duration_sec, 2)}s</b></span>
            <span>Speech coverage <b>{formatPercent(prep.speech_coverage)}</b></span>
            <span>VAD segments <b>{prep.vad_segments ?? 0}</b></span>
            <span>Analyzed chunks <b>{prep.chunk_count ?? 0}</b></span>
          </div>
        </div>

        {/* Neural Signal Distribution */}
        <div className="feature-card" style={{ gridColumn: 'span 8' }}>
          <div className="feature-card-title">
            <Brain size={16} /> Neural Classifier Signals
          </div>
          <div className="signal-list">
            {neuralSignals.length ? (
              neuralSignals.map((signal) => (
                <SignalRow key={signal.name} signal={signal} />
              ))
            ) : (
              <p className="empty-note">Neural feature vectors nominal.</p>
            )}
          </div>
        </div>
      </div>

      <div className="feature-detail-grid">
        {/* Authoritative Acoustic Deviation Ranking */}
        <div className="feature-card feature-card-wide">
          <div className="feature-card-title">
            <BarChart2 size={16} /> Biological Vocal Tract Deviations (Z-Scores)
          </div>
          {acousticFeatures.length ? (
            <div className="feature-table">
              {acousticFeatures.slice(0, 6).map((feature) => (
                <div key={feature.feature} className="feature-row">
                  <div>
                    <strong>{feature.label}</strong>
                    <span>
                      z-score {formatNumber(feature.avg_z_score, 2)} | observed in {feature.occurrences} chunk(s)
                    </span>
                  </div>
                  <div className={`severity-badge severity-${feature.severity}`}>
                    {severityLabel(feature.severity)} {formatPercent(feature.avg_risk_score)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-note">No ranked acoustic deviations observed in speech baselines.</p>
          )}
        </div>

        {/* Analyst Notes & Decision Reliability */}
        <div className="feature-card">
          <div className="feature-card-title">
            <AlertTriangle size={16} /> Analyst Notes &amp; Integrity
          </div>
          {warnings.length ? (
            <ul className="warning-list">
              {warnings.map((warning, index) => (
                <li key={warningKey(warning, index)}>{warning}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-note">No reliability or calibration anomalies reported.</p>
          )}
          <div className="decision-score">
            <span>Decision reliability</span>
            <strong>{formatPercent(diagnostics?.decision_reliability)}</strong>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeatureAnalysisPanel;

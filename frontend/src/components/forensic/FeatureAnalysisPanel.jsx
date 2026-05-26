import React from 'react';
import { Activity, AlertTriangle, BarChart2, Brain, Gauge } from 'lucide-react';
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
  const quality = featureAnalysis.signal_quality || {};
  const acousticFeatures = featureAnalysis.acoustic_features || [];
  const neuralSignals = featureAnalysis.neural_signals || [];
  const warnings = collectDiagnosticWarnings(diagnostics);

  return (
    <section className="feature-analysis-panel">
      <div className="feature-section-header">
        <div>
          <h3 className="panel-title">Feature Analysis</h3>
          <p className="feature-subtitle">
            Distinct forensic signals extracted from preprocessing, signal quality, acoustic deviation, and neural agents.
          </p>
        </div>
        <div className={`review-pill review-${diagnostics?.review_level || 'moderate_trust'}`}>
          {diagnostics?.review_level?.replaceAll('_', ' ') || 'moderate trust'}
        </div>
      </div>

      <div className="feature-grid">
        <div className="feature-card">
          <div className="feature-card-title">
            <Gauge size={16} /> Intake
          </div>
          <div className="stat-list">
            <span>Original duration <b>{formatNumber(prep.original_duration_sec, 2)}s</b></span>
            <span>Speech coverage <b>{formatPercent(prep.speech_coverage)}</b></span>
            <span>VAD segments <b>{prep.vad_segments ?? 0}</b></span>
            <span>Chunks analyzed <b>{prep.chunk_count ?? 0}</b></span>
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-card-title">
            <Activity size={16} /> Signal Quality
          </div>
          <div className="stat-list">
            <span>SNR <b>{formatNumber(quality.snr_db, 1)} dB</b></span>
            <span>Clipping <b>{formatPercent(quality.clipping_ratio)}</b></span>
            <span>Flatness <b>{formatNumber(quality.spectral_flatness, 4)}</b></span>
            <span>Reliability <b>{formatPercent(quality.reliability_score)}</b></span>
          </div>
        </div>

        <div className="feature-card feature-card-wide">
          <div className="feature-card-title">
            <Brain size={16} /> Neural Signals
          </div>
          <div className="signal-list">
            {neuralSignals.map((signal) => (
              <SignalRow key={signal.name} signal={signal} />
            ))}
          </div>
        </div>
      </div>

      <div className="feature-detail-grid">
        <div className="feature-card feature-card-wide">
          <div className="feature-card-title">
            <BarChart2 size={16} /> Acoustic Deviation Ranking
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
            <p className="empty-note">No ranked acoustic deviations were produced for this sample.</p>
          )}
        </div>

        <div className="feature-card">
          <div className="feature-card-title">
            <AlertTriangle size={16} /> Analyst Notes
          </div>
          {warnings.length ? (
            <ul className="warning-list">
              {warnings.map((warning, index) => (
                <li key={warningKey(warning, index)}>{warning}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-note">No major reliability warnings were raised.</p>
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

import React, { useMemo } from 'react';
import { AlertTriangle } from 'lucide-react';

const SEVERITY_RANK = { high: 0, elevated: 1, medium: 2, low: 3, unknown: 4 };

const ContradictionAlerts = ({ result }) => {
  const { threats, diagnostics } = useMemo(() => {
    const threatRows = [];
    (result?.timeline || []).forEach((chunk, chunkIndex) => {
      (chunk.threat_warnings || []).forEach((warning, warningIndex) => {
        threatRows.push({
          id: `threat-${chunkIndex}-${warningIndex}`,
          kind: 'threat',
          type: warning.type || warning.threat_type || 'unknown',
          severity: warning.severity || 'unknown',
          description: warning.description || 'Threat warning detected.',
          start_time: chunk.start_time,
          end_time: chunk.end_time,
        });
      });
    });

    threatRows.sort(
      (a, b) => (SEVERITY_RANK[a.severity] ?? 99) - (SEVERITY_RANK[b.severity] ?? 99),
    );

    const normalizeWarning = (warning) => {
      if (typeof warning === 'string') {
        return { category: 'general', message: warning };
      }
      return {
        category: warning.category || 'general',
        message: warning.message || String(warning),
      };
    };

    const qualityRows = (result?.diagnostics?.quality_warnings || []).map((warning, index) => {
      const row = normalizeWarning(warning);
      return {
        id: `quality-${index}`,
        kind: 'quality',
        type: row.category,
        severity: 'info',
        description: row.message,
        start_time: null,
        end_time: null,
      };
    });

    const synthesisRows = (result?.diagnostics?.synthesis_warnings || []).map((warning, index) => {
      const row = normalizeWarning(warning);
      return {
        id: `synthesis-${index}`,
        kind: 'synthesis',
        type: row.category,
        severity: 'elevated',
        description: row.message,
        start_time: null,
        end_time: null,
      };
    });

    const fallbackRows = (result?.diagnostics?.warnings || []).map((warning, index) => {
      const row = normalizeWarning(warning);
      const kind = row.category === 'signal_quality' ? 'quality' : 'synthesis';
      return {
        id: `diag-${index}`,
        kind,
        type: row.category,
        severity: kind === 'quality' ? 'info' : 'elevated',
        description: row.message,
        start_time: null,
        end_time: null,
      };
    });

    const diagnosticRows =
      qualityRows.length || synthesisRows.length
        ? [...qualityRows, ...synthesisRows]
        : fallbackRows;

    return { threats: threatRows, diagnostics: diagnosticRows };
  }, [result]);

  const hasAlerts = threats.length > 0 || diagnostics.length > 0;

  return (
    <section className="explanation-section">
      <h3 className="panel-title flex items-center gap-2">
        <AlertTriangle size={18} /> Contradiction &amp; Threat Alerts
      </h3>

      {!hasAlerts ? (
        <p className="drawer-empty">No active contradiction warnings for this report.</p>
      ) : (
        <div className="threat-alert-list">
          {threats.map((row) => (
            <div key={row.id} className={`threat-alert severity-${row.severity}`}>
              <div className="threat-alert-header">
                <span className="threat-type">{row.type}</span>
                <span className="threat-severity">{row.severity}</span>
              </div>
              <p className="threat-description">{row.description}</p>
              <p className="threat-time">
                {row.start_time != null && row.end_time != null
                  ? `${row.start_time}s – ${row.end_time}s`
                  : 'Time range unavailable'}
              </p>
            </div>
          ))}
          {diagnostics.map((row) => (
            <div
              key={row.id}
              className={`threat-alert diagnostic-alert ${row.kind === 'quality' ? 'quality-alert' : 'synthesis-alert'}`}
            >
              <div className="threat-alert-header">
                <span className="threat-type">
                  {row.kind === 'quality' ? 'signal quality' : 'synthesis evidence'}
                </span>
                <span className="threat-severity">{row.severity}</span>
              </div>
              <p className="threat-description">{row.description}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export default ContradictionAlerts;

/** Normalize backend diagnostic warnings (string or { category, message }). */

export const formatDiagnosticWarning = (warning) => {
  if (warning == null) return '';
  if (typeof warning === 'string') return warning;
  if (typeof warning === 'object') {
    return warning.message || warning.text || JSON.stringify(warning);
  }
  return String(warning);
};

export const warningKey = (warning, index = 0) => {
  if (typeof warning === 'string') return `${index}-${warning.slice(0, 48)}`;
  if (warning && typeof warning === 'object') {
    return `${index}-${warning.category || 'warn'}-${(warning.message || '').slice(0, 48)}`;
  }
  return `warn-${index}`;
};

export const collectDiagnosticWarnings = (diagnostics) => {
  if (!diagnostics) return [];
  const quality = (diagnostics.quality_warnings || []).map(formatDiagnosticWarning);
  const synthesis = (diagnostics.synthesis_warnings || []).map(formatDiagnosticWarning);
  if (quality.length || synthesis.length) {
    return [...quality, ...synthesis];
  }
  return (diagnostics.warnings || []).map(formatDiagnosticWarning).filter(Boolean);
};

export const normalizeDiagnostics = (diagnostics) => {
  if (!diagnostics) return diagnostics;
  const warnings = collectDiagnosticWarnings(diagnostics);
  return {
    ...diagnostics,
    warnings,
    quality_warnings: (diagnostics.quality_warnings || []).map((w) =>
      typeof w === 'string' ? { category: 'signal_quality', message: w } : w,
    ),
    synthesis_warnings: (diagnostics.synthesis_warnings || []).map((w) =>
      typeof w === 'string' ? { category: 'synthesis_evidence', message: w } : w,
    ),
  };
};

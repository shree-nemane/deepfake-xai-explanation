import { getEventMeta, normalizeEventType } from './forensicLabels';

const AGENT_LABELS = {
  wavlm: 'WavLM semantic',
  convnext: 'ConvNext spectral',
  aasist: 'AASIST anti-spoof',
  acoustic: 'Acoustic biological',
};

export const buildChunkSuspicionSummary = (chunk, globalConsensus) => {
  if (!chunk) {
    return {
      headline: 'Select a timeline segment',
      bullets: ['Click a marker on the timeline to inspect mel spectrogram and per-agent evidence.'],
      severity: 'neutral',
    };
  }

  const meta = getEventMeta(chunk.event_type);
  const eventKey = normalizeEventType(chunk.event_type);
  const bullets = [];
  const confidence = Math.round((chunk.confidence || 0) * 100);
  const verdict = chunk.verdict || 'inconclusive';

  bullets.push(`${meta.label} · chunk verdict ${verdict} at ${confidence}% consensus confidence.`);

  const threats = chunk.threat_warnings || [];
  if (threats.length) {
    threats.forEach((t) => {
      bullets.push(`${t.type || t.threat_type}: ${t.description || 'Threat warning on this segment.'}`);
    });
  }

  const details = chunk.details || {};
  const splits = [];
  Object.entries(details).forEach(([agent, info]) => {
    if (!info || agent.startsWith('_')) return;
    const v = info.verdict || info.calibrated_verdict || 'inconclusive';
    const c = Math.round((info.calibrated_confidence ?? info.confidence ?? 0) * 100);
    splits.push(`${AGENT_LABELS[agent] || agent}: ${v} (${c}%)`);
  });
  if (splits.length) {
    bullets.push(`Agent panel: ${splits.join(' · ')}`);
  }

  if (eventKey === 'contradiction') {
    bullets.push('Why suspicious: calibrated agents disagree — treat as analyst-review, not auto-guilty.');
  } else if (eventKey === 'splice') {
    bullets.push('Why suspicious: temporal splice or partial-edit pattern in consensus events.');
  } else if (verdict === 'fake') {
    bullets.push('Why suspicious: chunk-level consensus leaned fake with converging agent votes.');
  } else if (verdict === 'inconclusive') {
    bullets.push('Why inconclusive: margin or reliability suppressed a firm chunk label (fail-closed).');
  } else {
    bullets.push('Segment appears stable relative to surrounding timeline.');
  }

  if (globalConsensus?.verdict === 'inconclusive') {
    bullets.push(
      `Global run is inconclusive (${Math.round((globalConsensus.confidence || 0) * 100)}% confidence) — chunk context supports review.`,
    );
  }

  let severity = 'neutral';
  if (eventKey === 'contradiction' || eventKey === 'splice' || verdict === 'fake') severity = 'high';
  else if (verdict === 'inconclusive' || threats.length) severity = 'medium';

  return {
    headline: `${meta.label} · ${chunk.start_time?.toFixed(2)}s–${chunk.end_time?.toFixed(2)}s`,
    bullets,
    severity,
    meta,
  };
};

export const buildExportableReportSummary = (result) => {
  if (!result) return '';
  const c = result.consensus || {};
  const lines = [
    '=== Deepfake Forensic AI — Report Summary ===',
    `File: ${result.filename || 'unknown'}`,
    `Report ID: ${result.id || 'n/a'}`,
    `Verdict: ${(c.verdict || 'unknown').toUpperCase()}`,
    `Confidence: ${Math.round((c.confidence || 0) * 100)}%`,
    `Convergence: ${Math.round((c.convergence_strength || 0) * 100)}%`,
    '',
    result.narrative?.human_summary || '',
    '',
    '--- Diagnostics ---',
    ...(result.diagnostics?.synthesis_warnings || []).map((w) =>
      typeof w === 'string' ? w : `[synthesis] ${w.message}`,
    ),
    ...(result.diagnostics?.quality_warnings || []).map((w) =>
      typeof w === 'string' ? w : `[quality] ${w.message}`,
    ),
    '',
    '--- Timeline segments ---',
  ];

  (result.timeline || []).forEach((chunk, i) => {
    const summary = buildChunkSuspicionSummary(chunk, c);
    lines.push(`${i + 1}. ${summary.headline}`);
    summary.bullets.forEach((b) => lines.push(`   - ${b}`));
  });

  return lines.join('\n');
};

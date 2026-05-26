const threatSignature = (event) => {
  const warnings = event?.threat_warnings || [];
  if (!warnings.length) return '';
  return warnings
    .map((w) => `${w.type || w.threat_type || 'unknown'}:${w.severity || 'unknown'}`)
    .sort()
    .join('|');
};

/**
 * Merge adjacent timeline markers with the same event_type, verdict, and threats.
 */
export function compressTimeline(events, gapTolerance = 0.05) {
  if (!events?.length) return [];

  const sorted = [...events].sort(
    (a, b) => (a.start_time || 0) - (b.start_time || 0) || (a.end_time || 0) - (b.end_time || 0),
  );
  const merged = [];

  for (const event of sorted) {
    const row = { ...event, segment_count: event.segment_count || 1 };
    if (!merged.length) {
      merged.push(row);
      continue;
    }
    const prev = merged[merged.length - 1];
    const adjacent = (row.start_time || 0) <= (prev.end_time || 0) + gapTolerance;
    const same =
      prev.event_type === row.event_type &&
      prev.verdict === row.verdict &&
      threatSignature(prev) === threatSignature(row);

    if (same && adjacent) {
      prev.end_time = Math.max(prev.end_time || 0, row.end_time || 0);
      prev.segment_count = (prev.segment_count || 1) + (row.segment_count || 1);
      if ((row.confidence || 0) > (prev.confidence || 0)) {
        prev.confidence = row.confidence;
      }
    } else {
      merged.push(row);
    }
  }

  return merged;
}

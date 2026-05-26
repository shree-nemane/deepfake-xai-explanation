/** Human-readable labels and colors for consensus timeline event types. */

export const EVENT_LEGEND = [
  {
    key: 'contradiction',
    label: 'Agent contradiction',
    description: 'Neural vs acoustic disagreement on this segment',
    className: 'legend-contradiction',
  },
  {
    key: 'splice',
    label: 'Splice / partial edit',
    description: 'Localized manipulation or insert suspected',
    className: 'legend-splice',
  },
  {
    key: 'inconclusive',
    label: 'Inconclusive segment',
    description: 'Weak or split evidence — no firm chunk verdict',
    className: 'legend-inconclusive',
  },
  {
    key: 'stable',
    label: 'Stable segment',
    description: 'Agents largely agree on this window',
    className: 'legend-stable',
  },
];

export const normalizeEventType = (eventType) => {
  const raw = String(eventType || 'stable').toLowerCase();
  if (raw.includes('contradiction')) return 'contradiction';
  if (raw.includes('splice')) return 'splice';
  if (raw.includes('inconclusive')) return 'inconclusive';
  return 'stable';
};

export const getEventMeta = (eventType) => {
  const key = normalizeEventType(eventType);
  return EVENT_LEGEND.find((item) => item.key === key) || EVENT_LEGEND[3];
};

export const formatTimeRange = (start, end) => {
  const s = Number(start) || 0;
  const e = Number(end) || s;
  return `${s.toFixed(2)}s – ${e.toFixed(2)}s`;
};

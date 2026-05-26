import React, { useMemo } from 'react';
import { compressTimeline } from '../../utils/compressTimeline';
import { getEventMeta, formatTimeRange, normalizeEventType } from '../../utils/forensicLabels';

const TimelinePanel = ({ timeline, selectedIndex = 0, onSelectChunk }) => {
  const displayTimeline = useMemo(() => compressTimeline(timeline), [timeline]);
  const interactive = typeof onSelectChunk === 'function';

  const totalDuration = displayTimeline.length
    ? Math.max(...displayTimeline.map((event) => event.end_time || 0), 1)
    : 1;

  const rawCount = timeline?.length ?? 0;
  const showCompressionNote = rawCount > displayTimeline.length;

  if (!displayTimeline.length) {
    return (
      <div className="timeline-panel glass">
        <h3>Temporal Evidence Timeline</h3>
        <p className="timeline-empty">No temporal events detected for this report.</p>
      </div>
    );
  }

  return (
    <div className="timeline-panel glass">
      <h3>Temporal Evidence Timeline</h3>
      {showCompressionNote && (
        <p className="timeline-compression-note">
          {displayTimeline.length} analyst segment(s) from {rawCount} chunk events — click a marker for details.
        </p>
      )}

      <div className="timeline-ruler" aria-hidden>
        <span>0s</span>
        <span>{totalDuration.toFixed(1)}s</span>
      </div>

      <div className="timeline-container">
        <div className="timeline-track" role="list">
          {displayTimeline.map((event, index) => {
            const meta = getEventMeta(event.event_type);
            const typeKey = normalizeEventType(event.event_type);
            const left = ((event.start_time || 0) / totalDuration) * 100;
            const width = Math.max(
              (((event.end_time || 0) - (event.start_time || 0)) / totalDuration) * 100,
              1.2,
            );
            const isSelected = interactive && selectedIndex === index;
            const tooltip = [
              meta.label,
              formatTimeRange(event.start_time, event.end_time),
              `Verdict: ${event.verdict}`,
              `Confidence: ${Math.round((event.confidence || 0) * 100)}%`,
              event.segment_count > 1 ? `${event.segment_count} merged chunks` : null,
            ]
              .filter(Boolean)
              .join(' · ');

            const MarkerTag = interactive ? 'button' : 'div';
            const markerProps = interactive
              ? {
                  type: 'button',
                  onClick: () => onSelectChunk(index),
                  'aria-pressed': isSelected,
                  'aria-label': tooltip,
                }
              : { title: tooltip };

            return (
              <MarkerTag
                key={`${event.start_time}-${event.end_time}-${index}`}
                className={`timeline-segment timeline-segment-${typeKey} ${
                  event.verdict === 'fake' ? 'alert-fake' : ''
                } ${isSelected ? 'timeline-segment-selected' : ''}`}
                style={{ left: `${left}%`, width: `${width}%` }}
                {...markerProps}
              >
                <span className="timeline-segment-tooltip">{tooltip}</span>
              </MarkerTag>
            );
          })}
        </div>
      </div>

      {interactive && displayTimeline[selectedIndex] && (
        <p className="timeline-selection-hint">
          Selected: {getEventMeta(displayTimeline[selectedIndex].event_type).label} ·{' '}
          {formatTimeRange(
            displayTimeline[selectedIndex].start_time,
            displayTimeline[selectedIndex].end_time,
          )}
        </p>
      )}
    </div>
  );
};

export default TimelinePanel;

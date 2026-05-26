import React, { useMemo } from 'react';
import { compressTimeline } from '../../utils/compressTimeline';

const TimelinePanel = ({ timeline }) => {
  const displayTimeline = useMemo(() => compressTimeline(timeline), [timeline]);

  const totalDuration = displayTimeline.length
    ? Math.max(...displayTimeline.map((event) => event.end_time || 0), 1)
    : 1;

  const rawCount = timeline?.length ?? 0;
  const showCompressionNote = rawCount > displayTimeline.length;

  return (
    <div className="timeline-panel">
      <h3>Temporal Evidence Timeline</h3>
      {showCompressionNote && (
        <p className="timeline-compression-note">
          Showing {displayTimeline.length} analyst segment(s) merged from {rawCount} chunk events.
        </p>
      )}
      <div className="timeline-container">
        {displayTimeline.length > 0 ? (
          <div className="timeline-track">
            {displayTimeline.map((event, index) => (
              <div
                key={index}
                className={`timeline-marker ${event.verdict === 'fake' ? 'alert-fake' : ''}`}
                style={{ left: `${((event.start_time || 0) / totalDuration) * 100}%` }}
                title={`${event.start_time}s-${event.end_time}s ${event.verdict}${
                  event.segment_count > 1 ? ` (${event.segment_count} chunks)` : ''
                }`}
              >
                <span className="event-label">
                  {event.event_type}
                  {event.segment_count > 1 ? ` ×${event.segment_count}` : ''} (
                  {Math.round((event.confidence || 0) * 100)}%)
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p>No temporal events detected.</p>
        )}
      </div>
    </div>
  );
};

export default TimelinePanel;

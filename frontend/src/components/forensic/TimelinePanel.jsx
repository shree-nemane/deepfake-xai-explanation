import React from 'react';

const TimelinePanel = ({ timeline }) => {
  const totalDuration = timeline?.length
    ? Math.max(...timeline.map((event) => event.end_time || 0), 1)
    : 1;

  return (
    <div className="timeline-panel">
      <h3>Temporal Evidence Timeline</h3>
      <div className="timeline-container">
        {timeline && timeline.length > 0 ? (
          <div className="timeline-track">
            {timeline.map((event, index) => (
              <div
                key={index}
                className={`timeline-marker ${event.verdict === 'fake' ? 'alert-fake' : ''}`}
                style={{ left: `${((event.start_time || 0) / totalDuration) * 100}%` }}
                title={`${event.start_time}s-${event.end_time}s ${event.verdict}`}
              >
                <span className="event-label">
                  {event.event_type} ({Math.round((event.confidence || 0) * 100)}%)
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

from backend.forensic.timeline_compression import compress_timeline_events


def _event(start, end, event_type="contradiction", verdict="inconclusive", threats=None):
    return {
        "start_time": start,
        "end_time": end,
        "event_type": event_type,
        "verdict": verdict,
        "confidence": 0.5,
        "threat_warnings": threats or [],
    }


def test_compress_adjacent_same_signature():
    events = [
        _event(0.0, 1.0, threats=[{"type": "voice_clone", "severity": "high"}]),
        _event(1.0, 2.0, threats=[{"type": "voice_clone", "severity": "high"}]),
        _event(2.0, 3.0, threats=[{"type": "voice_clone", "severity": "high"}]),
    ]
    compressed = compress_timeline_events(events)
    assert len(compressed) == 1
    assert compressed[0]["end_time"] == 3.0
    assert compressed[0]["segment_count"] == 3


def test_does_not_merge_different_event_types():
    events = [
        _event(0.0, 1.0, event_type="contradiction"),
        _event(1.0, 2.0, event_type="stable"),
    ]
    compressed = compress_timeline_events(events)
    assert len(compressed) == 2

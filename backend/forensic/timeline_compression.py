"""Merge adjacent timeline events with the same forensic signature for analyst UI."""


def _threat_signature(event: dict) -> tuple:
    warnings = event.get("threat_warnings") or []
    if not warnings:
        return ()
    parts = []
    for warning in warnings:
        parts.append(
            (
                warning.get("type") or warning.get("threat_type") or "unknown",
                warning.get("severity") or "unknown",
            )
        )
    return tuple(sorted(parts))


def compress_timeline_events(events: list, gap_tolerance: float = 0.05) -> list:
    """
    Collapse consecutive chunks that share event_type, verdict, and threat profile.

    Preserves the first chunk's details; extends end_time and records segment_count.
    """
    if not events:
        return []

    sorted_events = sorted(
        events,
        key=lambda e: (e.get("start_time") or 0.0, e.get("end_time") or 0.0),
    )
    merged: list[dict] = []

    for event in sorted_events:
        row = {**event, "segment_count": event.get("segment_count", 1)}
        if not merged:
            merged.append(row)
            continue

        prev = merged[-1]
        same_type = prev.get("event_type") == row.get("event_type")
        same_verdict = prev.get("verdict") == row.get("verdict")
        prev_end = prev.get("end_time") or 0.0
        row_start = row.get("start_time") or 0.0
        adjacent = row_start <= prev_end + gap_tolerance
        same_threats = _threat_signature(prev) == _threat_signature(row)

        if same_type and same_verdict and adjacent and same_threats:
            prev["end_time"] = max(prev_end, row.get("end_time") or prev_end)
            prev["segment_count"] = prev.get("segment_count", 1) + row.get("segment_count", 1)
            if (row.get("confidence") or 0) > (prev.get("confidence") or 0):
                prev["confidence"] = row.get("confidence")
                prev["convergence_strength"] = row.get("convergence_strength")
        else:
            merged.append(row)

    return merged

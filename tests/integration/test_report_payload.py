from backend.api.routes.analysis import (
    _apply_mel_previews,
    _extract_mel_previews,
    _flatten_diagnostic_warnings,
)


def test_extract_and_apply_mel_previews():
    timeline = [
        {"start_time": 0.0, "end_time": 2.0, "mel_preview_base64": "abc123", "verdict": "real"},
        {"start_time": 2.0, "end_time": 4.0, "verdict": "fake"},
    ]
    stripped, previews = _extract_mel_previews(timeline)
    assert "mel_preview_base64" not in stripped[0]
    assert previews["0.0:2.0"] == "abc123"
    restored = _apply_mel_previews(stripped, previews)
    assert restored[0]["mel_preview_base64"] == "abc123"


def test_flatten_structured_diagnostic_warnings():
    warnings = [
        {"category": "signal_quality", "message": "Recording quality is degraded."},
        "plain string warning",
    ]
    flat = _flatten_diagnostic_warnings(warnings)
    assert flat[0] == "Recording quality is degraded."
    assert flat[1] == "plain string warning"

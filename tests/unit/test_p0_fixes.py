import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import math
import numpy as np
try:
    import pytest
except ImportError:
    pytest = None
from unittest.mock import patch
from datetime import datetime, timezone

from backend.agents.acoustic_agent import AcousticAgent
from backend.forensic.features.acoustic_features import extract_all_features
from backend.forensic.anomaly.zscore_engine import compute_abnormality_scores
from backend.api.schemas.analysis import TimelineEventSchema, AnalysisResponse, ConsensusSchema, AgentOutputSchema


def test_acoustic_agent_confidence_bounds():
    """Verify AcousticAgent confidence is always in [0.50, 0.99] regardless of distance to threshold."""
    agent = AcousticAgent()
    dummy_audio = np.zeros(48000, dtype=np.float32)

    # 1. Test near-threshold anomaly (0.53 vs threshold 0.52)
    with patch("backend.agents.acoustic_agent.extract_all_features", return_value={}):
        with patch("backend.agents.acoustic_agent.compute_abnormality_scores", return_value={}):
            with patch("backend.agents.acoustic_agent.compute_overall_anomaly", return_value=0.53):
                res = agent.analyze_chunk(dummy_audio)
                assert res["verdict"] == "fake"
                assert 0.50 <= res["confidence"] <= 0.99
                assert math.isclose(res["confidence"], 0.51, abs_tol=0.01)

    # 2. Test low anomaly (clean authentic speech, 0.10)
    with patch("backend.agents.acoustic_agent.extract_all_features", return_value={}):
        with patch("backend.agents.acoustic_agent.compute_abnormality_scores", return_value={}):
            with patch("backend.agents.acoustic_agent.compute_overall_anomaly", return_value=0.10):
                res = agent.analyze_chunk(dummy_audio)
                assert res["verdict"] == "real"
                assert res["confidence"] >= 0.90
                assert res["confidence"] <= 0.99

    # 3. Test extreme high anomaly (synthetic speech, 0.95)
    with patch("backend.agents.acoustic_agent.extract_all_features", return_value={}):
        with patch("backend.agents.acoustic_agent.compute_abnormality_scores", return_value={}):
            with patch("backend.agents.acoustic_agent.compute_overall_anomaly", return_value=0.95):
                res = agent.analyze_chunk(dummy_audio)
                assert res["verdict"] == "fake"
                assert res["confidence"] >= 0.90
                assert res["confidence"] <= 0.99


def test_jitter_percentage_normalization():
    """Verify jitter is computed as relative percentage rather than raw Hertz difference."""
    sr = 48000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Synthetic tone with smooth 150 Hz carrier
    y = np.sin(2 * np.pi * 150 * t).astype(np.float32)

    features = extract_all_features(y, sr)
    assert "jitter" in features
    # Jitter on a clean sine wave should be close to 0% (well below 2.0%)
    assert 0.0 <= features["jitter"] <= 2.0

    # Abnormality scoring should not produce an extreme risk score (>10 z-score) for a clean tone
    scores = compute_abnormality_scores(features)
    assert scores["jitter"]["z_score"] < 10.0


def test_timeline_event_schema_preserves_mel_preview():
    """Verify TimelineEventSchema includes mel_preview_base64 and doesn't strip it on dump."""
    event = TimelineEventSchema(
        start_time=0.0,
        end_time=2.0,
        event_type="agreement",
        verdict="real",
        confidence=0.88,
        convergence_strength=0.95,
        mel_preview_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        segment_count=1
    )
    dumped = event.model_dump()
    assert "mel_preview_base64" in dumped
    assert dumped["mel_preview_base64"].startswith("iVBORw0KGgo")
    assert dumped["segment_count"] == 1


def test_analysis_response_schema_preserves_mel_preview():
    """Verify AnalysisResponse model serialization preserves mel_preview_base64 in timeline."""
    response = AnalysisResponse(
        id="test-report-id",
        filename="sample.wav",
        consensus=ConsensusSchema(
            verdict="real",
            convergence_strength=0.95,
            confidence=0.88,
            uncertainty=0.12
        ),
        agents={
            "convnext": AgentOutputSchema(name="convnext", verdict="real", confidence=0.90, uncertainty=0.10)
        },
        timeline=[
            TimelineEventSchema(
                start_time=0.0,
                end_time=2.0,
                event_type="agreement",
                verdict="real",
                confidence=0.88,
                convergence_strength=0.95,
                mel_preview_base64="dummy_base64_preview"
            )
        ],
        mel_previews={"0.0:2.0": "dummy_base64_preview"},
        created_at=datetime.now(timezone.utc)
    )
    dumped = response.model_dump()
    assert dumped["timeline"][0]["mel_preview_base64"] == "dummy_base64_preview"
    assert dumped["mel_previews"]["0.0:2.0"] == "dummy_base64_preview"


if __name__ == "__main__":
    print("Running test_acoustic_agent_confidence_bounds...")
    test_acoustic_agent_confidence_bounds()
    print("Running test_jitter_percentage_normalization...")
    test_jitter_percentage_normalization()
    print("Running test_timeline_event_schema_preserves_mel_preview...")
    test_timeline_event_schema_preserves_mel_preview()
    print("Running test_analysis_response_schema_preserves_mel_preview...")
    test_analysis_response_schema_preserves_mel_preview()
    print("\n>>> ALL P0 FIX TESTS PASSED SUCCESSFULLY! <<<")


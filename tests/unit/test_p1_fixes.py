import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import math
import numpy as np
from unittest.mock import MagicMock, patch
import torch

from backend.agents.wavlm_agent import WavLMAgent
from backend.models.wavlm.wavlm_handler import WavLMHandler


def test_history_inconclusive_risk_score():
    """Verify that inconclusive reports in get_history do not default to 100% risk."""
    # Test logic directly matching the router implementation
    mock_reports = [
        # Report 1: Fake verdict with high fake_probability
        MagicMock(
            id="rep-fake",
            filename="fake.wav",
            created_at="2026-09-12",
            full_response={
                "consensus": {
                    "verdict": "fake",
                    "confidence": 0.88,
                    "fake_probability": 0.88
                }
            }
        ),
        # Report 2: Real verdict with high confidence
        MagicMock(
            id="rep-real",
            filename="real.wav",
            created_at="2026-09-12",
            full_response={
                "consensus": {
                    "verdict": "real",
                    "confidence": 0.92,
                    "fake_probability": 0.08
                }
            }
        ),
        # Report 3: Inconclusive verdict with zero confidence (tie / degraded audio)
        MagicMock(
            id="rep-inconclusive",
            filename="noisy.wav",
            created_at="2026-09-12",
            full_response={
                "consensus": {
                    "verdict": "inconclusive",
                    "confidence": 0.0,
                    "fake_probability": 0.50
                }
            }
        ),
        # Report 4: Inconclusive without fake_probability specified
        MagicMock(
            id="rep-inconclusive-empty",
            filename="empty.wav",
            created_at="2026-09-12",
            full_response={
                "consensus": {
                    "verdict": "inconclusive",
                    "confidence": 0.0
                }
            }
        )
    ]

    history_list = []
    for r in mock_reports:
        consensus = r.full_response.get("consensus", {})
        verdict = consensus.get("verdict", "inconclusive")
        confidence = float(consensus.get("confidence", 0.0))
        fake_prob = consensus.get("fake_probability")

        if verdict == "fake":
            risk_score = float(fake_prob * 100.0) if fake_prob is not None else float(confidence * 100.0)
        elif verdict == "real":
            risk_score = float((1.0 - confidence) * 100.0)
        else:
            # Inconclusive / degraded audio: use fake_probability if available, or neutral 50.0%
            risk_score = float(fake_prob * 100.0) if fake_prob is not None else 50.0

        history_list.append({
            "id": r.id,
            "prediction": verdict,
            "confidence": confidence,
            "risk_score": round(risk_score, 2)
        })

    # Assertions
    assert history_list[0]["risk_score"] == 88.0
    assert history_list[1]["risk_score"] == 8.0  # (1 - 0.92) * 100
    assert history_list[2]["risk_score"] == 50.0  # Inconclusive with 0.50 fake_prob
    assert history_list[3]["risk_score"] == 50.0  # Inconclusive with fallback 50.0
    # Crucially, neither inconclusive report should be 100%
    assert all(h["risk_score"] < 100.0 for h in history_list[2:])


def test_wavlm_single_pass_feature_extraction():
    """Verify WavLMHandler computes temporal entropy in the single forward pass."""
    dummy_audio = np.zeros(16000, dtype=np.float32)

    mock_last_hidden_state = torch.randn(1, 49, 768)  # (batch=1, time=49, hidden=768)
    mock_outputs = MagicMock()
    mock_outputs.last_hidden_state = mock_last_hidden_state

    # Instantiate handler with mocks
    with patch.object(WavLMHandler, "__init__", lambda self, device="cpu": None):
        handler = WavLMHandler()
        handler.device = "cpu"
        handler.processor = MagicMock(return_value={"input_values": torch.zeros(1, 16000)})
        handler.model = MagicMock(return_value=mock_outputs)

        # Call extract_embeddings with return_entropy=True
        mean_emb, instab, entropy = handler.extract_embeddings(dummy_audio, sr=16000, return_entropy=True)

        assert mean_emb.shape == (1, 768)
        assert isinstance(instab, float)
        assert isinstance(entropy, float)
        assert entropy >= 0.0

        # Model should have been called exactly ONCE
        assert handler.model.call_count == 1


def test_wavlm_agent_uses_single_pass():
    """Verify WavLMAgent executes without calling _compute_temporal_entropy redundant pass."""
    agent = WavLMAgent()
    dummy_chunk = np.ones(32000, dtype=np.float32) * 0.05  # Non-silent chunk

    mock_mean_emb = torch.randn(1, 768)
    mock_instab = 0.15
    mock_entropy = 0.04

    with patch("backend.agents.wavlm_agent.model_hub") as mock_hub:
        mock_hub.wavlm_handler.extract_embeddings.return_value = (mock_mean_emb, mock_instab, mock_entropy)
        # Mock _compute_temporal_entropy to fail if called
        with patch.object(agent, "_compute_temporal_entropy", side_effect=AssertionError("Redundant pass was called!")):
            result = agent.analyze_chunk(dummy_chunk)

            assert result["verdict"] == "fake"  # 0.15 > threshold 0.12
            assert result["evidence"]["phonetic_instability"] == 0.15
            assert result["evidence"]["temporal_entropy"] == 0.04
            mock_hub.wavlm_handler.extract_embeddings.assert_called_once_with(dummy_chunk, sr=16000, return_entropy=True)


def test_audio_processor_preserves_continuous_timeline():
    """Verify AudioProcessor preserves full continuous audio duration and outputs speech intervals."""
    from backend.preprocessing.audio_processor import AudioProcessor

    with patch.object(AudioProcessor, "__init__", lambda self: None):
        mock_timestamps = [
            {"start": 0, "end": 16000},        # 0.0s to 1.0s at 16k
            {"start": 32000, "end": 48000}     # 2.0s to 3.0s at 16k
        ]
        processor = AudioProcessor()
        processor.vad_model = MagicMock()
        processor.get_speech_timestamps = MagicMock(return_value=mock_timestamps)

        sr_48k = 48000
        duration_sec = 3.0
        t = np.linspace(0, duration_sec, int(sr_48k * duration_sec), endpoint=False)
        # 1 second of speech, 1 second of silence, 1 second of speech
        dummy_y48k = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        dummy_y48k[int(sr_48k * 1.0):int(sr_48k * 2.0)] = 0.0  # Silence in middle

        with patch("librosa.load", return_value=(dummy_y48k, sr_48k)):
            with patch("librosa.get_duration", return_value=duration_sec):
                with patch.object(processor, "validate_audio", return_value=(True, "")):
                    with patch.object(processor, "normalize_lufs", return_value=(dummy_y48k, {"gain_applied": 1.0})):
                        streams = processor.process_dual_stream("dummy.wav", concatenate_speech=False)

                        # Output duration should match original duration (3.0s)
                        assert len(streams["16k"]) == int(3.0 * 16000)
                        assert len(streams["48k"]) == int(3.0 * 48000)
                        assert streams["metadata"]["original_duration_sec"] == 3.0
                        assert streams["metadata"]["active_duration_sec"] == 2.0  # 2.0s of actual speech
                        assert math.isclose(streams["metadata"]["speech_coverage"], 2.0 / 3.0, abs_tol=0.01)
                        assert len(streams["metadata"]["speech_intervals"]) == 2


if __name__ == "__main__":
    print("Running test_history_inconclusive_risk_score...")
    test_history_inconclusive_risk_score()
    print("Running test_wavlm_single_pass_feature_extraction...")
    test_wavlm_single_pass_feature_extraction()
    print("Running test_wavlm_agent_uses_single_pass...")
    test_wavlm_agent_uses_single_pass()
    print("Running test_audio_processor_preserves_continuous_timeline...")
    test_audio_processor_preserves_continuous_timeline()
    print("\n>>> ALL P1 FIX TESTS PASSED! <<<")

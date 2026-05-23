import numpy as np
import pytest

from backend.agents.convnext_agent import ConvNextAgent
from backend.api.schemas.analysis import AnalysisResponse
from backend.consensus.consensus_engine import ConsensusEngine
from backend.orchestration.agent_registry import agent_registry
from backend.orchestration.forensic_orchestrator import ForensicOrchestrator, AnalysisUnavailableError

def test_current_schema_accepts_inconclusive():
    response = AnalysisResponse(
        id="validation-report",
        filename="sample.wav",
        consensus={
            "verdict": "inconclusive",
            "confidence": 0.0,
            "uncertainty": 1.0,
            "convergence_strength": 0.0,
        },
        agents={
            "convnext": {
                "name": "convnext",
                "verdict": "inconclusive",
                "confidence": 0.0,
                "uncertainty": 1.0,
                "evidence": {"fallback_reason": "inference_unavailable"},
            }
        },
        timeline=[
            {
                "start_time": 0.0,
                "end_time": 2.0,
                "event_type": "inconclusive",
                "verdict": "inconclusive",
                "confidence": 0.0,
                "convergence_strength": 0.0,
                "details": {},
            }
        ],
        heatmap_base64=None,
        created_at="2026-05-21T00:00:00",
    )
    assert response.consensus.verdict == "inconclusive"


def test_consensus_fail_closed():
    engine = ConsensusEngine()

    empty = engine.evaluate_chunk_consensus({}, global_reliability=1.0)
    assert empty["verdict"] == "inconclusive"

    all_fallback = engine.evaluate_chunk_consensus(
        {
            "convnext": {
                "verdict": "inconclusive",
                "confidence": 0.0,
                "uncertainty": 1.0,
            }
        },
        global_reliability=1.0,
    )
    assert all_fallback["verdict"] == "inconclusive"

    tie = engine.evaluate_chunk_consensus(
        {
            "convnext": {"verdict": "fake", "confidence": 0.9, "uncertainty": 0.1},
            "acoustic": {"verdict": "real", "confidence": 0.9, "uncertainty": 0.1},
        },
        global_reliability=1.0,
    )
    assert tie["verdict"] == "inconclusive"


def test_empty_registry_guard():
    saved_agents = dict(agent_registry._agents)
    try:
        agent_registry._agents.clear()
        orchestrator = ForensicOrchestrator()
        agent_registry._agents.clear()
        with pytest.raises(AnalysisUnavailableError):
            orchestrator.analyze_audio(np.zeros(16000), np.zeros(48000))
    finally:
        agent_registry._agents.clear()
        agent_registry._agents.update(saved_agents)


def test_fallback_is_visible():
    fallback = ConvNextAgent._fallback_verdict("model unavailable")
    assert fallback["verdict"] == "inconclusive"
    assert fallback["evidence"]["fallback_reason"] == "inference_unavailable"

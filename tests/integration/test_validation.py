"""Current-pipeline validation checks.

These tests avoid heavyweight model execution and verify the response contract
and fail-closed consensus behavior used by the API.
"""

import traceback

import numpy as np

from backend.agents.convnext_agent import ConvNextAgent
from backend.api.schemas.analysis import AnalysisResponse
from backend.consensus.consensus_engine import ConsensusEngine
from backend.orchestration.agent_registry import agent_registry
from backend.orchestration.forensic_orchestrator import (
    AnalysisUnavailableError,
    ForensicOrchestrator,
)


def assert_current_schema_accepts_inconclusive():
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


def assert_consensus_fail_closed():
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


def assert_empty_registry_guard():
    saved_agents = dict(agent_registry._agents)
    try:
        agent_registry._agents.clear()
        orchestrator = ForensicOrchestrator()
        agent_registry._agents.clear()
        try:
            orchestrator.analyze_audio(np.zeros(16000), np.zeros(48000))
        except AnalysisUnavailableError:
            return
        raise AssertionError("Empty registry did not fail closed.")
    finally:
        agent_registry._agents.clear()
        agent_registry._agents.update(saved_agents)


def assert_fallback_is_visible():
    fallback = ConvNextAgent._fallback_verdict("model unavailable")
    assert fallback["verdict"] == "inconclusive"
    assert fallback["evidence"]["fallback_reason"] == "inference_unavailable"


if __name__ == "__main__":
    try:
        assert_current_schema_accepts_inconclusive()
        assert_consensus_fail_closed()
        assert_empty_registry_guard()
        assert_fallback_is_visible()
        print("Validation successful: current schema and fail-closed behavior verified.")
    except Exception:
        print("ERROR CAUGHT DURING VALIDATION:")
        traceback.print_exc()
        raise

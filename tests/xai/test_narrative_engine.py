from backend.explainability.narrative_engine import NarrativeEngine


def test_narrative_includes_required_sections():
    result = NarrativeEngine().generate(
        global_consensus={"verdict": "fake", "confidence": 0.82, "uncertainty": 0.12, "convergence_strength": 0.75},
        frontend_agents={"wavlm": {}, "reliability": {"evidence": {"reliability_score": 0.9}}},
        chunk_consensus=[],
        shap_values={"chunks": [{"values": {"wavlm": 0.2}}]},
        counterfactuals={"summary": "wavlm has the strongest local sensitivity."},
        diagnostics={"warnings": []},
    )

    for section in NarrativeEngine.REQUIRED_SECTIONS:
        assert f"## {section}" in result["structured_summary"]


def test_narrative_mentions_threat_warning():
    result = NarrativeEngine().generate(
        global_consensus={"verdict": "inconclusive", "confidence": 0.55, "uncertainty": 0.4, "convergence_strength": 0.5},
        frontend_agents={"reliability": {"evidence": {"reliability_score": 0.8}}},
        chunk_consensus=[
            {
                "start_time": 1.0,
                "end_time": 3.0,
                "threat_warnings": [
                    {
                        "threat_type": "voice_clone",
                        "description": "Voice Clone Threat: phonetic cloning suspected.",
                        "severity": "high",
                    }
                ],
            }
        ],
    )

    assert "voice_clone" in result["structured_summary"]
    assert "Voice Clone Threat" in result["structured_summary"]
    assert result["narrative_metadata"]["threat_count"] == 1


def test_narrative_mentions_low_reliability():
    result = NarrativeEngine().generate(
        global_consensus={"verdict": "inconclusive", "confidence": 0.4, "uncertainty": 0.8, "convergence_strength": 0.1},
        frontend_agents={"reliability": {"evidence": {"reliability_score": 0.3}}},
        chunk_consensus=[],
    )

    assert "degraded" in result["structured_summary"]

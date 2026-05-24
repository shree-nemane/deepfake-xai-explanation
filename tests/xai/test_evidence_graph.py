from backend.explainability.evidence_graph import generate_evidence_graph


def _sample_graph():
    return generate_evidence_graph(
        filename="sample.wav",
        preprocessing={
            "original_duration_sec": 4.0,
            "active_duration_sec": 3.5,
            "speech_coverage": 0.875,
            "chunk_count": 2,
            "sample_rates": {"semantic_stream_hz": 16000, "acoustic_stream_hz": 48000},
        },
        frontend_agents={
            "reliability": {
                "name": "reliability",
                "verdict": "reliable",
                "confidence": 0.9,
                "uncertainty": 0.1,
                "evidence": {"reliability_score": 0.88},
            },
            "wavlm": {
                "name": "wavlm",
                "verdict": "fake",
                "confidence": 0.8,
                "uncertainty": 0.2,
                "evidence": {"phonetic_instability": 0.2},
            },
            "convnext": {
                "name": "convnext",
                "verdict": "real",
                "confidence": 0.7,
                "uncertainty": 0.3,
                "evidence": {"fake_probability": 0.3},
            },
        },
        chunk_consensus=[
            {
                "start_time": 0.0,
                "end_time": 2.0,
                "event_type": "contradiction",
                "verdict": "inconclusive",
                "consensus_confidence": 0.52,
                "threat_warnings": [
                    {
                        "threat_type": "localized_splice",
                        "description": "Agent contradiction in a localized region.",
                        "severity": "medium",
                    }
                ],
            }
        ],
        global_consensus={
            "verdict": "inconclusive",
            "confidence": 0.52,
            "convergence_strength": 0.44,
            "fake_probability": 0.51,
            "real_probability": 0.49,
        },
        xai_payload={
            "shap_values": {
                "method": "exact_consensus_shap",
                "chunks": [{"chunk_index": 0}],
                "summary": {"average_values": {"wavlm": 0.2}},
            },
            "counterfactuals": {
                "method": "analytical_level_1",
                "chunks": [{"chunk_index": 0}],
                "summary": "wavlm has strongest positive sensitivity.",
            },
        },
        narrative_payload={
            "human_summary": "Inconclusive forensic result.",
            "narrative_metadata": {"narrative_version": "deterministic_v1"},
        },
        diagnostics={"review_level": "needs_human_review", "warnings": ["Inspect contradiction."]},
    )


def test_evidence_graph_has_required_layers():
    graph = _sample_graph()
    layer_ids = {layer["id"] for layer in graph["layers"]}
    node_layers = {node["layer"] for node in graph["nodes"]}

    assert graph["schema_version"] == "evidence_graph_v1"
    assert layer_ids == {1, 2, 3, 4, 5, 6}
    assert {1, 2, 3, 4, 5, 6}.issubset(node_layers)


def test_evidence_graph_edges_are_directed_and_typed():
    graph = _sample_graph()

    assert graph["edges"]
    for edge in graph["edges"]:
        assert edge["source"]
        assert edge["target"]
        assert edge["relation"]


def test_evidence_graph_includes_threat_and_xai_nodes():
    graph = _sample_graph()
    node_types = {node["type"] for node in graph["nodes"]}
    node_ids = {node["id"] for node in graph["nodes"]}

    assert "threat_warning" in node_types
    assert "shapley_attribution" in node_types
    assert "counterfactual_sensitivity" in node_types
    assert "xai:shap" in node_ids
    assert "xai:counterfactuals" in node_ids

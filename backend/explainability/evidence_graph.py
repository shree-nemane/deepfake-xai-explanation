"""Deterministic evidence graph builder for forensic analysis reports."""


class EvidenceGraph:
    """Builds a typed, directed, six-layer evidence graph."""

    LAYERS = (
        {"id": 1, "name": "Audio Input"},
        {"id": 2, "name": "Preprocessing/Reliability"},
        {"id": 3, "name": "Forensic Agents"},
        {"id": 4, "name": "Consensus Arbitration"},
        {"id": 5, "name": "XAI Artifacts"},
        {"id": 6, "name": "Verdict & Narrative"},
    )

    def __init__(self):
        self.nodes = []
        self.edges = []
        self._node_ids = set()
        self._edge_ids = set()

    def add_node(self, node_id, layer, node_type, label, payload=None, severity=None, status=None):
        if node_id in self._node_ids:
            return node_id

        node = {
            "id": node_id,
            "layer": layer,
            "type": node_type,
            "label": label,
            "payload": payload or {},
        }
        if severity is not None:
            node["severity"] = severity
        if status is not None:
            node["status"] = status

        self.nodes.append(node)
        self._node_ids.add(node_id)
        return node_id

    def add_edge(self, source, target, relation):
        edge_key = (source, target, relation)
        if edge_key in self._edge_ids:
            return

        self.edges.append({
            "source": source,
            "target": target,
            "relation": relation,
        })
        self._edge_ids.add(edge_key)

    def export(self):
        layer_counts = {
            layer["id"]: sum(1 for node in self.nodes if node["layer"] == layer["id"])
            for layer in self.LAYERS
        }
        return {
            "schema_version": "evidence_graph_v1",
            "layers": list(self.LAYERS),
            "nodes": self.nodes,
            "edges": self.edges,
            "summary": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "layer_counts": layer_counts,
            },
        }


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _event_name(event):
    event_type = event.get("event_type")
    if hasattr(event_type, "value"):
        return event_type.value
    return str(event_type) if event_type is not None else "unknown"


def _agent_payload(agent):
    return {
        "verdict": agent.get("verdict"),
        "confidence": _safe_float(agent.get("confidence")),
        "uncertainty": _safe_float(agent.get("uncertainty")),
        "evidence": agent.get("evidence") or {},
    }


def generate_evidence_graph(
    consensus_results=None,
    timeline_events=None,
    *,
    filename=None,
    preprocessing=None,
    frontend_agents=None,
    chunk_consensus=None,
    global_consensus=None,
    xai_payload=None,
    narrative_payload=None,
    diagnostics=None,
):
    """Build a six-layer directed JSON graph from observed analysis artifacts."""

    graph = EvidenceGraph()
    preprocessing = preprocessing or {}
    frontend_agents = frontend_agents or {}
    chunk_consensus = chunk_consensus or timeline_events or []
    global_consensus = global_consensus or consensus_results or {}
    xai_payload = xai_payload or {}
    narrative_payload = narrative_payload or {}
    diagnostics = diagnostics or {}

    audio_node = graph.add_node(
        "audio:input",
        1,
        "audio_input",
        filename or "Uploaded audio",
        {
            "filename": filename,
            "original_duration_sec": preprocessing.get("original_duration_sec"),
            "active_duration_sec": preprocessing.get("active_duration_sec"),
        },
    )

    preprocessing_node = graph.add_node(
        "preprocessing:dual_stream",
        2,
        "preprocessing",
        "Dual-stream preprocessing",
        {
            "sample_rates": preprocessing.get("sample_rates"),
            "speech_coverage": preprocessing.get("speech_coverage"),
            "chunk_count": preprocessing.get("chunk_count"),
            "lufs": preprocessing.get("lufs"),
        },
    )
    graph.add_edge(audio_node, preprocessing_node, "processed_into")

    reliability = frontend_agents.get("reliability") or {}
    reliability_node = graph.add_node(
        "reliability:signal_quality",
        2,
        "reliability",
        "Signal reliability",
        _agent_payload(reliability),
        status=reliability.get("verdict"),
    )
    graph.add_edge(preprocessing_node, reliability_node, "measured_by")

    consensus_node = graph.add_node(
        "consensus:global",
        4,
        "consensus",
        "Global consensus",
        {
            "verdict": global_consensus.get("verdict"),
            "confidence": _safe_float(global_consensus.get("confidence")),
            "convergence_strength": _safe_float(global_consensus.get("convergence_strength")),
            "fake_probability": global_consensus.get("fake_probability"),
            "real_probability": global_consensus.get("real_probability"),
            "warnings": diagnostics.get("warnings") or [],
        },
        status=global_consensus.get("verdict"),
    )

    for agent_name in sorted(name for name in frontend_agents if name != "reliability"):
        agent = frontend_agents[agent_name] or {}
        agent_node = graph.add_node(
            f"agent:{agent_name}",
            3,
            "forensic_agent",
            agent.get("name") or agent_name,
            _agent_payload(agent),
            status=agent.get("verdict"),
        )
        graph.add_edge(preprocessing_node, agent_node, "evaluated_by")
        graph.add_edge(reliability_node, agent_node, "calibrates")
        graph.add_edge(agent_node, consensus_node, "calibrated_into")

    for index, chunk in enumerate(chunk_consensus):
        event_node = graph.add_node(
            f"consensus:chunk:{index}",
            4,
            "consensus_event",
            f"Chunk {index} {_event_name(chunk)}",
            {
                "start_time": chunk.get("start_time"),
                "end_time": chunk.get("end_time"),
                "event_type": _event_name(chunk),
                "verdict": chunk.get("verdict"),
                "confidence": chunk.get("consensus_confidence") or chunk.get("confidence"),
                "threat_warnings": chunk.get("threat_warnings") or [],
            },
            status=chunk.get("verdict"),
        )
        graph.add_edge(event_node, consensus_node, "aggregated_into")

        for warning_index, warning in enumerate(chunk.get("threat_warnings") or []):
            warning_node = graph.add_node(
                f"warning:{index}:{warning_index}",
                4,
                "threat_warning",
                warning.get("threat_type") or warning.get("type") or "Threat warning",
                warning,
                severity=warning.get("severity"),
            )
            graph.add_edge(event_node, warning_node, "raises")
            graph.add_edge(warning_node, consensus_node, "informs")

    shap_values = xai_payload.get("shap_values") or {}
    shap_node = graph.add_node(
        "xai:shap",
        5,
        "shapley_attribution",
        "Exact Shapley attribution",
        {
            "method": shap_values.get("method"),
            "summary": shap_values.get("summary"),
            "chunk_count": len(shap_values.get("chunks") or []),
        },
    )
    graph.add_edge(consensus_node, shap_node, "explained_by")

    counterfactuals = xai_payload.get("counterfactuals") or {}
    counterfactual_node = graph.add_node(
        "xai:counterfactuals",
        5,
        "counterfactual_sensitivity",
        "Analytical counterfactual sensitivity",
        {
            "method": counterfactuals.get("method"),
            "summary": counterfactuals.get("summary"),
            "chunk_count": len(counterfactuals.get("chunks") or []),
        },
    )
    graph.add_edge(consensus_node, counterfactual_node, "explained_by")

    verdict_node = graph.add_node(
        "verdict:final",
        6,
        "verdict",
        "Final verdict",
        {
            "verdict": global_consensus.get("verdict"),
            "confidence": _safe_float(global_consensus.get("confidence")),
            "review_level": diagnostics.get("review_level"),
        },
        status=global_consensus.get("verdict"),
    )
    graph.add_edge(consensus_node, verdict_node, "supports_verdict")
    graph.add_edge(shap_node, verdict_node, "supports_verdict")
    graph.add_edge(counterfactual_node, verdict_node, "supports_verdict")

    narrative_node = graph.add_node(
        "narrative:deterministic",
        6,
        "narrative",
        "Deterministic narrative",
        {
            "metadata": narrative_payload.get("narrative_metadata") or narrative_payload.get("metadata") or {},
            "human_summary": narrative_payload.get("human_summary"),
        },
    )
    graph.add_edge(verdict_node, narrative_node, "summarized_by")
    graph.add_edge(shap_node, narrative_node, "summarized_by")
    graph.add_edge(counterfactual_node, narrative_node, "summarized_by")

    return graph.export()

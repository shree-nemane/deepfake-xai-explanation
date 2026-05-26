class NarrativeEngine:
    """Rule-driven forensic narrative generator."""

    REQUIRED_SECTIONS = (
        "Finding",
        "Evidence",
        "Reliability",
        "Confidence",
        "Contradictions",
        "Explainability",
    )

    NEURAL_AGENTS = ("wavlm", "convnext", "aasist")

    @staticmethod
    def _safe_float(value, default=0.0):
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _warning_message(warning) -> str:
        if isinstance(warning, dict):
            return warning.get("message") or str(warning)
        return str(warning)

    @staticmethod
    def _warning_category(warning, default="general") -> str:
        if isinstance(warning, dict):
            return warning.get("category") or default
        return default

    def _collect_threats(self, chunk_consensus):
        threats = []
        for chunk in chunk_consensus or []:
            for warning in chunk.get("threat_warnings", []) or []:
                threat_type = warning.get("threat_type", warning.get("type", "unknown"))
                threats.append({
                    "type": threat_type,
                    "description": warning.get("description", ""),
                    "severity": warning.get("severity", "unknown"),
                    "start_time": chunk.get("start_time"),
                    "end_time": chunk.get("end_time"),
                })
        return threats

    def _agent_verdict_summary(self, frontend_agents):
        summary = {}
        for name, payload in (frontend_agents or {}).items():
            if name == "reliability":
                continue
            summary[name] = (payload or {}).get("verdict", "inconclusive")
        return summary

    def _inconclusive_rationale(self, frontend_agents, chunk_consensus, diagnostics):
        agents = self._agent_verdict_summary(frontend_agents)
        acoustic = agents.get("acoustic")
        neural_fake = [name for name in self.NEURAL_AGENTS if agents.get(name) == "fake"]
        neural_real = [name for name in self.NEURAL_AGENTS if agents.get(name) == "real"]
        lines = []

        if acoustic == "fake" and neural_real and not neural_fake:
            lines.append(
                "Inconclusive rationale: Acoustic features flagged biological anomaly while "
                f"neural detectors ({', '.join(neural_real)}) favored authentic speech — "
                "likely acoustic threshold mismatch or partial synthesis, not unanimous spoof evidence."
            )
        elif neural_fake and acoustic == "real":
            lines.append(
                "Inconclusive rationale: Neural detectors signaled synthesis while acoustic "
                "features remained plausible — review voice-clone or splice warnings on the timeline."
            )
        elif agents and len(set(agents.values())) > 1:
            split = ", ".join(f"{name}={verdict}" for name, verdict in sorted(agents.items()))
            lines.append(f"Inconclusive rationale: Agent panel split — {split}.")

        quality = (diagnostics or {}).get("quality_warnings") or []
        synthesis = (diagnostics or {}).get("synthesis_warnings") or []
        if not quality and not synthesis:
            for warning in (diagnostics or {}).get("warnings") or []:
                category = self._warning_category(warning)
                if category == "signal_quality":
                    quality.append(warning)
                elif category == "synthesis_evidence":
                    synthesis.append(warning)

        if quality:
            lines.append(
                "Inconclusive rationale: Signal-quality factors (not spoof labels) reduced trust — "
                + "; ".join(self._warning_message(w) for w in quality[:2])
            )
        if synthesis:
            lines.append(
                "Inconclusive rationale: Synthesis or agent-disagreement evidence — "
                + "; ".join(self._warning_message(w) for w in synthesis[:2])
            )

        contradiction_chunks = sum(
            1
            for chunk in chunk_consensus or []
            if chunk.get("threat_warnings")
        )
        if contradiction_chunks:
            lines.append(
                f"Inconclusive rationale: {contradiction_chunks} chunk(s) carried explicit threat warnings; "
                "fail-closed consensus withheld a definitive fake/real label."
            )

        if not lines:
            lines.append(
                "Inconclusive rationale: Consensus margin or convergence did not meet the calibrated "
                "decision threshold; this is intentional fail-closed behavior."
            )
        return lines

    def _top_shap_agents(self, shap_values, limit=3):
        totals = {}
        chunks = (shap_values or {}).get("chunks", [])
        for chunk in chunks:
            for agent, value in (chunk.get("values") or {}).items():
                totals[agent] = totals.get(agent, 0.0) + self._safe_float(value)
        if not totals:
            totals = (shap_values or {}).get("values", {})
        ranked = sorted(totals.items(), key=lambda item: abs(self._safe_float(item[1])), reverse=True)
        return ranked[:limit]

    def generate(
        self,
        global_consensus,
        frontend_agents,
        chunk_consensus,
        shap_values=None,
        counterfactuals=None,
        preprocessing=None,
        diagnostics=None,
    ):
        verdict = (global_consensus or {}).get("verdict", "inconclusive")
        confidence = self._safe_float((global_consensus or {}).get("confidence"))
        uncertainty = self._safe_float((global_consensus or {}).get("uncertainty"))
        convergence = self._safe_float((global_consensus or {}).get("convergence_strength"))
        probability_margin = self._safe_float((global_consensus or {}).get("probability_margin"))
        reliability = self._safe_float(
            ((frontend_agents or {}).get("reliability") or {}).get("evidence", {}).get("reliability_score"),
            self._safe_float(((diagnostics or {}).get("signal_quality") or {}).get("reliability_score"), 1.0),
        )
        threats = self._collect_threats(chunk_consensus)
        top_shap = self._top_shap_agents(shap_values)
        sensitivity_summary = (counterfactuals or {}).get("summary", "No analytical sensitivity summary available.")

        quality_warnings = list((diagnostics or {}).get("quality_warnings") or [])
        synthesis_warnings = list((diagnostics or {}).get("synthesis_warnings") or [])
        if not quality_warnings and not synthesis_warnings:
            for warning in (diagnostics or {}).get("warnings") or []:
                if self._warning_category(warning) == "signal_quality":
                    quality_warnings.append(warning)
                elif self._warning_category(warning) == "synthesis_evidence":
                    synthesis_warnings.append(warning)

        if verdict == "fake":
            finding = "Finding: Synthetic speech evidence was detected by the calibrated consensus layer."
        elif verdict == "real":
            finding = "Finding: The calibrated consensus layer favored authentic speech evidence."
        else:
            finding = "Finding: The calibrated consensus layer returned an inconclusive forensic result."
            for line in self._inconclusive_rationale(frontend_agents, chunk_consensus, diagnostics):
                finding += f"\n{line}"

        evidence_lines = [
            f"Evidence: {len(chunk_consensus or [])} temporal chunks were evaluated.",
            f"Evidence: Active agents in the response: {', '.join(sorted((frontend_agents or {}).keys())) or 'none'}.",
        ]
        agent_summary = self._agent_verdict_summary(frontend_agents)
        if agent_summary:
            evidence_lines.append(
                "Evidence: Per-agent global verdicts — "
                + ", ".join(f"{name}={verdict}" for name, verdict in sorted(agent_summary.items()))
                + "."
            )

        reliability_lines = [
            f"Reliability: Estimated reliability score is {reliability:.3f}.",
        ]
        if reliability < 0.60:
            reliability_lines.append(
                "Reliability: Recording quality is degraded, so calibrated confidence should be treated cautiously."
            )
        for warning in quality_warnings:
            reliability_lines.append(f"Reliability (signal quality): {self._warning_message(warning)}")
        for warning in synthesis_warnings:
            reliability_lines.append(
                f"Reliability note (synthesis evidence, not quality alone): {self._warning_message(warning)}"
            )

        confidence_lines = [
            f"Confidence: Global confidence is {confidence:.3f}, uncertainty is {uncertainty:.3f}, and convergence strength is {convergence:.3f}.",
        ]
        if verdict == "inconclusive" and probability_margin < 0.08:
            confidence_lines.append(
                f"Confidence: Probability margin is {probability_margin:.3f} — below the fail-closed holdback threshold."
            )

        if threats:
            contradiction_lines = ["Contradictions: Explicit threat warnings were detected:"]
            for threat in threats:
                window = ""
                if threat["start_time"] is not None and threat["end_time"] is not None:
                    window = f" ({threat['start_time']:.2f}s-{threat['end_time']:.2f}s)"
                contradiction_lines.append(
                    f"Contradictions: {threat['type']} [{threat['severity']}]{window}: {threat['description']}"
                )
        else:
            contradiction_lines = ["Contradictions: No explicit contradiction threat warning was supplied."]

        explainability_lines = [f"Explainability: {sensitivity_summary}"]
        if top_shap:
            formatted = ", ".join(f"{agent}={self._safe_float(value):.3f}" for agent, value in top_shap)
            explainability_lines.append(f"Explainability: Top Shapley contributors: {formatted}.")
        else:
            explainability_lines.append("Explainability: No Shapley contributor payload was supplied.")

        sections = {
            "Finding": finding,
            "Evidence": "\n".join(evidence_lines),
            "Reliability": "\n".join(reliability_lines),
            "Confidence": "\n".join(confidence_lines),
            "Contradictions": "\n".join(contradiction_lines),
            "Explainability": "\n".join(explainability_lines),
        }

        structured_summary = "\n\n".join(f"## {name}\n{sections[name]}" for name in self.REQUIRED_SECTIONS)
        human_summary = (
            f"{sections['Finding'].splitlines()[0]} Confidence is {confidence:.1%} with reliability {reliability:.1%}. "
            f"{'Threat warnings require timeline review.' if threats else 'No explicit contradiction warning was detected.'}"
        )
        narrative_metadata = {
            "narrative_version": "deterministic_v1",
            "verdict": verdict,
            "threat_count": len(threats),
            "top_shap_agents": [agent for agent, _ in top_shap],
            "sections": list(self.REQUIRED_SECTIONS),
            "agent_verdicts": agent_summary,
        }

        return {
            "structured_summary": structured_summary,
            "human_summary": human_summary,
            "narrative_metadata": narrative_metadata,
        }

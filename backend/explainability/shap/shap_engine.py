import itertools
import math

class SHAPEngine:
    """Exact Shapley attribution for calibrated consensus contributions."""

    VOTING_AGENTS = ("wavlm", "convnext", "aasist", "acoustic")

    def __init__(self, model=None):
        self.model = model

    @staticmethod
    def _safe_float(value, default=0.0):
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _agent_vector(self, agent_name, details):
        adjusted_confidence = self._safe_float(
            details.get("adjusted_confidence", details.get("calibrated_confidence", 0.5)),
            0.5,
        )
        adjusted_uncertainty = self._safe_float(
            details.get("adjusted_uncertainty", details.get("calibrated_uncertainty", 1.0)),
            1.0,
        )
        suppression_factor = self._safe_float(details.get("suppression_factor", 1.0), 1.0)
        effective_reliability = self._safe_float(details.get("effective_reliability", 1.0), 1.0)
        weight = max(0.0, effective_reliability * max(0.0, 1.0 - adjusted_uncertainty) * suppression_factor)
        verdict = details.get("verdict", "inconclusive")

        return {
            "agent": agent_name,
            "verdict": verdict,
            "adjusted_confidence": adjusted_confidence,
            "adjusted_uncertainty": adjusted_uncertainty,
            "suppression_factor": suppression_factor,
            "effective_reliability": effective_reliability,
            "weight": weight,
        }

    def _vectors(self, calibrated_details):
        return {
            agent_name: self._agent_vector(agent_name, calibrated_details[agent_name])
            for agent_name in self.VOTING_AGENTS
            if agent_name in calibrated_details
        }

    @staticmethod
    def coalition_value(agent_vectors):
        fake_support = 0.0
        real_support = 0.0

        for vector in agent_vectors:
            confidence = vector["adjusted_confidence"]
            weight = vector["weight"]
            if vector["verdict"] == "fake":
                fake_support += confidence * weight
                real_support += (1.0 - confidence) * weight
            elif vector["verdict"] == "real":
                real_support += confidence * weight
                fake_support += (1.0 - confidence) * weight

        total_support = fake_support + real_support
        if total_support <= 0.0:
            return 0.5
        return fake_support / total_support

    def compute_consensus_shap(self, calibrated_details):
        """Compute exact Shapley values over calibrated consensus details."""
        vectors = self._vectors(calibrated_details or {})
        agent_names = tuple(vectors.keys())
        n = len(agent_names)
        base_value = 0.5

        if n == 0:
            return {
                "method": "exact_consensus_shap",
                "base_value": base_value,
                "model_output": base_value,
                "values": {},
                "details": {},
            }

        values = {agent_name: 0.0 for agent_name in agent_names}
        all_agent_set = set(agent_names)

        for agent_name in agent_names:
            others = tuple(name for name in agent_names if name != agent_name)
            for coalition_size in range(len(others) + 1):
                for coalition in itertools.combinations(others, coalition_size):
                    coalition_set = set(coalition)
                    without_value = self.coalition_value(vectors[name] for name in coalition_set)
                    with_value = self.coalition_value(vectors[name] for name in coalition_set | {agent_name})
                    coefficient = (
                        math.factorial(coalition_size)
                        * math.factorial(n - coalition_size - 1)
                        / math.factorial(n)
                    )
                    values[agent_name] += coefficient * (with_value - without_value)

        model_output = self.coalition_value(vectors[name] for name in all_agent_set)
        total_abs = sum(abs(value) for value in values.values())
        details = {}
        for agent_name, vector in vectors.items():
            details[agent_name] = {
                "verdict": vector["verdict"],
                "adjusted_confidence": vector["adjusted_confidence"],
                "adjusted_uncertainty": vector["adjusted_uncertainty"],
                "suppression_factor": vector["suppression_factor"],
                "effective_reliability": vector["effective_reliability"],
                "weight": vector["weight"],
                "normalized_contribution": (values[agent_name] / total_abs) if total_abs else 0.0,
            }

        return {
            "method": "exact_consensus_shap",
            "base_value": base_value,
            "model_output": model_output,
            "values": values,
            "details": details,
        }

    def compute_importance(self, features_dict):
        """
        Compute SHAP values for forensic features.
        Backward-compatible feature importance wrapper for legacy callers.
        """
        feature_importance = {k: v["risk_score"] for k, v in features_dict.items()}
        return feature_importance

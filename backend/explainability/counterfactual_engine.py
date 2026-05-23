from backend.explainability.counterfactuals.counterfactual_engine import (
    CounterfactualEngine as AnalyticalCounterfactualEngine,
)


class CounterfactualEngine(AnalyticalCounterfactualEngine):
    """Compatibility adapter for the canonical analytical counterfactual engine."""

    def generate_counterfactuals(self, consensus_result, global_timeline=None):
        payload = self.compute_consensus_sensitivity(
            consensus_result.get("calibrated_details", {}),
            consensus_result.get("fake_probability"),
            consensus_result.get("real_probability"),
        )
        return [item["statement"] for item in payload["sensitivities"].values()]

class CounterfactualEngine:
    def __init__(self):
        pass

    def generate(self, features_dict, risk_threshold=0.5):
        """
        Simple feature perturbation counterfactuals.
        """
        counterfactuals = []
        for feature, data in features_dict.items():
            if data["risk_score"] > risk_threshold:
                counterfactuals.append({
                    "feature": feature,
                    "observation": f"High {feature} detected ({data['value']:.2f})",
                    "suggestion": f"If {feature} was closer to natural levels, risk would decrease.",
                    "impact_estimate": "Significant"
                })
        return counterfactuals

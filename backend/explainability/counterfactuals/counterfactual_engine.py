class CounterfactualEngine:
    def __init__(self):
        pass

    def generate(self, features_dict, risk_threshold=0.5):
        """
        Generate contextual, feature-specific counterfactuals.
        """
        counterfactuals = []
        
        # Expert knowledge base for counterfactual reasoning
        feature_context = {
            "jitter": {
                "desc": "pitch micro-fluctuations",
                "action": "reducing these artificial pitch jumps",
                "why": "align more closely with the natural biological stability of human vocal cords"
            },
            "shimmer": {
                "desc": "amplitude micro-fluctuations",
                "action": "smoothing these sudden volume spikes",
                "why": "reflect the natural, gradual airflow changes in human speech"
            },
            "hnr": {
                "desc": "harmonics-to-noise ratio",
                "action": "adjusting the background noise floor",
                "why": "match the organic acoustic resonance found in real vocal tracts rather than algorithmic generation"
            },
            "mfcc_variance": {
                "desc": "spectral variance over time",
                "action": "introducing more natural variation and breath pauses",
                "why": "break the unnatural consistency often produced by AI voice cloning models"
            },
            "pitch_variation": {
                "desc": "overall pitch contour",
                "action": "introducing natural prosodic emotion and inflection",
                "why": "remove the 'robotic' or monotonic delivery characteristic of basic TTS systems"
            },
            "zcr": {
                "desc": "zero-crossing rate (fricative noise)",
                "action": "adjusting the harshness of 's' and 'f' sounds",
                "why": "prevent the unnatural metallic or buzzing artifacts common in synthetic audio"
            }
        }

        for feature, data in features_dict.items():
            if data["risk_score"] > risk_threshold and not feature.endswith("_series"):
                
                # Get specific context or fall back to generic
                ctx = feature_context.get(feature, {
                    "desc": feature.replace("_", " "),
                    "action": f"normalizing this {feature.replace('_', ' ')} metric",
                    "why": "better match the statistical distribution of authentic human speech baselines"
                })
                
                counterfactuals.append({
                    "feature": feature,
                    "observation": f"Anomalous {ctx['desc']} detected (Value: {data['value']:.2f}, Risk: {data['risk_score']*100:.0f}%).",
                    "suggestion": f"If this audio were authentic, {ctx['action']} would {ctx['why']}, thereby lowering the synthetic risk score.",
                    "impact_estimate": "Significant"
                })
                
        return counterfactuals

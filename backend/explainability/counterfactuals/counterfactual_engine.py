class CounterfactualEngine:
    """Level 1 analytical consensus sensitivity engine."""

    def __init__(self):
        pass

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
        return {
            "agent": agent_name,
            "verdict": details.get("verdict", "inconclusive"),
            "adjusted_confidence": adjusted_confidence,
            "adjusted_uncertainty": adjusted_uncertainty,
            "suppression_factor": suppression_factor,
            "effective_reliability": effective_reliability,
            "weight": weight,
        }

    def _support_totals(self, vectors):
        fake_support = 0.0
        real_support = 0.0
        for vector in vectors.values():
            confidence = vector["adjusted_confidence"]
            weight = vector["weight"]
            if vector["verdict"] == "fake":
                fake_support += confidence * weight
                real_support += (1.0 - confidence) * weight
            elif vector["verdict"] == "real":
                real_support += confidence * weight
                fake_support += (1.0 - confidence) * weight
        return fake_support, real_support

    def compute_consensus_sensitivity(self, calibrated_details, fake_probability=None, real_probability=None):
        """Compute local analytical sensitivity for calibrated consensus details."""
        vectors = {
            name: self._agent_vector(name, details)
            for name, details in (calibrated_details or {}).items()
            if details.get("verdict") in {"fake", "real"}
        }
        fake_support, real_support = self._support_totals(vectors)
        total_support = fake_support + real_support

        if total_support <= 0.0:
            baseline_fake = 0.5 if fake_probability is None else self._safe_float(fake_probability, 0.5)
            baseline_real = 0.5 if real_probability is None else self._safe_float(real_probability, 0.5)
            return {
                "method": "analytical_level_1",
                "baseline": {
                    "fake_probability": baseline_fake,
                    "real_probability": baseline_real,
                    "fake_support": fake_support,
                    "real_support": real_support,
                },
                "sensitivities": {
                    name: {
                        "gradient": 0.0,
                        "direction": "neutral",
                        "current_confidence": vector["adjusted_confidence"],
                        "weight": vector["weight"],
                        "estimated_delta_for_10pct": 0.0,
                        "statement": f"{name} has no local effect because its calibrated support is zero.",
                    }
                    for name, vector in vectors.items()
                },
                "summary": "Consensus sensitivity is neutral because calibrated support is zero.",
            }

        baseline_fake = fake_support / total_support
        baseline_real = real_support / total_support
        if fake_probability is not None:
            baseline_fake = self._safe_float(fake_probability, baseline_fake)
        if real_probability is not None:
            baseline_real = self._safe_float(real_probability, baseline_real)

        sensitivities = {}
        for name, vector in vectors.items():
            if vector["verdict"] == "fake":
                gradient = vector["weight"] / total_support
                direction = "increases_fake_probability"
                action = "decreased"
                effect = "decrease"
            elif vector["verdict"] == "real":
                gradient = -vector["weight"] / total_support
                direction = "decreases_fake_probability"
                action = "increased"
                effect = "decrease"
            else:
                gradient = 0.0
                direction = "neutral"
                action = "changed"
                effect = "change"

            delta_for_10pct = gradient * 0.10
            sensitivities[name] = {
                "gradient": gradient,
                "direction": direction,
                "current_confidence": vector["adjusted_confidence"],
                "weight": vector["weight"],
                "estimated_delta_for_10pct": delta_for_10pct,
                "statement": (
                    f"If {name} adjusted confidence {action} by 10%, "
                    f"fake probability would {effect} by about {abs(delta_for_10pct):.3f}."
                ),
            }

        ranked = sorted(sensitivities.items(), key=lambda item: abs(item[1]["gradient"]), reverse=True)
        if ranked:
            top_name, top = ranked[0]
            summary = f"{top_name} has the strongest local sensitivity ({top['gradient']:.3f})."
        else:
            summary = "No voting agents were available for analytical sensitivity."

        return {
            "method": "analytical_level_1",
            "baseline": {
                "fake_probability": baseline_fake,
                "real_probability": baseline_real,
                "fake_support": fake_support,
                "real_support": real_support,
            },
            "sensitivities": sensitivities,
            "summary": summary,
        }

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

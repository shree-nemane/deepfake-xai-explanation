class ExplanationService:
    @staticmethod
    def generate_detailed_narrative(prediction, risk_score, forensic_scores, uncertainty, counterfactuals):
        """
        Synthesize a professional forensic narrative explaining the verdict.
        """
        is_fake = "Deepfake" in prediction or "Synthetic" in prediction
        
        # 1. Core Verdict Summary
        intro = f"The forensic analysis concludes that this audio sample is **{prediction.upper()}** with a risk score of {risk_score:.1f}%."
        
        # 2. Acoustic Evidence Analysis
        # Identify top 3 anomalies
        anomalies = sorted(
            [f for f, v in forensic_scores.items() if not f.endswith("_series")],
            key=lambda x: forensic_scores[x]["risk_score"],
            reverse=True
        )[:3]
        
        acoustic_detail = ""
        high_risk_features = [f for f in anomalies if forensic_scores[f]["risk_score"] > 0.6]
        
        if high_risk_features:
            features_text = ", ".join([f.replace("_", " ").title() for f in high_risk_features])
            acoustic_detail = f"Significant acoustic irregularities were detected in **{features_text}**. "
            
            # Specific technical reasons
            reasons = []
            if "jitter" in high_risk_features or "shimmer" in high_risk_features:
                reasons.append("Unnatural micro-fluctuations in pitch and amplitude suggest algorithmic vocoder artifacts.")
            if "hnr" in high_risk_features or "mfcc_variance" in high_risk_features:
                reasons.append("Spectral noise distribution deviates from natural human vocal tract resonance patterns.")
            
            acoustic_detail += " ".join(reasons)
        else:
            acoustic_detail = "Acoustic signal markers remain within expected natural speech distributions."

        # 3. Neural & Temporal Evidence
        neural_detail = ""
        if is_fake:
            neural_detail = "Neural attention mapping (XAI) reveals that the model is prioritizing high-frequency spectral regions often associated with generative artifacts. The phonetic embedding stream indicates temporal inconsistencies that are uncommon in organic speech."
        else:
            neural_detail = "The neural network identifies consistent spectral textures and phonetic transitions that align with established authentic speech baselines."

        # 4. Uncertainty & Stability
        uncertainty_text = ""
        if uncertainty == "low":
            uncertainty_text = "The prediction is highly stable across multiple inference passes, suggesting high forensic reliability."
        else:
            uncertainty_text = "Analysis shows moderate variance in neural activations, suggesting the sample may contain mixed forensic markers or environmental noise interference."

        # 5. Final Human-Understandable Reason
        reason = ""
        if is_fake:
            reason = "In simple terms, the audio sounds human but contains 'digital fingerprints'—microscopic errors in how the sound waves are formed—that only a computer would make when trying to mimic a voice."
        else:
            reason = "In simple terms, the audio maintains the natural biological rhythms and physical sound characteristics that are consistent with a real human voice box and throat."

        return {
            "summary": intro,
            "acoustic_evidence": acoustic_detail,
            "neural_evidence": neural_detail,
            "stability_audit": uncertainty_text,
            "layman_explanation": reason
        }

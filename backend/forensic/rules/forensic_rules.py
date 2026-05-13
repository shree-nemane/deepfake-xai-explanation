import numpy as np
from backend.forensic.anomaly.zscore_engine import compute_abnormality_scores, compute_overall_anomaly
from backend.forensic.anomaly.isolation_forest import ForensicAnomalyDetector

class ForensicRuleEngine:
    def __init__(self):
        self.anomaly_detector = ForensicAnomalyDetector()

    def apply_rules(self, features):
        """
        Apply hybrid rules: Univariate (Z-Score) and Multivariate (Isolation Forest).
        """
        forensic_scores = compute_abnormality_scores(features)
        
        feature_vector = np.array([forensic_scores[f]["value"] for f in [
            "zcr", "spectral_centroid", "spectral_bandwidth", "mfcc_variance", 
            "pitch_variation", "spectral_rolloff", "chroma_consistency", 
            "rms_energy", "jitter", "shimmer", "hnr"
        ]])
        
        multivariate_anomaly = self.anomaly_detector.predict_anomaly_score(feature_vector)
        univariate_anomaly = compute_overall_anomaly(forensic_scores)
        
        overall_anomaly = (univariate_anomaly * 0.6 + multivariate_anomaly * 0.4)
        
        return forensic_scores, overall_anomaly

    @staticmethod
    def get_decision_category(risk_score):
        """
        Map risk score to blueprint decision categories.
        """
        if risk_score <= 25:
            return "Likely Authentic"
        elif risk_score <= 50:
            return "Suspicious"
        elif risk_score <= 75:
            return "Likely Synthetic"
        else:
            return "High-Confidence Deepfake"

    @staticmethod
    def generate_verdict_reason(prediction, overall_anomaly, forensic_scores):
        """
        Synthesize a human-readable reason for the verdict.
        """
        top_anomalies = sorted(
            [f for f, v in forensic_scores.items() if not f.endswith("_series")],
            key=lambda x: forensic_scores[x]["risk_score"],
            reverse=True
        )[:2]
        
        reasons = []
        for f in top_anomalies:
            if forensic_scores[f]["risk_score"] > 0.5:
                reasons.append(f.replace("_", " "))

        if "Deepfake" in prediction or "Synthetic" in prediction:
            if reasons:
                return f"Analysis detected significant synthetic artifacts in {', '.join(reasons)}. Neural patterns align with generative models."
            return "Neural pattern analysis indicates synthetic origin despite subtle acoustic markers."
        else:
            if overall_anomaly > 0.3:
                return "Acoustic markers show minor instabilities, but neural patterns align with natural speech behavior."
            return "All forensic markers and neural patterns align with natural, authentic speech distributions."

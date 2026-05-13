import numpy as np

# Baseline statistics for natural speech (Real-world estimates)
REAL_SPEECH_BASELINES = {
    "zcr": {"mean": 0.08, "std": 0.03},
    "spectral_centroid": {"mean": 2500.0, "std": 500.0},
    "spectral_bandwidth": {"mean": 3000.0, "std": 400.0},
    "mfcc_variance": {"mean": 120.0, "std": 30.0},
    "pitch_variation": {"mean": 20.0, "std": 5.0},
    "spectral_rolloff": {"mean": 4500.0, "std": 800.0},
    "chroma_consistency": {"mean": 0.05, "std": 0.02},
    "rms_energy": {"mean": 0.15, "std": 0.05},
    "jitter": {"mean": 0.5, "std": 0.2},
    "shimmer": {"mean": 0.02, "std": 0.01},
    "hnr": {"mean": 15.0, "std": 5.0}
}

def compute_abnormality_scores(features):
    """
    Compute Z-Scores for each feature relative to natural speech baselines.
    """
    scores = {}
    for feature, value in features.items():
        if feature in REAL_SPEECH_BASELINES:
            baseline = REAL_SPEECH_BASELINES[feature]
            z_score = abs(value - baseline["mean"]) / (baseline["std"] + 1e-8)
            
            # Map Z-score to risk (0 to 1)
            # z < 1: normal (0-0.2)
            # 1-2: mild (0.2-0.5)
            # 2-3: moderate (0.5-0.8)
            # > 3: severe (0.8-1.0)
            risk = min(1.0, z_score / 4.0) 
            
            scores[feature] = {
                "value": value,
                "z_score": z_score,
                "risk_score": risk
            }
        else:
            scores[feature] = {
                "value": value,
                "z_score": 0.0,
                "risk_score": 0.0
            }
            
    return scores

def compute_overall_anomaly(risk_scores):
    """
    Combine individual risk scores into an overall anomaly score.
    """
    if not risk_scores:
        return 0.0
    
    # Weighted average or max? Max is more forensic-safe.
    # But let's use weighted average of top 3 anomalies.
    sorted_risks = sorted([v["risk_score"] for v in risk_scores.values()], reverse=True)
    top_3 = sorted_risks[:3]
    return np.mean(top_3) if top_3 else 0.0

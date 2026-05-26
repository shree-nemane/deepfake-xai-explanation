import numpy as np
import logging

from backend.agents.base_agent import BaseAgent
from backend.orchestration.agent_registry import agent_registry
from backend.forensic.features.acoustic_features import extract_all_features
from backend.forensic.anomaly.zscore_engine import compute_abnormality_scores, compute_overall_anomaly

logger = logging.getLogger(__name__)

# Anomaly threshold: scores above this lean towards fake (raised post-UAT to reduce false fake)
_ANOMALY_THRESHOLD = 0.52
# Scaling factor to map distance-from-threshold into [0, 0.99] confidence
_CONFIDENCE_SCALE = 2.2


class AcousticAgent(BaseAgent):
    """
    Acoustic forensic agent that evaluates biological plausibility of speech
    by extracting real acoustic features (ZCR, spectral centroid, MFCCs, pitch,
    jitter, shimmer, HNR, etc.) and scoring their deviation from natural-speech
    baselines via z-score anomaly detection.
    """

    def __init__(self):
        super().__init__(
            name="acoustic",
            sample_rate=48000,
            description="Biological plausibility analysis via acoustic feature z-score anomaly detection.",
        )

    # ------------------------------------------------------------------ #
    #  Core analysis
    # ------------------------------------------------------------------ #
    def analyze_chunk(self, audio_chunk: np.ndarray) -> dict:
        """
        Analyse a single audio chunk for acoustic anomalies.

        Parameters
        ----------
        audio_chunk : np.ndarray
            Raw audio samples at 48 kHz.

        Returns
        -------
        dict  with keys: verdict, confidence, uncertainty, evidence
        """
        try:
            # --- 1. Feature extraction ---------------------------------
            features = extract_all_features(audio_chunk, self.sample_rate)

            # --- 2. Z-score anomaly scoring ----------------------------
            forensic_scores = compute_abnormality_scores(features)

            # --- 3. Overall anomaly (0-1) ------------------------------
            overall_anomaly = compute_overall_anomaly(forensic_scores)

            # --- 4. Verdict -------------------------------------------
            verdict = "fake" if overall_anomaly > _ANOMALY_THRESHOLD else "real"

            # --- 5. Confidence ----------------------------------------
            confidence = min(
                abs(overall_anomaly - _ANOMALY_THRESHOLD) * _CONFIDENCE_SCALE,
                0.99,
            )

            # --- 6. Uncertainty (inversely related to confidence) ------
            uncertainty = round(1.0 - confidence, 4)

            # --- 7. Evidence: top-3 most anomalous features ------------
            ranked = sorted(
                forensic_scores.items(),
                key=lambda kv: kv[1]["risk_score"],
                reverse=True,
            )
            top_anomalies = {
                feat: {
                    "value": round(info["value"], 6),
                    "z_score": round(info["z_score"], 4),
                    "risk_score": round(info["risk_score"], 4),
                }
                for feat, info in ranked[:3]
            }

            return {
                "verdict": verdict,
                "confidence": round(confidence, 4),
                "uncertainty": uncertainty,
                "evidence": {
                    "overall_anomaly": round(overall_anomaly, 4),
                    "top_anomalous_features": top_anomalies,
                },
            }

        except Exception as exc:
            # Short chunks, silent audio, or any librosa failure
            logger.warning(
                "AcousticAgent: feature extraction failed (%s). "
                "Returning inconclusive result.",
                exc,
            )
            return {
                "verdict": "inconclusive",
                "confidence": 0.0,
                "uncertainty": 1.0,
                "evidence": {
                    "error": str(exc),
                    "fallback_reason": "feature_extraction_failed",
                    "note": "Feature extraction failed; excluded from real/fake voting.",
                },
            }


# ------------------------------------------------------------------ #
#  Register with the central agent registry
# ------------------------------------------------------------------ #
agent_registry.register("acoustic", AcousticAgent())

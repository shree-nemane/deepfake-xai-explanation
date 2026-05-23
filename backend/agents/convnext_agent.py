import numpy as np
import logging
import torch
import torch.nn.functional as F

from backend.agents.base_agent import BaseAgent
from backend.orchestration.agent_registry import agent_registry
from backend.agents.model_hub import model_hub
from backend.forensic.features.acoustic_features import generate_spectrogram

logger = logging.getLogger(__name__)

# ── Confidence calibration knobs ─────────────────────────────────────
_MIN_CHUNK_SAMPLES = 1024          # reject chunks shorter than this
_SILENCE_RMS_THRESHOLD = 1e-6     # treat as silence below this RMS
_LOW_CONF_DEFAULT = 0.10          # fallback confidence on error


class ConvNextAgent(BaseAgent):
    """
    Spectral-artifact forensic agent.

    Converts raw 48 kHz audio into a mel-spectrogram image, runs it through
    the ConvNext classifier (class 0 = fake, class 1 = real) via model_hub,
    and optionally produces a Grad-CAM heatmap for explainability.
    """

    def __init__(self):
        super().__init__(
            name="convnext",
            sample_rate=48000,
            description="Spectral artifact analysis via Mel-Spectrogram + ConvNext classification.",
        )

    # ------------------------------------------------------------------ #
    #  Core analysis
    # ------------------------------------------------------------------ #
    def analyze_chunk(self, audio_chunk: np.ndarray) -> dict:
        """
        Analyse a single audio chunk for spectral deepfake artifacts.

        Parameters
        ----------
        audio_chunk : np.ndarray
            Raw audio samples at 48 kHz.

        Returns
        -------
        dict  with keys: verdict, confidence, uncertainty, evidence
        """
        try:
            # --- 0. Sanity checks on the audio chunk --------------------
            if audio_chunk is None or len(audio_chunk) < _MIN_CHUNK_SAMPLES:
                return self._fallback_verdict(
                    reason=f"Chunk too short ({0 if audio_chunk is None else len(audio_chunk)} samples)."
                )

            rms = float(np.sqrt(np.mean(audio_chunk.astype(np.float64) ** 2)))
            if rms < _SILENCE_RMS_THRESHOLD:
                return self._fallback_verdict(reason="Silent or near-silent chunk.")

            # --- 1. Mel-spectrogram tensor (1, 3, 224, 224) -------------
            input_tensor = generate_spectrogram(audio_chunk, self.sample_rate)
            input_tensor = input_tensor.to(model_hub.device)

            # --- 2. Forward pass → logits (1, 2): [fake, real] ----------
            with torch.no_grad():
                logits = model_hub.convnext_handler.get_logits(input_tensor)

            probs = F.softmax(logits, dim=1)           # (1, 2)
            fake_prob = float(probs[0, 0])
            real_prob = float(probs[0, 1])

            # --- 3. Verdict & confidence --------------------------------
            if fake_prob >= real_prob:
                verdict = "fake"
                confidence = round(fake_prob, 4)
            else:
                verdict = "real"
                confidence = round(real_prob, 4)

            uncertainty = round(1.0 - confidence, 4)

            # --- 4. Spectral-analysis evidence flags --------------------
            #   Checkerboard artifacts often manifest as high-frequency
            #   periodic patterns; frequency smoothing suggests low-pass
            #   filtering typical of neural vocoders.
            checkerboard_artifacts = fake_prob > 0.70
            frequency_smoothing = fake_prob > 0.65

            # --- 5. Grad-CAM heatmap (optional, best-effort) -----------
            heatmap = self._generate_heatmap(input_tensor)

            return {
                "verdict": verdict,
                "confidence": confidence,
                "uncertainty": uncertainty,
                "evidence": {
                    "fake_probability": round(fake_prob, 4),
                    "real_probability": round(real_prob, 4),
                    "checkerboard_artifacts": checkerboard_artifacts,
                    "frequency_smoothing": frequency_smoothing,
                    "gradcam_heatmap": heatmap,
                },
            }

        except Exception as exc:
            logger.warning("ConvNextAgent: inference failed (%s).", exc)
            return self._fallback_verdict(reason=str(exc))

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _generate_heatmap(input_tensor: torch.Tensor):
        """Best-effort Grad-CAM; returns numpy heatmap or None."""
        try:
            heatmap = model_hub.gradcam_engine.generate(input_tensor)
            return heatmap
        except Exception as exc:
            logger.debug("Grad-CAM generation failed: %s", exc)
            return None

    @staticmethod
    def _fallback_verdict(reason: str) -> dict:
        """Return a visible inconclusive verdict when inference cannot run."""
        return {
            "verdict": "inconclusive",
            "confidence": 0.0,
            "uncertainty": 1.0,
            "evidence": {
                "error": reason,
                "fallback_reason": "inference_unavailable",
                "note": "Inference unavailable; excluded from real/fake voting.",
            },
        }


# ------------------------------------------------------------------ #
#  Register with the central agent registry
# ------------------------------------------------------------------ #
agent_registry.register("convnext", ConvNextAgent())

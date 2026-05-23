"""
WavLM Agent — Phonetic realism & temporal instability analysis.

Uses WavLM (via the shared model_hub) to extract
frame-level embeddings and derive forensic features:
  • phonetic_instability  – mean abs frame-to-frame delta (synthetic speech
                            tends to have values > 0.12)
  • temporal_entropy      – variance of hidden states across the time axis
  • embedding_norm        – L2 norm of the mean-pooled embedding vector

Verdict: phonetic_instability > THRESHOLD → fake.
"""

import logging

import numpy as np
import torch

from backend.agents.base_agent import BaseAgent
from backend.agents.model_hub import model_hub
from backend.orchestration.agent_registry import agent_registry

logger = logging.getLogger(__name__)

# ── Empirical threshold for phonetic instability ───────────────────────
_INSTABILITY_THRESHOLD = 0.12

# Minimum number of samples (~50 ms at 16 kHz) to attempt inference
_MIN_SAMPLES = 800


class WavLMAgent(BaseAgent):
    """Phonetic analysis agent backed by WavLM."""

    def __init__(self):
        super().__init__(
            name="wavlm",
            sample_rate=16000,
            description="Phonetic realism and temporal instability analysis.",
        )

    # ────────────────────────────────────────────────────────────────────
    def analyze_chunk(self, audio_chunk: np.ndarray) -> dict:
        """
        Analyse a 16 kHz mono audio chunk and return a forensic verdict.

        Parameters
        ----------
        audio_chunk : np.ndarray
            1-D float array of audio samples at 16 kHz.

        Returns
        -------
        dict  with keys  verdict, confidence, uncertainty, evidence.
        """
        try:
            # ── guard: too-short / silent audio ────────────────────────
            if audio_chunk is None or len(audio_chunk) < _MIN_SAMPLES:
                return self._fallback_result(
                    reason="audio_too_short",
                    detail=f"need >= {_MIN_SAMPLES} samples, got "
                           f"{0 if audio_chunk is None else len(audio_chunk)}",
                )

            rms = float(np.sqrt(np.mean(audio_chunk.astype(np.float64) ** 2)))
            if rms < 1e-6:
                return self._fallback_result(
                    reason="silent_audio",
                    detail=f"RMS={rms:.2e}",
                )

            # ── extract embeddings via shared model hub ────────────────
            mean_embeddings, phonetic_instability = (
                model_hub.wavlm_handler.extract_embeddings(audio_chunk, sr=16000)
            )

            # ── temporal entropy (variance across time dim) ────────────
            # Re-run a forward pass is wasteful; instead compute from
            # the mean-pooled embedding's spread.  For a richer signal
            # we do a lightweight re-inference to grab last_hidden_state.
            temporal_entropy = self._compute_temporal_entropy(audio_chunk)

            # ── embedding norm ─────────────────────────────────────────
            embedding_norm = float(torch.norm(mean_embeddings, p=2).item())

            # ── verdict ────────────────────────────────────────────────
            deviation = phonetic_instability - _INSTABILITY_THRESHOLD
            is_fake = deviation > 0.0

            # confidence: how far from the decision boundary (sigmoid-like)
            # scale factor chosen so that ±0.06 deviation ≈ 0.73 confidence
            fake_probability = float(1.0 / (1.0 + np.exp(-25.0 * deviation)))
            confidence = float(max(fake_probability, 1.0 - fake_probability))
            confidence = np.clip(confidence, 0.01, 0.99)

            # uncertainty: inverse of confidence spread
            uncertainty = float(1.0 - confidence)
            uncertainty = np.clip(uncertainty, 0.01, 0.99)

            return {
                "verdict": "fake" if is_fake else "real",
                "confidence": float(confidence),
                "uncertainty": float(uncertainty),
                "evidence": {
                    "phonetic_instability": float(phonetic_instability),
                    "temporal_entropy": float(temporal_entropy),
                    "embedding_norm": float(embedding_norm),
                    "instability_threshold": _INSTABILITY_THRESHOLD,
                    "deviation_from_threshold": float(deviation),
                    "fake_probability": float(fake_probability),
                },
            }

        except Exception as exc:
            logger.exception("WavLMAgent.analyze_chunk failed: %s", exc)
            return self._fallback_result(reason="inference_error", detail=str(exc))

    # ── helpers ─────────────────────────────────────────────────────────
    def _compute_temporal_entropy(self, audio_chunk: np.ndarray) -> float:
        """
        Compute temporal entropy from last_hidden_state variance across
        the time (sequence) dimension.
        """
        handler = model_hub.wavlm_handler
        inputs = handler.processor(
            audio_chunk, sampling_rate=16000, return_tensors="pt", padding=True
        )
        inputs = {k: v.to(handler.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = handler.model(**inputs)
            hidden = outputs.last_hidden_state  # (1, T, H)
            # Variance per hidden dim across time, then mean
            temporal_var = torch.var(hidden, dim=1).mean()
            return float(temporal_var.item())

    @staticmethod
    def _fallback_result(reason: str, detail: str = "") -> dict:
        """Return a visible inconclusive verdict when inference cannot run."""
        return {
            "verdict": "inconclusive",
            "confidence": 0.0,
            "uncertainty": 1.0,
            "evidence": {
                "phonetic_instability": 0.0,
                "temporal_entropy": 0.0,
                "embedding_norm": 0.0,
                "fallback_reason": reason,
                "fallback_detail": detail,
            },
        }


# ── Register with the global agent registry ───────────────────────────
agent_registry.register("wavlm", WavLMAgent())

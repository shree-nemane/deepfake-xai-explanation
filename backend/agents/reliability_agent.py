from backend.agents.base_agent import BaseAgent
from backend.orchestration.agent_registry import agent_registry
import numpy as np
import librosa


class ReliabilityAgent(BaseAgent):
    """
    Estimates audio signal trustworthiness by measuring real signal-quality
    metrics: SNR (via HPSS), clipping ratio, RMS energy, and spectral flatness.
    """

    def __init__(self):
        super().__init__(
            name="reliability",
            sample_rate=48000,
            description="Estimates trustworthiness (clipping, noise, compression).",
        )

    def analyze_chunk(self, audio_chunk: np.ndarray) -> dict:
        try:
            audio = audio_chunk.astype(np.float32)

            # ── Guard: silent / near-empty chunk ──────────────────────
            if audio.size == 0 or np.max(np.abs(audio)) < 1e-10:
                return {
                    "verdict": "unreliable",
                    "confidence": 0.1,
                    "uncertainty": 0.9,
                    "evidence": {
                        "snr_db": 0.0,
                        "clipping_ratio": 0.0,
                        "rms_energy": 0.0,
                        "spectral_flatness": 0.0,
                        "reliability_score": 0.1,
                        "note": "silent or empty audio chunk",
                    },
                }

            # ── 1. Signal-to-Noise Ratio via HPSS ────────────────────
            stft = librosa.stft(audio)
            harmonic, percussive = librosa.decompose.hpss(stft)
            signal_power = np.mean(np.abs(harmonic) ** 2 + np.abs(percussive) ** 2)
            noise = stft - harmonic - percussive
            noise_power = np.mean(np.abs(noise) ** 2)
            if noise_power < 1e-12:
                snr_db = 60.0  # effectively clean
            else:
                snr_db = float(10.0 * np.log10(signal_power / noise_power))

            # ── 2. Clipping Ratio ─────────────────────────────────────
            peak = np.max(np.abs(audio))
            clipping_threshold = 0.99 * peak
            clipped_samples = int(np.sum(np.abs(audio) > clipping_threshold))
            clipping_ratio = float(clipped_samples / audio.size)

            # ── 3. RMS Energy ─────────────────────────────────────────
            rms_energy = float(np.sqrt(np.mean(audio ** 2)))

            # ── 4. Spectral Flatness (compression artefact proxy) ─────
            sf = librosa.feature.spectral_flatness(y=audio)
            spectral_flatness = float(np.mean(sf))

            # ── 5. Composite Reliability Score ────────────────────────
            reliability_score = 1.0
            if snr_db < 15.0:
                reliability_score -= 0.3
            if clipping_ratio > 0.01:
                reliability_score -= 0.2
            if spectral_flatness > 0.5:
                reliability_score -= 0.2
            if rms_energy < 0.01:
                reliability_score -= 0.1
            reliability_score = float(np.clip(reliability_score, 0.1, 1.0))

            # ── 6. Verdict ────────────────────────────────────────────
            verdict = "reliable" if reliability_score > 0.5 else "unreliable"

            return {
                "verdict": verdict,
                "confidence": reliability_score,
                "uncertainty": round(1.0 - reliability_score, 4),
                "evidence": {
                    "snr_db": round(snr_db, 2),
                    "clipping_ratio": round(clipping_ratio, 6),
                    "rms_energy": round(rms_energy, 6),
                    "spectral_flatness": round(spectral_flatness, 6),
                    "reliability_score": round(reliability_score, 4),
                },
            }

        except Exception as exc:
            return {
                "verdict": "unreliable",
                "confidence": 0.1,
                "uncertainty": 0.9,
                "evidence": {
                    "error": str(exc),
                    "reliability_score": 0.1,
                },
            }


agent_registry.register("reliability", ReliabilityAgent())

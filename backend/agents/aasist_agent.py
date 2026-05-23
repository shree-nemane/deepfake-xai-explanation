from backend.agents.base_agent import BaseAgent
from backend.orchestration.agent_registry import agent_registry
import numpy as np
import librosa


class AASISTAgent(BaseAgent):
    """
    Waveform-level anti-spoofing agent.

    Instead of a pretrained AASIST neural network, this implementation
    performs four complementary signal-level analyses that target artifacts
    commonly introduced by neural vocoders, text-to-speech systems, and
    voice-conversion pipelines:

      1. Phase coherence — synthetic audio tends to have unnaturally smooth
         inter-frame phase transitions.
      2. Sub-band energy ratio — TTS / vocoder outputs often exhibit
         abnormal spectral energy distribution across low / mid / high bands.
      3. Zero-crossing rate irregularity — real speech has higher ZCR
         variability; synthetic audio is more uniform.
      4. Waveform periodicity — vocoder outputs tend to produce stronger
         autocorrelation peaks than natural speech.

    The four metrics are fused via a fixed weighted average to produce a
    final spoof score in [0, 1].
    """

    # ── Fusion weights ──────────────────────────────────────────────
    _W_PHASE = 0.35
    _W_ENERGY = 0.25
    _W_ZCR = 0.20
    _W_PERIODICITY = 0.20

    # ── STFT / analysis parameters ──────────────────────────────────
    _N_FFT = 1024
    _HOP_LENGTH = 256
    _ZCR_FRAME_LENGTH = 512

    def __init__(self):
        super().__init__(
            name="aasist",
            sample_rate=16000,
            description="Waveform-level anti-spoofing specialized expert.",
        )

    # ================================================================
    #  Public API
    # ================================================================

    def analyze_chunk(self, audio_chunk: np.ndarray) -> dict:
        """Analyze a 16 kHz audio chunk and return a spoofing verdict."""
        try:
            audio = np.asarray(audio_chunk, dtype=np.float32).squeeze()

            # --- guard: too-short or silent audio ----------------------
            if audio.size < self._N_FFT:
                return self._fallback_result(
                    reason="audio_too_short",
                    detail=f"Only {audio.size} samples; need >= {self._N_FFT}.",
                )

            rms = np.sqrt(np.mean(audio ** 2))
            if rms < 1e-7:
                return self._fallback_result(
                    reason="silent_audio",
                    detail=f"RMS energy {rms:.2e} below silence threshold.",
                )

            # --- compute sub-scores ------------------------------------
            phase_anomaly = self._phase_coherence(audio)
            energy_anomaly = self._subband_energy(audio)
            zcr_anomaly = self._zcr_irregularity(audio)
            periodicity_anomaly = self._waveform_periodicity(audio)

            # --- weighted fusion ---------------------------------------
            spoof_score = (
                self._W_PHASE * phase_anomaly
                + self._W_ENERGY * energy_anomaly
                + self._W_ZCR * zcr_anomaly
                + self._W_PERIODICITY * periodicity_anomaly
            )
            spoof_score = float(np.clip(spoof_score, 0.0, 1.0))

            is_fake = spoof_score > 0.5
            # Confidence scales with distance from the decision boundary.
            distance = abs(spoof_score - 0.5)
            confidence = float(np.clip(0.5 + distance, 0.0, 1.0))
            # Uncertainty is inversely related to confidence.
            uncertainty = float(np.clip(1.0 - confidence, 0.0, 1.0))

            return {
                "verdict": "fake" if is_fake else "real",
                "confidence": confidence,
                "uncertainty": uncertainty,
                "evidence": {
                    "spoof_score": round(spoof_score, 4),
                    "phase_anomaly": round(float(phase_anomaly), 4),
                    "energy_anomaly": round(float(energy_anomaly), 4),
                    "zcr_anomaly": round(float(zcr_anomaly), 4),
                    "periodicity_anomaly": round(float(periodicity_anomaly), 4),
                    "logical_access_attack": spoof_score > 0.7,
                    "vocoder_inconsistencies": spoof_score > 0.6,
                },
            }

        except Exception as exc:
            return self._fallback_result(
                reason="analysis_error",
                detail=str(exc),
            )

    # ================================================================
    #  Feature extractors
    # ================================================================

    def _phase_coherence(self, audio: np.ndarray) -> float:
        """
        Measure inter-frame phase smoothness.

        Natural speech exhibits noisy, high-variance phase differences
        between consecutive STFT frames.  Synthetic audio from neural
        vocoders tends to produce much smoother phase trajectories.

        Returns a score in [0, 1] where 1 = suspiciously smooth (synthetic).
        """
        stft = librosa.stft(audio, n_fft=self._N_FFT, hop_length=self._HOP_LENGTH)
        phase = np.angle(stft)  # (freq_bins, time_frames)

        if phase.shape[1] < 2:
            return 0.5  # not enough frames to judge

        # Frame-to-frame phase difference (unwrapped to avoid ±π jumps)
        phase_diff = np.diff(phase, axis=1)
        # Wrap to [-π, π]
        phase_diff = np.arctan2(np.sin(phase_diff), np.cos(phase_diff))

        # Variance of the phase difference across time, per frequency bin
        var_per_bin = np.var(phase_diff, axis=1)
        mean_var = float(np.mean(var_per_bin))

        # Empirical mapping: natural speech ≈ 1.0–2.0 rad² variance;
        # synthetic ≈ 0.1–0.5 rad².  A sigmoid-like mapping centers the
        # transition around 0.6 rad².
        score = 1.0 / (1.0 + np.exp(5.0 * (mean_var - 0.6)))
        return float(np.clip(score, 0.0, 1.0))

    def _subband_energy(self, audio: np.ndarray) -> float:
        """
        Compute spectral energy in three sub-bands and detect anomalies.

        Bands (for 16 kHz, Nyquist = 8 kHz):
          Low  :  0 – 1 kHz
          Mid  :  1 – 4 kHz
          High :  4 – 8 kHz

        TTS / vocoder outputs frequently under- or over-represent the
        high-frequency band relative to natural speech.

        Returns a score in [0, 1] where 1 = abnormal distribution (synthetic).
        """
        stft_mag = np.abs(
            librosa.stft(audio, n_fft=self._N_FFT, hop_length=self._HOP_LENGTH)
        )
        n_bins = stft_mag.shape[0]
        freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self._N_FFT)

        # Bin masks
        low_mask = freqs < 1000
        mid_mask = (freqs >= 1000) & (freqs < 4000)
        high_mask = freqs >= 4000

        total_energy = np.sum(stft_mag ** 2) + 1e-12
        low_ratio = np.sum(stft_mag[low_mask] ** 2) / total_energy
        mid_ratio = np.sum(stft_mag[mid_mask] ** 2) / total_energy
        high_ratio = np.sum(stft_mag[high_mask] ** 2) / total_energy

        # Expected ratios for natural speech (rough empirical centers)
        # Low ≈ 0.45, Mid ≈ 0.40, High ≈ 0.15
        deviation = (
            abs(low_ratio - 0.45)
            + abs(mid_ratio - 0.40)
            + abs(high_ratio - 0.15)
        )
        # Normalize: maximum possible deviation sum ≈ 2.0
        score = float(np.clip(deviation / 0.8, 0.0, 1.0))
        return score

    def _zcr_irregularity(self, audio: np.ndarray) -> float:
        """
        Measure uniformity of zero-crossing rate across short frames.

        Natural speech shows large ZCR swings between voiced (low ZCR)
        and unvoiced (high ZCR) segments.  Vocoder-generated audio has
        a more uniform ZCR profile.

        Returns a score in [0, 1] where 1 = suspiciously uniform (synthetic).
        """
        zcr = librosa.feature.zero_crossing_rate(
            audio,
            frame_length=self._ZCR_FRAME_LENGTH,
            hop_length=self._HOP_LENGTH,
        )[0]

        if zcr.size < 2:
            return 0.5

        zcr_var = float(np.var(zcr))
        # Natural speech ZCR variance is typically > 0.005;
        # synthetic tends to sit below 0.002.
        score = 1.0 / (1.0 + np.exp(800.0 * (zcr_var - 0.003)))
        return float(np.clip(score, 0.0, 1.0))

    def _waveform_periodicity(self, audio: np.ndarray) -> float:
        """
        Estimate the strength of the dominant autocorrelation peak.

        Neural vocoders (WaveNet, WaveRNN, HiFi-GAN, etc.) tend to
        produce waveforms with abnormally strong periodicity compared
        to natural glottal excitation.

        Returns a score in [0, 1] where 1 = excessively periodic (synthetic).
        """
        # Limit analysis to first 16000 samples (1 s) for speed
        segment = audio[: self.sample_rate]
        segment = segment - np.mean(segment)
        norm = np.dot(segment, segment)
        if norm < 1e-12:
            return 0.5

        # Full autocorrelation via FFT
        n = len(segment)
        fft_size = 1
        while fft_size < 2 * n:
            fft_size *= 2
        fft_seg = np.fft.rfft(segment, n=fft_size)
        acf = np.fft.irfft(fft_seg * np.conj(fft_seg))[:n]
        acf = acf / (norm + 1e-12)  # normalize so acf[0] ≈ 1

        # Search for peaks in plausible pitch range (50 Hz – 500 Hz)
        min_lag = self.sample_rate // 500  # 32 @ 16 kHz
        max_lag = min(self.sample_rate // 50, n - 1)  # 320 @ 16 kHz

        if max_lag <= min_lag:
            return 0.5

        acf_region = acf[min_lag : max_lag + 1]
        peak_strength = float(np.max(acf_region))

        # Natural speech: peak ≈ 0.3–0.6; vocoder: peak ≈ 0.7–0.95.
        score = float(np.clip((peak_strength - 0.3) / 0.5, 0.0, 1.0))
        return score

    # ================================================================
    #  Helpers
    # ================================================================

    @staticmethod
    def _fallback_result(reason: str, detail: str) -> dict:
        """Return a visible inconclusive result on edge-case inputs."""
        return {
            "verdict": "inconclusive",
            "confidence": 0.0,
            "uncertainty": 1.0,
            "evidence": {
                "spoof_score": 0.0,
                "phase_anomaly": 0.0,
                "energy_anomaly": 0.0,
                "zcr_anomaly": 0.0,
                "periodicity_anomaly": 0.0,
                "fallback_reason": reason,
                "fallback_detail": detail,
            },
        }


# ── Register with the global agent registry ──────────────────────────
agent_registry.register("aasist", AASISTAgent())

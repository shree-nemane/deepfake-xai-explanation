import librosa
import numpy as np
import pyloudnorm as pyln
import torch
import warnings
import os

# Suppress PyTorch warnings for VAD load
warnings.filterwarnings("ignore", message=".*weights_only.*")

class AudioProcessor:
    """Forensic-grade audio normalization and segmentation system."""
    
    def __init__(self):
        # Load Silero VAD
        self.vad_model, self.vad_utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        (self.get_speech_timestamps, _, self.read_audio, _, _) = self.vad_utils
        
    def validate_audio(self, file_path, y, sr):
        """Validates audio minimum requirements, codecs, and severe clipping."""
        # 1. Unsupported Codec Check
        _, ext = os.path.splitext(file_path.lower())
        unsupported = ['.m4a', '.wma', '.amr']
        if ext in unsupported:
            return False, f"Codec {ext} is currently unsupported for deterministic forensic analysis."
            
        # 2. Minimum Duration
        duration = librosa.get_duration(y=y, sr=sr)
        if duration < 1.0:
            return False, f"Audio too short ({duration:.2f}s). Minimum 1s required."
            
        # 3. Silence / Corruption
        if np.max(np.abs(y)) < 1e-4:
            return False, "Audio is silent or severely corrupted."
            
        # 4. Severe Global Clipping Detection
        clip_ratio = np.sum(np.abs(y) > 0.99) / len(y)
        if clip_ratio > 0.05:
            warnings.warn(f"Severe clipping detected ({clip_ratio*100:.2f}%). Reliability may be degraded.")
            
        return True, "Valid"

    def apply_vad(self, audio_tensor, sr=16000):
        """Isolate active speech to remove silence-only regions."""
        # Added min_speech_duration_ms and speech_pad_ms to preserve weak speech and breath regions
        speech_timestamps = self.get_speech_timestamps(
            audio_tensor, 
            self.vad_model, 
            sampling_rate=sr,
            min_speech_duration_ms=100, # Lowered to catch short breaths/weak speech
            speech_pad_ms=250 # Padded aggressively to avoid clipping phoneme tails
        )
        if not speech_timestamps:
            return audio_tensor # Fallback if VAD fails to find speech
            
        # Concatenate active speech segments
        active_speech = torch.cat([audio_tensor[ts['start']:ts['end']] for ts in speech_timestamps])
        return active_speech

    def normalize_lufs(self, y, sr, target_lufs=-23.0):
        """LUFS normalization for consistent loudness. Returns normalized audio and metadata."""
        meter = pyln.Meter(sr)
        metadata = {"original_lufs": None, "target_lufs": target_lufs, "gain_applied": 0.0}
        
        try:
            loudness = meter.integrated_loudness(y)
            metadata["original_lufs"] = loudness
            
            y_norm = pyln.normalize.loudness(y, loudness, target_lufs)
            
            # Estimate gain applied (approximate)
            if np.max(np.abs(y)) > 0:
                metadata["gain_applied"] = np.mean(np.abs(y_norm)) / np.mean(np.abs(y))
                
            return y_norm, metadata
        except Exception:
            # Fallback if audio is too short for pyloudnorm or silent
            max_val = np.max(np.abs(y))
            if max_val > 0:
                metadata["gain_applied"] = 1.0 / max_val
                return y / max_val, metadata
            return y, metadata

    def process_dual_stream(self, file_path):
        """
        Creates 16kHz and 48kHz streams.
        Applies VAD and LUFS normalization.
        """
        # Load at highest required SR
        y_48k, sr_48k = librosa.load(file_path, sr=48000)
        original_duration = librosa.get_duration(y=y_48k, sr=sr_48k)
        original_peak = float(np.max(np.abs(y_48k))) if len(y_48k) else 0.0
        original_rms = float(np.sqrt(np.mean(y_48k ** 2))) if len(y_48k) else 0.0
        clipping_ratio = float(np.sum(np.abs(y_48k) > 0.99) / len(y_48k)) if len(y_48k) else 0.0
        
        is_valid, msg = self.validate_audio(file_path, y_48k, sr_48k)
        if not is_valid:
            raise ValueError(msg)
            
        # Normalize LUFS
        y_48k_norm, lufs_metadata = self.normalize_lufs(y_48k, sr_48k)
        
        # Downsample for the 16k stream
        y_16k_norm = librosa.resample(y_48k_norm, orig_sr=48000, target_sr=16000)
        
        # Apply VAD on 16k stream to find speech boundaries
        tensor_16k = torch.tensor(y_16k_norm, dtype=torch.float32)
        
        # Pass preservation parameters here as well
        speech_timestamps = self.get_speech_timestamps(
            tensor_16k, 
            self.vad_model, 
            sampling_rate=16000,
            min_speech_duration_ms=100,
            speech_pad_ms=250
        )
        
        # We will use the timestamps to mask or extract from both streams
        if speech_timestamps:
            active_16k = torch.cat([tensor_16k[ts['start']:ts['end']] for ts in speech_timestamps]).numpy()
            
            # Map timestamps to 48k stream
            active_48k_chunks = []
            for ts in speech_timestamps:
                start_48k = int(ts['start'] * (48000 / 16000))
                end_48k = int(ts['end'] * (48000 / 16000))
                active_48k_chunks.append(y_48k_norm[start_48k:end_48k])
            active_48k = np.concatenate(active_48k_chunks)
        else:
            active_16k = y_16k_norm
            active_48k = y_48k_norm
            
        return {
            "16k": active_16k,
            "48k": active_48k,
            "metadata": {
                "original_duration_sec": original_duration,
                "active_duration_sec": len(active_16k) / 16000 if len(active_16k) else 0.0,
                "speech_coverage": (len(active_16k) / 16000) / original_duration if original_duration else 0.0,
                "original_peak": original_peak,
                "original_rms": original_rms,
                "global_clipping_ratio": clipping_ratio,
                "lufs": lufs_metadata,
                "vad_segments": len(speech_timestamps) if speech_timestamps else 0
            }
        }

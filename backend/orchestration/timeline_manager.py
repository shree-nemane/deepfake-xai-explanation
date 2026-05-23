import numpy as np
import logging

logger = logging.getLogger(__name__)

# D-08: Relaxed alignment tolerance of 1.0ms for boundary verification
ALIGNMENT_TOLERANCE = 1e-3

class TimelineManager:
    """Manages audio chunks, timestamps, and temporal evidence mapping."""
    
    def __init__(self, sample_rate, window_duration=2.0, overlap=0.5):
        self.sample_rate = sample_rate
        self.window_duration = window_duration
        self.overlap = overlap
        self.window_samples = int(window_duration * sample_rate)
        self.step_samples = int(self.window_samples * (1.0 - overlap))
        
    def create_chunks(self, audio_data):
        """
        Splits audio data into chunks based on window size and overlap.
        Returns a list of dictionaries containing chunk data and metadata.
        """
        chunks = []
        total_samples = len(audio_data)
        
        for start_idx in range(0, total_samples, self.step_samples):
            end_idx = start_idx + self.window_samples
            
            # If the last chunk is too short, we can pad it or drop it. 
            # For strict forensic analysis, we drop incomplete trailing chunks.
            if end_idx > total_samples:
                break
                
            chunk_data = audio_data[start_idx:end_idx]
            start_time = start_idx / self.sample_rate
            end_time = end_idx / self.sample_rate
            
            chunks.append({
                "start_time": start_time,
                "end_time": end_time,
                "data": chunk_data
            })
            
        return chunks

    def _create_chunks_with_mask(self, audio_data, mask_data, sample_rate):
        """
        Splits audio and mask arrays into aligned chunks with padding metadata.
        Returns chunks with 'mask' and 'is_padded' fields.
        """
        window_samples = int(self.window_duration * sample_rate)
        step_samples = int(window_samples * (1.0 - self.overlap))
        total_samples = len(audio_data)
        chunks = []
        
        for start_idx in range(0, total_samples, step_samples):
            end_idx = start_idx + window_samples
            if end_idx > total_samples:
                break
            
            chunk_data = audio_data[start_idx:end_idx]
            chunk_mask = mask_data[start_idx:end_idx]
            start_time = start_idx / sample_rate
            end_time = end_idx / sample_rate
            
            chunks.append({
                "start_time": start_time,
                "end_time": end_time,
                "data": chunk_data,
                "mask": chunk_mask,
                "is_padded": bool(not chunk_mask.all())
            })
        
        return chunks

    def create_aligned_chunks(self, audio_16k, audio_48k):
        """
        Creates temporally aligned chunks across dual streams with masked padding.
        Implements D-06 (masked padding), D-07 (index-crash prevention), D-08 (alignment verification).
        
        Args:
            audio_16k: numpy array of 16kHz audio samples
            audio_48k: numpy array of 48kHz audio samples
            
        Returns:
            tuple: (chunks_16k, chunks_48k) — aligned chunk lists with mask and is_padded fields
            
        Raises:
            ValueError: If chunk temporal boundaries are misaligned beyond ALIGNMENT_TOLERANCE
        """
        sr_16k = 16000
        sr_48k = 48000
        
        duration_16k = len(audio_16k) / sr_16k
        duration_48k = len(audio_48k) / sr_48k
        
        # D-06: Timestamp-preserving masked padding
        if abs(duration_16k - duration_48k) > ALIGNMENT_TOLERANCE:
            target_duration = max(duration_16k, duration_48k)
            target_16k_len = int(target_duration * sr_16k)
            target_48k_len = int(target_duration * sr_48k)
            
            mask_16k = np.ones(target_16k_len, dtype=bool)
            mask_48k = np.ones(target_48k_len, dtype=bool)
            
            if len(audio_16k) < target_16k_len:
                logger.info(
                    f"Padding 16kHz stream: {len(audio_16k)} → {target_16k_len} samples "
                    f"({duration_16k:.6f}s → {target_duration:.6f}s)"
                )
                mask_16k[len(audio_16k):] = False
                audio_16k = np.pad(audio_16k, (0, target_16k_len - len(audio_16k)))
            
            if len(audio_48k) < target_48k_len:
                logger.info(
                    f"Padding 48kHz stream: {len(audio_48k)} → {target_48k_len} samples "
                    f"({duration_48k:.6f}s → {target_duration:.6f}s)"
                )
                mask_48k[len(audio_48k):] = False
                audio_48k = np.pad(audio_48k, (0, target_48k_len - len(audio_48k)))
        else:
            mask_16k = np.ones(len(audio_16k), dtype=bool)
            mask_48k = np.ones(len(audio_48k), dtype=bool)
        
        # Create chunks with masks for each stream
        chunks_16k = self._create_chunks_with_mask(audio_16k, mask_16k, sr_16k)
        chunks_48k = self._create_chunks_with_mask(audio_48k, mask_48k, sr_48k)
        
        # D-07: Index-crash prevention — truncate to shorter chunk list
        min_chunks = min(len(chunks_16k), len(chunks_48k))
        if len(chunks_16k) != len(chunks_48k):
            logger.warning(
                f"Chunk count mismatch: 16k={len(chunks_16k)}, 48k={len(chunks_48k)}. "
                f"Truncating to {min_chunks} chunks."
            )
        chunks_16k = chunks_16k[:min_chunks]
        chunks_48k = chunks_48k[:min_chunks]
        
        # D-08: Alignment verification within tolerance
        for i in range(min_chunks):
            start_diff = abs(chunks_16k[i]["start_time"] - chunks_48k[i]["start_time"])
            end_diff = abs(chunks_16k[i]["end_time"] - chunks_48k[i]["end_time"])
            
            if start_diff > ALIGNMENT_TOLERANCE:
                raise ValueError(
                    f"Temporal alignment failure at chunk {i}: "
                    f"16k start={chunks_16k[i]['start_time']:.6f}, "
                    f"48k start={chunks_48k[i]['start_time']:.6f}, "
                    f"tolerance={ALIGNMENT_TOLERANCE}"
                )
            if end_diff > ALIGNMENT_TOLERANCE:
                raise ValueError(
                    f"Temporal alignment failure at chunk {i}: "
                    f"16k end={chunks_16k[i]['end_time']:.6f}, "
                    f"48k end={chunks_48k[i]['end_time']:.6f}, "
                    f"tolerance={ALIGNMENT_TOLERANCE}"
                )
        
        return chunks_16k, chunks_48k

    def map_evidence_to_timeline(self, agent_results):
        """
        Consolidates temporal evidence from multiple chunks.
        """
        # Logic to map evidence to global timeline
        timeline_events = []
        # TODO: Implement timeline aggregation logic
        return timeline_events

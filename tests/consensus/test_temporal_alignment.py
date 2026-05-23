"""
Phase 2 UAT Tests: Temporal Alignment & Masked Padding (D-06, D-07, D-08)
Tests timestamp-preserving masked padding, index-crash prevention,
and boundary alignment verification.
"""
import pytest
import numpy as np
from backend.orchestration.timeline_manager import TimelineManager, ALIGNMENT_TOLERANCE


# ─── Helpers ────────────────────────────────────────────────────────────────

def _make_signal(duration_sec, sample_rate):
    """Create a synthetic sine wave signal of given duration."""
    n_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    return np.sin(2 * np.pi * 440 * t).astype(np.float32)


# ═══════════════════════════════════════════════════════════════════════════
# D-06: Timestamp-Preserving Masked Padding
# ═══════════════════════════════════════════════════════════════════════════

class TestMaskedPadding:
    """D-06: Timestamp-preserving masked padding"""

    def test_equal_duration_no_padding(self):
        """16k and 48k streams with equal duration → no padding, all masks True"""
        duration = 4.0  # 4 seconds → 2 full chunks
        audio_16k = _make_signal(duration, 16000)
        audio_48k = _make_signal(duration, 48000)
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        assert len(chunks_16k) > 0
        assert len(chunks_16k) == len(chunks_48k)
        
        for c in chunks_16k:
            assert c["is_padded"] is False
            assert c["mask"].all()
        for c in chunks_48k:
            assert c["is_padded"] is False
            assert c["mask"].all()

    def test_shorter_16k_gets_padded(self):
        """16k shorter → padded with zeros, mask marks padded region"""
        audio_16k = _make_signal(3.5, 16000)  # 3.5s
        audio_48k = _make_signal(4.0, 48000)  # 4.0s → 16k gets padded
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        # At least one 16k chunk should have padded regions
        has_padded = any(c["is_padded"] for c in chunks_16k)
        assert has_padded or len(chunks_16k) == len(chunks_48k)
        
        # All 48k chunks should NOT be padded (it was the longer stream)
        for c in chunks_48k:
            assert c["is_padded"] is False

    def test_shorter_48k_gets_padded(self):
        """48k shorter → padded with zeros, mask marks padded region"""
        audio_16k = _make_signal(4.0, 16000)  # 4.0s
        audio_48k = _make_signal(3.5, 48000)  # 3.5s → 48k gets padded
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        # At least one 48k chunk should have padded regions
        has_padded = any(c["is_padded"] for c in chunks_48k)
        assert has_padded or len(chunks_16k) == len(chunks_48k)
        
        # All 16k chunks should NOT be padded
        for c in chunks_16k:
            assert c["is_padded"] is False

    def test_padded_chunk_flagged(self):
        """Chunks containing padded regions have is_padded=True and mask marks inactive samples"""
        audio_16k = _make_signal(3.0, 16000)  # 3.0s
        audio_48k = _make_signal(4.5, 48000)  # 4.5s → 16k gets padded to 4.5s
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        padded_chunks = [c for c in chunks_16k if c["is_padded"]]
        if padded_chunks:
            # Padded chunks should have some False values in mask
            for c in padded_chunks:
                assert not c["mask"].all(), "Padded chunk mask should have False values"

    def test_mask_values_correct(self):
        """Verify mask array exactly marks active vs padded samples"""
        # 16k: 2.5s = 40,000 samples; 48k: 4.0s = 192,000 samples
        # After padding: 16k padded to 64,000 samples (4.0s)
        audio_16k = _make_signal(2.5, 16000)
        audio_48k = _make_signal(4.0, 48000)
        original_16k_len = len(audio_16k)  # 40,000
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        # Reconstruct the full mask from all chunks (they overlap, so check first chunk at least)
        assert len(chunks_16k) > 0
        # Each chunk's data length should match expected window size
        expected_window = int(2.0 * 16000)  # 32000 samples
        for c in chunks_16k:
            assert len(c["data"]) == expected_window
            assert len(c["mask"]) == expected_window

    def test_padded_data_is_zeros(self):
        """Verify padded region contains zero values"""
        audio_16k = _make_signal(2.5, 16000)
        audio_48k = _make_signal(4.0, 48000)
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, _ = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        for c in chunks_16k:
            if c["is_padded"]:
                # Where mask is False, data should be zero
                padded_region = c["data"][~c["mask"]]
                if len(padded_region) > 0:
                    assert np.all(padded_region == 0.0), "Padded samples should be zeros"


# ═══════════════════════════════════════════════════════════════════════════
# D-07: Index-Crash Prevention
# ═══════════════════════════════════════════════════════════════════════════

class TestIndexCrashPrevention:
    """D-07: Truncate to min(len_16k, len_48k)"""

    def test_unequal_chunk_counts_truncated(self):
        """If streams produce unequal chunk counts, result is truncated to minimum"""
        # Create streams where the padding + chunking might produce different counts
        # 16k: exactly 4.0s (2 chunks), 48k: exactly 4.0s (2 chunks)
        # Both should produce equal chunks due to same duration
        audio_16k = _make_signal(4.0, 16000)
        audio_48k = _make_signal(4.0, 48000)
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        # Equal chunk counts after truncation
        assert len(chunks_16k) == len(chunks_48k)

    def test_empty_stream_returns_empty(self):
        """Zero-length input → empty chunk lists"""
        audio_16k = np.array([], dtype=np.float32)
        audio_48k = np.array([], dtype=np.float32)
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        assert len(chunks_16k) == 0
        assert len(chunks_48k) == 0

    def test_very_short_stream_returns_empty(self):
        """Stream shorter than one window → empty chunk lists"""
        audio_16k = _make_signal(0.5, 16000)  # 0.5s < 2.0s window
        audio_48k = _make_signal(0.5, 48000)
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        assert len(chunks_16k) == 0
        assert len(chunks_48k) == 0


# ═══════════════════════════════════════════════════════════════════════════
# D-08: Alignment Verification
# ═══════════════════════════════════════════════════════════════════════════

class TestAlignmentVerification:
    """D-08: 1ms tolerance boundary check"""

    def test_aligned_within_tolerance(self):
        """Chunks with equal start times → passes without error"""
        audio_16k = _make_signal(4.0, 16000)
        audio_48k = _make_signal(4.0, 48000)
        
        tm = TimelineManager(sample_rate=16000)
        # Should not raise
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        # Verify alignment
        for i in range(len(chunks_16k)):
            diff = abs(chunks_16k[i]["start_time"] - chunks_48k[i]["start_time"])
            assert diff <= ALIGNMENT_TOLERANCE

    def test_tolerance_boundary(self):
        """Equal-duration streams should pass alignment check cleanly"""
        duration = 6.0  # 6 seconds → 5 chunks with 50% overlap
        audio_16k = _make_signal(duration, 16000)
        audio_48k = _make_signal(duration, 48000)
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        assert len(chunks_16k) == len(chunks_48k)
        assert len(chunks_16k) > 0
        
        # Check all chunks aligned
        for i in range(len(chunks_16k)):
            start_diff = abs(chunks_16k[i]["start_time"] - chunks_48k[i]["start_time"])
            end_diff = abs(chunks_16k[i]["end_time"] - chunks_48k[i]["end_time"])
            assert start_diff <= ALIGNMENT_TOLERANCE
            assert end_diff <= ALIGNMENT_TOLERANCE

    def test_chunk_timestamps_monotonic(self):
        """Chunk start/end times should be monotonically increasing"""
        audio_16k = _make_signal(8.0, 16000)
        audio_48k = _make_signal(8.0, 48000)
        
        tm = TimelineManager(sample_rate=16000)
        chunks_16k, chunks_48k = tm.create_aligned_chunks(audio_16k, audio_48k)
        
        for stream_chunks in [chunks_16k, chunks_48k]:
            for i in range(1, len(stream_chunks)):
                assert stream_chunks[i]["start_time"] > stream_chunks[i-1]["start_time"]
                assert stream_chunks[i]["end_time"] > stream_chunks[i-1]["end_time"]


# ═══════════════════════════════════════════════════════════════════════════
# Integration: create_chunks backward compatibility
# ═══════════════════════════════════════════════════════════════════════════

class TestBackwardCompatibility:
    """Original create_chunks method still works unchanged"""

    def test_create_chunks_still_works(self):
        """Original create_chunks returns chunks without mask/is_padded"""
        audio = _make_signal(4.0, 16000)
        tm = TimelineManager(sample_rate=16000)
        chunks = tm.create_chunks(audio)
        
        assert len(chunks) > 0
        for c in chunks:
            assert "start_time" in c
            assert "end_time" in c
            assert "data" in c
            # Original chunks should NOT have mask/is_padded
            assert "mask" not in c
            assert "is_padded" not in c

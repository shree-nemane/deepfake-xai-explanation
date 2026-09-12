---
status: complete
date: 2026-09-12
tasks_completed: 3
---

# Quick Task Summary: Fix P0 Issues (Acoustic Confidence, Jitter Scale, Mel Preview API Schema)

**ID:** 20260912-p0-fixes  
**Date:** 2026-09-12  
**Status:** Complete

## Overview
Resolved the three P0 issues uncovered during the deep codebase review and forensic audit:
1. Normalized `AcousticAgent` confidence calibration so uncertainty does not mathematically vote for the opposing class in `ConsensusEngine`.
2. Normalized `jitter` in `acoustic_features.py` as relative percentage ($\%$) matching `REAL_SPEECH_BASELINES`, eliminating permanent false-positive anomaly spikes on clean speech.
3. Added `mel_preview_base64` and display fields to `TimelineEventSchema` and `AnalysisResponse` in `backend/api/schemas/analysis.py`, resolving dropped spectrogram previews in the frontend.
4. Updated test fixtures in `tests/conftest.py` with mock dataset audio fallbacks and created `tests/unit/test_p0_fixes.py`.

## Changes Summary

### 1. AcousticAgent Confidence Calibration
- **File:** `backend/agents/acoustic_agent.py`
- **Change:** Centered confidence at $0.50$ (decision boundary) and scaled linearly with distance from `_ANOMALY_THRESHOLD`:
  ```python
  _CONFIDENCE_SCALE = 1.0
  ...
  confidence = float(np.clip(0.50 + distance * _CONFIDENCE_SCALE, 0.50, 0.99))
  ```
- **Outcome:** Guarantees confidence $\in [0.50, 0.99]$. In `ConsensusEngine`, this prevents low-certainty agents from inverting votes.

### 2. Jitter Scale Normalization
- **File:** `backend/forensic/features/acoustic_features.py`
- **Change:** Calculated jitter as relative percentage of mean pitch across voiced frames ($f_0 > 0$):
  ```python
  mean_f0 = float(np.mean(pitch_clean))
  jitter = float((np.mean(np.abs(np.diff(pitch_clean))) / mean_f0) * 100.0) if mean_f0 > 0 else 0.0
  ```
- **Outcome:** Jitter now matches `REAL_SPEECH_BASELINES["jitter"]` ($\mu=0.5, \sigma=0.2$). Clean speech produces normal z-scores ($\approx 0.0$), eliminating false-positive anomaly classifications.

### 3. API Contract Spectrogram Previews
- **File:** `backend/api/schemas/analysis.py`
- **Change:** Added `mel_preview_base64: Optional[str] = None` and `segment_count: Optional[int] = 1` to `TimelineEventSchema`; added `timeline_raw_count`, `timeline_display_count`, and `mel_previews` to `AnalysisResponse`.
- **Outcome:** Pydantic v2 response serialization preserves base64 spectrogram image previews for all timeline chunks.

### 4. Test Suite & Verification
- **Files:** `tests/conftest.py`, `tests/unit/test_p0_fixes.py`
- **Change:**
  - Added fallback file paths in `conftest.py` targeting `mock_dataset/audio/adi.wav` and `fake1.wav`.
  - Created unit tests verifying acoustic agent confidence bounds, jitter calculation on pure tone / perturbed signals, and schema serialization.
- **Outcome:** 65 tests in `tests/consensus/`, `tests/forensic/`, `tests/xai/`, and `tests/unit/` passed with 0 failures.

## Verification
- Unit test suite: `python -m pytest tests/consensus/ tests/forensic/ tests/xai/ tests/unit/` passed 65/65 tests.

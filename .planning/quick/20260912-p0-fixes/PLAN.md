# Quick Task: Fix P0 Issues (Acoustic Confidence, Jitter Scale, Mel Preview API Schema)

**ID:** 20260912-p0-fixes  
**Created:** 2026-09-12  
**Status:** In Progress  

## Overview
Address the three critical P0 issues identified during the comprehensive codebase audit:
1. Normalize `AcousticAgent` confidence to $[0.50, 0.99]$ so uncertain decisions do not mathematically invert votes in `ConsensusEngine`.
2. Normalize `jitter` in `acoustic_features.py` as relative percentage ($\%$) to match the baseline distribution in `REAL_SPEECH_BASELINES`, preventing permanent false-positive anomaly spikes on natural speech.
3. Add `mel_preview_base64` to `TimelineEventSchema` in `schemas/analysis.py` so Pydantic does not strip spectrogram previews from `/analyze` responses.
4. Update `tests/conftest.py` mock audio fallbacks to allow tests to execute against existing wav files in `mock_dataset/audio/`.

## Tasks

### Task 1: Normalize AcousticAgent Confidence
- **Files:** `backend/agents/acoustic_agent.py`
- **Action:** Center `AcousticAgent` confidence at $0.50$ (decision boundary) and scale distance from `_ANOMALY_THRESHOLD` up to $0.99$, ensuring confidence is always $\ge 0.50$.
- **Verify:** Run acoustic agent calculation test and check confidence range is in $[0.50, 0.99]$.

### Task 2: Normalize Jitter Calculation
- **Files:** `backend/forensic/features/acoustic_features.py`
- **Action:** Calculate jitter as a percentage of mean pitch across voiced frames ($f_0 > 0$): $\frac{\text{mean}(|\Delta f_0|)}{\text{mean}(f_0)} \times 100$.
- **Verify:** Verify jitter on natural audio falls in $[0.1, 2.0]\%$, producing normal z-scores against baseline ($\mu=0.5, \sigma=0.2$).

### Task 3: Add mel_preview_base64 to TimelineEventSchema & Update Conftest
- **Files:** `backend/api/schemas/analysis.py`, `tests/conftest.py`
- **Action:**
  - Add `mel_preview_base64: Optional[str] = None` to `TimelineEventSchema`.
  - Add fallbacks in `conftest.py` for `adi.wav` / `fake1.wav` when `real.wav` / `fake.wav` are not found.
- **Verify:** Test payload serialization preserves `mel_preview_base64`.

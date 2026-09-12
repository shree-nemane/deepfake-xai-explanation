# Quick Task: Fix P1 Issues (History Risk Score, WavLM Single-Pass, VAD Timeline Integrity, Dashboard Empty State)

**ID:** 20260912-p1-fixes  
**Created:** 2026-09-12  
**Status:** In Progress  

## Overview
Address the four high-priority (P1) issues identified during the comprehensive forensic audit:
1. **Inconclusive Audit History Risk Score:** Fix `/history` endpoint in `backend/api/routes/analysis.py` to prevent assigning 100% risk to inconclusive or degraded audio.
2. **WavLM Redundant Forward Pass:** Unify embedding extraction and temporal entropy calculation in `backend/models/wavlm/wavlm_handler.py` and `backend/agents/wavlm_agent.py` to eliminate the duplicate 94M-parameter forward pass per chunk.
3. **VAD Timeline Integrity:** Update `backend/preprocessing/audio_processor.py` to preserve full continuous audio streams rather than destructively concatenating speech intervals, ensuring chunk timestamps match the original recording.
4. **Dashboard Navigation Blank State:** Update `frontend/src/App.jsx` to render an intuitive empty state when an investigator clicks "Dashboard" before running an analysis, with an action to start an investigation.

## Tasks

### Task 1: Fix /history Inconclusive Risk Score
- **Files:** `backend/api/routes/analysis.py`
- **Action:**
  - In `get_history`, explicitly check `verdict`.
  - If `fake`, use `fake_probability * 100` (or `confidence * 100`).
  - If `real`, use `(1.0 - confidence) * 100`.
  - If `inconclusive`, use `fake_probability * 100` if present, else neutral 50.0 risk score.
- **Verify:** Add unit test asserting inconclusive verdict receives 50.0 (or fake_prob) instead of 100.0.

### Task 2: Single-Pass WavLM Feature Extraction
- **Files:** `backend/models/wavlm/wavlm_handler.py`, `backend/agents/wavlm_agent.py`
- **Action:**
  - Update `WavLMHandler.extract_embeddings` to compute `temporal_entropy` from `outputs.last_hidden_state` during the single forward pass.
  - Return `(mean_embeddings, phonetic_instability, temporal_entropy)` when requested (`return_entropy=True` or default).
  - Update `WavLMAgent.analyze_chunk` to receive `temporal_entropy` from `extract_embeddings` without running a second forward pass.
- **Verify:** Run WavLM agent chunk analysis and verify `temporal_entropy` matches expected variance, with only 1 model invocation.

### Task 3: Preserve Continuous Audio Timeline in AudioProcessor
- **Files:** `backend/preprocessing/audio_processor.py`
- **Action:**
  - Instead of concatenating `voiced_chunks` and destroying silence gaps, preserve `y_16k_norm` and `y_48k_norm` as the continuous audio streams.
  - Store speech intervals in `metadata["speech_timestamps"]` and maintain `active_duration_sec` and `speech_coverage` metrics.
- **Verify:** Ensure `process_dual_stream` returns aligned streams matching the original audio duration, preserving real recording timestamps.

### Task 4: Empty State for Dashboard in Frontend
- **Files:** `frontend/src/App.jsx`
- **Action:**
  - When `activeTab === 'dashboard'` and `!result`, render the `.empty-state` container informing the user that no active report is loaded, with a button to switch to 'investigate'.
- **Verify:** Verify JSX syntax, proper imports from `lucide-react`, and run eslint/build check.

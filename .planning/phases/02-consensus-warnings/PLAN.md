---
phase: "02-consensus-warnings"
title: "Consensus Event Warnings & Temporal Alignment"
created: 2026-05-23
status: ready
depends_on: ["01-db-consolidation"]
requirements: ["XAI-10", "TST-04", "TST-07"]
---

# Phase 2: Consensus Event Warnings & Temporal Alignment — Execution Plan

## Objective

Implement structured contradiction reasoning heuristics and timestamp-preserving temporal alignment to detect partial deepfakes and vocal cloning. Expert disagreements trigger prioritized threat warnings that are persisted to database with full diagnostic context.

## Decisions Applied

All decisions from [02-CONTEXT.md](file:///d:/deepfake-xai-explanation/.planning/phases/02-consensus-warnings/02-CONTEXT.md) are binding: D-01 through D-09.

---

## Wave 1 — Contradiction Warning Engine

### Task 1.1: Threat Warning Heuristics in ConsensusEngine

**File:** [consensus_engine.py](file:///d:/deepfake-xai-explanation/backend/consensus/consensus_engine.py)

<read_first>
- Lines 90–250: `evaluate_chunk_consensus` — existing deep reasoning logic at lines 206–221
- Lines 222–232: Event classification enum logic
- [02-CONTEXT.md](file:///d:/deepfake-xai-explanation/.planning/phases/02-consensus-warnings/02-CONTEXT.md) D-01, D-02, D-03 for threshold values
</read_first>

**Changes:**

1. **Replace the informal `deep_reasoning` heuristic block** (lines 206–221) with a new method `_evaluate_threat_warnings(self, voting_agents, calibrated_results, agent_results)` that returns a `list[dict]` of structured threat warning objects.

2. **Each warning dict contains:**
   ```python
   {
       "threat_type": str,        # "voice_clone" | "localized_splice" | "partial_synthesis"
       "description": str,        # Full human-readable threat description (from D-01/D-02/D-03)
       "triggering_agents": dict, # {agent_name: {"verdict": ..., "confidence": ...}}
       "severity": str,           # "high" | "elevated"
   }
   ```

3. **Implement three prioritized threat rules** (evaluated in this order, with short-circuit — once D-01 or D-02 matches, D-03 does NOT fire for the same agents):

   **Rule D-01 — Voice Clone Threat:**
   ```
   IF wavlm.verdict == "fake" AND wavlm.raw_confidence >= 0.70
   AND (acoustic.verdict == "real" AND acoustic.raw_confidence >= 0.70
        OR convnext.verdict == "real" AND convnext.raw_confidence >= 0.70)
   THEN emit:
     threat_type = "voice_clone"
     description = "Voice Clone Threat: High-fidelity phonetic cloning suspected; phonetic structures exhibit synthetic entropy, but acoustic properties appear natural."
     severity = "high"
   ```

   **Rule D-02 — Localized Audio Splice Threat:**
   ```
   IF (aasist.verdict == "fake" AND aasist.raw_confidence >= 0.75
       OR convnext.verdict == "fake" AND convnext.raw_confidence >= 0.75)
   AND wavlm.verdict == "real"
   THEN emit:
     threat_type = "localized_splice"
     description = "Localized Splice Threat: Localized waveform/spectral manipulation detected. Synthetic audio inserted into a natural voice recording."
     severity = "high"
   ```

   **Rule D-03 — Partial Synthesis Threat (catch-all):**
   ```
   IF any agent.verdict == "fake" AND agent.raw_confidence >= 0.60
   AND any other_agent.verdict == "real" AND other_agent.raw_confidence >= 0.60
   AND this pair was NOT already matched by D-01 or D-02
   THEN emit:
     threat_type = "partial_synthesis"
     description = "Partial Synthesis Threat: Multi-agent consensus split. Experts disagree on localized temporal properties; inspect temporal features."
     severity = "elevated"
   ```

   > **Key:** Use `agent_results[name]["confidence"]` (raw, pre-calibration) for threshold comparisons, NOT `calibrated_results[name]["adjusted_confidence"]`. The thresholds in D-01/D-02/D-03 are specified against raw model outputs.

4. **Update the `deep_reasoning` field** in the return dict: populate it with `[w["description"] for w in warnings]` for backward compatibility.

5. **Add a new `threat_warnings` key** to the return dict containing the full structured warning list.

6. **Update event classification logic** (lines 222–232) to use `threat_warnings` instead of substring matching on `deep_reasoning`:
   ```python
   has_threat = len(threat_warnings) > 0
   has_splice = any(w["threat_type"] in ("voice_clone", "localized_splice") for w in threat_warnings)
   
   if global_reliability < 0.40:
       event_type = ConsensusEventType.RELIABILITY_WARNING
   elif verdict == "inconclusive":
       event_type = ConsensusEventType.RELIABILITY_WARNING if global_reliability < 0.60 else ConsensusEventType.CONTRADICTION
   else:
       if convergence_strength > 0.66 and not has_threat:
           event_type = ConsensusEventType.AGREEMENT
       elif has_splice:
           event_type = ConsensusEventType.SPLICE
       elif has_threat:
           event_type = ConsensusEventType.CONTRADICTION
       else:
           event_type = ConsensusEventType.AGREEMENT if convergence_strength > 0.66 else ConsensusEventType.CONTRADICTION
   ```

<acceptance_criteria>
- `_evaluate_threat_warnings` returns correct structured warnings for D-01, D-02, D-03 scenarios
- D-01 and D-02 short-circuit to prevent D-03 duplicates
- Raw (pre-calibration) confidence is used for threshold comparisons
- Event classification uses `threat_warnings` instead of string parsing
- Return dict contains both `deep_reasoning` (backward-compat strings) and `threat_warnings` (structured dicts)
- `threat_interpretation` key added to `diagnostic_metrics` JSON when warnings fire
</acceptance_criteria>

---

### Task 1.2: Persist Threat Descriptions to Database (D-04)

**File:** [analysis.py](file:///d:/deepfake-xai-explanation/backend/api/routes/analysis.py)

<read_first>
- Lines 333–358: ConsensusEvent and EventAgentDetails creation
- [02-CONTEXT.md](file:///d:/deepfake-xai-explanation/.planning/phases/02-consensus-warnings/02-CONTEXT.md) D-04, D-05
</read_first>

**Changes:**

1. **Update ConsensusEvent description** (line 336): When `threat_warnings` exist in the chunk consensus, use the **first** warning's description as the `description` column value instead of the generic `"event_type at chunk"` string:
   ```python
   threat_warnings = c.get("threat_warnings", [])
   if threat_warnings:
       description = threat_warnings[0]["description"]
   else:
       description = f"{c['event_type'].value if hasattr(c['event_type'], 'value') else c['event_type']} at chunk"
   ```

2. **Embed `threat_warnings` into the `diagnostic_metrics` JSON** so it is queryable:
   ```python
   diag = c.get("diagnostic_metrics") or {}
   if threat_warnings:
       diag["threat_interpretation"] = [
           {"type": w["threat_type"], "description": w["description"], "severity": w["severity"]}
           for w in threat_warnings
       ]
   ```

3. **Embed `threat_warnings` into the `agent_snapshot` JSON** per D-04:
   ```python
   snapshot = c.get("calibrated_details", {})
   if threat_warnings:
       snapshot["_threat_warnings"] = threat_warnings
   ```

4. **Update `frontend_timeline` list** (lines 360–369): Add `threat_warnings` to the timeline entry for the frontend:
   ```python
   frontend_timeline.append({
       ...existing keys...,
       "threat_warnings": [
           {"type": w["threat_type"], "description": w["description"], "severity": w["severity"]}
           for w in threat_warnings
       ]
   })
   ```

<acceptance_criteria>
- Threat descriptions land in both `description` column and `diagnostic_metrics` JSON
- `agent_snapshot` JSON includes `_threat_warnings` key when warnings exist
- `frontend_timeline` entries contain serialized `threat_warnings` for UI consumption
- No change when no warnings fire (backward compatible)
</acceptance_criteria>

---

## Wave 2 — Temporal Alignment & Masked Padding

### Task 2.1: Timestamp-Preserving Masked Padding in TimelineManager

**File:** [timeline_manager.py](file:///d:/deepfake-xai-explanation/backend/orchestration/timeline_manager.py)

<read_first>
- Lines 1–49: Complete file
- [02-CONTEXT.md](file:///d:/deepfake-xai-explanation/.planning/phases/02-consensus-warnings/02-CONTEXT.md) D-06, D-07, D-08
</read_first>

**Changes:**

1. **Add a new method `create_aligned_chunks`** that accepts both 16k and 48k arrays and returns a tuple `(chunks_16k, chunks_48k)`:

   ```python
   def create_aligned_chunks(self, audio_16k, audio_48k):
       """
       Creates temporally aligned chunks across dual streams with masked padding.
       Implements D-06 (masked padding), D-07 (index-crash prevention), D-08 (alignment verification).
       """
   ```

2. **D-06 — Masked Padding:** If `len(audio_16k)/16000 != len(audio_48k)/48000` (beyond `ALIGNMENT_TOLERANCE = 1e-3`), zero-pad the shorter stream to match the longer stream's duration. Attach a boolean `mask` array to each chunk indicating which samples are active (`True`) vs padded (`False`).

   ```python
   duration_16k = len(audio_16k) / 16000.0
   duration_48k = len(audio_48k) / 48000.0
   
   if abs(duration_16k - duration_48k) > ALIGNMENT_TOLERANCE:
       target_duration = max(duration_16k, duration_48k)
       target_16k_len = int(target_duration * 16000)
       target_48k_len = int(target_duration * 48000)
       
       mask_16k = np.ones(target_16k_len, dtype=bool)
       mask_48k = np.ones(target_48k_len, dtype=bool)
       
       if len(audio_16k) < target_16k_len:
           mask_16k[len(audio_16k):] = False
           audio_16k = np.pad(audio_16k, (0, target_16k_len - len(audio_16k)))
       if len(audio_48k) < target_48k_len:
           mask_48k[len(audio_48k):] = False
           audio_48k = np.pad(audio_48k, (0, target_48k_len - len(audio_48k)))
   else:
       mask_16k = np.ones(len(audio_16k), dtype=bool)
       mask_48k = np.ones(len(audio_48k), dtype=bool)
   ```

3. **Create chunks independently** using `self.create_chunks()` for each stream, but with an added `mask` slice per chunk:
   ```python
   chunk = {
       "start_time": start_time,
       "end_time": end_time,
       "data": chunk_data,
       "mask": mask_slice,       # boolean array, True = active
       "is_padded": bool(not mask_slice.all())
   }
   ```

4. **D-07 — Index-Crash Prevention:** Truncate to `min(len(chunks_16k), len(chunks_48k))`.

5. **D-08 — Alignment Verification:** For each chunk pair `(i)`, verify:
   ```python
   if abs(chunks_16k[i]["start_time"] - chunks_48k[i]["start_time"]) > ALIGNMENT_TOLERANCE:
       raise ValueError(
           f"Temporal alignment failure at chunk {i}: "
           f"16k start={chunks_16k[i]['start_time']:.6f}, "
           f"48k start={chunks_48k[i]['start_time']:.6f}, "
           f"tolerance={ALIGNMENT_TOLERANCE}"
       )
   ```

6. **Add `ALIGNMENT_TOLERANCE = 1e-3` as a module-level constant.**

<acceptance_criteria>
- Shorter stream is zero-padded to match the longer stream's duration
- Each chunk has a boolean `mask` array and `is_padded` flag
- Chunk lists are truncated to `min(len_16k, len_48k)` (D-07)
- Start/end time alignment verified within 1ms tolerance (D-08)
- `ValueError` raised on misaligned boundaries
- Original `create_chunks` method remains unchanged for backward compatibility
</acceptance_criteria>

---

### Task 2.2: Integrate Aligned Chunks into ForensicOrchestrator

**File:** [forensic_orchestrator.py](file:///d:/deepfake-xai-explanation/backend/orchestration/forensic_orchestrator.py)

<read_first>
- Lines 20–108: `analyze_audio` method
- Lines 26–27: Current chunk creation
- Lines 42–44: Current chunk iteration loop
</read_first>

**Changes:**

1. **Replace the independent chunking calls** (lines 26–27) with the new aligned method:
   ```python
   # OLD:
   chunks_16k = self.timeline_manager_16k.create_chunks(audio_16k)
   chunks_48k = self.timeline_manager_48k.create_chunks(audio_48k)
   
   # NEW:
   chunks_16k, chunks_48k = self.timeline_manager_16k.create_aligned_chunks(audio_16k, audio_48k)
   ```

   > Note: Only `timeline_manager_16k` is used for `create_aligned_chunks` since the method internally creates both 16k and 48k chunk managers.

2. **Alternatively**, modify the `TimelineManager` so `create_aligned_chunks` is a standalone utility or modify the orchestrator to use a single manager. The cleanest approach: make `create_aligned_chunks` a **static method** or a method on `TimelineManager` that takes both arrays and both sample rates.

   **Recommended approach**: Add to `TimelineManager.__init__` an optional `dual_sr` parameter, or better, make `create_aligned_chunks` accept `sr_low=16000, sr_high=48000` explicitly. This avoids needing two `TimelineManager` instances.

3. **Pass `is_padded` flag** into the chunk consensus results for downstream logging:
   ```python
   chunk_consensus["is_padded"] = chunk_16k.get("is_padded", False) or chunk_48k.get("is_padded", False)
   ```

4. **Guard padded chunks**: If `chunk.get("is_padded", False)` is True, log a warning but continue processing. The mask information is available for agents that choose to use it.

<acceptance_criteria>
- Orchestrator uses `create_aligned_chunks` instead of independent chunking
- `is_padded` flag propagated through chunk consensus pipeline
- No index-out-of-bounds possible due to D-07 truncation
- Alignment errors raise descriptive `ValueError` before agent loop
</acceptance_criteria>

---

## Wave 3 — Comprehensive UAT Test Suite (D-09)

### Task 3.1: Contradiction Warning Tests

**File:** [NEW] `tests/consensus/test_contradiction.py`

<read_first>
- [test_suppression.py](file:///d:/deepfake-xai-explanation/tests/consensus/test_suppression.py) for fixture patterns
- [02-CONTEXT.md](file:///d:/deepfake-xai-explanation/.planning/phases/02-consensus-warnings/02-CONTEXT.md) D-01, D-02, D-03 for thresholds
</read_first>

**Tests to implement:**

```python
class TestVoiceCloneThreat:
    """D-01: wavlm fake ≥0.70, acoustic/convnext real ≥0.70"""
    
    def test_voice_clone_wavlm_vs_acoustic(self):
        """wavlm=fake@0.85, acoustic=real@0.80 → voice_clone warning"""
    
    def test_voice_clone_wavlm_vs_convnext(self):
        """wavlm=fake@0.75, convnext=real@0.72 → voice_clone warning"""
    
    def test_no_voice_clone_below_threshold(self):
        """wavlm=fake@0.65 (below 0.70) → no warning"""
    
    def test_no_voice_clone_when_both_fake(self):
        """wavlm=fake, acoustic=fake → no contradiction → no warning"""


class TestLocalizedSpliceThreat:
    """D-02: aasist/convnext fake ≥0.75, wavlm real"""
    
    def test_splice_aasist_fake_wavlm_real(self):
        """aasist=fake@0.80, wavlm=real@0.70 → localized_splice"""
    
    def test_splice_convnext_fake_wavlm_real(self):
        """convnext=fake@0.78, wavlm=real@0.70 → localized_splice"""
    
    def test_no_splice_below_threshold(self):
        """aasist=fake@0.70 (below 0.75) → no warning"""


class TestPartialSynthesisThreat:
    """D-03: catch-all split ≥0.60, not matched by D-01/D-02"""
    
    def test_partial_synthesis_generic_split(self):
        """acoustic=fake@0.65, convnext=real@0.70 → partial_synthesis"""
    
    def test_no_duplicate_with_d01(self):
        """wavlm=fake@0.85, acoustic=real@0.80 → voice_clone only, NOT partial_synthesis"""
    
    def test_no_warning_below_threshold(self):
        """acoustic=fake@0.55 → no warning (below 0.60)"""


class TestThreatPriority:
    """Multi-threat scenarios"""
    
    def test_d01_and_d02_can_cofire(self):
        """If conditions for both D-01 and D-02 are met, both warnings emit"""
    
    def test_event_type_classification(self):
        """Verify SPLICE event_type assigned when voice_clone or localized_splice fires"""


class TestThreatPersistence:
    """D-04: Database persistence of threat warnings"""
    
    def test_threat_in_event_description(self):
        """ConsensusEvent.description contains the threat description string"""
    
    def test_threat_in_diagnostic_metrics(self):
        """diagnostic_metrics JSON contains threat_interpretation key"""
    
    def test_threat_in_agent_snapshot(self):
        """agent_snapshot JSON contains _threat_warnings key"""
```

<acceptance_criteria>
- At least 14 test cases covering all three rules and edge cases
- Tests use in-memory SQLite for persistence assertions
- Short-circuit logic verified (D-03 doesn't duplicate D-01/D-02)
- All tests pass with `pytest tests/consensus/test_contradiction.py -v`
</acceptance_criteria>

---

### Task 3.2: Temporal Alignment Tests

**File:** [NEW] `tests/consensus/test_temporal_alignment.py`

<read_first>
- [timeline_manager.py](file:///d:/deepfake-xai-explanation/backend/orchestration/timeline_manager.py) for chunking logic
- [02-CONTEXT.md](file:///d:/deepfake-xai-explanation/.planning/phases/02-consensus-warnings/02-CONTEXT.md) D-06, D-07, D-08
</read_first>

**Tests to implement:**

```python
class TestMaskedPadding:
    """D-06: Timestamp-preserving masked padding"""
    
    def test_equal_duration_no_padding(self):
        """16k and 48k streams with equal duration → no padding, all masks True"""
    
    def test_shorter_16k_gets_padded(self):
        """16k shorter → padded with zeros, mask[original:] = False"""
    
    def test_shorter_48k_gets_padded(self):
        """48k shorter → padded with zeros, mask[original:] = False"""
    
    def test_padded_chunk_flagged(self):
        """Chunks containing padded regions have is_padded=True"""
    
    def test_mask_values_correct(self):
        """Verify mask array exactly marks active vs padded samples"""


class TestIndexCrashPrevention:
    """D-07: Truncate to min(len_16k, len_48k)"""
    
    def test_unequal_chunk_counts_truncated(self):
        """If 16k yields 5 chunks and 48k yields 4 → result is 4 pairs"""
    
    def test_empty_stream_returns_empty(self):
        """Zero-length input → empty chunk lists"""


class TestAlignmentVerification:
    """D-08: 1ms tolerance boundary check"""
    
    def test_aligned_within_tolerance(self):
        """Chunks with <1ms start-time difference → passes"""
    
    def test_misaligned_raises_valueerror(self):
        """Chunks with >1ms start-time difference → ValueError"""
    
    def test_tolerance_boundary(self):
        """Exactly 1ms difference → passes (inclusive tolerance)"""
```

<acceptance_criteria>
- At least 10 test cases covering padding, truncation, and alignment
- All tests use synthetic numpy arrays (no audio files)
- `ValueError` raised on alignment failures
- All tests pass with `pytest tests/consensus/test_temporal_alignment.py -v`
</acceptance_criteria>

---

## Verification Plan

### Automated Tests

```bash
# Run Phase 2 tests
pytest tests/consensus/test_contradiction.py tests/consensus/test_temporal_alignment.py -v

# Run full Phase 1 regression suite to verify no breakage
pytest tests/consensus/ -v

# Verify import chain
python -c "from backend.consensus.consensus_engine import ConsensusEngine; print('OK')"
python -c "from backend.orchestration.timeline_manager import TimelineManager; print('OK')"
```

### Manual Verification

1. Verify `ConsensusEngine().evaluate_chunk_consensus()` returns `threat_warnings` key in output dict
2. Verify `TimelineManager().create_aligned_chunks()` returns chunks with `mask` and `is_padded` fields
3. Verify all existing Phase 1 tests still pass (11/11)

---

## File Change Summary

| File | Action | Wave |
|------|--------|------|
| [consensus_engine.py](file:///d:/deepfake-xai-explanation/backend/consensus/consensus_engine.py) | MODIFY | 1 |
| [analysis.py](file:///d:/deepfake-xai-explanation/backend/api/routes/analysis.py) | MODIFY | 1 |
| [timeline_manager.py](file:///d:/deepfake-xai-explanation/backend/orchestration/timeline_manager.py) | MODIFY | 2 |
| [forensic_orchestrator.py](file:///d:/deepfake-xai-explanation/backend/orchestration/forensic_orchestrator.py) | MODIFY | 2 |
| [test_contradiction.py](file:///d:/deepfake-xai-explanation/tests/consensus/test_contradiction.py) | NEW | 3 |
| [test_temporal_alignment.py](file:///d:/deepfake-xai-explanation/tests/consensus/test_temporal_alignment.py) | NEW | 3 |

---

*Plan created: 2026-05-23*
*Decisions binding: D-01 through D-09 from 02-CONTEXT.md*

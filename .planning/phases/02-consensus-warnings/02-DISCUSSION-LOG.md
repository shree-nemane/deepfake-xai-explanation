# Phase 2: Consensus Event Warnings & Temporal Alignment - Discussion Log

This log documents the interactive context-gathering session for **Phase 2: Consensus Event Warnings & Temporal Alignment**, capturing the user's alignment decisions and choices.

---

## Interactive Discussion Log

### 1. Choice of Discussion Areas
- **Presented options:**
  1. **Contradiction Threat Warning Heuristics** (Align on specific agent combination rules and confidence thresholds for identifying Voice Cloning, Audio Splicing, and Partial Synthesis).
  2. **Contradiction Persistence & Threat Descriptions** (Determine where threat warning strings are stored in ConsensusEvent database records).
  3. **Temporal Alignment & Truncating Policy** (Decide whether to truncate or pad dual-streams when resampling boundaries differ).
  4. **Alignment Verification & Time Tolerance** (Set the numeric tolerance for matching chunk start/end boundaries).
- **User's selection:** **All Areas Selected / Re-evaluated**.
- **User's rationale:** Refine and optimize both the contradiction rules and the temporal resampling safeguards under high-fidelity UAT constraints.

### 2. Calibrating Thresholds for Contradiction Alerts
- **Presented options:**
  - **Option 1 (Recommended):** Approve proposed thresholds:
    - **Voice Clone Threat**: `wavlm` (phonetic) flags `"fake"` with confidence $\ge 0.70$, while `acoustic` or `convnext` reports `"real"` with confidence $\ge 0.70$.
    - **Localized Audio Splice Threat**: `aasist` or `convnext` flags `"fake"` with confidence $\ge 0.75$, while `wavlm` reports `"real"`.
    - **Partial Synthesis Threat**: Any direct expert disagreement with confidence $\ge 0.60$.
- **User's selection:** **Option 1 (Approved)**.
- **Decision:** Locked these thresholds to prevent high false-alarm rates while ensuring reliable detection of highly targeted vocal manipulation vectors.

### 3. Temporal Alignment & Discrepancies
- **Presented options:**
  - **Option A (Truncate):** Truncate both streams to the minimum duration.
  - **Option B (Zero-Padding):** Pad the shorter stream with zeros to match the longer stream.
- **User's selection:** **Timestamp-Preserving Masked Padding**.
- **Decision:** Reject pure zero-padding and truncation. Implement a **timestamp-preserving masked padding** strategy where shorter streams are padded with zeros to keep lengths equal, while generating a boolean active/inactive mask array to explicitly signal forensic agents to ignore the padded boundary, avoiding false transients.

### 4. Contradiction Persistence & Descriptions
- **Presented options:**
  - **Option A:** Store in `ConsensusEvent.description`.
  - **Option B:** Store as a key inside `ConsensusEvent.diagnostic_metrics`.
  - **Option C:** Store in both.
- **User's selection:** **Option C (Both)**.
- **Decision:** Store the exact custom threat warning in the `description` column for fast query rendering, while keeping complete modular calibrated agent details inside the JSON `diagnostic_metrics` and `agent_snapshot` columns for advanced analytics.

### 5. Verification Tolerance
- **Presented options:**
  - **Option A:** Strict `1e-4` seconds tolerance (0.1ms).
  - **Option B:** Relaxed `1e-3` seconds tolerance (1.0ms).
- **User's selection:** **Option B (Relaxed 1.0ms)**.
- **Decision:** Set tolerance to `1e-3` seconds (1.0 ms) to safely absorb minor clock/resampling float variations without throwing spurious alignment exceptions.

---

*Phase: 02-consensus-warnings*
*Discussion completed: 2026-05-23*

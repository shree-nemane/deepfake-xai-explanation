# Phase 2: Consensus Event Warnings & Temporal Alignment - Context

**Gathered:** 2026-05-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement structured contradiction reasoning and temporal alignment checks to detect partial deepfakes and vocal cloning.

</domain>

<decisions>
## Implementation Decisions

### Contradiction Warning Heuristics
- **D-01 (Voice Clone Threat)**: Trigger a phonetic cloning warning when `wavlm` (phonetic) flags `"fake"` with confidence $\ge 0.70$, while `acoustic` or `convnext` reports `"real"` with confidence $\ge 0.70$.
  - *Threat description:* `"Voice Clone Threat: High-fidelity phonetic cloning suspected; phonetic structures exhibit synthetic entropy, but acoustic properties appear natural."`
- **D-02 (Localized Audio Splice Threat)**: Trigger a snippet insertion warning when `aasist` or `convnext` flags `"fake"` with confidence $\ge 0.75$, while `wavlm` reports `"real"`.
  - *Threat description:* `"Localized Splice Threat: Localized waveform/spectral manipulation detected. Synthetic audio inserted into a natural voice recording."`
- **D-03 (Partial Synthesis Threat)**: Trigger a general multi-agent disagreement warning on any direct split decision where one expert reports `"fake"` and another reports `"real"` with confidence $\ge 0.60$ (excluding cases matched by D-01 and D-02).
  - *Threat description:* `"Partial Synthesis Threat: Multi-agent consensus split. Experts disagree on localized temporal properties; inspect temporal features."`

### Contradiction Persistence & Descriptions
- **D-04**: Store the custom `threat_warning` description in **both** the `description` column of the `ConsensusEvent` database records AND within the `diagnostic_metrics`/`agent_snapshot` JSON breakdowns to maximize query accessibility while maintaining structured details.
- **D-05**: Persist segment-level agent details and suppression factors to `EventAgentDetails` child rows on database transaction commits.

### Dual-Stream Temporal Alignment & Padding Policy
- **D-06 (Masked Padding Policy)**: If duration discrepancies exist between the resampled 16 kHz and 48 kHz streams due to resampling boundaries, implement a **timestamp-preserving masked padding** policy. Pad the shorter stream with zeros to ensure equal length, but maintain an active/inactive mask array so that padded regions are explicitly flagged and ignored by forensic agents, preventing false-positive edge transients.
- **D-07 (Index-Crash Prevention)**: Enforce strict boundary matching in the loop by truncating the chunk processing list to `min(len_16k, len_48k)` to completely prevent index out-of-bounds errors.
- **D-08 (Alignment Verification)**: Verify that the start and end times of each 16k and 48k chunk correspond within a relaxed tolerance threshold of `1e-3` seconds (1.0 ms) to allow for clock variations, raising a descriptive `ValueError` on mismatch.

### Testing Integration
- **D-09**: Add comprehensive unit and integration UAT tests under `tests/consensus/test_contradiction.py` to verify contradiction rule mappings, event persistence, temporal alignment, and timestamp-preserving masked padding.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications
- [PROJECT.md](file:///.planning/PROJECT.md) — Baseline architecture constraints.
- [REQUIREMENTS.md](file:///.planning/REQUIREMENTS.md) — Target requirements (XAI-10, TST-04, TST-07).
- [ROADMAP.md](file:///.planning/ROADMAP.md) — Phase 2 UAT criteria.

### Database Architectures
- [database.py](file:///backend/persistence/database.py) — SQLAlchemy tables for ConsensusEvent and EventAgentDetails.

### Core Processing & Arbitration
- [timeline_manager.py](file:///backend/orchestration/timeline_manager.py) — Audio chunking and time bounds indexing.
- [forensic_orchestrator.py](file:///backend/orchestration/forensic_orchestrator.py) — Temporal chunk loop and DB transaction committing.
- [consensus_engine.py](file:///backend/consensus/consensus_engine.py) — Temporal consensus evaluation and event classification.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ConsensusEngine.evaluate_chunk_consensus` already calculates `calibrated_details` and basic event classifications, serving as the perfect locus for our detailed threat warning heuristics.
- `AudioProcessor.process_dual_stream` already handles dual-stream downsampling, LUFS normalization, and Silero VAD mapping.

### Established Patterns
- Programmatic database assertions in `tests/consensus/test_suppression.py` serve as a guide for checking SQL foreign key cascades and event mappings.
- Custom Pytest mock data fixtures (`real_audio_data`, `fake_audio_data`) can be reused in the new UAT tests.

</code_context>

<deferred>
## Deferred Ideas

- **Neural AASIST Model Upgrade** — Deferred to Phase 6 / Milestone v2.
- **Level 2 Perturbation Simulation** — Deferred to Phase 6 / Milestone v2.

</deferred>

---

*Phase: 02-consensus-warnings*
*Context gathered: 2026-05-23*

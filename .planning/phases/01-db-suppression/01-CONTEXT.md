# Phase 1: DB Consolidation, Directory Restructuring & Suppression Engine - Context

**Gathered:** 2026-05-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish a clean, unified multi-agent architecture by purging legacy databases and implementing dynamic multi-level reliability suppression.

</domain>

<decisions>
## Implementation Decisions

### Dynamic Suppression Integration
- **D-01:** Integrate dynamic suppression into the consensus formula directly by multiplying each agent's effective weight by the reliability suppression factor before voting: $W_{i,\text{eff}} = W_i \times \text{SuppressionFactor}$.
- **D-02:** Use a continuous linear sigmoid function to map the Reliability Agent's score smoothly to the suppression weights, avoiding step jumps.
- **D-03:** Perform dynamic reliability calibration chunk-by-chunk on a segment level using the chunk reliability score.
- **D-04:** Implement a hybrid fail-closed strategy when Reliability Score $< 0.20$: skip heavy neural agents (ConvNext, WavLM) but run lightweight deterministic diagnostics (AASIST, Acoustic, Reliability), record a `QualityFailure` `ConsensusEvent` in the database, and return a safe inconclusive global verdict with 0.0 confidence.

### Database Migration & Purge
- **D-05:** Perform a complete purge of legacy database systems. Delete the legacy database file `forensic_reports_legacy.db` from the root, completely delete the legacy code folder `backend/database_legacy/`, and remove any associated import references in active code.

### Database Schema Expansion
- **D-06:** Store SHAP attribution arrays and Counterfactual sensitivity metrics as native JSON columns in SQLite using the SQLAlchemy `JSON` column type.
- **D-07:** Persist structured explanation narrative reports inside a dedicated `narrative_reports` table linked via one-to-one relationship with `reports`.
- **D-08:** Persist segment-level agent contradictions in a hybrid schema: a parent `ConsensusEvent` table, a child `EventAgentDetails` table, and a fast-rendering JSON snapshot cache column inside `ConsensusEvent` for UI binding.

### Testing Reorganization
- **D-09:** Restructure the test directory tree to establish segregated folders: `tests/unit/`, `tests/integration/`, `tests/consensus/`, `tests/xai/`, etc.
- **D-10:** Execute backend tests using the standard module invocation: `python -m pytest`.

### the agent's Discretion
- Sigmoid calibration coefficients for smooth transition mapping.
- Specific column structures and foreign keys inside the expanded database tables.
- Temporary database migration step sequences.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications
- [PROJECT.md](file:///d:/deepfake-xai-explanation/.planning/PROJECT.md) — Platform vision, baseline requirements, and active scope limits.
- [REQUIREMENTS.md](file:///d:/deepfake-xai-explanation/.planning/REQUIREMENTS.md) — Target requirements (DB-02, DB-03, SUP-02, TST-02, TST-03).
- [ROADMAP.md](file:///d:/deepfake-xai-explanation/.planning/ROADMAP.md) — Success UAT criteria for Phase 1.

### Database Architectures
- [database.py](file:///d:/deepfake-xai-explanation/backend/persistence/database.py) — Target SQLAlchemy models to expand.

### Consensus & Calibration Math
- [consensus_engine.py](file:///d:/deepfake-xai-explanation/backend/consensus/consensus_engine.py) — Logic core for dynamic suppression weight dampening.
- [calibration_engine.py](file:///d:/deepfake-xai-explanation/backend/consensus/calibration_engine.py) — Calibration adjustments mapping reliability to suppression factor.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ReliabilityAgent` inside `backend/agents/reliability_agent.py` already computes SNR, clipping, and spectral flatness metrics.
- `ConsensusEngine` inside `backend/consensus/consensus_engine.py` is initialized inside routes and orchestrators, making it the perfect locus for integrating dynamic weight dampening.

### Established Patterns
- Absolute backend imports: all scripts must import modules using package roots, e.g., `from backend.persistence.database import init_db`.
- Fail-Closed design: consensus voting defaults to Safe inconclusive states when no agents are registered or when split tie votes occur.

### Integration Points
- `backend/persistence/database.py` connects directly to `backend/api/routes/analysis.py` for database persistence hooks.
- `backend/orchestration/forensic_orchestrator.py` orchestrates segment loop chunks and runs the consensus engine.

</code_context>

<deferred>
## Deferred Ideas

- **LLM Narrative Rewriter** — Deferred to Phase 6 / Milestone v2.
- **Counterfactual Level 2 Perturbation Simulation** — Deferred to Phase 6 / Milestone v2.
- **Neural AASIST Upgrade** — Deferred to Phase 6 / Milestone v2.

</deferred>

---

*Phase: 01-db-suppression*
*Context gathered: 2026-05-23*

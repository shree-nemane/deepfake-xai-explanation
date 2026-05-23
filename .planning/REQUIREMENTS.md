# Requirements: Consensus-Based Explainable Forensic Audio Intelligence Platform

**Defined:** 2026-05-23
**Core Value:** Move beyond opaque, black-box deepfake classifiers by delivering transparent, multi-agent temporal consensus reasoning, mathematically exact SHAP attributions, and bulletproof forensic narratives.

## v1 Requirements

### Database & Model Clean-up

- [x] **DB-02**: Fully deprecate all legacy database schemas, connections, and files under `backend/database_legacy/` and remove associated legacy services.
- [x] **DB-03**: Expand current SQLAlchemy tables to persist SHAP attribution arrays, Level 1 analytical sensitivity gradients, and structured deterministic explanation narrative strings.

### Dynamic Calibration & Suppression

- [x] **SUP-02**: Implement a multi-level dynamic reliability suppression policy that dampens agent confidence weights based on the composite Reliability Score:
  - `Reliability > 0.80`: Full contribution (1.0 scale)
  - `0.60 - 0.80`: Mild confidence damping
  - `0.40 - 0.60`: Moderate uncertainty increase
  - `0.20 - 0.40`: Heavy confidence reduction
  - `< 0.20`: Fail-closed execution (mutes agents, outputs safe `inconclusive` global verdict)

### Shapley Coalition & Analytical Counterfactuals

- [x] **XAI-06**: Compute exact, deterministic Shapley values over calibrated expert support vectors across all $2^4 = 16$ possible agent coalitions per segment chunk.
- [x] **XAI-07**: Build Level 1 Analytical Sensitivity engine to compute consensus-to-expert mathematical derivatives, estimating local verdict sensitivity.
- [ ] **XAI-08**: Model and generate a 6-layer directed Evidence Graph mapping: Audio Input (L1) -> Preprocessing/Reliability (L2) -> Forensic Agents (L3) -> Consensus Arbitration (L4) -> XAI Artifacts (L5) -> Verdict & Narrative (L6).
- [x] **XAI-09**: Implement Layer 1 Deterministic Narrative Engine to generate structured evidence findings, anomaly metrics, and timeline ranges.
- [x] **XAI-10**: Map expert segment contradictions to explicit threat warnings (e.g. voice cloning, localized splices) treated as valuable forensic indicators.

### Front-End Dashboard Upgrade

- [ ] **UI-02**: Implement an expandable **Explainability Drawer** on the React Dashboard showing SHAP contribution bar charts, Counterfactual sensitivity sliders, and the interactive Plotly Evidence Graph.
- [ ] **UI-03**: Build a **Detailed Forensic Explanation Tab** to render human-readable structured narratives, active contradiction alerts, and detailed evidence grids.
- [ ] **UI-04**: Build a real-time **Multi-Stage Progress Indicator** on the uploader card displaying active pipeline stages.

### Multi-Tiered Testing Harness

- [x] **TST-02**: Restructure tests directory folder trees to segregate `unit/`, `integration/`, `consensus/`, `xai/`, `performance/`, `benchmark/`, and `datasets/`.
- [x] **TST-03**: Develop comprehensive Pytest cases validating Suppression Engine damping behaviors.
- [x] **TST-04**: Develop comprehensive Pytest cases asserting ConsensusEvent contradiction logic and warning thresholds.
- [x] **TST-05**: Develop comprehensive Pytest cases verifying exact Shapley mathematical values.
- [x] **TST-06**: Develop comprehensive Pytest cases verifying Counterfactual analytical sensitivity gradients.
- [x] **TST-07**: Develop robust integration tests verifying temporal segment alignment across resampled streams.

---

## v2 Requirements

### Neural AASIST Upgrade
- **AGT-06**: Transition AASIST agent from deterministic signal heuristics to a full neural network model running in the `ModelHub` cache.

### Counterfactual Level 2 Simulation
- **XAI-11**: Implement Level 2 Perturbation-Based Simulator that dynamically alters agent confidence scores in small increments to find the exact verdict transition boundaries.

### LLM Narrative Rewriter
- **XAI-12**: Integrate a local lightweight language model (restricted from inventing evidence) to rewrite structured evidence reports into highly fluent, human-friendly forensic paragraphs.

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| **Production RDBMS/S3 Deployments** | Local SQLite and directory uploads are sufficient for this investigator research tool. |
| **Multithreaded Agent Execution** | Orchestrator runs sequentially until model thread safety is verified. |
| **Real-time Streaming Capture** | Out of scope; platform works on uploaded static audio files. |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DB-02 | Phase 1 | Complete |
| DB-03 | Phase 1 | Complete |
| SUP-02 | Phase 1 | Complete |
| XAI-06 | Phase 3 | Complete |
| XAI-07 | Phase 3 | Complete |
| XAI-08 | Phase 4 | Pending |
| XAI-09 | Phase 3 | Complete |
| XAI-10 | Phase 2 | Complete |
| UI-02 | Phase 5 | Pending |
| UI-03 | Phase 5 | Pending |
| UI-04 | Phase 4 | Pending |
| TST-02 | Phase 1 | Complete |
| TST-03 | Phase 1 | Complete |
| TST-04 | Phase 2 | Complete |
| TST-05 | Phase 3 | Complete |
| TST-06 | Phase 3 | Complete |
| TST-07 | Phase 2 | Complete |

**Coverage:**
- v1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-23*
*Last updated: 2026-05-23 after Phase 3 execution*

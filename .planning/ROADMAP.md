# Project Roadmap: Consensus-Based Explainable Forensic Audio Intelligence Platform

## Proposed Phases

### Phase 1: DB Consolidation, Directory Restructuring & Suppression Engine
**Goal:** Establish a clean, unified multi-agent architecture by purging legacy databases and implementing dynamic multi-level reliability suppression.
**Mode:** mvp
**Success Criteria:**
1. No references to `database_legacy` or `forensic_reports_legacy.db` exist in active code.
2. SQLite schema extended to support rich XAI, Counterfactual, and structured Narrative fields in `forensic_intelligence.db`.
3. The directory tree restructured into clean folders under `tests/unit/`, `tests/integration/`, `tests/consensus/`, etc.
4. suppression engine dampens confidence scales under five distinct quality tiers and fail-closed mutes agents if Reliability Score `< 0.20`.
5. Pytest suite tests and confirms 100% correct dynamic suppression behaviors.

### Phase 2: Consensus Event Warnings & Temporal Alignment
**Goal:** Implement structured contradiction reasoning and temporal alignment checks to detect partial deepfakes and vocal cloning.
**Mode:** mvp
**Success Criteria:**
1. Split votes between expert agents successfully trigger active contradiction warnings.
2. Contradiction events are stored as `ConsensusEvent` rows in the database containing exact times, expert scores, and threat interpretations.
3. Temporal segment boundaries are correctly aligned across 16 kHz and 48 kHz resampled streams.
4. Pytest suite includes comprehensive integration assertions verifying contradiction logic and segment robustness.

### Phase 3: Exact Shapley Coalition & Analytical Counterfactuals
**Goal:** Implement exact, deterministic SHAP attributions and analytical consensus sensitivity estimates.
**Mode:** mvp
**Success Criteria:**
1. System calculates exact Shapley values ($2^4 = 16$ evaluations per segment chunk) on calibrated expert support vectors with zero Monte Carlo variance.
2. Level 1 Analytical Sensitivity engine calculates local derivatives for consensus-to-expert weights to identify verdict shift sensitivities.
3. Layer 1 Deterministic Narrative Engine successfully generates structured text summaries (Findings, Evidence, Reliability, Confidence).
4. Pytest suite tests and confirms exact mathematical correctness of Shapley values and analytical counterfactual estimates.
**Plans:**
- [x] 03-PLAN: Exact Shapley Coalition & Analytical Counterfactuals
  - Wave 1: Pure Explainability Engines (exact SHAP, analytical counterfactuals)
  - Wave 2: Deterministic Narrative and API Integration
  - Wave 3: Verification Harness
**Status:** Completed 2026-05-23

### Phase 4: Preprocessing & Multi-Stage Real-Time Feedback UI
**Goal:** Build the directed Evidence Graph data structure and update the frontend uploader with live multi-stage feedback.
**Mode:** mvp
**Success Criteria:**
1. Backend compiles a 6-layer directed Evidence Graph representation for each run.
2. React uploader displays real-time multi-stage progress indicators (`Normalizing...`, `Segmenting...`, `Running Agent Panel...`, etc.) on the dashboard card.
3. High-fidelity progress updates synchronize cleanly with backend pre-processing states.
**Plans:**
- [x] 04-01: Evidence Graph and Real-Time Progress
  - Wave 1: Backend graph generation, progress endpoints, uploader progress UI, and verification
**Status:** Completed 2026-05-24

### Phase 5: Explanations Console, SHAP & Plotly Graph Drawer
**Goal:** Build the expandable Explainability Drawer and Detailed Forensic Explanation Tab on the React dashboard.
**Mode:** mvp
**Success Criteria:**
1. React UI features a slide-out Explainability Drawer housing SHAP Recharts bar charts, Counterfactual sliders, and the interactive Plotly Evidence Graph.
2. React UI includes a Detailed Forensic Explanation Tab presenting structured narratives, z-score tables, and dynamic active contradiction warnings.
3. End-to-end validation (upload -> progress feedback -> multi-agent run -> dynamic suppression -> consensus persistence -> detailed UI explanation drawer/tabs).
**Plans:**
- [x] 05-01: Explainability Drawer with SHAP, Sensitivity, and Plotly Graph
  - Wave 1: Drawer shell, SHAP Recharts panel, Level 1 sensitivity controls, Plotly graph, dashboard wiring
- [x] 05-02: Detailed Forensic Explanation Tab
  - Wave 2 *(blocked on Wave 1 completion)*: Dashboard tabs, narrative sections, threat alerts, evidence tables
**Status:** Completed 2026-05-24

---

## Mapped Requirements

- **Phase 1**: `DB-02`, `DB-03`, `SUP-02`, `TST-02`, `TST-03`
- **Phase 2**: `XAI-10`, `TST-04`, `TST-07`
- **Phase 3**: `XAI-06`, `XAI-07`, `XAI-09`, `TST-05`, `TST-06`
- **Phase 4**: `XAI-08`, `UI-04`
- **Phase 5**: `UI-02`, `UI-03`

*Requirements Coverage: 17/17 (100% mapped) ✓*
*Last updated: 2026-05-24 after Phase 4 execution*

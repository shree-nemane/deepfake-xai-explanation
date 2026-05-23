# Consensus-Based Explainable Forensic Audio Intelligence Platform

## What This Is

An investigator-grade digital forensics platform designed to authenticate audio recordings, detect synthetic voice clones (deepfakes), and provide transparent, evidence-based explanations using Explainable AI (XAI) techniques. The system coordinates a panel of independent, specialized forensic agents that reason over overlapping temporal chunks, calibrating their verdicts dynamically based on recording quality and generating structural proof for human review.

## Core Value

Move beyond opaque, black-box deepfake classifiers by delivering transparent, multi-agent temporal consensus reasoning, mathematically exact SHAP attributions, and bulletproof forensic narratives.

## Requirements

### Validated

*The following capabilities exist in the codebase and have been verified through testing:*
- ✓ **PRE-01**: Dual-stream preprocessing loading audio at 48 kHz, validating format/codec constraints, performing EBU R128 LUFS loudness normalization (target -23.0), and applying neural Silero VAD to isolate active speech. — *Phase 0*
- ✓ **PRE-02**: Aligned resampling generating a 16 kHz semantic stream (for neural agents) and a 48 kHz acoustic stream (for high-fidelity agents). — *Phase 0*
- ✓ **SEG-01**: Overlapping segment timeline chunking splitting active speech streams into 2.0-second chunk windows with a 50% temporal overlap (1.0s hop). — *Phase 0*
- ✓ **AGT-01**: Base Agent class abstraction and global mutable `agent_registry` managing autonomous expert plugin lifecycles. — *Phase 0*
- ✓ **AGT-02**: Neural ConvNext Agent translating 48 kHz chunks into Mel-spectrogram tensors and running inference to output spectral artifact risk scores. — *Phase 0*
- ✓ **AGT-03**: Neural WavLM Agent extracting deep speech embeddings and computing temporal entropy to score phonetic speech instability. — *Phase 0*
- ✓ **AGT-04**: Acoustic Agent extracting biological plausibility metrics (ZCR, MFCCs, pitch, jitter, shimmer) and scoring their deviation via z-score anomaly detection. — *Phase 0*
- ✓ **AGT-05**: Reliability Agent calculating real-signal quality indicators (SNR via HPSS, clipping ratios, RMS energy, spectral flatness) to score recording trustworthiness. — *Phase 0*
- ✓ **CON-01**: Consensus Engine calibrating agent confidence scores, computing weighted probability support values, and executing agreement/contradiction arbitrations. — *Phase 0*
- ✓ **DB-01**: Persistent relational database schema in SQLAlchemy mapping sessions to Report, AgentOutput, EvidenceSegment, ConsensusEvent, and XAIArtifact rows. — *Phase 0*
- ✓ **UI-01**: React uploader dashboard rendering real-time analysis charts, consensus panels, reliability trends, and temporal spectrogram heatmaps. — *Phase 0*
- ✓ **TST-01**: Automated Pytest harness exercising orchestrator pipelines and agent robustness on committed mock audio fixtures. — *Phase 0*

### Active

*The following active requirements define the scope of the current upgrade milestone (v1 Release):*

**Database & Model Consolidation:**
- [ ] **DB-02**: Fully deprecate the legacy database files and remove legacy models/session endpoints under `backend/database_legacy/` and legacy services.
- [ ] **DB-03**: Expand SQLAlchemy schemas to store rich SHAP attribution arrays, Level 1 Counterfactual analytical sensitivities, and structured template narrative strings.

**Multi-Level Dynamic Suppression:**
- [ ] **SUP-02**: Implement a multi-level dynamic reliability suppression policy based on the Reliability Score:
  - `> 0.80` -> Full contribution (no damping)
  - `0.60 - 0.80` -> Mild confidence damping
  - `0.40 - 0.60` -> Moderate uncertainty increase
  - `0.20 - 0.40` -> Heavy confidence reduction
  - `< 0.20` -> Fail-closed execution (mutes agents, outputs safe `inconclusive` global verdict)

**Shapley Coalition & Level 1 Counterfactual XAI:**
- [ ] **XAI-06**: Implement exact, deterministic Shapley value calculations over calibrated expert support vectors across all $2^4 = 16$ coalitions per chunk (WavLM, ConvNext, AASIST, Acoustic) without Monte Carlo approximations.
- [ ] **XAI-07**: Build Level 1 Analytical Sensitivity engine computing local consensus-to-expert gradients to show how sensitive the global verdict is to each agent.
- [ ] **XAI-08**: Develop a 6-layer directed Evidence Graph mapping data flow: Audio Input (L1) -> Preprocessing/Reliability (L2) -> Forensic Agents (L3) -> Consensus Arbitration (L4) -> XAI Artifacts (L5) -> Verdict & Narrative (L6).
- [ ] **XAI-09**: Implement a Layer 1 Deterministic Narrative Engine utilizing rule-driven templates to translate findings, z-score anomalies, and segment alignments into structured evidence reports.
- [ ] **XAI-10**: Elevate segment contradictions into active warnings, mapping specific expert splits (e.g. WavLM fake + Acoustic real) to descriptive threat indicators (e.g. "Voice Clone Suspected").

**Hybrid UI & Real-Time Feedback:**
- [ ] **UI-02**: Create an expandable **Explainability Drawer** on the React Dashboard housing SHAP horizontal bar charts, Counterfactual sensitivity controls, and the Plotly-based Evidence Graph.
- [ ] **UI-03**: Build a **Detailed Forensic Explanation Tab** to render human-readable narratives, contradiction warnings, and tabular evidence breakdowns.
- [ ] **UI-04**: Implement a real-time **Multi-Stage Progress Indicator** on the uploader card displaying current active steps during the analysis pipeline.

**Comprehensive Forensic Test Harness:**
- [ ] **TST-02**: Reorganize testing directory folders under `tests/unit/`, `tests/integration/`, `tests/consensus/`, `tests/xai/`, `tests/performance/`, `tests/benchmark/`, and `tests/datasets/`.
- [ ] **TST-03**: Develop dedicated unit and integration assertions verifying the Multi-Level Suppression Engine.
- [ ] **TST-04**: Develop unit tests verifying ConsensusEvent contradiction logic and warning triggers.
- [ ] **TST-05**: Develop unit tests asserting exact Shapley mathematical value correctness.
- [ ] **TST-06**: Develop unit tests validating Counterfactual analytical sensitivity estimates.
- [ ] **TST-07**: Develop robust integration assertions confirming temporal segment alignment across streams.

### Out of Scope

- **LLM Narrative Rewriter**: Local language model integration is deferred to the v2 milestone; v1 relies on the bulletproof Deterministic Template Engine.
- **Counterfactual Level 2 Simulation**: Perturbation-based simulation is deferred to v2; v1 delivers Level 1 analytical sensitivity gradients.
- **Neural AASIST Upgrade**: Transitioning the AASIST agent from its optimized deterministic signal heuristics to a full neural network is deferred to v2.
- **Production RDBMS/S3 Deployments**: SQLite files and local upload directory remain in scope for this local research platform; cloud storage is out of scope.

## Context

The system represents an upgrade of a local digital audio forensics project. The baseline has successfully laid out preprocessing and basic agent registrations, but suffers from split legacy codebases, uncalibrated confidence scales under noisy conditions, lack of deep XAI analytics (SHAP, counterfactuals), and a generic uploader interface that hides contradictions.

## Constraints

- **Execution Mode**: Forensic orchestration runs sequentially across chunks; multithreading remains constrained until model thread safety is verified.
- **Resource Constraints**: High-capacity models (WavLM, ConvNext) are lazily loaded via `ModelHub` process singletons to prevent out-of-memory errors on typical CPU environments.
- **Security Constraint**: CORS is configured to wide-open `*` for local web access but must not be committed to cloud production.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **Hybrid Agent Design** | Combine lightweight deterministic signal agents (AASIST, Acoustic, Reliability) with advanced neural agents (ConvNext, WavLM) to maintain high robustness at low resource cost. | ✓ Approved |
| **Multi-Level Suppression** | Reject binary suppression to preserve moderate signal evidence; dynamically damp agent weights along five distinct quality tiers. | ✓ Approved |
| **Exact Shapley Values** | Small coalition footprint ($N=4$, 16 states) allows exact, deterministic calculations without Monte Carlo variance. | ✓ Approved |
| **Consolidated Database** | Completely purge legacy schemas and tables to prevent future architectural drift. | ✓ Approved |
| **Hybrid UI Layout** | Deliver a clean dashboard along with an expandable explainability drawer and a detailed explanation tab for multi-tiered analysis. | ✓ Approved |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-23 after project initialization*

# Phase 1: DB Consolidation, Directory Restructuring & Suppression Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-23
**Phase:** 01-db-suppression
**Areas discussed:** Suppression policy implementation, XAI & Narrative schema expansion

---

## Suppression Policy Integration Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Dynamic Weight Damping | Scale agent weights inside consensus formulas ($W_{\text{eff}} = W \times \text{DampingFactor}$) before voting. | ✓ |
| Post-Consensus Damping | Scale standard consensus results at the end of voting. | |

**User's choice:** Dynamic Weight Damping.
**Notes:** Prevents noisy/uncalibrated agents from corrupting the voting consensus before damping weights.

---

## Dynamic Suppression Mapping Curve

| Option | Description | Selected |
|--------|-------------|----------|
| Five-Tier Multiplier Policy | Apply distinct step weights along quality thresholds (e.g. 1.0, 0.75, 0.5, 0.25, 0.0). | |
| Continuous Linear Sigmoid | Map reliability scores to a smooth continuous sigmoid mathematical curve to scale weights smoothly. | ✓ |

**User's choice:** Continuous Linear Sigmoid.
**Notes:** Smooths out confidence values on the UI and avoids jarring step transitions.

---

## Suppression Calibration Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Segment-Level Chunk Reliability | Calibrate dynamically chunk-by-chunk inside specific 2.0s windows. | ✓ |
| Global File-Level Reliability | Apply uniform suppression to all chunks based on global file average. | |

**User's choice:** Segment-Level Chunk Reliability.
**Notes:** Catches localized transient noises or anomalies (e.g. mic pops or coughs) without muting clean parts.

---

## Handling the Fail-Closed (<0.20) State

| Option | Description | Selected |
|--------|-------------|----------|
| Short-Circuit Fail-Closed | Skip all agent runs entirely to save compute and return inconclusive. | |
| Permissive Fail-Closed | Run all agents for diagnostic logging, but override combined consensus. | |
| Hybrid Fail-Closed Strategy | Skip heavy neural models (ConvNext, WavLM) but execute lightweight diagnostics (AASIST, Acoustic, Reliability), record `QualityFailure` in `ConsensusEvent`, and return inconclusive. | ✓ |

**User's choice:** Hybrid Fail-Closed Strategy.
**Notes:** Retains rich diagnostic logging and forensic traceability without wasting heavy neural inference compute.

---

## Database Migration & Purge

| Option | Description | Selected |
|--------|-------------|----------|
| Complete Purge | Delete all legacy files (`forensic_reports_legacy.db` and folder `backend/database_legacy/`) from the workspace. | ✓ |
| Deprecate but Retain | Keep legacy files in an archive folder but disable active route hooks. | |

**User's choice:** Complete Purge.
**Notes:** Eliminates technical debt completely and guarantees clean single-db schema development.

---

## XAI & Narrative Schema Expansion

| Option | Description | Selected |
|--------|-------------|----------|
| Native JSON Column | Store SHAP and Counterfactuals as dynamic JSON objects inside standard database columns. | ✓ |
| Serialized String Column | Store as text columns requiring manual serialization/deserialization. | |

**User's choice:** Native JSON Column.
**Notes:** Clean, extensible, and natively understood by Python backend and React/Vite front-end components.

---

## Persisting Structured Explanation Narrative

| Option | Description | Selected |
|--------|-------------|----------|
| Column in Report Table | Store narrative text directly in reports table. | |
| Row in XAIArtifact Table | Store narrative text in XAIArtifact table under special type. | |
| Dedicated NarrativeReport Table | Create a dedicated table to house structured template summaries with clean relations. | ✓ |

**User's choice:** Dedicated NarrativeReport Table.
**Notes:** Preserves database normalization standards and decouples high-level report lists from rich text narrative payloads.

---

## Contradiction Warning Schema Design

| Option | Description | Selected |
|--------|-------------|----------|
| Native JSON Array Column | Store list of agent dicts directly in the ConsensusEvent row. | |
| Flat Relational Table | Create an involved_agents child table with foreign keys. | |
| Hybrid Relational + JSON | Parent ConsensusEvent + child EventAgentDetails table + fast JSON snapshot cache column. | ✓ |

**User's choice:** Hybrid Relational + JSON Design.
**Notes:** Guarantees relational database querying integrity while enabling high-speed JSON rendering for React UI components.

---

## the agent's Discretion

- Sigmoid calibration coefficients for smooth transition mapping.
- Specific database column fields and relations.
- Testing directory folder naming conventions under `tests/`.

---

## Deferred Ideas

- **LLM Narrative Rewriter** — Deferred to Milestone v2.
- **Counterfactual Level 2 Perturbation Simulation** — Deferred to Milestone v2.
- **Neural AASIST Upgrade** — Deferred to Milestone v2.

---

*Phase: 01-db-suppression*
*Discussion log generated: 2026-05-23*

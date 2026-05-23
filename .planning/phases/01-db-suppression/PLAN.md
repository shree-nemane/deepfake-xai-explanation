---
phase: "01-db-suppression"
title: "DB Consolidation, Directory Restructuring & Suppression Engine"
created: 2026-05-23
status: complete
reconstructed: true
requirements: ["DB-02", "DB-03", "SUP-02", "TST-02", "TST-03"]
---

# Phase 1: DB Consolidation, Directory Restructuring & Suppression Engine — Reconstructed Plan

## Objective

Establish a clean, unified multi-agent architecture by removing active legacy database usage, expanding persistence for XAI/narrative/consensus artifacts, implementing reliability-aware suppression, and organizing tests into focused folders.

## Tasks

### Task 1.1: Legacy Database Purge

- Remove active references to `backend/database_legacy/` and `forensic_reports_legacy.db`.
- Keep the active persistence path centered on `backend/persistence/database.py` and `forensic_intelligence.db`.

### Task 1.2: Rich Persistence Schema

- Expand SQLAlchemy models for `XAIArtifact`, `NarrativeReport`, `ConsensusEvent`, `EventAgentDetails`, and `ProcessingMetadata`.
- Store SHAP values, counterfactuals, evidence graph data, narrative metadata, and event diagnostics as native JSON/text fields.

### Task 1.3: Dynamic Suppression

- Add continuous reliability suppression through `ConsensusEngine._get_sigmoid_suppression`.
- Add agent-specific suppression factors based on SNR, clipping, spectral flatness, RMS energy, and waveform quality.
- Preserve fail-closed inconclusive behavior when reliability is below `0.20`.

### Task 1.4: Test Organization and Coverage

- Organize tests under `tests/unit/`, `tests/integration/`, `tests/consensus/`, `tests/xai/`, `tests/performance/`, `tests/benchmark/`, and `tests/datasets/`.
- Add focused consensus tests for suppression math, database schema behavior, and fail-closed guards.

## Verification Plan

- `python -m pytest tests\consensus -q`
- `python -m pytest tests\integration\test_validation.py -q`
- `python -m backend.migrations.validate_schema`
- Active agent registry import check: `import backend.agents; agent_registry.get_agent_names()`

## Reconstruction Note

This plan was reconstructed after implementation from the Phase 1 context, codebase evidence, and passing verification results so GSD artifact state matches the actual project state before Phase 3 begins.

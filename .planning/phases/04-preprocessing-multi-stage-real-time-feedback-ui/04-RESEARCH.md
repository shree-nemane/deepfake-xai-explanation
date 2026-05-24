# Phase 4 Research: Evidence Graph and Real-Time Progress

**Phase:** 04-preprocessing-multi-stage-real-time-feedback-ui
**Date:** 2026-05-24
**Status:** Complete

## Research Question

What needs to be true to plan Phase 4 well: a 6-layer directed JSON Evidence Graph and real backend-driven progress updates for the existing local forensic audio analysis flow.

## Current State

- `backend/explainability/evidence_graph.py` exists but is a placeholder; `generate_evidence_graph()` returns an empty graph.
- `backend/persistence/database.py` already includes `XAIArtifact.evidence_graph`, so no schema migration should be needed for graph persistence.
- `backend/api/routes/analysis.py` already assembles preprocessing, feature analysis, diagnostics, XAI payloads, narrative payloads, and the final response in one place.
- `frontend/src/features/analysis/Uploader.jsx` currently shows a simulated `framer-motion` progress bar while the single `POST /analyze/` request runs.
- `frontend/src/components/forensic/EvidenceGraph.jsx` currently renders a simple agent vote relationship summary from `agents`, `consensus`, and `diagnostics`; it does not consume backend graph data.

## Recommended Approach

### Evidence Graph

Build a deterministic graph builder in `backend/explainability/evidence_graph.py` that returns:

- `schema_version`
- `layers`
- `nodes`
- `edges`
- `summary`

Nodes should be stable and typed:

- `audio_input`
- preprocessing/reliability nodes
- one node per forensic agent
- consensus and chunk-warning nodes
- SHAP and counterfactual nodes
- final verdict and narrative nodes

Edges should be directed and relation-typed:

- `processed_into`
- `measured_by`
- `evaluated_by`
- `calibrated_into`
- `explained_by`
- `summarized_by`
- `supports_verdict`

The graph should be built after `xai_payload` and `narrative_payload` exist so Layer 5 and Layer 6 can link to real artifacts. Persist it on the rich `XAIArtifact` row and include it in `final_response["xai"]["evidence_graph"]`.

### Progress Updates

Use a job-based analysis flow alongside the existing synchronous route:

- Keep `POST /analyze/` for backward compatibility and tests.
- Add `POST /analyze/jobs` to accept the upload, create a job ID, save the temp file, and start background analysis.
- Add `GET /analyze/jobs/{job_id}/progress` for polling fallback.
- Add `GET /analyze/jobs/{job_id}/events` as a Server-Sent Events stream for real-time stage updates.
- Add `GET /analyze/jobs/{job_id}/result` to retrieve the final `AnalysisResponse` when complete.

For this local single-user research app, an in-memory job store is acceptable. It should still include a lock, timestamps, terminal states, error capture, and cleanup of uploaded temp files.

### Frontend Integration

Update `App.jsx` and `Uploader.jsx` so analysis starts through the job endpoint and listens to backend progress:

- Start job with the selected file.
- Subscribe to SSE progress if available.
- Fall back to polling `/progress` if SSE fails.
- Render current stage label/status/percent and completed stages in the uploader card.
- Fetch `/result` on completion and route to the dashboard.

Dashboard changes should stay minimal:

- Pass `result.xai?.evidence_graph` to `EvidenceGraph`.
- Let `EvidenceGraph` render a concise graph summary from backend graph data.
- Do not build the Phase 5 drawer, Plotly graph, SHAP bar chart, or detailed explanation tab.

## Risks

| Risk | Mitigation |
|------|------------|
| Background task uses a closed request DB session | Create a fresh `SessionLocal` session inside the background job. |
| SSE stream leaks or never terminates | End stream on `complete` or `error`, include heartbeat/timeout behavior, and expose polling fallback. |
| In-memory jobs grow without bound | Record timestamps and remove terminal jobs after a small TTL or when result is fetched. |
| Graph overstates evidence | Build nodes only from existing observed response artifacts and include source payload references. |
| Frontend progress gets stuck | Treat `complete`/`error` as terminal, and fall back to polling if EventSource errors. |

## Validation Strategy

- Unit-test `EvidenceGraph` generation with synthetic preprocessing, agents, consensus, XAI, diagnostics, and narrative payloads.
- Unit-test progress job state transitions without running neural models.
- Extend schema validation so `AnalysisResponse` accepts `xai.evidence_graph` and progress-compatible payloads.
- Run:
  - `python -m pytest tests\xai tests\consensus tests\integration\test_validation.py -q`
  - `python -m backend.migrations.validate_schema`
  - `npm run build` from `frontend/`

## RESEARCH COMPLETE

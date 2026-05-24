# Phase 4: Preprocessing & Multi-Stage Real-Time Feedback UI - Context

**Gathered:** 2026-05-24
**Status:** Ready for planning
**Source:** `$gsd-progress --next` routed to `$gsd-discuss-phase 4`; user selected all Phase 4 gray areas directly.

<domain>
## Phase Boundary

Phase 4 delivers the backend evidence graph data contract and real-time analysis progress feedback needed by the existing investigation UI.

In scope:
- Generate a 6-layer directed JSON Evidence Graph for each analysis run:
  - L1 Audio Input
  - L2 Preprocessing/Reliability
  - L3 Forensic Agents
  - L4 Consensus Arbitration
  - L5 XAI Artifacts
  - L6 Verdict & Narrative
- Persist the graph in the existing `XAIArtifact.evidence_graph` JSON column and expose it in the analysis response.
- Add a backend progress endpoint or stream so the frontend can show real stage transitions during analysis.
- Replace the current simulated uploader progress animation with progress UI driven by backend stage updates.

Out of scope:
- The expandable explainability drawer remains Phase 5.
- The detailed forensic explanation tab remains Phase 5.
- New SHAP/counterfactual chart interactions remain Phase 5 unless a minimal data pass-through is needed for graph linkage.

</domain>

<decisions>
## Implementation Decisions

### Evidence Graph Data Shape
- **D-01:** Use a deterministic 6-layer directed JSON graph, not an ad hoc visual-only graph.
- **D-02:** Graph nodes must include stable IDs, layer numbers, node type, label, payload/metadata, and optional severity/status fields where the source evidence supports them.
- **D-03:** Graph edges must be directed and typed, with relations such as `processed_into`, `evaluated_by`, `calibrated_into`, `explained_by`, and `supports_verdict`.
- **D-04:** The graph must be built from observed pipeline artifacts only: preprocessing metadata, reliability evidence, agent outputs, chunk consensus details, threat warnings, SHAP values, counterfactuals, diagnostics, and narrative output.
- **D-05:** `backend/explainability/evidence_graph.py` is the natural home for the graph builder, but the existing placeholder should be replaced with a real builder instead of being treated as complete.

### Progress Transport and UI
- **D-06:** Use a backend progress endpoint or stream for real-time stage updates. Do not rely on the current fixed-duration animated progress bar as the source of truth.
- **D-07:** Planning should evaluate the simplest reliable transport for this local app, with Server-Sent Events or a pollable job/status endpoint preferred over broad WebSocket infrastructure unless the codebase strongly points otherwise.
- **D-08:** Progress stages should map to real analysis milestones: upload received, preprocessing, segmentation, agent panel, consensus, XAI/evidence graph, narrative/persistence, complete/error.
- **D-09:** The frontend uploader should render backend-reported stage label, status, percent/order, and errors. It should degrade gracefully if progress updates are unavailable.

### Phase Boundary
- **D-10:** Phase 4 stops at graph data plus progress UI.
- **D-11:** Phase 5 owns the expandable explainability drawer, SHAP bar charts, counterfactual controls, Plotly graph rendering, and detailed forensic explanation tab.
- **D-12:** Phase 4 may adapt the existing `EvidenceGraph` component only enough to consume/display the new graph data at dashboard level or to verify the graph payload. It should not build the full Phase 5 drawer experience.

### the agent's Discretion
- Exact endpoint names and transport details, as long as the frontend receives true backend stage updates.
- Exact node and edge field names, as long as the graph remains deterministic, typed, directed, and easy for Phase 5 to visualize.
- Whether progress state is kept in memory, associated with a report/job ID, or represented through a lightweight status store, provided it fits the local single-user research tool constraints.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope
- `.planning/PROJECT.md` - Current validated requirements, active scope, and Phase 4/5 boundary.
- `.planning/REQUIREMENTS.md` - Pending Phase 4 requirements: `XAI-08` and `UI-04`.
- `.planning/ROADMAP.md` - Phase 4 goal and success criteria.
- `DFXAI_project_spec.md` - Primary project source of truth for evidence graph, progress UI, and v1/v2 boundaries.
- `DFXAI_agent_prompt.md` - Supplemental execution guidance and project expectations.

### Prior Phase Context
- `.planning/phases/03-exact-shapley-coalition-analytical-counterfactuals/03-CONTEXT.md` - Phase 3 decisions that defer the evidence graph and React drawer work.
- `.planning/phases/03-exact-shapley-coalition-analytical-counterfactuals/SUMMARY.md` - Confirms exact SHAP, analytical counterfactuals, deterministic narrative, and API `xai`/`narrative` fields are available.

### Backend Integration Points
- `backend/explainability/evidence_graph.py` - Current placeholder graph builder to replace with a real 6-layer JSON builder.
- `backend/api/routes/analysis.py` - Main `POST /analyze/` route, response assembly, persistence, XAI payload creation, narrative generation, and natural progress-stage instrumentation point.
- `backend/api/schemas/analysis.py` - Response schema to extend with `evidence_graph` or graph-bearing `xai` payload fields.
- `backend/persistence/database.py` - Existing `XAIArtifact.evidence_graph` JSON column and report relationships.
- `backend/preprocessing/audio_processor.py` - Preprocessing stage source.
- `backend/orchestration/timeline_manager.py` - Segment/timeline stage source.
- `backend/orchestration/forensic_orchestrator.py` - Agent-panel orchestration and chunk result source.
- `backend/consensus/consensus_engine.py` - Consensus arbitration and calibrated details source.
- `backend/explainability/shap/shap_engine.py` - Phase 3 SHAP artifact source.
- `backend/explainability/counterfactuals/counterfactual_engine.py` - Phase 3 analytical sensitivity source.
- `backend/explainability/narrative_engine.py` - Phase 3 narrative source.

### Frontend Integration Points
- `frontend/src/App.jsx` - Owns upload request state and tab routing after analysis.
- `frontend/src/features/analysis/Uploader.jsx` - Current simulated progress UI to replace with backend-driven stage updates.
- `frontend/src/features/analysis/Dashboard.jsx` - Current dashboard composition and evidence graph placement.
- `frontend/src/components/forensic/EvidenceGraph.jsx` - Current summary-style relationship map; may be adapted minimally but full interactive graph remains Phase 5.
- `frontend/src/components/forensic/TimelinePanel.jsx` - Existing timeline display that can inform progress/graph validation.
- `frontend/src/components/forensic/FeatureAnalysisPanel.jsx` - Existing diagnostic and preprocessing display patterns.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/explainability/evidence_graph.py`: placeholder class and `generate_evidence_graph()` factory are already named for this phase.
- `XAIArtifact.evidence_graph`: database schema already has a JSON column for the graph.
- `AnalysisResponse.xai`: response schema already accepts arbitrary XAI payloads.
- `frontend/src/features/analysis/Uploader.jsx`: has upload/progress layout, error state, and `isAnalyzing` state ready to replace simulated progress.
- `frontend/src/components/forensic/EvidenceGraph.jsx`: existing dashboard component can validate/preview graph payloads before Phase 5 visualization.

### Established Patterns
- Backend response assembly is centralized in `backend/api/routes/analysis.py` with helper functions for preprocessing, diagnostics, feature analysis, and XAI payloads.
- Persistence uses native SQLAlchemy JSON fields, not stringified JSON.
- Frontend data flow currently uses Axios from `App.jsx` and passes `result` into dashboard components.
- UI styling is custom CSS utility classes plus `framer-motion` and `lucide-react`; new progress UI should stay consistent with the existing uploader card and dashboard panels.

### Integration Points
- Add graph construction after `xai_payload` and `narrative_payload` are available so L5/L6 graph nodes can link to SHAP, counterfactual, verdict, and narrative artifacts.
- Persist the graph on the rich `XAIArtifact` row and include it in `final_response`.
- Add a progress reporting mechanism around the current long-running analysis route or split analysis into job start plus status/stream endpoints if planning finds that cleaner.
- Frontend needs a job/progress subscription or polling loop that updates uploader stage state while the analysis is running.

</code_context>

<specifics>
## Specific Ideas

- The progress UI should reflect real backend stages rather than pretending analysis is progressing on a fixed timer.
- The graph should be JSON-first and visualization-ready for Phase 5, but Phase 4 should not overbuild the final interactive graph UI.
- The graph should preserve forensic auditability by linking source artifacts through directed edges instead of flattening evidence into a single summary node.

</specifics>

<deferred>
## Deferred Ideas

- Expandable Explainability Drawer with SHAP bars, counterfactual controls, and Plotly graph rendering is Phase 5.
- Detailed Forensic Explanation Tab with narrative grids and contradiction alerts is Phase 5.
- Full interactive graph layout decisions, filtering controls, and charting polish are Phase 5.

</deferred>

---

*Phase: 04-preprocessing-multi-stage-real-time-feedback-ui*
*Context gathered: 2026-05-24*

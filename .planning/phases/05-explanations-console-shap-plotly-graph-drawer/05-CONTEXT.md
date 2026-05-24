# Phase 5: Explanations Console, SHAP & Plotly Graph Drawer - Context

**Gathered:** 2026-05-24
**Status:** Ready for planning
**Source:** Resume-work continuation; Phase 4 complete; prior session deferred Phase 5 UI specifics as already clear from project docs.

<domain>
## Phase Boundary

Phase 5 delivers the investigator-facing explainability UI on top of existing backend XAI payloads. No new ML, consensus, or persistence logic unless a minimal response-field pass-through is required for UI consumption.

In scope:
- Expandable **Explainability Drawer** on the analysis dashboard with:
  - SHAP horizontal bar charts (Recharts) from `result.xai.shap_values`
  - Level 1 analytical counterfactual sensitivity controls (chunk selector + per-agent sliders showing gradient-driven statements)
  - Interactive Plotly evidence graph from `result.xai.evidence_graph`
- **Detailed Forensic Explanation Tab** with:
  - Structured narrative sections from `result.narrative`
  - Active contradiction / threat warnings from `result.timeline[].threat_warnings` and `result.diagnostics.warnings`
  - Tabular evidence breakdown (z-score tables from `result.feature_analysis`, agent/chunk details)

Out of scope:
- Backend changes to SHAP, counterfactual, narrative, or evidence graph engines (Phase 3/4 already deliver payloads).
- Level 2 perturbation counterfactual simulation (v2).
- LLM narrative rewriting (v2).
- Replacing Phase 4 uploader progress or backend job endpoints.
- Reworking the dashboard summary panels beyond wiring drawer/tab entry points.

</domain>

<decisions>
## Implementation Decisions

### Explainability Drawer
- **D-01:** Add a slide-out drawer anchored to the dashboard, toggled by a primary "Explainability" action — not a separate route.
- **D-02:** Reuse `ShapBarChart` from `frontend/src/features/analysis/AnalysisCharts.jsx`; map `xai.shap_values.summary.average_values` to `{ name, score }` rows (score scaled for display).
- **D-03:** Counterfactual UI is **Level 1 analytical sensitivity only**: chunk selector over `xai.counterfactuals.chunks`, per-agent range input/slider bound to `estimated_delta_for_10pct` or gradient magnitude, display backend `statement` text — no simulated verdict recompute on the client.
- **D-04:** Plotly graph lives in a dedicated component using `react-plotly.js`, converting `evidence_graph.nodes` and `evidence_graph.edges` into a layered network layout (layer on Y-axis, stable node order on X-axis).
- **D-05:** Phase 4 `EvidenceGraph.jsx` summary panel remains on the main dashboard overview; the drawer hosts the interactive Plotly visualization.

### Detailed Explanation Tab
- **D-06:** Add in-dashboard tab switcher: **Overview** (current dashboard layout) and **Forensic Explanation** (new tab).
- **D-07:** Render narrative as section cards parsed from `narrative.structured_summary` (`Finding`, `Evidence`, `Reliability`, `Confidence`, `Contradictions`, `Explainability`) with fallback to `narrative.human_summary`.
- **D-08:** Contradiction alerts aggregate chunk-level `timeline[].threat_warnings` plus `diagnostics.warnings`; show severity, time range, and description.
- **D-09:** Evidence grid/table shows acoustic z-score rows from `feature_analysis.acoustic_features` and chunk agent calibrated details from `timeline[].details` where available.

### Phase Boundary & Compatibility
- **D-10:** Frontend-only phase; consume existing `AnalysisResponse` fields from job result and history reload paths.
- **D-11:** Graceful empty states when `xai`, `narrative`, or `evidence_graph` are missing (older reports).
- **D-12:** Match existing glass-panel styling, `framer-motion` transitions, and `lucide-react` icons — no new CSS framework.

### the agent's Discretion
- Exact drawer width, animation timing, and tab label strings as long as UX stays consistent with the existing dashboard.
- Plotly layout algorithm details (layer bands vs force layout) as long as nodes/edges remain readable and layer metadata is visible.
- Whether counterfactual controls use sliders or numeric steppers, provided they expose chunk selection and per-agent sensitivity statements.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope
- `DFXAI_project_spec.md` — UI layout, SHAP/counterfactual/evidence graph/narrative requirements (sections 8.1, 15, 16).
- `.planning/PROJECT.md` — Active requirements `UI-02`, `UI-03`.
- `.planning/ROADMAP.md` — Phase 5 goal and success criteria.
- `.planning/REQUIREMENTS.md` — Requirement definitions for UI-02 and UI-03.

### Prior Phase Deliverables
- `.planning/phases/04-preprocessing-multi-stage-real-time-feedback-ui/SUMMARY.md` — Evidence graph + progress UI; explicit Phase 5 deferral.
- `.planning/phases/03-exact-shapley-coalition-analytical-counterfactuals/SUMMARY.md` — XAI payload shapes.

### Backend Payload Contracts (read-only for Phase 5)
- `backend/api/routes/analysis.py` — `_build_xai_payload`, narrative assembly, `frontend_timeline` threat_warnings.
- `backend/explainability/narrative_engine.py` — `REQUIRED_SECTIONS`.
- `backend/explainability/evidence_graph.py` — graph node/edge schema.
- `backend/api/schemas/analysis.py` — `AnalysisResponse` fields.

### Frontend Integration Points
- `frontend/src/features/analysis/Dashboard.jsx` — mount drawer trigger and tab switcher.
- `frontend/src/features/analysis/AnalysisCharts.jsx` — existing `ShapBarChart`.
- `frontend/src/components/forensic/EvidenceGraph.jsx` — Phase 4 summary panel (keep on overview).
- `frontend/src/components/forensic/FeatureAnalysisPanel.jsx` — z-score / signal patterns to mirror in explanation tab.
- `frontend/src/index.css` — styling conventions.
- `frontend/package.json` — `recharts`, `plotly.js`, `react-plotly.js` already installed.

</canonical_refs>

<specifics>
## Specific Ideas

- Drawer should feel like an investigator console: SHAP attribution on the left, counterfactual sensitivity in the center, Plotly graph spanning the lower/right area.
- Explanation tab should read like a forensic report: narrative sections first, then threat alerts, then tabular evidence.
- Do not duplicate Phase 4 progress UI or replace the overview dashboard panels.

</specifics>

<deferred>
## Deferred Ideas

- Level 2 perturbation counterfactual simulation (v2 / XAI-11).
- LLM narrative rewriter (v2 / XAI-12).
- Export-to-PDF or print layouts.
- Full graph filtering/search controls beyond basic layer coloring.

</deferred>

---

*Phase: 05-explanations-console-shap-plotly-graph-drawer*
*Context gathered: 2026-05-24*

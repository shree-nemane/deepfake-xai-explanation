# Phase 5 Research: Explainability Drawer & Forensic Explanation Tab

**Phase:** 05-explanations-console-shap-plotly-graph-drawer
**Date:** 2026-05-24
**Status:** Complete

## Research Question

What is needed to plan Phase 5: consume existing XAI/narrative payloads in a drawer (SHAP, counterfactual sensitivity, Plotly graph) and a detailed forensic explanation tab without backend rework?

## Current State

- Backend already returns `xai.shap_values`, `xai.counterfactuals`, `xai.evidence_graph`, and `narrative` on `AnalysisResponse` (`backend/api/routes/analysis.py`).
- `frontend/package.json` includes `recharts`, `plotly.js`, and `react-plotly.js` but no component imports Plotly yet.
- `AnalysisCharts.jsx` exports `ShapBarChart` — unused by dashboard today.
- `EvidenceGraph.jsx` renders a **summary** panel from graph nodes; not an interactive Plotly network.
- `Dashboard.jsx` renders a single overview layout with no drawer or secondary tab.
- `VisualXAI.jsx` shows Grad-CAM/IG images but is not mounted in `Dashboard.jsx`.
- Timeline entries include `threat_warnings`; `feature_analysis.acoustic_features` includes `avg_z_score`.

## Recommended Approach

### Plan Split (MVP vertical slices)

| Plan | Wave | Requirement | Delivers |
|------|------|-------------|----------|
| 05-01 | 1 | UI-02 | Drawer shell + SHAP chart + counterfactual sensitivity panel + Plotly graph |
| 05-02 | 2 | UI-03 | Dashboard tab switcher + narrative sections + threat alerts + evidence tables |

Wave 2 depends on Wave 1 because both modify `Dashboard.jsx` and share dashboard-level navigation state.

### Explainability Drawer (05-01)

1. **`ExplainabilityDrawer.jsx`** — fixed right slide-over (`framer-motion`), backdrop click closes, `open`/`onClose`/`result` props.
2. **`ShapContributionPanel.jsx`** — transform `result.xai?.shap_values?.summary?.average_values` into Recharts data; show `shap_summary` caption.
3. **`CounterfactualPanel.jsx`** — chunk `<select>` over `counterfactuals.chunks`; per-agent slider 0–20% mapped to `estimated_delta_for_10pct`; show `sensitivities[agent].statement`.
4. **`PlotlyEvidenceGraph.jsx`** — map nodes to `{ x, y, text, layer, type }`, edges to Plotly `layout.shapes` or `scatter` line traces; color by `layer` or `status`.
5. Wire **`Dashboard.jsx`**: "Open Explainability" button; pass full `result`.

### Detailed Explanation Tab (05-02)

1. **`DashboardViewTabs.jsx`** — local state `overview | explanation`.
2. **`ForensicExplanationTab.jsx`** — container for narrative, alerts, tables.
3. **`NarrativeSections.jsx`** — split `structured_summary` on `## Section` headers; card per `NarrativeEngine.REQUIRED_SECTIONS` name.
4. **`ContradictionAlerts.jsx`** — flatten `timeline[].threat_warnings` with chunk times; append `diagnostics.warnings`.
5. **`EvidenceBreakdownTable.jsx`** — table of acoustic features (`name`, `avg_z_score`, `severity`) plus optional per-chunk agent rows from timeline `details`.

### Data Mapping Reference

```text
SHAP bars:     result.xai.shap_values.summary.average_values  → { name: agent, score: abs(value)*100 }
Counterfactual: result.xai.counterfactuals.chunks[i].sensitivities[agent]
Plotly graph:  result.xai.evidence_graph.nodes / .edges
Narrative:     result.narrative.structured_summary | human_summary
Threats:       result.timeline[].threat_warnings + result.diagnostics.warnings
Z-scores:      result.feature_analysis.acoustic_features[].avg_z_score
```

## Risks

| Risk | Mitigation |
|------|------------|
| Plotly bundle size slows build | Lazy-import `react-plotly.js` inside `PlotlyEvidenceGraph.jsx`. |
| Missing XAI on old reports | Empty-state messages in drawer/tab sections. |
| Counterfactual mistaken for Level 2 sim | Label UI "Analytical Sensitivity (Level 1)"; show backend statements only. |
| Dashboard layout regression | Keep overview tab identical to current `Dashboard` content; add tabs without removing panels. |

## Validation Architecture

- **Automated:** `npm run build` after each plan; extend `tests/integration/test_validation.py` only if new response fields are added (not expected).
- **Manual UAT:** Upload sample audio → open drawer → verify SHAP bars, sensitivity statements, Plotly nodes → switch to Explanation tab → verify narrative sections and threat rows.
- **Regression:** `python -m pytest tests\xai tests\consensus tests\integration\test_validation.py -q` unchanged green.

## RESEARCH COMPLETE

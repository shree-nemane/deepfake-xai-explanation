# Phase 5 Pattern Map

**Phase:** 05-explanations-console-shap-plotly-graph-drawer
**Date:** 2026-05-24

## New Files → Closest Analogs

| New File | Role | Analog | Pattern to Reuse |
|----------|------|--------|------------------|
| `ExplainabilityDrawer.jsx` | Slide-over shell | `Uploader.jsx` motion + glass panels | `framer-motion`, backdrop overlay, `lucide-react` icons |
| `ShapContributionPanel.jsx` | SHAP chart | `AnalysisCharts.jsx` → `ShapBarChart` | Import and reuse `ShapBarChart`; data transform only |
| `CounterfactualPanel.jsx` | Sensitivity UI | `FeatureAnalysisPanel.jsx` → `SignalRow` | Slider + label rows, severity classes |
| `PlotlyEvidenceGraph.jsx` | Network viz | (new) | Lazy `react-plotly.js` import; dark theme matching CSS vars |
| `DashboardViewTabs.jsx` | Tab switcher | `Sidebar.jsx` active state | Button group with active class |
| `ForensicExplanationTab.jsx` | Tab content | `FeatureAnalysisPanel.jsx` | Section header + grid of cards |
| `NarrativeSections.jsx` | Narrative cards | `ConsensusPanel.jsx` metrics | `.glass` cards, `.panel-title` |
| `ContradictionAlerts.jsx` | Threat list | `FeatureAnalysisPanel` warnings block | `AlertTriangle`, severity pills |
| `EvidenceBreakdownTable.jsx` | Z-score table | `FeatureAnalysisPanel` signal rows | Table/stat-list styling from `index.css` |

## Data Flow

```text
App.jsx result
  → Dashboard.jsx
       ├─ overview tab (existing panels)
       ├─ ExplainabilityDrawer(result)
       └─ ForensicExplanationTab(result)  [tab 2]
```

## CSS Conventions

- Add classes to `frontend/src/index.css`: `.explainability-drawer`, `.drawer-backdrop`, `.dashboard-tabs`, `.narrative-section`, `.threat-alert`, `.evidence-table`
- Follow existing `--primary`, `--error`, `--warning`, `.glass` tokens

## Do Not Duplicate

- Do not rewrite `EvidenceGraph.jsx` summary panel — drawer gets Plotly variant.
- Do not add axios calls — all data from `result` prop.

## PATTERN MAPPING COMPLETE

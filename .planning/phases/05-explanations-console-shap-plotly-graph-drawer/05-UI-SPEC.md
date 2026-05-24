# Phase 5 UI Design Contract

**Phase:** 05-explanations-console-shap-plotly-graph-drawer
**Status:** Approved for planning
**Created:** 2026-05-24

## Screen Inventory

| Screen / Region | Purpose |
|-----------------|---------|
| Dashboard Overview (existing) | Unchanged layout: verdict banner, consensus, evidence summary, agents, timeline, heatmap |
| Explainability Drawer | Slide-over console for SHAP, counterfactual sensitivity, Plotly graph |
| Forensic Explanation Tab | Report-style narrative, alerts, evidence tables |

## Explainability Drawer

### Layout
- **Position:** Fixed right panel, width `min(520px, 92vw)`, full viewport height below header.
- **Trigger:** Primary button in dashboard verdict banner area: "Open Explainability" with `Brain` or `Sparkles` icon.
- **Sections (top → bottom):**
  1. Header: title + close button
  2. SHAP Contributions (Recharts horizontal bar chart)
  3. Analytical Sensitivity (chunk selector + agent sliders + statement text)
  4. Interactive Evidence Graph (Plotly, min-height 320px)

### SHAP Chart
- Data: average Shapley values per agent
- Bar color: `var(--error)` if value pushes fake direction (positive avg for fake-leaning), else `var(--primary)`
- Empty state: "No Shapley attributions available for this report."

### Counterfactual Controls
- Subtitle: "Level 1 Analytical Sensitivity — not perturbation simulation"
- Chunk dropdown labels: `Chunk {index} ({start}s–{end}s)`
- Per-agent slider: 0–20% with live statement from backend payload
- Empty state: "No sensitivity gradients available."

### Plotly Graph
- Nodes positioned by layer (Y) and index within layer (X)
- Edge lines with arrow markers; hover shows node label + type
- Empty state: "No evidence graph available."

### Motion & A11y
- Enter/exit: `framer-motion` slide from right (200ms)
- Focus trap not required for v1; backdrop click closes drawer
- `aria-label` on open/close buttons

## Forensic Explanation Tab

### Tab Bar
- Two tabs below dashboard header: **Overview** | **Forensic Explanation**
- Default: Overview (preserves current behavior)

### Narrative Sections
- Six section cards matching narrative engine sections: Finding, Evidence, Reliability, Confidence, Contradictions, Explainability
- Parse `structured_summary` markdown headers; fallback single card with `human_summary`

### Contradiction Alerts
- Alert strip/card list sorted by severity (high → low)
- Each row: severity badge, time range, threat type, description
- Include diagnostic warnings as secondary alert style

### Evidence Breakdown Table
- Table columns: Signal / Agent, Value, Z-Score, Severity, Notes
- Primary rows from `feature_analysis.acoustic_features`
- Optional expandable rows for chunk agent details from timeline

## Visual Tokens (reuse existing)
- Panels: `.glass`, `.panel-title`
- Verdict colors: `.text-error`, `.text-warning`, `.text-success`
- Spacing: match `Dashboard.jsx` `gap-6` grid rhythm

## Out of Scope (UI)
- Mobile-first responsive polish beyond drawer `92vw` cap
- Dark/light theme toggle
- Graph node filtering UI

---

*Consumed by plans 05-01 and 05-02*

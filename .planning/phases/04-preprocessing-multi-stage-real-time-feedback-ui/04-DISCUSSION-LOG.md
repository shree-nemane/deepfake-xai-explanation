# Phase 4: Preprocessing & Multi-Stage Real-Time Feedback UI - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-24
**Phase:** 04-preprocessing-multi-stage-real-time-feedback-ui
**Areas discussed:** Progress behavior, Evidence graph shape, Phase boundary

---

## Progress Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Deterministic local stages | Show inferred stages in the existing long-running POST flow without a backend progress channel. | |
| Backend progress endpoint/stream | Add a backend status endpoint or streaming transport so the UI reflects real stage updates. | ✓ |
| You decide | Let the implementation plan choose the least risky mechanism. | |

**User's choice:** Use a backend progress endpoint/stream for real-time stage updates.
**Notes:** The existing uploader progress animation is not sufficient as the source of truth.

---

## Evidence Graph Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Lightweight relationship summary | Keep the current frontend-oriented relationship map and enrich it slightly. | |
| 6-layer directed JSON graph | Generate a backend graph with explicit layers, typed nodes, and directed edges. | ✓ |
| You decide | Let planning pick the graph structure. | |

**User's choice:** Use a 6-layer directed JSON evidence graph.
**Notes:** The graph should map Audio Input -> Preprocessing/Reliability -> Forensic Agents -> Consensus Arbitration -> XAI Artifacts -> Verdict & Narrative.

---

## Phase Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Graph data + progress UI | Stop Phase 4 at evidence graph data generation/persistence and backend-driven progress UI. | ✓ |
| Include drawer/tab work now | Pull the explainability drawer and detailed forensic explanation tab into Phase 4. | |
| You decide | Let planning decide how much UI belongs here. | |

**User's choice:** Phase 4 should stop at graph data plus progress UI.
**Notes:** The explainability drawer and detailed explanation tab are explicitly deferred to Phase 5.

---

## the agent's Discretion

- Choose the most reliable local-app transport for progress updates during planning.
- Define exact graph field names and implementation boundaries, provided the graph stays directed, typed, deterministic, and visualization-ready.

## Deferred Ideas

- Expandable explainability drawer.
- Detailed forensic explanation tab.
- Phase 5 chart and interactive graph polish.

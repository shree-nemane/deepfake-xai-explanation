---
phase: 5
slug: explanations-console-shap-plotly-graph-drawer
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-24
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (backend), Vite build (frontend) |
| **Config file** | `pytest` default; `frontend/vite.config.js` |
| **Quick run command** | `npm run build` (frontend/) |
| **Full suite command** | `python -m pytest tests\xai tests\consensus tests\integration\test_validation.py -q` + `npm run build` |
| **Estimated runtime** | ~45 seconds |

---

## Sampling Rate

- **After every task commit:** Run `npm run build` from `frontend/` when JSX/CSS changed
- **After every plan wave:** Run full backend pytest suite + frontend build
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 05-01-01 | 01 | 1 | UI-02 | build | `npm run build` | ⬜ pending |
| 05-01-02 | 01 | 1 | UI-02 | build | `npm run build` | ⬜ pending |
| 05-01-03 | 01 | 1 | UI-02 | build | `npm run build` | ⬜ pending |
| 05-01-04 | 01 | 1 | UI-02 | build | `npm run build` | ⬜ pending |
| 05-01-05 | 01 | 1 | UI-02 | build+pytest | full suite | ⬜ pending |
| 05-02-01 | 02 | 2 | UI-03 | build | `npm run build` | ⬜ pending |
| 05-02-02 | 02 | 2 | UI-03 | build | `npm run build` | ⬜ pending |
| 05-02-03 | 02 | 2 | UI-03 | build | `npm run build` | ⬜ pending |
| 05-02-04 | 02 | 2 | UI-03 | build+pytest | full suite | ⬜ pending |

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements — no new test framework install.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Drawer SHAP/Plotly render with live upload | UI-02 | Visual/chart libraries | Upload audio, open drawer, confirm charts render |
| Explanation tab narrative + alerts | UI-03 | Markdown parsing UX | Switch tab, confirm six narrative sections and threat rows |

---

## Validation Sign-Off

- [x] All tasks have verify commands
- [x] Sampling continuity maintained
- [x] Wave 0 not required
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending execution

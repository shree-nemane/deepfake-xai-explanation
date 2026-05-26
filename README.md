# Consensus-Based Explainable Forensic Audio Intelligence Platform

Investigator-grade platform for authenticating speech audio, detecting deepfakes and partial synthesis, and producing **transparent forensic evidence** — not just a probability score.

Multi-agent temporal consensus, reliability-aware suppression, exact Shapley attributions, contradiction warnings, deterministic narratives, and a full explainability UI.

---

## What this system does

1. **Preprocesses** uploaded audio (LUFS normalization, VAD, dual 16 kHz / 48 kHz streams)
2. **Segments** active speech into 2-second overlapping chunks
3. **Runs five forensic agents** per chunk (ConvNext, WavLM, AASIST, Acoustic, Reliability)
4. **Suppresses** low-trust evidence dynamically (fail-closed below reliability 0.20)
5. **Reasons** over agreement and contradictions (voice clone, splice, partial synthesis)
6. **Generates XAI** — exact SHAP, Level 1 counterfactual sensitivity, 6-layer evidence graph
7. **Writes** deterministic narrative reports and persists everything to SQLite
8. **Presents** results in a React investigation dashboard with live progress, explainability drawer, and forensic explanation tab

---

## v1 milestone status

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | DB consolidation, suppression engine, test layout | Complete |
| 2 | Contradiction warnings, temporal alignment | Complete |
| 3 | Exact SHAP, analytical counterfactuals, narrative engine | Complete |
| 4 | Evidence graph data + backend-driven upload progress | Complete |
| 5 | Explainability drawer + forensic explanation tab | Complete |

All 17 mapped v1 requirements are implemented. See `DFXAI_project_spec.md` for the full product specification.

---

## Architecture

```text
Upload (React)
    → POST /analyze/jobs + SSE progress
        → Preprocessing (LUFS, VAD, dual-stream)
        → 2s overlapping chunks
        → Forensic agents (ConvNext, WavLM, AASIST, Acoustic, Reliability)
        → Reliability suppression + consensus engine
        → XAI (SHAP, counterfactuals, evidence graph, narrative)
        → SQLite persistence
    → Dashboard + Explainability drawer + Explanation tab
```

### Forensic agents

| Agent | Role |
|-------|------|
| **ConvNext** | Spectral / spectrogram artifact detection (48 kHz) |
| **WavLM** | Phonetic instability and speech realism (16 kHz) |
| **AASIST** | Deterministic waveform spoof heuristics (v1) |
| **Acoustic** | Biological plausibility (jitter, shimmer, MFCC z-scores) |
| **Reliability** | SNR, clipping, quality — drives suppression |

### Explainability (v1)

- **Exact Shapley values** over 4 voting agents (16 coalitions, no Monte Carlo)
- **Level 1 analytical sensitivity** — gradient-based counterfactual statements
- **6-layer evidence graph** — JSON persisted and visualized in Plotly
- **Deterministic narrative** — six structured sections (no LLM in v1)

---

## Tech stack

| Layer | Stack |
|-------|--------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, SQLite, PyTorch, Librosa |
| Frontend | React 19, Vite, Recharts, Plotly (lazy-loaded), Framer Motion |
| ML | ConvNext, WavLM (lazy via ModelHub), Silero VAD |
| Tests | pytest (unit, integration, consensus, xai) |

---

## Project structure

```text
deepfake-xai/
├── backend/
│   ├── app.py                    # FastAPI entry
│   ├── api/routes/analysis.py    # All /analyze endpoints
│   ├── agents/                   # Forensic agent plugins
│   ├── consensus/                # Suppression, calibration, threats
│   ├── explainability/           # SHAP, counterfactuals, graph, narrative
│   ├── orchestration/            # Chunk loop, agent registry
│   ├── preprocessing/            # Dual-stream audio processor
│   ├── persistence/              # SQLAlchemy models + DB
│   └── migrations/               # Schema validation
├── frontend/
│   └── src/
│       ├── App.jsx                 # Upload, progress SSE, routing
│       ├── features/analysis/      # Dashboard, uploader, charts
│       └── components/
│           ├── forensic/           # Overview panels
│           └── explainability/     # Drawer + explanation tab (Phase 5)
├── tests/
│   ├── unit/ integration/ consensus/ xai/ performance/ benchmark/
├── docs/
│   └── API_REFERENCE.md          # Full HTTP API documentation
├── DFXAI_project_spec.md         # Master PRD + system design
├── DFXAI_agent_prompt.md         # Implementation agent reference
└── .planning/                    # GSD planning (development branch only)
```

---

## Quick start

### Prerequisites

- Python 3.10+
- Node.js 18+
- ~4 GB RAM for neural models (CPU works; GPU optional)

### 1. Backend

```powershell
# From project root
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m backend.app
```

API: `http://localhost:8000`  
OpenAPI: `http://localhost:8000/docs`

**Verify the forensic API** (not another app on port 8000):

```powershell
curl http://localhost:8000/
# Expected: {"status":"online","message":"Deepfake Forensic AI API is operational."}
```

If you see a Django page or connection errors, stop other servers on port 8000 and run `python -m backend.app` again. The React dev server must use `http://localhost:5173` so CORS matches `backend/app.py`.

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

UI: `http://localhost:5173`

### 3. Analyze audio

1. Open the UI → **Forensic Investigation**
2. Upload `.wav` or `.mp3`
3. Watch backend-driven progress stages
4. Review dashboard → **Open Explainability** drawer or **Forensic Explanation** tab

---

## Testing

```powershell
.venv\Scripts\Activate.ps1

# Core regression suite (recommended)
python -m pytest tests\xai tests\consensus tests\integration\test_validation.py -q

# Full suite (includes skipped performance/benchmark tests)
python -m pytest tests -q

# Schema validation
python -m backend.migrations.validate_schema

# Frontend production build
cd frontend
npm run build
```

**Last verified:** 61 passed, 4 skipped (performance/benchmark), frontend build OK.

---

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Health check |
| POST | `/analyze/` | Synchronous analyze |
| POST | `/analyze/jobs` | Start async job |
| GET | `/analyze/jobs/{id}/progress` | Poll progress |
| GET | `/analyze/jobs/{id}/events` | SSE progress stream |
| GET | `/analyze/jobs/{id}/result` | Final report |
| GET | `/analyze/history` | Recent reports |
| GET | `/analyze/{report_id}` | Load saved report |

Full request/response schemas: **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)**

---

## Frontend features

### Investigation dashboard (Overview tab)

- Verdict banner with confidence and convergence
- Consensus panel and agent cards
- Evidence graph summary (Phase 4)
- Feature analysis, reliability, timeline, Grad-CAM heatmap

### Explainability drawer (UI-02)

- SHAP contribution bar chart (Recharts)
- Level 1 analytical sensitivity controls per chunk
- Interactive Plotly evidence graph

### Forensic Explanation tab (UI-03)

- Six narrative sections (Finding → Explainability)
- Contradiction / threat alerts with time ranges
- Acoustic z-score and per-chunk agent evidence tables

---

## Configuration & data

| Item | Location | Notes |
|------|----------|-------|
| SQLite DB | `forensic_intelligence.db` | Created on first run |
| Upload temp | `uploads/` | Gitignored |
| CORS | `backend/app.py` | `allow_origins=["*"]` — local only |
| Job store | In-memory | Resets on server restart |

---

## Git branches

| Branch | Purpose |
|--------|---------|
| **`development`** | Active work; includes `.planning/` for GSD continuity |
| **`main`** | Clean production branch — application code + docs only, **no** `.planning/` or agent metadata |

Develop on `development`. Release to `main` without planning artifacts.

---

## Known limitations (v1)

- Sequential chunk processing (no multithreaded agents yet)
- In-memory job progress (not durable across restarts)
- AASIST is deterministic heuristics, not full neural deployment
- No Level 2 perturbation counterfactuals or LLM narrative (v2)
- ESLint config has pre-existing JSX `no-unused-vars` noise; production build passes
- Plotly bundle is large (~4.6 MB) — lazy-loaded but first drawer open may be slow

---

## Documentation index

| Document | Description |
|----------|-------------|
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | HTTP API, schemas, examples |
| [DFXAI_project_spec.md](DFXAI_project_spec.md) | Master PRD + system design |
| [DFXAI_agent_prompt.md](DFXAI_agent_prompt.md) | Agent implementation rules |
| `http://localhost:8000/docs` | Live OpenAPI (when backend running) |

---

## GSD development

This project is managed with [GSD](https://github.com/anthropics/get-shit-done) on the `development` branch.

```powershell
# Resume / check progress
/gsd-progress
/gsd-progress --next

# Local venv + SDK
.venv\Scripts\Activate.ps1
C:\Users\rahul\AppData\Roaming\npm\gsd-sdk.cmd query init.progress
```

Planning state lives in `.planning/` (development only).

---

## License

Research and educational use. See project evaluators / academic context in `DFXAI_project_spec.md`.

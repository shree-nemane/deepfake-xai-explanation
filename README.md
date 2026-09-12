# Consensus-Based Explainable Forensic Audio Intelligence Platform

Investigator-grade platform for authenticating speech audio, detecting deepfakes and partial synthesis, and producing **transparent forensic evidence** — not just a probability score.

Multi-agent temporal consensus, reliability-aware suppression, exact Shapley attributions, contradiction warnings, deterministic narratives, and a full explainability UI.

---

## What this system does

1. **Preprocesses** uploaded audio (LUFS normalization, Silero VAD, continuous timeline preservation, dual 16 kHz / 48 kHz streams; supports WAV, FLAC, MP3, OGG)
2. **Segments** active speech into 2-second overlapping chunks
3. **Runs forensic agent panel** per chunk (ConvNeXt, WavLM, Acoustic, Reliability)
4. **Suppresses** low-trust evidence dynamically based on real-time SNR and clipping
5. **Reasons** over agreement and contradictions (voice clone, splice, partial synthesis)
6. **Generates explainability** — exact Shapley values (16 coalitions), Level 1 counterfactual sensitivity, 6-layer evidence graph
7. **Writes** deterministic narrative reports and persists everything to SQLite
8. **Presents** results in an investigator-grade React dashboard with a 4-Agent Consensus Bench, continuous timeline chunk inspector, integrated SHAP & counterfactual explainability, and case dossier export

---

## Architecture

```text
Upload / Specimen Selection (React)
    → POST /analyze/jobs + SSE progress stream
        → Preprocessing (EBU R128 LUFS, Silero VAD, continuous dual-stream)
        → 2.0s overlapping temporal chunks (50% overlap)
        → Forensic agents (ConvNeXt, WavLM single-pass, Acoustic biological, Reliability)
        → Reliability suppression + multi-agent consensus engine
        → Explainability (exact SHAP, counterfactuals, evidence graph, deterministic narrative)
        → SQLite relational persistence
    → Unified 4-Agent Consensus Bench + Continuous Timeline + Explainability View
```

### Forensic agents

| Agent | Role |
|-------|------|
| **ConvNeXt** | Spectral / spectrogram artifact detection (48 kHz Mel bands) |
| **WavLM** | Phonetic instability & transformer temporal entropy (16 kHz single-pass) |
| **Acoustic** | Biological plausibility (pitch stability, normalized jitter %, shimmer, MFCC z-scores) |
| **Reliability** | Signal-to-noise ratio (HPSS dB), clipping ratio, spectral flatness — drives suppression |

### Explainability

- **Exact Shapley values** over 4 voting agents (16 coalitions, no Monte Carlo)
- **Level 1 analytical sensitivity** — gradient-based counterfactual statements
- **6-layer evidence graph** — JSON persisted and visualized in Plotly
- **Deterministic narrative** — six structured sections (rule-based, reproducible)

---

## Tech stack

| Layer | Stack |
|-------|--------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, SQLite, PyTorch, Librosa |
| Frontend | React 19, Vite, Recharts, Plotly (lazy-loaded), Framer Motion |
| ML | ConvNext, WavLM (lazy via ModelHub), Silero VAD |
| Tests | pytest (unit, integration, consensus, explainability) |

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
│   └── persistence/              # SQLAlchemy models + DB
├── frontend/
│   └── src/
│       ├── App.jsx               # Upload, progress SSE, routing
│       ├── features/analysis/    # Dashboard, uploader
│       └── components/
│           ├── forensic/         # Overview panels, chunk inspector
│           └── explainability/   # Drawer + explanation tab
├── tests/                        # pytest suites
├── scripts/
│   ├── run-dev.ps1               # Start API + UI (Windows)
│   ├── verify.py                 # Quick API smoke test
│   └── extract_report_sample.py  # Export redacted report JSON for papers
├── API_REFERENCE.md              # HTTP API documentation
├── RESEARCH_AND_REPORT_DOC.md    # Paper / blackbook / architecture source
└── DFXAI_project_spec.md         # Product specification
```

---

## Quick start

### Prerequisites

- Python 3.10+
- Node.js 18+
- ~4 GB RAM for neural models (CPU works; GPU optional)

### Option A — helper script (Windows)

```powershell
.\scripts\run-dev.ps1
```

### Option B — manual

**Backend** (project root):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m backend.app
```

**Frontend**:

```powershell
cd frontend
npm install
npm run dev
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| OpenAPI | http://localhost:8000/docs |
| UI | http://localhost:5173 |

### Verify the forensic API

Port **8000** must serve this project, not another app (e.g. Django):

```powershell
curl http://localhost:8000/
# {"status":"online","message":"Deepfake Forensic AI API is operational."}
```

If upload fails with a network/CORS error, stop other servers on port 8000 and restart `python -m backend.app`. The UI must run on `http://localhost:5173` (matches CORS in `backend/app.py`).

### Analyze audio

1. Open the UI → **Forensic Investigation**
2. Upload `.wav` or `.mp3`
3. Watch backend-driven progress stages
4. Review the dashboard — timeline chunk inspector, explainability drawer, forensic explanation tab

---

## Testing

```powershell
.venv\Scripts\Activate.ps1

# Recommended regression
python -m pytest tests\xai tests\consensus tests\forensic tests\integration\test_validation.py -q

# Full suite
python -m pytest tests -q

# Schema validation
python -m backend.migrations.validate_schema

# API smoke test (requires sample wav in repo root)
python scripts\verify.py

# Frontend production build
cd frontend
npm run build
```

---

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Health check |
| POST | `/analyze/` | Synchronous analyze (WAV, FLAC, MP3, OGG) |
| POST | `/analyze/jobs` | Start async job |
| GET | `/analyze/jobs/{id}/progress` | Poll progress |
| GET | `/analyze/jobs/{id}/events` | SSE progress stream |
| GET | `/analyze/jobs/{id}/result` | Final report |
| GET | `/analyze/history` | Recent reports |
| GET | `/analyze/{report_id}` | Load saved report |
| GET | `/samples` | List built-in test specimens |
| GET | `/samples/{filename}` | Stream specimen audio (`fake1.wav`, `adi.wav`) |

Full schemas: **[API_REFERENCE.md](API_REFERENCE.md)**

---

## Frontend features

- **Investigation Ingestion** — Drag & drop evidence vault, format tags (WAV, FLAC, MP3, OGG), instant 1-click test specimens (`fake1.wav`, `adi.wav`), and real-time SSE progress tracking.
- **4-Agent Consensus Bench** — Unified cards for ConvNeXt Spectral, WavLM Phonetic, Acoustic Biological, and Signal Trustworthiness agents.
- **Continuous Timeline & Chunk Inspector** — 2.0s overlapping chunk timeline with event classification (stable, contradiction, splice), mel-spectrogram preview, and per-chunk suspicion rationales.
- **Forensic Feature Telemetry** — Intake parameters, neural classifier risk meters, biological vocal tract deviation rankings (z-scores), and analyst diagnostic notes.
- **Unified Forensic Explainability** — Case narrative findings, contradiction threat classification (D-01 Voice Clone, D-02 Splice), exact Game-Theoretic SHAP attributions, and counterfactual sensitivity sliders.
- **Case Dossier Export Toolbar** — 1-click copy of executive case summary, `.txt` audit report download, and raw evidence `.json` export.
- **Streamlined Navigation & Real Telemetry** — New Investigation, Forensic Report (with dynamic active badge), Audit History, and System Telemetry with live engine connection status.

---

## Configuration

| Item | Location | Notes |
|------|----------|-------|
| SQLite DB | `forensic_intelligence.db` | Created on first run |
| Upload temp | `uploads/` | Gitignored |
| CORS | `backend/app.py` | `localhost:5173` / `127.0.0.1:5173` |
| Job progress | In-memory | Resets on server restart |

---

## Git branches

| Branch | Purpose |
|--------|---------|
| **`development`** | Active development |
| **`main`** | Production-facing branch — application code and docs only |

Develop on `development`. Merge to `main` for production-facing releases (application code and public documentation only).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| Blank / blue screen after analysis | React render error (e.g. malformed diagnostics) | Pull latest; hard-refresh browser; check browser console |
| CORS or network error on upload | Wrong process on port 8000 | `curl http://localhost:8000/` must return forensic API JSON |
| Explainability drawer dims screen | Plotly load failure | Close drawer (Esc); use Overview evidence graph; check console |
| No mel spectrogram in history | Report saved before mel feature | Re-run analysis on current build |
| Slow first drawer open | Large Plotly bundle | Expected once per session; graph loads after drawer opens |

---

## Known limitations (v1)

- Sequential chunk processing (no multithreaded agents yet)
- In-memory job progress (not durable across restarts)
- AASIST uses deterministic heuristics, not full neural deployment
- No Level 2 perturbation counterfactuals
- Plotly bundle is large (~4.6 MB) — lazy-loaded

---

## Documentation

All reference documents live at the **repository root** for easy sharing with collaborators.

| Document | Description |
|----------|-------------|
| [RESEARCH_AND_REPORT_DOC.md](RESEARCH_AND_REPORT_DOC.md) | **Start here for papers/blackbook** — architecture, methods, case study, JSON excerpts |
| [API_REFERENCE.md](API_REFERENCE.md) | HTTP API, schemas, curl examples |
| [DFXAI_project_spec.md](DFXAI_project_spec.md) | Product specification and system design |
| `sample_report_redacted.json` | Full analysis JSON (generate: `python scripts/extract_report_sample.py`) |
| http://localhost:8000/docs | Live OpenAPI when backend is running |

---

## License

Research and educational use. See `DFXAI_project_spec.md` for academic context.

<!-- refreshed: 2026-05-23 -->
# Architecture

**Analysis Date:** 2026-05-23

## System Overview

```text
React / Vite Investigation UI
`frontend/src/App.jsx`
        |
        v
FastAPI Router Controller
`backend/app.py` -> `backend/api/routes/analysis.py`
        |
        v
Audio Preprocessor (LUFS / VAD / Resampling)
`backend/preprocessing/audio_processor.py`
        |
        v
Timeline & Segment Chunking
`backend/orchestration/timeline_manager.py`
        |
        v
Forensic Multi-Agent Orchestrator
`backend/orchestration/forensic_orchestrator.py`
`backend/agents/*.py` (ConvNext, WavLM, AASIST, Acoustic, Reliability)
        |
        v
Consensus Reasoner & Dynamic Calibrator
`backend/consensus/consensus_engine.py`
`backend/consensus/calibration_engine.py`
        |
        v
Relational Persistence & XAI Grad-CAM
`backend/persistence/database.py`
`backend/explainability/gradcam/gradcam_engine.py`
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| **FastAPI Core Application** | Creates the FastAPI app, sets wide-open CORS headers, triggers SQLite initialization. | `backend/app.py` |
| **API Routers & Schemas** | Exposes REST endpoints (`POST /analyze/`, `GET /analyze/history`), validates input formats, handles DB session dependencies, and maps responses to Pydantic definitions. | `backend/api/routes/analysis.py`, `backend/api/schemas/analysis.py` |
| **Dual-Stream Audio Processor** | Loads audio, checks codec constraints and signal limits, performs EBU R128 LUFS loudness normalization, applies neural Silero VAD to isolate active speech, and splits audio into 16 kHz and 48 kHz aligned arrays. | `backend/preprocessing/audio_processor.py` |
| **Timeline Segment Manager** | Segments raw dual-stream audio into overlapping 2.0-second chunk windows (with 50% overlap). | `backend/orchestration/timeline_manager.py` |
| **Forensic Orchestration Registry** | Maintains a registry of active agents, loops through chunks sequentially, routes them to registered forensic experts, and compiles consensus statistics. | `backend/orchestration/forensic_orchestrator.py`, `backend/orchestration/agent_registry.py` |
| **Spectral Artifact Agent** | Generates mel-spectrogram matrices from 48 kHz chunks, runs them through the ConvNext neural classifier, and triggers Grad-CAM heatmap generation. | `backend/agents/convnext_agent.py` |
| **Phonetic Instability Agent** | Evaluates phonetic structural deviations using WavLM speech embeddings and temporal entropy checks. | `backend/agents/wavlm_agent.py` |
| **Acoustic Plausibility Agent** | Extracts biological features (ZCR, MFCCs, pitch, jitter, shimmer) and compares them against natural-speech baselines via z-score anomaly scoring. | `backend/agents/acoustic_agent.py` |
| **Signal Trustworthiness Agent** | Measures SNR (via HPSS), clipping ratios, and spectral flatness to estimate recording reliability scores, which suppress neural model weights if degradation is severe. | `backend/agents/reliability_agent.py` |
| **Thread-Safe Model Cache** | Manages process-wide lazy loading and memory allocation of large model weights with thread locks. | `backend/agents/model_hub.py` |
| **Consensus Engine** | Calibrates agent confidence using reliability metrics, calculates weighted probability support vectors, and runs deep logic checks to identify partial fakes and voice clones. | `backend/consensus/consensus_engine.py`, `backend/consensus/calibration_engine.py` |
| **Relational Persistence** | Stores permanent records of reports, agent verdicts, timelines, consensus events, and XAI heatmap blobs. | `backend/persistence/database.py` |
| **Investigation Frontend Dashboard** | Organizes layout sections, uploads audio forms, handles Axios routes, and routes data to interactive charts, consensus indicators, and temporal heatmaps. | `frontend/src/App.jsx`, `frontend/src/features/analysis/Dashboard.jsx` |

## Pattern Overview

- **Monorepo Structure**: Separated clean backend (Python, FastAPI, PyTorch) and frontend (Vite, React, custom CSS utilities).
- **Self-Registering Plugins**: Forensic agents inherit `BaseAgent` and automatically register into the central `agent_registry` via side-effects upon module imports.
- **Lazy-Loaded Singleton**: Heavy ML models are centralized inside `ModelHub` to save GPU/CPU memory footprint, utilizing double-checked thread locking for safe execution.
- **Fail-Closed Consensus**: Agreement/contradiction voting systems default to inconclusive verdicts on split votes, keeping decision limits high and secure.
- **Incremental dynamic calibration**: A specific signal-quality agent (`ReliabilityAgent`) determines recording SNR and clipping, actively calibrating and scaling down downstream neural weights to avoid false synthesis verdicts on noisy audio.

## Entry Points

1. **Uvicorn Backend API**: `backend/app.py` started via `python -m backend.app`.
2. **FastAPI POST analyze Route**: `backend/api/routes/analysis.py` handling `/analyze/`.
3. **React Mount**: `frontend/src/main.jsx` mounting `frontend/src/App.jsx`.
4. **Pytest Suite Entry**: Running `python -m pytest` from project root directory to execute all unit and integration assertions.

## Architectural Constraints

- **Sequential Processing**: Core orchestration loops over temporal chunks and forensic agents sequentially.
- **Import-Time Initialization Overhead**: `AudioProcessor` loads Silero VAD weights from PyTorch Hub inside its constructor. Because it is instantiated as a module global in `backend/api/routes/analysis.py`, importing routes initiates network requests and model weights loading, creating slow/brittle module imports.
- **Registry Dependency**: Desired agent modules must be explicitly imported before `agent_registry` registers them. `ForensicOrchestrator` performs `import backend.agents` inside its `__init__` to satisfy this constraint.
- **CORS Configuration**: Allowed origins are set to allow all (`*`) for local convenience.

## Anti-Patterns

### Import-Time Model Loading
- **Issue**: `AudioProcessor` instantiates Silero VAD on route module imports.
- **Impact**: Server startup and test suites can stall while loading or downloading weights, increasing fragility.
- **Mitigation**: Move initialization to a lifespan event hook in `backend/app.py` or load lazily upon the first upload request.

### Sequential Agent Loops
- **Issue**: Chronological audio chunks and multiple agents are iterated sequentially in the main request thread.
- **Impact**: Higher execution latencies for large audio files.
- **Mitigation**: Implement thread pools (`concurrent.futures`) to parallelize chunk analysis across agents.

---

*Architecture analysis: 2026-05-23*

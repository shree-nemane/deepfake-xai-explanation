# Codebase Structure

**Analysis Date:** 2026-05-23

## Directory Layout

```text
deepfake-xai-explanation/
|-- backend/                 # FastAPI server, ML handlers, and forensic orchestration
|   |-- api/                 # API routers and Pydantic validation schemas
|   |-- agents/              # Modular forensic expert agents and ModelHub singleton
|   |-- consensus/           # Voting consensus and Dynamic Calibration engines
|   |-- explainability/      # Grad-CAM spectrogram explainers and temporal heatmap generators
|   |-- forensic/            # Acoustic feature extractors and Z-score anomaly engines
|   |-- models/              # Neural weight loaders and ConvNext/WavLM models
|   |-- persistence/         # SQLite DB schemas and SQLAlchemy ORM models
|   |-- preprocessing/       # EBU LUFS meters and Silero VAD speech processors
|   |-- requirements.txt     # Python backend dependencies
|   `-- app.py               # Main API launch script
|-- frontend/                # React / Vite SPA UI
|   |-- src/                 # JSX application components and custom CSS
|   |   |-- components/      # Reusable UI layouts and forensic visualization widgets
|   |   |-- features/        # Main feature dashboards (analysis, history)
|   |   `-- index.css        # Core custom utility classes and design tokens
|   |-- package.json         # Node.js dependencies and run script declarations
|   `-- vite.config.js       # Vite module resolution bundler config
|-- tests/                   # Pytest automated test harness
|   |-- conftest.py          # Shared audio load fixtures
|   |-- test_pipeline.py     # End-to-end orchestrator pipeline tests
|   |-- test_reliability.py  # Consensus math and registry guard tests
|   `-- test_feature_analysis.py # Individual agent robustness assertions
|-- mock_dataset/            # Mock dataset audio files (real.wav, fake.wav)
|-- uploads/                 # Target folder for temporal uploaded file buffering
|-- forensic_intelligence.db # Active single-file SQLite database
`-- README.md                # System overview and local installation guides
```

## Directory Purposes

### `backend/`
- **`api/`**: Router endpoints (`api/routes/analysis.py`) and schemas (`api/schemas/analysis.py`) mapping incoming parameters and outgoing payload contracts.
- **`agents/`**: Core agent implementations and their registry. Includes `model_hub.py` which aggregates and lazily preloads Torch models.
- **`consensus/`**: Handles weighted arbitration via `consensus_engine.py` and dynamics calibration via `calibration_engine.py`.
- **`explainability/`**: Generates heatmaps (Grad-CAM), temporal graphs, and base64 plots.
- **`forensic/`**: Analyzes biological traits (`forensic/features/acoustic_features.py`) and z-score distances.
- **`persistence/`**: Manages relational entities and table scopes in `database.py`.
- **`preprocessing/`**: Conducts loudness normalization (`audio_processor.py`) and active speech extraction.

### `frontend/src/`
- **`components/layout/`**: Exposes global components (sidebar navigation, header titles).
- **`components/forensic/`**: Provides tailored visual panels (temporal heatmaps, evidence graphs, agent consensus cards).
- **`features/analysis/`**: Exposes core screens (uploader drop-zones, analytical charts).
- **`features/history/`**: Renders dynamic history logs of prior forensic checks.

### `tests/`
- Standard pytest suite designed to verify full pipeline execution, individual agent outputs, consensus edge cases, and schema validation structures without executing redundant GPU operations.

## Where to Add New Code

**New API Endpoint:**
1. Declare path inside `backend/api/routes/`.
2. Map schema specifications under `backend/api/schemas/`.
3. Include router in `backend/app.py` if a new module is introduced.

**New Forensic Agent:**
1. Create `backend/agents/<agent_name>_agent.py`.
2. Inherit from `BaseAgent` and override `analyze_chunk(audio_chunk)`.
3. Call `agent_registry.register("<agent_name>", ...)` at module level.
4. Ensure the new module is imported during startup so registration fires (added to `backend/agents/__init__.py`).

**New UI Component:**
1. Add generic layouts to `frontend/src/components/layout/`.
2. Place specialized forensic graphs or panel widgets under `frontend/src/components/forensic/`.
3. Consume the new widget inside `frontend/src/features/analysis/Dashboard.jsx`.

---

*Structure analysis: 2026-05-23*

<!-- GSD:project-start source:PROJECT.md -->

## Project

**Consensus-Based Explainable Forensic Audio Intelligence Platform**

An investigator-grade digital forensics platform designed to authenticate audio recordings, detect synthetic voice clones (deepfakes), and provide transparent, evidence-based explanations using Explainable AI (XAI) techniques. The system coordinates a panel of independent, specialized forensic agents that reason over overlapping temporal chunks, calibrating their verdicts dynamically based on recording quality and generating structural proof for human review.

**Core Value:** Move beyond opaque, black-box deepfake classifiers by delivering transparent, multi-agent temporal consensus reasoning, mathematically exact SHAP attributions, and bulletproof forensic narratives.

### Constraints

- **Execution Mode**: Forensic orchestration runs sequentially across chunks; multithreading remains constrained until model thread safety is verified.
- **Resource Constraints**: High-capacity models (WavLM, ConvNext) are lazily loaded via `ModelHub` process singletons to prevent out-of-memory errors on typical CPU environments.
- **Security Constraint**: CORS is configured to wide-open `*` for local web access but must not be committed to cloud production.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- Python - Backend API development, digital audio processing, machine learning model inference, z-score anomaly detection, consensus engine calibration, and persistent ORM mapping. Defined primarily in `backend/app.py`, `backend/api/routes/analysis.py`, `backend/preprocessing/audio_processor.py`, and `backend/consensus/consensus_engine.py`.
- JavaScript/JSX - Interactive React frontend UI, analytical visualization dashboards, history logs, and file uploading. Located in `frontend/src/App.jsx`, `frontend/src/features/analysis/Dashboard.jsx`, and various forensic feature panels under `frontend/src/components/forensic/`.
- CSS - High-fidelity styling tokens, keyframe animations, glassmorphic layout cards, and timeline heatmaps. Declared in `frontend/src/index.css` and `frontend/src/App.css`.
- JSON - Package manifests and dependencies defined in `frontend/package.json`.

## Runtime

- Python 3.9+ (Python 3.12 detected in local environment).
- Node.js v16+ (with npm) for package bundling and dev tooling.
- pip is used for backend package installation via `backend/requirements.txt`.
- npm is used for frontend package installation via `frontend/package.json` and locked with `frontend/package-lock.json`.

## Frameworks

- FastAPI - REST API server, asynchronous request routing, and multipart upload streaming in `backend/app.py` and `backend/api/routes/analysis.py`.
- SQLAlchemy - SQLite ORM database mapping, relational modeling, and transactional session management in `backend/persistence/database.py`.
- PyTorch - Deep learning neural network execution and multi-agent model inference inside `backend/agents/model_hub.py` and `backend/preprocessing/audio_processor.py` (Silero VAD).
- Hugging Face Transformers - Acoustic and semantic feature representations via ConvNext and WavLM handlers.
- Librosa - High-fidelity sample rate conversion, signal duration checking, spectral flatness estimation, and acoustic feature decomposition.
- React 19 - Interactive front-end view engine and feature layout state.
- Vite 8 - Lightning-fast ES module bundling and dev server execution.
- Pytest - Full-coverage testing framework, mocking fixtures, and parallel feature validations in `tests/`.
- Uvicorn - ASGI server execution.
- Vite Scripts - Defined in `frontend/package.json` for compilation, linting, and serving.
- ESLint - Frontend flat configuration and code style checks.

## Key Dependencies

- `fastapi` & `uvicorn` - Main API web shell.
- `sqlalchemy` - Local relational DB layer.
- `torch` & `transformers` - ML neural network engine.
- `librosa` & `pyloudnorm` - Audio preprocessors and EBU R128 loudness meters.
- `scikit-learn` - Machine learning and anomaly detection utilities.
- `captum` & `shap` - Explainable AI engines.
- `silero-vad` - Neural voice activity detection tool.
- `axios` - Frontend REST client.
- `recharts` & `plotly.js` - Dynamic visual graphs and heatmaps.
- `framer-motion` & `lucide-react` - UI animations and interface icons.
- `python-multipart` - FastAPI streaming upload handler.
- `onnxruntime` - CPU-optimized neural runtimes.
- `opencv-python` - Spec-heatmap image transformations and color map conversions.

## Configuration

- Backend configuration is managed dynamically in `backend/config.py` using standard defaults and environment variables:
- Database: Hardcoded local SQLite file `forensic_intelligence.db` in repository root.
- CORS: Allowed for all origins (`*`) in `backend/app.py`.
- API URL: Client base url is hardcoded to `http://localhost:8000` in the frontend source code.

## Platform Requirements

- Local system setup of Python (3.9+) and Node.js (16+).
- Run backend: `python -m backend.app` from root.
- Run frontend: `npm run dev` inside `frontend/` directory.
- Production deployments require explicit CORS settings, secure DB connection strings, and model pre-loading strategies to avoid latency spikes.

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Naming Patterns

- Backend Python files use lowercase `snake_case`, e.g., `backend/api/routes/analysis.py`, `backend/persistence/database.py`.
- Concrete forensic agents end in `_agent.py`, e.g., `backend/agents/convnext_agent.py`, `backend/agents/reliability_agent.py`.
- Frontend JSX files use `PascalCase`, e.g., `frontend/src/features/analysis/Dashboard.jsx`, `frontend/src/components/forensic/TemporalHeatmap.jsx`.
- Both Python backend and Javascript/React use `PascalCase` for classes, e.g., `ForensicOrchestrator`, `ConsensusEngine`, `AudioProcessor`.
- Python methods and functions use `snake_case`, e.g., `process_dual_stream`, `evaluate_chunk_consensus`, `analyze_chunk`.
- React and Javascript functions use `camelCase`, e.g., `handleFileChange`, `fetchHistory`, `renderCharts`.
- Python variables use `snake_case`, e.g., `chunk_consensus`, `voting_agents`, `active_speech`.
- Python constants use uppercase, e.g., `DATABASE_URL`, `PHONETIC_ENGINE`.
- React state variables use `camelCase` with matching setter functions, e.g., `activeTab` / `setActiveTab`, `isAnalyzing` / `setIsAnalyzing`.

## Code Style

- Python follows PEP 8 standards (4-space indentations, explicit imports).
- Frontend React uses custom utility classes declared inside `frontend/src/index.css`.
- ESLint flat configuration is declared inside `frontend/eslint.config.js`, enforcing clean variable scoping (`no-unused-vars` rules).
- Standard linter execution is performed using:

## Import Organization

- Backend relies on absolute package roots, e.g., `from backend.orchestration.agent_registry import agent_registry`.
- Frontend React uses relative import trees, e.g., `import ReliabilityPanel from '../../components/forensic/ReliabilityPanel'`.

## Error Handling

- **Fail-Closed Consensus**: Tie decisions, empty voting lists, or uncalibrated results fallback safely to conclusive `"inconclusive"` outputs instead of throwing errors.
- **Fail-Safe Agent Inferencing**: Individual agent exceptions (such as network model download drops, or empty chunk inputs) are caught locally. They log standard warnings and return inconclusive fallback dictionaries rather than crashing the orchestrator pipeline.
- **API Router Exceptions**: Backend requests catch validation issues and return `HTTPException(status_code=500, detail=str(e))` to let the frontend render clear warnings.

## Logging

- Backend components declare local logging channels:
- Important warning boundaries (such as VAD preservation, clipping anomalies, and modelpreloading) write to `logger.warning` or `logger.info`.

## Function Design

- Keep API controllers thin by routing processing to dedicated services like `AudioProcessor` and `ForensicOrchestrator`.
- Keep agent calculations pure by matching the functional `analyze_chunk(audio_chunk)` interface contract.
- Relational transactions are completed inside the API route using session dependencies (`db: Session = Depends(get_db)`).

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## System Overview

```text

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

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agent/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

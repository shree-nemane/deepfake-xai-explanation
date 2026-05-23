# Technology Stack

**Analysis Date:** 2026-05-23

## Languages

**Primary:**
- Python - Backend API development, digital audio processing, machine learning model inference, z-score anomaly detection, consensus engine calibration, and persistent ORM mapping. Defined primarily in `backend/app.py`, `backend/api/routes/analysis.py`, `backend/preprocessing/audio_processor.py`, and `backend/consensus/consensus_engine.py`.
- JavaScript/JSX - Interactive React frontend UI, analytical visualization dashboards, history logs, and file uploading. Located in `frontend/src/App.jsx`, `frontend/src/features/analysis/Dashboard.jsx`, and various forensic feature panels under `frontend/src/components/forensic/`.

**Secondary:**
- CSS - High-fidelity styling tokens, keyframe animations, glassmorphic layout cards, and timeline heatmaps. Declared in `frontend/src/index.css` and `frontend/src/App.css`.
- JSON - Package manifests and dependencies defined in `frontend/package.json`.

## Runtime

**Environment:**
- Python 3.9+ (Python 3.12 detected in local environment).
- Node.js v16+ (with npm) for package bundling and dev tooling.

**Package Manager:**
- pip is used for backend package installation via `backend/requirements.txt`.
- npm is used for frontend package installation via `frontend/package.json` and locked with `frontend/package-lock.json`.

## Frameworks

**Core:**
- FastAPI - REST API server, asynchronous request routing, and multipart upload streaming in `backend/app.py` and `backend/api/routes/analysis.py`.
- SQLAlchemy - SQLite ORM database mapping, relational modeling, and transactional session management in `backend/persistence/database.py`.
- PyTorch - Deep learning neural network execution and multi-agent model inference inside `backend/agents/model_hub.py` and `backend/preprocessing/audio_processor.py` (Silero VAD).
- Hugging Face Transformers - Acoustic and semantic feature representations via ConvNext and WavLM handlers.
- Librosa - High-fidelity sample rate conversion, signal duration checking, spectral flatness estimation, and acoustic feature decomposition.
- React 19 - Interactive front-end view engine and feature layout state.
- Vite 8 - Lightning-fast ES module bundling and dev server execution.

**Testing:**
- Pytest - Full-coverage testing framework, mocking fixtures, and parallel feature validations in `tests/`.

**Build/Dev:**
- Uvicorn - ASGI server execution.
- Vite Scripts - Defined in `frontend/package.json` for compilation, linting, and serving.
- ESLint - Frontend flat configuration and code style checks.

## Key Dependencies

**Critical:**
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

**Infrastructure:**
- `python-multipart` - FastAPI streaming upload handler.
- `onnxruntime` - CPU-optimized neural runtimes.
- `opencv-python` - Spec-heatmap image transformations and color map conversions.

## Configuration

**Environment:**
- Backend configuration is managed dynamically in `backend/config.py` using standard defaults and environment variables:
  - `PHONETIC_ENGINE` (default: `"wavlm"`)
  - `UPLOAD_DIR` (default: `"uploads"`)
  - `DATABASE_URL` (default: `"sqlite:///forensic_intelligence.db"`)
  - `TARGET_LUFS` (EBU R128 standard loudness default: `-23.0`)
  - `WINDOW_DURATION_SEC` (default: `2.0` seconds)
  - `WINDOW_OVERLAP` (default: `0.5` seconds, 50% overlap)
- Database: Hardcoded local SQLite file `forensic_intelligence.db` in repository root.
- CORS: Allowed for all origins (`*`) in `backend/app.py`.
- API URL: Client base url is hardcoded to `http://localhost:8000` in the frontend source code.

## Platform Requirements

**Development:**
- Local system setup of Python (3.9+) and Node.js (16+).
- Run backend: `python -m backend.app` from root.
- Run frontend: `npm run dev` inside `frontend/` directory.

**Production:**
- Production deployments require explicit CORS settings, secure DB connection strings, and model pre-loading strategies to avoid latency spikes.

---

*Stack analysis: 2026-05-23*

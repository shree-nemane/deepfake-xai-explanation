# External Integrations

**Analysis Date:** 2026-05-23

## APIs & External Services

**Machine Learning Model Sources:**
- Hugging Face Model Hub - Weight checkouts and network queries are performed via `transformers` pipelines inside `backend/models/convnext/convnext_handler.py` and `backend/models/wavlm/wavlm_handler.py`.
- Silero VAD Hub - Voice activity detection model weights are loaded dynamically from the `snakers4/silero-vad` GitHub repository via `torch.hub.load` in `backend/preprocessing/audio_processor.py`.
  - SDK/Client: `torch.hub`
  - Authentication: None required.
- Browser-to-Backend REST Endpoint:
  - React client makes HTTP REST requests to the local FastAPI backend.
  - SDK/Client: `axios` in `frontend/src/App.jsx`, `frontend/src/features/history/History.jsx`, and `frontend/src/features/analysis/Analytics.jsx`.
  - Authentication: None.

## Data Storage

**Databases:**
- SQLite Relational Database:
  - Connection String: `sqlite:///forensic_intelligence.db` configured in `backend/persistence/database.py` and `backend/config.py`.
  - Client: SQLAlchemy ORM.
  - Initializer: `init_db()` is called inside `backend/app.py` during module launch.
  - Target Tables:
    - `reports` - Investigation high-level records, uploaded filename, and full API response payloads.
    - `agents` - Aggregate agent-level prediction verdicts, confidence, and uncertainty.
    - `evidence_segments` - Dynamic timelines containing temporal chunks and their consensus risk scores.
    - `consensus_events` - Agreement/contradiction state changes and temporal convergence incidents.
    - `xai_artifacts` - Explainable AI items (spectrogram Grad-CAM heatmaps serialized in Base64).

**File Storage:**
- Temporary Upload Storage: Local directory `uploads/` is used to persist uploaded files during processing, after which they are deleted inside a `finally` block in `backend/api/routes/analysis.py`.
- Mock Test Fixtures: Local testing datasets are placed in `mock_dataset/audio/` containing `real.wav` and `fake.wav` files.
- Local Anomaly Pickles: Pre-trained Isolation Forest anomaly detection artifact `backend/forensic/anomaly/iso_forest.pkl` is loaded via `pickle` at runtime.

**Caching:**
- Thread-Safe Model Cache: High-performance singleton class `ModelHub` inside `backend/agents/model_hub.py` manages process-wide lazy loading and sharing of models to prevent multiple CPU/GPU memory footprint duplications.

## Authentication & Identity

**Provider:**
- None detected.
  - Implementation: The server is entirely open to local network operations; CORS middleware allows requests from all origins (`*`) in `backend/app.py`.

## Monitoring & Observability

**Logging Framework:**
- Python standard `logging` is configured and used inside forensic agents (e.g. `backend/agents/convnext_agent.py`, `backend/agents/wavlm_agent.py`, `backend/agents/aasist_agent.py`) to report loading states, model devices, and fallback warning events.
- Exceptions: Detailed stack trace prints are logged to standard output (`traceback.print_exc()`) upon catching core processing failures inside `backend/api/routes/analysis.py`.

## CI/CD & Deployment

**CI Configuration:**
- None. No active CI/CD scripts are configured in the repository.

**Hosting Platforms:**
- None. The project operates locally.

## Environment Configuration

**Supported Environment Variables:**
- Loaded and processed inside `backend/config.py`:
  - `PHONETIC_ENGINE`: Selects default phonetic analysis framework (default: `"wavlm"`).
  - `UPLOAD_DIR`: Target path for buffering files (default: `"uploads"`).
  - `DATABASE_URL`: Connection string for SQLAlchemy (default: `"sqlite:///forensic_intelligence.db"`).

## Webhooks & Callbacks

**Incoming Handlers:**
- `POST /analyze/` - Receives multipart form-data audio files for deepfake classification and explanation.
- `GET /analyze/history` - Returns the last 20 reports for frontend rendering.
- `GET /analyze/{report_id}` - Returns rich diagnostic details for a prior analysis.

**Outgoing Callbacks:**
- None detected.

---

*Integration audit: 2026-05-23*

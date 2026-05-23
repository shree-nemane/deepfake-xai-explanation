# Codebase Concerns

**Analysis Date:** 2026-05-23

## Technical Debt

**Import-Time Model & VAD Loading:**
- **Issue**: `AudioProcessor` loads Silero VAD weights from PyTorch Hub inside its constructor. Because it is instantiated as a module global in `backend/api/routes/analysis.py`, importing routes initiates network requests and model weights loading, creating slow/brittle module imports.
- **Impact**: Importing the router inside automated tests or dev commands triggers HTTP network requests and loads PyTorch files, making local testing slow and network-dependent.
- **Mitigation**: Lazily instantiate VAD inside the processing loop, or hook VAD pre-loading to a lifespan startup event in `backend/app.py`.

**Monolithic Request Handler:**
- **Issue**: `analyze_audio` in `backend/api/routes/analysis.py` contains the entire upload validation, dual-stream preprocessing, orchestration routing, SQLAlchemy relational creation, model outputs averaging, Base64 Grad-CAM extraction, and temporary file cleanup in a single 150-line controller method.
- **Impact**: Hard to isolate component testing, prone to transaction leak concerns if DB connections drop mid-processing.
- **Mitigation**: Extract transactional operations and orchestrator calls into separate application services.

## Known Bugs & Issues

**Agent Registry Side-Effect Dependencies:**
- **Symptom**: `agent_registry` may appear completely empty unless agent files are imported first to fire the `@register` decorators.
- **Trigger**: Importing `ForensicOrchestrator` directly and calling `analyze_audio` without importing agent modules.
- **Mitigation**: Pragmatically resolved in `ForensicOrchestrator.__init__` by adding `import backend.agents` as a side-effect trigger, but remains a fragile pattern.

**Sequential Orchestration Bottlenecks:**
- **Symptom**: Large audio files with many 2.0-second chunk segments can stall processing because chunks are routed to agents sequentially.
- **Trigger**: Processing uploads longer than 30 seconds.
- **Mitigation**: Leverage thread pools (`concurrent.futures`) inside the chunk loop to process agents concurrently.

## Security Vulnerabilities

**Wide-Open CORS Policies:**
- **Risk**: `allow_origins=["*"]` configured in `backend/app.py` allows any malicious browser domain to query forensic metrics.
- **Mitigation**: Restrict origins to authorized local domains in production configurations.

**Lack of Upload Authentication:**
- **Risk**: API endpoints `/analyze/` accept uploads from unauthenticated network users.
- **Mitigation**: Enforce bearer token authentication or API keys for analysis endpoints.

**Incomplete Upload Validation:**
- **Risk**: File uploads are only verified by filename suffix `.wav` or `.mp3`. Malicious payloads disguised with audio extensions could exploit backend system tools.
- **Mitigation**: Inspect MIME-types and read raw headers to ensure uploaded files represent correct formats before feeding them to Librosa.

## Scaling Limits

**File-Based Database:**
- **Limit**: Relational persistence uses a local SQLite database file `forensic_intelligence.db`. Concurrent multi-process writes could lock database transactions, making horizontal scaling impossible.
- **Scaling Path**: Migrate `DATABASE_URL` to a production PostgreSQL database when deploying to production.

**Process-Local Model Cache:**
- **Limit**: The `ModelHub` thread-safe singleton resides entirely in the local process memory, which is inefficient if multiple app instances are run.
- **Scaling Path**: Run models as containerized microservices or separate GPU-backed workers (such as Celery/Redis).

---

*Concerns audit: 2026-05-23*

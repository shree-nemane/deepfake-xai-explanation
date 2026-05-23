# Coding Conventions

**Analysis Date:** 2026-05-23

## Naming Patterns

**Files:**
- Backend Python files use lowercase `snake_case`, e.g., `backend/api/routes/analysis.py`, `backend/persistence/database.py`.
- Concrete forensic agents end in `_agent.py`, e.g., `backend/agents/convnext_agent.py`, `backend/agents/reliability_agent.py`.
- Frontend JSX files use `PascalCase`, e.g., `frontend/src/features/analysis/Dashboard.jsx`, `frontend/src/components/forensic/TemporalHeatmap.jsx`.

**Classes:**
- Both Python backend and Javascript/React use `PascalCase` for classes, e.g., `ForensicOrchestrator`, `ConsensusEngine`, `AudioProcessor`.

**Functions:**
- Python methods and functions use `snake_case`, e.g., `process_dual_stream`, `evaluate_chunk_consensus`, `analyze_chunk`.
- React and Javascript functions use `camelCase`, e.g., `handleFileChange`, `fetchHistory`, `renderCharts`.

**Variables:**
- Python variables use `snake_case`, e.g., `chunk_consensus`, `voting_agents`, `active_speech`.
- Python constants use uppercase, e.g., `DATABASE_URL`, `PHONETIC_ENGINE`.
- React state variables use `camelCase` with matching setter functions, e.g., `activeTab` / `setActiveTab`, `isAnalyzing` / `setIsAnalyzing`.

## Code Style

**Formatting:**
- Python follows PEP 8 standards (4-space indentations, explicit imports).
- Frontend React uses custom utility classes declared inside `frontend/src/index.css`.
- ESLint flat configuration is declared inside `frontend/eslint.config.js`, enforcing clean variable scoping (`no-unused-vars` rules).

**Linting:**
- Standard linter execution is performed using:
  ```bash
  cd frontend && npm run lint
  ```

## Import Organization

**Order:**
1. Standard library modules (e.g. `os`, `uuid`, `logging`).
2. Third-party packages (e.g. `fastapi`, `sqlalchemy`, `torch`, `librosa`).
3. Local application modules (e.g. `backend.persistence.database`, `backend.preprocessing.audio_processor`).

**Path Resolution:**
- Backend relies on absolute package roots, e.g., `from backend.orchestration.agent_registry import agent_registry`.
- Frontend React uses relative import trees, e.g., `import ReliabilityPanel from '../../components/forensic/ReliabilityPanel'`.

## Error Handling

**Core Principles:**
- **Fail-Closed Consensus**: Tie decisions, empty voting lists, or uncalibrated results fallback safely to conclusive `"inconclusive"` outputs instead of throwing errors.
- **Fail-Safe Agent Inferencing**: Individual agent exceptions (such as network model download drops, or empty chunk inputs) are caught locally. They log standard warnings and return inconclusive fallback dictionaries rather than crashing the orchestrator pipeline.
- **API Router Exceptions**: Backend requests catch validation issues and return `HTTPException(status_code=500, detail=str(e))` to let the frontend render clear warnings.

## Logging

- Backend components declare local logging channels:
  ```python
  import logging
  logger = logging.getLogger(__name__)
  ```
- Important warning boundaries (such as VAD preservation, clipping anomalies, and modelpreloading) write to `logger.warning` or `logger.info`.

## Function Design

- Keep API controllers thin by routing processing to dedicated services like `AudioProcessor` and `ForensicOrchestrator`.
- Keep agent calculations pure by matching the functional `analyze_chunk(audio_chunk)` interface contract.
- Relational transactions are completed inside the API route using session dependencies (`db: Session = Depends(get_db)`).

---

*Convention analysis: 2026-05-23*

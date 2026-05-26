# Research & Implementation Report — Consensus-Based Explainable Forensic Audio Intelligence Platform

**Document version:** 1.0  
**Generated:** 2026-05-26  
**Primary branch analyzed:** `development`  
**Comparison baseline:** `main`  
**Database sample:** `real_sample_voice.wav` → report `0fada112-21cd-4b0b-9295-e2870b1d300a`  
**Verification status (2026-05-26):** 67 pytest passed, 4 skipped; `npm run build` succeeds on `development` working tree

---

## Document purpose

This file is the **single source document** for writing:

- A **blackbook / final-year implementation report**
- A **research paper** (methods, system design, evaluation framing)
- An **architecture summary** for reviewers
- An **experimental results / case-study** section grounded in a real stored analysis

It is built from **side-by-side inspection** of the `development` codebase, `main` branch history, `DFXAI_project_spec.md`, `docs/API_REFERENCE.md`, `README.md`, SQLite analysis history (`forensic_intelligence.db`), and frontend component structure.

**Note on `project_info.md`:** No file named `project_info.md` exists in this repository. The authoritative product and system-design source is **`DFXAI_project_spec.md`**. Requirement IDs referenced in this document (e.g. XAI-06, UI-02) appear in that specification and in phase completion notes embedded in git history on `development`.

**Note on screenshots:** No committed UI screenshots were found in the repository at generation time. Frontend behavior is described from React component structure and persisted API payloads; visual captures are **not included** unless added manually later.

---

## 1. Executive summary

The platform under analysis is a **forensic audio intelligence system** that detects deepfake speech, voice cloning, partial synthesis, and localized splice evidence using **temporal chunking**, a **panel of five specialized agents**, **reliability-aware suppression**, **explicit contradiction / threat reasoning**, and **deterministic explainability artifacts** (exact Shapley values, analytical sensitivity, evidence graph, structured narrative).

Compared with the earlier **monolithic ConvNext-oriented prototype** (`backend/deepfake_logic.py`, still present as legacy reference but **not** wired into the active API path), the current `development` system provides:

| Dimension | Legacy / early ConvNext-oriented logic | Current `development` system |
|-----------|--------------------------------------|------------------------------|
| Decision unit | Whole-file or single-model score | 2 s overlapping chunks with per-chunk consensus |
| Models / experts | Primarily ConvNext + hand-crafted features | ConvNext, WavLM, AASIST (heuristic), Acoustic (z-score), Reliability |
| Uncertainty handling | Limited | Fail-closed below reliability 0.20; global inconclusive if margin/confidence thresholds fail |
| Contradictions | Not first-class | D-01 voice clone, D-02 splice, D-03 partial synthesis warnings |
| XAI | Grad-CAM / basic heatmap | Exact SHAP (16 coalitions), Level 1 counterfactual gradients, 6-layer evidence graph |
| Narrative | Minimal or template strings | Six-section deterministic narrative engine |
| API | Synchronous `POST /analyze/` | Sync + **async jobs** with SSE progress (`POST /analyze/jobs`) |
| Persistence | Simpler report JSON | Normalized tables + `full_response` JSON snapshot |
| UI | Dashboard panels | Dashboard + explainability drawer + forensic explanation tab + chunk inspector |

A **real uploaded voice** (`real_sample_voice.wav`, ~14.7 s) produced an **`inconclusive`** global verdict with **acoustic → fake** vs **neural agents → real**, which the system correctly treats as analyst-review evidence rather than a forced binary label.

---

## 2. Project overview

### 2.1 Problem domain

Synthetic speech and partial audio manipulation can be **localized in time** and **ambiguous at the file level**. A single scalar “fake probability” is insufficient for forensic or academic review because:

1. Only part of a recording may be manipulated (splice / partial synthesis).
2. Recording quality (noise, clipping, compression) can mimic or mask artifacts.
3. Different detectors emphasize different failure modes (spectral vs phonetic vs biological).
4. Reviewers require **auditable evidence** linking verdicts to time ranges and expert disagreements.

### 2.2 System goal

Deliver **investigator-grade outputs**:

- Global verdict: `fake` | `real` | `inconclusive`
- Temporal timeline of chunk-level events and threats
- Per-agent calibrated evidence
- Explainability artifacts suitable for UI and database audit
- Human-readable narrative without relying on a free-form LLM in v1

### 2.3 Core design principles (from project spec)

1. **Evidence first** — every claim traceable to agent outputs.  
2. **Temporal precision** — suspicious regions localized by timestamp.  
3. **Reliability-aware reasoning** — poor SNR/clipping reduces trust in neural experts.  
4. **Explainability by design** — SHAP, sensitivity, graph, narrative are first-class.  
5. **Fail closed** — degraded evidence yields `inconclusive`, not overconfident fake/real.  
6. **Modular implementation** — agents register via plugin pattern; tests per subsystem.

---

## 3. Original problem and motivation

### 3.1 What the early ConvNext-oriented approach could not do

The legacy module `backend/deepfake_logic.py` (present on both branches, **not imported** by `backend/api/routes/analysis.py`) implements:

- Librosa load @ 16 kHz, peak normalization
- Hand-crafted feature thresholds (ZCR, spectral centroid, MFCC variance, pitch variation)
- Mel-spectrogram → **ConvNext** image classifier
- Reference-vector distance heuristics for “fake-like” vs “real-like” feature profiles

**Insufficiencies for forensic use:**

| Limitation | Impact |
|------------|--------|
| File-level framing | Cannot localize partial edits or short spoofed inserts |
| Single dominant neural pathway | Phonetic cloning with plausible spectra may evade ConvNext-only reasoning |
| No reliability gating | Noisy/clipped audio can produce false synthetic calls |
| No structured disagreement model | Agent conflicts not surfaced as threats |
| No exact attribution | No Shapley coalition accounting across experts |
| No persistent contradiction events | Hard to defend decisions in viva / paper review |
| Monolithic code path | Hard to extend with WavLM, acoustic biology, anti-spoof heuristics |

### 3.2 Research gap addressed by current system

The current platform reframes detection as **multi-expert temporal consensus under quality suppression**, with **explicit threat typology** and **deterministic XAI**, aligning with forensic audio intelligence literature themes: ensemble disagreement, calibration, temporal localization, and explainable ML — without claiming courtroom certification in v1.

---

## 4. Evolution: `main` branch → `development` branch

### 4.1 What `main` already contained (inspection summary)

`main` is **not** ConvNext-only at the orchestration layer. It already includes:

- `ForensicOrchestrator`, `TimelineManager`, five agents (ConvNext, WavLM, AASIST, Acoustic, Reliability)
- `ConsensusEngine` with suppression and threat heuristics
- SQLAlchemy schema v2 (`reports`, `agents`, `evidence_segments`, `consensus_events`, `xai_artifacts`, `narrative_reports`, …)
- Synchronous `POST /analyze/` pipeline in `backend/api/routes/analysis.py`
- Basic narrative rows and Grad-CAM heatmap in response

**Not found on `main` (added on `development`):**

- Async analysis jobs + SSE progress (`/analyze/jobs`, `/jobs/{id}/events`, `/jobs/{id}/result`)
- Full **exact SHAP engine** (`backend/explainability/shap/shap_engine.py`) with 16-coalition math
- **Level 1 counterfactual engine** (`backend/explainability/counterfactuals/counterfactual_engine.py`)
- **Evidence graph v1** builder (`backend/explainability/evidence_graph.py`, schema `evidence_graph_v1`)
- **NarrativeEngine** with six sections and inconclusive rationale (`backend/explainability/narrative_engine.py`)
- Phase 5 UI: explainability drawer, forensic explanation tab, Plotly graph
- Chunk evidence explorer, mel spectrogram previews, timeline compression
- UAT calibration (acoustic threshold, quality vs synthesis diagnostic split)
- `docs/API_REFERENCE.md`, expanded `README.md`, `scripts/run-dev.ps1`, `scripts/extract_report_sample.py`
- Structured pytest suites under `tests/xai/`, `tests/forensic/`, etc.

### 4.2 Quantitative diff (git)

Approximately **75 files** differ between `main` and `development` (~7,100 insertions / ~400 deletions in prior diff stat), dominated by explainability, frontend, tests, and documentation.

### 4.3 Implementation phases (v1 deliverables)

| Phase | Theme | Key deliverables |
|-------|--------|------------------|
| 1 | DB & suppression | Legacy DB removal, fail-closed suppression, schema expansion |
| 2 | Consensus warnings | Voice clone / splice / partial synthesis threats, temporal alignment tests |
| 3 | XAI core | Exact SHAP, analytical counterfactuals, narrative engine |
| 4 | Graph & progress | 6-layer evidence graph, backend-driven upload progress (jobs/SSE) |
| 5 | UI console | Explainability drawer, explanation tab, SHAP/Plotly/sensitivity |
| Post-UAT | Calibration & UX | Timeline compression, inconclusive narrative, acoustic tuning, mel previews, diagnostic object format |

---

## 5. System architecture

### 5.1 Layered architecture (paper-ready)

```text
┌─────────────────────────────────────────────────────────────────┐
│  Presentation: React 19 + Vite (Dashboard, Drawer, History)    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP / SSE
┌────────────────────────────▼────────────────────────────────────┐
│  API: FastAPI (`backend/app.py`, `api/routes/analysis.py`)       │
│  • Sync analyze  • Async jobs  • History  • Report reload        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  Preprocessing: AudioProcessor (LUFS, VAD, dual-stream resample) │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  Segmentation: TimelineManager (2.0 s window, 50% overlap, align)  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  Orchestration: ForensicOrchestrator + agent_registry (5 agents)   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  Consensus: CalibrationEngine + ConsensusEngine                    │
│  • Per-chunk verdict  • Threat warnings  • Global aggregation      │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  Explainability: SHAP, Counterfactuals, EvidenceGraph, Narrative   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  Persistence: SQLite (`forensic_intelligence.db`)                │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Entry points

| Entry | Path | Role |
|-------|------|------|
| API server | `python -m backend.app` | Uvicorn on port 8000 |
| Sync analysis | `POST /analyze/` | Blocking full pipeline |
| Async analysis | `POST /analyze/jobs` | Background task + progress |
| UI | `frontend` → `npm run dev` | Port 5173 |
| Tests | `python -m pytest tests` | Regression |
| Report extract | `python scripts/extract_report_sample.py` | Redacted JSON for docs |

### 5.3 Technology stack

| Layer | Technologies |
|-------|----------------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, SQLite, PyTorch, Librosa, pyloudnorm, OpenCV |
| ML models | ConvNext (spectrogram), WavLM (embeddings), Silero VAD |
| Frontend | React 19, Vite, Recharts, Plotly (lazy), Framer Motion, Axios |
| Tests | pytest |

---

## 6. Preprocessing pipeline

**Implementation:** `backend/preprocessing/audio_processor.py`

### 6.1 Stages

1. **Load & validate** — minimum 1 s duration; reject silence; warn on severe clipping (>5% samples near full scale); block unsupported codecs (e.g. `.m4a`, `.wma`, `.amr`).
2. **LUFS normalization** — EBU R128 target **−23 LUFS** via `pyloudnorm`; metadata records original loudness and gain.
3. **VAD (Silero)** — active speech extraction with `min_speech_duration_ms=100`, `speech_pad_ms=250` to preserve weak phonation.
4. **Dual-stream resampling**
   - **16 kHz** semantic stream → WavLM, Reliability (shared path)
   - **48 kHz** forensic stream → ConvNext, Acoustic, AASIST

### 6.2 Metadata exposed to API (`preprocessing` block)

Example from real sample (report `0fada112…`):

| Field | Value (real_sample_voice.wav) |
|-------|-------------------------------|
| `original_duration_sec` | 14.722 |
| `active_duration_sec` | 14.388 |
| `speech_coverage` | 0.9773 |
| `vad_segments` | 6 |
| `chunk_count` | 13 |
| `chunk_window_sec` | 2.0 |
| `chunk_overlap` | 0.5 |
| `lufs.original` | −19.46 dB |
| `lufs.target` | −23.0 |

---

## 7. Segmentation and temporal alignment

**Implementation:** `backend/orchestration/timeline_manager.py`

### 7.1 Parameters (locked in v1)

| Parameter | Value |
|-----------|--------|
| Window duration | 2.0 s |
| Overlap | 50% (1.0 s hop) |
| Alignment tolerance | 1 ms (`ALIGNMENT_TOLERANCE = 1e-3`) |

### 7.2 Dual-stream alignment (D-06–D-08)

- Pads shorter stream to match longer duration while preserving timestamps.
- Each chunk carries `mask` and `is_padded` flags.
- `create_aligned_chunks` verifies pairwise start/end times across 16 kHz and 48 kHz lists.

### 7.3 Timeline compression (post-UAT)

**Implementation:** `backend/forensic/timeline_compression.py`

Merges adjacent timeline segments with identical `event_type`, `verdict`, and threat signature for analyst UI. API returns both raw chunk count and display segment count (`timeline_raw_count`, `timeline_display_count`).

---

## 8. Forensic agent panel

**Registration:** `backend/agents/__init__.py` imports modules → `agent_registry`  
**Orchestration:** `backend/orchestration/forensic_orchestrator.py`

### 8.1 Execution order per chunk

1. **Reliability agent** first → `reliability_score`, SNR, clipping, flatness, RMS.
2. If `reliability_score < 0.20` → **fail-closed**: heavy neural agents (ConvNext, WavLM) return `inconclusive` skip payloads; saves compute and prevents false neural calls on unusable audio.
3. Other agents run on rate-matched chunk (`16k` or `48k`).
4. **ConsensusEngine.evaluate_chunk_consensus** consumes raw + calibrated results.

### 8.2 Agent reference table

| Agent | Sample rate | Method | Verdict basis |
|-------|-------------|--------|----------------|
| **Reliability** | 16 kHz | HPSS SNR, clipping ratio, spectral flatness, RMS | Quality score (not fake/real vote) |
| **ConvNext** | 48 kHz | Mel-spectrogram → ConvNext classifier; optional Grad-CAM | Classifier logits → fake/real |
| **WavLM** | 16 kHz | Embeddings + temporal entropy | Phonetic instability |
| **AASIST** | 48 kHz | Deterministic heuristics (phase, sub-band energy, ZCR, periodicity) | Weighted spoof score (not full neural AASIST in v1) |
| **Acoustic** | 48 kHz | Librosa features vs natural-speech baselines; z-score risk | Overall anomaly vs threshold (**0.52** post-UAT, was 0.4) |

**Model loading:** `backend/agents/model_hub.py` — lazy singleton with thread locks for ConvNext/WavLM.

### 8.3 Real-sample agent summary (`real_sample_voice.wav`)

| Agent | Global verdict (majority over 13 chunks) | Avg confidence |
|-------|------------------------------------------|----------------|
| acoustic | **fake** | 0.99 |
| aasist | real | 0.72 |
| convnext | real | 0.98 |
| wavlm | real | 0.74 |
| reliability | inconclusive (aggregate label) | 1.0 |

This split is the canonical UAT case for **inconclusive global verdict** with **partial_synthesis** threat narrative.

---

## 9. Consensus, calibration, and suppression

**Implementation:** `backend/consensus/consensus_engine.py`, `backend/consensus/calibration_engine.py`

### 9.1 Per-chunk processing

1. Calibrate agent confidences using reliability metrics.
2. Apply **agent-specific suppression** (e.g. ConvNext vulnerable to compression/speech quality; WavLM to noise; Acoustic to clipping/phase).
3. Compute fake/real support vectors and chunk verdict.
4. Evaluate **threat warnings** from raw (pre-calibration) agent verdicts/confidences.
5. Assign `ConsensusEventType`: `agreement`, `contradiction`, `splice`, `quality_failure`, `reliability_warning`.

### 9.2 Global aggregation

**Implementation:** `ForensicOrchestrator._calculate_global_consensus`

| Rule | Threshold |
|------|-----------|
| Minimum global confidence | 0.60 (`_MIN_GLOBAL_DECISION_CONFIDENCE`) |
| Minimum fake/real probability margin | 0.08 (`_MIN_GLOBAL_PROBABILITY_MARGIN`) |
| If margin or confidence fails | **`inconclusive`** |

Real sample global consensus:

```json
{
  "verdict": "inconclusive",
  "confidence": 0.599,
  "convergence_strength": 0.75,
  "fake_probability": 0.401,
  "real_probability": 0.599,
  "probability_margin": 0.198,
  "decision_threshold": 0.6
}
```

Margin 0.198 < 0.20 would not alone trigger inconclusive, but **confidence 0.599 < 0.60** triggers fail-closed holdback (per code). *Document both metrics for paper discussion.*

### 9.3 Reliability suppression tiers (SUP-02)

| Reliability | Effect |
|-------------|--------|
| ≥ 0.80 | Full contribution |
| 0.60–0.80 | Mild damping |
| 0.40–0.60 | Moderate uncertainty increase |
| 0.20–0.40 | Heavy reduction |
| < 0.20 | Fail-closed (neural skip) |

Sigmoid mapping implemented in `_get_sigmoid_suppression`.

---

## 10. Contradiction and threat handling

**Implementation:** `ConsensusEngine._evaluate_threat_warnings`

### 10.1 Threat typology (v1)

| ID | Name | Trigger (simplified) |
|----|------|----------------------|
| D-01 | Voice clone | WavLM fake ≥ 0.70 AND (Acoustic real ≥ 0.70 OR ConvNext real ≥ 0.70) |
| D-02 | Localized splice | ConvNext fake ≥ 0.70 AND Acoustic real ≥ 0.70 (pair-dependent) |
| D-03 | Partial synthesis | Multi-agent split when D-01/D-02 did not fully explain |

### 10.2 Real-sample threat

All 13 chunks recorded `event_type: contradiction` with elevated **partial_synthesis** warning:

> *Partial Synthesis Threat: Multi-agent consensus split. Experts disagree on localized temporal properties; inspect temporal features.*

Persisted to:

- `consensus_events` table (per chunk)
- `timeline[].threat_warnings` in API payload
- Narrative **Contradictions** section
- Evidence graph threat nodes (layer 4–5)

---

## 11. Explainability (XAI) pipeline

### 11.1 Exact Shapley values (XAI-06)

**Implementation:** `backend/explainability/shap/shap_engine.py`

- Voting set: `{wavlm, convnext, aasist, acoustic}` — **4 agents → 2⁴ = 16 coalitions**
- Coalition value: weighted fake support / (fake + real support) from calibrated verdicts
- Properties tested: efficiency, symmetry, dummy agent (see `tests/xai/test_shap_engine.py`)
- Output per chunk in `xai.shap_values.chunks[]` plus `shap_summary`

### 11.2 Level 1 analytical counterfactuals (XAI-07)

**Implementation:** `backend/explainability/counterfactuals/counterfactual_engine.py`

- Computes numerical gradient of local fake probability w.r.t. each agent’s calibrated confidence
- Direction labels: `increases_fake_probability` / `decreases_fake_probability`
- Exposed in drawer **Analytical Sensitivity** panel with per-chunk selector

### 11.3 Evidence graph (XAI-08)

**Implementation:** `backend/explainability/evidence_graph.py`

Six layers:

1. Audio Input  
2. Preprocessing / Reliability  
3. Forensic Agents  
4. Consensus Arbitration  
5. XAI Artifacts  
6. Verdict & Narrative  

Export schema: `evidence_graph_v1` with `nodes`, `edges`, `layer_counts`. Visualized in Overview (static summary) and Explainability drawer (Plotly scatter, lazy-loaded).

### 11.4 Grad-CAM heatmap

- Best ConvNext chunk heatmap encoded as **JPEG base64** in `heatmap_base64`
- Shown in **Interactive Spectral Heatmap** with temporal bands synced to timeline selection

### 11.5 Mel spectrogram previews (post-UAT)

**Implementation:** `mel_spectrogram_preview_base64()` in `backend/forensic/features/acoustic_features.py`

- Generated per **display timeline segment** from 48 kHz audio slice
- Stored in DB under top-level `mel_previews` map (keys `start:end`) to avoid bloating each timeline row
- `GET /analyze/{id}` re-injects into timeline for history reload

### 11.6 Narrative generation (XAI-09)

**Implementation:** `backend/explainability/narrative_engine.py`

**Sections (required):** Finding, Evidence, Reliability, Confidence, Contradictions, Explainability

**Post-UAT inconclusive rationale** adds explicit lines for:

- Acoustic vs neural split  
- Quality vs synthesis diagnostic categories  
- Fail-closed threshold language  

**Not an LLM** — template and rule driven (`deterministic_v1`).

---

## 12. Database schema

**File:** `backend/persistence/database.py`  
**Database file:** `forensic_intelligence.db` (SQLite, project root)

### 12.1 Entity-relationship summary

```text
Report 1──* AgentOutput
      1──* EvidenceSegment
      1──* ConsensusEvent 1──* EventAgentDetails
      1──* XAIArtifact
      1──1 NarrativeReport
      1──1 ProcessingMetadata
      JSON full_response (complete API snapshot)
```

### 12.2 Table purposes

| Table | Purpose |
|-------|---------|
| `reports` | Session metadata + `full_response` JSON |
| `agents` | Per-file agent aggregates (verdict, confidence, uncertainty) |
| `evidence_segments` | Temporal risk segments (`start_time`, `end_time`, `risk_score`) |
| `consensus_events` | Chunk events with `event_type`, snapshots, diagnostics |
| `event_agent_details` | Per-agent row per consensus event |
| `xai_artifacts` | SHAP JSON, counterfactuals, evidence_graph, heatmap string |
| `narrative_reports` | Structured + human summaries |
| `processing_metadata` | Chunk duration, overlap, sample rates, pipeline version |

### 12.3 `full_response` JSON

Canonical API-shaped blob for fast history reload. On save, **mel previews** may be stored in sibling `mel_previews` dict (not embedded in each timeline row) for size efficiency.

---

## 13. API flow

**Router:** `backend/api/routes/analysis.py`  
**Schema:** `backend/api/schemas/analysis.py`

### 13.1 Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health |
| POST | `/analyze/` | Synchronous full pipeline |
| POST | `/analyze/jobs` | Create async job |
| GET | `/analyze/jobs/{id}/progress` | Poll progress |
| GET | `/analyze/jobs/{id}/events` | SSE stage stream |
| GET | `/analyze/jobs/{id}/result` | Final JSON (when complete) |
| GET | `/analyze/history` | List reports (id, filename, risk, date) |
| GET | `/analyze/{report_id}` | Reload `full_response` (+ mel rehydration) |

### 13.2 Progress stages (jobs)

Defined in `ANALYSIS_STAGES`:

1. upload_received  
2. preprocessing  
3. segmentation  
4. agent_panel  
5. consensus  
6. xai_evidence_graph  
7. narrative_persistence  
8. complete  

### 13.3 CORS (`development`)

Explicit origins: `http://localhost:5173`, `127.0.0.1:5173` (and 5174). **Not** wildcard + credentials (browser-safe).

---

## 14. Frontend flow

**Shell:** `frontend/src/App.jsx`  
**Dashboard:** `frontend/src/features/analysis/Dashboard.jsx`

### 14.1 User journeys

1. **Investigate** → upload WAV/MP3 → async job → SSE/poll progress → auto-navigate to Dashboard  
2. **Dashboard Overview** → verdict banner, consensus, evidence graph summary, feature analysis, agents grid, chunk inspector, heatmap, report export  
3. **Open Explainability** → portal drawer: SHAP, sensitivity, Plotly graph (deferred load + error boundary)  
4. **Forensic Explanation tab** → narrative sections, contradiction alerts, evidence tables  
5. **History** → `GET /analyze/history` → `GET /analyze/{id}` → Dashboard  

### 14.2 Key UI components

| Component | Role |
|-----------|------|
| `ChunkEvidenceExplorer` | Timeline legend, segment selection, suspicion card, mel panel, agent table, heatmap |
| `TimelinePanel` | Hover tooltips; click-to-select segment |
| `TemporalHeatmap` | Grad-CAM with band selection; callout above image (no clipped tooltips) |
| `ReportSummaryExport` | Copy/download text summary |
| `ExplainabilityDrawer` | Portal + deferred Plotly |
| `FeatureAnalysisPanel` | Intake, quality, neural signals, acoustic ranking, **string-safe warnings** |

### 14.3 Client-side normalization

`frontend/src/utils/normalizeReport.js` — ensures diagnostic warnings are render-safe; merges `mel_previews` on load.

`frontend/src/components/layout/ErrorBoundary.jsx` — prevents full-app blank screen on render errors.

### 14.4 Known UI defect fixed (2026-05-26)

Rendering `{category, message}` warning objects directly in React caused **fatal render crash** (observed as full-screen slate/blue). Fixed in `FeatureAnalysisPanel` via `collectDiagnosticWarnings()`.

---

## 15. Output for one uploaded file (case study)

**File:** `real_sample_voice.wav`  
**Report ID:** `0fada112-21cd-4b0b-9295-e2870b1d300a`  
**Created:** 2026-05-26 (SQLite `reports.created_at`)

### 15.1 Pipeline counts

| Metric | Value |
|--------|--------|
| Original duration | 14.72 s |
| Chunks analyzed | 13 |
| Timeline display segments (compressed) | 1 (merged 13 chunks) |
| Global verdict | **inconclusive** |
| Review level | moderate_trust |
| Decision reliability | 0.732 |

### 15.2 Top-level API payload keys

`id`, `filename`, `consensus`, `agents`, `timeline`, `timeline_raw_count`, `timeline_display_count`, `preprocessing`, `feature_analysis`, `diagnostics`, `xai`, `narrative`, `heatmap_base64`, `mel_previews`, `processing_metadata`, `created_at`

### 15.3 What the investigator sees (Overview)

1. **Banner:** “Analysis Inconclusive” with confidence ~60%, convergence 75%  
2. **Consensus panel** with fake/real probabilities  
3. **Evidence graph** summary (node/edge counts, layer list)  
4. **Feature analysis** — SNR, clipping, ranked acoustic z-scores, neural signal meters  
5. **Agent cards** — acoustic fake vs others real  
6. **Chunk inspector** — single merged 0–14 s contradiction segment; partial synthesis explanation; mel PNG if previews present  
7. **Heatmap** — ConvNext Grad-CAM with selectable band  
8. **Report export** — plaintext summary for blackbook appendix  

### 15.4 Narrative (human summary, stored)

> Finding: The calibrated consensus layer returned an inconclusive forensic result. Confidence is 59.9% with reliability 100.0%. Threat warnings require timeline review.

Structured summary additionally contains six markdown sections with inconclusive rationale lines (acoustic vs neural split) when generated on latest `development` build.

### 15.5 Diagnostics warnings (structured)

```json
{
  "quality_warnings": [],
  "synthesis_warnings": [
    {
      "category": "synthesis_evidence",
      "message": "Agents disagree on at least one chunk; inspect the temporal timeline before relying on the verdict."
    },
    {
      "category": "synthesis_evidence",
      "message": "Consensus confidence is low; treat this as analyst-support evidence, not a final conclusion."
    }
  ]
}
```

### 15.6 Redacted full sample

A redacted JSON export (no raw base64 blobs) is available at:

- **`docs/sample_report_redacted.json`**  
- Regenerate: `python scripts/extract_report_sample.py --report-id 0fada112-21cd-4b0b-9295-e2870b1d300a`

---

## 16. Example report structure (schema template)

```json
{
  "id": "<uuid>",
  "filename": "<original_name.wav>",
  "consensus": {
    "verdict": "fake|real|inconclusive",
    "confidence": 0.0,
    "uncertainty": 0.0,
    "convergence_strength": 0.0,
    "fake_probability": 0.0,
    "real_probability": 0.0,
    "probability_margin": 0.0,
    "decision_threshold": 0.6
  },
  "agents": {
    "<agent_name>": {
      "verdict": "...",
      "confidence": 0.0,
      "uncertainty": 0.0,
      "evidence": { }
    }
  },
  "timeline": [
    {
      "start_time": 0.0,
      "end_time": 2.0,
      "event_type": "contradiction|agreement|splice|...",
      "verdict": "fake|real|inconclusive",
      "confidence": 0.0,
      "convergence_strength": 0.0,
      "details": { "<agent>": { "verdict", "calibrated_confidence", "suppression_factor", ... } },
      "threat_warnings": [ { "type", "description", "severity" } ],
      "segment_count": 1
    }
  ],
  "mel_previews": { "0.0:14.0": "<png base64>" },
  "preprocessing": { },
  "feature_analysis": { },
  "diagnostics": { },
  "xai": {
    "shap_values": { "chunks": [ ] },
    "counterfactuals": { },
    "evidence_graph": { },
    "shap_summary": "...",
    "counterfactual_summary": "..."
  },
  "narrative": {
    "structured_summary": "## Finding\n...",
    "human_summary": "...",
    "metadata": { }
  },
  "heatmap_base64": "<jpeg>",
  "processing_metadata": { }
}
```

---

## 17. Evaluation and verification

### 17.1 Automated tests (2026-05-26)

| Suite | Focus |
|-------|--------|
| `tests/consensus/` | Suppression, contradictions, persistence |
| `tests/xai/` | SHAP math, counterfactuals, narrative, evidence graph |
| `tests/integration/` | Schema validation, report payload, mel strip/apply |
| `tests/forensic/` | Timeline compression |
| **Total** | **67 passed**, 4 skipped (performance/benchmark placeholders) |

### 17.2 Manual / UAT observations (2026-05-25 — 2026-05-26)

- Fail-closed **inconclusive** under agent split: **correct by design**
- Acoustic fake vs neural real: calibration target, not architecture failure
- UI stability fixes: drawer portal, diagnostic string rendering, Plotly containment

### 17.3 Suggested paper evaluation framing

| Evaluation type | What exists today | Gap |
|-----------------|-------------------|-----|
| Unit correctness | SHAP axioms, threat thresholds, alignment | — |
| Case study | Real + fake samples in DB | Needs curated table of N files |
| Accuracy vs benchmark | Not in repo | Requires labeled dataset + batch runner |
| Latency study | Not in repo | Could log stage timings from jobs |
| User study | Not in repo | Forensic explanation tab supports future UX study |

*Do not claim superhuman detection accuracy without benchmark scripts — not present in codebase.*

---

## 18. Limitations and future work

### 18.1 v1 limitations (from spec + code)

| Limitation | Detail |
|------------|--------|
| Sequential processing | Chunks and agents run in single thread |
| In-memory jobs | Progress lost on server restart |
| AASIST | Heuristic, not full pretrained AASIST network |
| No Level-2 counterfactuals | No audio perturbation simulation |
| No LLM narrative | Rule-based only |
| SQLite only | No production RDBMS / object store |
| Model hub CPU focus | GPU optional, not required in docs |
| Large Plotly bundle | First drawer open costly |

### 18.2 Documented future work (v2 themes)

- Neural AASIST deployment  
- Level 2 perturbation counterfactuals  
- LLM-assisted narrative rewrite (optional)  
- Parallel chunk execution  
- Durable job queue  
- Production CORS and auth  

---

## 19. Blackbook / viva implementation notes

### 19.1 What to demonstrate live

1. Health check `GET /`  
2. Upload short WAV → show **8 progress stages**  
3. Point to **inconclusive** when acoustic disagrees with WavLM/ConvNext  
4. Open **chunk inspector** → mel spectrogram + agent table  
5. Open **Explainability drawer** → SHAP bars + sensitivity  
6. Switch to **Forensic Explanation** → six narrative sections + threats  
7. **History** → reload same report from SQLite  
8. Run `python -m pytest tests/xai tests/consensus -q`  

### 19.2 Design decisions worth defending

| Decision | Defense |
|----------|-----------|
| Inconclusive as first-class | Forensic ethics; avoids false conviction on split experts |
| Exact SHAP vs Monte Carlo | Reproducible, auditable for N=4 agents |
| Reliability before neural | Prevents expensive inference on unusable audio |
| Deterministic narrative | Same input → same explanation (examiner can replay) |
| Dual sample rates | Matches model training domains (16 kHz speech vs 48 kHz spectral) |

### 19.3 Files examiners may ask about

| Topic | File |
|-------|------|
| “Where is the main pipeline?” | `backend/api/routes/analysis.py` → `_run_analysis_from_path` |
| “Where is consensus?” | `backend/consensus/consensus_engine.py` |
| “Where is SHAP?” | `backend/explainability/shap/shap_engine.py` |
| “Database?” | `backend/persistence/database.py` |
| “UI entry?” | `frontend/src/App.jsx` |

---

## 20. Paper-ready terminology

| Term | Definition in this system |
|------|---------------------------|
| **Forensic agent** | Independent expert module producing `{verdict, confidence, uncertainty, evidence}` per chunk |
| **Temporal chunk** | 2 s window, 50% overlap, aligned across 16/48 kHz streams |
| **Calibrated confidence** | Agent score after reliability-based adjustment |
| **Suppression factor** | ∈ [0,1] multiplier from signal quality metrics |
| **Fail-closed** | Policy preferring `inconclusive` over weak binary decision |
| **Threat warning** | Structured contradiction typology (voice clone, splice, partial synthesis) |
| **Coalition value** | v(S) = fake support share for subset S of agents |
| **Shapley value** | Average marginal contribution across permutations (exact here) |
| **Level 1 sensitivity** | Gradient of local fake probability w.r.t. agent confidence |
| **Evidence graph** | Directed acyclic description of pipeline layers L1–L6 |
| **Deterministic narrative** | Rule-generated textual forensic report |

---

## 21. Version status and release snapshot (2026-05-26)

| Item | Status |
|------|--------|
| v1 implementation phases 1–5 | Complete (DB/suppression, consensus warnings, XAI core, evidence graph + progress UI, explainability console) |
| Core capability areas | Dual-stream preprocessing, five agents, fail-closed consensus, exact SHAP, Level 1 sensitivity, 6-layer evidence graph, deterministic narrative, React investigation UI |
| Post-UAT improvements | Timeline compression, inconclusive narrative detail, acoustic threshold calibration (0.52), quality vs synthesis diagnostic categories, mel segment previews, dashboard stability fixes |
| Automated verification | 67 pytest passed, 4 skipped; frontend production build OK |
| Repository branches | `development` (full tree); `main` (application + public docs only) |
| Research deliverable | This document + `scripts/extract_report_sample.py` for case-study JSON export |

### 21.1 v1 requirement themes (for traceability in reports)

| ID prefix | Theme |
|-----------|--------|
| PRE / SEG | LUFS normalization, VAD, dual-stream resampling, 2 s / 50% overlap chunking |
| AGT | ConvNext, WavLM, AASIST (heuristic), Acoustic, Reliability agents |
| CON / SUP | Consensus engine, reliability suppression, fail-closed below 0.20 |
| XAI | Exact Shapley (XAI-06), analytical sensitivity (XAI-07), evidence graph (XAI-08), narrative (XAI-09), threat warnings (XAI-10) |
| UI | Progress stages (UI-04), explainability drawer (UI-02), forensic explanation tab (UI-03) |
| DB | Consolidated SQLite schema (DB-02, DB-03) |
| TST | Unit, integration, consensus, and XAI test suites |

---

## 22. Appendix A — Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run-dev.ps1` | Start backend + frontend (Windows) |
| `scripts/verify.py` | API smoke test with sample WAVs |
| `scripts/extract_report_sample.py` | Export redacted `full_response` from SQLite |

---

## 22. Appendix B — Primary references in repo

| Document | Path |
|----------|------|
| Master PRD / system design | `DFXAI_project_spec.md` |
| API reference | `docs/API_REFERENCE.md` |
| Setup, testing, troubleshooting | `README.md` |
| This report (paper / blackbook source) | `RESEARCH_AND_REPORT_DOC.md` |
| Sample report (redacted; generate locally) | Run `python scripts/extract_report_sample.py` → `docs/sample_report_redacted.json` (gitignored) |

---

## 23. Appendix C — Honest gaps (not invented)

| Item | Status |
|------|--------|
| `project_info.md` | **Not found** in repository |
| UI screenshots | **Not in repo** at generation time |
| Benchmark accuracy table | **Not implemented** |
| Real-time streaming inference | **Out of scope** (spec) |
| Speaker diarization | **Out of scope** (spec) |

---

*End of document. For updates after new commits, regenerate Section 15 via `scripts/extract_report_sample.py` and re-run pytest.*

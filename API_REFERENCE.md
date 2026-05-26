# API Reference

Base URL (local default): `http://localhost:8000`

Interactive OpenAPI docs: `http://localhost:8000/docs`

All analysis routes are mounted under `/analyze` unless noted.

---

## Health

### `GET /`

Returns API liveness.

**Response 200**

```json
{
  "status": "online",
  "message": "Deepfake Forensic AI API is operational."
}
```

---

## Synchronous analysis

### `POST /analyze/`

Upload and analyze audio in a single blocking request. Suitable for tests and simple clients.

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | yes | Audio file (`.wav` or `.mp3`) |

**Success:** `200` — `AnalysisResponse` (see schema below)

**Errors**

| Status | Condition |
|--------|-----------|
| `400` | Invalid file extension |
| `503` | Analysis unavailable (model/runtime failure) |
| `500` | Unexpected pipeline error |

**Notes**

- Uploaded temp file is deleted after the request completes.
- Full report is persisted to SQLite (`forensic_intelligence.db`).

---

## Async job analysis (recommended for UI)

The React dashboard uses the job flow for real-time progress.

### `POST /analyze/jobs`

Start background analysis and receive a job snapshot immediately.

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | yes | Audio file (`.wav` or `.mp3`) |

**Response 200 — Job snapshot**

```json
{
  "job_id": "uuid",
  "filename": "sample.wav",
  "stage": "upload_received",
  "status": "queued",
  "percent": 5,
  "message": "Upload received.",
  "error": null,
  "created_at": "2026-05-24T10:00:00+00:00",
  "updated_at": "2026-05-24T10:00:00+00:00",
  "sequence": 0,
  "stages": [
    {
      "id": "upload_received",
      "label": "Upload received",
      "percent": 5,
      "status": "complete"
    }
  ]
}
```

### `GET /analyze/jobs/{job_id}/progress`

Poll current job state. Same shape as job creation response (without `result`).

**Errors:** `404` if job not found.

### `GET /analyze/jobs/{job_id}/events`

Server-Sent Events stream of progress snapshots.

- Emits when `sequence` changes.
- Terminal events: `status` = `complete` or `error`.
- Frontend should fall back to polling if `EventSource` fails.

**Errors:** `404` if job not found.

### `GET /analyze/jobs/{job_id}/result`

Fetch final analysis when job is complete.

**Success:** `200` — `AnalysisResponse`

**Errors**

| Status | Condition |
|--------|-----------|
| `404` | Job not found |
| `202` | Job still running |
| `500` | Job failed (`error` field set on progress snapshot) |

---

## Reports & history

### `GET /analyze/history`

Returns the 20 most recent reports with summary fields.

**Response 200 — array**

```json
[
  {
    "id": "uuid",
    "filename": "sample.wav",
    "created_at": "2026-05-24T10:00:00",
    "prediction": "fake",
    "confidence": 0.87,
    "risk_score": 87.0
  }
]
```

### `GET /analyze/{report_id}`

Load a persisted full report by ID.

**Success:** `200` — same object as `AnalysisResponse` stored in `Report.full_response`

**Errors:** `404` if report missing

---

## Analysis pipeline stages

Jobs progress through these stages (see `ANALYSIS_STAGES` in `backend/api/routes/analysis.py`):

| Stage ID | Label | Approx. % |
|----------|-------|-----------|
| `upload_received` | Upload received | 5 |
| `preprocessing` | Normalizing and isolating speech | 18 |
| `segmentation` | Segmenting aligned streams | 30 |
| `agent_panel` | Running forensic agent panel | 48 |
| `consensus` | Calibrating consensus | 66 |
| `xai_evidence_graph` | Building XAI and evidence graph | 82 |
| `narrative_persistence` | Writing narrative and report | 94 |
| `complete` | Analysis complete | 100 |

---

## `AnalysisResponse` schema

Pydantic model: `backend/api/schemas/analysis.py`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Report UUID |
| `filename` | string | Original upload name |
| `consensus` | object | Global verdict and probabilities |
| `agents` | object | Per-agent aggregated outputs keyed by agent name |
| `timeline` | array | Chunk-level consensus events |
| `preprocessing` | object | Duration, VAD, chunk counts |
| `feature_analysis` | object | Acoustic/neural signal breakdown |
| `diagnostics` | object | Review level, warnings, reliability hints |
| `xai` | object | SHAP, counterfactuals, evidence graph |
| `narrative` | object | Structured + human summaries |
| `heatmap_base64` | string \| null | ConvNext Grad-CAM PNG (base64) |
| `mel_previews` | object \| null | Map of `"start:end"` → PNG base64 (per display segment; stripped from DB timeline rows) |
| `timeline_raw_count` | int \| null | Chunk count before UI compression |
| `timeline_display_count` | int \| null | Segment count after compression |
| `processing_metadata` | object | Chunk duration, overlap, sample rates |
| `created_at` | datetime | Report timestamp |

### `consensus`

| Field | Type | Description |
|-------|------|-------------|
| `verdict` | string | `fake`, `real`, or `inconclusive` |
| `confidence` | float | 0–1 |
| `convergence_strength` | float | Agreement across chunks |
| `uncertainty` | float | Residual uncertainty |
| `fake_probability` | float | Calibrated fake probability |
| `real_probability` | float | Calibrated real probability |
| `probability_margin` | float | Margin between fake/real |
| `decision_threshold` | float | Threshold used (default ~0.6) |

### `agents.{name}`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Agent identifier |
| `verdict` | string | Aggregated chunk verdict |
| `confidence` | float | Mean confidence |
| `uncertainty` | float | Mean uncertainty |
| `evidence` | object | Agent-specific metrics |

**Agent keys:** `convnext`, `wavlm`, `aasist`, `acoustic`, `reliability`

### `timeline[]`

| Field | Type | Description |
|-------|------|-------------|
| `start_time` | float | Chunk start (seconds) |
| `end_time` | float | Chunk end (seconds) |
| `event_type` | string | Consensus event type |
| `verdict` | string | Chunk verdict |
| `confidence` | float | Chunk confidence |
| `convergence_strength` | float | Chunk agreement |
| `details` | object | Per-agent calibrated details |
| `deep_reasoning` | array | Optional reasoning strings |
| `threat_warnings` | array | Contradiction/threat objects |
| `segment_count` | int \| null | Number of raw chunks merged into this display segment |

**Threat warning object**

```json
{
  "type": "voice_clone",
  "description": "Human-readable threat summary",
  "severity": "high"
}
```

### `xai`

| Field | Type | Description |
|-------|------|-------------|
| `shap_values` | object | Exact Shapley attributions |
| `counterfactuals` | object | Level 1 analytical sensitivity |
| `evidence_graph` | object | 6-layer directed JSON graph |
| `shap_summary` | string | Text summary |
| `counterfactual_summary` | string | Top sensitivity statement |

**`shap_values` structure**

```json
{
  "method": "exact_consensus_shap",
  "chunks": [
    {
      "chunk_index": 0,
      "start_time": 0.0,
      "end_time": 2.0,
      "values": { "wavlm": 0.12, "convnext": 0.08 },
      "efficiency": 1.0
    }
  ],
  "summary": {
    "average_values": { "wavlm": 0.1, "convnext": 0.07 },
    "top_contributors": [{ "agent": "wavlm", "value": 0.1 }]
  }
}
```

**`counterfactuals.chunks[].sensitivities.{agent}`**

```json
{
  "gradient": 0.5,
  "direction": "increases_fake_probability",
  "current_confidence": 0.8,
  "weight": 1.0,
  "estimated_delta_for_10pct": 0.14,
  "statement": "If phonetic instability decreased by 14%, deepfake confidence would decrease by ..."
}
```

**`evidence_graph`**

```json
{
  "schema_version": "evidence_graph_v1",
  "layers": [{ "id": 1, "name": "Audio Input" }],
  "nodes": [
    { "id": "audio:input", "layer": 1, "type": "audio_input", "label": "Uploaded audio" }
  ],
  "edges": [
    { "source": "audio:input", "target": "preprocess:vad", "relation": "processed_into" }
  ],
  "summary": { "node_count": 12, "edge_count": 11, "layer_counts": { "1": 1 } }
}
```

### `narrative`

| Field | Type | Description |
|-------|------|-------------|
| `structured_summary` | string | Markdown sections: Finding, Evidence, Reliability, Confidence, Contradictions, Explainability |
| `human_summary` | string | Single-paragraph summary |
| `metadata` | object | `narrative_version`, `verdict`, `threat_count`, `sections`, `agent_verdicts`, `top_shap_agents` |

### `diagnostics`

| Field | Type | Description |
|-------|------|-------------|
| `decision_reliability` | float | 0–1 aggregate trust in the decision |
| `review_level` | string | e.g. `moderate_trust`, `high_trust`, `low_trust` |
| `warnings` | array | Combined analyst warnings (`{category, message}`) |
| `quality_warnings` | array | Recording-quality issues (SNR, clipping, etc.) |
| `synthesis_warnings` | array | Agent disagreement / low confidence |
| `event_counts` | object | Counts by `event_type` (e.g. `contradiction`) |
| `agent_count` | int | Agents in response |
| `chunk_count` | int | Temporal chunks analyzed |

**Warning object**

```json
{
  "category": "synthesis_evidence",
  "message": "Agents disagree on at least one chunk; inspect the temporal timeline before relying on the verdict."
}
```

### `feature_analysis` (summary)

| Block | Contents |
|-------|----------|
| `preprocessing` | Same shape as top-level `preprocessing` |
| `signal_quality` | `snr_db`, `clipping_ratio`, `spectral_flatness`, `rms_energy`, `reliability_score` |
| `acoustic_features` | Ranked list: `feature`, `avg_z_score`, `avg_risk_score`, `severity` |
| `neural_signals` | Per-agent aggregate meters for dashboard |
| `consensus_events` | Event type counts |

---

## Sample report JSON

Regenerate a redacted full response (base64 replaced with length placeholders):

```bash
python scripts/extract_report_sample.py --report-id <uuid>
# writes sample_report_redacted.json at repo root
```

Canonical case study in **`RESEARCH_AND_REPORT_DOC.md`** §15–16 uses report `0fada112-21cd-4b0b-9295-e2870b1d300a` (`real_sample_voice.wav`).

---

## CORS

Explicit dev origins only (required when `allow_credentials=True`):

- `http://localhost:5173`, `http://127.0.0.1:5173`
- `http://localhost:5174`, `http://127.0.0.1:5174`

Configured in `backend/app.py`. **Do not use wildcard `*` with credentials in production.**

---

## Persistence

- Database file: `forensic_intelligence.db` (SQLite, project root)
- Upload temp dir: `uploads/` (gitignored)
- Job progress: in-memory only (single-user local research tool)

---

## Error handling conventions

| Scenario | Behavior |
|----------|----------|
| Invalid file type | `400` with `"Invalid file type."` |
| Missing report | `404` with `"Report not found"` |
| Job still running | `202` on `/result` |
| Low reliability chunk | Fail-closed `inconclusive` at consensus layer |
| Agent failure | Isolated where safe; pipeline continues |

---

## Example: job flow (curl)

```bash
# Start job
curl -F "file=@sample.wav" http://localhost:8000/analyze/jobs

# Poll progress
curl http://localhost:8000/analyze/jobs/{job_id}/progress

# Get result when complete
curl http://localhost:8000/analyze/jobs/{job_id}/result
```

---

## Example: synchronous analyze

```bash
curl -F "file=@sample.wav" http://localhost:8000/analyze/
```

---

*API reference for v1 — see `RESEARCH_AND_REPORT_DOC.md` for paper/blackbook narrative and case study.*

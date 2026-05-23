# MASTER PROJECT SPEC
## Consensus-Based Explainable Forensic Audio Intelligence Platform

**Document type:** PRD + System Design  
**Status:** Source of truth for implementation  
**Development strategy:** Vertical MVP  
**Project scope:** Final-year software project with research-grade architecture

---

## 1. Project Overview

This project is a forensic audio intelligence platform that analyzes uploaded speech audio for deepfake, voice-clone, partial synthesis, and audio splice evidence. The system is not a simple binary classifier. It is a multi-agent forensic reasoning system that:

1. preprocesses audio into temporally aligned chunks,
2. runs independent forensic agents on each chunk,
3. applies reliability-based suppression when evidence quality is poor,
4. reasons over contradictions and agreement events,
5. generates exact explainability artifacts and human-readable forensic narratives.

The main output is a forensic verdict with supporting evidence, not just a probability score.

---

## 2. Problem Statement

Modern synthetic speech can sound highly natural and can be partially inserted into otherwise real recordings. Traditional detectors often fail in three ways:

- they collapse the entire file into a single prediction,
- they hide the reasons behind the prediction,
- they do not handle partial or localized attacks well.

This project solves those problems by combining:
- temporal chunk analysis,
- independent forensic agents,
- dynamic reliability suppression,
- explicit contradiction detection,
- exact XAI artifacts,
- structured narrative reporting.

---

## 3. Goals

### Primary goals
- Detect synthetic speech, voice cloning, partial synthesis, and localized splice attacks.
- Identify suspicious time regions instead of only producing a file-level verdict.
- Preserve forensic credibility through reliability-aware suppression and fail-closed behavior.
- Produce explainable outputs that can be inspected in the UI and stored in the database.

### Secondary goals
- Support research-style validation and ablation analysis.
- Provide a clean backend architecture suitable for future improvements.
- Make the UI useful for forensic investigation, not only for demos.

---

## 4. Non-Goals

This version does **not** aim to:
- perform real-time live call analysis,
- support video deepfake detection,
- support speaker diarization as a standalone feature,
- train large neural models from scratch,
- use a free-form LLM as the main narrative engine in v1,
- use cross-attention fusion as the core consensus mechanism in v1,
- implement adversarial training in phase 1 or 2.

---

## 5. Target Users

### Primary users
- Final-year project evaluators
- Academic reviewers
- Forensic analysis users
- Demo reviewers
- Future research users

### Secondary users
- Security teams
- Media verification teams
- Research collaborators

---

## 6. Product Principles

The system must follow these principles:

1. **Evidence first**: outputs must be backed by agent-level evidence.
2. **Temporal precision**: suspicious evidence must be localized by time.
3. **Reliability-aware reasoning**: poor-quality evidence must not be treated as equally trustworthy.
4. **Explainability by design**: explanations are not an afterthought.
5. **Fail closed under degraded evidence**: the system must not hallucinate certainty when audio quality is too poor.
6. **Modular implementation**: each subsystem must be independently testable.

---

## 7. Final Architectural Summary

### High-level flow
Audio input  
→ preprocessing  
→ sample-rate branching  
→ segment-level chunking  
→ independent forensic agents  
→ agent explainability  
→ temporal consensus engine  
→ reliability calibration  
→ forensic reasoner  
→ XAI synthesis  
→ persistence  
→ UI

### Core agents
- ConvNext Agent: spectral artifact reasoning
- WavLM Agent: phonetic and temporal speech realism
- AASIST Agent: deterministic waveform-level spoof checks in v1
- Acoustic Agent: LFCC/CQCC/phase-based forensic signals
- Reliability Agent: quality and trust scoring

### Core reasoning layer
- Temporal Consensus Engine
- Contradiction Threat Rules
- Reliability Suppression Engine
- Exact SHAP Engine
- Analytical Counterfactual Engine
- Deterministic Narrative Engine

---

## 8. System Architecture

## 8.1 Frontend

### Responsibilities
- upload audio
- show multi-stage processing progress
- display agent verdicts and confidence
- display timeline-based suspicious regions
- display consensus events
- display SHAP charts and counterfactual sensitivity
- display evidence graph
- display structured narrative summary

### Frontend stack
- React + Vite
- Recharts for score and attribution charts
- React-Plotly.js for evidence graphs
- vanilla CSS or minimal component styling

### Frontend layout
- Upload panel
- Progress stage indicator
- Timeline panel
- Agent panel grid
- Reliability panel
- Consensus panel
- Explainability drawer / tab
- Narrative panel

---

## 8.2 Backend

### Responsibilities
- file validation
- preprocessing
- chunk generation
- representation routing
- model/agent inference
- reliability suppression
- consensus reasoning
- XAI generation
- narrative generation
- database persistence
- API response assembly

### Backend stack
- FastAPI
- SQLAlchemy
- SQLite for v1
- PyTorch
- Librosa
- NumPy / SciPy
- SHAP values computed analytically by the consensus engine

---

## 8.3 Core modules

### Preprocessing
- audio validation
- silence trimming
- VAD
- LUFS normalization
- quality analysis
- 16 kHz and 48 kHz branching

### Segmentation
- fixed 2-second chunks
- 50% overlap
- masked padding to align stream durations
- chunk metadata generation

### Agents
- ConvNext Agent
- WavLM Agent
- AASIST Agent
- Acoustic Agent
- Reliability Agent

### Consensus
- contradiction detection
- threat classification
- temporal persistence detection
- agreement strength calculation
- final verdict arbitration

### Explainability
- exact SHAP on calibrated consensus contributions
- analytical sensitivity counterfactuals
- evidence graph generation
- deterministic narrative generation

### Persistence
- reports
- narrative reports
- XAI artifacts
- consensus events
- agent event details
- processing metadata

---

## 9. Functional User Flows

## 9.1 Upload and analysis flow
1. User uploads `.wav`, `.mp3`, or `.flac`.
2. Backend validates file type and duration.
3. Backend trims silence and normalizes loudness.
4. Backend creates 16 kHz and 48 kHz streams.
5. Backend splits audio into 2-second chunks with 50% overlap.
6. Each chunk is routed to the relevant agents.
7. Reliability is computed per chunk.
8. If chunk reliability is below threshold, fail-closed logic applies.
9. Agent outputs are suppressed using continuous sigmoid mapping.
10. Consensus engine computes agreement/contradiction events.
11. XAI artifacts and narrative report are generated.
12. Result is persisted and returned to the frontend.

## 9.2 Investigation flow
1. User opens the report.
2. User sees progress, verdict, and confidence.
3. User inspects suspicious time regions.
4. User opens agent details for a chunk.
5. User views contradiction warnings if present.
6. User inspects SHAP and counterfactual outputs.
7. User reads the structured narrative and exportable summary.

---

## 10. Data Model

## 10.1 Report
Stores high-level report metadata and final verdict.

### Fields
- id
- audio_id
- filename
- original_duration
- processed_duration
- verdict
- confidence
- uncertainty
- reliability_score
- schema_version
- pipeline_version
- created_at
- updated_at

---

## 10.2 NarrativeReport
Stores structured and human-readable narrative output separately from the main report.

### Fields
- id
- report_id
- structured_summary
- human_summary
- narrative_metadata (JSON)
- generated_by
- narrative_version
- created_at
- updated_at

---

## 10.3 XAIArtifact
Stores explainability artifacts as structured JSON.

### Fields
- id
- report_id
- shap_values (JSON)
- counterfactuals (JSON)
- evidence_graph (JSON)
- shap_summary
- counterfactual_summary
- xai_version
- created_at
- updated_at

### Notes
Use native JSON columns, not stringified JSON blobs.

---

## 10.4 ConsensusEvent
Stores agreement, contradiction, splice, quality failure, and reliability warning events.

### Fields
- id
- report_id
- event_type
- threat_type
- severity
- description
- diagnostic_metrics (JSON)
- agent_snapshot (JSON)
- threat_confidence
- start_time
- end_time
- created_at
- updated_at

### Notes
- `description` is the human-readable summary.
- `diagnostic_metrics` stores machine-readable evidence.
- `agent_snapshot` stores the agent-level evidence payload.

---

## 10.5 EventAgentDetail
Stores per-agent details for each consensus event.

### Fields
- id
- event_id
- agent_name
- agent_version
- verdict
- confidence
- uncertainty
- adjusted_confidence
- suppression_factor
- temporal_region (JSON)
- created_at
- updated_at

---

## 10.6 ProcessingMetadata
Stores technical metadata required for reproducibility.

### Fields
- id
- report_id
- sample_rate_semantic
- sample_rate_forensic
- chunk_duration
- overlap_ratio
- time_tolerance_ms
- valid_fraction
- created_at

---

## 11. Agent Logic

## 11.1 ConvNext Agent
### Purpose
Detect spectral and spectrogram-based artifacts.

### Input
- spectrogram chunks

### Output
- verdict
- confidence
- uncertainty
- Grad-CAM-like heatmap metadata

### Notes
In v1, use pretrained ConvNext and do not train the fusion layer end-to-end.

---

## 11.2 WavLM Agent
### Purpose
Detect phonetic instability, unnatural speech rhythm, and speech realism issues.

### Input
- 16 kHz waveform chunks

### Output
- verdict
- confidence
- uncertainty
- phonetic instability score

---

## 11.3 AASIST Agent
### Purpose
Provide deterministic waveform-level spoof reasoning in v1.

### Input
- waveform chunks

### Output
- verdict
- confidence
- uncertainty
- phase coherence / periodicity / sub-band anomaly signals

### Notes
In v1, AASIST is a deterministic signal-processing agent, not a heavy neural deployment.

---

## 11.4 Acoustic Agent
### Purpose
Analyze biological plausibility.

### Features
- LFCC
- CQCC
- jitter
- shimmer
- HNR
- phase coherence
- spectral rolloff
- harmonic distortion

### Output
- anomaly score
- verdict
- confidence
- uncertainty

---

## 11.5 Reliability Agent
### Purpose
Estimate signal trustworthiness and support suppression.

### Signals
- clipping ratio
- noise level
- SNR
- compression artifacts
- silent regions
- waveform degradation

### Output
- reliability score
- suppression factor
- uncertainty multiplier
- quality failure flag

---

## 12. Reliability and Suppression

## 12.1 Suppression policy
Use dynamic weight damping before consensus.

### Behavior
- Each agent receives an effective weight.
- The weight is multiplied by a continuous sigmoid-based suppression factor.
- Suppression is computed per chunk.
- Suppression is agent-specific when possible.

### Fail-closed behavior
If chunk reliability < 0.20:
- skip heavyweight neural agents
- run only lightweight diagnostics
- create a QualityFailure event
- return `inconclusive`

### Important
Do not use post-consensus damping as the main mechanism.

---

## 13. Temporal Processing Rules

### Chunking
- 2-second windows
- 50% overlap

### Alignment
- compare chunk boundaries using ±1 ms tolerance
- require overlap ratio ≥ 95% for verification

### Duration mismatch handling
- use timestamp-preserving masked padding
- do not truncate evidence by default

### Time tolerance
- 1e-3 seconds

---

## 14. Contradiction Threat Rules

Threat thresholds are base thresholds that can be escalated by reliability penalties.

### Base thresholds
- Voice clone: WavLM ≥ 0.70
- Audio splice: ConvNext / AASIST ≥ 0.75
- General contradiction: ≥ 0.60

### Threat types
- voice_clone
- localized_splice
- partial_synthesis
- persistent_synthesis
- reliability_warning
- quality_failure

### Storage
Each contradiction warning must persist:
- a human-readable description
- a threat type
- a severity
- a structured diagnostics JSON
- per-agent evidence details

---

## 15. Explainability

## 15.1 SHAP
Use exact coalition-based Shapley computation because there are only four agents.

### Important
SHAP must be computed on calibrated consensus contributions, not raw embeddings.

## 15.2 Counterfactuals
Use analytical sensitivity in v1.

### Example output
“If phonetic instability decreased by 14%, deepfake confidence would decrease by 31%.”

## 15.3 Evidence graph
Represent:
- audio input
- preprocessing and reliability
- forensic agents
- consensus arbitration
- XAI artifacts
- final verdict and narrative

## 15.4 Narrative engine
Use deterministic templates in v1.

### Behavior
- agreement events produce standard synthetic-risk wording
- contradiction events produce explicit voice-clone / splice warnings
- low reliability produces evidence-quality warnings

---

## 16. API Design

## 16.1 `POST /analyze`
Accepts multipart audio upload.

### Returns
- report_id
- final verdict
- confidence
- uncertainty
- reliability
- chunk timeline
- agent outputs
- consensus events
- SHAP summary
- counterfactual summary
- narrative summary
- processing metadata

---

## 16.2 `GET /reports/{id}`
Returns the full persisted report with linked narrative, consensus events, and XAI artifacts.

---

## 16.3 `GET /reports/{id}/timeline`
Returns chunk-level evidence and event markers.

---

## 16.4 `GET /reports/{id}/xai`
Returns SHAP, counterfactual, and evidence graph payloads.

---

## 17. File / Folder Structure

```text
backend/
├── api/
├── agents/
│   ├── convnext_agent.py
│   ├── wavlm_agent.py
│   ├── aasist_agent.py
│   ├── acoustic_agent.py
│   └── reliability_agent.py
├── consensus/
│   ├── consensus_engine.py
│   ├── suppression_engine.py
│   ├── contradiction_rules.py
│   └── temporal_alignment.py
├── preprocessing/
│   ├── validation.py
│   ├── vad.py
│   ├── normalization.py
│   └── branching.py
├── segmentation/
│   ├── chunker.py
│   ├── mask_manager.py
│   └── timeline_manager.py
├── explainability/
│   ├── shap_engine.py
│   ├── counterfactual_engine.py
│   ├── evidence_graph.py
│   └── narrative_engine.py
├── persistence/
│   ├── models.py
│   ├── repositories.py
│   └── schema.py
├── orchestration/
│   ├── forensic_orchestrator.py
│   ├── agent_registry.py
│   └── progress_tracker.py
├── evaluation/
├── migrations/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── charts/
│   ├── graphs/
│   ├── services/
│   └── styles/
```

---

## 18. Tech Stack with Justification

### Frontend
- React + Vite: fast iteration and clean component structure
- Recharts: simple charts and SHAP visualization
- Plotly: node-link evidence graph visualization

### Backend
- FastAPI: async API and clean routing
- SQLAlchemy: flexible relational models
- SQLite: simple local database for v1

### ML / signal
- PyTorch: pretrained neural inference
- Librosa: audio preprocessing and feature extraction
- NumPy / SciPy: numerical computations

### Explainability
- custom exact SHAP logic
- analytical counterfactual sensitivity
- structured narrative templates

---

## 19. Edge Cases

- very short audio
- silence-only audio
- highly compressed audio
- clipped audio
- partial deepfake only in a small chunk
- duration mismatch between streams
- low reliability chunks
- contradictory agent outputs
- exact boundary ambiguity between chunks
- padded tail regions
- model confidence high but reliability low

---

## 20. Constraints and Risks

### Constraints
- single developer
- limited compute
- local development
- no training of large new models in v1

### Risks
- false positives from poor audio quality
- too much architecture complexity if scope expands
- schema churn if future fields are not planned
- confusion if hidden suppression logic is not documented
- UI overload if evidence is not layered carefully

---

## 21. Testing Strategy

## 21.1 Unit tests
- suppression mapping
- confidence adjustment
- threshold logic
- contradiction rules
- chunk alignment
- JSON serialization
- narrative generation

## 21.2 Integration tests
- upload to report flow
- report to persistence flow
- agent to consensus flow
- consensus to XAI flow

## 21.3 Temporal tests
- boundary tolerance
- overlap verification
- padding alignment
- chunk mismatch behavior

## 21.4 Failure-path tests
- reliability < 0.20
- skipped neural agents
- quality failure event
- inconclusive verdict behavior

## 21.5 Benchmark tests
- accuracy
- precision
- recall
- EER
- calibration sanity
- contradiction detection sanity

---

## 22. Error Handling

- invalid file type → reject with clear validation message
- corrupted audio → reject before inference
- too short audio → reject or mark inconclusive
- low reliability chunk → fail closed
- agent failure → isolate agent, log failure, continue if safe
- consensus failure → return diagnostic report, not a silent crash
- persistence failure → preserve response payload and log failure
- alignment mismatch → raise explicit alignment exception

---

## 23. Deployment Overview

### Local v1
- backend runs locally
- frontend runs locally
- SQLite file stored in project directory
- uploads stored temporarily and cleaned after processing

### Recommended runtime
- CPU support must work
- GPU can be used if available
- no hard dependency on cloud services

### Future deployment
- Dockerized backend
- separate frontend deployment
- optional migration to PostgreSQL if scaling is needed

---

## 24. Development Milestones

### Phase 1
- database consolidation
- suppression engine
- directory restructuring
- fail-closed reliability behavior

### Phase 2
- contradiction intelligence
- temporal alignment
- persistence of threat descriptions
- time tolerance verification

### Phase 3
- exact SHAP
- counterfactual sensitivity
- evidence graph
- deterministic narrative report

### Phase 4
- UI refinement
- report exports
- research presentation polish

---

## 25. Implementation Rule

The system must always obey this order:

1. preprocessing
2. segmentation
3. agent inference
4. reliability suppression
5. consensus reasoning
6. explainability
7. persistence
8. frontend display

No step may silently bypass the others.

---

## 26. Final Summary

This project is a multi-agent forensic speech analysis system with temporal chunk reasoning, reliability-aware suppression, exact explainability, contradiction persistence, and deterministic narrative reporting.

The implementation must remain modular, auditable, and testable at every stage.


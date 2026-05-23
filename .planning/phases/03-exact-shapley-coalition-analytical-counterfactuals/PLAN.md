---
phase: "03-exact-shapley-coalition-analytical-counterfactuals"
title: "Exact Shapley Coalition & Analytical Counterfactuals"
created: 2026-05-23
status: ready
type: mvp
requirements: ["XAI-06", "XAI-07", "XAI-09", "TST-05", "TST-06"]
---

# Phase 3: Exact Shapley Coalition & Analytical Counterfactuals - Execution Plan

## Objective

Implement mathematically exact explainability for the calibrated consensus layer: exact Shapley values over the four voting forensic agents, Level 1 analytical counterfactual sensitivity, and deterministic narrative summaries persisted through the existing database and response pipeline.

## Decisions Applied

All decisions from `03-CONTEXT.md` are binding: D-01 through D-06.

---

## Wave 1 - Pure Explainability Engines

### Task 1.1: Exact Shapley Engine

**Files:**
- `backend/explainability/shap/shap_engine.py`
- `tests/xai/test_shap_engine.py`

**Changes:**

1. Replace the risk-score proxy implementation with a deterministic exact Shapley implementation.
2. Add a method such as `compute_consensus_shap(calibrated_details: dict) -> dict`.
3. Use voting agents only: `wavlm`, `convnext`, `aasist`, `acoustic`.
4. Implement exact coalition enumeration across all 16 coalitions.
5. Define coalition value as calibrated fake probability:
   - fake-verdict agent contributes `adjusted_confidence * weight` to fake support.
   - real-verdict agent contributes `(1 - adjusted_confidence) * weight` to fake support.
   - `weight = effective_reliability * (1 - adjusted_uncertainty) * suppression_factor`.
   - empty or zero-support coalitions return `0.5`.
6. Return a structured payload:
   ```python
   {
       "base_value": 0.5,
       "model_output": <full coalition fake_probability>,
       "values": {"wavlm": ..., "convnext": ..., "aasist": ..., "acoustic": ...},
       "details": {
           "wavlm": {
               "verdict": "...",
               "adjusted_confidence": ...,
               "adjusted_uncertainty": ...,
               "suppression_factor": ...,
               "effective_reliability": ...,
               "weight": ...,
               "normalized_contribution": ...
           }
       }
   }
   ```
7. Preserve `compute_importance(features_dict)` as a backward-compatible wrapper if any existing caller still uses it.

**Acceptance criteria:**
- Exact Shapley uses no Monte Carlo sampling.
- Sum of Shapley values equals `model_output - base_value` within `1e-9`.
- Symmetric equivalent agents receive equal attributions.
- Zero-weight or fully suppressed agents receive zero or near-zero attribution.
- Existing imports of `SHAPEngine` still work.

---

### Task 1.2: Analytical Counterfactual Engine

**Files:**
- `backend/explainability/counterfactuals/counterfactual_engine.py`
- `backend/explainability/counterfactual_engine.py`
- `tests/xai/test_counterfactual_engine.py`

**Changes:**

1. Make `backend/explainability/counterfactuals/counterfactual_engine.py` the canonical Level 1 analytical engine.
2. Add a method such as `compute_consensus_sensitivity(calibrated_details: dict, fake_probability: float, real_probability: float) -> dict`.
3. Calculate local derivatives for the consensus fake probability using weighted support math:
   - `dP/dF = R / (F + R)^2`
   - `dP/dR = -F / (F + R)^2`
4. For each agent, compute:
   - current adjusted confidence
   - effective weight
   - gradient direction
   - sensitivity magnitude
   - deterministic recommendation text
5. Keep the top-level `backend/explainability/counterfactual_engine.py` as a compatibility adapter or remove its duplicate logic only if all imports are updated.
6. Return a structured payload:
   ```python
   {
       "method": "analytical_level_1",
       "baseline": {"fake_probability": ..., "real_probability": ...},
       "sensitivities": {
           "wavlm": {
               "gradient": ...,
               "direction": "increases_fake_probability",
               "current_confidence": ...,
               "estimated_delta_for_10pct": ...,
               "statement": "..."
           }
       },
       "summary": "..."
   }
   ```

**Acceptance criteria:**
- No perturbation simulation or iterative search is used.
- Fake-verdict agents have positive fake-probability sensitivity when their adjusted confidence increases.
- Real-verdict agents have negative fake-probability sensitivity when their adjusted confidence increases.
- Zero-support cases return stable neutral sensitivities, not divide-by-zero errors.
- Tests validate numerical derivative signs and at least one hand-calculated value.

---

## Wave 2 - Deterministic Narrative and API Integration

### Task 2.1: Deterministic Narrative Engine

**Files:**
- `backend/explainability/narrative_engine.py`
- `tests/xai/test_narrative_engine.py`

**Changes:**

1. Create a deterministic `NarrativeEngine`.
2. Generate `structured_summary`, `human_summary`, and `narrative_metadata`.
3. Include these structured sections:
   - Finding
   - Evidence
   - Reliability
   - Confidence
   - Contradictions
   - Explainability
4. Use only observed values from:
   - `global_consensus`
   - `frontend_agents`
   - `chunk_consensus`
   - `shap_values`
   - `counterfactuals`
   - `preprocessing`
   - `diagnostics`
5. Explicitly mention voice clone/localized splice/partial synthesis warnings when present.
6. Explicitly mention low reliability or fail-closed evidence-quality limitations when present.
7. Avoid unsupported claims. No LLM text generation.

**Acceptance criteria:**
- Narrative output is deterministic for identical inputs.
- Output includes all required sections.
- Threat warnings and low-reliability diagnostics appear when supplied.
- Missing optional XAI data degrades gracefully without exceptions.

---

### Task 2.2: API Persistence and Response Assembly

**Files:**
- `backend/api/routes/analysis.py`
- `backend/api/schemas/analysis.py`
- `backend/explainability/xai_manager.py`
- `tests/integration/test_validation.py`

**Changes:**

1. Import and use `SHAPEngine`, canonical `CounterfactualEngine`, and `NarrativeEngine` in the analysis route or a small local helper.
2. For each chunk consensus, calculate exact Shapley and analytical counterfactual payloads from `calibrated_details`.
3. Persist aggregate payloads in `XAIArtifact`:
   - `shap_values`
   - `counterfactuals`
   - `shap_summary`
   - `counterfactual_summary`
   - `xai_version`
4. Replace inline narrative string construction with `NarrativeEngine`.
5. Persist narrative output in `NarrativeReport`.
6. Add response fields for the richer XAI/narrative data in a backward-compatible way, for example:
   ```python
   "xai": {
       "shap_values": ...,
       "counterfactuals": ...,
       "shap_summary": ...,
       "counterfactual_summary": ...
   },
   "narrative": {
       "structured_summary": ...,
       "human_summary": ...,
       "metadata": ...
   }
   ```
7. Keep existing `heatmap_base64`, `feature_analysis`, `diagnostics`, and timeline fields unchanged.

**Acceptance criteria:**
- Placeholder `segment_contributions` / `sensitivity_estimates` payloads are replaced by engine outputs.
- Database persistence uses native JSON payloads, not stringified JSON.
- Response schema accepts the new XAI and narrative payloads.
- Existing validation and consensus tests still pass.

---

## Wave 3 - Verification Harness

### Task 3.1: Mathematical XAI Tests

**Files:**
- `tests/xai/test_shap_engine.py`
- `tests/xai/test_counterfactual_engine.py`

**Tests:**

- Exact Shapley efficiency: sum equals `v(N) - v(empty)`.
- Exact Shapley symmetry: identical calibrated agents receive identical values.
- Exact Shapley dummy behavior: zero-weight suppressed agent contributes `0.0`.
- Counterfactual gradient sign for fake-verdict agents.
- Counterfactual gradient sign for real-verdict agents.
- Counterfactual neutral behavior on zero-support input.

**Acceptance criteria:**
- `pytest tests/xai/test_shap_engine.py tests/xai/test_counterfactual_engine.py -q` passes.
- Tests use synthetic dictionaries and do not load neural models.

---

### Task 3.2: Narrative and Integration Tests

**Files:**
- `tests/xai/test_narrative_engine.py`
- `tests/integration/test_validation.py`
- `tests/consensus/test_suppression.py` if schema validation needs extension

**Tests:**

- Narrative engine includes required sections.
- Narrative engine includes threat warning text when supplied.
- Narrative engine includes reliability caveats when reliability is low.
- API response schema accepts `xai` and `narrative` payloads.
- Existing consensus suite remains green.

**Acceptance criteria:**
- `pytest tests/xai tests/consensus tests/integration/test_validation.py -q` passes.
- `python -m backend.migrations.validate_schema` passes.
- No tests require downloading neural model weights.

---

## Verification Plan

Run after implementation:

```powershell
. .venv\Scripts\Activate.ps1
python -m pytest tests\xai tests\consensus tests\integration\test_validation.py -q
python -m backend.migrations.validate_schema
python -c "from backend.explainability.shap.shap_engine import SHAPEngine; print('SHAPEngine OK')"
python -c "from backend.explainability.counterfactuals.counterfactual_engine import CounterfactualEngine; print('CounterfactualEngine OK')"
python -c "from backend.explainability.narrative_engine import NarrativeEngine; print('NarrativeEngine OK')"
```

## Requirements Coverage

| Requirement | Covered By |
|-------------|------------|
| XAI-06 | Task 1.1, Task 3.1 |
| XAI-07 | Task 1.2, Task 3.1 |
| XAI-09 | Task 2.1, Task 3.2 |
| TST-05 | Task 3.1 |
| TST-06 | Task 3.1 |

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Divergence between SHAP value function and consensus math | Use `calibrated_details` and mirror `ConsensusEngine` weighted support semantics. |
| Duplicate counterfactual engines confuse imports | Declare `backend/explainability/counterfactuals/counterfactual_engine.py` canonical and keep top-level file as adapter only. |
| Route-level tests trigger heavy model loading | Keep most tests pure; only validate schema/serialization in lightweight integration tests. |
| Narrative overstates evidence | Use deterministic templates tied to observed fields only. |

## Success Criteria

- Exact Shapley attributions are deterministic and mathematically verified.
- Analytical counterfactuals expose local sensitivity without perturbation simulation.
- Deterministic narrative summaries are generated and persisted.
- API response exposes XAI/narrative payloads for future UI phases.
- Phase 3 verification commands pass.

---

*Plan created: 2026-05-23*
*Ready for execution*

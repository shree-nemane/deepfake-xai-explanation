# Phase 3 Research: Exact SHAP, Analytical Counterfactuals, Narrative Engine

## Summary

The project can implement Phase 3 without additional product discussion. The spec defines exact Shapley values over four calibrated agents, Level 1 analytical sensitivity, and deterministic narratives. Current code already exposes the needed calibrated consensus data through `chunk_consensus[*]["calibrated_details"]` and has persistence columns for `XAIArtifact` and `NarrativeReport`.

## Existing State

- `ConsensusEngine.evaluate_chunk_consensus()` returns:
  - `fake_probability`
  - `real_probability`
  - `calibrated_details`
  - `threat_warnings`
  - `diagnostic_metrics`
- `analysis.py` persists:
  - `XAIArtifact.shap_values`
  - `XAIArtifact.counterfactuals`
  - `XAIArtifact.shap_summary`
  - `XAIArtifact.counterfactual_summary`
  - `NarrativeReport.structured_summary`
  - `NarrativeReport.human_summary`
- Current XAI engines are placeholders:
  - `SHAPEngine.compute_importance()` uses feature risk score proxies.
  - Counterfactual engines emit generic suggestion text, not analytical consensus sensitivity.
  - Narrative generation is inline string formatting inside `analysis.py`.

## Exact Shapley Approach

For agents `N = {wavlm, convnext, aasist, acoustic}`, calculate:

```text
phi_i = sum_{S subseteq N \ {i}} |S|!(n-|S|-1)! / n! * (v(S union {i}) - v(S))
```

Use `n = 4` and evaluate all coalitions exactly. No random sampling.

Recommended value function:

```text
v(S) = coalition fake probability
```

For each included agent:

- If verdict is `fake`, fake support receives `adjusted_confidence * weight`.
- If verdict is `real`, fake support receives `(1 - adjusted_confidence) * weight`.
- Weight should mirror existing consensus semantics as closely as available from `calibrated_details`:
  `effective_reliability * (1 - adjusted_uncertainty) * suppression_factor`.
- Empty/zero-support coalition returns `0.5`.

This makes Shapley values explain the chunk's calibrated fake probability, not raw feature importance.

## Analytical Counterfactual Approach

For weighted fake support `F`, real support `R`, and `P = F / (F + R)`:

```text
dP/dF = R / (F + R)^2
dP/dR = -F / (F + R)^2
```

For each agent, derive sensitivity from its verdict direction and current calibrated weight:

- Fake-verdict agent: increasing adjusted confidence increases `F` and decreases real-side support.
- Real-verdict agent: increasing adjusted confidence increases `R` and decreases fake-side support.
- Near-zero denominator returns neutral sensitivity `0.0`.

Outputs should include per-agent gradient, direction, current value, and deterministic text like:

```text
If wavlm adjusted confidence decreased by 0.14, fake probability would decrease by about 0.31.
```

## Narrative Approach

Move narrative generation out of `analysis.py` into a deterministic engine under `backend/explainability/`.

Inputs:

- `global_consensus`
- `frontend_agents`
- `chunk_consensus`
- `shap_values`
- `counterfactuals`
- `preprocessing`
- `diagnostics`

Outputs:

- `structured_summary`: machine-friendly sections.
- `human_summary`: concise forensic paragraph.
- `narrative_metadata`: evidence counts, top contributors, warnings, and versions.

Templates must cite only observed evidence: verdict, confidence, reliability, threat warnings, top SHAP contributors, and counterfactual sensitivity.

## Risks

- Placeholder SHAP/counterfactual payloads in `analysis.py` may mislead the UI if not replaced atomically.
- There are two counterfactual engine files. Avoid expanding both independently; choose a canonical engine and preserve wrappers only for compatibility.
- Tests should not import `analysis.py` if doing so triggers `AudioProcessor` and model/VAD initialization. Prefer pure engine tests plus targeted serialization tests.

## Verification Targets

- Exact Shapley efficiency: sum of agent values equals `v(N) - v(empty)` within tolerance.
- Symmetry: identical agents receive identical Shapley values.
- Dummy/null agent: zero-weight neutral agent gets near-zero attribution.
- Analytical sensitivity signs match verdict direction.
- Narrative text contains required sections and never references unavailable evidence.
- Existing consensus and validation tests remain green.


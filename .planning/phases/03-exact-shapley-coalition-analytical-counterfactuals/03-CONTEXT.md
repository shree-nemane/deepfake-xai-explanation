# Phase 3: Exact Shapley Coalition & Analytical Counterfactuals - Context

**Gathered:** 2026-05-23
**Status:** Ready for planning
**Source:** Direct planning from `DFXAI_project_spec.md`, `DFXAI_agent_prompt.md`, ROADMAP, REQUIREMENTS, and current codebase

<domain>
## Phase Boundary

Implement backend explainability for the existing multi-agent audio forensic pipeline:

- Exact deterministic Shapley values over calibrated consensus support vectors.
- Level 1 analytical counterfactual sensitivity estimates.
- Deterministic narrative summaries from consensus, reliability, timeline, and XAI artifacts.

This phase does not build the frontend explainability drawer and does not implement the full 6-layer Evidence Graph UI surface. Evidence Graph is mapped to Phase 4, and React drawer/tab work is mapped to Phase 5.

</domain>

<decisions>
## Implementation Decisions

### D-01: Exact Shapley Scope
- Compute Shapley values over the four voting forensic agents only: `wavlm`, `convnext`, `aasist`, and `acoustic`.
- Use exact enumeration over all coalitions. With four agents, this is 16 coalition evaluations per chunk, not Monte Carlo sampling.
- Use calibrated consensus details, adjusted confidence, adjusted uncertainty, suppression factor, and verdict direction as inputs. Do not use raw embeddings or raw model logits.

### D-02: Coalition Value Function
- Define the coalition value as the coalition's calibrated fake probability using the same weighted support semantics as `ConsensusEngine`.
- Preserve deterministic behavior when a coalition is empty or has zero total support by returning neutral fake probability `0.5`.
- Include enough per-agent contribution metadata for auditability: marginal contribution, normalized contribution, verdict, adjusted confidence, adjusted uncertainty, suppression factor, and effective reliability.

### D-03: Analytical Counterfactual Scope
- Implement Level 1 analytical sensitivity only. Do not implement perturbation simulation or iterative search; that is v2 scope.
- Calculate local derivatives of fake probability with respect to each agent's adjusted confidence/support contribution.
- Produce deterministic "what would change" text from those gradients, confidence direction, and current verdict.

### D-04: Narrative Engine Scope
- Implement a rule-driven deterministic narrative engine.
- Generate structured sections: Finding, Evidence, Reliability, Confidence, Contradictions, Explainability.
- Use existing contradiction warnings and reliability diagnostics; do not use an LLM.

### D-05: API/Persistence Integration
- Replace placeholder XAI payloads in `backend/api/routes/analysis.py` with outputs from Phase 3 engines.
- Persist SHAP, counterfactual, and narrative outputs through the existing `XAIArtifact` and `NarrativeReport` schemas created in Phase 1.
- Keep the response shape backward compatible while adding richer `xai` / narrative fields where useful for later UI phases.

### D-06: Test Discipline
- Add pure unit tests under `tests/xai/` for mathematical exactness and deterministic narrative behavior.
- Add integration-level assertions that the API assembly path can serialize and persist the new XAI payloads without loading heavyweight neural models.

### the agent's Discretion
- Internal class/function names, as long as they match existing Python style and stay under `backend/explainability/`.
- Exact text wording of deterministic narrative templates, as long as they are evidence-bound and contain no invented claims.
- Whether to preserve the existing placeholder `SHAPEngine.compute_importance()` as a compatibility wrapper.

</decisions>

<canonical_refs>
## Canonical References

### Project Specifications
- `DFXAI_project_spec.md` - Source of truth for exact SHAP, analytical counterfactuals, deterministic narrative, and v1/v2 boundaries.
- `DFXAI_agent_prompt.md` - Execution rules: small diffs, verify after changes, no speculative redesign.
- `.planning/PROJECT.md` - Current validated requirements and remaining active scope.
- `.planning/REQUIREMENTS.md` - Phase 3 requirements: `XAI-06`, `XAI-07`, `XAI-09`, `TST-05`, `TST-06`.
- `.planning/ROADMAP.md` - Phase 3 success criteria.

### Existing Backend Code
- `backend/consensus/consensus_engine.py` - Source of calibrated details and support semantics.
- `backend/orchestration/forensic_orchestrator.py` - Produces chunk-level consensus and global consensus.
- `backend/api/routes/analysis.py` - Current persistence and response assembly integration point.
- `backend/persistence/database.py` - Existing `XAIArtifact` and `NarrativeReport` schemas.
- `backend/explainability/shap/shap_engine.py` - Placeholder SHAP engine to replace/extend.
- `backend/explainability/counterfactuals/counterfactual_engine.py` - Placeholder feature counterfactual engine.
- `backend/explainability/counterfactual_engine.py` - Existing consensus counterfactual placeholder; consolidate or preserve compatibility deliberately.
- `backend/explainability/xai_manager.py` - Existing manager wrapper.

### Existing Tests
- `tests/consensus/test_suppression.py` - Suppression and schema test patterns.
- `tests/consensus/test_contradiction.py` - Consensus payload fixture style.
- `tests/integration/test_validation.py` - Lightweight integration validation pattern.

</canonical_refs>

<specifics>
## Specific Implementation Notes

- `backend/api/routes/analysis.py` currently persists placeholder `shap_values={"segment_contributions": [...]}` and placeholder `counterfactuals={"sensitivity_estimates": [...]}`. Phase 3 must replace those with mathematically meaningful engine outputs.
- `backend/explainability/shap/shap_engine.py` currently imports `shap` and returns risk score proxies. Exact Shapley for this project should be custom deterministic Python over the calibrated consensus vectors.
- `backend/explainability/evidence_graph.py` remains Phase 4 scope except where Phase 3 needs a minimal narrative reference.
- Phase 3 should preserve CPU-only execution and avoid triggering neural model downloads in tests.

</specifics>

<deferred>
## Deferred Ideas

- Full 6-layer Evidence Graph generation is Phase 4.
- React SHAP/counterfactual/evidence graph UI is Phase 5.
- Counterfactual Level 2 perturbation simulation is v2.
- LLM narrative rewriting is v2.

</deferred>

---

*Phase: 03-exact-shapley-coalition-analytical-counterfactuals*
*Context gathered: 2026-05-23 from locked project specification and codebase inspection*

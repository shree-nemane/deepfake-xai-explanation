import math

from backend.explainability.shap.shap_engine import SHAPEngine


def _detail(verdict, confidence, weight=1.0):
    return {
        "verdict": verdict,
        "adjusted_confidence": confidence,
        "adjusted_uncertainty": 0.0,
        "suppression_factor": weight,
        "effective_reliability": 1.0,
    }


def test_exact_shap_efficiency():
    engine = SHAPEngine()
    result = engine.compute_consensus_shap({
        "wavlm": _detail("fake", 0.90),
        "convnext": _detail("fake", 0.80),
        "aasist": _detail("real", 0.70),
        "acoustic": _detail("real", 0.60),
    })

    total = sum(result["values"].values())
    assert math.isclose(total, result["model_output"] - result["base_value"], abs_tol=1e-9)


def test_exact_shap_symmetry_for_identical_agents():
    engine = SHAPEngine()
    result = engine.compute_consensus_shap({
        "wavlm": _detail("fake", 0.80),
        "convnext": _detail("fake", 0.80),
    })

    assert math.isclose(result["values"]["wavlm"], result["values"]["convnext"], abs_tol=1e-9)


def test_exact_shap_zero_weight_agent_is_dummy():
    engine = SHAPEngine()
    result = engine.compute_consensus_shap({
        "wavlm": _detail("fake", 0.90),
        "convnext": _detail("fake", 0.90, weight=0.0),
    })

    assert math.isclose(result["values"]["convnext"], 0.0, abs_tol=1e-9)


def test_empty_shap_returns_neutral_payload():
    result = SHAPEngine().compute_consensus_shap({})

    assert result["base_value"] == 0.5
    assert result["model_output"] == 0.5
    assert result["values"] == {}

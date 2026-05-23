import math

from backend.explainability.counterfactuals.counterfactual_engine import CounterfactualEngine


def _detail(verdict, confidence, weight=1.0):
    return {
        "verdict": verdict,
        "adjusted_confidence": confidence,
        "adjusted_uncertainty": 0.0,
        "suppression_factor": weight,
        "effective_reliability": 1.0,
    }


def test_fake_agent_has_positive_fake_probability_gradient():
    result = CounterfactualEngine().compute_consensus_sensitivity({
        "wavlm": _detail("fake", 0.80),
        "acoustic": _detail("real", 0.80),
    })

    assert result["sensitivities"]["wavlm"]["gradient"] > 0
    assert result["sensitivities"]["wavlm"]["direction"] == "increases_fake_probability"


def test_real_agent_has_negative_fake_probability_gradient():
    result = CounterfactualEngine().compute_consensus_sensitivity({
        "wavlm": _detail("fake", 0.80),
        "acoustic": _detail("real", 0.80),
    })

    assert result["sensitivities"]["acoustic"]["gradient"] < 0
    assert result["sensitivities"]["acoustic"]["direction"] == "decreases_fake_probability"


def test_gradient_matches_hand_calculated_value():
    result = CounterfactualEngine().compute_consensus_sensitivity({
        "wavlm": _detail("fake", 0.80),
        "acoustic": _detail("real", 0.80),
    })

    assert math.isclose(result["sensitivities"]["wavlm"]["gradient"], 0.5, abs_tol=1e-9)
    assert math.isclose(result["sensitivities"]["acoustic"]["gradient"], -0.5, abs_tol=1e-9)


def test_zero_support_returns_neutral_sensitivity():
    result = CounterfactualEngine().compute_consensus_sensitivity({
        "wavlm": _detail("fake", 0.80, weight=0.0),
    })

    assert result["sensitivities"]["wavlm"]["gradient"] == 0.0
    assert result["sensitivities"]["wavlm"]["direction"] == "neutral"

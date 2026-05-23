from backend.explainability.integrated_gradients.ig_engine import IGEngine
from backend.explainability.shap.shap_engine import SHAPEngine
from backend.explainability.counterfactuals.counterfactual_engine import CounterfactualEngine

class XAIManager:
    def __init__(self, model, device):
        self.model = model
        self.device = device
        self.ig_engine = IGEngine(model, device)
        self.shap_engine = SHAPEngine(model)
        self.cf_engine = CounterfactualEngine()

    def compute_integrated_gradients(self, input_tensor, target_class=None):
        return self.ig_engine.compute(input_tensor, target_class)

    def compute_shap_values(self, features_dict):
        return self.shap_engine.compute_importance(features_dict)

    def compute_consensus_shap(self, calibrated_details):
        return self.shap_engine.compute_consensus_shap(calibrated_details)

    def generate_counterfactuals(self, features_dict, risk_threshold=0.5):
        return self.cf_engine.generate(features_dict, risk_threshold)

    def compute_consensus_sensitivity(self, calibrated_details, fake_probability=None, real_probability=None):
        return self.cf_engine.compute_consensus_sensitivity(
            calibrated_details,
            fake_probability,
            real_probability,
        )

    @staticmethod
    def attr_to_base64(attr_map):
        return IGEngine.to_base64(attr_map)

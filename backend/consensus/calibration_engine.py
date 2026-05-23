class CalibrationEngine:
    """Normalizes confidence and uncertainty across disparate forensic agents."""
    
    def __init__(self):
        # Baseline reliabilities for different agents based on historical benchmarking
        self.agent_base_reliability = {
            "wavlm": 0.90,
            "convnext": 0.88,
            "aasist": 0.92,
            "acoustic": 0.80
        }
        
    def calibrate(self, agent_name, raw_confidence, raw_uncertainty, reliability_score=1.0):
        """
        Calibrates the raw output of an agent based on its historical reliability
        and the current sample's reliability (e.g., from the ReliabilityAgent).
        """
        base_rel = self.agent_base_reliability.get(agent_name, 0.8)
        
        # Effective reliability incorporates both historical accuracy and signal quality
        effective_reliability = base_rel * reliability_score
        
        # Calibrated confidence shrinks towards 0.5 (uncertainty) if reliability is low
        calibrated_confidence = 0.5 + (raw_confidence - 0.5) * effective_reliability
        
        # Uncertainty increases if reliability is low
        calibrated_uncertainty = raw_uncertainty + (1.0 - effective_reliability) * 0.5
        calibrated_uncertainty = min(1.0, calibrated_uncertainty)
        
        return {
            "calibrated_confidence": calibrated_confidence,
            "calibrated_uncertainty": calibrated_uncertainty,
            "effective_reliability": effective_reliability
        }

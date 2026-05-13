import torch
import numpy as np

class UncertaintyEngine:
    def __init__(self, model):
        self.model = model

    def estimate(self, input_tensor, num_passes=30):
        """
        Monte Carlo Dropout uncertainty estimation.
        """
        self.model.train() # Enable dropout for uncertainty estimation
        
        try:
            torch.manual_seed(42) # Ensure passes are deterministic for the same input
            all_probs = []
            for _ in range(num_passes):
                with torch.no_grad():
                    outputs = self.model(input_tensor)
                    probs = torch.softmax(outputs.logits, dim=1)
                    all_probs.append(probs.cpu().numpy())
        finally:
            self.model.eval() # CRITICAL: Ensure we return to eval mode
        
        all_probs = np.array(all_probs).squeeze()
        mean_probs = np.mean(all_probs, axis=0)
        variance = np.var(all_probs, axis=0)
        entropy = -np.sum(mean_probs * np.log(mean_probs + 1e-8))
        
        pred = np.argmax(mean_probs)
        total_variance = np.sum(variance)
        
        uncertainty = "low" if total_variance < 0.01 else "moderate" if total_variance < 0.05 else "high"
            
        return {
            "prediction": "fake" if pred == 1 else "real",
            "confidence": float(mean_probs[pred]),
            "uncertainty": uncertainty,
            "variance": float(total_variance),
            "entropy": float(entropy)
        }

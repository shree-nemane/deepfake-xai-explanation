import torch
from captum.attr import IntegratedGradients
import numpy as np
import cv2
import base64

class IGEngine:
    def __init__(self, model, device):
        self.model = model
        self.device = device
        # Wrap model to return only logits for Captum compatibility
        self.ig = IntegratedGradients(lambda x: self.model(x).logits)

    def compute(self, input_tensor, target_class=None):
        if target_class is None:
            outputs = self.model(input_tensor)
            target_class = torch.argmax(outputs.logits, dim=1).item()
            
        attributions, delta = self.ig.attribute(input_tensor, target=target_class, return_convergence_delta=True)
        
        attributions = attributions.squeeze().cpu().detach().numpy()
        attributions = np.transpose(attributions, (1, 2, 0))
        
        attr_map = np.abs(attributions).mean(axis=2)
        attr_map = (attr_map - attr_map.min()) / (attr_map.max() - attr_map.min() + 1e-8)
        
        return attr_map

    @staticmethod
    def to_base64(attr_map):
        try:
            attr_colored = cv2.applyColorMap((attr_map * 255).astype(np.uint8), cv2.COLORMAP_HOT)
            _, buffer = cv2.imencode('.png', attr_colored)
            return base64.b64encode(buffer).decode('utf-8')
        except Exception:
            return None

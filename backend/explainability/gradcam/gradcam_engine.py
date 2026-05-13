import torch
import torch.nn.functional as F
import numpy as np
import cv2

class GradCAMEngine:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _save_activation(self, module, input, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def _register_hooks(self):
        self.target_layer.register_forward_hook(self._save_activation)
        self.target_layer.register_full_backward_hook(self._save_gradient)

    def generate(self, input_tensor, target_class=None):
        self.gradients = None
        self.activations = None
        
        self.model.zero_grad()
        outputs = self.model(input_tensor)
        logits = outputs.logits
        pred_class = logits.argmax(dim=1).item()
        
        if target_class is None:
            target_class = pred_class
            
        score = logits[0, target_class]
        score.backward()
        
        if self.gradients is None or self.activations is None:
            return np.zeros((224, 224), dtype=np.float32)

        grads = self.gradients.mean(dim=(2, 3), keepdim=True)
        acts = self.activations
        cam = (acts * grads).sum(dim=1).squeeze()
        cam = F.relu(cam)
        
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min + 1e-8)
        else:
            cam = torch.zeros_like(cam)
            
        heatmap = cam.cpu().numpy()
        return cv2.resize(heatmap, (224, 224))

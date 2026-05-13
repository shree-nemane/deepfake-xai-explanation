import torch
from transformers import ConvNextForImageClassification
from backend.forensic.features.acoustic_features import generate_spectrogram

class ConvNextHandler:
    def __init__(self, device):
        self.device = device
        self.model_name = "kubinooo/convnext-tiny-224-audio-deepfake-classification"
        self.model = ConvNextForImageClassification.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    def get_features(self, y, sr):
        """
        Extract features from the layer before the classifier.
        """
        input_tensor = generate_spectrogram(y, sr).to(self.device)
        with torch.no_grad():
            outputs = self.model.convnext(input_tensor)
            pooled_output = outputs.pooler_output # Shape: (1, 768)
        return pooled_output, input_tensor

    def get_logits(self, input_tensor):
        """
        Run full inference to get raw logits.
        """
        with torch.no_grad():
            outputs = self.model(input_tensor)
        return outputs.logits

    def get_target_layer(self):
        """
        Returns the layer used for Grad-CAM.
        """
        return self.model.convnext.encoder.stages[3].layers[-1].dwconv

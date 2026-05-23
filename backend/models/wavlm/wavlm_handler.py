import numpy as np
import torch
from transformers import AutoFeatureExtractor, WavLMModel


class WavLMHandler:
    """Shared WavLM embedding extractor for phonetic/semantic agents."""

    def __init__(self, device, model_name="microsoft/wavlm-base-plus"):
        self.device = device
        self.model_name = model_name
        self.processor = AutoFeatureExtractor.from_pretrained(self.model_name)
        self.model = WavLMModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    def extract_embeddings(self, y, sr=16000):
        """Return mean-pooled WavLM embeddings and temporal instability."""
        audio = np.asarray(y, dtype=np.float32)
        inputs = self.processor(
            audio,
            sampling_rate=sr,
            return_tensors="pt",
            padding=True,
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state
            mean_embeddings = torch.mean(embeddings, dim=1)

            if embeddings.shape[1] > 1:
                deltas = embeddings[:, 1:, :] - embeddings[:, :-1, :]
                phonetic_instability = torch.mean(torch.abs(deltas)).item()
            else:
                phonetic_instability = 0.0

        return mean_embeddings, phonetic_instability

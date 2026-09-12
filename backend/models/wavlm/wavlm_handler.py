import numpy as np
import torch
try:
    from transformers import AutoFeatureExtractor, WavLMModel
except ImportError:
    AutoFeatureExtractor = None
    WavLMModel = None


class WavLMHandler:
    """Shared WavLM embedding extractor for phonetic/semantic agents."""

    def __init__(self, device, model_name="microsoft/wavlm-base-plus"):
        if AutoFeatureExtractor is None or WavLMModel is None:
            raise ImportError("transformers library is required for WavLMHandler")
        self.device = device
        self.model_name = model_name
        self.processor = AutoFeatureExtractor.from_pretrained(self.model_name)
        self.model = WavLMModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    def extract_embeddings(self, y, sr=16000, return_entropy=False):
        """Return mean-pooled WavLM embeddings, temporal instability, and optional temporal entropy."""
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
                temporal_entropy = float(torch.var(embeddings, dim=1).mean().item())
            else:
                phonetic_instability = 0.0
                temporal_entropy = 0.0

        if return_entropy:
            return mean_embeddings, phonetic_instability, temporal_entropy
        return mean_embeddings, phonetic_instability

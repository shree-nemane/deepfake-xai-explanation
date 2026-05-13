import torch
from transformers import Wav2Vec2Processor, Wav2Vec2Model
import numpy as np

class Wav2VecHandler:
    def __init__(self, device):
        self.device = device
        self.model_name = "facebook/wav2vec2-base"
        self.processor = Wav2Vec2Processor.from_pretrained(self.model_name)
        self.model = Wav2Vec2Model.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    def extract_embeddings(self, y, sr=16000):
        """
        Extract mean-pooled embeddings from Wav2Vec2.
        """
        inputs = self.processor(y, sampling_rate=sr, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # last_hidden_state shape: (batch_size, sequence_length, hidden_size)
            embeddings = outputs.last_hidden_state
            
            # Mean pooling over the sequence length
            mean_embeddings = torch.mean(embeddings, dim=1)
            
        return mean_embeddings # Shape: (1, 768)

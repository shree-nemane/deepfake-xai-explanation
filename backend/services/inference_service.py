import torch
import os
from transformers import ConvNextForImageClassification
from backend.forensic.features.acoustic_features import generate_spectrogram, extract_all_features
from backend.explainability.gradcam.gradcam_engine import GradCAMEngine
from backend.models.wav2vec.wav2vec_handler import Wav2VecHandler
from backend.models.fusion.fusion_model import ForensicFusionModel
from backend.explainability.xai_manager import XAIManager
import numpy as np
import librosa
import pyloudnorm as pyln

from backend.forensic.confidence.uncertainty_engine import UncertaintyEngine

from backend.models.convnext.convnext_handler import ConvNextHandler

class InferenceService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.convnext_handler = None
        self.wav2vec_handler = None
        self.fusion_model = None
        self.gradcam = None
        self.xai_manager = None
        self.uncertainty_engine = None
        self.load_models()

    def load_models(self):
        print(f"Initializing model handlers on {self.device}...")
        self.convnext_handler = ConvNextHandler(self.device)
        self.convnext = self.convnext_handler.model # For compatibility with engines
        
        # Init Engines
        self.gradcam = GradCAMEngine(self.convnext, self.convnext_handler.get_target_layer())
        self.xai_manager = XAIManager(self.convnext, self.device)
        self.uncertainty_engine = UncertaintyEngine(self.convnext)
        
        print(f"Loading Wav2Vec2 model on {self.device}...")
        self.wav2vec_handler = Wav2VecHandler(self.device)
        
        print("Initializing Fusion Model...")
        # Forensic dim is 11 as defined in acoustic_features.py
        self.fusion_model = ForensicFusionModel(convnext_dim=768, wav2vec_dim=768, forensic_dim=11).to(self.device)
        self.fusion_model.eval()
        
        print("Models loaded successfully.")

    def preprocess_audio_robust(self, y, sr):
        """
        Apply VAD, Trimming, and LUFS normalization.
        """
        # 1. Trimming
        y_trimmed, _ = librosa.effects.trim(y)
        
        # 2. LUFS Normalization
        meter = pyln.Meter(sr)
        loudness = meter.integrated_loudness(y_trimmed)
        y_norm = pyln.normalize.loudness(y_trimmed, loudness, -23.0)
        
        return y_norm

    def get_convnext_features(self, input_tensor):
        """
        Extract features from the layer before the classifier.
        """
        with torch.no_grad():
            # For ConvNextTiny, we can get the pooled output
            outputs = self.convnext.convnext(input_tensor)
            pooled_output = outputs.pooler_output # Shape: (1, 768)
        return pooled_output

    def predict_hybrid(self, y, sr, forensic_scores):
        """
        Run hybrid inference using ConvNext, Wav2Vec2, and Fusion.
        """
        # 0. Ensure Eval Mode (Protect against state leakage)
        self.convnext.eval()
        self.fusion_model.eval()
        
        # Preprocess
        y = self.preprocess_audio_robust(y, sr)
        
        # 1. ConvNext Branch
        conv_feat, input_tensor = self.convnext_handler.get_features(y, sr)
        
        # 2. Wav2Vec2 Branch
        wav_feat = self.wav2vec_handler.extract_embeddings(y, sr)
        
        # 3. Forensic Features Branch
        # Convert dict to tensor in specific order
        feature_order = [
            "zcr", "spectral_centroid", "spectral_bandwidth", "mfcc_variance", 
            "pitch_variation", "spectral_rolloff", "chroma_consistency", 
            "rms_energy", "jitter", "shimmer", "hnr"
        ]
        foren_feat = torch.tensor([forensic_scores[f]["value"] for f in feature_order], dtype=torch.float32).unsqueeze(0).to(self.device)
        
        # 4. Fusion
        with torch.no_grad():
            logits = self.fusion_model(conv_feat, wav_feat, foren_feat)
            probs = torch.softmax(logits, dim=1)
            pred = torch.argmax(probs, dim=1).item()
            conf = probs[0][pred].item()

        # 5. Visual XAI (Grad-CAM & Integrated Gradients)
        with torch.set_grad_enabled(True):
            heatmap = self.gradcam.generate(input_tensor)
            ig_map = self.xai_manager.compute_integrated_gradients(input_tensor)

        # 6. SHAP & Counterfactuals
        shap_values = self.xai_manager.compute_shap_values(forensic_scores)
        counterfactuals = self.xai_manager.generate_counterfactuals(forensic_scores)

        return {
            "prediction": "fake" if pred == 1 else "real",
            "confidence": conf,
            "heatmap": heatmap,
            "ig_map": ig_map,
            "shap_values": shap_values,
            "counterfactuals": counterfactuals,
            "hybrid_probs": probs.cpu().numpy()
        }

    def predict_with_uncertainty(self, y, sr, num_passes=30):
        input_tensor = generate_spectrogram(y, sr).to(self.device)
        return self.uncertainty_engine.estimate(input_tensor, num_passes)

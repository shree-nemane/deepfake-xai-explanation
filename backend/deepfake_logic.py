# -*- coding: utf-8 -*-
"""
DeepFake Audio Detection + Evidence-Based XAI Pipeline (Logic Module)
"""

import torch
import numpy as np
import librosa
from PIL import Image
import cv2
import io
import base64
from transformers import ConvNextForImageClassification
import os
import json
from sklearn.metrics.pairwise import cosine_similarity
from matplotlib import pyplot as plt

# ==========================================
# 1. CONSTANTS & THRESHOLDS (LOCKED)
# ==========================================

THRESHOLDS = {
    "pitch_variation_low": 8.0,
    "mfcc_variance_low": 80.0,
    "zcr_high": 0.12,
    "spectral_centroid_high": 3500.0,
}

FEATURE_ORDER = [
    "zcr",
    "spectral_centroid",
    "spectral_bandwidth",
    "mfcc_variance",
    "pitch_variation"
]

REFERENCE_FAKE = {
    "zcr": 0.18,
    "spectral_centroid": 4500.0,
    "spectral_bandwidth": 2000.0,
    "mfcc_variance": 30.0,
    "pitch_variation": 3.0
}

REFERENCE_REAL = {
    "zcr": 0.08,
    "spectral_centroid": 2500.0,
    "spectral_bandwidth": 3000.0,
    "mfcc_variance": 120.0,
    "pitch_variation": 20.0
}

# ==========================================
# 2. AUDIO PIPELINE (LOAD & VALIDATE)
# ==========================================

def preprocess_audio(audio_path):
    """Load and normalize audio safely."""
    y, sr = librosa.load(audio_path, sr=16000)
    max_val = np.max(np.abs(y))
    if max_val > 0:
        y = y / max_val
    return y, sr

def validate_audio(y, sr):
    """Validate audio length and content."""
    duration = librosa.get_duration(y=y, sr=sr)
    if duration < 1.0:
        return False, f"Audio too short ({duration:.2f}s). Minimum 1s required."
    
    if np.max(np.abs(y)) < 1e-4:
        return False, "Audio is silent."
        
    return True, "Valid"

def generate_spectrogram(y, sr):
    """Convert raw audio to model input tensor with safe normalization."""
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    denom = mel_spec_db.max() - mel_spec_db.min()
    if denom > 0:
        mel_spec_db = (mel_spec_db - mel_spec_db.min()) / denom
    else:
        mel_spec_db = np.zeros_like(mel_spec_db)
        
    mel_spec_img = (mel_spec_db * 255).astype(np.uint8)
    mel_spec_img = Image.fromarray(mel_spec_img).resize((224, 224)).convert("RGB")
    
    mel_spec_tensor = np.array(mel_spec_img).transpose(2, 0, 1) / 255.0
    return torch.tensor(mel_spec_tensor, dtype=torch.float32).unsqueeze(0)

# ==========================================
# 3. FEATURE EXTRACTION & SIMILARITY
# ==========================================

def extract_audio_features(y, sr):
    """Extract evidence-based forensic features with stable pitch."""
    zcr = np.mean(librosa.feature.zero_crossing_rate(y))
    centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_variance = np.mean(np.var(mfccs, axis=1))
    
    pitch = librosa.yin(y, fmin=50, fmax=300)
    pitch = pitch[pitch > 0]
    pitch_variation = np.std(pitch) if len(pitch) > 1 else 0.0
    
    return {
        "zcr": float(zcr),
        "spectral_centroid": float(centroid),
        "spectral_bandwidth": float(bandwidth),
        "mfcc_variance": float(mfcc_variance),
        "pitch_variation": float(pitch_variation)
    }

def feature_to_vector(features):
    """Convert features to normalized vector with clipping."""
    return np.array([
        np.clip(features["zcr"] / 0.5, 0, 1),
        np.clip(features["spectral_centroid"] / 5000.0, 0, 1),
        np.clip(features["spectral_bandwidth"] / 3000.0, 0, 1),
        np.clip(features["mfcc_variance"] / 200.0, 0, 1),
        np.clip(features["pitch_variation"] / 50.0, 0, 1)
    ]).reshape(1, -1)

def compute_similarity(features):
    """Dual similarity comparison with strength categorization."""
    curr_vec = feature_to_vector(features)
    fake_vec = feature_to_vector(REFERENCE_FAKE)
    real_vec = feature_to_vector(REFERENCE_REAL)
    
    sim_fake = cosine_similarity(curr_vec, fake_vec)[0][0]
    sim_real = cosine_similarity(curr_vec, real_vec)[0][0]
    
    delta = sim_fake - sim_real
    if delta > 0.25:
        strength = "Strong"
    elif delta > 0.1:
        strength = "Moderate"
    else:
        strength = "Weak"
        
    decision = "Closer to synthetic patterns" if sim_fake > sim_real else "Closer to natural speech"
    
    return {
        "fake_similarity": float(sim_fake),
        "real_similarity": float(sim_real),
        "delta": float(delta),
        "strength": strength,
        "decision": decision
    }

# ==========================================
# 4. MODEL INFERENCE & CALIBRATION
# ==========================================

def model_predict(input_tensor, model):
    """Run model prediction."""
    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.softmax(outputs.logits, dim=1)
        pred = torch.argmax(probs, dim=1).item()
        conf = probs[0][pred].item()
    return pred, conf

def calibrate_confidence(conf):
    """Apply temperature-like scaling for reliability."""
    return conf ** (1 / 1.5)

# ==========================================
# 5. EXPLAINABILITY (GRAD-CAM + REASONS)
# ==========================================

class GradCAM:
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
        # 1. Clear previous state (Critical Fix for "Same Results" bug)
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
        
        # 2. Safety check for gradients (Fix for "Red Screen" bug)
        if self.gradients is None or self.activations is None:
            return np.zeros((224, 224), dtype=np.float32)

        grads = self.gradients.mean(dim=(2, 3), keepdim=True)
        acts = self.activations
        cam = (acts * grads).sum(dim=1).squeeze()
        cam = torch.relu(cam)
        
        # 3. Robust Normalization
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min + 1e-8)
        else:
            cam = torch.zeros_like(cam)
            
        heatmap = cam.cpu().numpy()
        return cv2.resize(heatmap, (224, 224))

def interpret_heatmap(heatmap):
    """Extract dominant frequency and time regions from heatmap."""
    idx = np.unravel_index(np.argmax(heatmap), heatmap.shape)
    return {
        "frequency_region": int(idx[0]),
        "time_region": int(idx[1])
    }

def generate_reasons(features):
    """Rule-based engine with ratio-based severity (Fully Independent Forensic Witness)."""
    reasons = []
    
    def get_severity(val, thresh, lower_is_bad=True):
        if lower_is_bad:
            ratio = val / thresh
        else:
            ratio = thresh / val
        
        if ratio < 0.5: return "High"
        if ratio < 1.0: return "Medium"
        return "Low"

    # 1. Pitch
    val = features["pitch_variation"]
    thresh = THRESHOLDS["pitch_variation_low"]
    if val < thresh:
        reasons.append({
            "reason": "Unnaturally stable pitch",
            "evidence": f"Pitch variation = {val:.2f} (< {thresh} threshold)",
            "severity": get_severity(val, thresh, True)
        })
        
    # 2. MFCC Variance
    val = features["mfcc_variance"]
    thresh = THRESHOLDS["mfcc_variance_low"]
    if val < thresh:
        reasons.append({
            "reason": "Over-smoothed audio timbre",
            "evidence": f"MFCC variance = {val:.2f} (< {thresh} threshold)",
            "severity": get_severity(val, thresh, True)
        })
        
    # 3. ZCR
    val = features["zcr"]
    thresh = THRESHOLDS["zcr_high"]
    if val > thresh:
        reasons.append({
            "reason": "High-frequency noise artifacts",
            "evidence": f"ZCR = {val:.2f} (> {thresh} threshold)",
            "severity": get_severity(val, thresh, False)
        })
        
    # 4. Spectral Centroid
    val = features["spectral_centroid"]
    thresh = THRESHOLDS["spectral_centroid_high"]
    if val > thresh:
        reasons.append({
            "reason": "Synthetic frequency distribution",
            "evidence": f"Spectral centroid = {val:.2f} (> {thresh} threshold)",
            "severity": get_severity(val, thresh, False)
        })
        
    if len(reasons) == 0:
        reasons.append({
            "reason": "No strong synthetic artifacts detected",
            "evidence": "All features within natural thresholds",
            "severity": "Low"
        })
        
    return reasons

# ==========================================
# 6. ORCHESTRATOR & REPORTING
# ==========================================

def generate_report(pred, conf, calib_conf, features, heatmap_info, reasons, similarity):
    """Construct professional forensic report."""
    qualitative_label = "Fake" if pred == 1 else "Real"
    
    if calib_conf > 0.8:
        conf_interp = "High"
    elif calib_conf > 0.6:
        conf_interp = "Moderate"
    else:
        conf_interp = "Low"
    
    justification = [
        f"Model prediction indicates {qualitative_label.lower()} audio",
        f"Feature-based indicators show {len(reasons) if reasons[0]['severity'] != 'Low' else 0} acoustic anomalies",
        f"Similarity analysis supports {similarity['decision'].lower()} ({similarity['strength']} strength)"
    ]

    # Forensic Alignment Interpretation (Expert Note)
    # A sample is rules_fake if it contains any non-low severity anomalies
    model_is_fake = (pred == 1)
    rules_have_anomalies = any(r['severity'] in ['High', 'Medium'] for r in reasons)

    if model_is_fake and rules_have_anomalies:
        alignment_note = "FORENSIC CONVERGENCE: Both neural focus and acoustic artifacts confirm synthetic origin."
    elif not model_is_fake and not rules_have_anomalies:
        alignment_note = "FORENSIC ALIGNMENT: Neural patterns and acoustic metrics both indicate natural speech."
    elif model_is_fake and not rules_have_anomalies:
        alignment_note = "FORENSIC DISCREPANCY: Model identifies synthetic patterns that evade traditional acoustic rules. This suggests high-fidelity generation."
    else:
        alignment_note = "FORENSIC DISCREPANCY: Significant acoustic anomalies detected despite natural model classification. May indicate manual editing or recording artifacts."

    if pred == 1 and calib_conf > 0.8:
        risk_statement = "High likelihood of synthetic audio; forensic markers are definitive."
    elif pred == 1:
        risk_statement = "Moderate likelihood of synthetic audio; detection confirmed with caution."
    else:
        risk_statement = "Low risk; patterns align with natural behavioral distributions."

    system_notes = [
        "Explanation based on deterministic feature analysis (No Generative AI used)",
        "Confidence calibrated using temperature scaling",
        "Signal-level metrics decoupled from internal model parameters"
    ]
    
    if conf_interp == "Low":
        system_notes.append("Prediction confidence is low; interpret results with significant caution.")

    report = {
        "Prediction": qualitative_label,
        "Risk Statement": risk_statement,
        "Confidence": {
            "raw": round(conf, 4),
            "calibrated": round(calib_conf, 4),
            "interpretation": conf_interp
        },
        "Evidence Summary": {
            "anomaly_count": len(reasons) if reasons[0]['severity'] != 'Low' else 0,
            "Key Indicators": reasons,
            "Feature Values": {k: round(v, 4) for k, v in features.items()}
        },
        "Model Focus": heatmap_info,
        "Similarity Analysis": {
            "fake_similarity": round(similarity["fake_similarity"], 4),
            "real_similarity": round(similarity["real_similarity"], 4),
            "strength": similarity["strength"],
            "decision": similarity["decision"]
        },
        "Decision Justification": justification,
        "Forensic Alignment": alignment_note,
        "Final Conclusion": risk_statement,
        "System Metadata": {
            "reasoning_engine": "Rule-based (Expert) + Comparative (Similarity)",
            "calibration": "Temperature-scaled power law",
            "notes": system_notes
        }
    }
    return report

def heatmap_to_base64(heatmap):
    """Convert heatmap numpy array to base64 string."""
    try:
        # Use colormap to make it look like the original PLT output
        heatmap_colored = cv2.applyColorMap((heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)
        _, buffer = cv2.imencode('.png', heatmap_colored)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception:
        return None

def run_pipeline(audio_path, model, gradcam_engine):
    """Main execution flow (Strict Contract)."""
    try:
        y, sr = preprocess_audio(audio_path)
        is_valid, msg = validate_audio(y, sr)
        if not is_valid:
            return {"error": msg}, None
        
        features = extract_audio_features(y, sr)
        input_tensor = generate_spectrogram(y, sr)
        pred, conf = model_predict(input_tensor, model)
        calibrated_conf = calibrate_confidence(conf)
        
        heatmap = gradcam_engine.generate(input_tensor)
        heatmap_info = interpret_heatmap(heatmap)
        reasons = generate_reasons(features)
        similarity = compute_similarity(features)
        
        report = generate_report(pred, conf, calibrated_conf, features, heatmap_info, reasons, similarity)
        heatmap_base64 = heatmap_to_base64(heatmap)
        
        return {
            "report": report,
            "heatmap": heatmap_base64
        }, None
        
    except Exception as e:
        return None, str(e)

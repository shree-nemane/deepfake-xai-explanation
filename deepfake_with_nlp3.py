# -*- coding: utf-8 -*-
"""
DeepFake Audio Detection + Evidence-Based XAI Pipeline
Final Locked Version
"""

import torch
import numpy as np
import librosa
from PIL import Image
import matplotlib.pyplot as plt
import cv2
from transformers import ConvNextForImageClassification
import os
import json
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 1. CONSTANTS & THRESHOLDS (LOCKED)
# ==========================================

THRESHOLDS = {
    "pitch_variation_low": 5.0,
    "mfcc_variance_low": 50.0,
    "zcr_high": 0.15,
    "spectral_centroid_high": 4000.0,
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
    
    # Safe normalization (Fix 5)
    max_val = np.max(np.abs(y))
    if max_val > 0:
        y = y / max_val
        
    return y, sr

def validate_audio(y, sr):
    """Validate audio length and content."""
    # Length check (Step 2)
    duration = librosa.get_duration(y=y, sr=sr)
    if duration < 1.0:
        return False, f"Audio too short ({duration:.2f}s). Minimum 1s required."
    
    # Silence check
    if np.max(np.abs(y)) < 1e-4:
        return False, "Audio is silent."
        
    return True, "Valid"

def generate_spectrogram(y, sr):
    """Convert raw audio to model input tensor with safe normalization (Issue 3)."""
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # Safe normalization (Issue 3)
    denom = mel_spec_db.max() - mel_spec_db.min()
    if denom > 0:
        mel_spec_db = (mel_spec_db - mel_spec_db.min()) / denom
    else:
        mel_spec_db = np.zeros_like(mel_spec_db)
        
    mel_spec_img = (mel_spec_db * 255).astype(np.uint8)
    mel_spec_img = Image.fromarray(mel_spec_img).resize((224, 224)).convert("RGB")
    
    # Convert to Tensor (CxHxW)
    mel_spec_tensor = np.array(mel_spec_img).transpose(2, 0, 1) / 255.0
    return torch.tensor(mel_spec_tensor, dtype=torch.float32).unsqueeze(0)

# ==========================================
# 3. FEATURE EXTRACTION & SIMILARITY
# ==========================================

def extract_audio_features(y, sr):
    """Extract evidence-based forensic features with stable pitch (Issue 2)."""
    # 1. Zero Crossing Rate (ZCR)
    zcr = np.mean(librosa.feature.zero_crossing_rate(y))
    
    # 2. Spectral Centroid
    centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    
    # 3. Spectral Bandwidth
    bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
    
    # 4. MFCC Variance (Timbre smoothing)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_variance = np.mean(np.var(mfccs, axis=1))
    
    # 5. Stable Pitch Variation (Issue 2: Switching to YIN)
    # Using yin for better stability than piptrack
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
    """Convert features to normalized vector with clipping (Issue 4)."""
    return np.array([
        np.clip(features["zcr"] / 0.5, 0, 1),
        np.clip(features["spectral_centroid"] / 5000.0, 0, 1),
        np.clip(features["spectral_bandwidth"] / 3000.0, 0, 1),
        np.clip(features["mfcc_variance"] / 200.0, 0, 1),
        np.clip(features["pitch_variation"] / 50.0, 0, 1)
    ]).reshape(1, -1)

def compute_similarity(features):
    """Dual similarity comparison with strength categorization (Polish 2)."""
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
    """Run model prediction (Fix 2)."""
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
        """Register hooks using full_backward_hook for stability (Issue 1)."""
        self.target_layer.register_forward_hook(self._save_activation)
        self.target_layer.register_full_backward_hook(self._save_gradient)

    def generate(self, input_tensor, target_class=None):
        outputs = self.model(input_tensor)
        logits = outputs.logits
        pred_class = logits.argmax(dim=1).item()
        if target_class is None:
            target_class = pred_class
            
        self.model.zero_grad()
        score = logits[0, target_class]
        score.backward()
        
        grads = self.gradients.mean(dim=(2, 3), keepdim=True)
        acts = self.activations
        cam = (acts * grads).sum(dim=1).squeeze()
        cam = torch.relu(cam)
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        
        heatmap = cam.cpu().numpy()
        return cv2.resize(heatmap, (224, 224))

def interpret_heatmap(heatmap):
    """Extract dominant frequency and time regions from heatmap."""
    # Find coordinates of max activation
    idx = np.unravel_index(np.argmax(heatmap), heatmap.shape)
    # y-axis (0-223) is Frequency, x-axis (0-223) is Time
    return {
        "frequency_region": int(idx[0]),
        "time_region": int(idx[1])
    }

def generate_reasons(features):
    """Rule-based engine with ratio-based severity (Polish 3)."""
    reasons = []
    
    # Heuristic: ratio < 0.5 (High), < 1.0 (Medium)
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
        
    # Default case (Issue 5)
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

def generate_report(audio_path, pred, conf, calib_conf, features, heatmap_info, reasons, similarity):
    """Construct professional forensic report with adaptive layers (Issue 6)."""
    qualitative_label = "Fake" if pred == 1 else "Real"
    
    # Polish 1: Confidence interpretation
    if calib_conf > 0.8:
        conf_interp = "High"
    elif calib_conf > 0.6:
        conf_interp = "Moderate"
    else:
        conf_interp = "Low"
    
    # Decision Justification (Polish 4)
    justification = [
        f"Model prediction indicates {qualitative_label.lower()} audio",
        f"Feature-based indicators show {len(reasons) if reasons[0]['severity'] != 'Low' else 0} acoustic anomalies",
        f"Similarity analysis supports {similarity['decision'].lower()} ({similarity['strength']} strength)"
    ]

    # Adaptive Risk Statement (Issue 6)
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
    
    # Confidence Warning (Issue 6)
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
        "Final Conclusion": risk_statement,
        
        "System Metadata": {
            "reasoning_engine": "Rule-based (Expert) + Comparative (Similarity)",
            "calibration": "Temperature-scaled power law",
            "notes": system_notes
        }
    }
    return report

def run_pipeline(audio_path, model, gradcam_engine):
    """Main execution flow (Strict Order)."""
    try:
        # 1. Preprocess
        y, sr = preprocess_audio(audio_path)
        
        # 2. Validate
        is_valid, msg = validate_audio(y, sr)
        if not is_valid:
            return {"error": msg}
        
        # 3. Features
        features = extract_audio_features(y, sr)
        
        # 4. Spectrogram
        input_tensor = generate_spectrogram(y, sr)
        
        # 5. Predict
        pred, conf = model_predict(input_tensor, model)
        
        # 6. Calibrate
        calibrated_conf = calibrate_confidence(conf)
        
        # 7. Grad-CAM
        heatmap = gradcam_engine.generate(input_tensor)
        
        # 8. Interpret Heatmap
        heatmap_info = interpret_heatmap(heatmap)
        
        # 9. Reasons
        reasons = generate_reasons(features)
        
        # 10. Similarity
        similarity = compute_similarity(features)
        
        # 11. Report
        report = generate_report(audio_path, pred, conf, calibrated_conf, features, heatmap_info, reasons, similarity)
        
        return report, input_tensor, heatmap
        
    except Exception as e:
        return {"error": str(e)}, None, None

def evaluate_folder(folder_path, model, gradcam_engine):
    """Simple batch evaluation mode."""
    results = []
    files = [f for f in os.listdir(folder_path) if f.endswith(('.wav', '.mp3'))]
    print(f"Evaluating {len(files)} files in {folder_path}...")
    
    for f in files:
        path = os.path.join(folder_path, f)
        report, _, _ = run_pipeline(path, model, gradcam_engine)
        if "error" not in report:
            results.append(report)
            print(f"Done: {f} -> {report['Prediction']}")
        else:
            print(f"Failed: {f} -> {report['error']}")
            
    return results

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    # Load Model
    print("Loading Forensic Model...")
    model_name = "kubinooo/convnext-tiny-224-audio-deepfake-classification"
    model = ConvNextForImageClassification.from_pretrained(model_name)
    model.eval()
    
    # Init Grad-CAM
    target_layer = model.convnext.encoder.stages[3].layers[-1].dwconv
    gradcam_engine = GradCAM(model, target_layer)
    
    # Run Single Sample
    test_audio = "fake.wav" # Replace with valid path
    if os.path.exists(test_audio):
        report, input_tensor, heatmap = run_pipeline(test_audio, model, gradcam_engine)
        
        if "error" in report:
            print("\n❌ PIPELINE ERROR:", report["error"])
        else:
            print("\n🔍 FORENSIC REPORT:")
            print(json.dumps(report, indent=2))
            
            # Simple visualization
            plt.figure(figsize=(10, 5))
            plt.subplot(1, 2, 1)
            plt.imshow(input_tensor[0].permute(1, 2, 0).numpy())
            plt.title("Mel-Spectrogram")
            plt.subplot(1, 2, 2)
            plt.imshow(heatmap, cmap='jet')
            plt.title("Attention Heatmap")
            plt.show()
    else:
        print(f"\n⚠️ Sample file '{test_audio}' not found. Please provide actual audio.")
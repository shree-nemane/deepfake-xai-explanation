import base64
import numpy as np
import librosa
import torch
import cv2

def extract_all_features(y, sr):
    """
    Extract comprehensive forensic features with temporal resolution.
    """
    features = {}
    
    # 1. ZCR (Temporal)
    zcr_series = librosa.feature.zero_crossing_rate(y)[0]
    features["zcr"] = float(np.mean(zcr_series))
    features["zcr_series"] = zcr_series.tolist()
    
    # 2. Spectral Centroid (Temporal)
    centroid_series = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    features["spectral_centroid"] = float(np.mean(centroid_series))
    features["spectral_centroid_series"] = centroid_series.tolist()
    
    # ... (Other features)
    
    # 3. Spectral Bandwidth
    features["spectral_bandwidth"] = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
    
    # 4. MFCCs and Variance
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_var_series = np.var(mfccs, axis=0)
    features["mfcc_variance"] = float(np.mean(mfcc_var_series))
    features["mfcc_var_series"] = mfcc_var_series.tolist()
    
    # 5. Pitch Variation (YIN)
    pitch = librosa.yin(y, fmin=50, fmax=300)
    # Map pitch to series (preserving length)
    features["pitch_series"] = pitch.tolist()
    pitch_clean = pitch[pitch > 0]
    features["pitch_variation"] = float(np.std(pitch_clean)) if len(pitch_clean) > 1 else 0.0
    
    # 6. Spectral Rolloff
    features["spectral_rolloff"] = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
    
    # 7. Chroma STFT
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    features["chroma_consistency"] = float(np.mean(np.var(chroma, axis=1)))
    
    # 8. Root Mean Square (RMS) Energy
    rms = librosa.feature.rms(y=y)
    features["rms_energy"] = float(np.mean(rms))
    
    # 9. Simple Jitter/Shimmer approximations (since we don't have parselmouth easily available)
    # Jitter: average absolute difference between consecutive fundamental frequencies
    if len(pitch) > 1:
        features["jitter"] = float(np.mean(np.abs(np.diff(pitch))))
    else:
        features["jitter"] = 0.0
        
    # Shimmer: average absolute difference between consecutive peak amplitudes
    # We can use the RMS envelope as a proxy
    if len(rms[0]) > 1:
        features["shimmer"] = float(np.mean(np.abs(np.diff(rms[0]))))
    else:
        features["shimmer"] = 0.0

    # 10. Harmonic-to-Noise Ratio (HNR) - approximation using harmonic/percussive source separation
    harmonic, percussive = librosa.effects.hpss(y)
    harm_power = np.mean(harmonic**2)
    perc_power = np.mean(percussive**2)
    features["hnr"] = float(10 * np.log10(harm_power / (perc_power + 1e-8))) if perc_power > 0 else 0.0

    return features

def mel_spectrogram_preview_base64(y, sr, width=320, height=160):
    """PNG preview of mel spectrogram for UI (viridis colormap)."""
    if y is None or len(y) < max(int(sr * 0.08), 1):
        return None
    try:
        mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64, fmax=8000)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        denom = mel_db.max() - mel_db.min()
        if denom > 0:
            mel_db = (mel_db - mel_db.min()) / denom
        else:
            mel_db = np.zeros_like(mel_db)
        img = (mel_db * 255).astype(np.uint8)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
        colored = cv2.applyColorMap(img, cv2.COLORMAP_VIRIDIS)
        _, buffer = cv2.imencode(".png", colored)
        return base64.b64encode(buffer).decode("utf-8")
    except Exception:
        return None


def generate_spectrogram(y, sr, size=(224, 224)):
    """Convert raw audio to model input tensor."""
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # Normalization
    denom = mel_spec_db.max() - mel_spec_db.min()
    if denom > 0:
        mel_spec_db = (mel_spec_db - mel_spec_db.min()) / denom
    else:
        mel_spec_db = np.zeros_like(mel_spec_db)
        
    # Resize and convert to tensor
    import cv2
    img = (mel_spec_db * 255).astype(np.uint8)
    img = cv2.resize(img, size)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    tensor = img_rgb.transpose(2, 0, 1) / 255.0
    tensor = torch.tensor(tensor, dtype=torch.float32)
    
    # Apply ImageNet normalization expected by ConvNext
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    tensor = (tensor - mean) / std
    
    return tensor.unsqueeze(0)

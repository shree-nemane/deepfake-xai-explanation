import os
import librosa
import soundfile as sf
import numpy as np

def generate_mock_audio():
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'mock_dataset', 'audio')
    os.makedirs(base_dir, exist_ok=True)
    
    real_path = os.path.join(base_dir, 'real.wav')
    fake_path = os.path.join(base_dir, 'fake.wav')
    
    print("Generating real speech sample using librosa built-in 'libri1'...")
    try:
        # 'libri1' is a short speech clip
        y_real, sr = librosa.load(librosa.ex('libri1'), sr=16000)
        sf.write(real_path, y_real, sr)
        print(f"Saved real audio to {real_path}")
    except Exception as e:
        print(f"Failed to generate real audio: {e}")

    print("Generating fake speech sample...")
    try:
        # We use 'libri2' and apply a robotic pitch shift and some noise to simulate a bad deepfake
        y_base, sr = librosa.load(librosa.ex('libri2'), sr=16000)
        
        # Add slight white noise
        noise = np.random.normal(0, 0.005, len(y_base))
        y_fake = y_base + noise
        
        # Pitch shift slightly (using simple resampling/speedup for distortion)
        y_fake = librosa.effects.pitch_shift(y_fake, sr=sr, n_steps=2.5)
        
        sf.write(fake_path, y_fake, sr)
        print(f"Saved fake audio to {fake_path}")
    except Exception as e:
        print(f"Failed to generate fake audio: {e}")

if __name__ == "__main__":
    generate_mock_audio()

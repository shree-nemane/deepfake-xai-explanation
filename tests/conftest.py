import os
import pytest
import librosa
import numpy as np

MOCK_AUDIO_DIR = os.path.join(os.path.dirname(__file__), '..', 'mock_dataset', 'audio')

@pytest.fixture
def real_audio_path():
    path = os.path.join(MOCK_AUDIO_DIR, 'real.wav')
    if not os.path.exists(path):
        pytest.skip(f"Mock real audio not found at {path}")
    return path

@pytest.fixture
def fake_audio_path():
    path = os.path.join(MOCK_AUDIO_DIR, 'fake.wav')
    if not os.path.exists(path):
        pytest.skip(f"Mock fake audio not found at {path}")
    return path

@pytest.fixture
def real_audio_data(real_audio_path):
    # Load at 16k for standard processing
    y_16k, _ = librosa.load(real_audio_path, sr=16000)
    y_48k, _ = librosa.load(real_audio_path, sr=48000)
    return y_16k, y_48k

@pytest.fixture
def fake_audio_data(fake_audio_path):
    y_16k, _ = librosa.load(fake_audio_path, sr=16000)
    y_48k, _ = librosa.load(fake_audio_path, sr=48000)
    return y_16k, y_48k

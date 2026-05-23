import os

class Config:
    # Phonetic engine
    PHONETIC_ENGINE = os.getenv("PHONETIC_ENGINE", "wavlm")
    
    # Paths
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///forensic_intelligence.db")
    
    # Audio settings
    TARGET_LUFS = -23.0
    WINDOW_DURATION_SEC = 2.0
    WINDOW_OVERLAP = 0.5

config = Config()

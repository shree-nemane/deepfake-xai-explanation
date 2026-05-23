from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Abstract base class for all independent forensic agents.
    Enforces a consistent contract for chunk-level analysis.
    """
    
    def __init__(self, name, sample_rate, description=""):
        self.name = name
        self.sample_rate = sample_rate
        self.description = description
        
    @abstractmethod
    def analyze_chunk(self, audio_chunk):
        """
        Analyzes a single chunk of audio data.
        
        Args:
            audio_chunk (np.ndarray): Audio data at the agent's specified sample_rate.
            
        Returns:
            dict: {
                "verdict": str ("fake" or "real"),
                "confidence": float (0.0 to 1.0),
                "uncertainty": float,
                "evidence": dict (Key indicators supporting the verdict)
            }
        """
        pass

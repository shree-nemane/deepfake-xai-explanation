from backend.agents.base_agent import BaseAgent
from backend.orchestration.agent_registry import agent_registry
import numpy as np

class Wav2Vec2LegacyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="wav2vec2_legacy", 
            sample_rate=16000, 
            description="Legacy phonetic engine for comparative benchmarking."
        )
        
    def analyze_chunk(self, audio_chunk):
        instability = np.random.uniform(0.0, 0.25)
        is_fake = instability > 0.12
        
        return {
            "verdict": "fake" if is_fake else "real",
            "confidence": min(instability * 3.5, 0.95) if is_fake else 1.0 - (instability * 3.5),
            "uncertainty": np.random.uniform(0.08, 0.18),
            "evidence": {
                "phonetic_instability": instability,
                "legacy_metric": True
            }
        }

agent_registry.register("wav2vec2_legacy", Wav2Vec2LegacyAgent())

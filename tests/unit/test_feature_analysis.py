import pytest
import numpy as np

def test_feature_analysis_all_agents(real_audio_data, fake_audio_data):
    """
    Test that all registered agents can process a chunk of real and fake audio
    without crashing and return a correctly formatted dictionary.
    """
    from backend.orchestration.agent_registry import agent_registry
    import backend.agents  # triggers registration
    
    y_real_16k, y_real_48k = real_audio_data
    y_fake_16k, y_fake_48k = fake_audio_data
    
    # We take the first 1-second chunk
    chunk_real_16k = y_real_16k[:16000] if len(y_real_16k) >= 16000 else np.pad(y_real_16k, (0, 16000 - len(y_real_16k)))
    chunk_real_48k = y_real_48k[:48000] if len(y_real_48k) >= 48000 else np.pad(y_real_48k, (0, 48000 - len(y_real_48k)))
    
    chunk_fake_16k = y_fake_16k[:16000] if len(y_fake_16k) >= 16000 else np.pad(y_fake_16k, (0, 16000 - len(y_fake_16k)))
    chunk_fake_48k = y_fake_48k[:48000] if len(y_fake_48k) >= 48000 else np.pad(y_fake_48k, (0, 48000 - len(y_fake_48k)))
    
    agents = agent_registry.get_all_agents()
    assert len(agents) > 0, "No agents found in registry"
    
    for agent in agents:
        sr = getattr(agent, 'sample_rate', 16000)
        target_real_chunk = chunk_real_16k if sr == 16000 else chunk_real_48k
        target_fake_chunk = chunk_fake_16k if sr == 16000 else chunk_fake_48k
        
        # Test real
        result_real = agent.analyze_chunk(target_real_chunk)
        assert "verdict" in result_real
        assert "confidence" in result_real
        assert result_real["verdict"] in ["real", "fake", "inconclusive", "reliable", "unreliable"]
        
        # Test fake
        result_fake = agent.analyze_chunk(target_fake_chunk)
        assert "verdict" in result_fake
        assert "confidence" in result_fake
        assert result_fake["verdict"] in ["real", "fake", "inconclusive", "reliable", "unreliable"]


import pytest
from backend.orchestration.forensic_orchestrator import ForensicOrchestrator

def test_pipeline_real_audio(real_audio_data):
    """Test the full analysis pipeline on real audio."""
    y_16k, y_48k = real_audio_data
    
    orchestrator = ForensicOrchestrator()
    results = orchestrator.analyze_audio(y_16k, y_48k)
    
    assert "agent_results" in results
    assert "chunk_consensus" in results
    assert "global_consensus" in results
    
    # We assert it produces a verdict (real, fake, or inconclusive)
    # Since deep-learning models might output anything for a short random sample, we don't strictly assert "real" here
    # but we ensure the pipeline executes successfully without exceptions.
    global_consensus = results["global_consensus"]
    assert global_consensus["verdict"] in ["real", "fake", "inconclusive"]
    assert "confidence" in global_consensus
    assert "convergence_strength" in global_consensus

def test_pipeline_fake_audio(fake_audio_data):
    """Test the full analysis pipeline on fake audio."""
    y_16k, y_48k = fake_audio_data
    
    orchestrator = ForensicOrchestrator()
    results = orchestrator.analyze_audio(y_16k, y_48k)
    
    assert "agent_results" in results
    assert "chunk_consensus" in results
    assert "global_consensus" in results
    
    global_consensus = results["global_consensus"]
    assert global_consensus["verdict"] in ["real", "fake", "inconclusive"]
    assert "confidence" in global_consensus
    assert "convergence_strength" in global_consensus

def test_api_analysis_endpoint(fake_audio_path):
    """Test the FastAPI POST /analyze/ route and verify the complete JSON output contract."""
    from fastapi.testclient import TestClient
    from backend.app import app
    
    client = TestClient(app)
    with open(fake_audio_path, "rb") as f:
        response = client.post("/analyze/", files={"file": ("fake.wav", f, "audio/wav")})
    
    assert response.status_code == 200
    data = response.json()
    
    # 1. Assert Global Consensus Uncertainty & Probability Margin
    assert "consensus" in data
    consensus = data["consensus"]
    assert "verdict" in consensus
    assert "confidence" in consensus
    assert "uncertainty" in consensus
    assert isinstance(consensus["uncertainty"], float)
    assert "convergence_strength" in consensus
    assert "fake_probability" in consensus
    assert "real_probability" in consensus
    
    # 2. Assert Timeline event_type casing (should be lowercase value)
    assert "timeline" in data
    timeline = data["timeline"]
    if timeline:
        for event in timeline:
            assert "event_type" in event
            # event_type values should be lowercase
            assert event["event_type"].islower()
            
    # 3. Assert nested processing metadata structure
    assert "processing_metadata" in data
    metadata = data["processing_metadata"]
    assert metadata["chunk_duration"] == 2.0
    assert metadata["overlap"] == 0.5
    assert metadata["pipeline_version"] == "forensic_pipeline_v1"
    assert metadata["schema_version"] == "v2.0"
    assert "sample_rates" in metadata
    assert metadata["sample_rates"]["semantic"] == 16000
    assert metadata["sample_rates"]["forensic"] == 48000

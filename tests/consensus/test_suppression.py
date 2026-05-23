import pytest
import math
from backend.consensus.consensus_engine import ConsensusEngine
from backend.persistence.database import (
    Base, Report, ConsensusEvent, XAIArtifact, NarrativeReport, EventAgentDetails, ConsensusEventType, ProcessingMetadata, engine, SessionLocal
)

def test_sigmoid_suppression_math():
    engine = ConsensusEngine()
    
    # Tier 1: Reliability >= 0.80 -> Full Contribution (1.0)
    assert engine._get_sigmoid_suppression(0.85) == 1.0
    assert engine._get_sigmoid_suppression(0.80) == 1.0
    
    # Tier 5: Reliability < 0.20 -> Fail-Closed Mute (0.0)
    assert engine._get_sigmoid_suppression(0.18) == 0.0
    assert engine._get_sigmoid_suppression(0.19) == 0.0
    
    # Intermediate Tier: 0.50 -> Exactly 0.50
    assert math.isclose(engine._get_sigmoid_suppression(0.50), 0.50, abs_tol=1e-5)
    
    # Sigmoid monotonicity and bounds check
    for r in [0.25, 0.35, 0.45, 0.60, 0.75]:
        val = engine._get_sigmoid_suppression(r)
        assert 0.0 <= val <= 1.0
        # Assert S-curve properties (growth is monotonic)
        assert engine._get_sigmoid_suppression(r - 0.05) < val

def test_agent_specific_suppression_logic():
    engine = ConsensusEngine()
    
    # Base clean metrics
    clean_metrics = {
        "snr_db": 30.0,
        "clipping_ratio": 0.0,
        "spectral_flatness": 0.0,
        "rms_energy": 0.05
    }
    
    # Convnext should be sensitive to flat spectral compression artifacts
    compressed_metrics = {
        "snr_db": 30.0,
        "clipping_ratio": 0.0,
        "spectral_flatness": 0.5, # compression artifacts proxy
        "rms_energy": 0.05
    }
    assert engine._calculate_agent_suppression("convnext", clean_metrics) == 1.0
    assert engine._calculate_agent_suppression("convnext", compressed_metrics) == 0.0

    # WavLM should be sensitive to low SNR noise
    noisy_metrics = {
        "snr_db": 5.0, # high noise
        "clipping_ratio": 0.0,
        "spectral_flatness": 0.0,
        "rms_energy": 0.05
    }
    assert engine._calculate_agent_suppression("wavlm", clean_metrics) == 1.0
    assert engine._calculate_agent_suppression("wavlm", noisy_metrics) == 0.0

    # Acoustic should be sensitive to clipping
    clipped_metrics = {
        "snr_db": 30.0,
        "clipping_ratio": 0.05, # high clipping
        "spectral_flatness": 0.0,
        "rms_energy": 0.05
    }
    assert engine._calculate_agent_suppression("acoustic", clean_metrics) == 1.0
    assert engine._calculate_agent_suppression("acoustic", clipped_metrics) == 0.0

    # AASIST should be sensitive to compound waveform distortions (both clipping and noise)
    assert engine._calculate_agent_suppression("aasist", clean_metrics) == 1.0
    assert engine._calculate_agent_suppression("aasist", noisy_metrics) == 0.0
    assert engine._calculate_agent_suppression("aasist", clipped_metrics) == 0.0

def test_mathematical_uncertainty_propagation():
    engine = ConsensusEngine()
    
    # Global reliability = 0.50 -> raw uncertainty (e.g. 0.20) scales by 1 + 2(1 - 0.5) = 2.0x
    agent_results = {
        "wavlm": {"verdict": "fake", "confidence": 0.90, "uncertainty": 0.20},
        "reliability": {
            "evidence": {
                "snr_db": 30.0,
                "clipping_ratio": 0.0,
                "spectral_flatness": 0.0,
                "rms_energy": 0.05
            }
        }
    }
    
    res = engine.evaluate_chunk_consensus(agent_results, global_reliability=0.50)
    details = res["calibrated_details"]["wavlm"]
    
    # Uncertainty doubles under beta=2.0 scaling from base calibrated uncertainty
    base_unc = 0.20 + (1.0 - 0.90 * 0.5) * 0.5 # calibrates base uncertainty
    expected_unc = min(1.0, base_unc * (1.0 + 2.0 * (1.0 - 0.5)))
    assert math.isclose(details["adjusted_uncertainty"], expected_unc, abs_tol=1e-5)

def test_database_schema_and_enums():
    # Setup standard SQLite connection in-memory for isolated test
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    test_engine = create_engine("sqlite:///:memory:")
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    
    try:
        # 1. Create Report
        report = Report(filename="forensic_test.wav", schema_version="v2.0")
        db.add(report)
        db.commit()
        db.refresh(report)
        assert report.id is not None
        
        # 2. Create NarrativeReport
        narrative = NarrativeReport(
            report_id=report.id,
            structured_summary="Structured deterministic text summarized.",
            human_summary="Human-friendly narrative text.",
            narrative_metadata={"version": "1.0"},
            generated_by="NarrativeTestEngine",
            narrative_version="v1"
        )
        db.add(narrative)
        
        # 3. Create XAIArtifact with Native JSON
        xai = XAIArtifact(
            report_id=report.id,
            shap_values={"segment_1": 0.85},
            counterfactuals={"shift_point": 0.42},
            evidence_graph={"L1": "input", "L2": "cons"},
            shap_summary="Long shapley summary detail text...",
            counterfactual_summary="Analytical gradient text...",
            xai_version="v1"
        )
        db.add(xai)
        
        # 4. Create Enum-safe ConsensusEvent
        event = ConsensusEvent(
            report_id=report.id,
            event_type=ConsensusEventType.CONTRADICTION,
            description="Contradiction detected at segment.",
            involved_agents=["wavlm", "convnext"],
            agent_snapshot={"wavlm": "fake", "convnext": "real"},
            diagnostic_metrics={"snr_db": 30.0, "clipping_ratio": 0.0}
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        
        # 5. Create EventAgentDetails child details
        details = EventAgentDetails(
            event_id=event.id,
            agent_name="wavlm",
            agent_version="WavLM-v1",
            verdict="fake",
            confidence=0.91,
            uncertainty=0.09,
            adjusted_confidence=0.88,
            suppression_factor=0.95,
            temporal_region={"start": 0.0, "end": 2.0}
        )
        db.add(details)
        
        # 6. Create ProcessingMetadata
        metadata = ProcessingMetadata(
            report_id=report.id,
            chunk_duration=2.0,
            overlap=0.5,
            semantic_sr=16000,
            forensic_sr=48000,
            pipeline_version="forensic_pipeline_v1"
        )
        db.add(metadata)
        db.commit()
        
        # Cascades and relations assertions
        retrieved_report = db.query(Report).filter(Report.id == report.id).first()
        assert retrieved_report.schema_version == "v2.0"
        assert retrieved_report.processing_metadata.pipeline_version == "forensic_pipeline_v1"
        assert retrieved_report.narrative_report.structured_summary == "Structured deterministic text summarized."
        
        retrieved_event = db.query(ConsensusEvent).filter(ConsensusEvent.id == event.id).first()
        assert retrieved_event.event_type == ConsensusEventType.CONTRADICTION
        assert retrieved_event.agent_snapshot == {"wavlm": "fake", "convnext": "real"}
        assert retrieved_event.diagnostic_metrics == {"snr_db": 30.0, "clipping_ratio": 0.0}
        assert retrieved_event.event_agent_details[0].agent_name == "wavlm"
        assert retrieved_event.event_agent_details[0].agent_version == "WavLM-v1"
        
        # Test foreign key cascade deletion
        db.delete(retrieved_report)
        db.commit()
        
        # Cascade should orphaned-delete child detail tables
        assert db.query(NarrativeReport).filter(NarrativeReport.report_id == report.id).first() is None
        assert db.query(ConsensusEvent).filter(ConsensusEvent.report_id == report.id).first() is None
        assert db.query(EventAgentDetails).filter(EventAgentDetails.event_id == event.id).first() is None
        assert db.query(ProcessingMetadata).filter(ProcessingMetadata.report_id == report.id).first() is None

    finally:
        db.close()

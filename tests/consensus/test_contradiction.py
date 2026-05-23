"""
Phase 2 UAT Tests: Contradiction Warning Heuristics (D-01, D-02, D-03)
Tests structured threat warning generation, short-circuit logic,
event classification, and database persistence.
"""
import pytest
import math
from backend.consensus.consensus_engine import ConsensusEngine
from backend.persistence.database import (
    Base, Report, ConsensusEvent, EventAgentDetails, ConsensusEventType, SessionLocal
)


# ─── Fixtures ───────────────────────────────────────────────────────────────

CLEAN_METRICS = {
    "snr_db": 30.0,
    "clipping_ratio": 0.0,
    "spectral_flatness": 0.0,
    "rms_energy": 0.05,
    "reliability_score": 0.90,
}


def _make_agent_results(**overrides):
    """Build agent_results dict with defaults for clean-signal reliability."""
    base = {
        "reliability": {"evidence": CLEAN_METRICS},
    }
    for name, spec in overrides.items():
        base[name] = {
            "verdict": spec[0],
            "confidence": spec[1],
            "uncertainty": 0.10,
        }
    return base


def _run_consensus(agent_results, reliability=0.90):
    """Helper that runs evaluate_chunk_consensus and returns result."""
    engine = ConsensusEngine()
    return engine.evaluate_chunk_consensus(agent_results, global_reliability=reliability)


# ═══════════════════════════════════════════════════════════════════════════
# D-01: Voice Clone Threat
# ═══════════════════════════════════════════════════════════════════════════

class TestVoiceCloneThreat:
    """D-01: wavlm fake ≥0.70, acoustic/convnext real ≥0.70"""

    def test_voice_clone_wavlm_vs_acoustic(self):
        """wavlm=fake@0.85, acoustic=real@0.80 → voice_clone warning"""
        results = _make_agent_results(
            wavlm=("fake", 0.85),
            acoustic=("real", 0.80),
        )
        res = _run_consensus(results)
        warnings = res["threat_warnings"]
        assert len(warnings) >= 1
        assert warnings[0]["threat_type"] == "voice_clone"
        assert warnings[0]["severity"] == "high"
        assert "wavlm" in warnings[0]["triggering_agents"]
        assert "acoustic" in warnings[0]["triggering_agents"]

    def test_voice_clone_wavlm_vs_convnext(self):
        """wavlm=fake@0.75, convnext=real@0.72 → voice_clone warning"""
        results = _make_agent_results(
            wavlm=("fake", 0.75),
            convnext=("real", 0.72),
        )
        res = _run_consensus(results)
        warnings = res["threat_warnings"]
        assert len(warnings) >= 1
        assert warnings[0]["threat_type"] == "voice_clone"
        assert "convnext" in warnings[0]["triggering_agents"]

    def test_voice_clone_both_acoustic_and_convnext(self):
        """wavlm=fake@0.80, acoustic=real@0.75, convnext=real@0.72 → single voice_clone with both triggers"""
        results = _make_agent_results(
            wavlm=("fake", 0.80),
            acoustic=("real", 0.75),
            convnext=("real", 0.72),
        )
        res = _run_consensus(results)
        warnings = [w for w in res["threat_warnings"] if w["threat_type"] == "voice_clone"]
        assert len(warnings) == 1
        assert "acoustic" in warnings[0]["triggering_agents"]
        assert "convnext" in warnings[0]["triggering_agents"]

    def test_no_voice_clone_below_threshold(self):
        """wavlm=fake@0.65 (below 0.70) → no voice_clone warning"""
        results = _make_agent_results(
            wavlm=("fake", 0.65),
            acoustic=("real", 0.80),
        )
        res = _run_consensus(results)
        voice_clone_warnings = [w for w in res["threat_warnings"] if w["threat_type"] == "voice_clone"]
        assert len(voice_clone_warnings) == 0

    def test_no_voice_clone_when_both_fake(self):
        """wavlm=fake, acoustic=fake → no contradiction → no voice_clone warning"""
        results = _make_agent_results(
            wavlm=("fake", 0.85),
            acoustic=("fake", 0.80),
        )
        res = _run_consensus(results)
        voice_clone_warnings = [w for w in res["threat_warnings"] if w["threat_type"] == "voice_clone"]
        assert len(voice_clone_warnings) == 0


# ═══════════════════════════════════════════════════════════════════════════
# D-02: Localized Audio Splice Threat
# ═══════════════════════════════════════════════════════════════════════════

class TestLocalizedSpliceThreat:
    """D-02: aasist/convnext fake ≥0.75, wavlm real"""

    def test_splice_aasist_fake_wavlm_real(self):
        """aasist=fake@0.80, wavlm=real@0.70 → localized_splice"""
        results = _make_agent_results(
            aasist=("fake", 0.80),
            wavlm=("real", 0.70),
        )
        res = _run_consensus(results)
        warnings = res["threat_warnings"]
        assert len(warnings) >= 1
        splice_warnings = [w for w in warnings if w["threat_type"] == "localized_splice"]
        assert len(splice_warnings) == 1
        assert splice_warnings[0]["severity"] == "high"
        assert "aasist" in splice_warnings[0]["triggering_agents"]

    def test_splice_convnext_fake_wavlm_real(self):
        """convnext=fake@0.78, wavlm=real@0.70 → localized_splice"""
        results = _make_agent_results(
            convnext=("fake", 0.78),
            wavlm=("real", 0.70),
        )
        res = _run_consensus(results)
        splice_warnings = [w for w in res["threat_warnings"] if w["threat_type"] == "localized_splice"]
        assert len(splice_warnings) == 1
        assert "convnext" in splice_warnings[0]["triggering_agents"]

    def test_no_splice_below_threshold(self):
        """aasist=fake@0.70 (below 0.75) → no localized_splice warning"""
        results = _make_agent_results(
            aasist=("fake", 0.70),
            wavlm=("real", 0.80),
        )
        res = _run_consensus(results)
        splice_warnings = [w for w in res["threat_warnings"] if w["threat_type"] == "localized_splice"]
        assert len(splice_warnings) == 0

    def test_no_splice_when_wavlm_not_real(self):
        """aasist=fake@0.80, wavlm=fake@0.75 → no splice (wavlm must be real)"""
        results = _make_agent_results(
            aasist=("fake", 0.80),
            wavlm=("fake", 0.75),
        )
        res = _run_consensus(results)
        splice_warnings = [w for w in res["threat_warnings"] if w["threat_type"] == "localized_splice"]
        assert len(splice_warnings) == 0


# ═══════════════════════════════════════════════════════════════════════════
# D-03: Partial Synthesis Threat (catch-all)
# ═══════════════════════════════════════════════════════════════════════════

class TestPartialSynthesisThreat:
    """D-03: catch-all split ≥0.60, not matched by D-01/D-02"""

    def test_partial_synthesis_generic_split(self):
        """acoustic=fake@0.65, convnext=real@0.70 → partial_synthesis"""
        results = _make_agent_results(
            acoustic=("fake", 0.65),
            convnext=("real", 0.70),
        )
        res = _run_consensus(results)
        partial_warnings = [w for w in res["threat_warnings"] if w["threat_type"] == "partial_synthesis"]
        assert len(partial_warnings) == 1
        assert partial_warnings[0]["severity"] == "elevated"

    def test_no_duplicate_with_d01(self):
        """wavlm=fake@0.85, acoustic=real@0.80 → voice_clone only, NOT partial_synthesis"""
        results = _make_agent_results(
            wavlm=("fake", 0.85),
            acoustic=("real", 0.80),
        )
        res = _run_consensus(results)
        partial_warnings = [w for w in res["threat_warnings"] if w["threat_type"] == "partial_synthesis"]
        assert len(partial_warnings) == 0
        # But voice_clone should be present
        voice_clone_warnings = [w for w in res["threat_warnings"] if w["threat_type"] == "voice_clone"]
        assert len(voice_clone_warnings) == 1

    def test_no_warning_below_threshold(self):
        """acoustic=fake@0.55 → no warning (below 0.60)"""
        results = _make_agent_results(
            acoustic=("fake", 0.55),
            convnext=("real", 0.70),
        )
        res = _run_consensus(results)
        partial_warnings = [w for w in res["threat_warnings"] if w["threat_type"] == "partial_synthesis"]
        assert len(partial_warnings) == 0


# ═══════════════════════════════════════════════════════════════════════════
# Multi-Threat Priority and Classification
# ═══════════════════════════════════════════════════════════════════════════

class TestThreatPriority:
    """Multi-threat scenarios and event classification"""

    def test_d01_and_d02_can_cofire(self):
        """
        This tests a scenario where D-01 and D-02 could theoretically both match.
        D-01 requires wavlm=fake, D-02 requires wavlm=real — mutually exclusive,
        so they cannot cofire on same chunk. Verify only one fires.
        """
        # D-01 scenario: wavlm fake
        results = _make_agent_results(
            wavlm=("fake", 0.85),
            acoustic=("real", 0.80),
            aasist=("fake", 0.80),
        )
        res = _run_consensus(results)
        d01 = [w for w in res["threat_warnings"] if w["threat_type"] == "voice_clone"]
        d02 = [w for w in res["threat_warnings"] if w["threat_type"] == "localized_splice"]
        # D-01 fires, D-02 cannot (wavlm is fake, not real)
        assert len(d01) == 1
        assert len(d02) == 0

    def test_event_type_splice_classification(self):
        """Verify SPLICE event_type assigned when voice_clone fires"""
        results = _make_agent_results(
            wavlm=("fake", 0.85),
            acoustic=("real", 0.80),
        )
        res = _run_consensus(results)
        assert res["event_type"] == ConsensusEventType.SPLICE

    def test_event_type_splice_on_localized(self):
        """Verify SPLICE event_type assigned when localized_splice fires"""
        results = _make_agent_results(
            aasist=("fake", 0.80),
            wavlm=("real", 0.70),
        )
        res = _run_consensus(results)
        assert res["event_type"] == ConsensusEventType.SPLICE

    def test_event_type_contradiction_on_partial(self):
        """Verify CONTRADICTION event_type assigned when partial_synthesis fires"""
        results = _make_agent_results(
            acoustic=("fake", 0.65),
            convnext=("real", 0.70),
        )
        res = _run_consensus(results)
        assert res["event_type"] == ConsensusEventType.CONTRADICTION

    def test_no_threats_agreement(self):
        """All agents agree real → AGREEMENT event, no warnings"""
        results = _make_agent_results(
            wavlm=("real", 0.90),
            acoustic=("real", 0.85),
            convnext=("real", 0.88),
            aasist=("real", 0.92),
        )
        res = _run_consensus(results)
        assert res["event_type"] == ConsensusEventType.AGREEMENT
        assert len(res["threat_warnings"]) == 0

    def test_backward_compat_deep_reasoning(self):
        """deep_reasoning strings populated from threat_warnings for backward compat"""
        results = _make_agent_results(
            wavlm=("fake", 0.85),
            acoustic=("real", 0.80),
        )
        res = _run_consensus(results)
        assert len(res["deep_reasoning"]) > 0
        assert "Voice Clone Threat" in res["deep_reasoning"][0]


# ═══════════════════════════════════════════════════════════════════════════
# D-04: Database Persistence of Threat Warnings
# ═══════════════════════════════════════════════════════════════════════════

class TestThreatPersistence:
    """D-04: Database persistence of threat warnings"""

    @pytest.fixture
    def db(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        test_engine = create_engine("sqlite:///:memory:")
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        Base.metadata.create_all(bind=test_engine)
        session = TestSession()
        yield session
        session.close()

    def test_threat_in_event_description(self, db):
        """ConsensusEvent.description contains the threat description string"""
        report = Report(filename="test_clone.wav", schema_version="v2.0")
        db.add(report)
        db.flush()

        event = ConsensusEvent(
            report_id=report.id,
            event_type=ConsensusEventType.SPLICE,
            description="Voice Clone Threat: High-fidelity phonetic cloning suspected; phonetic structures exhibit synthetic entropy, but acoustic properties appear natural.",
            start_time=0.0,
            end_time=2.0,
            involved_agents=["wavlm", "acoustic"],
            agent_snapshot={},
            diagnostic_metrics={}
        )
        db.add(event)
        db.commit()

        retrieved = db.query(ConsensusEvent).filter(ConsensusEvent.id == event.id).first()
        assert "Voice Clone Threat" in retrieved.description

    def test_threat_in_diagnostic_metrics(self, db):
        """diagnostic_metrics JSON contains threat_interpretation key"""
        report = Report(filename="test_diag.wav", schema_version="v2.0")
        db.add(report)
        db.flush()

        diag = {
            "snr_db": 30.0,
            "threat_interpretation": [
                {"type": "voice_clone", "description": "Voice Clone Threat: ...", "severity": "high"}
            ]
        }
        event = ConsensusEvent(
            report_id=report.id,
            event_type=ConsensusEventType.SPLICE,
            description="Voice Clone Threat: ...",
            start_time=0.0,
            end_time=2.0,
            involved_agents=["wavlm", "acoustic"],
            agent_snapshot={},
            diagnostic_metrics=diag
        )
        db.add(event)
        db.commit()

        retrieved = db.query(ConsensusEvent).filter(ConsensusEvent.id == event.id).first()
        assert "threat_interpretation" in retrieved.diagnostic_metrics
        assert retrieved.diagnostic_metrics["threat_interpretation"][0]["type"] == "voice_clone"

    def test_threat_in_agent_snapshot(self, db):
        """agent_snapshot JSON contains _threat_warnings key"""
        report = Report(filename="test_snap.wav", schema_version="v2.0")
        db.add(report)
        db.flush()

        snapshot = {
            "wavlm": {"verdict": "fake", "confidence": 0.85},
            "_threat_warnings": [
                {"threat_type": "voice_clone", "description": "Voice Clone Threat: ...", "severity": "high"}
            ]
        }
        event = ConsensusEvent(
            report_id=report.id,
            event_type=ConsensusEventType.SPLICE,
            description="Voice Clone Threat: ...",
            start_time=0.0,
            end_time=2.0,
            involved_agents=["wavlm", "acoustic"],
            agent_snapshot=snapshot,
            diagnostic_metrics={}
        )
        db.add(event)
        db.commit()

        retrieved = db.query(ConsensusEvent).filter(ConsensusEvent.id == event.id).first()
        assert "_threat_warnings" in retrieved.agent_snapshot
        assert retrieved.agent_snapshot["_threat_warnings"][0]["threat_type"] == "voice_clone"

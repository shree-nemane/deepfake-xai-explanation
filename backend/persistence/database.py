from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
import os
import uuid

DATABASE_URL = "sqlite:///forensic_intelligence.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class ConsensusEventType(PyEnum):
    AGREEMENT = "agreement"
    CONTRADICTION = "contradiction"
    SPLICE = "splice"
    QUALITY_FAILURE = "quality_failure"
    RELIABILITY_WARNING = "reliability_warning"

class Report(Base):
    """High-level metadata for an analysis session."""
    __tablename__ = "reports"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    schema_version = Column(String, default="v2.0")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    full_response = Column(JSON, nullable=True)
    
    # Relationships
    agents = relationship("AgentOutput", back_populates="report", cascade="all, delete-orphan")
    evidence_segments = relationship("EvidenceSegment", back_populates="report", cascade="all, delete-orphan")
    consensus_events = relationship("ConsensusEvent", back_populates="report", cascade="all, delete-orphan")
    xai_artifacts = relationship("XAIArtifact", back_populates="report", cascade="all, delete-orphan")
    narrative_report = relationship("NarrativeReport", back_populates="report", uselist=False, cascade="all, delete-orphan")
    processing_metadata = relationship("ProcessingMetadata", back_populates="report", uselist=False, cascade="all, delete-orphan")

class AgentOutput(Base):
    """Stores agent outputs, confidence, and uncertainty for the entire file/session."""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False)
    agent_name = Column(String, nullable=False) # 'wavlm', 'convnext', 'acoustic', etc.
    prediction = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    
    report = relationship("Report", back_populates="agents")

class EvidenceSegment(Base):
    """MOST IMPORTANT TABLE. Stores localized timestamps and chunk verdicts."""
    __tablename__ = "evidence_segments"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    agent_name = Column(String, nullable=False)
    risk_score = Column(Float, nullable=False)
    features = Column(JSON, nullable=True) # E.g., specific anomalies found in this chunk
    
    report = relationship("Report", back_populates="evidence_segments")

class ConsensusEvent(Base):
    """Stores agreement/contradiction events and temporal convergence."""
    __tablename__ = "consensus_events"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False)
    event_type = Column(SQLEnum(ConsensusEventType), nullable=False)
    description = Column(String, nullable=False)
    start_time = Column(Float, nullable=True) # Optional temporal localization
    end_time = Column(Float, nullable=True)
    involved_agents = Column(JSON, nullable=False) # List of agent names involved
    agent_snapshot = Column(JSON, nullable=True)
    diagnostic_metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    report = relationship("Report", back_populates="consensus_events")
    event_agent_details = relationship("EventAgentDetails", back_populates="consensus_event", cascade="all, delete-orphan")

class XAIArtifact(Base):
    """Stores references or serialized data for XAI artifacts."""
    __tablename__ = "xai_artifacts"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False)
    artifact_type = Column(String, nullable=True) # Keep for backward compatibility with heatmap
    data = Column(String, nullable=True) # Keep for backward compatibility with heatmap
    shap_values = Column(JSON, nullable=True)
    counterfactuals = Column(JSON, nullable=True)
    evidence_graph = Column(JSON, nullable=True)
    shap_summary = Column(Text, nullable=True)
    counterfactual_summary = Column(Text, nullable=True)
    xai_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    report = relationship("Report", back_populates="xai_artifacts")

class NarrativeReport(Base):
    """Stores structured and human summaries generated by the Narrative Engine."""
    __tablename__ = "narrative_reports"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), unique=True, nullable=False)
    structured_summary = Column(Text, nullable=True)
    human_summary = Column(Text, nullable=True)
    narrative_metadata = Column(JSON, nullable=True)
    generated_by = Column(String, nullable=True)
    narrative_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    report = relationship("Report", back_populates="narrative_report")

class EventAgentDetails(Base):
    """Stores segment-level agent details for consensus contradiction events."""
    __tablename__ = "event_agent_details"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    event_id = Column(String, ForeignKey("consensus_events.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    agent_version = Column(String, nullable=True) # e.g. "WavLM-v1"
    verdict = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=True)
    adjusted_confidence = Column(Float, nullable=True)
    suppression_factor = Column(Float, nullable=True)
    temporal_region = Column(JSON, nullable=True) # {"start_time": ..., "end_time": ...}
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    consensus_event = relationship("ConsensusEvent", back_populates="event_agent_details")

class ProcessingMetadata(Base):
    """Stores research metadata for analysis runs, facilitating reproducibility."""
    __tablename__ = "processing_metadata"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), unique=True, nullable=False)
    chunk_duration = Column(Float, default=2.0)
    overlap = Column(Float, default=0.5)
    semantic_sr = Column(Integer, default=16000)
    forensic_sr = Column(Integer, default=48000)
    pipeline_version = Column(String, default="forensic_pipeline_v1")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    report = relationship("Report", back_populates="processing_metadata")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

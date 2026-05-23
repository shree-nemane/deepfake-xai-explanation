from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import datetime

class AgentOutputSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    verdict: str
    confidence: float
    uncertainty: float
    evidence: Optional[Dict[str, Any]] = None

class ConsensusSchema(BaseModel):
    verdict: str
    convergence_strength: float
    confidence: float
    uncertainty: float
    fake_probability: Optional[float] = None
    real_probability: Optional[float] = None
    probability_margin: Optional[float] = None
    decision_threshold: Optional[float] = None

class TimelineEventSchema(BaseModel):
    start_time: float
    end_time: float
    event_type: str
    verdict: str
    confidence: float
    convergence_strength: float
    details: Optional[Dict[str, Any]] = None
    deep_reasoning: Optional[List[str]] = None
    threat_warnings: Optional[List[Dict[str, Any]]] = None

class SampleRatesSchema(BaseModel):
    semantic: int
    forensic: int

class ProcessingMetadataSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chunk_duration: float
    overlap: float
    sample_rates: SampleRatesSchema
    schema_version: str
    pipeline_version: str

class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    consensus: ConsensusSchema
    agents: Dict[str, AgentOutputSchema]
    timeline: List[TimelineEventSchema]
    preprocessing: Optional[Dict[str, Any]] = None
    feature_analysis: Optional[Dict[str, Any]] = None
    diagnostics: Optional[Dict[str, Any]] = None
    heatmap_base64: Optional[str] = None
    processing_metadata: Optional[ProcessingMetadataSchema] = None
    created_at: datetime

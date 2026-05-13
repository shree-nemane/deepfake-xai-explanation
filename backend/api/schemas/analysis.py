from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class EvidenceSchema(BaseModel):
    feature_name: str
    value: float
    anomaly_score: float

    class Config:
        from_attributes = True

class XAISchema(BaseModel):
    gradcam: Optional[str] = None
    shap: Optional[Dict[str, Any]] = None
    integrated_gradients: Optional[str] = None
    counterfactuals: Optional[List[Dict[str, Any]]] = None

class AnalysisResponse(BaseModel):
    id: str
    prediction: str
    confidence: float
    uncertainty: str
    risk_score: float
    verdict_reason: str
    detailed_narrative: Dict[str, str]
    xai: XAISchema
    forensic_features: List[EvidenceSchema]
    timeline_data: Optional[List[Dict[str, float]]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    message: str

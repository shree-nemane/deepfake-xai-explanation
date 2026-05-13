from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import os
import shutil
import librosa
import numpy as np
from backend.database.session import get_db
from backend.api.schemas.analysis import AnalysisResponse
from backend.services.inference_service import InferenceService
from backend.services.report_service import ReportService
from backend.forensic.features.acoustic_features import extract_all_features
from backend.forensic.rules.forensic_rules import ForensicRuleEngine
from backend.services.explanation_service import ExplanationService
from backend.explainability.xai_manager import XAIManager
from backend.database.models import Report

router = APIRouter(prefix="/analyze", tags=["analysis"])

@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).limit(20).all()
    return reports

# Shared Services
inference_service = InferenceService()
rule_engine = ForensicRuleEngine()

UPLOADS_DIR = "uploads"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

@router.post("/", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(('.wav', '.mp3')):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    temp_path = os.path.join(UPLOADS_DIR, f"{file_id}{ext}")

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Preprocess
        y, sr = librosa.load(temp_path, sr=16000)
        
        # 2. Extract Forensic Features
        features = extract_all_features(y, sr)
        forensic_scores, overall_anomaly = rule_engine.apply_rules(features)
        
        # 3. Model Inference (Hybrid: ConvNext + Wav2Vec2 + Fusion)
        hybrid_results = inference_service.predict_hybrid(y, sr, forensic_scores)
        
        # 4. Uncertainty (Monte Carlo Dropout on ConvNext)
        uncertainty_results = inference_service.predict_with_uncertainty(y, sr)
        
        # 5. Visual XAI (Grad-CAM, IG)
        heatmap_base64 = ReportService.heatmap_to_base64(hybrid_results["heatmap"])
        ig_base64 = XAIManager.attr_to_base64(hybrid_results["ig_map"])
        
        # 6. Final Decision Logic (Adaptive)
        # Risk Score combines hybrid model confidence and anomaly scores
        model_risk = hybrid_results["confidence"] if hybrid_results["prediction"] == "fake" else (1 - hybrid_results["confidence"])
        final_risk_score = (model_risk * 0.7 + overall_anomaly * 0.3) * 100
        decision_category = ForensicRuleEngine.get_decision_category(final_risk_score)
        
        # 7. Construct Timeline Data
        # We'll use ZCR and MFCC variance as indicators of temporal anomalies
        zcr_series = features.get("zcr_series", [])
        mfcc_series = features.get("mfcc_var_series", [])
        timeline_data = []
        for i in range(min(len(zcr_series), 100)): # Cap at 100 points for performance
            timeline_data.append({
                "time": i,
                "zcr": zcr_series[i],
                "timbre_instability": mfcc_series[i] if i < len(mfcc_series) else 0
            })

        # 8. Aggregate results
        detailed_narrative = ExplanationService.generate_detailed_narrative(
            decision_category, final_risk_score, forensic_scores, 
            uncertainty_results["uncertainty"], hybrid_results["counterfactuals"]
        )
        
        analysis_data = {
            **uncertainty_results,
            "prediction": decision_category,
            "confidence": hybrid_results["confidence"],
            "heatmap_base64": heatmap_base64,
            "ig_base64": ig_base64,
            "shap_values": hybrid_results["shap_values"],
            "counterfactuals": hybrid_results["counterfactuals"],
            "risk_score": final_risk_score,
            "verdict_reason": detailed_narrative["layman_explanation"],
            "detailed_narrative": detailed_narrative
        }
        
        # 9. Persist to Database
        report = ReportService.create_report(db, analysis_data, forensic_scores, file.filename)
        
        # 10. Format response
        return {
            "id": report.id,
            "prediction": report.prediction,
            "confidence": report.confidence,
            "uncertainty": report.uncertainty,
            "risk_score": report.risk_score,
            "verdict_reason": analysis_data["verdict_reason"],
            "detailed_narrative": detailed_narrative,
            "xai": {
                "gradcam": heatmap_base64,
                "integrated_gradients": ig_base64,
                "shap": hybrid_results["shap_values"],
                "counterfactuals": hybrid_results["counterfactuals"],
                "uncertainty_metrics": uncertainty_results
            },
            "forensic_features": [
                {"feature_name": f, "value": v["value"], "anomaly_score": v["risk_score"]}
                for f, v in forensic_scores.items() if not f.endswith("_series")
            ],
            "timeline_data": timeline_data,
            "created_at": report.created_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

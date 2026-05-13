from backend.database.models import Report, Evidence
from sqlalchemy.orm import Session
import json
import base64
import cv2
import numpy as np

class ReportService:
    @staticmethod
    def create_report(db: Session, analysis_results: dict, forensic_scores: dict, filename: str):
        """
        Aggregate results and save to database.
        """
        # 1. Map results to report model
        report = Report(
            filename=filename,
            prediction=analysis_results["prediction"],
            confidence=analysis_results["confidence"],
            uncertainty=analysis_results.get("uncertainty", "N/A"),
            risk_score=analysis_results.get("risk_score", 0.0),
            model_version="ConvNext-Tiny-V1",
            rule_version="Z-Score-V1",
            xai_data={
                "gradcam": analysis_results.get("heatmap_base64"),
                "integrated_gradients": analysis_results.get("ig_base64"),
                "shap": analysis_results.get("shap_values"),
                "counterfactuals": analysis_results.get("counterfactuals"),
                "uncertainty_metrics": {
                    "variance": analysis_results.get("variance"),
                    "entropy": analysis_results.get("entropy")
                }
            }
        )
        
        db.add(report)
        db.flush() # Get report ID
        
        # 2. Add evidence
        for feature, data in forensic_scores.items():
            if feature.endswith("_series") or isinstance(data["value"], list):
                continue
            evidence = Evidence(
                report_id=report.id,
                feature_name=feature,
                value=float(data["value"]),
                anomaly_score=float(data["risk_score"])
            )
            db.add(evidence)
            
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def heatmap_to_base64(heatmap):
        """Convert heatmap numpy array to base64 string."""
        try:
            heatmap_colored = cv2.applyColorMap((heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)
            _, buffer = cv2.imencode('.png', heatmap_colored)
            return base64.b64encode(buffer).decode('utf-8')
        except Exception:
            return None

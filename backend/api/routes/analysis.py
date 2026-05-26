from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from collections import Counter, defaultdict
from datetime import datetime, timezone
import asyncio
import json
import threading
import uuid
import os
import shutil
import cv2
import base64
import numpy as np

from backend.persistence.database import get_db, SessionLocal, Report, AgentOutput, EvidenceSegment, ConsensusEvent, XAIArtifact, ConsensusEventType, NarrativeReport, EventAgentDetails, ProcessingMetadata
from backend.api.schemas.analysis import AnalysisResponse
from backend.preprocessing.audio_processor import AudioProcessor
from backend.orchestration.forensic_orchestrator import AnalysisUnavailableError, ForensicOrchestrator
from backend.explainability.counterfactuals.counterfactual_engine import CounterfactualEngine
from backend.explainability.evidence_graph import generate_evidence_graph
from backend.explainability.narrative_engine import NarrativeEngine
from backend.forensic.timeline_compression import compress_timeline_events
from backend.forensic.features.acoustic_features import mel_spectrogram_preview_base64
from backend.explainability.shap.shap_engine import SHAPEngine
from enum import Enum as PyEnum

router = APIRouter(prefix="/analyze", tags=["analysis"])


ANALYSIS_STAGES = [
    {"id": "upload_received", "label": "Upload received", "percent": 5},
    {"id": "preprocessing", "label": "Normalizing and isolating speech", "percent": 18},
    {"id": "segmentation", "label": "Segmenting aligned streams", "percent": 30},
    {"id": "agent_panel", "label": "Running forensic agent panel", "percent": 48},
    {"id": "consensus", "label": "Calibrating consensus", "percent": 66},
    {"id": "xai_evidence_graph", "label": "Building XAI and evidence graph", "percent": 82},
    {"id": "narrative_persistence", "label": "Writing narrative and report", "percent": 94},
    {"id": "complete", "label": "Analysis complete", "percent": 100},
]
STAGE_INDEX = {stage["id"]: index for index, stage in enumerate(ANALYSIS_STAGES)}


class AnalysisJobStore:
    """Thread-safe in-memory progress store for local analysis jobs."""

    def __init__(self):
        self._jobs = {}
        self._lock = threading.Lock()

    def create(self, job_id, filename):
        now = datetime.now(timezone.utc).isoformat()
        job = {
            "job_id": job_id,
            "filename": filename,
            "stage": "upload_received",
            "status": "queued",
            "percent": 5,
            "message": "Upload received.",
            "error": None,
            "result": None,
            "created_at": now,
            "updated_at": now,
            "sequence": 0,
        }
        with self._lock:
            self._jobs[job_id] = job
        return self.snapshot(job_id)

    def update(self, job_id, stage, status="running", percent=None, message=None, error=None, result=None):
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            stage_defaults = next((item for item in ANALYSIS_STAGES if item["id"] == stage), None)
            job["stage"] = stage
            job["status"] = status
            job["percent"] = percent if percent is not None else (stage_defaults or {}).get("percent", job["percent"])
            job["message"] = message if message is not None else (stage_defaults or {}).get("label", stage)
            job["error"] = error
            if result is not None:
                job["result"] = result
            job["updated_at"] = datetime.now(timezone.utc).isoformat()
            job["sequence"] += 1
            return self._snapshot_unlocked(job)

    def snapshot(self, job_id, include_result=False):
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            return self._snapshot_unlocked(job, include_result=include_result)

    def result(self, job_id):
        with self._lock:
            job = self._jobs.get(job_id)
            return None if job is None else job.get("result")

    def _snapshot_unlocked(self, job, include_result=False):
        active_index = STAGE_INDEX.get(job["stage"], 0)
        stages = []
        for index, stage in enumerate(ANALYSIS_STAGES):
            if job["status"] == "error" and index == active_index:
                status = "error"
            elif index < active_index or job["stage"] == "complete":
                status = "complete"
            elif index == active_index:
                status = job["status"]
            else:
                status = "pending"
            stages.append({**stage, "status": status})

        snapshot = {
            key: job[key]
            for key in (
                "job_id",
                "filename",
                "stage",
                "status",
                "percent",
                "message",
                "error",
                "created_at",
                "updated_at",
                "sequence",
            )
        }
        snapshot["stages"] = stages
        if include_result:
            snapshot["result"] = job.get("result")
        return snapshot


analysis_jobs = AnalysisJobStore()
_orchestrator = None
_audio_processor = None
_runtime_lock = threading.Lock()


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        with _runtime_lock:
            if _orchestrator is None:
                _orchestrator = ForensicOrchestrator()
    return _orchestrator


def _get_audio_processor():
    global _audio_processor
    if _audio_processor is None:
        with _runtime_lock:
            if _audio_processor is None:
                _audio_processor = AudioProcessor()
    return _audio_processor


def _emit_progress(progress_callback, stage, status="running", message=None, percent=None):
    if progress_callback:
        progress_callback(stage=stage, status=status, message=message, percent=percent)


def _severity(score):
    score = _safe_float(score)
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "elevated"
    if score >= 0.2:
        return "low"
    return "nominal"


def _label(key):
    return key.replace("_", " ").title()


def _average_numeric_evidence(chunks):
    numeric_evidence = {}
    for chunk in chunks:
        for key, value in (chunk.get("evidence") or {}).items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                numeric_evidence.setdefault(key, []).append(float(value))

    return {
        key: sum(values) / len(values)
        for key, values in numeric_evidence.items()
        if values
    }


def _build_preprocessing_summary(streams, chunk_count):
    metadata = streams.get("metadata", {})
    lufs = metadata.get("lufs", {})
    duration_16k = len(streams["16k"]) / 16000 if len(streams.get("16k", [])) else 0.0
    duration_48k = len(streams["48k"]) / 48000 if len(streams.get("48k", [])) else 0.0

    return {
        "sample_rates": {"semantic_stream_hz": 16000, "acoustic_stream_hz": 48000},
        "original_duration_sec": round(_safe_float(metadata.get("original_duration_sec")), 3),
        "active_duration_sec": round(duration_16k, 3),
        "high_fidelity_duration_sec": round(duration_48k, 3),
        "speech_coverage": round(_safe_float(metadata.get("speech_coverage")), 4),
        "original_peak": _safe_float(metadata.get("original_peak")),
        "original_rms": _safe_float(metadata.get("original_rms")),
        "global_clipping_ratio": _safe_float(metadata.get("global_clipping_ratio")),
        "vad_segments": int(metadata.get("vad_segments", 0)),
        "chunk_count": chunk_count,
        "chunk_window_sec": 2.0,
        "chunk_overlap": 0.5,
        "lufs": {
            "original": _safe_float(lufs.get("original_lufs"), None),
            "target": _safe_float(lufs.get("target_lufs"), -23.0),
            "gain_applied": _safe_float(lufs.get("gain_applied")),
        },
    }


def _build_acoustic_feature_rows(agent_results):
    collected = defaultdict(lambda: {"values": [], "z_scores": [], "risk_scores": [], "count": 0})

    for chunk in agent_results.get("acoustic", []):
        top_features = (chunk.get("evidence") or {}).get("top_anomalous_features", {})
        for feature_name, info in top_features.items():
            collected[feature_name]["values"].append(_safe_float(info.get("value")))
            collected[feature_name]["z_scores"].append(_safe_float(info.get("z_score")))
            collected[feature_name]["risk_scores"].append(_safe_float(info.get("risk_score")))
            collected[feature_name]["count"] += 1

    rows = []
    for feature_name, info in collected.items():
        risk = sum(info["risk_scores"]) / len(info["risk_scores"]) if info["risk_scores"] else 0.0
        rows.append({
            "feature": feature_name,
            "label": _label(feature_name),
            "avg_value": sum(info["values"]) / len(info["values"]) if info["values"] else 0.0,
            "avg_z_score": sum(info["z_scores"]) / len(info["z_scores"]) if info["z_scores"] else 0.0,
            "avg_risk_score": risk,
            "occurrences": info["count"],
            "severity": _severity(risk),
        })

    return sorted(rows, key=lambda item: item["avg_risk_score"], reverse=True)


def _get_event_name(event):
    et = event.get("event_type")
    if hasattr(et, "value"):
        return et.value
    return str(et) if et is not None else "UNKNOWN"


def _build_feature_analysis(agent_results, frontend_agents, chunk_consensus, preprocessing):
    acoustic_features = _build_acoustic_feature_rows(agent_results)
    reliability = (frontend_agents.get("reliability") or {}).get("evidence", {})
    wavlm = (frontend_agents.get("wavlm") or {}).get("evidence", {})
    convnext = (frontend_agents.get("convnext") or {}).get("evidence", {})
    aasist = (frontend_agents.get("aasist") or {}).get("evidence", {})
    acoustic = (frontend_agents.get("acoustic") or {}).get("evidence", {})

    wavlm_threshold = _safe_float(wavlm.get("instability_threshold"), 0.12)
    neural_signals = [
        {
            "name": "WavLM phonetic instability",
            "value": _safe_float(wavlm.get("phonetic_instability")),
            "threshold": wavlm_threshold,
            "risk_score": min(_safe_float(wavlm.get("phonetic_instability")) / max(wavlm_threshold, 1e-6), 1.0),
            "severity": _severity(min(_safe_float(wavlm.get("phonetic_instability")) / max(wavlm_threshold, 1e-6), 1.0)),
        },
        {
            "name": "ConvNext spectral fake probability",
            "value": _safe_float(convnext.get("fake_probability")),
            "threshold": 0.5,
            "risk_score": _safe_float(convnext.get("fake_probability")),
            "severity": _severity(_safe_float(convnext.get("fake_probability"))),
        },
        {
            "name": "AASIST waveform spoof score",
            "value": _safe_float(aasist.get("spoof_score")),
            "threshold": 0.5,
            "risk_score": _safe_float(aasist.get("spoof_score")),
            "severity": _severity(_safe_float(aasist.get("spoof_score"))),
        },
        {
            "name": "Acoustic anomaly score",
            "value": _safe_float(acoustic.get("overall_anomaly")),
            "threshold": 0.4,
            "risk_score": _safe_float(acoustic.get("overall_anomaly")),
            "severity": _severity(_safe_float(acoustic.get("overall_anomaly"))),
        },
    ]

    event_counts = Counter(_get_event_name(event) for event in chunk_consensus)

    return {
        "preprocessing": preprocessing,
        "signal_quality": {
            "snr_db": _safe_float(reliability.get("snr_db")),
            "clipping_ratio": _safe_float(reliability.get("clipping_ratio")),
            "spectral_flatness": _safe_float(reliability.get("spectral_flatness")),
            "rms_energy": _safe_float(reliability.get("rms_energy")),
            "reliability_score": _safe_float(reliability.get("reliability_score"), 1.0),
        },
        "acoustic_features": acoustic_features,
        "neural_signals": neural_signals,
        "consensus_events": dict(event_counts),
    }


def _timeline_mel_key(row: dict) -> str:
    return f"{row.get('start_time')}:{row.get('end_time')}"


def _extract_mel_previews(timeline: list) -> tuple[list, dict]:
    """Split mel PNG payloads out of timeline rows for lean DB storage."""
    stripped = []
    previews = {}
    for row in timeline or []:
        row = dict(row)
        mel = row.pop("mel_preview_base64", None)
        if mel:
            previews[_timeline_mel_key(row)] = mel
        stripped.append(row)
    return stripped, previews


def _apply_mel_previews(timeline: list, previews: dict) -> list:
    if not previews:
        return timeline
    enriched = []
    for row in timeline or []:
        row = dict(row)
        mel = previews.get(_timeline_mel_key(row))
        if mel:
            row["mel_preview_base64"] = mel
        enriched.append(row)
    return enriched


def _diagnostic_warning(category: str, message: str) -> dict:
    return {"category": category, "message": message}


def _flatten_diagnostic_warnings(warnings: list) -> list:
    flat = []
    for item in warnings or []:
        if isinstance(item, dict):
            flat.append(item.get("message") or str(item))
        else:
            flat.append(str(item))
    return flat


def _build_diagnostics(global_consensus, frontend_agents, chunk_consensus):
    reliability = (frontend_agents.get("reliability") or {}).get("evidence", {})
    reliability_score = _safe_float(reliability.get("reliability_score"), 1.0)
    clipping_ratio = _safe_float(reliability.get("clipping_ratio"))
    confidence = _safe_float(global_consensus.get("confidence"))
    convergence = _safe_float(global_consensus.get("convergence_strength"))
    probability_margin = _safe_float(global_consensus.get("probability_margin"))
    event_counts = Counter(_get_event_name(event) for event in chunk_consensus)

    decision_reliability = max(0.0, min(1.0, confidence * 0.45 + convergence * 0.35 + reliability_score * 0.20))
    quality_warnings = []
    synthesis_warnings = []
    if reliability_score < 0.6:
        quality_warnings.append(
            _diagnostic_warning(
                "signal_quality",
                "Recording quality is degraded; calibrated agent confidence has been suppressed.",
            )
        )
    if clipping_ratio > 0.01:
        quality_warnings.append(
            _diagnostic_warning(
                "signal_quality",
                "Clipping is above forensic threshold and may hide synthesis artifacts.",
            )
        )
    if event_counts.get("contradiction", 0) > 0:
        synthesis_warnings.append(
            _diagnostic_warning(
                "synthesis_evidence",
                "Agents disagree on at least one chunk; inspect the temporal timeline before relying on the verdict.",
            )
        )
    if confidence < 0.6:
        synthesis_warnings.append(
            _diagnostic_warning(
                "synthesis_evidence",
                "Consensus confidence is low; treat this as analyst-support evidence, not a final conclusion.",
            )
        )
    if probability_margin < 0.08:
        synthesis_warnings.append(
            _diagnostic_warning(
                "synthesis_evidence",
                "Fake/real probability margin is narrow; the global verdict has been held back.",
            )
        )

    warnings = quality_warnings + synthesis_warnings

    if decision_reliability >= 0.75:
        review_level = "high_trust"
    elif decision_reliability >= 0.55:
        review_level = "moderate_trust"
    else:
        review_level = "needs_human_review"

    return {
        "decision_reliability": decision_reliability,
        "review_level": review_level,
        "warnings": warnings,
        "quality_warnings": quality_warnings,
        "synthesis_warnings": synthesis_warnings,
        "event_counts": dict(event_counts),
        "agent_count": len(frontend_agents),
        "chunk_count": len(chunk_consensus),
    }


def _build_xai_payload(chunk_consensus):
    shap_engine = SHAPEngine()
    counterfactual_engine = CounterfactualEngine()
    shap_chunks = []
    counterfactual_chunks = []
    aggregate_shap = defaultdict(float)

    for index, chunk in enumerate(chunk_consensus):
        calibrated_details = chunk.get("calibrated_details", {})
        shap_payload = shap_engine.compute_consensus_shap(calibrated_details)
        counterfactual_payload = counterfactual_engine.compute_consensus_sensitivity(
            calibrated_details,
            chunk.get("fake_probability"),
            chunk.get("real_probability"),
        )

        for agent_name, value in shap_payload.get("values", {}).items():
            aggregate_shap[agent_name] += _safe_float(value)

        shap_chunks.append({
            "chunk_index": index,
            "start_time": chunk.get("start_time"),
            "end_time": chunk.get("end_time"),
            **shap_payload,
        })
        counterfactual_chunks.append({
            "chunk_index": index,
            "start_time": chunk.get("start_time"),
            "end_time": chunk.get("end_time"),
            **counterfactual_payload,
        })

    if shap_chunks:
        avg_shap = {
            agent_name: value / len(shap_chunks)
            for agent_name, value in aggregate_shap.items()
        }
    else:
        avg_shap = {}

    top_shap = sorted(avg_shap.items(), key=lambda item: abs(item[1]), reverse=True)
    shap_summary = (
        "Exact Shapley attributions computed over calibrated consensus coalitions."
        if shap_chunks else
        "No chunk-level calibrated consensus details were available for Shapley attribution."
    )
    if top_shap:
        shap_summary = f"{shap_summary} Top contributor: {top_shap[0][0]} ({top_shap[0][1]:.3f})."

    top_sensitivity = None
    for chunk in counterfactual_chunks:
        for agent_name, info in chunk.get("sensitivities", {}).items():
            magnitude = abs(_safe_float(info.get("gradient")))
            if top_sensitivity is None or magnitude > top_sensitivity["magnitude"]:
                top_sensitivity = {
                    "agent": agent_name,
                    "magnitude": magnitude,
                    "statement": info.get("statement", ""),
                }

    counterfactual_summary = (
        top_sensitivity["statement"]
        if top_sensitivity else
        "No analytical consensus sensitivity was available."
    )

    return {
        "shap_values": {
            "method": "exact_consensus_shap",
            "chunks": shap_chunks,
            "summary": {
                "average_values": avg_shap,
                "top_contributors": [
                    {"agent": agent_name, "value": value}
                    for agent_name, value in top_shap
                ],
            },
        },
        "counterfactuals": {
            "method": "analytical_level_1",
            "chunks": counterfactual_chunks,
            "summary": counterfactual_summary,
        },
        "shap_summary": shap_summary,
        "counterfactual_summary": counterfactual_summary,
    }

@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).limit(20).all()
    history_list = []
    for r in reports:
        if not r.full_response:
            continue
        consensus = r.full_response.get("consensus", {})
        history_list.append({
            "id": r.id,
            "filename": r.filename,
            "created_at": r.created_at,
            "prediction": consensus.get("verdict", "inconclusive"),
            "confidence": consensus.get("confidence", 0.0),
            "risk_score": (consensus.get("fake_probability", 0.0) * 100) if consensus.get("verdict") == "fake" else ((1 - consensus.get("confidence", 1.0)) * 100)
        })
    return history_list

@router.get("/{report_id}")
async def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report or not report.full_response:
        raise HTTPException(status_code=404, detail="Report not found")
    payload = dict(report.full_response)
    mel_previews = payload.pop("mel_previews", None) or {}
    if mel_previews and payload.get("timeline"):
        payload["timeline"] = _apply_mel_previews(payload["timeline"], mel_previews)
    return payload

UPLOADS_DIR = "uploads"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)


def _run_analysis_from_path(temp_path, filename, db, report_id=None, progress_callback=None):
    file_id = report_id or str(uuid.uuid4())
    try:
        # 1. Preprocess (Dual-Stream)
        _emit_progress(progress_callback, "preprocessing", message="Normalizing audio and isolating speech.")
        streams = _get_audio_processor().process_dual_stream(temp_path)
        audio_16k = streams["16k"]
        audio_48k = streams["48k"]
        
        # 2. Orchestrate Agents
        _emit_progress(progress_callback, "segmentation", message="Preparing overlapping temporal chunks.")
        _emit_progress(progress_callback, "agent_panel", message="Running neural and acoustic forensic agents.")
        results = _get_orchestrator().analyze_audio(audio_16k, audio_48k)
        
        agent_results = results["agent_results"]
        chunk_consensus = results["chunk_consensus"]
        global_consensus = results["global_consensus"]
        _emit_progress(progress_callback, "consensus", message="Calibrating multi-agent consensus.")
        
        # 3. Create Report in Database
        report = Report(id=file_id, filename=filename)
        db.add(report)
        db.flush()
        
        # 4. Save Agent Outputs (File-level aggregate approximations for now)
        frontend_agents = {}
        for agent_name, chunks in agent_results.items():
            if not chunks: continue
            avg_conf = sum(c.get("confidence", 0) for c in chunks) / len(chunks)
            avg_unc = sum(c.get("uncertainty", 0) for c in chunks) / len(chunks)
            fake_votes = sum(1 for c in chunks if c.get("verdict") == "fake")
            real_votes = sum(1 for c in chunks if c.get("verdict") == "real")
            if fake_votes > (len(chunks) / 2):
                overall_verdict = "fake"
            elif real_votes > (len(chunks) / 2):
                overall_verdict = "real"
            else:
                overall_verdict = "inconclusive"
            
            db.add(AgentOutput(
                report_id=report.id,
                agent_name=agent_name,
                prediction=overall_verdict,
                confidence=avg_conf,
                uncertainty=avg_unc
            ))

            averaged_evidence = _average_numeric_evidence(chunks)
            
            frontend_agents[agent_name] = {
                "name": agent_name,
                "verdict": overall_verdict,
                "confidence": avg_conf,
                "uncertainty": avg_unc,
                "evidence": {
                    **averaged_evidence,
                    "fake_chunks": fake_votes,
                    "real_chunks": real_votes,
                    "inconclusive_chunks": len(chunks) - fake_votes - real_votes,
                    "total_chunks": len(chunks)
                }
            }
            
        # 5. Save Timeline and Consensus
        frontend_timeline = []
        for c in chunk_consensus:
            if c["verdict"] == "fake":
                risk_score = c["consensus_confidence"]
            elif c["verdict"] == "real":
                risk_score = 1 - c["consensus_confidence"]
            else:
                risk_score = 0.5

            db.add(EvidenceSegment(
                report_id=report.id,
                start_time=c["start_time"],
                end_time=c["end_time"],
                agent_name="consensus",
                risk_score=risk_score
            ))
            
            # Extract threat warnings from consensus engine output
            threat_warnings = c.get("threat_warnings", [])
            
            # D-04: Use threat description as ConsensusEvent.description when available
            if threat_warnings:
                description = threat_warnings[0]["description"]
            else:
                description = f"{c['event_type'].value if hasattr(c['event_type'], 'value') else c['event_type']} at chunk"
            
            # D-04: Embed threat_warnings into diagnostic_metrics JSON
            diag = dict(c.get("diagnostic_metrics") or {})
            if threat_warnings:
                diag["threat_interpretation"] = [
                    {"type": w["threat_type"], "description": w["description"], "severity": w["severity"]}
                    for w in threat_warnings
                ]
            
            # D-04: Embed threat_warnings into agent_snapshot JSON
            snapshot = dict(c.get("calibrated_details", {}))
            if threat_warnings:
                snapshot["_threat_warnings"] = threat_warnings
            
            event = ConsensusEvent(
                report_id=report.id,
                event_type=c["event_type"],
                description=description,
                start_time=c["start_time"],
                end_time=c["end_time"],
                involved_agents=["wavlm", "convnext", "aasist", "acoustic"],
                agent_snapshot=snapshot,
                diagnostic_metrics=diag
            )
            db.add(event)
            db.flush() # Flush to populate event.id
            
            # Save EventAgentDetails for each voting agent in this chunk
            for agent_name, details in c["calibrated_details"].items():
                db.add(EventAgentDetails(
                    event_id=event.id,
                    agent_name=agent_name,
                    agent_version=f"{agent_name.capitalize()}-v1",
                    verdict=details.get("verdict", "inconclusive"),
                    confidence=details.get("calibrated_confidence", 0.0),
                    uncertainty=details.get("calibrated_uncertainty", 1.0),
                    adjusted_confidence=details.get("adjusted_confidence", 0.0),
                    suppression_factor=details.get("suppression_factor", 1.0),
                    temporal_region={"start_time": c["start_time"], "end_time": c["end_time"]}
                ))
            
            frontend_timeline.append({
                "start_time": c["start_time"],
                "end_time": c["end_time"],
                "event_type": c["event_type"].value if hasattr(c["event_type"], "value") else str(c["event_type"]),
                "verdict": c["verdict"],
                "confidence": c["consensus_confidence"],
                "convergence_strength": c["convergence_strength"],
                "details": c["calibrated_details"],
                "deep_reasoning": c.get("deep_reasoning", []),
                "threat_warnings": [
                    {"type": w["threat_type"], "description": w["description"], "severity": w["severity"]}
                    for w in threat_warnings
                ]
            })
            
        # 6. Extract Heatmap for XAI
        heatmap_base64 = None
        convnext_chunks = agent_results.get("convnext", [])
        if convnext_chunks:
            best_chunk = max(convnext_chunks, key=lambda c: c.get("confidence", 0))
            heatmap_array = best_chunk.get("evidence", {}).get("gradcam_heatmap")
            if heatmap_array is not None:
                heatmap_uint8 = np.uint8(255 * heatmap_array)
                heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
                _, buffer = cv2.imencode('.png', heatmap_color)
                heatmap_base64 = base64.b64encode(buffer).decode('utf-8')
        
        if heatmap_base64:
            db.add(XAIArtifact(
                report_id=report.id,
                artifact_type="heatmap",
                data=heatmap_base64,
                xai_version="v1"
            ))
            
        preprocessing = _build_preprocessing_summary(streams, len(chunk_consensus))
        feature_analysis = _build_feature_analysis(agent_results, frontend_agents, chunk_consensus, preprocessing)
        diagnostics = _build_diagnostics(global_consensus, frontend_agents, chunk_consensus)
        _emit_progress(progress_callback, "xai_evidence_graph", message="Computing XAI payloads and evidence graph.")
        xai_payload = _build_xai_payload(chunk_consensus)

        # Save structured Narrative Report
        narrative_payload = NarrativeEngine().generate(
            global_consensus=global_consensus,
            frontend_agents=frontend_agents,
            chunk_consensus=chunk_consensus,
            shap_values=xai_payload["shap_values"],
            counterfactuals=xai_payload["counterfactuals"],
            preprocessing=preprocessing,
            diagnostics=diagnostics,
        )
        evidence_graph = generate_evidence_graph(
            filename=filename,
            preprocessing=preprocessing,
            frontend_agents=frontend_agents,
            chunk_consensus=chunk_consensus,
            global_consensus=global_consensus,
            xai_payload=xai_payload,
            narrative_payload=narrative_payload,
            diagnostics=diagnostics,
        )

        # Save rich XAI Artifact details
        xai_art = XAIArtifact(
            report_id=report.id,
            shap_values=xai_payload["shap_values"],
            counterfactuals=xai_payload["counterfactuals"],
            evidence_graph=evidence_graph,
            shap_summary=xai_payload["shap_summary"],
            counterfactual_summary=xai_payload["counterfactual_summary"],
            xai_version="v1"
        )
        db.add(xai_art)

        _emit_progress(progress_callback, "narrative_persistence", message="Persisting report artifacts.")
        narrative = NarrativeReport(
            report_id=report.id,
            structured_summary=narrative_payload["structured_summary"],
            human_summary=narrative_payload["human_summary"],
            narrative_metadata=narrative_payload["narrative_metadata"],
            generated_by="Deterministic Narrative Engine",
            narrative_version="v1"
        )
        db.add(narrative)
        
        # Save ProcessingMetadata for research reproducibility
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
        db.refresh(report)

        display_timeline = compress_timeline_events(frontend_timeline)

        def _attach_mel_previews(timeline_rows, audio_samples, sample_rate=48000):
            if audio_samples is None or len(audio_samples) == 0:
                return
            for row in timeline_rows:
                start = float(row.get("start_time") or 0.0)
                end = float(row.get("end_time") or start)
                i0 = max(0, int(start * sample_rate))
                i1 = min(len(audio_samples), max(i0 + 1, int(end * sample_rate)))
                row["mel_preview_base64"] = mel_spectrogram_preview_base64(
                    audio_samples[i0:i1], sample_rate
                )

        _attach_mel_previews(display_timeline, audio_48k)
        
        final_response = {
            "id": report.id,
            "filename": report.filename,
            "consensus": {
                "verdict": global_consensus["verdict"],
                "convergence_strength": global_consensus["convergence_strength"],
                "confidence": global_consensus["confidence"],
                "uncertainty": global_consensus.get("uncertainty", 0.0),
                "fake_probability": global_consensus.get("fake_probability"),
                "real_probability": global_consensus.get("real_probability"),
                "probability_margin": global_consensus.get("probability_margin"),
                "decision_threshold": global_consensus.get("decision_threshold")
            },
            "agents": frontend_agents,
            "timeline": display_timeline,
            "timeline_raw_count": len(frontend_timeline),
            "timeline_display_count": len(display_timeline),
            "preprocessing": preprocessing,
            "feature_analysis": feature_analysis,
            "diagnostics": diagnostics,
            "xai": {
                "shap_values": xai_payload["shap_values"],
                "counterfactuals": xai_payload["counterfactuals"],
                "evidence_graph": evidence_graph,
                "shap_summary": xai_payload["shap_summary"],
                "counterfactual_summary": xai_payload["counterfactual_summary"],
            },
            "narrative": {
                "structured_summary": narrative_payload["structured_summary"],
                "human_summary": narrative_payload["human_summary"],
                "metadata": narrative_payload["narrative_metadata"],
            },
            "heatmap_base64": heatmap_base64,
            "processing_metadata": {
                "chunk_duration": 2.0,
                "overlap": 0.5,
                "sample_rates": {
                    "semantic": 16000,
                    "forensic": 48000
                },
                "schema_version": "v2.0",
                "pipeline_version": "forensic_pipeline_v1"
            },
            "created_at": report.created_at.isoformat()
        }
        
        storage_timeline, mel_previews = _extract_mel_previews(final_response["timeline"])
        storage_payload = {
            **final_response,
            "timeline": storage_timeline,
            "mel_previews": mel_previews,
        }
        report.full_response = storage_payload
        db.commit()
        
        _emit_progress(progress_callback, "complete", status="complete", message="Analysis complete.", percent=100)
        return final_response

    except AnalysisUnavailableError as e:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise


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
        return _run_analysis_from_path(temp_path, file.filename, db, report_id=file_id)
    except AnalysisUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _job_progress_callback(job_id):
    def callback(stage, status="running", message=None, percent=None):
        analysis_jobs.update(job_id, stage, status=status, message=message, percent=percent)

    return callback


def _run_analysis_job(job_id, temp_path, filename):
    db = SessionLocal()
    try:
        result = _run_analysis_from_path(
            temp_path,
            filename,
            db,
            report_id=job_id,
            progress_callback=_job_progress_callback(job_id),
        )
        analysis_jobs.update(
            job_id,
            "complete",
            status="complete",
            message="Analysis complete.",
            percent=100,
            result=result,
        )
    except AnalysisUnavailableError as exc:
        analysis_jobs.update(
            job_id,
            "agent_panel",
            status="error",
            message="Analysis unavailable.",
            error=str(exc),
        )
    except Exception as exc:
        analysis_jobs.update(
            job_id,
            "complete",
            status="error",
            message="Analysis failed.",
            error=str(exc),
        )
    finally:
        db.close()
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/jobs")
async def create_analysis_job(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.wav', '.mp3')):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    job_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    temp_path = os.path.join(UPLOADS_DIR, f"{job_id}{ext}")

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    snapshot = analysis_jobs.create(job_id, file.filename)
    background_tasks.add_task(_run_analysis_job, job_id, temp_path, file.filename)
    return snapshot


@router.get("/jobs/{job_id}/progress")
async def get_analysis_job_progress(job_id: str):
    snapshot = analysis_jobs.snapshot(job_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    return snapshot


@router.get("/jobs/{job_id}/result", response_model=AnalysisResponse)
async def get_analysis_job_result(job_id: str):
    snapshot = analysis_jobs.snapshot(job_id, include_result=True)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    if snapshot["status"] == "error":
        raise HTTPException(status_code=500, detail=snapshot["error"] or "Analysis failed")
    if snapshot["status"] != "complete" or snapshot.get("result") is None:
        raise HTTPException(status_code=202, detail="Analysis is still running")
    return snapshot["result"]


@router.get("/jobs/{job_id}/events")
async def stream_analysis_job_events(job_id: str):
    if analysis_jobs.snapshot(job_id) is None:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    async def event_stream():
        last_sequence = None
        while True:
            snapshot = analysis_jobs.snapshot(job_id)
            if snapshot is None:
                yield "event: error\ndata: {\"error\":\"Analysis job not found\"}\n\n"
                break

            if snapshot["sequence"] != last_sequence:
                last_sequence = snapshot["sequence"]
                yield f"data: {json.dumps(snapshot)}\n\n"

            if snapshot["status"] in {"complete", "error"}:
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

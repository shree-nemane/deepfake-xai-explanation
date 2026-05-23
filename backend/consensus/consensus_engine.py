from backend.consensus.calibration_engine import CalibrationEngine
from backend.persistence.database import ConsensusEventType
import numpy as np
import math

class ConsensusEngine:
    """
    Forensic consensus reasoning engine.
    Arbitrates evidence across independent agents, applies agent-specific signal quality
    suppression, propagates uncertainty, and computes Temporal Consensus.
    """
    
    def __init__(self):
        self.calibration = CalibrationEngine()
        
    def _get_sigmoid_suppression(self, global_reliability: float) -> float:
        """Calculates the overall continuous sigmoid suppression factor S(r)."""
        if global_reliability < 0.20:
            return 0.0
        if global_reliability >= 0.80:
            return 1.0
        # Map [0.20, 0.80] to a continuous S-curve normalized to [-3.0, 3.0]
        x = (global_reliability - 0.5) / 0.1
        sig_raw = 1.0 / (1.0 + math.exp(-x))
        sig_min = 1.0 / (1.0 + math.exp(3))
        sig_max = 1.0 / (1.0 + math.exp(-3))
        factor = (sig_raw - sig_min) / (sig_max - sig_min)
        return max(0.0, min(1.0, factor))

    def _calculate_agent_suppression(self, agent_name: str, metrics: dict) -> float:
        """Calculates agent-specific suppression based on specialized acoustic vulnerabilities."""
        if not metrics:
            return 1.0

        snr_db = metrics.get("snr_db", 30.0)
        clipping_ratio = metrics.get("clipping_ratio", 0.0)
        spectral_flatness = metrics.get("spectral_flatness", 0.0)
        rms_energy = metrics.get("rms_energy", 0.05)

        # 1. noise_score: maps SNR [5, 30] to [0, 1]
        if snr_db >= 30.0:
            noise_score = 1.0
        elif snr_db <= 5.0:
            noise_score = 0.0
        else:
            noise_score = (snr_db - 5.0) / 25.0

        # 2. clipping_score: maps clipping_ratio [0.0001, 0.05] to [1, 0]
        if clipping_ratio <= 0.0001:
            clipping_score = 1.0
        elif clipping_ratio >= 0.05:
            clipping_score = 0.0
        else:
            clipping_score = 1.0 - (clipping_ratio / 0.05)

        # 3. compression_score: maps spectral flatness [0.05, 0.50] to [1, 0]
        if spectral_flatness <= 0.05:
            compression_score = 1.0
        elif spectral_flatness >= 0.50:
            compression_score = 0.0
        else:
            compression_score = 1.0 - (spectral_flatness - 0.05) / 0.45

        # 4. speech_quality: maps RMS [0.001, 0.05] to [0.1, 1.0]
        if rms_energy >= 0.05:
            speech_quality = 1.0
        elif rms_energy <= 0.001:
            speech_quality = 0.1
        else:
            speech_quality = 0.1 + 0.9 * (rms_energy - 0.001) / 0.049

        # 5. phase_quality: flat spectra indicate high phase corruption
        phase_quality = max(0.0, min(1.0, 1.0 - 0.5 * spectral_flatness))

        # 6. waveform_quality: compound waveform degradation
        waveform_quality = clipping_score * noise_score

        # Agent-Specific Vulnerability mapping
        if agent_name == "convnext":
            return float(compression_score * speech_quality)
        elif agent_name == "wavlm":
            return float(noise_score * speech_quality)
        elif agent_name == "acoustic":
            return float(clipping_score * phase_quality)
        elif agent_name == "aasist":
            return float(waveform_quality)
        
        return 1.0

    def _evaluate_threat_warnings(self, voting_agents, calibrated_results, agent_results):
        """
        Evaluates structured threat warnings based on contradiction heuristics.
        Implements D-01 (Voice Clone), D-02 (Localized Splice), D-03 (Partial Synthesis).
        Uses raw (pre-calibration) confidence for threshold comparisons.
        Returns a list of structured warning dicts.
        """
        warnings = []
        if not voting_agents:
            return warnings

        # Extract raw verdicts and confidences (pre-calibration)
        def _get_raw(name):
            r = agent_results.get(name, {})
            return r.get("verdict"), r.get("confidence", 0.0)

        wavlm_verdict, wavlm_conf = _get_raw("wavlm")
        acoustic_verdict, acoustic_conf = _get_raw("acoustic")
        convnext_verdict, convnext_conf = _get_raw("convnext")
        aasist_verdict, aasist_conf = _get_raw("aasist")

        # Track agent pairs matched by D-01/D-02 to short-circuit D-03
        matched_agents = set()

        # --- D-01: Voice Clone Threat ---
        # wavlm fake >= 0.70 AND (acoustic real >= 0.70 OR convnext real >= 0.70)
        if wavlm_verdict == "fake" and wavlm_conf >= 0.70:
            triggering = {"wavlm": {"verdict": wavlm_verdict, "confidence": wavlm_conf}}
            d01_fired = False
            if acoustic_verdict == "real" and acoustic_conf >= 0.70:
                triggering["acoustic"] = {"verdict": acoustic_verdict, "confidence": acoustic_conf}
                matched_agents.update({"wavlm", "acoustic"})
                d01_fired = True
            if convnext_verdict == "real" and convnext_conf >= 0.70:
                triggering["convnext"] = {"verdict": convnext_verdict, "confidence": convnext_conf}
                matched_agents.update({"wavlm", "convnext"})
                d01_fired = True
            if d01_fired:
                warnings.append({
                    "threat_type": "voice_clone",
                    "description": "Voice Clone Threat: High-fidelity phonetic cloning suspected; phonetic structures exhibit synthetic entropy, but acoustic properties appear natural.",
                    "triggering_agents": triggering,
                    "severity": "high",
                })

        # --- D-02: Localized Audio Splice Threat ---
        # (aasist fake >= 0.75 OR convnext fake >= 0.75) AND wavlm real
        if wavlm_verdict == "real":
            triggering = {"wavlm": {"verdict": wavlm_verdict, "confidence": wavlm_conf}}
            d02_fired = False
            if aasist_verdict == "fake" and aasist_conf >= 0.75:
                triggering["aasist"] = {"verdict": aasist_verdict, "confidence": aasist_conf}
                matched_agents.update({"aasist", "wavlm"})
                d02_fired = True
            if convnext_verdict == "fake" and convnext_conf >= 0.75:
                triggering["convnext"] = {"verdict": convnext_verdict, "confidence": convnext_conf}
                matched_agents.update({"convnext", "wavlm"})
                d02_fired = True
            if d02_fired:
                warnings.append({
                    "threat_type": "localized_splice",
                    "description": "Localized Splice Threat: Localized waveform/spectral manipulation detected. Synthetic audio inserted into a natural voice recording.",
                    "triggering_agents": triggering,
                    "severity": "high",
                })

        # --- D-03: Partial Synthesis Threat (catch-all) ---
        # Any agent fake >= 0.60 vs any other agent real >= 0.60, excluding D-01/D-02 matched pairs
        all_agents = {
            "wavlm": (wavlm_verdict, wavlm_conf),
            "acoustic": (acoustic_verdict, acoustic_conf),
            "convnext": (convnext_verdict, convnext_conf),
            "aasist": (aasist_verdict, aasist_conf),
        }
        fake_agents = {n: c for n, (v, c) in all_agents.items() if v == "fake" and c >= 0.60}
        real_agents = {n: c for n, (v, c) in all_agents.items() if v == "real" and c >= 0.60}

        d03_fired = False
        for fake_name in fake_agents:
            for real_name in real_agents:
                # Short-circuit: skip pairs already matched by D-01 or D-02
                if {fake_name, real_name}.issubset(matched_agents):
                    continue
                d03_fired = True
                break
            if d03_fired:
                break

        if d03_fired:
            triggering = {}
            for n, c in fake_agents.items():
                triggering[n] = {"verdict": "fake", "confidence": c}
            for n, c in real_agents.items():
                triggering[n] = {"verdict": "real", "confidence": c}
            warnings.append({
                "threat_type": "partial_synthesis",
                "description": "Partial Synthesis Threat: Multi-agent consensus split. Experts disagree on localized temporal properties; inspect temporal features.",
                "triggering_agents": triggering,
                "severity": "elevated",
            })

        return warnings

    def evaluate_chunk_consensus(self, agent_results, global_reliability):
        """
        Evaluates agreement/contradiction for a single chunk using agent-specific suppression,
        sigmoid calibration, and explicit uncertainty propagation.
        """
        # Fail-Closed Threshold Check (< 0.20)
        if global_reliability < 0.20:
            metrics = agent_results.get("reliability", {}).get("evidence", {})
            return {
                "verdict": "inconclusive",
                "consensus_confidence": 0.0,
                "consensus_uncertainty": 1.0,
                "convergence_strength": 0.0,
                "conflict_severity": 0.0,
                "event_type": ConsensusEventType.QUALITY_FAILURE,
                "fake_probability": 0.5,
                "real_probability": 0.5,
                "fake_votes": 0,
                "real_votes": 0,
                "calibrated_details": {},
                "deep_reasoning": ["Fail-closed: Signal reliability is severely degraded (< 0.20). Neural agents skipped."],
                "diagnostic_metrics": metrics
            }

        fake_votes = 0
        real_votes = 0
        fake_support = 0.0
        real_support = 0.0
        total_weight = 0.0
        
        calibrated_results = {}
        metrics = agent_results.get("reliability", {}).get("evidence", {})
        
        # Exclude reliability and inconclusive/error states from direct voting.
        voting_agents = {
            k: v for k, v in agent_results.items()
            if k != "reliability" and v.get("verdict") in {"fake", "real"}
        }
        
        for agent_name, result in voting_agents.items():
            # 1. Compute suppression factors
            agent_supp = self._calculate_agent_suppression(agent_name, metrics)
            sigmoid_supp = self._get_sigmoid_suppression(global_reliability)
            S_i = float(sigmoid_supp * agent_supp)
            
            # 2. Historical base calibration
            calib = self.calibration.calibrate(
                agent_name, 
                result["confidence"], 
                result["uncertainty"], 
                global_reliability
            )
            
            # 3. Apply confidence suppression
            raw_conf = calib["calibrated_confidence"]
            adj_conf = float(0.5 + (raw_conf - 0.5) * S_i)
            
            # 4. Explicit Uncertainty Propagation (beta=2.0)
            raw_unc = calib["calibrated_uncertainty"]
            adj_unc = float(min(1.0, raw_unc * (1.0 + 2.0 * (1.0 - global_reliability))))
            
            calib["adjusted_confidence"] = adj_conf
            calib["adjusted_uncertainty"] = adj_unc
            calib["suppression_factor"] = S_i
            calib["verdict"] = result["verdict"]
            
            calibrated_results[agent_name] = calib
            
            # 5. Calculate voting weight dampened by suppression and propagated uncertainty
            weight = float(calib["effective_reliability"] * (1.0 - adj_unc) * S_i)
            total_weight += weight
            
            if result["verdict"] == "fake":
                fake_votes += 1
                fake_support += adj_conf * weight
                real_support += (1.0 - adj_conf) * weight
            else:
                real_votes += 1
                real_support += adj_conf * weight
                fake_support += (1.0 - adj_conf) * weight
                
        # Determine Consensus
        total_support = fake_support + real_support
        if total_support > 0:
            final_fake_prob = fake_support / total_support
            final_real_prob = real_support / total_support
        else:
            final_fake_prob = 0.5
            final_real_prob = 0.5
            
        if not voting_agents or fake_votes == real_votes:
            verdict = "inconclusive"
            confidence = 0.0 if not voting_agents else max(final_fake_prob, final_real_prob)
        elif final_fake_prob > final_real_prob:
            verdict = "fake"
            confidence = final_fake_prob
        elif final_real_prob > final_fake_prob:
            verdict = "real"
            confidence = final_real_prob
        else:
            verdict = "inconclusive"
            confidence = max(final_fake_prob, final_real_prob)
        
        # Calculate Evidence Convergence Strength
        total_votes = fake_votes + real_votes
        max_votes = max(fake_votes, real_votes)
        convergence_strength = (max_votes / total_votes) if total_votes > 0 else 0
        
        # Heuristic conflict scoring
        conflict_severity = 0.0
        if fake_votes > 0 and real_votes > 0:
            avg_fake_conf = fake_support / total_support if total_support > 0 else 0.5
            avg_real_conf = real_support / total_support if total_support > 0 else 0.5
            conflict_severity = min(1.0, (avg_fake_conf * avg_real_conf) * 4.0)
        
        # Deep Contradiction Analysis — Structured Threat Warnings (D-01, D-02, D-03)
        threat_warnings = self._evaluate_threat_warnings(voting_agents, calibrated_results, agent_results)
        reasoning = [w["description"] for w in threat_warnings]

        # Determine Event Classification Enum using structured warnings
        has_threat = len(threat_warnings) > 0
        has_splice = any(w["threat_type"] in ("voice_clone", "localized_splice") for w in threat_warnings)

        if global_reliability < 0.40:
            event_type = ConsensusEventType.RELIABILITY_WARNING
        elif has_splice:
            # Threat warnings take priority — a voice clone or splice IS the forensic event
            event_type = ConsensusEventType.SPLICE
        elif has_threat:
            event_type = ConsensusEventType.CONTRADICTION
        elif verdict == "inconclusive":
            event_type = ConsensusEventType.RELIABILITY_WARNING if global_reliability < 0.60 else ConsensusEventType.CONTRADICTION
        else:
            if convergence_strength > 0.66:
                event_type = ConsensusEventType.AGREEMENT
            else:
                event_type = ConsensusEventType.CONTRADICTION

        avg_voting_uncertainty = sum(details["adjusted_uncertainty"] for details in calibrated_results.values()) / len(voting_agents) if voting_agents else 1.0

        return {
            "verdict": verdict,
            "consensus_confidence": confidence,
            "consensus_uncertainty": float(avg_voting_uncertainty),
            "convergence_strength": convergence_strength,
            "conflict_severity": conflict_severity,
            "event_type": event_type,
            "fake_probability": final_fake_prob,
            "real_probability": final_real_prob,
            "fake_votes": fake_votes,
            "real_votes": real_votes,
            "calibrated_details": calibrated_results,
            "deep_reasoning": reasoning,
            "threat_warnings": threat_warnings,
            "diagnostic_metrics": metrics
        }

from backend.orchestration.agent_registry import agent_registry
from backend.orchestration.timeline_manager import TimelineManager
from backend.persistence.database import ConsensusEventType
import logging

logger = logging.getLogger(__name__)

_MIN_GLOBAL_DECISION_CONFIDENCE = 0.60
_MIN_GLOBAL_PROBABILITY_MARGIN = 0.08

class AnalysisUnavailableError(RuntimeError):
    """Raised when the analysis pipeline cannot produce a trustworthy result."""

class ForensicOrchestrator:
    """Central nervous system for the forensic intelligence platform."""
    
    def __init__(self):
        import backend.agents  # noqa: F401 - imports register agent modules

        self.timeline_manager = TimelineManager(sample_rate=16000)
        
    def analyze_audio(self, audio_16k, audio_48k):
        """
        Main entry point for forensic analysis.
        Routes audio to appropriate agents and aggregates their findings.
        """
        # 1. Segment the audio into temporally aligned chunks (D-06, D-07, D-08)
        chunks_16k, chunks_48k = self.timeline_manager.create_aligned_chunks(audio_16k, audio_48k)
        
        # 2. Extract active agents from registry
        agents = agent_registry.get_all_agents()
        voting_agents = [agent for agent in agents if agent.name != "reliability"]
        if not voting_agents:
            raise AnalysisUnavailableError("No voting forensic agents are registered.")
        
        agent_results = {agent.name: [] for agent in agents}
        
        # 3. Execution over Chunks
        from backend.consensus.consensus_engine import ConsensusEngine
        consensus_engine = ConsensusEngine()
        
        chunk_level_consensus = []
        for i in range(len(chunks_16k)):
            chunk_16k = chunks_16k[i]
            chunk_48k = chunks_48k[i]  # Temporal alignment verified by create_aligned_chunks
            
            # Log if chunk contains padded regions
            if chunk_16k.get("is_padded", False) or chunk_48k.get("is_padded", False):
                logger.info(f"Chunk {i} contains padded regions (is_padded=True)")
            
            chunk_agent_results = {}
            chunk_reliability = 1.0 # Default if reliability agent fails/missing
            
            # A. First execute the reliability agent
            reliability_agent = next((a for a in agents if a.name == "reliability"), None)
            if reliability_agent:
                target_chunk = chunk_16k if reliability_agent.sample_rate == 16000 else chunk_48k
                rel_result = reliability_agent.analyze_chunk(target_chunk["data"])
                rel_result["start_time"] = target_chunk["start_time"]
                rel_result["end_time"] = target_chunk["end_time"]
                
                agent_results["reliability"].append(rel_result)
                chunk_agent_results["reliability"] = rel_result
                
                if "evidence" in rel_result:
                    chunk_reliability = rel_result.get("evidence", {}).get("reliability_score", 1.0)
            
            # B. Check for hybrid fail-closed
            is_fail_closed = chunk_reliability < 0.20
            
            # C. Run other agents
            for agent in agents:
                if agent.name == "reliability":
                    continue
                
                is_heavy_neural = agent.name in {"convnext", "wavlm"}
                
                if is_fail_closed and is_heavy_neural:
                    # Hybrid fail-closed bypass
                    result = {
                        "verdict": "inconclusive",
                        "confidence": 0.0,
                        "uncertainty": 1.0,
                        "evidence": {
                            "error": "Reliability score below fail-closed threshold (< 0.20)",
                            "fallback_reason": "inference_unavailable",
                            "note": "Fail-closed skip: heavy neural model skipped to save compute.",
                        }
                    }
                else:
                    target_chunk = chunk_16k if agent.sample_rate == 16000 else chunk_48k
                    result = agent.analyze_chunk(target_chunk["data"])
                
                result["start_time"] = target_chunk["start_time"]
                result["end_time"] = target_chunk["end_time"]
                
                agent_results[agent.name].append(result)
                chunk_agent_results[agent.name] = result
                
            # 4. Trigger Consensus Engine for this chunk using dynamic reliability
            chunk_consensus = consensus_engine.evaluate_chunk_consensus(chunk_agent_results, chunk_reliability)
            chunk_consensus["start_time"] = chunk_16k["start_time"]
            chunk_consensus["end_time"] = chunk_16k["end_time"]
            chunk_consensus["is_padded"] = chunk_16k.get("is_padded", False) or chunk_48k.get("is_padded", False)
            chunk_level_consensus.append(chunk_consensus)
            
        # 5. Global Aggregation
        global_consensus = self._calculate_global_consensus(chunk_level_consensus)
        
        return {
            "agent_results": agent_results,
            "chunk_consensus": chunk_level_consensus,
            "global_consensus": global_consensus
        }
        
    def _calculate_global_consensus(self, chunk_level_consensus):
        """Aggregate chunk-level consensus into a single file-level verdict."""
        if not chunk_level_consensus:
            return {
                "verdict": "inconclusive",
                "confidence": 0.0,
                "uncertainty": 1.0,
                "convergence_strength": 0.0,
                "fake_ratio": 0.0,
                "real_ratio": 0.0,
                "fake_probability": 0.5,
                "real_probability": 0.5,
                "probability_margin": 0.0,
                "decision_threshold": _MIN_GLOBAL_DECISION_CONFIDENCE
            }
            
        fake_chunks = sum(1 for c in chunk_level_consensus if c["verdict"] == "fake")
        real_chunks = sum(1 for c in chunk_level_consensus if c["verdict"] == "real")
        total_chunks = len(chunk_level_consensus)
        
        fake_ratio = fake_chunks / total_chunks
        real_ratio = real_chunks / total_chunks
        avg_fake_probability = sum(c.get("fake_probability", 0.5) for c in chunk_level_consensus) / total_chunks
        avg_real_probability = sum(c.get("real_probability", 0.5) for c in chunk_level_consensus) / total_chunks
        avg_confidence = max(avg_fake_probability, avg_real_probability)

        probability_margin = abs(avg_fake_probability - avg_real_probability)
        if probability_margin < _MIN_GLOBAL_PROBABILITY_MARGIN or avg_confidence < _MIN_GLOBAL_DECISION_CONFIDENCE:
            verdict = "inconclusive"
        elif avg_fake_probability > avg_real_probability:
            verdict = "fake"
        elif avg_real_probability > avg_fake_probability:
            verdict = "real"
        else:
            verdict = "inconclusive"
        
        avg_convergence = sum(c["convergence_strength"] for c in chunk_level_consensus) / total_chunks
        avg_uncertainty = sum(c.get("consensus_uncertainty", 1.0) for c in chunk_level_consensus) / total_chunks
        
        return {
            "verdict": verdict,
            "confidence": avg_confidence,
            "uncertainty": avg_uncertainty,
            "convergence_strength": avg_convergence,
            "fake_ratio": fake_ratio,
            "real_ratio": real_ratio,
            "fake_probability": avg_fake_probability,
            "real_probability": avg_real_probability,
            "probability_margin": probability_margin,
            "decision_threshold": _MIN_GLOBAL_DECISION_CONFIDENCE
        }

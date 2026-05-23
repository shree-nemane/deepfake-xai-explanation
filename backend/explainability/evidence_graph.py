class EvidenceGraph:
    """
    Constructs a graph linking agents, anomalies, and timestamps to explain
    how the consensus was reached.
    """
    
    def __init__(self):
        self.nodes = []
        self.edges = []
        
    def add_agent_node(self, agent_name, verdict, confidence):
        node_id = f"agent_{agent_name}"
        self.nodes.append({
            "id": node_id,
            "type": "agent",
            "label": agent_name,
            "verdict": verdict,
            "confidence": confidence
        })
        return node_id
        
    def add_evidence_node(self, anomaly_type, severity, timestamp):
        node_id = f"evidence_{anomaly_type}_{timestamp}"
        self.nodes.append({
            "id": node_id,
            "type": "evidence",
            "label": anomaly_type,
            "severity": severity,
            "timestamp": timestamp
        })
        return node_id
        
    def link(self, source_id, target_id, relation_type):
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "relation": relation_type
        })
        
    def export(self):
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }

def generate_evidence_graph(consensus_results, timeline_events):
    """Factory function to build the graph from orchestrator outputs."""
    graph = EvidenceGraph()
    # TODO: Populate graph based on actual consensus events
    return graph.export()

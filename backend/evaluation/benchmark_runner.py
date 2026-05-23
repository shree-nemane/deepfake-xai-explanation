import os
import json
import argparse
import re
from datetime import datetime
from tqdm import tqdm
from collections import defaultdict
from pathlib import Path

from backend.preprocessing.audio_processor import AudioProcessor
from backend.orchestration.forensic_orchestrator import ForensicOrchestrator
from backend.agents.model_hub import model_hub

class BenchmarkRunner:
    """
    Evaluation framework to run large-scale testing on datasets and calculate
    global consensus accuracy, as well as individual agent accuracy.
    """
    
    def __init__(self, output_dir="evaluation_results"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        print("Initializing Forensic Intelligence Platform for Benchmarking...")
        # Pre-load heavy PyTorch artifacts into memory once
        model_hub.preload_all()
        
        self.audio_processor = AudioProcessor()
        self.orchestrator = ForensicOrchestrator()
        
        self.reset_metrics()
        
    def reset_metrics(self):
        self.metrics = {
            "total_processed": 0,
            "failed_files": 0,
            "global": {"TP": 0, "FP": 0, "TN": 0, "FN": 0, "ABSTAIN": 0},
            "agents": defaultdict(lambda: {"TP": 0, "FP": 0, "TN": 0, "FN": 0, "ABSTAIN": 0}),
            "consensus_events": defaultdict(int),
            "convergence_strength": {"correct": [], "incorrect": []}
        }
        self.raw_results = []
        
    def infer_ground_truth(self, filepath):
        """Infer ground truth from exact label tokens in file or parent names."""
        path = Path(filepath)
        tokens = []
        for part in [path.stem, *path.parent.parts]:
            tokens.extend(token for token in re.split(r"[^a-z0-9]+", part.lower()) if token)

        if {"fake", "spoof", "spoofed", "synthetic"} & set(tokens):
            return 'fake'
        elif {"real", "bonafide", "bona", "genuine", "authentic"} & set(tokens):
            return 'real'
        return 'unknown'

    def update_confusion_matrix(self, matrix, prediction, ground_truth):
        if prediction == 'fake' and ground_truth == 'fake':
            matrix["TP"] += 1
        elif prediction == 'fake' and ground_truth == 'real':
            matrix["FP"] += 1
        elif prediction == 'real' and ground_truth == 'real':
            matrix["TN"] += 1
        elif prediction == 'real' and ground_truth == 'fake':
            matrix["FN"] += 1
        else:
            matrix["ABSTAIN"] += 1

    def calculate_stats(self, matrix):
        tp, fp, tn, fn = matrix["TP"], matrix["FP"], matrix["TN"], matrix["FN"]
        abstain = matrix.get("ABSTAIN", 0)
        total = tp + fp + tn + fn + abstain
        accuracy = (tp + tn) / total if total > 0 else 0
        decisive_total = tp + fp + tn + fn
        decisive_accuracy = (tp + tn) / decisive_total if decisive_total > 0 else 0
        coverage = decisive_total / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "total": total,
            "abstentions": abstain,
            "coverage": coverage,
            "decisive_accuracy": decisive_accuracy,
        }

    def process_file(self, filepath, ground_truth):
        try:
            streams = self.audio_processor.process_dual_stream(filepath)
            results = self.orchestrator.analyze_audio(streams["16k"], streams["48k"])
            
            global_consensus = results["global_consensus"]
            pred = global_consensus["verdict"]
            
            # Global Metrics
            self.update_confusion_matrix(self.metrics["global"], pred, ground_truth)
            
            # Track convergence correlation
            is_correct = (pred == ground_truth)
            conv_str = global_consensus["convergence_strength"]
            if is_correct:
                self.metrics["convergence_strength"]["correct"].append(conv_str)
            else:
                self.metrics["convergence_strength"]["incorrect"].append(conv_str)
                
            # Agent Metrics (Aggregate their chunk verdicts via simple majority voting)
            for agent_name, chunks in results["agent_results"].items():
                if not chunks: continue
                if agent_name == "reliability":
                    continue

                voting_chunks = [c for c in chunks if c.get("verdict") in {"fake", "real"}]
                if not voting_chunks:
                    agent_pred = "inconclusive"
                else:
                    fake_votes = sum(1 for c in voting_chunks if c.get("verdict") == "fake")
                    real_votes = sum(1 for c in voting_chunks if c.get("verdict") == "real")
                    if fake_votes > real_votes:
                        agent_pred = "fake"
                    elif real_votes > fake_votes:
                        agent_pred = "real"
                    else:
                        agent_pred = "inconclusive"
                self.update_confusion_matrix(self.metrics["agents"][agent_name], agent_pred, ground_truth)
                
            # Consensus Events
            for event in results["chunk_consensus"]:
                self.metrics["consensus_events"][event["event_type"]] += 1
                
            self.metrics["total_processed"] += 1
            
            self.raw_results.append({
                "file": filepath,
                "ground_truth": ground_truth,
                "prediction": pred,
                "is_correct": is_correct,
                "confidence": global_consensus["confidence"],
                "convergence_strength": conv_str
            })
            
        except Exception as e:
            print(f"\\nError processing {filepath}: {str(e)}")
            self.metrics["failed_files"] += 1

    def run_benchmark(self, dataset_dir):
        self.reset_metrics()
        
        # Collect all audio files
        audio_files = []
        for root, _, files in os.walk(dataset_dir):
            for file in files:
                if file.lower().endswith(('.wav', '.mp3', '.flac')):
                    filepath = os.path.join(root, file)
                    gt = self.infer_ground_truth(filepath)
                    if gt != 'unknown':
                        audio_files.append((filepath, gt))
                        
        print(f"Found {len(audio_files)} labeled audio files.")
        
        for filepath, gt in tqdm(audio_files, desc="Running Benchmark"):
            self.process_file(filepath, gt)
            
        self.generate_report()

    def generate_report(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate stats
        global_stats = self.calculate_stats(self.metrics["global"])
        agent_stats = {name: self.calculate_stats(matrix) for name, matrix in self.metrics["agents"].items()}
        
        avg_corr = sum(self.metrics["convergence_strength"]["correct"]) / max(1, len(self.metrics["convergence_strength"]["correct"]))
        avg_incorr = sum(self.metrics["convergence_strength"]["incorrect"]) / max(1, len(self.metrics["convergence_strength"]["incorrect"]))
        
        report = {
            "timestamp": timestamp,
            "metrics": {
                "total_processed": self.metrics["total_processed"],
                "failed_files": self.metrics["failed_files"],
                "global_performance": global_stats,
                "agent_performance": agent_stats,
                "consensus_events": dict(self.metrics["consensus_events"]),
                "convergence_correlation": {
                    "avg_strength_when_correct": avg_corr,
                    "avg_strength_when_incorrect": avg_incorr
                }
            },
            "raw_results": self.raw_results
        }
        
        filepath = os.path.join(self.output_dir, f"benchmark_{timestamp}.json")
        with open(filepath, "w") as f:
            json.dump(report, f, indent=4)
            
        self.print_summary(report["metrics"])
        print(f"\\nDetailed report saved to {filepath}")
        
    def print_summary(self, metrics):
        print("\\n" + "="*50)
        print(" BENCHMARK RESULTS SUMMARY")
        print("="*50)
        print(f"Files Processed : {metrics['total_processed']}")
        print(f"Failed Files    : {metrics['failed_files']}")
        print("-" * 50)
        
        gp = metrics["global_performance"]
        print(f"GLOBAL CONSENSUS ENGINE")
        print(f"Accuracy  : {gp['accuracy']:.2%}")
        print(f"Coverage  : {gp['coverage']:.2%}")
        print(f"Decisive Accuracy : {gp['decisive_accuracy']:.2%}")
        print(f"Abstentions       : {gp['abstentions']}")
        print(f"Precision : {gp['precision']:.2%}")
        print(f"Recall    : {gp['recall']:.2%}")
        print(f"F1-Score  : {gp['f1_score']:.2%}")
        print("-" * 50)
        
        print("INDIVIDUAL AGENT ACCURACY")
        for agent, stats in metrics["agent_performance"].items():
            print(f"{agent.ljust(12)}: {stats['accuracy']:.2%}")
            
        print("-" * 50)
        print("CONVERGENCE INTELLIGENCE")
        cc = metrics["convergence_correlation"]
        print(f"Avg Strength (Correct Predictions)   : {cc['avg_strength_when_correct']:.2f}")
        print(f"Avg Strength (Incorrect Predictions) : {cc['avg_strength_when_incorrect']:.2f}")
        print("="*50 + "\\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forensic Intelligence Platform Benchmark")
    parser.add_argument("--dataset", type=str, required=True, help="Path to evaluation dataset directory")
    parser.add_argument("--output", type=str, default="evaluation_results", help="Output directory for reports")
    args = parser.parse_args()
    
    runner = BenchmarkRunner(output_dir=args.output)
    runner.run_benchmark(args.dataset)

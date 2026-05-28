# ==============================================================================
# JEE MENTOR AI - MODEL PERFORMANCE BENCHMARK SUITE
# ==============================================================================
import os
import json
import time
from typing import List, Dict, Any
from sqlalchemy.orm import Session

# Import backend modules
from backend.database import SessionLocal
from backend.orchestrator import JEEOrchestrator

class JEEBenchmarkSuite:
    def __init__(self, dataset_path: str = "dataset/cleaned_jee_dataset.json"):
        self.dataset_path = dataset_path
        self.output_json = "evaluation/benchmark_runs.json"
        os.makedirs("evaluation", exist_ok=True)

    def load_test_cases(self, count: int = 5) -> List[Dict[str, Any]]:
        """Loads a subset of ground truth JEE questions for benchmarking."""
        if not os.path.exists(self.dataset_path):
            print(f"[ERROR] Evaluation dataset not found at: {self.dataset_path}")
            return []
            
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Draw a representative slice of count questions
        return data[:count]

    def run_benchmark(self, sample_size: int = 5):
        """Executes the solver pipeline over test cases and saves detailed runs."""
        print(f"[INFO] Initializing Benchmark run over {sample_size} test cases...")
        
        db = SessionLocal()
        orchestrator = JEEOrchestrator(db)
        
        test_cases = self.load_test_cases(sample_size)
        if not test_cases:
            print("[ERROR] No benchmark test cases available. Aborting run.")
            return

        runs = []
        
        for idx, case in enumerate(test_cases):
            print(f"[INFO] Benchmarking Question {idx+1}/{len(test_cases)} [{case['subject']} - {case['topic']}]")
            
            # Start timer
            start_time = time.time()
            
            # Execute solver
            solve_res = orchestrator.orchestrate_question_solve(
                question_text=case["input"],
                subject=case["subject"]
            )
            
            duration = (time.time() - start_time) * 1000
            
            runs.append({
                "id": f"bench_{idx+1}",
                "subject": case["subject"],
                "topic": case["topic"],
                "difficulty": case["difficulty"],
                "input": case["input"],
                "ground_truth_output": case["output"],
                "predicted_output": solve_res["solution"],
                "formulas_used": solve_res["formulas_used"],
                "latency_ms": round(duration, 2)
            })
            
            # Brief cooldown to prevent CPU stress
            time.sleep(0.5)

        # Write results
        with open(self.output_json, "w", encoding="utf-8") as f:
            json.dump(runs, f, indent=2, ensure_ascii=False)
            
        print(f"[SUCCESS] Benchmark complete! Logged detailed runs to: {self.output_json}")
        db.close()

if __name__ == "__main__":
    bench = JEEBenchmarkSuite()
    bench.run_benchmark(sample_size=3)

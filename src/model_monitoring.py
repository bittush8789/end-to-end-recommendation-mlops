import os
import json
import logging
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelMonitoring:
    """
    Lightweight model monitoring using statistical drift detection.
    Tracks data drift, prediction drift, and generates JSON reports.
    Evidently AI integration can be substituted here when the package is available.
    """
    
    def __init__(self, reference_data_path: str = "data/user_interactions.csv",
                 reports_dir: str = "artifacts/monitoring"):
        self.reference_data_path = reference_data_path
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)
        
    def load_reference_data(self) -> pd.DataFrame:
        return pd.read_csv(self.reference_data_path)

    def compute_column_stats(self, df: pd.DataFrame, col: str) -> dict:
        """Compute basic statistical distribution for a numeric column."""
        series = df[col].dropna()
        return {
            "mean": round(float(series.mean()), 4),
            "std": round(float(series.std()), 4),
            "min": round(float(series.min()), 4),
            "max": round(float(series.max()), 4),
            "count": int(series.count()),
            "pct_25": round(float(series.quantile(0.25)), 4),
            "pct_75": round(float(series.quantile(0.75)), 4)
        }

    def detect_data_drift(self, current_df: pd.DataFrame) -> dict:
        """Compare current data statistics vs reference to flag potential drift."""
        reference_df = self.load_reference_data()
        
        numeric_cols = ["rating", "views", "clicks", "purchased"]
        drift_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "reference_rows": len(reference_df),
            "current_rows": len(current_df),
            "columns": {}
        }
        
        drift_detected = False
        
        for col in numeric_cols:
            if col not in reference_df.columns or col not in current_df.columns:
                continue
                
            ref_stats = self.compute_column_stats(reference_df, col)
            cur_stats = self.compute_column_stats(current_df, col)
            
            # Simple drift detection: flag if mean shifts by > 15%
            mean_shift_pct = abs(cur_stats["mean"] - ref_stats["mean"]) / (ref_stats["mean"] + 1e-9) * 100
            is_drifted = mean_shift_pct > 15.0
            
            if is_drifted:
                drift_detected = True
                
            drift_report["columns"][col] = {
                "reference": ref_stats,
                "current": cur_stats,
                "mean_shift_pct": round(mean_shift_pct, 2),
                "drift_detected": is_drifted
            }
            
        drift_report["overall_drift_detected"] = drift_detected
        
        # Save report
        report_path = os.path.join(self.reports_dir, "data_drift_report.json")
        with open(report_path, "w") as f:
            json.dump(drift_report, f, indent=4)
            
        logger.info(f"Data drift report saved: {report_path}. Drift detected: {drift_detected}")
        return drift_report

    def generate_prediction_drift_report(self, baseline_scores: list, current_scores: list) -> dict:
        """Compare recommendation score distributions between baseline and current model outputs."""
        import statistics
        
        def stats(scores):
            return {
                "mean": round(statistics.mean(scores), 4),
                "stdev": round(statistics.stdev(scores) if len(scores) > 1 else 0, 4),
                "min": round(min(scores), 4),
                "max": round(max(scores), 4)
            }
            
        baseline_stats = stats(baseline_scores)
        current_stats  = stats(current_scores)
        
        shift = abs(current_stats["mean"] - baseline_stats["mean"]) / (baseline_stats["mean"] + 1e-9) * 100
        drift_detected = shift > 20.0
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "baseline_scores": baseline_stats,
            "current_scores": current_stats,
            "mean_shift_pct": round(shift, 2),
            "drift_detected": drift_detected
        }
        
        report_path = os.path.join(self.reports_dir, "prediction_drift_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=4)
            
        logger.info(f"Prediction drift report saved: {report_path}. Drift detected: {drift_detected}")
        return report

    def run_full_monitoring(self, current_data_path: str = None) -> dict:
        """Runs the complete monitoring suite and returns combined results."""
        logger.info("Running full model monitoring suite...")
        
        current_path = current_data_path or self.reference_data_path
        current_df = pd.read_csv(current_path)
        
        drift_report = self.detect_data_drift(current_df)
        
        # Simulate baseline vs current recommendation scores (replace with real model outputs in prod)
        import numpy as np
        np.random.seed(1)
        baseline_scores = list(np.random.uniform(0.4, 0.8, 200))
        current_scores  = list(np.random.uniform(0.35, 0.75, 200))
        
        pred_report = self.generate_prediction_drift_report(baseline_scores, current_scores)
        
        summary = {
            "data_drift": drift_report["overall_drift_detected"],
            "prediction_drift": pred_report["drift_detected"],
            "reports_dir": self.reports_dir
        }
        
        logger.info(f"Monitoring summary: {summary}")
        return summary

if __name__ == "__main__":
    monitor = ModelMonitoring()
    results = monitor.run_full_monitoring()
    print("\nMonitoring Results:", json.dumps(results, indent=2))

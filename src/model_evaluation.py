import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from data_ingestion import DataIngestion
from feature_engineering import FeatureEngineering
from recommendation_engine import RecommendationEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelEvaluation:
    def __init__(self, artifacts_dir: str = "artifacts", k: int = 10):
        self.artifacts_dir = artifacts_dir
        self.k = k
        self.report_path = os.path.join(self.artifacts_dir, "evaluation_report.json")
        
    def evaluate(self, engine: RecommendationEngine, df_test_interactions: pd.DataFrame) -> Dict[str, float]:
        """Evaluates recommendation quality metrics (Precision@K, Recall@K, MAP, NDCG) on test set."""
        logger.info(f"Evaluating model recommendations at K={self.k}...")
        
        # Filter test interactions to keep only positive ones (e.g. rating >= 3.0 or purchased == 1)
        # to represent relevant items
        df_test_pos = df_test_interactions[df_test_interactions["rating"] >= 3.0]
        
        if df_test_pos.empty:
            logger.warning("No positive test interactions to evaluate against.")
            return {"precision_at_k": 0.0, "recall_at_k": 0.0, "map": 0.0, "ndcg": 0.0}
            
        precisions = []
        recalls = []
        average_precisions = []
        ndcgs = []
        
        test_users = df_test_pos["user_id"].unique()
        
        for user_id in test_users:
            # Positive product list in test set for this user
            actual_relevant = set(df_test_pos[df_test_pos["user_id"] == user_id]["product_id"])
            if not actual_relevant:
                continue
                
            # Get model top-K recommendations
            recs = engine.recommend_for_user(user_id, top_n=self.k)
            rec_pids = [r["product_id"] for r in recs]
            
            # 1. Precision@K
            hits = sum(1 for pid in rec_pids if pid in actual_relevant)
            precision = hits / len(rec_pids) if rec_pids else 0.0
            precisions.append(precision)
            
            # 2. Recall@K
            recall = hits / len(actual_relevant) if actual_relevant else 0.0
            recalls.append(recall)
            
            # 3. MAP (Mean Average Precision)
            ap = 0.0
            running_hits = 0
            for i, pid in enumerate(rec_pids):
                if pid in actual_relevant:
                    running_hits += 1
                    ap += running_hits / (i + 1)
            ap /= min(len(actual_relevant), self.k) if actual_relevant else 1.0
            average_precisions.append(ap)
            
            # 4. NDCG (Normalized Discounted Cumulative Gain)
            dcg = 0.0
            for i, pid in enumerate(rec_pids):
                if pid in actual_relevant:
                    dcg += 1.0 / np.log2(i + 2)
            idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(actual_relevant), self.k)))
            ndcg = dcg / idcg if idcg > 0 else 0.0
            ndcgs.append(ndcg)
            
        metrics = {
            "precision_at_k": round(float(np.mean(precisions)), 4),
            "recall_at_k": round(float(np.mean(recalls)), 4),
            "map_at_k": round(float(np.mean(average_precisions)), 4),
            "ndcg_at_k": round(float(np.mean(ndcgs)), 4),
            "evaluated_users_count": len(test_users)
        }
        
        # Write report
        with open(self.report_path, "w") as f:
            json.dump(metrics, f, indent=4)
        logger.info(f"Evaluation report saved to {self.report_path}")
        
        return metrics

if __name__ == "__main__":
    # Test run
    ingestor = DataIngestion()
    prod, inter = ingestor.load_data()
    
    # Run a simple split
    np.random.seed(42)
    msk = np.random.rand(len(inter)) < 0.8
    train_inter = inter[msk]
    test_inter = inter[~msk]
    
    fe = FeatureEngineering()
    u_feat, p_feat = fe.transform(prod, train_inter)
    
    engine = RecommendationEngine(n_factors=10)
    engine.fit(prod, train_inter, u_feat, p_feat)
    
    evaluator = ModelEvaluation(k=10)
    metrics = evaluator.evaluate(engine, test_inter)
    print("Evaluation Metrics Summary:\n", json.dumps(metrics, indent=2))

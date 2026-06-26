import os
import sys
import numpy as np
import mlflow
import logging

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from data_ingestion import DataIngestion
from data_validation import DataValidation
from feature_engineering import FeatureEngineering
from model_training import train_model
from recommendation_engine import RecommendationEngine
from model_evaluation import ModelEvaluation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("Starting Recommendation Platform Training Pipeline...")
    
    # 1. Ingest Data
    ingestor = DataIngestion()
    products, interactions = ingestor.load_data()
    
    # 2. Validate Data
    validator = DataValidation()
    val_report = validator.validate(products, interactions)
    if val_report["status"] != "SUCCESS":
        logger.error("Validation failed. Pipeline aborted.")
        sys.exit(1)
        
    # 3. Train/Test Split for Evaluation
    np.random.seed(42)
    mask = np.random.rand(len(interactions)) < 0.8
    train_interactions = interactions[mask]
    test_interactions = interactions[~mask]
    
    # 4. Feature Engineering
    fe = FeatureEngineering()
    user_features, product_features = fe.transform(products, train_interactions)
    
    # 5. Fit & Save Model
    mlflow.set_experiment("Ecommerce_Recommendation_System")
    with mlflow.start_run(run_name="Full_Pipeline_Run") as run:
        logger.info("Fitting and evaluating hybrid model...")
        
        n_factors = 15
        collab_w = 0.7
        content_w = 0.3
        
        engine = RecommendationEngine(n_factors=n_factors, collaborative_weight=collab_w, content_weight=content_w)
        engine.fit(products, train_interactions, user_features, product_features)
        
        # Save model
        model_path = os.path.join("artifacts", "model.pkl")
        engine.save(model_path)
        
        # Evaluate
        evaluator = ModelEvaluation(k=10)
        metrics = evaluator.evaluate(engine, test_interactions)
        
        # Log to MLflow
        mlflow.log_param("n_factors", n_factors)
        mlflow.log_param("collab_weight", collab_w)
        mlflow.log_param("content_weight", content_w)
        
        for k, v in metrics.items():
            mlflow.log_metric(k, v)
            
        mlflow.log_artifact(model_path)
        mlflow.log_artifact(validator.report_path)
        mlflow.log_artifact(evaluator.report_path)
        
        logger.info(f"Pipeline run complete. Run ID: {run.info.run_id}")
        print("Pipeline Metrics:\n", metrics)

if __name__ == "__main__":
    run_pipeline()

import os
import mlflow
import logging
import pandas as pd
from data_ingestion import DataIngestion
from feature_engineering import FeatureEngineering
from recommendation_engine import RecommendationEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_model(n_factors: int = 15, collab_weight: float = 0.7, content_weight: float = 0.3) -> None:
    logger.info("Initializing MLflow experiment...")
    mlflow.set_experiment("Ecommerce_Recommendation_System")
    
    with mlflow.start_run():
        # Load and validate
        ingestor = DataIngestion()
        products, interactions = ingestor.load_data()
        
        fe = FeatureEngineering()
        user_features, product_features = fe.transform(products, interactions)
        
        # Log params
        mlflow.log_param("n_factors", n_factors)
        mlflow.log_param("collaborative_weight", collab_weight)
        mlflow.log_param("content_weight", content_weight)
        mlflow.log_param("num_users", len(user_features))
        mlflow.log_param("num_products", len(product_features))
        
        # Create recommendation engine
        engine = RecommendationEngine(
            n_factors=n_factors,
            collaborative_weight=collab_weight,
            content_weight=content_weight
        )
        
        engine.fit(products, interactions, user_features, product_features)
        
        # Save model artifact
        model_path = os.path.join("artifacts", "model.pkl")
        engine.save(model_path)
        
        # Log artifact to MLflow
        mlflow.log_artifact(model_path)
        
        # Metrics - dummy/placeholder verification metric or feature count
        mlflow.log_metric("total_users", len(user_features))
        mlflow.log_metric("total_products", len(product_features))
        mlflow.log_metric("total_interactions", len(interactions))
        
        logger.info("Model training completed and logged to MLflow successfully.")

if __name__ == "__main__":
    train_model()

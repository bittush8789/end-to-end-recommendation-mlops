import os
import sys
import logging
from typing import List, Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from recommendation_engine import RecommendationEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PredictionPipeline:
    def __init__(self, model_path: str = "artifacts/model.pkl"):
        self.model_path = model_path
        self.engine = None
        self.load_model()
        
    def load_model(self) -> None:
        """Loads recommendation model from pickle file. Generates one if it doesn't exist."""
        if not os.path.exists(self.model_path):
            logger.warning(f"Model file {self.model_path} not found. Running training pipeline first...")
            from training_pipeline import run_pipeline
            run_pipeline()
            
        try:
            self.engine = RecommendationEngine.load(self.model_path)
        except Exception as e:
            logger.error(f"Error loading model from {self.model_path}: {e}")
            # Try retraining
            from training_pipeline import run_pipeline
            run_pipeline()
            self.engine = RecommendationEngine.load(self.model_path)

    def get_user_recommendations(self, user_id: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """Returns top N recommended products for a given user."""
        if not self.engine:
            self.load_model()
        return self.engine.recommend_for_user(user_id, top_n=top_n)

    def get_similar_products(self, product_id: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Returns top N similar products for a product."""
        if not self.engine:
            self.load_model()
        return self.engine.recommend_similar_products(product_id, top_n=top_n)

    def get_trending_products(self, top_n: int = 6) -> Dict[str, List[Dict[str, Any]]]:
        """Returns dict of trending products."""
        if not self.engine:
            self.load_model()
        return self.engine.get_trending_products(top_n=top_n)

    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Searches products matching name or category."""
        if not self.engine or self.engine.df_products is None:
            self.load_model()
            
        df = self.engine.df_products
        query = query.lower()
        
        matches = df[
            df["product_name"].str.lower().str.contains(query) | 
            df["category"].str.lower().str.contains(query)
        ]
        
        res = []
        for _, row in matches.iterrows():
            res.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "category": row["category"],
                "description": row["description"]
            })
        return res

if __name__ == "__main__":
    pipeline = PredictionPipeline()
    recs = pipeline.get_user_recommendations("U001", top_n=2)
    print("User Recommendations for U001:\n", recs)

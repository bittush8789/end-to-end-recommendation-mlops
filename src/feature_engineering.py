import os
import logging
import pandas as pd
from typing import Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureEngineering:
    def __init__(self):
        pass
        
    def transform(self, df_products: pd.DataFrame, df_interactions: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Engineers user features and product features from the raw inputs."""
        logger.info("Engineering features for users and products...")
        
        # 1. User Features
        # Total Purchases
        user_purchases = df_interactions.groupby("user_id")["purchased"].sum().reset_index(name="user_total_purchases")
        # Average Rating
        user_ratings = df_interactions.groupby("user_id")["rating"].mean().reset_index(name="user_avg_rating")
        # Purchase Frequency (ratio of purchased items to total items interacted)
        user_total_interactions = df_interactions.groupby("user_id").size().reset_index(name="user_total_interactions")
        
        user_features = pd.merge(user_purchases, user_ratings, on="user_id", how="outer")
        user_features = pd.merge(user_features, user_total_interactions, on="user_id", how="outer")
        user_features["user_purchase_frequency"] = (
            user_features["user_total_purchases"] / user_features["user_total_interactions"]
        ).fillna(0.0)
        
        # 2. Product Features
        # Product Popularity (total views, clicks, purchases)
        prod_stats = df_interactions.groupby("product_id").agg({
            "views": "sum",
            "clicks": "sum",
            "purchased": "sum",
            "rating": ["mean", "count"]
        })
        prod_stats.columns = [
            "product_total_views",
            "product_total_clicks",
            "product_total_purchases",
            "product_avg_rating",
            "product_interaction_count"
        ]
        prod_stats = prod_stats.reset_index()
        
        # Merge with products for category features
        product_features = pd.merge(df_products, prod_stats, on="product_id", how="left")
        
        # Category Popularity score (average purchases in that category)
        cat_scores = product_features.groupby("category")["product_total_purchases"].mean().reset_index(name="category_avg_purchases")
        product_features = pd.merge(product_features, cat_scores, on="category", how="left")
        
        # Fill NaNs for products that had no interactions
        product_features["product_total_views"] = product_features["product_total_views"].fillna(0)
        product_features["product_total_clicks"] = product_features["product_total_clicks"].fillna(0)
        product_features["product_total_purchases"] = product_features["product_total_purchases"].fillna(0)
        product_features["product_avg_rating"] = product_features["product_avg_rating"].fillna(0.0)
        product_features["product_interaction_count"] = product_features["product_interaction_count"].fillna(0)
        
        logger.info("Feature engineering completed successfully.")
        return user_features, product_features

if __name__ == "__main__":
    from data_ingestion import DataIngestion
    ingestor = DataIngestion()
    prod, inter = ingestor.load_data()
    fe = FeatureEngineering()
    u_feat, p_feat = fe.transform(prod, inter)
    print("User Features preview:\n", u_feat.head(2))
    print("Product Features preview:\n", p_feat.head(2))

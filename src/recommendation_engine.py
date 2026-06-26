import os
import pickle
import logging
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from typing import List, Dict, Any, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self, n_factors: int = 10, collaborative_weight: float = 0.7, content_weight: float = 0.3):
        self.n_factors = n_factors
        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight
        
        # State variables to be serialized
        self.df_products: pd.DataFrame = None
        self.df_interactions: pd.DataFrame = None
        
        # Collaborative filtering state
        self.user_to_idx: Dict[str, int] = {}
        self.idx_to_user: Dict[int, str] = {}
        self.product_to_idx: Dict[str, int] = {}
        self.idx_to_product: Dict[int, str] = {}
        self.reconstructed_ratings: np.ndarray = None
        self.product_latent_features: np.ndarray = None
        
        # Content-based filtering state
        self.tfidf_vectorizer: TfidfVectorizer = None
        self.tfidf_matrix: np.ndarray = None
        
        # Feature engineered caches
        self.user_features: pd.DataFrame = None
        self.product_features: pd.DataFrame = None

    def fit(self, df_products: pd.DataFrame, df_interactions: pd.DataFrame, user_features: pd.DataFrame, product_features: pd.DataFrame) -> None:
        """Trains the collaborative, content-based, and hybrid sub-models."""
        logger.info("Fitting hybrid recommendation engine...")
        self.df_products = df_products.copy()
        self.df_interactions = df_interactions.copy()
        self.user_features = user_features.copy()
        self.product_features = product_features.copy()
        
        # 1. Fit Content-Based Model
        logger.info("Fitting content-based TF-IDF model...")
        # Create rich descriptions by merging category and description text
        texts = (self.df_products["category"].fillna("") + " " + self.df_products["description"].fillna("")).tolist()
        self.tfidf_vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
        
        # 2. Fit Collaborative Filtering (SVD Matrix Factorization)
        logger.info("Fitting collaborative filtering TruncatedSVD model...")
        users = sorted(self.df_interactions["user_id"].unique())
        products = sorted(self.df_products["product_id"].unique())
        
        self.user_to_idx = {uid: i for i, uid in enumerate(users)}
        self.idx_to_user = {i: uid for i, uid in enumerate(users)}
        self.product_to_idx = {pid: i for i, pid in enumerate(products)}
        self.idx_to_product = {i: pid for i, pid in enumerate(products)}
        
        # Pivot interactions table to rating matrix
        rating_matrix = np.zeros((len(users), len(products)))
        for _, row in self.df_interactions.iterrows():
            u_idx = self.user_to_idx.get(row["user_id"])
            p_idx = self.product_to_idx.get(row["product_id"])
            if u_idx is not None and p_idx is not None:
                rating_matrix[u_idx, p_idx] = float(row["rating"])
                
        # SVD decomposition
        # Adjust n_factors if matrix is smaller than n_factors
        actual_factors = min(self.n_factors, min(rating_matrix.shape) - 1)
        if actual_factors < 2:
            actual_factors = 1
            
        svd = TruncatedSVD(n_components=actual_factors, random_state=42)
        # Transform matrix
        user_factors = svd.fit_transform(rating_matrix)
        self.product_latent_features = svd.components_.T
        
        # Reconstruct the rating matrix (predictions)
        self.reconstructed_ratings = np.dot(user_factors, svd.components_)
        
        # Normalize reconstructed ratings to standard 1-5 scale bounds
        if self.reconstructed_ratings.size > 0:
            min_r = self.reconstructed_ratings.min()
            max_r = self.reconstructed_ratings.max()
            if max_r - min_r > 1e-5:
                self.reconstructed_ratings = 1.0 + 4.0 * (self.reconstructed_ratings - min_r) / (max_r - min_r)
            else:
                self.reconstructed_ratings = np.ones_like(self.reconstructed_ratings) * 3.0
                
        logger.info("Recommendation engine fit complete.")

    def get_collaborative_score(self, user_id: str, product_id: str) -> float:
        """Returns the collaborative filtering prediction rating (normalized 0 to 1)."""
        u_idx = self.user_to_idx.get(user_id)
        p_idx = self.product_to_idx.get(product_id)
        
        if u_idx is None or p_idx is None:
            # Fallback to general product average rating
            prod_row = self.product_features[self.product_features["product_id"] == product_id]
            if not prod_row.empty:
                return float(prod_row["product_avg_rating"].values[0]) / 5.0
            return 0.5
            
        predicted_rating = self.reconstructed_ratings[u_idx, p_idx]
        return float(predicted_rating) / 5.0

    def get_content_score(self, user_id: str, product_id: str) -> float:
        """Returns the content similarity score between user history and candidate product."""
        p_idx = self.product_to_idx.get(product_id)
        if p_idx is None:
            return 0.0
            
        # Get products this user has interacted with
        user_history = self.df_interactions[self.df_interactions["user_id"] == user_id]
        if user_history.empty:
            return 0.0
            
        # Get historical products
        hist_product_ids = user_history["product_id"].tolist()
        hist_indices = [self.product_to_idx[pid] for pid in hist_product_ids if pid in self.product_to_idx]
        if not hist_indices:
            return 0.0
            
        # Compute user's average content vector weighted by rating or simple average
        user_profile_vector = np.asarray(self.tfidf_matrix[hist_indices].mean(axis=0))
        candidate_vector = self.tfidf_matrix[p_idx]
        
        sim = cosine_similarity(user_profile_vector, candidate_vector)[0][0]
        return float(sim)

    def recommend_for_user(self, user_id: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """Generates hybrid recommendations for a given user."""
        if self.df_products is None:
            raise ValueError("Engine is not fitted yet.")
            
        recommendations = []
        user_history = self.df_interactions[self.df_interactions["user_id"] == user_id]
        purchased_pids = set(user_history[user_history["purchased"] == 1]["product_id"]) if not user_history.empty else set()
        
        for _, row in self.df_products.iterrows():
            pid = row["product_id"]
            
            # Exclude already purchased products
            if pid in purchased_pids:
                continue
                
            collab_score = self.get_collaborative_score(user_id, pid)
            content_score = self.get_content_score(user_id, pid)
            
            hybrid_score = (self.collaborative_weight * collab_score) + (self.content_weight * content_score)
            
            # Get category score & details
            recommendations.append({
                "product_id": pid,
                "product_name": row["product_name"],
                "category": row["category"],
                "description": row["description"],
                "collaborative_score": round(collab_score, 4),
                "content_score": round(content_score, 4),
                "recommendation_score": round(hybrid_score, 4)
            })
            
        # Sort recommendations
        recommendations = sorted(recommendations, key=lambda x: x["recommendation_score"], reverse=True)
        return recommendations[:top_n]

    def recommend_similar_products(self, product_id: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Finds alternative/similar products based on description and SVD factors similarity."""
        p_idx = self.product_to_idx.get(product_id)
        if p_idx is None:
            return []
            
        # 1. Content similarities
        target_vector = self.tfidf_matrix[p_idx]
        content_sims = cosine_similarity(target_vector, self.tfidf_matrix).flatten()
        
        # 2. Collaborative similarities (cosine similarity of latent factor matrix)
        target_latent = self.product_latent_features[p_idx].reshape(1, -1)
        collab_sims = cosine_similarity(target_latent, self.product_latent_features).flatten()
        
        similar_items = []
        for i, row in self.df_products.iterrows():
            pid = row["product_id"]
            if pid == product_id:
                continue
                
            idx = self.product_to_idx.get(pid)
            if idx is None:
                continue
                
            c_score = float(collab_sims[idx])
            t_score = float(content_sims[idx])
            
            # Map cosine distance range [-1, 1] to [0, 1]
            c_score_norm = (c_score + 1.0) / 2.0
            
            hybrid_sim = (self.collaborative_weight * c_score_norm) + (self.content_weight * t_score)
            
            similar_items.append({
                "product_id": pid,
                "product_name": row["product_name"],
                "category": row["category"],
                "description": row["description"],
                "similarity_score": round(hybrid_sim, 4)
            })
            
        similar_items = sorted(similar_items, key=lambda x: x["similarity_score"], reverse=True)
        return similar_items[:top_n]

    def get_trending_products(self, top_n: int = 6) -> Dict[str, List[Dict[str, Any]]]:
        """Returns trending products: most viewed and most purchased."""
        if self.product_features is None:
            return {"most_viewed": [], "most_purchased": []}
            
        most_viewed_df = self.product_features.sort_values(by="product_total_views", ascending=False).head(top_n)
        most_purchased_df = self.product_features.sort_values(by="product_total_purchases", ascending=False).head(top_n)
        
        def format_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
            res = []
            for _, row in df.iterrows():
                res.append({
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "category": row["category"],
                    "description": row["description"],
                    "views": int(row["product_total_views"]),
                    "purchases": int(row["product_total_purchases"]),
                    "rating": round(float(row["product_avg_rating"]), 2)
                })
            return res
            
        return {
            "most_viewed": format_list(most_viewed_df),
            "most_purchased": format_list(most_purchased_df)
        }

    def save(self, filepath: str) -> None:
        """Serializes the engine state to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(self, f)
        logger.info(f"Recommendation engine saved successfully to {filepath}")

    @staticmethod
    def load(filepath: str) -> 'RecommendationEngine':
        """Deserializes the engine state from disk."""
        with open(filepath, "rb") as f:
            engine = pickle.load(f)
        logger.info(f"Recommendation engine loaded successfully from {filepath}")
        return engine

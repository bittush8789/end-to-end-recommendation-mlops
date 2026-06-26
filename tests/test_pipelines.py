import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add src and api to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipelines")))

from data_ingestion import DataIngestion
from data_validation import DataValidation
from feature_engineering import FeatureEngineering
from recommendation_engine import RecommendationEngine
from app import app

client = TestClient(app)

@pytest.fixture(scope="module")
def sample_data():
    ingestor = DataIngestion(data_dir="test_data_temp")
    products, interactions = ingestor.load_data()
    yield products, interactions
    
    # Cleanup temp test files
    for filepath in [ingestor.products_path, ingestor.interactions_path]:
        if os.path.exists(filepath):
            os.remove(filepath)
    if os.path.exists("test_data_temp"):
        os.rmdir("test_data_temp")

def test_ingestion(sample_data):
    products, interactions = sample_data
    assert not products.empty
    assert not interactions.empty
    assert "product_id" in products.columns
    assert "user_id" in interactions.columns

def test_validation(sample_data):
    products, interactions = sample_data
    validator = DataValidation(artifacts_dir="test_artifacts_temp")
    report = validator.validate(products, interactions)
    assert report["status"] == "SUCCESS"
    
    # Cleanup
    if os.path.exists(validator.report_path):
        os.remove(validator.report_path)
    if os.path.exists("test_artifacts_temp"):
        os.rmdir("test_artifacts_temp")

def test_feature_engineering(sample_data):
    products, interactions = sample_data
    fe = FeatureEngineering()
    user_features, product_features = fe.transform(products, interactions)
    
    assert "user_avg_rating" in user_features.columns
    assert "product_avg_rating" in product_features.columns
    assert len(user_features) > 0
    assert len(product_features) > 0

def test_recommendation_engine(sample_data):
    products, interactions = sample_data
    fe = FeatureEngineering()
    user_features, product_features = fe.transform(products, interactions)
    
    engine = RecommendationEngine(n_factors=5)
    engine.fit(products, interactions, user_features, product_features)
    
    recs = engine.recommend_for_user("U001", top_n=5)
    assert len(recs) <= 5
    if recs:
        assert "recommendation_score" in recs[0]
        
    sims = engine.recommend_similar_products("P1001", top_n=3)
    assert len(sims) <= 3

def test_api_endpoints():
    response = client.get("/")
    assert response.status_code == 200
    assert "health_check" in response.json()

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded"]

    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    response = client.get("/trending")
    assert response.status_code == 200
    assert "most_viewed" in response.json()

    response = client.get("/eda")
    assert response.status_code == 200
    assert "summary" in response.json()
    assert "categories" in response.json()


import os
import sys
import time
import psutil
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Add pipelines to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pipelines"))
from prediction_pipeline import PredictionPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="E-Commerce Recommendation System API",
    description="Production-grade recommendation engine API serving personalized, similar, and trending products.",
    version="1.0.0"
)

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend directory for static serving
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Prometheus Metrics Definitions
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total number of HTTP requests processed by the API",
    ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"]
)

# Initialize Prediction Pipeline
try:
    pipeline = PredictionPipeline()
except Exception as e:
    logger.error(f"Failed to initialize prediction pipeline: {e}")
    pipeline = None

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    endpoint = request.url.path
    method = request.method
    
    # Process request
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise e
    finally:
        latency = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        
    return response

@app.get("/")
def read_root():
    # Redirect root to frontend interface index.html
    return RedirectResponse(url="/frontend/index.html")


@app.get("/health")
def health_check():
    """Health check endpoint containing system resources."""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    status = "healthy"
    if pipeline is None or pipeline.engine is None:
        status = "degraded"
        
    return {
        "status": status,
        "system": {
            "cpu_utilization_percent": cpu_percent,
            "memory_utilization_percent": memory.percent,
            "memory_available_bytes": memory.available
        },
        "model_loaded": pipeline is not None and pipeline.engine is not None
    }

@app.get("/metrics")
def metrics():
    """Exposes Prometheus-compatible metric scrapings."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/products")
def get_products(search: str = None):
    """Retrieves all products, optionally filtered by keyword query."""
    if not pipeline or not pipeline.engine:
        raise HTTPException(status_code=503, detail="Prediction engine is unavailable.")
        
    if search:
        return pipeline.search_products(search)
        
    # Return all products
    df = pipeline.engine.df_products
    return df.to_dict(orient="records")

@app.get("/product/{product_id}")
def get_product(product_id: str):
    """Retrieves metadata of a single product."""
    if not pipeline or not pipeline.engine:
        raise HTTPException(status_code=503, detail="Prediction engine is unavailable.")
        
    df = pipeline.engine.df_products
    prod_row = df[df["product_id"] == product_id]
    if prod_row.empty:
        raise HTTPException(status_code=404, detail="Product not found.")
        
    return prod_row.iloc[0].to_dict()

@app.get("/recommend/user/{user_id}")
def recommend_for_user(user_id: str, limit: int = 10):
    """Exposes Top K personalized recommendations for a given User ID."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Prediction engine is unavailable.")
        
    try:
        recs = pipeline.get_user_recommendations(user_id, top_n=limit)
        return {"user_id": user_id, "recommendations": recs}
    except Exception as e:
        logger.error(f"Error serving user recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommend/product/{product_id}")
def recommend_similar_products(product_id: str, limit: int = 5):
    """Exposes Top similar and alternative products for a given Product ID."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Prediction engine is unavailable.")
        
    try:
        recs = pipeline.get_similar_products(product_id, top_n=limit)
        return {"product_id": product_id, "recommendations": recs}
    except Exception as e:
        logger.error(f"Error serving similar products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trending")
def get_trending(limit: int = 6):
    """Retrieves lists of trending products (most viewed and most purchased)."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Prediction engine is unavailable.")
        
    try:
        return pipeline.get_trending_products(top_n=limit)
    except Exception as e:
        logger.error(f"Error serving trending products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/eda")
def get_eda():
    """Generates dataset exploratory stats (ratings, categories, metrics)."""
    if not pipeline or not pipeline.engine:
        raise HTTPException(status_code=503, detail="Prediction engine is unavailable.")
        
    df_p = pipeline.engine.df_products
    df_i = pipeline.engine.df_interactions
    
    # Category distribution
    cat_counts = df_p["category"].value_counts().to_dict()
    
    # Rating distribution
    rating_counts = df_i["rating"].value_counts().sort_index().to_dict()
    # Convert keys to string for JSON serialization compatibility
    rating_counts_str = {str(k): int(v) for k, v in rating_counts.items()}
    
    return {
        "summary": {
            "total_products": len(df_p),
            "total_users": len(df_i["user_id"].unique()),
            "total_interactions": len(df_i),
            "avg_ratings": round(float(df_i["rating"].mean()), 2),
            "purchase_ratio": round(float(df_i["purchased"].mean() * 100), 2)
        },
        "categories": cat_counts,
        "ratings_distribution": rating_counts_str
    }


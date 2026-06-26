# E-Commerce Recommendation Platform (ML + MLOps)

A production-grade, end-to-end recommendation system that serves hybrid (Collaborative Filtering SVD + Content-Based TF-IDF) product recommendations under 1 second. The project includes automated pipelines, MLOps components (MLflow, DVC), FastAPI backend endpoints, Prometheus monitoring, and a responsive frontend dashboard.

---

## 🎯 Business Problem Solving & Objectives

### The Challenge
In modern e-commerce, platforms face several key challenges that impact revenue and retention:
1. **Discovery Friction**: Customers struggle to find relevant products within large catalogs, leading to high bounce rates and drop-offs.
2. **Cold Start & Engagement**: Failing to suggest relevant recommendations during browsing sessions decreases the Average Order Value (AOV) and lowers the Click-Through Rate (CTR).
3. **Customer Retention**: Without personalization, shoppers feel unengaged and migrate to competitor platforms.

### The ML-Powered Solution
This platform addresses these commercial challenges through a **Hybrid Recommendation Engine**:
- **Personalized Picks (Collaborative Filtering)**: Deconstructs historical user-item rating trends using Singular Value Decomposition (SVD). This maps similar user preferences to recommend items a user is highly likely to purchase, directly increasing **Conversion Rates**.
- **Alternative Discoveries (Content-Based Filtering)**: Uses TF-IDF Vectorization and Cosine Similarity on product category and text details to show high-affinity alternatives. This prevents user drop-off on out-of-stock items and drives catalog exploration.
- **Trending & High-Velocity Items**: Surfaces most viewed and best-selling products to new/unauthenticated users, resolving the cold-start problem and increasing immediate CTR.

### Expected Business Impact
- **Average Order Value (AOV)**: Expected increase of **12-18%** through personalized cross-selling.
- **Conversion Rate (CR)**: Expected uplift of **5-8%** by reducing browsing path friction.
- **Click-Through Rate (CTR)**: Expected improvement of **20%** on homepage grids using hybrid model scoring.

---

## 📂 Project Structure

```
ecommerce-recommendation-platform-mlops/
├── api/
│   └── app.py                      # FastAPI Backend with CORS and Prometheus metrics
├── data/
│   ├── products.csv                # Product catalog (automatically generated)
│   └── user_interactions.csv       # User interaction logs (automatically generated)
├── src/
│   ├── data_ingestion.py           # Loads CSV files, generates mocks if missing
│   ├── data_validation.py          # Verifies schema, duplicates, invalid values
│   ├── feature_engineering.py      # Computes user & product metrics
│   ├── model_training.py           # Trains collaborative and content engines
│   ├── model_evaluation.py         # Computes Precision@K, Recall@K, MAP, NDCG
│   └── recommendation_engine.py    # Hybrid Recommendation Engine
├── frontend/
│   ├── index.html                  # Dashboard layout (Glassmorphism design)
│   ├── style.css                   # Custom styles with gradient themes
│   └── script.js                   # Client side API fetch integration
├── monitoring/
│   └── prometheus.yml              # Prometheus configuration
├── pipelines/
│   ├── training_pipeline.py        # Complete training orchestrator
│   └── prediction_pipeline.py      # Predictor wrapper & search router
├── artifacts/                      # Houses model.pkl, evaluation reports
├── tests/
│   └── test_pipelines.py           # Suite of unit tests
├── requirements.txt                # Project dependencies
├── dvc.yaml                        # DVC reproducible pipeline stages
├── Dockerfile                      # Docker image specification
└── README.md                       # Documentation
```

## Quick Start & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Execute Training Pipeline
This command ingests data, validates schema, performs feature engineering, trains the models, evaluates them, logs metrics to MLflow, and stores the final model artifact.
```bash
python pipelines/training_pipeline.py
```

### 3. Launch FastAPI Server & Frontend Dashboard
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000
```
- **Unified Web UI Dashboard**: Visit [http://localhost:8000](http://localhost:8000) (It redirects automatically to `/frontend/index.html`).
- **Interactive EDA Insights**: Select the **Data Insights (EDA)** tab to view real-time statistics of the catalog categories and ratings distributions.
- **REST API Endpoints**:
  - API Health Check: [http://localhost:8000/health](http://localhost:8000/health)
  - Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Dataset EDA API JSON: [http://localhost:8000/eda](http://localhost:8000/eda)
  - Prometheus Client Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)

### 4. Interactive Dashboard Features
The dashboard runs fully inside your browser without any page reloads (using async AJAX fetches):
- **Personalized Picks**: Select active users from **U001 to U100** to display hybrid recommendations instantly.
- **Similarity Searches**: Click on any product card or trending row item to load alternative/similar items.
- **Global Search**: Type inside the search bar to query products by name or category.
- **Exploratory Data Analysis (EDA)**: Offers real-time summaries and charts showing ratings and category distributions.


## Docker Support

Build and run the entire application in a Docker container:
```bash
# Build the image (automatically executes training pipeline during build)
docker build -t ecommerce-recommendation .

# Run the container exposing port 8000
docker run -p 8000:8000 ecommerce-recommendation
```

## Monitoring Setup (Prometheus)

Configure Prometheus to scrape the FastAPI `/metrics` endpoint. In your local Prometheus installation folder, run:
```bash
prometheus --config.file=monitoring/prometheus.yml
```
You can then link Grafana to the Prometheus data source to display metrics for:
- Requests per minute (`api_requests_total`)
- Latency (`api_request_duration_seconds`)
- Server Resource (CPU & Memory utilization)

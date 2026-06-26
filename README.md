# E-Commerce Recommendation Platform (ML + MLOps)

A production‑grade, end‑to‑end recommendation system that serves hybrid (Collaborative Filtering SVD + Content‑Based TF‑IDF) product recommendations under 1 second. The project includes automated pipelines, MLOps components (MLflow, DVC), FastAPI backend endpoints, Prometheus monitoring, and a responsive frontend dashboard.

## 🖥️ Dashboard Preview

![VelocityRecs Dashboard Preview](photo/image.png)

---

## 🎯 Business Problem Solving & Objectives

### The Challenge
In modern e‑commerce, platforms face several key challenges that impact revenue and retention:
1. **Discovery Friction** – customers struggle to find relevant products within large catalogs, leading to high bounce rates.
2. **Cold‑Start & Engagement** – missing recommendations during browsing decreases Average Order Value (AOV) and Click‑Through Rate (CTR).
3. **Customer Retention** – without personalization shoppers migrate to competitors.

### The ML‑Powered Solution
This platform addresses these challenges through a **Hybrid Recommendation Engine**:
- **Personalized Picks (Collaborative Filtering)** – SVD on historical user‑item interactions to surface items a user is highly likely to purchase.
- **Alternative Discoveries (Content‑Based Filtering)** – TF‑IDF + Cosine Similarity on product descriptions to suggest similar items.
- **Trending & High‑Velocity Items** – surfacing most viewed / best‑selling products for cold‑start users.

### Expected Business Impact
- **AOV** + 12‑18 % via cross‑selling.
- **Conversion Rate** + 5‑8 % by reducing browsing friction.
- **CTR** + 20 % on homepage grids using hybrid scoring.

---

## 📁 MLOps Folder Structure

Below is the recommended folder layout for a production‑grade MLOps recommendation system. Each top‑level directory groups related concerns (code, infrastructure, data, monitoring, CI/CD).

```text
recommendation-system/
├── api/                     # FastAPI service (model inference API)
│   └── app.py
├── data/                    # Raw / generated datasets
│   ├── products.csv
│   └── user_interactions.csv
├── src/                     # Core ML pipeline code
│   ├── data_ingestion.py
│   ├── data_validation.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   └── recommendation_engine.py
├── pipelines/               # Kubeflow pipelines / orchestration scripts
│   ├── training_pipeline.py
│   └── prediction_pipeline.py
├── monitoring/              # Prometheus & Grafana configs
│   └── prometheus.yml
├── terraform/               # IaC for AWS resources (ECR, EKS, IAM)
│   └── ecr.tf
├── k8s/                     # Kubernetes manifests for FastAPI & HPA
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── namespace.yaml
├── kserve/                  # Model serving via KServe
│   └── inferenceservice.yaml
├── argocd/                  # GitOps deployment via Argo CD
│   ├── install.yaml
│   └── namespace.yaml
├── mlflow/                  # MLflow server scripts & configs
│   └── mlflow_server.sh
├── dvc.yaml                 # Data & model versioning pipeline
├── Dockerfile               # Container image definition for FastAPI
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation (this file)
```

## Quick Start & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Training Pipeline
```bash
python pipelines/training_pipeline.py
```
This script performs data ingestion, validation, feature engineering, model training, evaluation, and logs everything to **MLflow** and **DVC**.

### 3. Launch FastAPI & Frontend
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000
```
- UI: <http://localhost:8000>
- Swagger docs: <http://localhost:8000/docs>
- Prometheus metrics: <http://localhost:8000/metrics>

## Docker Support
```bash
# Build the image
docker build -t ecommerce-recommendation .

# Run the container (exposes FastAPI on port 8000)
docker run -p 8000:8000 ecommerce-recommendation
```

## Monitoring (Prometheus + Grafana)
```bash
prometheus --config.file=monitoring/prometheus.yml
```
Configure Grafana to use the Prometheus data source and import the provided dashboards (found in `monitoring/grafana/`).

## CI/CD Pipeline (GitHub Actions)
The `.github/workflows/main.yml` pipeline runs on every push to **`cicd`**:
1. ✅ Run unit tests
2. 📊 Data validation (DVC pull & checksum verification)
3. 🤖 Model training & evaluation (MLflow tracking)
4. 🐳 Build & push Docker image to **ECR**
5. 📦 Deploy manifests to **EKS** (kubectl apply)
6. 🚀 Deploy model via **KServe**
7. 📈 Sync Argo CD for GitOps continuous delivery

---

## 🛠️ Tools & Step‑by‑Step Usage (Industry‑Standard)
Below is a detailed guide for each tool used in this MLOps stack, detailing the exact commands to run and how to use them in the lifecycle.

### 1. FastAPI
* **Purpose**: Serves model predictions and metrics via REST endpoints.
* **How to use it**:
  1. Initialize FastAPI app in `api/app.py`.
  2. Start the API locally:
     ```bash
     uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
     ```
  3. Query predictions via interactive docs: Open [http://localhost:8000/docs](http://localhost:8000/docs).
* **Use‑Case**: Low-latency serving of recommendation results to frontend applications.

### 2. Python
* **Purpose**: Base programming language for pipeline scripts, data manipulation, and models.
* **How to use it**:
  1. Create a clean virtual environment:
     ```bash
     python -m venv venv
     source venv/Scripts/activate  # On Windows: venv\Scripts\activate
     ```
  2. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
* **Use‑Case**: Running data preparation, validation, engineering, and training steps.

### 3. Scikit‑Learn / LightFM
* **Purpose**: Collaborative filtering & Content-based algorithms.
* **How to use it**:
  1. Train models via training script:
     ```bash
     python src/model_training.py
     ```
  2. Persist model binary:
     ```python
     import joblib
     joblib.dump(model, 'artifacts/model.pkl')
     ```
* **Use‑Case**: Building hybrid recommendation pipelines.

### 4. MLflow
* **Purpose**: Experiment tracking, metric visualization, and model registry.
* **How to use it**:
  1. Run a local MLflow UI dashboard:
     ```bash
     mlflow server --host 127.0.0.1 --port 5000
     ```
  2. Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) to view metrics and parameter differences across runs.
* **Use‑Case**: Comparing hyperparameters and registering model files.

### 5. DVC (Data Version Control)
* **Purpose**: Versioning dataset csv files and large model binaries without checking them into Git.
* **How to use it**:
  1. Initialize DVC:
     ```bash
     dvc init
     ```
  2. Track data changes:
     ```bash
     dvc add data/products.csv data/user_interactions.csv
     ```
  3. Git track the small metadata pointers:
     ```bash
     git add data/products.csv.dvc .gitignore
     ```
  4. Push datasets to configured S3 or local remote:
     ```bash
     dvc push
     ```
  5. Pull data onto a clean runner:
     ```bash
     dvc pull
     ```
* **Use‑Case**: Enforcing reproducibility in CI/CD environments.

### 6. Docker
* **Purpose**: Packaging runtime environments into immutable container images.
* **How to use it**:
  1. Build the production Docker image:
     ```bash
     docker build -t recommend-api:latest .
     ```
  2. Run container to verify:
     ```bash
     docker run -p 8000:8000 recommend-api:latest
     ```
* **Use‑Case**: Deploying identical runtimes locally, to EKS, and other staging systems.

### 7. Kubernetes (kubectl)
* **Purpose**: Cluster management and API deployments.
* **How to use it**:
  1. Deploy all services and configmaps:
     ```bash
     kubectl apply -f k8s/namespace.yaml
     kubectl apply -f k8s/
     ```
  2. Check Deployment rollout status:
     ```bash
     kubectl rollout status deployment/recommendation-api -n recommendation
     ```
* **Use‑Case**: Highly-scalable hosting with rolling updates.

### 8. KServe
* **Purpose**: Serve raw pickle models with declarative YAML server wrappers.
* **How to use it**:
  1. Deploy Inference Service:
     ```bash
     kubectl apply -f kserve/inferenceservice.yaml
     ```
  2. Check status of model availability:
     ```bash
     kubectl get inferenceservice recommender -n recommendation
     ```
* **Use‑Case**: Serverless inference orchestration with request routing and scaling-to-zero.

### 9. Kubeflow Pipelines (KFP)
* **Purpose**: Orchestrating the end-to-end DAG (Directed Acyclic Graph) of ML workflows.
* **How to use it**:
  1. Define pipelines using python KFP SDK and compile:
     ```bash
     pip install kfp
     python pipelines/training_pipeline.py --compile
     ```
  2. Upload `pipeline.yaml` to Kubeflow Dashboard.
* **Use‑Case**: Automating scheduled retraining runs.

### 10. GitHub Actions
* **Purpose**: Continuous Integration & Deployment.
* **How to use it**:
  1. Configure workflow triggers inside `.github/workflows/main.yml`.
  2. Set secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.) inside GitHub Repository Settings.
  3. Git push triggers steps automatically.
* **Use‑Case**: Automating unit tests, image builds, and deployments on git events.

### 11. AWS EKS (Amazon Elastic Kubernetes Service)
* **Purpose**: Managed container environment on AWS.
* **How to use it**:
  1. Link local context to remote cluster:
     ```bash
     aws eks update-kubeconfig --region us-east-1 --name cluster-name
     ```
  2. Check node health:
     ```bash
     kubectl get nodes
     ```
* **Use‑Case**: Production cloud-native server hosting.

### 12. Prometheus
* **Purpose**: Scrape time-series server metrics.
* **How to use it**:
  1. Launch Prometheus server:
     ```bash
     prometheus --config.file=monitoring/prometheus.yml
     ```
  2. Query server metrics at: [http://localhost:9090](http://localhost:9090).
* **Use‑Case**: Alerts on request failures or server latency spikes.

### 13. Grafana
* **Purpose**: Dashboard visualization of system metrics.
* **How to use it**:
  1. Connect Prometheus datasource to Grafana.
  2. Import panels using metric keys such as `api_requests_total`.
* **Use‑Case**: Operational dashboards for monitoring real-time API traffic.

### 14. Evidently AI
* **Purpose**: Evaluate feature drift and model performance quality.
* **How to use it**:
  1. Run data/model drift monitoring script:
     ```bash
     python src/data_validation.py --drift-analysis
     ```
  2. Review generated HTML validation reports.
* **Use‑Case**: Proactive alerts prior to model accuracy decay.

### 15. Argo CD
* **Purpose**: GitOps Continuous Delivery.
* **How to use it**:
  1. Apply Argo CD applications:
     ```bash
     kubectl apply -f argocd/install.yaml
     ```
  2. Monitor deployment updates via Argo CD UI dashboard.
* **Use‑Case**: Declarative synchronisation of K8s resources with git repositories.

---

## License

MIT License

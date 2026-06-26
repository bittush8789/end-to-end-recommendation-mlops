FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy codebase
COPY . .

# Run training pipeline to generate artifacts on container build
RUN python pipelines/training_pipeline.py

# Expose port
EXPOSE 8000

# Start API server
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]

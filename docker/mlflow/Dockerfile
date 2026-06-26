FROM python:3.11-slim

RUN pip install --no-cache-dir mlflow boto3 psycopg2-binary

EXPOSE 5000

ENV MLFLOW_S3_ENDPOINT_URL=""
ENV AWS_DEFAULT_REGION="us-east-1"

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "${MLFLOW_BACKEND_URI}", \
     "--default-artifact-root", "${MLFLOW_ARTIFACT_ROOT}", \
     "--serve-artifacts"]

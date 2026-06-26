# ──────────────────────────────────────────────────────────────────────────────
# Stage 1: Build dependencies
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools only in builder stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# ──────────────────────────────────────────────────────────────────────────────
# Stage 2: Production image
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS production

# Security: run as non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source
COPY api/       api/
COPY src/        src/
COPY pipelines/  pipelines/
COPY frontend/   frontend/
COPY data/       data/
COPY artifacts/  artifacts/

# Set ownership
RUN chown -R appuser:appgroup /app

USER appuser

# Make sure scripts in .local are usable
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

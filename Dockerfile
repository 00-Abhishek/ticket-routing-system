# Build stage
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and filter torch version
COPY requirements.txt .
RUN grep -v '^torch>=' requirements.txt > requirements.docker.txt

# Download and cache torch wheel
RUN curl -L --retry 20 --retry-all-errors --continue-at - \
        'https://download-r2.pytorch.org/whl/cpu/torch-2.12.1%2Bcpu-cp311-cp311-manylinux_2_28_x86_64.whl' \
        --output /tmp/torch-2.12.1+cpu-cp311-cp311-manylinux_2_28_x86_64.whl

# Install dependencies into virtual environment
RUN pip install --upgrade pip wheel \
    && pip install /tmp/torch-2.12.1+cpu-cp311-cp311-manylinux_2_28_x86_64.whl \
    && pip install -r requirements.docker.txt

# Runtime stage
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create runtime directories
RUN mkdir -p data models reports && chmod 755 data models reports

EXPOSE 8000 8501

# Default command (override in docker-compose for dashboard)
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

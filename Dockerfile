FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN grep -v '^torch>=' requirements.txt > requirements.docker.txt \
    && pip install --upgrade pip \
    && curl -L --retry 20 --retry-all-errors --continue-at - \
        'https://download-r2.pytorch.org/whl/cpu/torch-2.12.1%2Bcpu-cp311-cp311-manylinux_2_28_x86_64.whl' \
        --output /tmp/torch-2.12.1+cpu-cp311-cp311-manylinux_2_28_x86_64.whl \
    && pip install /tmp/torch-2.12.1+cpu-cp311-cp311-manylinux_2_28_x86_64.whl \
    && pip install -r requirements.docker.txt

COPY . .

RUN mkdir -p data models reports

EXPOSE 8000 8501

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

# Phase 10 Docker Deployment

## Scope

Phase 10 containerizes the FastAPI backend and Streamlit dashboard with Docker Compose and mounts the trained models, reports, and SQLite data from the host repository.

## Architecture Diagram

```text
Host Machine
    |
    +-- http://localhost:8000/docs
    |       |
    |       v
    |   backend container
    |   uvicorn src.api.app:app
    |       |
    |       +-- /app/data
    |       +-- /app/models
    |       +-- /app/reports
    |
    +-- http://localhost:8501
            |
            v
        dashboard container
        streamlit run dashboard/app.py
            |
            v
        BACKEND_URL=http://backend:8000
```

## Container Layout

### backend

- Runs FastAPI with Uvicorn.
- Command:

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

- Exposes `8000:8000`.
- Healthcheck calls `GET /health`.
- Uses a CPU-only Torch wheel during image build for reliable container installation.

### dashboard

- Runs Streamlit.
- Command:

```bash
streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501
```

- Exposes `8501:8501`.
- Depends on the backend healthcheck.
- Uses `BACKEND_URL=http://backend:8000`.

## Volumes

The Compose file mounts:

- `./data:/app/data`
- `./models:/app/models`
- `./reports:/app/reports`

This preserves SQLite data and keeps trained model/report artifacts available to both containers.

## Validated Runtime Result

Validation completed locally on `2026-06-28`.

Verified successfully:

- `docker compose build`
- `docker compose up -d`
- Backend healthy on `http://127.0.0.1:8000/health`
- Dashboard reachable on `http://127.0.0.1:8501/_stcore/health`
- Dashboard container could reach backend through `BACKEND_URL=http://backend:8000`
- `GET /metrics` returned model and rule metadata
- `POST /predict` returned a live prediction
- `POST /analyze` returned full workflow output and persisted rows to SQLite
- `GET /history` and `GET /analytics` reflected persisted Docker-run requests
- Mounted model and report files were present inside the backend container
- Host database file `data/ticket_routing.db` updated during container execution

## Startup Instructions

Run:

```bash
docker compose up --build
```

Expected access:

- FastAPI docs: `http://localhost:8000/docs`
- Streamlit dashboard: `http://localhost:8501`

## Troubleshooting

### Backend fails to start

Check that the trained DistilBERT model exists:

```text
models/distilbert/
```

The backend needs this directory to load the classifier.

### Dashboard shows offline

Confirm the backend container is healthy:

```bash
docker compose ps
```

The dashboard uses:

```text
BACKEND_URL=http://backend:8000
```

inside Docker Compose.

### SQLite data is missing

Confirm `data/` is mounted and writable. The database path is:

```text
data/ticket_routing.db
```

### Slow first startup

The image installs Python dependencies during build. Rebuilds are faster when `requirements.txt` and the Dockerfile do not change because dependency layers are cached.

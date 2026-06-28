# Phase 11 System Validation Report

## Validation Date

- 2026-06-28

## Architecture Summary

```text
Streamlit Dashboard
        |
        v
FastAPI Backend
        |
        +-- DistilBERT classifier
        +-- spaCy rule-based NER
        +-- PriorityEngine
        +-- TicketRouter
        +-- SQLite PredictionRepository
```

The complete validated workflow is:

```text
Ticket
  -> DistilBERT Classification
  -> NER Extraction
  -> Priority Assignment
  -> Routing
  -> SQLite Persistence
  -> API Response
  -> Dashboard Display
```

## Functional Testing Results

The automated suite covers:

- Text preprocessing
- Baseline model utilities
- DistilBERT metric helpers
- NER extraction
- Routing
- Priority assignment
- FastAPI endpoints
- Dashboard parsing and chart helpers
- SQLite persistence
- Integration workflow behavior
- Docker configuration checks

Verification result:

```text
pytest
58 passed in 19.23s
```

## API Testing Results

Validated endpoints:

- `GET /health`
- `GET /metrics`
- `GET /history`
- `GET /analytics`
- `POST /predict`
- `POST /entities`
- `POST /priority`
- `POST /route`
- `POST /analyze`

Integration tests verify that `/analyze` returns classification, entities, priority, matched rule, assigned team, and persists the prediction.

## Database Testing Results

SQLite persistence is implemented with SQLAlchemy.

Covered behaviors:

- Table creation
- Save prediction
- Recent prediction history
- Total prediction count
- Category distribution
- Priority distribution

Production database path:

```text
data/ticket_routing.db
```

## Dashboard Testing Results

Dashboard helper tests validate:

- API response parsing
- Backend URL environment configuration
- Markdown report parsing
- Model comparison table loading
- Plotly chart generation helpers

The dashboard reads `BACKEND_URL` from the environment and falls back to `http://127.0.0.1:8000`.

Captured screenshot targets:

| Screenshot | Validation Target |
| --- | --- |
| `docs/screenshots/dashboard_home.png` | Dashboard home and API health status |
| `docs/screenshots/prediction_results.png` | Ticket analysis result display |
| `docs/screenshots/analytics_page.png` | Analytics page with model metrics |
| `docs/screenshots/fastapi_swagger_docs.png` | FastAPI Swagger documentation |
| `docs/screenshots/database_history_endpoint.png` | Persisted history endpoint |

## Deployment Summary

Docker Compose validation completed locally on `2026-06-28`.

Verified successfully:

- `docker compose build`
- `docker compose up -d`
- Backend health at `GET /health`
- Dashboard reachability at `GET /_stcore/health`
- Dashboard-to-backend communication through `BACKEND_URL=http://backend:8000`
- `GET /metrics`
- `POST /predict`
- `POST /analyze`
- Mounted model and report directories inside the backend container
- SQLite persistence through `GET /history`, `GET /analytics`, and the mounted host database file `data/ticket_routing.db`

## Known Limitations

- LSTM is not implemented in the repository.
- Entity extraction is rule-based and pattern-driven, not a trained NER model.
- The dashboard still makes multiple endpoint calls for one analysis action instead of relying only on `/analyze`.
- Priority `matched_rule` is returned by the API but is not persisted to SQLite.
- The API currently has no authentication layer.

# FastAPI Backend Design

## Scope

The implemented backend exposes the complete ticket-analysis workflow through FastAPI and loads runtime services once at startup.

Covered capabilities:

- DistilBERT classification
- Rule-based entity extraction
- Rule-based priority assignment
- Deterministic routing
- Prediction history
- Aggregate analytics
- Full workflow persistence through `/analyze`

## Architecture

```text
Client
  |
  v
FastAPI Routes
  |
  v
TicketAnalysisService singleton
  |
  +-- DistilBERT model + tokenizer
  +-- spaCy EntityExtractor
  +-- PriorityEngine
  +-- TicketRouter
  +-- PredictionRepository
```

The DistilBERT model, tokenizer, label mapping, NER extractor, priority engine, routing engine, and repository are created once and reused through FastAPI dependency injection.

## Files

- `src/api/__init__.py`
- `src/api/app.py`
- `src/api/schemas.py`
- `src/api/dependencies.py`
- `src/api/services.py`
- `tests/test_api.py`

## Endpoint Summary

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness check |
| GET | `/metrics` | Runtime model and rules metadata |
| GET | `/history` | Recent persisted predictions |
| GET | `/analytics` | Aggregate prediction analytics |
| POST | `/predict` | Category prediction |
| POST | `/entities` | Entity extraction |
| POST | `/priority` | Priority assignment |
| POST | `/route` | Category-to-team routing |
| POST | `/analyze` | Full workflow plus persistence |

## Example Responses

### `GET /metrics`

```json
{
  "model_name": "distilbert-base-uncased",
  "number_of_classes": 8,
  "available_entities": ["DEVICE", "ERROR_CODE", "LOCATION", "SOFTWARE", "SYSTEM"],
  "supported_priorities": ["Critical", "High", "Medium", "Low"]
}
```

### `POST /priority`

```json
{
  "priority": "Critical",
  "matched_rule": "server down"
}
```

### `POST /analyze`

```json
{
  "category": "Access",
  "confidence": 0.88,
  "entities": {
    "SOFTWARE": ["Outlook"],
    "DEVICE": ["laptop"]
  },
  "priority": "High",
  "matched_rule": "cannot login",
  "assigned_team": "Access Management Team"
}
```

## Error Handling

- Request validation errors return HTTP `422`.
- Unsupported categories return HTTP `400`.
- Model-loading failures exposed through `/metrics` return HTTP `503`.

## Deployment Notes

Run locally with:

```bash
uvicorn src.api.app:app --reload
```

OpenAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Required runtime artifacts:

- `models/distilbert/`
- `config/entity_patterns.json`

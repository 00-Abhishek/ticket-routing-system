# API Specification

## Overview

The backend is implemented with FastAPI and exposes prediction, entity extraction, priority assignment, routing, persistence history, and analytics endpoints for the IT support ticket workflow.

Base URL:

```text
http://127.0.0.1:8000
```

OpenAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## Authentication Status

No authentication is currently implemented. The API is intended for local development, academic demonstration, and containerized project submission scenarios.

## Request Models

### `PredictRequest`

```json
{
  "ticket_text": "Need admin rights for Visual Studio"
}
```

### `RouteRequest`

```json
{
  "category": "Hardware"
}
```

## Response Models

### `HealthResponse`

```json
{
  "status": "healthy"
}
```

### `PredictResponse`

```json
{
  "category": "Administrative rights",
  "confidence": 0.93
}
```

### `EntitiesResponse`

```json
{
  "entities": {
    "SOFTWARE": ["Visual Studio"]
  }
}
```

### `PriorityResponse`

```json
{
  "priority": "High",
  "matched_rule": "cannot login"
}
```

### `RouteResponse`

```json
{
  "category": "Hardware",
  "assigned_team": "Hardware Team"
}
```

### `FullPipelineResponse`

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

### `HistoryResponse`

```json
{
  "predictions": [
    {
      "id": 1,
      "ticket_text": "Unable to login to Outlook on my laptop",
      "predicted_category": "Access",
      "confidence_score": 0.88,
      "entities_json": "{\"DEVICE\": [\"laptop\"], \"SOFTWARE\": [\"Outlook\"]}",
      "priority": "High",
      "assigned_team": "Access Management Team",
      "created_at": "2026-06-28T12:34:56Z"
    }
  ]
}
```

### `AnalyticsResponse`

```json
{
  "total_predictions": 12,
  "category_distribution": {
    "Access": 5,
    "Hardware": 4,
    "Storage": 3
  },
  "priority_distribution": {
    "Critical": 1,
    "High": 4,
    "Medium": 6,
    "Low": 1
  }
}
```

## Endpoints

### `GET /health`

Purpose: basic liveness check.

Example response:

```json
{
  "status": "healthy"
}
```

### `GET /metrics`

Purpose: return model and rules metadata loaded at startup.

Example response:

```json
{
  "model_name": "distilbert-base-uncased",
  "number_of_classes": 8,
  "available_entities": ["DEVICE", "ERROR_CODE", "LOCATION", "SOFTWARE", "SYSTEM"],
  "supported_priorities": ["Critical", "High", "Medium", "Low"]
}
```

### `GET /history`

Purpose: return recent persisted prediction records.

Query parameter:

- `limit` default `50`, capped internally for safety

Example response:

```json
{
  "predictions": [
    {
      "id": 3,
      "ticket_text": "Need more mailbox storage for shared mailbox",
      "predicted_category": "Storage",
      "confidence_score": 0.91,
      "entities_json": "{\"SYSTEM\": [\"mailbox\"]}",
      "priority": "Medium",
      "assigned_team": "Storage Team",
      "created_at": "2026-06-28T12:40:00Z"
    }
  ]
}
```

### `GET /analytics`

Purpose: return persisted aggregate counts.

Example response:

```json
{
  "total_predictions": 3,
  "category_distribution": {
    "Access": 1,
    "Hardware": 1,
    "Storage": 1
  },
  "priority_distribution": {
    "Critical": 1,
    "High": 1,
    "Medium": 1
  }
}
```

### `POST /predict`

Purpose: classify ticket category using the loaded DistilBERT model.

Example request:

```json
{
  "ticket_text": "Need admin rights for Visual Studio"
}
```

Example response:

```json
{
  "category": "Administrative rights",
  "confidence": 0.93
}
```

### `POST /entities`

Purpose: extract configured entities using spaCy `EntityRuler`.

Example request:

```json
{
  "ticket_text": "Outlook not working on laptop"
}
```

Example response:

```json
{
  "entities": {
    "SOFTWARE": ["Outlook"],
    "DEVICE": ["laptop"]
  }
}
```

### `POST /priority`

Purpose: assign a rule-based priority and preserve the matched keyword rule.

Example request:

```json
{
  "ticket_text": "Production server is down"
}
```

Example response:

```json
{
  "priority": "Critical",
  "matched_rule": "server down"
}
```

### `POST /route`

Purpose: map a predicted category to a support team.

Example request:

```json
{
  "category": "Hardware"
}
```

Example response:

```json
{
  "category": "Hardware",
  "assigned_team": "Hardware Team"
}
```

### `POST /analyze`

Purpose: run the complete workflow and persist the result.

Example request:

```json
{
  "ticket_text": "Unable to login to Outlook on my laptop"
}
```

Example response:

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

## Error Responses

### Validation errors

FastAPI returns HTTP `422` when required request fields are missing or invalid.

Example:

```json
{
  "detail": [
    {
      "loc": ["body", "ticket_text"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

### Unsupported routing category

`POST /route` and `POST /analyze` return HTTP `400` if routing receives an unsupported category.

Example:

```json
{
  "detail": "Unsupported category for routing: Unknown"
}
```

### Model loading failure

`GET /metrics` returns HTTP `503` if required model artifacts cannot be loaded.

Example:

```json
{
  "detail": "Label mapping not found: D:\\DEVELOPMENT\\CODEx_PROJECTS\\ticket-routing-system\\models\\distilbert\\label_mapping.json"
}
```

## Known Limitations

- The API has no authentication or rate limiting.
- `/analyze` persists the workflow result, but matched priority rules are not currently stored in SQLite.
- The dashboard still calls several specialized endpoints in addition to `/analyze`; it does not yet rely on `/analyze` alone.
- Entity extraction is rule-based and depends on configured patterns rather than trained NER weights.

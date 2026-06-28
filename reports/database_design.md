# Phase 9 SQLite Persistence Design

## Scope

Phase 9 implements SQLite persistence for prediction, entity, priority, and routing decisions.

This phase does not implement Docker deployment.

## Database File

```text
data/ticket_routing.db
```

## ER Diagram

```text
ticket_predictions
------------------
id PK
ticket_text
predicted_category
confidence_score
entities_json
priority
assigned_team
created_at
```

## Schema Design

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | Integer primary key | Unique prediction identifier |
| `ticket_text` | Text | Original user ticket text |
| `predicted_category` | String | DistilBERT predicted category |
| `confidence_score` | Float | Classification confidence |
| `entities_json` | Text | Extracted entities serialized as JSON |
| `priority` | String | Rule-based priority |
| `assigned_team` | String | Routing engine assigned support team |
| `created_at` | DateTime UTC | Persistence timestamp |

## Persistence Workflow

```text
POST /analyze
    |
    v
TicketAnalysisService.analyze
    |
    +-- predict category
    +-- extract entities
    +-- assign priority
    +-- route category
    |
    v
PredictionRepository.save_prediction
    |
    v
ticket_predictions
```

Tables are created automatically if missing.

## Repository API

`PredictionRepository` supports:

- `save_prediction(...)`
- `get_recent_predictions(limit=50)`
- `get_prediction_count()`
- `get_category_distribution()`
- `get_priority_distribution()`

## FastAPI Integration

After successful `/analyze`, the prediction is automatically saved.

Additional endpoints:

- `GET /history`
- `GET /analytics`

`GET /analytics` returns:

- Total predictions
- Category distribution
- Priority distribution

## Analytics Support

The current schema supports dashboard metrics such as:

- Recent ticket analysis history
- Total predictions served
- Category usage distribution
- Priority distribution
- Routing/team trend analysis through `assigned_team`

Future phases can extend this with user feedback, corrected category, corrected priority, model version, latency, and request source.


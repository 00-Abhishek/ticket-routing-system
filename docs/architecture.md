# Architecture

## System Overview

```text
Streamlit Dashboard
        |
        v
FastAPI Backend
        |
        v
TicketAnalysisService
        |
        +-- DistilBERT classifier
        +-- spaCy EntityExtractor
        +-- PriorityEngine
        +-- TicketRouter
        +-- PredictionRepository
                |
                v
        SQLite (ticket_predictions)
```

## End-to-End Flow

```text
Ticket Input
  -> Preprocessing
  -> DistilBERT classification
  -> Entity extraction
  -> Priority assignment
  -> Routing
  -> SQLite persistence
  -> API response
  -> Dashboard display
```

## Major Components

### Classification

- Baseline training scripts under `scripts/`
- Final runtime classifier: `src/api/services.py`
- Saved artifacts under `models/`

### Entity extraction

- Configurable patterns: `config/entity_patterns.json`
- Runtime extractor: `src/ner/extractor.py`

### Priority

- Rules: `src/priority/rules.py`
- Engine: `src/priority/engine.py`

### Routing

- Rules: `src/routing/rules.py`
- Router: `src/routing/router.py`

### API

- Routes: `src/api/app.py`
- Schemas: `src/api/schemas.py`
- Dependency loader: `src/api/dependencies.py`

### Persistence

- SQLAlchemy database setup: `src/database/database.py`
- ORM model: `src/database/models.py`
- Repository layer: `src/database/repository.py`

### Dashboard

- Main app: `dashboard/app.py`
- Helpers: `dashboard/components.py`, `dashboard/charts.py`, `dashboard/utils.py`

## Deployment Shape

Docker Compose runs:

- `backend` on port `8000`
- `dashboard` on port `8501`

Mounted directories:

- `data/`
- `models/`
- `reports/`

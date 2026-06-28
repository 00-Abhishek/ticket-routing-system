# Requirements

## Project Goal

Build a production-ready NLP system that classifies IT support tickets, extracts useful entities, assigns operational priority, routes tickets to support teams, persists analysis history, and exposes the workflow through an API and dashboard.

## Dataset

Path:

```text
data/all_tickets_processed_improved_v3.csv
```

Columns:

- `Document`
- `Topic_group`

## Implemented Requirements

### Data and preprocessing

- Dataset exploration and EDA
- Class-distribution reporting
- Ticket-length and noise analysis
- Reusable text preprocessing pipeline

### Classification models

- TF-IDF + Logistic Regression baseline
- TF-IDF + Multinomial Naive Bayes baseline
- DistilBERT base uncased as the final classifier
- Stratified 80/10/10 split for training workflows
- Reproducible training with seeded execution
- Saved model artifacts and metric reports

### NLP workflow

- Rule-based spaCy entity extraction
- Rule-based priority engine
- Deterministic routing engine

### Application layer

- FastAPI backend with prediction, entity, priority, routing, metrics, history, analytics, and full-analysis endpoints
- Streamlit dashboard for analysis and report-driven analytics
- SQLite persistence with SQLAlchemy
- Docker and Docker Compose configuration
- Automated unit and integration tests

## Explicitly Not Implemented

- LSTM classifier
- Word2Vec-based sequence modeling
- Trained statistical NER model
- API authentication and authorization

These items must not be described as completed repository features.

## Optional Future Work

- Add an LSTM comparison model only if future academic requirements explicitly demand it
- Use `/analyze` as the single dashboard inference endpoint
- Replace demo dashboard priority and routing charts with live `/analytics` data
- Persist priority `matched_rule` to SQLite
- Add API authentication suitable for academic deployment

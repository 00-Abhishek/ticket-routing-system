# Automated IT Support Ticket Classification and Routing System

This repository contains the complete NTCC project implementation for classifying IT support tickets, extracting technical entities, assigning rule-based priority, routing tickets to support teams, persisting analysis history, and exposing the workflow through FastAPI, Streamlit, SQLite, and Docker.

# 🌐 Live Demo

Try it out here: [Automated IT Support Ticket Classification and Routing System](https://00-abhishek-ticket-routing-system-dashboardapp-a3vhvs.streamlit.app/)
## Project Overview

The system solves a common IT service-desk problem: large volumes of support tickets arrive as unstructured text, and manual triage is slow, inconsistent, and difficult to scale. This project automates the workflow with:

- DistilBERT for eight-class ticket classification
- spaCy `EntityRuler` for configurable entity extraction
- A rule-based priority engine
- A deterministic routing engine
- FastAPI for backend inference and analytics
- Streamlit for an interactive dashboard
- SQLite with SQLAlchemy for persistence

## Implemented Workflow

```text
Ticket Input
  -> Text preprocessing
  -> DistilBERT classification
  -> Entity extraction
  -> Priority assignment
  -> Routing
  -> SQLite persistence
  -> FastAPI response
  -> Streamlit visualization
```

## Model Stack

### Final classifier

- `DistilBERT base uncased`
- Stratified 80/10/10 train/validation/test split
- Early stopping and checkpointing
- CUDA and mixed precision support when available

### Baselines

- TF-IDF + Logistic Regression
- TF-IDF + Multinomial Naive Bayes

### Verified test metrics

| Model | Accuracy | Precision Macro | Recall Macro | F1 Macro |
| --- | --- | --- | --- | --- |
| Logistic Regression | 0.8616 | 0.8507 | 0.8762 | 0.8622 |
| Naive Bayes | 0.7795 | 0.8802 | 0.6814 | 0.7336 |
| DistilBERT | 0.8878 | 0.8922 | 0.8847 | 0.8883 |

Source reports:

- `reports/model_baselines.md`
- `reports/model_distilbert.md`

## Routing and Priority

### Routing

Predicted categories are mapped to support teams:

- `Hardware` -> `Hardware Team`
- `HR Support` -> `HR Team`
- `Access` -> `Access Management Team`
- `Storage` -> `Storage Team`
- `Purchase` -> `Procurement Team`
- `Administrative rights` -> `System Administration Team`
- `Internal Project` -> `Internal Projects Team`
- `Miscellaneous` -> `Service Desk Team`

### Priority

Keyword-driven priority assignment is evaluated in this order:

- `Critical`
- `High`
- `Medium`
- `Low`

If no keyword rule matches, the default priority is `Medium`.

## API

Implemented FastAPI endpoints:

- `GET /health`
- `GET /metrics`
- `GET /history`
- `GET /analytics`
- `POST /predict`
- `POST /entities`
- `POST /priority`
- `POST /route`
- `POST /analyze`

Run locally:

```bash
uvicorn src.api.app:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Streamlit Dashboard

The dashboard communicates with the FastAPI backend and provides:

- Ticket input and analysis
- Category and confidence display
- Extracted entity display
- Priority and matched-rule display
- Routing destination display
- Report-driven analytics charts
- API health monitoring

Run locally:

```bash
streamlit run dashboard/app.py
```

## Dataset

Expected dataset path:

```text
data/all_tickets_processed_improved_v3.csv
```

Required columns:

- `Document`
- `Topic_group`

The dataset is intentionally not tracked in Git.

## Installation

### Local Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Required model artifacts

The repository expects trained model artifacts under:

```text
models/
```

The final DistilBERT weights are tracked with Git LFS because the main model file is large.

## Docker Deployment

Build and start both services:

```bash
docker compose up --build
```

Expected access:

- FastAPI: `http://localhost:8000/docs`
- Streamlit: `http://localhost:8501`

Compose mounts:

- `./data:/app/data`
- `./models:/app/models`
- `./reports:/app/reports`

## Testing

Run the full suite:

```bash
pytest
```

Current verified status:

- `58/58` tests passing

## Repository Structure

```text
ticket-routing-system/
├── config/
├── dashboard/
├── data/
├── docs/
├── models/
├── reports/
├── scripts/
├── src/
├── tests/
├── .dockerignore
├── .gitignore
├── AGENTS.md
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── README.md
└── requirements.txt
```

## Current Status

Implemented and verified:

- EDA and preprocessing pipeline
- Baseline models
- DistilBERT classifier
- Rule-based entity extraction
- Routing engine
- Priority engine
- FastAPI backend
- Streamlit dashboard
- SQLite persistence
- Docker configuration
- Automated tests

Not implemented:

- LSTM model
- Trained statistical NER
- API authentication

These remain optional future work and should not be claimed as completed features.

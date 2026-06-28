# Automated Classification and Routing of IT Support Tickets using NLP

## Project Overview

Build a production-quality NLP system that automatically classifies IT support tickets, extracts entities, predicts priority, and routes tickets to the correct support team.

Dataset contains:

* Document
* Topic_group

Approximately 47,837 records.

Categories:

* Hardware
* HR Support
* Access
* Storage
* Purchase
* Internal Project
* Administrative rights
* Miscellaneous

---

## Technical Requirements

Python 3.11

Backend:

* FastAPI

Machine Learning:

* Scikit-learn
* TensorFlow
* Hugging Face Transformers

NLP:

* spaCy
* NLTK

Database:

* SQLite

Dashboard:

* Streamlit

Deployment:

* Docker

---

## Required Models

### Baseline Models

Implement:

1. TF-IDF + Logistic Regression
2. TF-IDF + Naive Bayes

Generate evaluation metrics.

---

### Deep Learning Model

Implement:

1. LSTM

Generate evaluation metrics.

---

### Transformer Model

Implement:

1. DistilBERT

This is the primary production model.

Generate:

* Accuracy
* Precision
* Recall
* F1 Score
* Confusion Matrix

---

## Entity Extraction

Use spaCy.

Extract:

* SOFTWARE
* DEVICE
* ERROR_CODE

Support rule-based patterns and extensibility.

---

## Priority Engine

Priority Levels:

* Critical
* High
* Medium
* Low

Use configurable business rules.

---

## Routing Rules

Hardware → Hardware Team

HR Support → HR Team

Access → Access Management Team

Storage → Storage Team

Purchase → Procurement Team

Administrative rights → System Administration Team

Internal Project → Internal Projects Team

Miscellaneous → Service Desk Team

---

## API Requirements

Endpoints:

POST /predict

POST /entities

POST /route

GET /health

GET /metrics

---

## Dashboard Requirements

Features:

* Ticket submission
* Prediction display
* Confidence scores
* Entity extraction
* Routing results
* Dataset statistics
* Model metrics
* Charts

---

## Code Quality

Requirements:

* Type hints
* Docstrings
* Modular architecture
* Unit tests
* Logging
* Error handling

Avoid monolithic files.

Keep business logic separated from API layer.

---

## Deliverables

* Trained models
* API
* Dashboard
* Docker support
* Tests
* Documentation
* Evaluation report

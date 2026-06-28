# NTCC Report Forensic Audit

## Executive Summary

The repository is the source of truth for this audit. The audited report is
`NTCC_Final_Report_AbhishekPal.docx`.

**Overall repository-to-report match: 28.8%.**

Scoring basis: 85 material claim groups were checked across the abstract,
chapters, tables, figures, dataset, models, NER, routing, API, database,
dashboard, Docker, and results. The report contains 15 correct claim groups,
19 partially correct claim groups, 43 incorrect claim groups, and 8 material
implementation areas missing from the report. Partial claims receive half
credit: `(15 + 19 * 0.5) / 85 = 28.8%`.

The report describes a substantially different system from the repository. Its
dominant narrative is a four-class Flask application with a trained
Bidirectional LSTM, Word2Vec embeddings, and a trained spaCy NER model. The
repository actually contains an eight-class FastAPI application whose
production classifier is DistilBERT, with TF-IDF Logistic Regression and
Multinomial Naive Bayes baselines, configurable spaCy `EntityRuler` extraction,
a rule-based priority engine, deterministic routing, SQLite/SQLAlchemy
persistence, a Streamlit dashboard, and Docker Compose deployment files.

### Highest-Risk Discrepancies

| Area | Audit Status | Finding |
| --- | --- | --- |
| Dataset | Incorrect | Report states 2,650 tickets and 4 classes; actual dataset has 47,837 tickets and 8 classes. |
| Split | Incorrect | Report states 70/15/15; actual model split is stratified 80/10/10. |
| LSTM and Word2Vec | Incorrect | No LSTM/Word2Vec implementation, saved model, training report, or metrics exist. |
| NER | Incorrect | NER is configurable rule-based spaCy `EntityRuler`, not a trained transition-based model. |
| API | Incorrect | API is FastAPI with 9 project endpoints, not Flask with 3 `/api/*` endpoints. |
| Results | Incorrect | Reported baseline, LSTM, DistilBERT, per-class, NER, latency, and sample-test results are unsupported or wrong. |
| Missing system components | Missing | Priority engine, SQLite, SQLAlchemy, Streamlit, Plotly, Docker Compose, persistence analytics, and system tests are omitted. |
| Figures | Missing | The Word report contains zero embedded inline figures, despite generated repository charts and screenshots being available. |

### Evidence Hierarchy

1. Executable source code and configuration.
2. Saved model artifacts and generated reports.
3. Tests and direct repository inspection.
4. Design documentation, only where consistent with source code.

Claims not provable from these sources are marked **UNVERIFIED - REQUIRES
RE-EXECUTION**.

## Chapter-by-Chapter Audit

### Front Matter, Abstract, Keywords, and Lists

**Status: Incorrect**

What matches:

- The project title broadly matches the implemented ticket classification and
  routing system.
- DistilBERT, TF-IDF, Logistic Regression, Naive Bayes, spaCy, and NLP are
  relevant technologies.

What is incorrect:

- The abstract states four categories, an LSTM result of approximately 85%,
  DistilBERT accuracy of 91.4%, trained spaCy NER, Flask, and sub-200ms latency.
  None of these claims matches repository evidence.
- Keywords include LSTM, Flask REST API, and generic deep-learning claims that
  imply implemented components not present in the repository.
- The list of tables describes unsupported LSTM and NER performance tables.

What is missing:

- FastAPI, Streamlit, SQLite, SQLAlchemy, rule-based priority assignment,
  configurable routing, Docker Compose, and the eight-class taxonomy.

Evidence:

- `reports/final_results.md`
- `reports/model_distilbert.md`
- `src/api/app.py`
- `src/ner/extractor.py`
- `src/priority/engine.py`
- `src/database/models.py`
- `dashboard/app.py`
- `docker-compose.yml`

Administrative statements about the internship organisation, dates, academic
supervision, originality, hardware ownership, and authorship are **UNVERIFIED -
REQUIRES RE-EXECUTION** because they cannot be proven from repository artifacts.

### Chapter 1: Introduction

**Status: Partially Correct**

What matches:

- The motivation for automating manual IT ticket classification and routing is
  consistent with the implemented project.
- Single-label classification, modularity, and documented REST access are
  relevant.
- Multilingual support, multi-label classification, and automatic resolution
  recommendation are not implemented.

What is incorrect:

- Sections 1.3, 1.4, and 1.5 define a four-category problem using Network
  Issues, OS Issues, Application Bugs, and Security Incidents. The implemented
  labels are Access, Administrative rights, HR Support, Hardware, Internal
  Project, Miscellaneous, Purchase, and Storage.
- Objectives claim an implemented Bidirectional LSTM, Word2Vec, trained NER,
  and Flask API.
- The report claims NER-enriched routing. The actual routing decision is based
  only on the predicted category; entities are returned and persisted but do
  not alter routing.

What is missing:

- Priority assignment, SQLite persistence, dashboard analytics, and Docker
  deployment objectives.

Evidence:

- `models/distilbert/label_mapping.json`
- `src/routing/rules.py`
- `src/api/services.py`
- `src/database/repository.py`
- `dashboard/app.py`

### Chapter 2: Literature Review

**Status: Partially Correct**

What matches:

- The general descriptions of TF-IDF, Logistic Regression, Naive Bayes,
  Transformers, DistilBERT, NER, and ticket automation are relevant background.
- LSTM and trained NER are valid literature topics.

What is incorrect:

- Section 2.7 states the project provides a comparative evaluation of four
  model architectures and NER-augmented routing. Only three classifiers have
  proven artifacts and metrics, and routing is category-to-team mapping.
- Citations and external literature claims were not independently validated in
  this repository audit.

What is missing:

- Literature/context for rule-based `EntityRuler`, rule-based priority
  assignment, FastAPI, persistence, and dashboard-driven operational workflows.

Evidence:

- `models/`
- `reports/model_baselines.md`
- `reports/model_distilbert.md`
- `src/ner/extractor.py`
- `src/routing/router.py`

### Chapter 3: System Design

**Status: Incorrect**

What matches:

- The implementation is modular and separates classification, NER, routing,
  and service concerns.
- DistilBERT and NER are loaded once by a service singleton.
- Routing rules are configurable and separate from model training.

What is incorrect:

- The service layer is FastAPI/Uvicorn, not Flask.
- The preprocessing description includes IP anonymisation, placeholders,
  tokenisation, stop-word removal, and lemmatisation that do not exist.
- There is no `preprocessing.py` with `preprocess(text, mode)`. Actual code is
  `src/preprocessing/text.py` with `clean_ticket_text` and
  `normalize_ticket_series`.
- There is no classifier factory, runtime A/B selection, Keras LSTM, SLA tier,
  or escalation-rule routing.
- NER supports five labels, not three, and uses rules rather than a trained
  pipeline.
- Table 3.1 lists three nonexistent `/api/*` endpoints.
- Table 3.2 lists Flask, TensorFlow/Keras, NLTK, and inaccurate pinned versions.

What is missing:

- Priority engine, persistence repository, SQLite, SQLAlchemy, Streamlit,
  Plotly, `/history`, `/analytics`, and Docker architecture.

Evidence:

- `src/api/app.py`
- `src/api/services.py`
- `src/preprocessing/text.py`
- `src/priority/engine.py`
- `src/routing/router.py`
- `src/database/repository.py`
- `dashboard/app.py`
- `requirements.txt`

### Chapter 4: Methodology

**Status: Incorrect**

What matches:

- Dataset records use free-form ticket text and a target label.
- Stratification and random seed 42 are used.
- TF-IDF uses unigrams/bigrams, `min_df=2`, and `max_features=50,000`.
- DistilBERT uses `distilbert-base-uncased`, max length 128, batch size 16,
  learning rate `2e-5`, weight decay `0.01`, warmup, mixed precision where
  CUDA is available, checkpointing, and validation macro-F1 selection.
- Accuracy, macro precision, macro recall, and macro F1 are generated.

What is incorrect:

- Dataset size, classes, percentages, and 70/15/15 split are wrong.
- Dataset origin and expert annotation claims are **UNVERIFIED - REQUIRES
  RE-EXECUTION**.
- IP/placeholder replacement, error-code tokenisation, NLTK stop-word removal,
  spaCy tokenisation, and lemmatisation are not implemented.
- Word2Vec and Bidirectional LSTM sections describe nonexistent work.
- Baseline parameters are wrong. Actual Logistic Regression uses `C=2.0`,
  `class_weight="balanced"`, `max_iter=1000`; MultinomialNB uses `alpha=0.5`.
- Models are not assembled as scikit-learn `Pipeline` objects.
- DistilBERT uses 8 labels and requests 3 epochs, not 4 labels and 5 epochs.
- No `WeightedRandomSampler` is used.
- The NER training corpus, Prodigy annotations, 30 epochs, and held-out NER
  evaluation do not exist.
- Experiments were not proven to have been repeated three times.

What is missing:

- Actual EDA statistics, class distribution, priority methodology, routing
  rules, persistence methodology, and integration-test strategy.

Evidence:

- `data/all_tickets_processed_improved_v3.csv`
- `reports/eda/dataset_profile.json`
- `reports/eda/class_distribution.csv`
- `src/classification/baselines.py`
- `scripts/run_phase4_distilbert.py`
- `models/distilbert/checkpoint-7176/trainer_state.json`
- `config/entity_patterns.json`

### Chapter 5: Implementation

**Status: Incorrect**

What matches:

- Python, PyTorch, Transformers, spaCy, scikit-learn, Pandas, and Matplotlib
  are used.
- DistilBERT is loaded through Hugging Face Transformers and trained using
  `Trainer`.
- Saved model selection is based on validation macro F1.
- Models and services are loaded once for API use.

What is incorrect:

- Ubuntu, CPU, RAM, IDE, and most exact environment-version claims are
  **UNVERIFIED - REQUIRES RE-EXECUTION**.
- The generated DistilBERT report identifies the training GPU as NVIDIA
  GeForce RTX 4060 Ti, not RTX 3050.
- `requirements.txt` uses minimum version constraints and does not include
  TensorFlow, Keras, NLTK, Flask, Flask-RESTful, or marshmallow.
- Baselines are not scikit-learn pipelines and do not use 5-fold CV.
- LSTM implementation and training claims are unsupported.
- DistilBERT has 8 labels, uses 3 epochs, and has no weighted sampler.
- NER is not trained or loaded with `spacy.load`.
- The API is FastAPI, uses Pydantic schemas, and exposes 9 project endpoints.
- Tests use pytest, not unittest. The claim about replaying 200 held-out samples
  and zero errors is unsupported.

What is missing:

- SQLite/SQLAlchemy, priority engine, dashboard, Docker, and their tests.

Evidence:

- `requirements.txt`
- `reports/model_distilbert.md`
- `models/distilbert/config.json`
- `src/api/app.py`
- `tests/`

### Chapter 6: Results and Analysis

**Status: Incorrect**

What matches:

- DistilBERT is the strongest tested model.
- Generated results include accuracy, precision, recall, F1, per-class metrics,
  and confusion matrices.

What is incorrect:

- The split, repeated-run methodology, dataset table, all baseline values,
  LSTM table, DistilBERT values, per-class labels/values, NER metrics, model
  comparison, 50-ticket API accuracy, and 127ms latency are unsupported or
  incorrect.
- The report's narrative analyses nonexistent four-class confusion patterns.

What is missing:

- Actual eight-class per-class results, actual confusion matrices, validation
  metrics, weighted metrics, and test-suite result.

Evidence:

- `reports/model_baselines.md`
- `reports/model_distilbert.md`
- `reports/final_results.md`
- `tests/`

### Chapter 7: Conclusion and Future Scope

**Status: Incorrect**

What matches:

- DistilBERT is the recommended production classifier.
- Multi-label classification, multilingual support, active learning,
  explainability, resolution recommendation, and ITSM connectors remain future
  work.

What is incorrect:

- The conclusion repeats fabricated/unsupported 78.3%, 85.2%, 91.4%, trained
  NER F1, Flask, latency, four-model comparison, and four-category claims.
- Docker containerisation is listed as future work although Dockerfile and
  Docker Compose configuration already exist.
- Routing is described as entity-enriched decision logic; actual routing is
  category-based.

What is missing:

- Completed FastAPI, priority engine, SQLite persistence, Streamlit dashboard,
  Docker configuration, and automated testing.

Evidence:

- `reports/final_results.md`
- `Dockerfile`
- `docker-compose.yml`
- `reports/system_validation.md`

## Table and Figure Audit

### Report Tables

| Report Table | Status | Correction |
| --- | --- | --- |
| Abbreviations | Partially Correct | Terms are generally valid, but LSTM, Flask-related context, CNN, and RNN do not describe implemented components. Add FastAPI, SQLAlchemy, SQLite, ORM, and UI/dashboard terms if used. |
| Table 3.1 REST API Endpoint Specification | Incorrect | Replace three `/api/*` endpoints with the nine implemented project endpoints listed in the API Audit. |
| Table 3.2 Technology Stack Summary | Incorrect | Replace Flask/TensorFlow/Keras/NLTK stack with the actual stack listed below. |
| Table 4.1 Dataset Category Description | Incorrect | Replace four categories with the eight actual labels and counts. |
| Table 6.1 Dataset Statistics | Incorrect | Replace all values with the Dataset Audit table. Vocabulary size is unverified. |
| Table 6.2 Baseline Model Performance | Incorrect | Replace with actual test macro metrics from `reports/model_baselines.md`. |
| Table 6.3 LSTM Model Performance | Incorrect | Replace with “Not implemented; no metrics available.” |
| Table 6.4 DistilBERT Performance | Incorrect | Replace with actual test metrics from `reports/model_distilbert.md`. |
| Table 6.5 DistilBERT Per-Class Report | Incorrect | Replace with the actual eight-class table in the Results Audit. |
| Table 6.6 NER Performance | Incorrect | No labeled NER evaluation exists; all values are unverified. |
| Table 6.7 Comprehensive Model Comparison | Incorrect | Replace with the actual three-model comparison. |

### Figures

**Status: Missing**

The Word report contains **zero embedded inline figures**. No figure can be
verified as present in the report.

Actual figure/screenshot artifacts available for insertion:

- `reports/eda/class_distribution.png`
- `reports/eda/ticket_word_count_distribution.png`
- `reports/eda/ticket_clean_length_distribution.png`
- `reports/eda/text_quality_signals.png`
- `docs/screenshots/dashboard_home.png`
- `docs/screenshots/prediction_results.png`
- `docs/screenshots/analytics_page.png`
- `docs/screenshots/fastapi_swagger_docs.png`
- `docs/screenshots/database_history_endpoint.png`

Recommended figure descriptions are supplied in
`reports/report_replacements.md`.

## Dataset Audit

### Correct Dataset Facts

| Item | Report Value | Actual Value | Status | Evidence |
| --- | --- | --- | --- | --- |
| Dataset name | Not consistently named | `data/all_tickets_processed_improved_v3.csv` | Missing | Dataset file; training scripts |
| Rows | 2,650 | 47,837 | Incorrect | `reports/eda/dataset_profile.json` |
| Columns | Not stated in result table | 2: `Document`, `Topic_group` | Missing | Source CSV; EDA report |
| Classes | 4 | 8 | Incorrect | `models/distilbert/label_mapping.json` |
| Split | 70/15/15 | Stratified 80/10/10 | Incorrect | `src/classification/baselines.py` |
| Train rows | 1,855 | 38,269 | Incorrect | Model reports |
| Validation rows | 397 | 4,784 | Incorrect | Model reports |
| Test rows | 398 | 4,784 | Incorrect | Model reports |
| Average ticket length | 67.4 postprocessed tokens | 43.60 average cleaned word count; 291.88 average raw characters | Incorrect | EDA profile |
| Vocabulary size | 14,823 | UNVERIFIED - REQUIRES RE-EXECUTION | Unsupported | No generated vocabulary statistic |
| Duplicates | Not stated | 0 | Missing | EDA profile |
| Missing documents/labels | Not stated | 0 / 0 | Missing | EDA profile |
| Imbalance ratio | “Moderate” | 7.7369 largest/smallest | Partially Correct | EDA profile |

### Actual Class Distribution

| Class | Tickets | Percentage |
| --- | ---: | ---: |
| Hardware | 13,617 | 28.47% |
| HR Support | 10,915 | 22.82% |
| Access | 7,125 | 14.89% |
| Miscellaneous | 7,060 | 14.76% |
| Storage | 2,777 | 5.81% |
| Purchase | 2,464 | 5.15% |
| Internal Project | 2,119 | 4.43% |
| Administrative rights | 1,760 | 3.68% |

Additional proven EDA values:

- Median word count: 26
- Average cleaned character length: 291.87
- Median cleaned character length: 175
- Very short rows under 3 words: 14
- Rows containing URLs, email addresses, or numbers in the EDA scan: 0

## Model Audit

| Model | Exists in Code | Saved Artifact | Trained Metrics | Audit Finding |
| --- | --- | --- | --- | --- |
| TF-IDF + Logistic Regression | Yes | `models/logistic_regression.pkl`, shared vectorizer | Yes | Real and reportable |
| TF-IDF + Multinomial Naive Bayes | Yes | `models/naive_bayes.pkl`, shared vectorizer | Yes | Real and reportable |
| DistilBERT base uncased | Yes | `models/distilbert/` plus checkpoints | Yes | Real, trained production model |
| Bidirectional LSTM | No | None | None | Report claims are unsupported/fabricated |
| Word2Vec | No | None | None | Report claims are unsupported/fabricated |

Actual baseline configuration:

- Shared `TfidfVectorizer`: max 50,000 features, unigram/bigram,
  `min_df=2`, `max_df=0.95`, `sublinear_tf=True`.
- Logistic Regression: `C=2.0`, `class_weight="balanced"`,
  `max_iter=1000`, seed 42.
- Multinomial Naive Bayes: `alpha=0.5`.

Actual DistilBERT configuration:

- `distilbert-base-uncased`
- 8 output labels
- stratified 80/10/10 split
- seed 42
- max length 128
- batch size 16
- 3 requested and completed epochs
- learning rate `2e-5`
- weight decay `0.01`
- mixed precision enabled during recorded run
- early stopping callback and checkpointing enabled
- best checkpoint: `checkpoint-7176`
- recorded training device: NVIDIA GeForce RTX 4060 Ti

Training duration, inference latency, and repeated-run variance are
**UNVERIFIED - REQUIRES RE-EXECUTION**.

## NER Audit

**Actual implementation:** configurable, rule-based spaCy extraction.

- Uses `spacy.blank("en")`.
- Adds spaCy `EntityRuler`.
- Loads configurable patterns from `config/entity_patterns.json`.
- Uses case-insensitive phrase matching.
- Uses strict token regex patterns for error codes.
- No labeled NER dataset, Prodigy export, `config.cfg`, trained model directory,
  or entity-level evaluation metrics exist.

Actual entity types:

- `SOFTWARE`
- `DEVICE`
- `ERROR_CODE`
- `SYSTEM`
- `LOCATION`

The report's NER precision/recall/F1 values are **UNVERIFIED - REQUIRES
RE-EXECUTION** and must be removed.

Evidence:

- `src/ner/extractor.py`
- `config/entity_patterns.json`
- `reports/entity_analysis.md`
- `reports/entity_extraction.md`
- `tests/test_ner.py`

## Routing Audit

**Actual routing architecture:**

```text
Predicted Category
  -> TicketRouter.route(category)
  -> CATEGORY_TO_TEAM lookup
  -> RouteResult(category, assigned_team)
```

Actual mappings:

| Category | Assigned Team |
| --- | --- |
| Hardware | Hardware Team |
| HR Support | HR Team |
| Access | Access Management Team |
| Storage | Storage Team |
| Purchase | Procurement Team |
| Administrative rights | System Administration Team |
| Internal Project | Internal Projects Team |
| Miscellaneous | Service Desk Team |

Unknown categories raise `UnsupportedCategoryError`. Entities, SLA tiers, and
escalation rules do not currently change routing.

**Actual priority architecture:**

```text
Ticket Text
  -> normalize text
  -> evaluate Critical, High, Medium, Low keyword rules
  -> PriorityResult(priority, matched_rule)
```

If no rule matches, priority defaults to Medium. Priority is independent from
the classifier and is included in `/priority` and `/analyze`.

Evidence:

- `src/routing/rules.py`
- `src/routing/router.py`
- `src/priority/rules.py`
- `src/priority/engine.py`

## API Audit

The actual API uses **FastAPI**, Pydantic, and Uvicorn. Flask-specific content
must be removed.

| Method | Endpoint | Actual Purpose | Main Response Fields |
| --- | --- | --- | --- |
| GET | `/health` | Health status | `status` |
| GET | `/metrics` | Model/rule metadata | `model_name`, `number_of_classes`, `available_entities`, `supported_priorities` |
| GET | `/history` | Recent persisted analyses | `predictions` |
| GET | `/analytics` | Persistence analytics | `total_predictions`, `category_distribution`, `priority_distribution` |
| POST | `/predict` | DistilBERT classification | `category`, `confidence` |
| POST | `/entities` | Rule-based entity extraction | `entities` |
| POST | `/priority` | Rule-based priority assignment | `priority`, `matched_rule` |
| POST | `/route` | Category-to-team routing | `category`, `assigned_team` |
| POST | `/analyze` | Full workflow and persistence | `category`, `confidence`, `entities`, `priority`, `matched_rule`, `assigned_team` |

Automatic OpenAPI/Swagger documentation is available at `/docs`.

Evidence:

- `src/api/app.py`
- `src/api/schemas.py`
- `src/api/services.py`
- `tests/test_api.py`

## Database Audit

The implementation uses SQLite and SQLAlchemy.

- Database file: `data/ticket_routing.db`
- ORM table: `ticket_predictions`
- Tables are created automatically through `Base.metadata.create_all`.
- `/analyze` persists successful prediction workflows.
- Entities are serialized as JSON text.
- Timestamps are generated in UTC.

Actual columns:

| Column | Type/Purpose |
| --- | --- |
| `id` | Autoincrement integer primary key |
| `ticket_text` | Original ticket text |
| `predicted_category` | Classifier output |
| `confidence_score` | Classifier confidence |
| `entities_json` | JSON-serialized entities |
| `priority` | Rule-based priority |
| `assigned_team` | Routing result |
| `created_at` | UTC timestamp |

Repository analytics support total count, category distribution, and priority
distribution.

Evidence:

- `src/database/models.py`
- `src/database/database.py`
- `src/database/repository.py`
- `tests/test_database.py`

## Dashboard Audit

The implemented dashboard uses Streamlit and communicates with the FastAPI
backend through HTTP.

Implemented features:

- API URL from `BACKEND_URL`, defaulting to `http://127.0.0.1:8000`
- health status using `GET /health`
- ticket input and analysis workflow
- prediction and confidence display
- grouped entities
- priority and matched rule
- assigned routing team
- full analysis display
- analytics tab
- model comparison table/chart from generated reports
- class distribution chart from EDA artifacts
- sample/demo priority and routing charts
- API and response-shape error handling

The priority and routing distribution charts are static demo data; they do not
currently call `/analytics`.

Evidence:

- `dashboard/app.py`
- `dashboard/components.py`
- `dashboard/charts.py`
- `dashboard/utils.py`
- `tests/test_dashboard_utils.py`

## Docker Audit

Docker deployment configuration exists and was validated locally in the repository environment on 2026-06-28.

- Base image: `python:3.11-slim`
- Backend service: Uvicorn on port 8000
- Dashboard service: Streamlit on port 8501
- Dashboard waits for healthy backend
- Backend healthcheck: `GET /health`
- Volumes: `data/`, `models/`, `reports/`
- Environment variable: `BACKEND_URL=http://backend:8000`
- Startup command: `docker compose up --build`

Validated status: `docker compose build` succeeded, `docker compose up -d` started both services, backend health and dashboard health passed, `/predict` and `/analyze` returned valid responses, model/report mounts were present, and SQLite persistence was confirmed through `/history`, `/analytics`, and the mounted host database file.

Evidence:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `tests/test_config.py`
- `reports/docker_deployment.md`

## Results Audit

### Chapter 6 Table 6.1: Dataset Statistics

| Metric | Original Value | Correct Value | Evidence |
| --- | --- | --- | --- |
| Total tickets | 2,650 | 47,837 | `reports/eda/dataset_profile.json` |
| Training set | 1,855 (70%) | 38,269 (80%) | Model reports |
| Validation set | 397 (15%) | 4,784 (10%) | Model reports |
| Test set | 398 (15%) | 4,784 (10%) | Model reports |
| Average ticket length | 67.4 tokens | 43.60 average cleaned words | EDA profile |
| Vocabulary size | 14,823 | UNVERIFIED - REQUIRES RE-EXECUTION | No artifact |
| Target categories | 4 | 8 | Label mapping |

### Chapter 6 Tables 6.2, 6.3, 6.4, and 6.7

Correct values below are test-set macro metrics.

| Model | Original Accuracy | Correct Accuracy | Original Precision | Correct Macro Precision | Original Recall | Correct Macro Recall | Original F1 | Correct Macro F1 | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| TF-IDF + Naive Bayes | 75.6% | 77.95% | 0.74 | 0.8802 | 0.75 | 0.6814 | 0.74 | 0.7336 | `reports/model_baselines.md` |
| TF-IDF + Logistic Regression | 78.3% | 86.16% | 0.77 | 0.8507 | 0.78 | 0.8762 | 0.77 | 0.8622 | `reports/model_baselines.md` |
| Bidirectional LSTM | 85.2% | UNVERIFIED - REQUIRES RE-EXECUTION | 0.85 | UNVERIFIED | 0.85 | UNVERIFIED | 0.84 | UNVERIFIED | No implementation/artifact |
| DistilBERT | 91.4% | 88.78% | 0.91 | 0.8922 | 0.90 | 0.8847 | 0.90 | 0.8883 | `reports/model_distilbert.md` |

### Chapter 6 Table 6.5: Correct DistilBERT Per-Class Results

| Class | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Access | 0.9076 | 0.9369 | 0.9220 | 713 |
| Administrative rights | 0.8471 | 0.8182 | 0.8324 | 176 |
| HR Support | 0.9033 | 0.8909 | 0.8971 | 1,091 |
| Hardware | 0.8776 | 0.8847 | 0.8812 | 1,362 |
| Internal Project | 0.8846 | 0.8679 | 0.8762 | 212 |
| Miscellaneous | 0.8362 | 0.8385 | 0.8373 | 706 |
| Purchase | 0.9540 | 0.9231 | 0.9383 | 247 |
| Storage | 0.9270 | 0.9170 | 0.9220 | 277 |

All four original per-class names, values, and supports are incorrect.

### Chapter 6 Table 6.6: NER Results

| Original Entity Metric Claim | Correct Value | Evidence |
| --- | --- | --- |
| DEVICE F1 0.86 | UNVERIFIED - REQUIRES RE-EXECUTION | No labeled NER evaluation |
| SOFTWARE F1 0.90 | UNVERIFIED - REQUIRES RE-EXECUTION | No labeled NER evaluation |
| ERROR_CODE F1 0.93 | UNVERIFIED - REQUIRES RE-EXECUTION | No labeled NER evaluation |

The implemented NER tests verify deterministic extraction behavior, not
precision/recall/F1 against labeled ground truth.

### API and System Performance Claims

| Claim | Audit Result | Evidence |
| --- | --- | --- |
| 50-ticket sample accuracy of 92% | UNVERIFIED - REQUIRES RE-EXECUTION | No result artifact |
| Average API latency of 127ms | UNVERIFIED - REQUIRES RE-EXECUTION | No benchmark artifact |
| Sub-200ms response latency | UNVERIFIED - REQUIRES RE-EXECUTION | No benchmark artifact |
| 200 held-out tickets replayed with zero errors | UNVERIFIED - REQUIRES RE-EXECUTION | No result artifact |
| All experiments repeated three times | UNVERIFIED - REQUIRES RE-EXECUTION | No multi-run artifacts |
| Automated test suite | Correct, but report details wrong | `python -m pytest -q`: 58 passed in 23.94s on 2026-06-28 |

## Audit Verification

- Word report inspected: 404 paragraphs, 11 tables, 2 sections, 0 inline figures.
- Source dataset directly inspected: 47,837 rows, 2 columns, 8 labels, no
  missing values, no duplicate rows.
- Saved baseline and DistilBERT artifacts directly inspected.
- FastAPI routes directly enumerated from the application.
- Full current test suite executed successfully:

```text
58 passed in 23.94s
```

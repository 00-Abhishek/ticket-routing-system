# NTCC Report Rewrite Package

This package contains paste-ready replacements for incorrect or missing report
content. Repository artifacts are the source of truth. Do not retain conflicting
four-class, Flask, LSTM, Word2Vec, trained-NER, fabricated metric, or latency
claims.

## Global Terminology Replacements

Replace throughout the report:

| Remove/Replace | Use Instead |
| --- | --- |
| Four ticket categories | Eight ticket categories |
| Network Issues, OS Issues, Application Bugs, Security Incidents | Access, Administrative rights, HR Support, Hardware, Internal Project, Miscellaneous, Purchase, Storage |
| Flask / Flask-RESTful | FastAPI with Uvicorn |
| Three REST endpoints | Nine project endpoints |
| Trained spaCy NER model | Configurable rule-based spaCy EntityRuler |
| Three NER entity types | Five entity types: SOFTWARE, DEVICE, ERROR_CODE, SYSTEM, LOCATION |
| 70/15/15 split | Stratified 80/10/10 split |
| Bidirectional LSTM and Word2Vec as implemented models | Not implemented; discussed only as future/related work |
| NER-augmented routing decision | Category-to-team routing with entities returned and persisted as metadata |
| Production-ready deployment proven | Docker Compose deployment validated locally on 2026-06-28 |

Remove every unsupported value for LSTM performance, NER precision/recall/F1,
API latency, 50-ticket manual accuracy, 200-ticket replay results, repeated-run
means, training duration, and vocabulary size. Replace each with:

> UNVERIFIED - REQUIRES RE-EXECUTION

## ABSTRACT

### Replacement Text

This project presents an automated IT support ticket classification and routing
system implemented as a modular NLP application. The system processes
unstructured ticket text, predicts one of eight operational categories, extracts
configured IT entities, assigns a rule-based priority, maps the predicted
category to a support team, persists the analysis, and exposes the workflow
through a FastAPI backend and Streamlit dashboard.

The source dataset is `data/all_tickets_processed_improved_v3.csv` and contains
47,837 records with the columns `Document` and `Topic_group`. The eight target
classes are Access, Administrative rights, HR Support, Hardware, Internal
Project, Miscellaneous, Purchase, and Storage. A seeded stratified split of 80%
training, 10% validation, and 10% test data was used consistently for the
implemented classifiers.

Three classifiers have verified training artifacts and test metrics. TF-IDF
with Multinomial Naive Bayes achieved 0.7795 accuracy and 0.7336 macro F1.
TF-IDF with Logistic Regression achieved 0.8616 accuracy and 0.8622 macro F1.
Fine-tuned DistilBERT base uncased achieved the strongest result, with 0.8878
test accuracy and 0.8883 macro F1, and is used as the production classifier.
No LSTM model was implemented or evaluated.

Entity extraction uses a configurable spaCy `EntityRuler` rather than a trained
NER model. It supports SOFTWARE, DEVICE, ERROR_CODE, SYSTEM, and LOCATION
entities. Category routing is deterministic and configurable, while a separate
keyword-based priority engine assigns Critical, High, Medium, or Low priority.
Successful full analyses are persisted to SQLite through SQLAlchemy. The
FastAPI backend exposes prediction, entity extraction, priority, routing,
history, analytics, health, and full-analysis endpoints. A Streamlit dashboard
provides ticket analysis, API health monitoring, model comparison, and
visualisations. Dockerfile and Docker Compose configuration support backend and
dashboard containerisation.

**Keywords:** Natural Language Processing, IT Support Ticket Classification,
DistilBERT, TF-IDF, Logistic Regression, Multinomial Naive Bayes, spaCy
EntityRuler, FastAPI, Streamlit, SQLite, SQLAlchemy, Docker.

## CHAPTER 1: INTRODUCTION

### 1.3 Problem Statement - Replacement Text

Given an unstructured IT support ticket, the implemented system predicts one of
eight operational categories: Access, Administrative rights, HR Support,
Hardware, Internal Project, Miscellaneous, Purchase, or Storage. It then
extracts configured technical entities, assigns a rule-based priority, routes
the predicted category to a configured support team, persists the complete
analysis, and returns structured results through an API and dashboard.

The project also compares two traditional TF-IDF baselines with a fine-tuned
DistilBERT classifier. The repository does not contain an implemented LSTM
model, and routing does not currently use extracted entities to change the
assigned team.

### 1.4 Objectives - Replacement Text

The verified project objectives are:

1. Explore and profile the 47,837-ticket dataset and generate reproducible EDA
   artifacts.
2. Train and evaluate TF-IDF Logistic Regression and Multinomial Naive Bayes
   baselines.
3. Fine-tune and evaluate DistilBERT base uncased as the production
   classifier.
4. Implement configurable rule-based entity extraction using spaCy.
5. Implement deterministic category-to-team routing and keyword-based priority
   assignment.
6. Expose the system through a documented FastAPI backend.
7. Persist completed analyses using SQLite and SQLAlchemy.
8. Provide a Streamlit dashboard for analysis and visualisation.
9. Provide Dockerfile and Docker Compose deployment configuration.
10. Validate the system with unit and integration tests.

### 1.5 Scope of the Project - Replacement Text

The implemented scope includes single-label classification across eight ticket
categories, configurable rule-based entity extraction, category-based routing,
rule-based priority assignment, API access, SQLite persistence, dashboard
visualisation, Docker configuration, and automated tests. The system does not
include an LSTM classifier, Word2Vec embeddings, trained statistical NER,
multi-label classification, multilingual support, automatic resolution
recommendation, entity-dependent routing, active learning, or direct
integration with external ITSM platforms.

## CHAPTER 2: LITERATURE REVIEW

### 2.7 Research Gap and Project Motivation - Replacement Text

The implemented project evaluates three verified classification approaches:
TF-IDF with Logistic Regression, TF-IDF with Multinomial Naive Bayes, and
fine-tuned DistilBERT. It integrates the selected DistilBERT classifier with
configurable rule-based entity extraction, deterministic category routing,
keyword-based priority assignment, persistence, an API, and a dashboard. LSTM
and trained NER remain relevant literature topics but are not implemented
experimental components of this repository.

## CHAPTER 3: SYSTEM DESIGN

### 3.1 Overall System Architecture - Replacement Text

The system uses a modular architecture centred on a FastAPI service layer. At
startup, `TicketAnalysisService` loads the trained DistilBERT model and
tokenizer, label mapping, spaCy rule-based entity extractor, priority engine,
routing engine, and prediction repository. A full analysis request performs
classification, entity extraction, priority assignment, category routing, and
SQLite persistence before returning a structured response. A Streamlit
dashboard communicates with the FastAPI backend through HTTP.

```text
Streamlit Dashboard or API Client
              |
              v
        FastAPI Backend
              |
              v
     TicketAnalysisService
       |      |      |      |
       v      v      v      v
 DistilBERT  NER  Priority  Router
              |
              v
     SQLAlchemy Repository
              |
              v
            SQLite
```

### 3.2 Data Flow Design - Replacement Text

For `POST /analyze`, ticket text is validated by a Pydantic request schema. The
saved DistilBERT tokenizer encodes the text with truncation and a maximum length
of 128 tokens. The classifier returns a category and confidence score. In
parallel within the service workflow, the spaCy `EntityRuler` extracts
configured entities and the priority engine evaluates keyword rules from
Critical to Low. The routing engine maps the predicted category to a configured
support team. The completed analysis is persisted to SQLite and returned as
JSON containing category, confidence, entities, priority, matched rule, and
assigned team.

### 3.3 Module Design - Replacement Text

The preprocessing module in `src/preprocessing/text.py` performs Unicode NFKC
normalisation, lowercasing, URL removal, email removal, control-character
normalisation, technical-token-friendly character filtering, and whitespace
normalisation. It does not perform lemmatisation, stop-word removal, IP
placeholder replacement, or error-code placeholder replacement.

The classification package contains reusable baseline and DistilBERT training
utilities. Saved baseline artifacts include a shared TF-IDF vectorizer,
Logistic Regression model, and Multinomial Naive Bayes model. The production
API loads the saved DistilBERT model.

The NER module uses `spacy.blank("en")` and a configurable `EntityRuler`.
Patterns are loaded from `config/entity_patterns.json`. Supported labels are
SOFTWARE, DEVICE, ERROR_CODE, SYSTEM, and LOCATION.

The routing module maps each supported category to one support team and raises
a descriptive error for unknown categories. The priority module independently
assigns Critical, High, Medium, or Low based on configurable keyword rules.

### Table 3.1: REST API Endpoint Specification - Replacement Table

| Method | Endpoint | Description | Main Response Fields |
| --- | --- | --- | --- |
| GET | `/health` | Return API health status | `status` |
| GET | `/metrics` | Return model and rule metadata | `model_name`, `number_of_classes`, `available_entities`, `supported_priorities` |
| GET | `/history` | Return recent persisted predictions | `predictions` |
| GET | `/analytics` | Return persistence analytics | `total_predictions`, `category_distribution`, `priority_distribution` |
| POST | `/predict` | Classify ticket text | `category`, `confidence` |
| POST | `/entities` | Extract configured entities | `entities` |
| POST | `/priority` | Assign rule-based priority | `priority`, `matched_rule` |
| POST | `/route` | Route a category to a team | `category`, `assigned_team` |
| POST | `/analyze` | Run and persist the complete workflow | `category`, `confidence`, `entities`, `priority`, `matched_rule`, `assigned_team` |

### Table 3.2: Technology Stack Summary - Replacement Table

| Category | Actual Technology | Purpose |
| --- | --- | --- |
| Language/runtime | Python; Docker image uses Python 3.11 | Application and container runtime |
| Baseline ML | scikit-learn | TF-IDF, Logistic Regression, Multinomial Naive Bayes, metrics |
| Transformer | PyTorch and Hugging Face Transformers | DistilBERT training and inference |
| NLP entity extraction | spaCy `EntityRuler` | Configurable rule-based entity extraction |
| API | FastAPI, Pydantic, Uvicorn | Backend and OpenAPI documentation |
| Persistence | SQLite and SQLAlchemy | Prediction history and analytics |
| Dashboard | Streamlit and Plotly | Interactive analysis and charts |
| Data/EDA | Pandas, NumPy, Matplotlib, Seaborn | Dataset processing and EDA |
| Deployment | Docker and Docker Compose | Backend/dashboard container configuration |
| Testing | pytest and FastAPI TestClient | Unit and integration testing |

## CHAPTER 4: METHODOLOGY

### 4.1 Dataset Description - Replacement Text

The project uses `data/all_tickets_processed_improved_v3.csv`. It contains
47,837 rows and two columns: `Document`, containing ticket text, and
`Topic_group`, containing the target class. Direct EDA found no missing
documents, no missing labels, and no duplicate rows. The dataset contains eight
classes and is imbalanced, with an largest-to-smallest class ratio of 7.7369.
The origin and expert-annotation process of the dataset are not proven by
repository artifacts and should not be stated without an external source.

### Table 4.1: IT Ticket Dataset Categories - Replacement Table

| Category | Tickets | Percentage | Routed Team |
| --- | ---: | ---: | --- |
| Hardware | 13,617 | 28.47% | Hardware Team |
| HR Support | 10,915 | 22.82% | HR Team |
| Access | 7,125 | 14.89% | Access Management Team |
| Miscellaneous | 7,060 | 14.76% | Service Desk Team |
| Storage | 2,777 | 5.81% | Storage Team |
| Purchase | 2,464 | 5.15% | Procurement Team |
| Internal Project | 2,119 | 4.43% | Internal Projects Team |
| Administrative rights | 1,760 | 3.68% | System Administration Team |

### 4.2 Text Preprocessing Pipeline - Replacement Text

The reusable preprocessing function applies Unicode NFKC normalisation,
lowercasing, URL removal, email removal, control-character normalisation,
technical-token-friendly filtering, and whitespace normalisation. Characters
useful in technical text, including periods, underscores, colons, slashes,
backslashes, and hyphens, are preserved where possible. The implemented
pipeline does not use NLTK stop-word removal, spaCy lemmatisation,
`en_core_web_sm`, IP placeholders, email placeholders, or error-code
placeholders.

### 4.3 Feature Extraction - Replacement Text

The baseline classifiers share a scikit-learn `TfidfVectorizer` configured with
unigrams and bigrams, a maximum of 50,000 features, `min_df=2`,
`max_df=0.95`, and sublinear term frequency. Word2Vec embeddings are not
implemented. DistilBERT uses its saved WordPiece tokenizer with truncation and
maximum sequence length 128.

### 4.4 Classification Models - Replacement Text

Three classifiers have verified implementations and metrics. Logistic
Regression uses `C=2.0`, balanced class weights, a maximum of 1,000 iterations,
and random seed 42. Multinomial Naive Bayes uses `alpha=0.5`. DistilBERT base
uncased is fine-tuned for eight labels using the Hugging Face Trainer, a batch
size of 16, learning rate `2e-5`, weight decay `0.01`, 10% warmup, mixed
precision when CUDA is available, checkpointing, and validation macro-F1 model
selection. The recorded run completed 3 epochs. No Bidirectional LSTM model was
implemented.

### 4.5 Named Entity Recognition - Replacement Text

The entity extraction module is rule-based because the repository contains no
labeled NER training dataset. It creates a blank English spaCy pipeline and
adds an `EntityRuler` configured with case-insensitive phrase matching and
patterns loaded from `config/entity_patterns.json`. It supports SOFTWARE,
DEVICE, SYSTEM, LOCATION, and ERROR_CODE. Strict regex patterns are used for
error-code-like tokens. No NER precision, recall, or F1 can be reported without
creating and evaluating a labeled entity dataset.

### 4.6 Evaluation Metrics - Replacement Text

Implemented classifiers are evaluated on a held-out stratified test set using
accuracy, macro precision, macro recall, macro F1, weighted precision, weighted
recall, weighted F1, per-class metrics, and confusion matrices. The split uses
random seed 42 and contains 80% training, 10% validation, and 10% test data.
Repository artifacts prove one recorded run for each generated model report;
repeated-run means and variance are not available.

## CHAPTER 5: IMPLEMENTATION

### 5.1 Development Environment - Replacement Text

The application is implemented in Python. Deployment configuration uses the
`python:3.11-slim` Docker base image. The recorded DistilBERT training report
identifies an NVIDIA GeForce RTX 4060 Ti and mixed-precision training. Exact
host operating system, CPU, RAM, IDE, and training duration are unverified.
Dependencies are declared with minimum version constraints in
`requirements.txt`; they include Pandas, NumPy, Matplotlib, Seaborn,
scikit-learn, PyTorch, Transformers, spaCy, FastAPI, Uvicorn, Streamlit,
Plotly, SQLAlchemy, PyYAML, and pytest.

### 5.2 Data Collection and Exploratory Analysis - Replacement Text

EDA was executed against the 47,837-row source CSV and generated a dataset
profile, class distribution CSV and chart, ticket-length charts, text-quality
signals, samples by class, and a preprocessed preview. Proven findings include
an average cleaned word count of 43.60, a median of 26 words, eight classes, no
missing values or duplicates, and a class imbalance ratio of 7.7369. Dataset
origin claims require an external citation and are otherwise unverified.

### 5.3 Preprocessing Pipeline Implementation - Replacement Text

`src/preprocessing/text.py` contains `clean_ticket_text` and
`normalize_ticket_series`. Compiled regular expressions remove URLs, emails,
and control characters while preserving useful technical-token characters.
The module is used by EDA and baseline training. It does not load spaCy or NLTK
and is not wrapped in a scikit-learn `FunctionTransformer`.

### 5.4 Baseline Model Implementation - Replacement Text

Baseline training loads and validates the source CSV, applies the shared
normalisation function, creates a seeded stratified 80/10/10 split, fits one
shared TF-IDF vectorizer on training text, trains Logistic Regression and
Multinomial Naive Bayes, evaluates validation and test splits, generates
aggregate/per-class/confusion-matrix results, and saves the models and
vectorizer with joblib. Five-fold cross-validation and hyperparameter search
are not implemented.

### 5.5 LSTM Model Implementation - Replacement Text

No LSTM or Word2Vec implementation exists in the repository. No LSTM artifact,
training log, or metric is available. LSTM results must not be reported.

### 5.6 DistilBERT Fine-tuning Implementation - Replacement Text

The DistilBERT training script uses `distilbert-base-uncased` with eight output
labels and the same seeded stratified 80/10/10 split used by the baselines.
Text is tokenized with `DistilBertTokenizerFast`, truncated to a maximum length
of 128, and wrapped in a custom PyTorch dataset. Hugging Face `Trainer` runs
with a batch size of 16, 3 epochs, learning rate `2e-5`, weight decay `0.01`,
warmup equal to 10% of training steps, mixed precision when CUDA is available,
epoch-based evaluation/checkpointing, and early stopping configured on macro
F1. The best saved checkpoint is `checkpoint-7176`. Weighted sampling is not
implemented.

### 5.7 NER Module Implementation - Replacement Text

The NER module uses a blank English spaCy pipeline and `EntityRuler`. At
startup, it loads phrase and token patterns from
`config/entity_patterns.json`. It returns typed matches with text, label,
character offsets, and pattern identifier. The API groups extracted matches by
label. There is no Prodigy annotation corpus, spaCy training configuration, or
trained NER model.

### 5.8 FastAPI REST API Implementation - Replacement Text

The backend is implemented with FastAPI, Pydantic, and Uvicorn. FastAPI
dependency injection returns a cached `TicketAnalysisService` singleton so the
DistilBERT model, tokenizer, label mapping, entity extractor, priority engine,
routing engine, and repository are not loaded per request. Pydantic schemas
validate requests and responses. OpenAPI/Swagger documentation is generated
automatically at `/docs`.

### 5.9 System Integration and Testing - Replacement Text

The pytest suite covers preprocessing, baseline utilities, DistilBERT metric
helpers, NER extraction, routing, priority assignment, API endpoints, database
persistence, dashboard utilities, Docker configuration, and integration
workflows. Integration tests use FastAPI TestClient and an in-memory SQLite
database to verify classification response structure, entity extraction,
priority, routing, persistence, history, and analytics. Claims about replaying
200 held-out tickets, a 50-ticket accuracy sample, and measured latency are
unverified and must not be included without a reproducible benchmark artifact.
The current full repository test run completed successfully with 58 passing
tests.

### New Section: 5.10 SQLite Persistence

The persistence layer uses SQLAlchemy with SQLite at
`data/ticket_routing.db`. The `ticket_predictions` table stores original ticket
text, predicted category, confidence, JSON-serialized entities, priority,
assigned team, and UTC creation timestamp. Successful `/analyze` requests are
saved automatically. Repository methods provide recent history, total
prediction count, category distribution, and priority distribution.

### New Section: 5.11 Streamlit Dashboard

The Streamlit dashboard calls the FastAPI backend through a configurable
`BACKEND_URL`. It provides API health monitoring, ticket input, classification
and confidence display, grouped entity display, priority and matched rule,
routing destination, a full-analysis panel, and an analytics tab. Plotly charts
display generated class-distribution and model-comparison data. Priority and
routing distribution charts currently use demo data.

### New Section: 5.12 Docker Deployment Configuration

The Dockerfile uses `python:3.11-slim`, installs requirements, copies project
source, creates data/model/report directories, and exposes ports 8000 and 8501.
Docker Compose defines a FastAPI backend and Streamlit dashboard, mounts
`data/`, `models/`, and `reports/`, supplies
`BACKEND_URL=http://backend:8000`, and waits for the backend healthcheck.
Docker Compose deployment was validated locally on 2026-06-28 using `docker compose build` and `docker compose up -d`, with healthy backend and dashboard services, successful endpoint checks, mounted model/report directories, and persisted SQLite writes.

## CHAPTER 6: RESULTS AND ANALYSIS

### 6.1 Experimental Setup - Replacement Text

All implemented classifiers use a seeded stratified 80/10/10
train/validation/test split: 38,269 training rows, 4,784 validation rows, and
4,784 test rows. Metrics in the generated reports are from the held-out test
set. Repeated-run means are not available. The recorded DistilBERT training run
used an NVIDIA GeForce RTX 4060 Ti with mixed precision enabled.

### Table 6.1: Dataset Statistics Summary - Replacement Table

| Statistic | Correct Value |
| --- | ---: |
| Total tickets | 47,837 |
| Training set | 38,269 (80%) |
| Validation set | 4,784 (10%) |
| Test set | 4,784 (10%) |
| Average cleaned word count | 43.60 |
| Median cleaned word count | 26 |
| Average raw character length | 291.88 |
| Number of target categories | 8 |
| Missing documents | 0 |
| Missing labels | 0 |
| Duplicate rows | 0 |
| Vocabulary size | UNVERIFIED - REQUIRES RE-EXECUTION |

### Table 6.2: Baseline Model Performance, Test Set - Replacement Table

| Model | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| TF-IDF + Logistic Regression | 0.8616 | 0.8507 | 0.8762 | 0.8622 | 0.8620 |
| TF-IDF + Multinomial Naive Bayes | 0.7795 | 0.8802 | 0.6814 | 0.7336 | 0.7732 |

### Table 6.3: LSTM Model Performance - Replacement Table

| Model | Result |
| --- | --- |
| Bidirectional LSTM | Not implemented; no artifact or metric exists. |

### Table 6.4: DistilBERT Performance, Test Set - Replacement Table

| Model | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| DistilBERT base uncased | 0.8878 | 0.8922 | 0.8847 | 0.8883 | 0.8877 |

### Table 6.5: DistilBERT Per-Class Classification Report - Replacement Table

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

### Table 6.6: NER Module Results - Replacement Table

| Entity Type | Evaluation Status |
| --- | --- |
| SOFTWARE | UNVERIFIED - REQUIRES A LABELED NER TEST SET |
| DEVICE | UNVERIFIED - REQUIRES A LABELED NER TEST SET |
| ERROR_CODE | UNVERIFIED - REQUIRES A LABELED NER TEST SET |
| SYSTEM | UNVERIFIED - REQUIRES A LABELED NER TEST SET |
| LOCATION | UNVERIFIED - REQUIRES A LABELED NER TEST SET |

### Table 6.7: Comprehensive Model Comparison - Replacement Table

| Model | Accuracy | Macro Precision | Macro Recall | Macro F1 |
| --- | ---: | ---: | ---: | ---: |
| TF-IDF + Multinomial Naive Bayes | 0.7795 | 0.8802 | 0.6814 | 0.7336 |
| TF-IDF + Logistic Regression | 0.8616 | 0.8507 | 0.8762 | 0.8622 |
| DistilBERT base uncased | 0.8878 | 0.8922 | 0.8847 | 0.8883 |

### 6.8 API Performance and Testing - Replacement Text

The API is covered by automated endpoint and integration tests. Verified
workflows include health checks, prediction, entity extraction, priority,
routing, full analysis, persistence, history, and analytics. No reproducible
latency benchmark or separate 50-ticket manual accuracy experiment exists in
the repository. Therefore latency and manual-sample accuracy claims must be
reported as **UNVERIFIED - REQUIRES RE-EXECUTION**.

### 6.9 Discussion - Replacement Text

DistilBERT achieved the strongest verified test performance, improving accuracy
from 0.8616 for Logistic Regression to 0.8878 and macro F1 from 0.8622 to
0.8883. Logistic Regression remains a strong and substantially smaller
baseline. Multinomial Naive Bayes achieved high macro precision but weaker
macro recall, especially for minority classes. The rule-based NER, priority,
and routing components provide deterministic operational metadata but must not
be described as statistically evaluated ML models. The current repository
demonstrates an integrated prototype with persistence, API, dashboard, and
container configuration; Docker runtime was validated locally, while production latency and scalability still require separate benchmarking.

## CHAPTER 7: CONCLUSION AND FUTURE SCOPE

### 7.1 Conclusion - Replacement Text

The project implements and validates an end-to-end NLP workflow for automated
IT support ticket classification and routing. It profiles a 47,837-ticket,
eight-class dataset; trains two TF-IDF baselines and a DistilBERT classifier;
extracts configurable IT entities; assigns rule-based priority; routes
categories to support teams; persists complete analyses; and exposes the system
through FastAPI and Streamlit. DistilBERT is the recommended classifier based
on verified test accuracy of 0.8878 and macro F1 of 0.8883. Logistic Regression
achieved 0.8616 accuracy and 0.8622 macro F1, while Multinomial Naive Bayes
achieved 0.7795 accuracy and 0.7336 macro F1. No LSTM model or trained NER
evaluation is present.

### 7.2 Key Contributions - Replacement Text

Verified contributions include:

1. Reproducible EDA and preprocessing for a 47,837-ticket dataset.
2. Saved and evaluated TF-IDF Logistic Regression and Multinomial Naive Bayes
   baselines.
3. A saved eight-class DistilBERT model with checkpoints and test metrics.
4. Configurable spaCy rule-based entity extraction for five entity types.
5. Deterministic category routing and rule-based priority assignment.
6. A documented FastAPI backend with nine project endpoints.
7. SQLite/SQLAlchemy persistence with history and analytics endpoints.
8. A Streamlit dashboard with analysis and visualisation workflows.
9. Dockerfile and Docker Compose deployment configuration.
10. Unit and integration tests covering the implemented modules.

### 7.3 Limitations - Replacement Text

The system uses single-label classification and does not support multilingual
text, active learning, automated resolution recommendation, or direct ITSM
integration. NER is rule-based and has no labeled evaluation set, so entity
precision, recall, and F1 are unknown. Priority is rule-based because the
dataset has no priority labels. Routing uses only the predicted category and
does not use entities or priority to select a team. Dashboard priority and
routing distribution charts use demo data. API latency, throughput, repeated
training stability are unverified. Docker runtime was validated locally. DistilBERT
inference requires the saved model directory and may require significant CPU
memory when no GPU is available.

### 7.4 Future Scope - Replacement Text

Future work should create a labeled NER evaluation set, collect human-confirmed
priority labels, add entity- and priority-aware routing, measure API latency and
throughput, execute repeated training runs, connect dashboard charts to persisted analytics, and integrate with ITSM platforms.
Additional research directions include multi-label and hierarchical
classification, multilingual models, active learning, explainability, and
resolution recommendation.

## Updated Figure Descriptions

Insert only figures backed by repository artifacts:

1. **Figure: Support Ticket Class Distribution.** Horizontal bar chart showing
   all eight dataset classes and their ticket counts. Source:
   `reports/eda/class_distribution.png`.
2. **Figure: Ticket Word Count Distribution.** Distribution of cleaned ticket
   word counts used to assess sequence length. Source:
   `reports/eda/ticket_word_count_distribution.png`.
3. **Figure: Cleaned Ticket Character Length Distribution.** Character-length
   distribution capped at the 99th percentile. Source:
   `reports/eda/ticket_clean_length_distribution.png`.
4. **Figure: Model Comparison Dashboard.** Streamlit analytics view comparing
   actual test accuracy, macro precision, macro recall, and macro F1 for the
   three verified models. Source: `docs/screenshots/analytics_page.png`.
5. **Figure: Full Ticket Analysis Workflow.** Streamlit result view showing
   prediction, confidence, and extracted entities. Source:
   `docs/screenshots/prediction_results.png`.
6. **Figure: FastAPI OpenAPI Documentation.** Swagger interface generated by
   FastAPI. Source: `docs/screenshots/fastapi_swagger_docs.png`.
7. **Figure: Persisted Prediction History.** API response from the history
   endpoint. Source: `docs/screenshots/database_history_endpoint.png`.

Do not include figures or captions for an LSTM architecture, trained NER
evaluation, Flask API, or unsupported latency benchmark.

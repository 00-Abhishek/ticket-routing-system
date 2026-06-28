# Streamlit Dashboard Design

## Scope

The dashboard is implemented with Streamlit and communicates with the FastAPI backend for operational analysis. It also reads generated Markdown and CSV reports for analytics visualizations.

## UI Architecture

```text
Streamlit Dashboard
    |
    +-- dashboard/app.py
    |       Main page, tabs, API health, ticket analysis workflow
    |
    +-- dashboard/components.py
    |       Reusable panels for prediction, entities, priority, routing, status
    |
    +-- dashboard/charts.py
    |       Plotly chart helpers
    |
    +-- dashboard/utils.py
            API calls, response parsing, report parsing
```

Backend URL behavior:

- Default local URL: `http://127.0.0.1:8000`
- Environment override: `BACKEND_URL`
- Docker Compose value: `http://backend:8000`

## Dashboard Workflow

1. User opens the Streamlit dashboard.
2. Dashboard checks `GET /health`.
3. User enters ticket text in `Enter IT Support Ticket`.
4. User clicks `Analyze Ticket`.
5. Dashboard calls:
   - `POST /analyze`
   - `POST /predict`
   - `POST /entities`
   - `POST /priority`
6. Dashboard renders:
   - Predicted category
   - Confidence score
   - Extracted entities
   - Assigned priority
   - Matched priority rule
   - Assigned support team
   - Full analysis summary

## Analytics Page

### Model Comparison

Reads the generated baseline and DistilBERT reports and shows test-set metrics for:

- Logistic Regression
- Naive Bayes
- DistilBERT

### Class Distribution

Reads `reports/eda/class_distribution.csv` and renders a Plotly horizontal bar chart.

### Priority Distribution

Currently uses sample/demo data.

### Routing Distribution

Currently uses sample/demo data.

These two charts are valid dashboard placeholders but have not yet been switched to live `/analytics` data.

## Error Handling

The dashboard handles:

- API unavailable
- Empty ticket input
- HTTP request failures
- Invalid JSON
- Invalid response shapes
- Missing local report files

## Run Commands

Start the API:

```bash
uvicorn src.api.app:app --reload
```

Start the dashboard:

```bash
streamlit run dashboard/app.py
```

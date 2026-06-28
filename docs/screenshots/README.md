# Phase 11 Screenshots

This folder contains the final validation screenshots captured from the running
FastAPI and Streamlit applications.

Captured screenshots:

| File | View |
| --- | --- |
| `dashboard_home.png` | Streamlit dashboard home and health status |
| `prediction_results.png` | Completed ticket analysis with prediction and entities |
| `analytics_page.png` | Dashboard analytics and model comparison |
| `fastapi_swagger_docs.png` | FastAPI OpenAPI/Swagger documentation |
| `database_history_endpoint.png` | Persisted prediction history endpoint |

Run the local services before recapturing screenshots:

```bash
uvicorn src.api.app:app --reload
streamlit run dashboard/app.py
```

Useful URLs:

- FastAPI docs: `http://127.0.0.1:8000/docs`
- Streamlit dashboard: `http://127.0.0.1:8501`
- History endpoint: `http://127.0.0.1:8000/history`
- Demo analysis view: `http://127.0.0.1:8501/?demo_ticket=Unable%20to%20login%20to%20Outlook%20on%20my%20laptop&auto_analyze=1`

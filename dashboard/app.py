"""Streamlit dashboard for automated IT support ticket analysis."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.charts import (
    create_class_distribution_chart,
    create_model_comparison_chart,
    create_priority_distribution_chart,
    create_routing_distribution_chart,
)
from dashboard.components import (
    render_entities_panel,
    render_prediction_panel,
    render_priority_panel,
    render_routing_panel,
    render_status,
)
from dashboard.utils import (
    DashboardAPIError,
    call_api,
    compact_error_message,
    get_default_api_url,
    load_class_distribution,
    load_model_comparison,
    parse_entities_response,
    parse_priority_response,
    parse_predict_response,
)

st.set_page_config(
    page_title="IT Ticket NLP Dashboard",
    page_icon="🎫",
    layout="wide",
)


def get_api_url() -> str:
    """Read API URL from sidebar."""
    return st.sidebar.text_input("FastAPI URL", value=get_default_api_url())


def api_health(api_url: str) -> bool:
    """Return whether the API health endpoint is reachable."""
    try:
        data = call_api("GET", "/health", api_url)
    except DashboardAPIError:
        return False
    return data.get("status") == "healthy"


def get_embedded_service():
    """Lazy load direct Python NLP service when FastAPI backend is not running."""
    try:
        from src.api.services import get_ticket_analysis_service
        return get_ticket_analysis_service()
    except Exception as exc:
        st.sidebar.warning(f"Embedded engine fallback unavailable: {exc}")
        return None


def render_analysis_page(api_url: str, is_api_online: bool) -> None:
    """Render ticket analysis workflow."""
    st.header("Ticket Analysis")
    demo_ticket = str(st.query_params.get("demo_ticket", ""))
    auto_analyze = str(st.query_params.get("auto_analyze", "")).lower() in {"1", "true", "yes"}

    ticket_text = st.text_area("Enter IT Support Ticket", value=demo_ticket, height=180)
    analyze_clicked = st.button("Analyze Ticket", type="primary")

    if analyze_clicked or (auto_analyze and ticket_text.strip()):
        if not ticket_text.strip():
            st.warning("Please enter a ticket before analyzing.")
            return

        if is_api_online:
            try:
                full_response = call_api("POST", "/analyze", api_url, {"ticket_text": ticket_text})
                predict_response = call_api("POST", "/predict", api_url, {"ticket_text": ticket_text})
                entities_response = call_api("POST", "/entities", api_url, {"ticket_text": ticket_text})
                priority_response = call_api("POST", "/priority", api_url, {"ticket_text": ticket_text})
            except DashboardAPIError as exc:
                st.error(compact_error_message(str(exc)))
                return

            category, confidence = parse_predict_response(predict_response)
            entities = parse_entities_response(entities_response)
            priority, matched_rule = parse_priority_response(priority_response)
            full_priority, full_matched_rule = parse_priority_response(full_response)
            assigned_team = str(full_response.get("assigned_team", "Unknown"))
        else:
            service = get_embedded_service()
            if service is None:
                st.error("FastAPI backend is offline and embedded engine could not be initialized.")
                return
            with st.spinner("Analyzing ticket..."):
                analysis = service.analyze(ticket_text)
                category = analysis["category"]
                confidence = float(analysis["confidence"])
                entities = analysis["entities"]
                priority = analysis["priority"]
                matched_rule = analysis["matched_rule"]
                assigned_team = analysis["assigned_team"]

        st.subheader("Prediction")
        render_prediction_panel(category, confidence)

        st.subheader("Entity Extraction")
        render_entities_panel(entities)

        st.subheader("Priority")
        render_priority_panel(priority, matched_rule)

        st.subheader("Routing")
        render_routing_panel(assigned_team)


def render_analytics_page() -> None:
    """Render report-driven analytics."""
    st.header("Analytics")
    model_metrics = load_model_comparison()
    class_distribution = load_class_distribution()

    st.subheader("Model Comparison")
    if model_metrics.empty:
        st.info("Model comparison report is not available yet.")
    else:
        st.dataframe(model_metrics, use_container_width=True, hide_index=True)
        st.plotly_chart(create_model_comparison_chart(model_metrics), use_container_width=True)

    st.subheader("Class Distribution")
    if class_distribution.empty:
        st.info("Class distribution report is not available yet.")
    else:
        st.plotly_chart(create_class_distribution_chart(class_distribution), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Priority Distribution")
        st.plotly_chart(create_priority_distribution_chart(), use_container_width=True)
    with col2:
        st.subheader("Routing Distribution")
        st.plotly_chart(create_routing_distribution_chart(), use_container_width=True)


def main() -> None:
    """Run dashboard."""
    st.title("Automated IT Support Ticket NLP")
    api_url = get_api_url()
    st.sidebar.subheader("System Status")
    is_api_online = api_health(api_url)
    if is_api_online:
        render_status(True)
        st.sidebar.caption("Connected to FastAPI backend")
    else:
        st.sidebar.success("🟢 Online (In-App Engine)")
        st.sidebar.caption("Running direct Python NLP engine")

    tab_analysis, tab_analytics = st.tabs(["Analyze Ticket", "Analytics"])
    with tab_analysis:
        render_analysis_page(api_url, is_api_online)
    with tab_analytics:
        render_analytics_page()


if __name__ == "__main__":
    main()


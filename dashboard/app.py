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


def render_analysis_page(api_url: str) -> None:
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

        st.subheader("Prediction")
        render_prediction_panel(category, confidence)

        st.subheader("Entity Extraction")
        render_entities_panel(entities)

        st.subheader("Priority")
        render_priority_panel(priority, matched_rule)

        st.subheader("Routing")
        render_routing_panel(str(full_response.get("assigned_team", "Unknown")))

        st.subheader("Full Analysis")
        render_prediction_panel(
            str(full_response.get("category", "Unknown")),
            float(full_response.get("confidence", 0.0)),
        )
        render_entities_panel(parse_entities_response({"entities": full_response.get("entities", {})}))
        render_priority_panel(full_priority, full_matched_rule)
        render_routing_panel(str(full_response.get("assigned_team", "Unknown")))


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
    render_status(api_health(api_url))

    tab_analysis, tab_analytics = st.tabs(["Analyze Ticket", "Analytics"])
    with tab_analysis:
        render_analysis_page(api_url)
    with tab_analytics:
        render_analytics_page()


if __name__ == "__main__":
    main()

"""Reusable Streamlit UI components."""

from __future__ import annotations

import streamlit as st

from dashboard.utils import confidence_to_percent

ENTITY_ORDER = ["SOFTWARE", "DEVICE", "SYSTEM", "LOCATION", "ERROR_CODE"]


def render_status(is_healthy: bool) -> None:
    """Render API health status."""
    if is_healthy:
        st.success("🟢 Healthy")
    else:
        st.error("🔴 Offline")


def render_prediction_panel(category: str, confidence: float) -> None:
    """Render predicted category and confidence."""
    col1, col2 = st.columns(2)
    col1.metric("Predicted Category", category)
    col2.metric("Confidence Score", confidence_to_percent(confidence))


def render_entities_panel(entities: dict[str, list[str]]) -> None:
    """Render extracted entities grouped by label."""
    for label in ENTITY_ORDER:
        values = entities.get(label, [])
        display = ", ".join(values) if values else "None"
        st.write(f"**{label}**: {display}")


def render_priority_panel(priority: str, matched_rule: str | None) -> None:
    """Render priority result."""
    col1, col2 = st.columns(2)
    col1.metric("Assigned Priority", priority)
    col2.metric("Matched Rule", matched_rule or "Default")


def render_routing_panel(assigned_team: str) -> None:
    """Render assigned support team."""
    st.metric("Assigned Support Team", assigned_team)


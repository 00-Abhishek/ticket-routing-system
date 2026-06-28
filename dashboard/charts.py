"""Plotly chart helpers for the Streamlit dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_class_distribution_chart(distribution: pd.DataFrame) -> go.Figure:
    """Create class distribution bar chart."""
    if distribution.empty:
        return go.Figure()
    chart_data = distribution.sort_values("ticket_count", ascending=True)
    fig = px.bar(
        chart_data,
        x="ticket_count",
        y="Topic_group",
        orientation="h",
        labels={"ticket_count": "Tickets", "Topic_group": "Category"},
        color="percentage",
        color_continuous_scale="Blues",
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10), coloraxis_showscale=False)
    return fig


def create_model_comparison_chart(metrics: pd.DataFrame) -> go.Figure:
    """Create grouped model comparison chart."""
    if metrics.empty:
        return go.Figure()
    chart_data = metrics.melt(id_vars="Model", value_vars=["Accuracy", "Precision", "Recall", "F1"])
    fig = px.bar(
        chart_data,
        x="Model",
        y="value",
        color="variable",
        barmode="group",
        labels={"value": "Score", "variable": "Metric"},
        range_y=[0, 1],
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10), legend_title_text="")
    return fig


def create_priority_distribution_chart() -> go.Figure:
    """Create sample/demo priority distribution chart."""
    data = pd.DataFrame(
        {
            "Priority": ["Critical", "High", "Medium", "Low"],
            "Tickets": [8, 24, 52, 16],
        }
    )
    fig = px.pie(data, names="Priority", values="Tickets", hole=0.45)
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
    return fig


def create_routing_distribution_chart() -> go.Figure:
    """Create sample/demo routing distribution chart."""
    data = pd.DataFrame(
        {
            "Team": [
                "Hardware Team",
                "HR Team",
                "Access Management Team",
                "Storage Team",
                "Procurement Team",
                "System Administration Team",
                "Internal Projects Team",
                "Service Desk Team",
            ],
            "Tickets": [31, 18, 22, 9, 7, 11, 5, 14],
        }
    )
    fig = px.bar(data.sort_values("Tickets"), x="Tickets", y="Team", orientation="h")
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10))
    return fig


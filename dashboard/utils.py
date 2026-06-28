"""Utility functions for the Streamlit dashboard."""

from __future__ import annotations

import re
import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_API_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 10


class DashboardAPIError(RuntimeError):
    """Raised when the dashboard cannot communicate with the API."""


def normalize_api_url(api_url: str) -> str:
    """Normalize an API base URL by trimming whitespace and trailing slash."""
    normalized = api_url.strip().rstrip("/")
    if not normalized:
        raise ValueError("API URL cannot be empty.")
    return normalized


def get_default_api_url() -> str:
    """Return backend API URL from environment, falling back to localhost."""
    return normalize_api_url(os.getenv("BACKEND_URL", DEFAULT_API_URL))


def call_api(
    method: str,
    endpoint: str,
    api_url: str = DEFAULT_API_URL,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call a FastAPI endpoint and return JSON data."""
    base_url = normalize_api_url(api_url)
    url = f"{base_url}{endpoint}"
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise DashboardAPIError(f"API request failed for {endpoint}: {exc}") from exc
    except ValueError as exc:
        raise DashboardAPIError(f"API returned invalid JSON for {endpoint}.") from exc

    if not isinstance(data, dict):
        raise DashboardAPIError(f"API returned an invalid response shape for {endpoint}.")
    return data


def parse_predict_response(data: dict[str, Any]) -> tuple[str, float]:
    """Parse a /predict response into category and confidence."""
    category = data.get("category")
    confidence = data.get("confidence")
    if not isinstance(category, str) or not isinstance(confidence, int | float):
        raise ValueError("Invalid predict response.")
    return category, float(confidence)


def parse_entities_response(data: dict[str, Any]) -> dict[str, list[str]]:
    """Parse and normalize a /entities response."""
    entities = data.get("entities")
    if not isinstance(entities, dict):
        raise ValueError("Invalid entities response.")

    normalized: dict[str, list[str]] = {}
    for label, values in entities.items():
        if isinstance(label, str) and isinstance(values, list):
            normalized[label] = [str(value) for value in values]
    return normalized


def parse_priority_response(data: dict[str, Any]) -> tuple[str, str | None]:
    """Parse a priority response while preserving its matched rule."""
    priority = data.get("priority")
    matched_rule = data.get("matched_rule")
    if not isinstance(priority, str) or (
        matched_rule is not None and not isinstance(matched_rule, str)
    ):
        raise ValueError("Invalid priority response.")
    return priority, matched_rule


def parse_markdown_table(markdown_text: str, heading: str | None = None) -> pd.DataFrame:
    """Extract the first markdown table after a heading, or the first table overall."""
    lines = markdown_text.splitlines()
    start_index = 0
    if heading is not None:
        for index, line in enumerate(lines):
            if line.strip() == heading:
                start_index = index + 1
                break

    table_lines: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines.append(stripped)
        elif table_lines:
            break

    if len(table_lines) < 2:
        return pd.DataFrame()

    headers = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows = []
    for line in table_lines[2:]:
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return pd.DataFrame(rows, columns=headers)


def load_model_comparison(report_path: Path | None = None) -> pd.DataFrame:
    """Load model comparison metrics from existing reports."""
    baseline_path = report_path or PROJECT_ROOT / "reports" / "model_baselines.md"
    distilbert_path = PROJECT_ROOT / "reports" / "model_distilbert.md"
    rows: list[dict[str, Any]] = []

    if baseline_path.exists():
        baseline_text = baseline_path.read_text(encoding="utf-8")
        baseline_table = parse_markdown_table(baseline_text, "## Aggregate Metrics")
        for _, row in baseline_table.iterrows():
            if row.get("Split") == "Test":
                rows.append(
                    {
                        "Model": row["Model"].replace("TF-IDF + ", ""),
                        "Accuracy": float(row["Accuracy"]),
                        "Precision": float(row["Precision Macro"]),
                        "Recall": float(row["Recall Macro"]),
                        "F1": float(row["F1 Macro"]),
                    }
                )

    if distilbert_path.exists():
        distilbert_text = distilbert_path.read_text(encoding="utf-8")
        aggregate_table = parse_markdown_table(distilbert_text, "## Aggregate Metrics")
        test_rows = aggregate_table[aggregate_table["Split"] == "Test"] if not aggregate_table.empty else pd.DataFrame()
        if not test_rows.empty:
            row = test_rows.iloc[0]
            rows.append(
                {
                    "Model": "DistilBERT",
                    "Accuracy": float(row["Accuracy"]),
                    "Precision": float(row["Precision Macro"]),
                    "Recall": float(row["Recall Macro"]),
                    "F1": float(row["F1 Macro"]),
                }
            )
    return pd.DataFrame(rows)


def load_class_distribution(path: Path | None = None) -> pd.DataFrame:
    """Load class distribution generated during Phase 1."""
    distribution_path = path or PROJECT_ROOT / "reports" / "eda" / "class_distribution.csv"
    if not distribution_path.exists():
        return pd.DataFrame(columns=["Topic_group", "ticket_count", "percentage"])
    return pd.read_csv(distribution_path)


def confidence_to_percent(confidence: float) -> str:
    """Format confidence as a percentage string."""
    return f"{confidence * 100:.1f}%"


def compact_error_message(message: str) -> str:
    """Make backend/client errors readable in the dashboard."""
    return re.sub(r"\s+", " ", message).strip()

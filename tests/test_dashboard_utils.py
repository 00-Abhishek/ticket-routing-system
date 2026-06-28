import pandas as pd
import pytest
from plotly.graph_objects import Figure

from dashboard.charts import (
    create_class_distribution_chart,
    create_model_comparison_chart,
    create_priority_distribution_chart,
    create_routing_distribution_chart,
)
from dashboard.utils import (
    confidence_to_percent,
    get_default_api_url,
    normalize_api_url,
    parse_entities_response,
    parse_markdown_table,
    parse_priority_response,
    parse_predict_response,
)


def test_parse_predict_response() -> None:
    category, confidence = parse_predict_response({"category": "Hardware", "confidence": 0.91})

    assert category == "Hardware"
    assert confidence == 0.91


def test_parse_predict_response_rejects_invalid_shape() -> None:
    with pytest.raises(ValueError, match="predict"):
        parse_predict_response({"category": "Hardware"})


def test_parse_entities_response() -> None:
    entities = parse_entities_response({"entities": {"SOFTWARE": ["Outlook"], "DEVICE": ["laptop"]}})

    assert entities == {"SOFTWARE": ["Outlook"], "DEVICE": ["laptop"]}


def test_parse_priority_response_preserves_matched_rule() -> None:
    priority, matched_rule = parse_priority_response(
        {"priority": "High", "matched_rule": "cannot login"}
    )

    assert priority == "High"
    assert matched_rule == "cannot login"


def test_parse_markdown_table_after_heading() -> None:
    markdown = """
## Other

| A | B |
| --- | --- |
| x | y |

## Aggregate Metrics

| Model | Accuracy |
| --- | --- |
| DistilBERT | 0.8878 |
"""

    table = parse_markdown_table(markdown, "## Aggregate Metrics")

    assert table.to_dict("records") == [{"Model": "DistilBERT", "Accuracy": "0.8878"}]


def test_normalize_api_url_and_confidence_formatting() -> None:
    assert normalize_api_url(" http://127.0.0.1:8000/ ") == "http://127.0.0.1:8000"
    assert confidence_to_percent(0.8878) == "88.8%"


def test_default_api_url_uses_backend_url_environment(monkeypatch) -> None:
    monkeypatch.setenv("BACKEND_URL", "http://backend:8000/")

    assert get_default_api_url() == "http://backend:8000"


def test_chart_generation_helpers_return_figures() -> None:
    distribution = pd.DataFrame(
        {
            "Topic_group": ["Hardware", "Access"],
            "ticket_count": [100, 50],
            "percentage": [66.7, 33.3],
        }
    )
    metrics = pd.DataFrame(
        {
            "Model": ["Logistic Regression", "Naive Bayes", "DistilBERT"],
            "Accuracy": [0.86, 0.78, 0.89],
            "Precision": [0.85, 0.88, 0.89],
            "Recall": [0.87, 0.68, 0.88],
            "F1": [0.86, 0.73, 0.89],
        }
    )

    assert isinstance(create_class_distribution_chart(distribution), Figure)
    assert isinstance(create_model_comparison_chart(metrics), Figure)
    assert isinstance(create_priority_distribution_chart(), Figure)
    assert isinstance(create_routing_distribution_chart(), Figure)

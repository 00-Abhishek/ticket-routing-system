"""Pydantic request and response schemas for the API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PredictRequest(BaseModel):
    """Request containing support ticket text."""

    ticket_text: str = Field(..., min_length=1)


class RouteRequest(BaseModel):
    """Request containing a predicted ticket category."""

    category: str = Field(..., min_length=1)


class PredictResponse(BaseModel):
    """Classification response."""

    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class EntitiesResponse(BaseModel):
    """Named entity extraction response grouped by label."""

    entities: dict[str, list[str]]


class PriorityResponse(BaseModel):
    """Priority assignment response."""

    priority: str
    matched_rule: str | None


class RouteResponse(BaseModel):
    """Routing decision response."""

    category: str
    assigned_team: str


class FullPipelineResponse(BaseModel):
    """End-to-end ticket analysis response."""

    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    entities: dict[str, list[str]]
    priority: str
    matched_rule: str | None
    assigned_team: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


class MetricsResponse(BaseModel):
    """Runtime model/service metadata response."""

    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    number_of_classes: int
    available_entities: list[str]
    supported_priorities: list[str]


class PredictionHistoryItem(BaseModel):
    """Persisted prediction history item."""

    id: int
    ticket_text: str
    predicted_category: str
    confidence_score: float
    entities_json: str
    priority: str
    assigned_team: str
    created_at: str


class HistoryResponse(BaseModel):
    """Recent prediction history response."""

    predictions: list[PredictionHistoryItem]


class AnalyticsResponse(BaseModel):
    """Prediction analytics response."""

    total_predictions: int
    category_distribution: dict[str, int]
    priority_distribution: dict[str, int]

"""FastAPI application for support ticket analysis."""

from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, HTTPException

from src.api.dependencies import get_analysis_service
from src.api.schemas import (
    AnalyticsResponse,
    EntitiesResponse,
    FullPipelineResponse,
    HistoryResponse,
    HealthResponse,
    MetricsResponse,
    PredictRequest,
    PredictResponse,
    PriorityResponse,
    RouteRequest,
    RouteResponse,
)
from src.api.services import ModelLoadError, TicketAnalysisService
from src.routing import UnsupportedCategoryError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Automated IT Support Ticket NLP API",
    description="Classify, extract entities, prioritize, and route IT support tickets.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return API health status."""
    return HealthResponse(status="healthy")


@app.get("/metrics", response_model=MetricsResponse)
def metrics(service: TicketAnalysisService = Depends(get_analysis_service)) -> MetricsResponse:
    """Return model and rule metadata."""
    try:
        return MetricsResponse(**service.metrics())
    except ModelLoadError as exc:
        logger.exception("Unable to load model metrics.")
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/predict", response_model=PredictResponse)
def predict(
    request: PredictRequest,
    service: TicketAnalysisService = Depends(get_analysis_service),
) -> PredictResponse:
    """Predict the support ticket category."""
    prediction = service.predict(request.ticket_text)
    return PredictResponse(category=prediction.category, confidence=prediction.confidence)


@app.post("/entities", response_model=EntitiesResponse)
def entities(
    request: PredictRequest,
    service: TicketAnalysisService = Depends(get_analysis_service),
) -> EntitiesResponse:
    """Extract named entities from support ticket text."""
    return EntitiesResponse(entities=service.extract_entities(request.ticket_text))


@app.post("/priority", response_model=PriorityResponse)
def priority(
    request: PredictRequest,
    service: TicketAnalysisService = Depends(get_analysis_service),
) -> PriorityResponse:
    """Assign rule-based ticket priority."""
    result = service.assign_priority(request.ticket_text)
    return PriorityResponse(priority=result.priority, matched_rule=result.matched_rule)


@app.post("/route", response_model=RouteResponse)
def route(
    request: RouteRequest,
    service: TicketAnalysisService = Depends(get_analysis_service),
) -> RouteResponse:
    """Route a predicted category to the responsible support team."""
    try:
        result = service.route(request.category)
    except UnsupportedCategoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RouteResponse(category=result.category, assigned_team=result.assigned_team)


@app.post("/analyze", response_model=FullPipelineResponse)
def analyze(
    request: PredictRequest,
    service: TicketAnalysisService = Depends(get_analysis_service),
) -> FullPipelineResponse:
    """Run the full ticket analysis workflow."""
    try:
        result = service.analyze(request.ticket_text)
    except UnsupportedCategoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FullPipelineResponse(**result)


@app.get("/history", response_model=HistoryResponse)
def history(
    limit: int = 50,
    service: TicketAnalysisService = Depends(get_analysis_service),
) -> HistoryResponse:
    """Return recent persisted prediction history."""
    return HistoryResponse(predictions=service.history(limit=limit))


@app.get("/analytics", response_model=AnalyticsResponse)
def analytics(service: TicketAnalysisService = Depends(get_analysis_service)) -> AnalyticsResponse:
    """Return persisted prediction analytics."""
    return AnalyticsResponse(**service.analytics())

"""FastAPI dependency providers."""

from __future__ import annotations

from src.api.services import TicketAnalysisService, get_ticket_analysis_service


def get_analysis_service() -> TicketAnalysisService:
    """Provide the singleton ticket analysis service to API routes."""
    return get_ticket_analysis_service()


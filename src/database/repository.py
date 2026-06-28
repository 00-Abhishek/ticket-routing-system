"""Repository for persisted prediction records and analytics."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from src.database.database import SessionLocal, init_database
from src.database.models import TicketPrediction


class PredictionRepository:
    """Data access layer for ticket prediction persistence."""

    def __init__(self, session_factory: Callable[[], Session] = SessionLocal, initialize: bool = True) -> None:
        self.session_factory = session_factory
        if initialize:
            init_database()

    def save_prediction(
        self,
        ticket_text: str,
        category: str,
        confidence: float,
        entities: dict[str, list[str]],
        priority: str,
        assigned_team: str,
    ) -> TicketPrediction:
        """Persist a prediction, extracted entities, priority, and routing decision."""
        entities_json = json.dumps(entities, sort_keys=True)
        with self.session_factory() as session:
            prediction = TicketPrediction(
                ticket_text=ticket_text,
                predicted_category=category,
                confidence_score=confidence,
                entities_json=entities_json,
                priority=priority,
                assigned_team=assigned_team,
            )
            session.add(prediction)
            session.commit()
            session.refresh(prediction)
            return prediction

    def get_recent_predictions(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return recent predictions ordered newest first."""
        safe_limit = max(1, min(limit, 500))
        with self.session_factory() as session:
            statement = (
                select(TicketPrediction)
                .order_by(desc(TicketPrediction.created_at), desc(TicketPrediction.id))
                .limit(safe_limit)
            )
            return [row.to_dict() for row in session.scalars(statement)]

    def get_prediction_count(self) -> int:
        """Return total persisted prediction count."""
        with self.session_factory() as session:
            return int(session.scalar(select(func.count(TicketPrediction.id))) or 0)

    def get_category_distribution(self) -> dict[str, int]:
        """Return prediction counts grouped by predicted category."""
        with self.session_factory() as session:
            statement = (
                select(TicketPrediction.predicted_category, func.count(TicketPrediction.id))
                .group_by(TicketPrediction.predicted_category)
                .order_by(TicketPrediction.predicted_category)
            )
            return {category: int(count) for category, count in session.execute(statement)}

    def get_priority_distribution(self) -> dict[str, int]:
        """Return prediction counts grouped by assigned priority."""
        with self.session_factory() as session:
            statement = (
                select(TicketPrediction.priority, func.count(TicketPrediction.id))
                .group_by(TicketPrediction.priority)
                .order_by(TicketPrediction.priority)
            )
            return {priority: int(count) for priority, count in session.execute(statement)}

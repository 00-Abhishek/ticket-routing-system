"""SQLAlchemy ORM models for prediction persistence."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base ORM class."""


class TicketPrediction(Base):
    """Stored prediction and routing decision for a support ticket."""

    __tablename__ = "ticket_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_text: Mapped[str] = mapped_column(Text, nullable=False)
    predicted_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    entities_json: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    assigned_team: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )

    def to_dict(self) -> dict[str, object]:
        """Serialize the prediction row for API responses."""
        created_at = self.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        return {
            "id": self.id,
            "ticket_text": self.ticket_text,
            "predicted_category": self.predicted_category,
            "confidence_score": self.confidence_score,
            "entities_json": self.entities_json,
            "priority": self.priority,
            "assigned_team": self.assigned_team,
            "created_at": created_at.isoformat(),
        }


import json

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.models import Base
from src.database.repository import PredictionRepository


def build_repository():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return PredictionRepository(session_factory=session_factory, initialize=False), engine


def test_table_creation() -> None:
    _, engine = build_repository()

    inspector = inspect(engine)

    assert "ticket_predictions" in inspector.get_table_names()


def test_save_prediction() -> None:
    repository, _ = build_repository()

    prediction = repository.save_prediction(
        ticket_text="Outlook not working on laptop",
        category="Hardware",
        confidence=0.91,
        entities={"SOFTWARE": ["Outlook"], "DEVICE": ["laptop"]},
        priority="High",
        assigned_team="Hardware Team",
    )

    assert prediction.id == 1
    assert prediction.predicted_category == "Hardware"
    assert json.loads(prediction.entities_json) == {"DEVICE": ["laptop"], "SOFTWARE": ["Outlook"]}


def test_query_recent_predictions() -> None:
    repository, _ = build_repository()
    repository.save_prediction("Ticket one", "Hardware", 0.8, {}, "Medium", "Hardware Team")
    repository.save_prediction("Ticket two", "Access", 0.9, {}, "High", "Access Management Team")

    recent = repository.get_recent_predictions(limit=1)

    assert len(recent) == 1
    assert recent[0]["ticket_text"] == "Ticket two"
    assert recent[0]["created_at"].endswith("+00:00")


def test_analytics_queries() -> None:
    repository, _ = build_repository()
    repository.save_prediction("Ticket one", "Hardware", 0.8, {}, "Medium", "Hardware Team")
    repository.save_prediction("Ticket two", "Hardware", 0.9, {}, "High", "Hardware Team")
    repository.save_prediction("Ticket three", "Access", 0.7, {}, "High", "Access Management Team")

    assert repository.get_prediction_count() == 3
    assert repository.get_category_distribution() == {"Access": 1, "Hardware": 2}
    assert repository.get_priority_distribution() == {"High": 2, "Medium": 1}

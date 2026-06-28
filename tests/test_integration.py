from dataclasses import dataclass

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.app import app
from src.api.dependencies import get_analysis_service
from src.api.services import Prediction
from src.database.models import Base
from src.database.repository import PredictionRepository
from src.ner import EntityExtractor
from src.priority import PriorityEngine
from src.routing import TicketRouter


@dataclass
class IntegrationAnalysisService:
    repository: PredictionRepository
    ner_extractor: EntityExtractor
    priority_engine: PriorityEngine
    router: TicketRouter

    def predict(self, ticket_text: str) -> Prediction:
        text = ticket_text.lower()
        if "admin rights" in text or "administrator permission" in text:
            return Prediction("Administrative rights", 0.93)
        if "payroll" in text or "hr portal" in text:
            return Prediction("HR Support", 0.91)
        if "mailbox" in text or "shared drive" in text or "folder" in text:
            return Prediction("Storage", 0.90)
        if "purchase" in text or "procurement" in text or "headset" in text:
            return Prediction("Purchase", 0.89)
        if "project code" in text or "billing code" in text:
            return Prediction("Internal Project", 0.88)
        if "login" in text or "access denied" in text or "vpn" in text:
            return Prediction("Access", 0.92)
        if "laptop" in text or "server" in text or "printer" in text:
            return Prediction("Hardware", 0.94)
        return Prediction("Miscellaneous", 0.87)

    def extract_entities(self, ticket_text: str) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = {}
        for entity in self.ner_extractor.extract(ticket_text):
            grouped.setdefault(entity.label, [])
            if entity.text not in grouped[entity.label]:
                grouped[entity.label].append(entity.text)
        return grouped

    def assign_priority(self, ticket_text: str):
        return self.priority_engine.assign_priority(ticket_text)

    def route(self, category: str):
        return self.router.route(category)

    def analyze(self, ticket_text: str) -> dict[str, object]:
        prediction = self.predict(ticket_text)
        entities = self.extract_entities(ticket_text)
        priority = self.assign_priority(ticket_text)
        route = self.route(prediction.category)
        self.repository.save_prediction(
            ticket_text=ticket_text,
            category=prediction.category,
            confidence=prediction.confidence,
            entities=entities,
            priority=priority.priority,
            assigned_team=route.assigned_team,
        )
        return {
            "category": prediction.category,
            "confidence": prediction.confidence,
            "entities": entities,
            "priority": priority.priority,
            "matched_rule": priority.matched_rule,
            "assigned_team": route.assigned_team,
        }

    def history(self, limit: int = 50):
        return self.repository.get_recent_predictions(limit)

    def analytics(self):
        return {
            "total_predictions": self.repository.get_prediction_count(),
            "category_distribution": self.repository.get_category_distribution(),
            "priority_distribution": self.repository.get_priority_distribution(),
        }

    def metrics(self):
        return {
            "model_name": "distilbert-base-uncased",
            "number_of_classes": 8,
            "available_entities": ["DEVICE", "ERROR_CODE", "LOCATION", "SOFTWARE", "SYSTEM"],
            "supported_priorities": ["Critical", "High", "Medium", "Low"],
        }


def build_integration_client() -> tuple[TestClient, PredictionRepository]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    repository = PredictionRepository(session_factory=session_factory, initialize=False)
    service = IntegrationAnalysisService(
        repository=repository,
        ner_extractor=EntityExtractor(),
        priority_engine=PriorityEngine(),
        router=TicketRouter(),
    )
    app.dependency_overrides[get_analysis_service] = lambda: service
    return TestClient(app), repository


def test_predict_endpoint_integration() -> None:
    client, _ = build_integration_client()

    response = client.post("/predict", json={"ticket_text": "Unable to login to Outlook on my laptop"})

    assert response.status_code == 200
    assert response.json()["category"] == "Access"
    assert response.json()["confidence"] == 0.92


def test_analyze_endpoint_persists_full_workflow() -> None:
    client, repository = build_integration_client()

    response = client.post("/analyze", json={"ticket_text": "Unable to login to Outlook on my laptop"})

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Access"
    assert body["priority"] == "High"
    assert body["assigned_team"] == "Access Management Team"
    assert body["entities"]["SOFTWARE"] == ["Outlook"]
    assert body["entities"]["DEVICE"] == ["laptop"]
    assert repository.get_prediction_count() == 1


def test_database_history_and_analytics_after_analysis() -> None:
    client, _ = build_integration_client()
    client.post("/analyze", json={"ticket_text": "Production server is down and system unavailable"})
    client.post("/analyze", json={"ticket_text": "Need more mailbox storage for shared mailbox"})

    history = client.get("/history").json()["predictions"]
    analytics = client.get("/analytics").json()

    assert len(history) == 2
    assert analytics["total_predictions"] == 2
    assert analytics["category_distribution"] == {"Hardware": 1, "Storage": 1}
    assert analytics["priority_distribution"] == {"Critical": 1, "Medium": 1}


def test_routing_priority_and_entity_extraction_integration() -> None:
    client, _ = build_integration_client()

    response = client.post(
        "/analyze",
        json={"ticket_text": "Production server is down in the data center with HTTP 500"},
    )

    body = response.json()
    assert body["category"] == "Hardware"
    assert body["priority"] == "Critical"
    assert body["assigned_team"] == "Hardware Team"
    assert "LOCATION" in body["entities"]
    assert "ERROR_CODE" in body["entities"]


def test_priority_rule_is_identical_across_priority_and_analyze_endpoints() -> None:
    client, _ = build_integration_client()
    ticket = "I am unable to log in to the employee portal since this morning..."

    priority_body = client.post("/priority", json={"ticket_text": ticket}).json()
    analyze_body = client.post("/analyze", json={"ticket_text": ticket}).json()

    assert priority_body == {"priority": "High", "matched_rule": "cannot login"}
    assert analyze_body["priority"] == priority_body["priority"]
    assert analyze_body["matched_rule"] == priority_body["matched_rule"]

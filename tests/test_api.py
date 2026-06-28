from dataclasses import dataclass

from fastapi.testclient import TestClient

from src.api.app import app
from src.api.dependencies import get_analysis_service
from src.api.services import Prediction
from src.priority.engine import PriorityResult
from src.routing.router import RouteResult


@dataclass
class StubAnalysisService:
    def predict(self, ticket_text: str) -> Prediction:
        if "admin rights" in ticket_text.lower():
            return Prediction(category="Administrative rights", confidence=0.93)
        return Prediction(category="Hardware", confidence=0.88)

    def extract_entities(self, ticket_text: str) -> dict[str, list[str]]:
        entities: dict[str, list[str]] = {}
        if "outlook" in ticket_text.lower():
            entities["SOFTWARE"] = ["Outlook"]
        if "laptop" in ticket_text.lower():
            entities["DEVICE"] = ["laptop"]
        return entities

    def assign_priority(self, ticket_text: str) -> PriorityResult:
        if "production server is down" in ticket_text.lower():
            return PriorityResult(priority="Critical", matched_rule="server down")
        if "unable to login" in ticket_text.lower() or "unable to log in" in ticket_text.lower():
            return PriorityResult(priority="High", matched_rule="cannot login")
        return PriorityResult(priority="Medium", matched_rule=None)

    def route(self, category: str) -> RouteResult:
        mapping = {
            "Hardware": "Hardware Team",
            "Administrative rights": "System Administration Team",
        }
        return RouteResult(category=category, assigned_team=mapping[category])

    def analyze(self, ticket_text: str) -> dict[str, object]:
        prediction = self.predict(ticket_text)
        priority = self.assign_priority(ticket_text)
        route = self.route(prediction.category)
        return {
            "category": prediction.category,
            "confidence": prediction.confidence,
            "entities": self.extract_entities(ticket_text),
            "priority": priority.priority,
            "matched_rule": priority.matched_rule,
            "assigned_team": route.assigned_team,
        }

    def metrics(self) -> dict[str, object]:
        return {
            "model_name": "distilbert-base-uncased",
            "number_of_classes": 8,
            "available_entities": ["DEVICE", "ERROR_CODE", "LOCATION", "SOFTWARE", "SYSTEM"],
            "supported_priorities": ["Critical", "High", "Medium", "Low"],
        }

    def history(self, limit: int = 50) -> list[dict[str, object]]:
        return [
            {
                "id": 1,
                "ticket_text": "Outlook not working on laptop",
                "predicted_category": "Hardware",
                "confidence_score": 0.88,
                "entities_json": '{"DEVICE": ["laptop"], "SOFTWARE": ["Outlook"]}',
                "priority": "High",
                "assigned_team": "Hardware Team",
                "created_at": "2026-06-02T12:00:00+00:00",
            }
        ][:limit]

    def analytics(self) -> dict[str, object]:
        return {
            "total_predictions": 1,
            "category_distribution": {"Hardware": 1},
            "priority_distribution": {"High": 1},
        }


def override_analysis_service() -> StubAnalysisService:
    return StubAnalysisService()


app.dependency_overrides[get_analysis_service] = override_analysis_service
client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_metrics_endpoint() -> None:
    response = client.get("/metrics")

    assert response.status_code == 200
    body = response.json()
    assert body["model_name"] == "distilbert-base-uncased"
    assert body["number_of_classes"] == 8
    assert "SOFTWARE" in body["available_entities"]
    assert "Critical" in body["supported_priorities"]


def test_predict_endpoint() -> None:
    response = client.post("/predict", json={"ticket_text": "Need admin rights for Visual Studio"})

    assert response.status_code == 200
    assert response.json() == {
        "category": "Administrative rights",
        "confidence": 0.93,
    }


def test_entities_endpoint() -> None:
    response = client.post("/entities", json={"ticket_text": "Outlook not working on laptop"})

    assert response.status_code == 200
    assert response.json() == {
        "entities": {
            "SOFTWARE": ["Outlook"],
            "DEVICE": ["laptop"],
        }
    }


def test_priority_endpoint() -> None:
    response = client.post("/priority", json={"ticket_text": "Production server is down"})

    assert response.status_code == 200
    assert response.json() == {
        "priority": "Critical",
        "matched_rule": "server down",
    }


def test_route_endpoint() -> None:
    response = client.post("/route", json={"category": "Hardware"})

    assert response.status_code == 200
    assert response.json() == {
        "category": "Hardware",
        "assigned_team": "Hardware Team",
    }


def test_analyze_endpoint() -> None:
    response = client.post("/analyze", json={"ticket_text": "Unable to login to Outlook on my laptop"})

    assert response.status_code == 200
    assert response.json() == {
        "category": "Hardware",
        "confidence": 0.88,
        "entities": {
            "SOFTWARE": ["Outlook"],
            "DEVICE": ["laptop"],
        },
        "priority": "High",
        "matched_rule": "cannot login",
        "assigned_team": "Hardware Team",
    }


def test_priority_and_analyze_preserve_same_matched_rule() -> None:
    ticket = "I am unable to log in to the employee portal since this morning..."

    priority_response = client.post("/priority", json={"ticket_text": ticket})
    analyze_response = client.post("/analyze", json={"ticket_text": ticket})

    assert priority_response.status_code == 200
    assert analyze_response.status_code == 200
    assert priority_response.json()["matched_rule"] == "cannot login"
    assert analyze_response.json()["matched_rule"] == priority_response.json()["matched_rule"]


def test_history_endpoint() -> None:
    response = client.get("/history")

    assert response.status_code == 200
    body = response.json()
    assert body["predictions"][0]["predicted_category"] == "Hardware"
    assert body["predictions"][0]["priority"] == "High"


def test_analytics_endpoint() -> None:
    response = client.get("/analytics")

    assert response.status_code == 200
    assert response.json() == {
        "total_predictions": 1,
        "category_distribution": {"Hardware": 1},
        "priority_distribution": {"High": 1},
    }

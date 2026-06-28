"""Application services loaded once for FastAPI endpoints."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast

from src.ner import EntityExtractor
from src.priority import PriorityEngine, PriorityResult
from src.priority.rules import get_supported_priorities
from src.routing import TicketRouter
from src.database.repository import PredictionRepository

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models" / "distilbert"
DEFAULT_PATTERN_PATH = PROJECT_ROOT / "config" / "entity_patterns.json"


@dataclass(frozen=True)
class Prediction:
    """Model prediction result."""

    category: str
    confidence: float


class ModelLoadError(RuntimeError):
    """Raised when trained model artifacts cannot be loaded."""


class TicketAnalysisService:
    """Facade over classification, NER, priority, and routing services."""

    def __init__(
        self,
        model_dir: Path = DEFAULT_MODEL_DIR,
        pattern_path: Path = DEFAULT_PATTERN_PATH,
        prediction_repository: PredictionRepository | None = None,
    ) -> None:
        self.model_dir = model_dir
        self.pattern_path = pattern_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.label2id, self.id2label = self._load_label_mapping(model_dir)
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(str(model_dir))
        self.model = DistilBertForSequenceClassification.from_pretrained(str(model_dir))
        self.model.to(self.device)
        self.model.eval()
        self.ner_extractor = EntityExtractor(pattern_path=pattern_path)
        self.priority_engine = PriorityEngine()
        self.ticket_router = TicketRouter()
        self.prediction_repository = prediction_repository or PredictionRepository()
        logger.info("Loaded API services using model directory %s on %s.", model_dir, self.device)

    @property
    def model_name(self) -> str:
        """Return the classifier model name shown by /metrics."""
        return "distilbert-base-uncased"

    @property
    def number_of_classes(self) -> int:
        """Return number of trained classifier labels."""
        return len(self.id2label)

    def predict(self, ticket_text: str) -> Prediction:
        """Predict ticket category and confidence using the trained DistilBERT model."""
        encoded = self.tokenizer(
            ticket_text,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt",
        )
        encoded = {key: value.to(self.device) for key, value in encoded.items()}
        with torch.no_grad():
            logits = self.model(**encoded).logits
            probabilities = torch.softmax(logits, dim=-1)[0]
            confidence, label_id = torch.max(probabilities, dim=0)

        category = self.id2label[int(label_id.item())]
        result = Prediction(category=category, confidence=float(confidence.item()))
        logger.info("Predicted category %r with confidence %.4f.", result.category, result.confidence)
        return result

    def extract_entities(self, ticket_text: str) -> dict[str, list[str]]:
        """Extract and group entities by label."""
        grouped: dict[str, list[str]] = {}
        for entity in self.ner_extractor.extract(ticket_text):
            grouped.setdefault(entity.label, [])
            if entity.text not in grouped[entity.label]:
                grouped[entity.label].append(entity.text)
        return grouped

    def assign_priority(self, ticket_text: str) -> PriorityResult:
        """Assign priority to a ticket."""
        return self.priority_engine.assign_priority(ticket_text)

    def route(self, category: str):
        """Route a predicted category to a support team."""
        return self.ticket_router.route(category)

    def analyze(self, ticket_text: str) -> dict[str, Any]:
        """Run classification, entity extraction, priority, and routing."""
        prediction = self.predict(ticket_text)
        entities = self.extract_entities(ticket_text)
        priority = self.assign_priority(ticket_text)
        route = self.route(prediction.category)
        self.prediction_repository.save_prediction(
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

    def history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return recent persisted prediction records."""
        return self.prediction_repository.get_recent_predictions(limit=limit)

    def analytics(self) -> dict[str, Any]:
        """Return persisted prediction analytics."""
        return {
            "total_predictions": self.prediction_repository.get_prediction_count(),
            "category_distribution": self.prediction_repository.get_category_distribution(),
            "priority_distribution": self.prediction_repository.get_priority_distribution(),
        }

    def metrics(self) -> dict[str, Any]:
        """Return metadata for model and rule-based services."""
        return {
            "model_name": self.model_name,
            "number_of_classes": self.number_of_classes,
            "available_entities": self._available_entity_labels(),
            "supported_priorities": list(get_supported_priorities()),
        }

    @staticmethod
    def _load_label_mapping(model_dir: Path) -> tuple[dict[str, int], dict[int, str]]:
        mapping_path = model_dir / "label_mapping.json"
        if not mapping_path.exists():
            raise ModelLoadError(f"Label mapping not found: {mapping_path}")
        with mapping_path.open("r", encoding="utf-8") as file:
            mapping = json.load(file)
        label2id = {str(label): int(index) for label, index in mapping["label2id"].items()}
        id2label = {int(index): str(label) for index, label in mapping["id2label"].items()}
        return label2id, id2label

    def _available_entity_labels(self) -> list[str]:
        patterns = EntityExtractor.load_patterns(self.pattern_path)
        return sorted({str(pattern["label"]) for pattern in patterns})


@lru_cache(maxsize=1)
def get_ticket_analysis_service() -> TicketAnalysisService:
    """Return singleton service instance for dependency injection."""
    return TicketAnalysisService()

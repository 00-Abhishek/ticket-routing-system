"""spaCy rule-based entity extraction for IT support tickets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import spacy
from spacy.language import Language
from spacy.pipeline import EntityRuler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATTERN_PATH = PROJECT_ROOT / "config" / "entity_patterns.json"


@dataclass(frozen=True)
class EntityMatch:
    """A normalized entity extracted from a support ticket."""

    text: str
    label: str
    start_char: int
    end_char: int
    pattern_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EntityExtractor:
    """Configurable spaCy EntityRuler extractor for ticket entities."""

    def __init__(self, pattern_path: Path = DEFAULT_PATTERN_PATH) -> None:
        self.pattern_path = pattern_path
        self.nlp = self._build_pipeline(pattern_path)

    def extract(self, text: str) -> list[EntityMatch]:
        """Extract configured entities from raw ticket text."""
        if not text or not text.strip():
            return []

        doc = self.nlp(text)
        return [
            EntityMatch(
                text=entity.text,
                label=entity.label_,
                start_char=entity.start_char,
                end_char=entity.end_char,
                pattern_id=entity.ent_id_ or None,
            )
            for entity in doc.ents
        ]

    def extract_as_dicts(self, text: str) -> list[dict[str, Any]]:
        """Extract entities and serialize them as dictionaries."""
        return [match.to_dict() for match in self.extract(text)]

    @staticmethod
    def load_patterns(pattern_path: Path = DEFAULT_PATTERN_PATH) -> list[dict[str, Any]]:
        if not pattern_path.exists():
            raise FileNotFoundError(f"Entity pattern file not found: {pattern_path}")
        with pattern_path.open("r", encoding="utf-8") as file:
            patterns = json.load(file)
        if not isinstance(patterns, list):
            raise ValueError("Entity pattern file must contain a JSON list.")
        return patterns

    @classmethod
    def _build_pipeline(cls, pattern_path: Path) -> Language:
        nlp = spacy.blank("en")
        ruler = nlp.add_pipe(
            "entity_ruler",
            config={
                "overwrite_ents": True,
                "phrase_matcher_attr": "LOWER",
                "validate": True,
            },
        )
        assert isinstance(ruler, EntityRuler)
        ruler.add_patterns(cls.load_patterns(pattern_path))
        return nlp


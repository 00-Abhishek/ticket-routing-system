"""Rule-based priority assignment for support tickets."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from src.priority.rules import MEDIUM, get_match_terms, get_priority_rules

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PriorityResult:
    """Priority decision returned by the priority engine."""

    priority: str
    matched_rule: str | None

    def __post_init__(self) -> None:
        if not self.priority or not self.priority.strip():
            raise ValueError("PriorityResult priority must be a non-empty string.")

    def to_dict(self) -> dict[str, str | None]:
        """Serialize the priority result for API, dashboard, or persistence layers."""
        return {
            "priority": self.priority,
            "matched_rule": self.matched_rule,
        }


class PriorityEngine:
    """Assign ticket priority using configurable keyword rules."""

    def assign_priority(self, ticket_text: str) -> PriorityResult:
        """Assign priority by matching highest-priority rules first.

        Args:
            ticket_text: Raw support ticket text.

        Returns:
            PriorityResult with the selected priority and canonical matched rule.

        Raises:
            TypeError: If ticket_text is not a string.
        """
        if not isinstance(ticket_text, str):
            logger.error("Priority assignment received non-string ticket text: %r", ticket_text)
            raise TypeError("ticket_text must be provided as a string.")

        normalized_text = self._normalize_text(ticket_text)
        for priority, keywords in get_priority_rules().items():
            for keyword in keywords:
                if self._keyword_matches(normalized_text, keyword):
                    result = PriorityResult(priority=priority, matched_rule=keyword)
                    logger.info(
                        "Assigned priority %r using rule %r.",
                        result.priority,
                        result.matched_rule,
                    )
                    return result

        logger.info("No priority keyword matched; defaulting to %r.", MEDIUM)
        return PriorityResult(priority=MEDIUM, matched_rule=None)

    @staticmethod
    def _normalize_text(ticket_text: str) -> str:
        lowered = ticket_text.lower()
        normalized = re.sub(r"[^a-z0-9]+", " ", lowered)
        return re.sub(r"\s+", " ", normalized).strip()

    @classmethod
    def _keyword_matches(cls, normalized_text: str, keyword: str) -> bool:
        for term in get_match_terms(keyword):
            normalized_term = cls._normalize_text(term)
            pattern = rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])"
            if re.search(pattern, normalized_text):
                return True
        return False


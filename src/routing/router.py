"""Business logic for routing predicted ticket categories to support teams."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from src.routing.rules import get_supported_categories, get_team_for_category

logger = logging.getLogger(__name__)


class UnsupportedCategoryError(ValueError):
    """Raised when routing is requested for an unsupported category."""


@dataclass(frozen=True)
class RouteResult:
    """Routing decision for a predicted ticket category."""

    category: str
    assigned_team: str

    def __post_init__(self) -> None:
        if not self.category or not self.category.strip():
            raise ValueError("RouteResult category must be a non-empty string.")
        if not self.assigned_team or not self.assigned_team.strip():
            raise ValueError("RouteResult assigned_team must be a non-empty string.")

    def to_dict(self) -> dict[str, str]:
        """Serialize the routing result for API, dashboard, or persistence layers."""
        return {
            "category": self.category,
            "assigned_team": self.assigned_team,
        }


class TicketRouter:
    """Route predicted support ticket categories to responsible teams."""

    def route(self, category: str) -> RouteResult:
        """Return a routing decision for a predicted category.

        Args:
            category: Predicted ticket category, such as "Hardware" or "Access".

        Raises:
            UnsupportedCategoryError: If the category is blank or not configured.
        """
        normalized_category = self._normalize_category(category)
        assigned_team = get_team_for_category(normalized_category)
        if assigned_team is None:
            supported = ", ".join(get_supported_categories())
            logger.error(
                "Unsupported routing category received: %r. Supported categories: %s",
                category,
                supported,
            )
            raise UnsupportedCategoryError(
                f"Unsupported category '{category}'. Supported categories: {supported}."
            )

        result = RouteResult(category=normalized_category, assigned_team=assigned_team)
        logger.info(
            "Routed category %r to team %r.",
            result.category,
            result.assigned_team,
        )
        return result

    @staticmethod
    def _normalize_category(category: str) -> str:
        if not isinstance(category, str):
            raise UnsupportedCategoryError("Category must be provided as a string.")
        normalized = category.strip()
        if not normalized:
            raise UnsupportedCategoryError("Category must be a non-empty string.")
        return normalized


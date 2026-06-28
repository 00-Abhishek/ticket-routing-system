"""Configurable routing rules for ticket category assignment."""

from __future__ import annotations

from types import MappingProxyType

CATEGORY_TO_TEAM: dict[str, str] = {
    "Hardware": "Hardware Team",
    "HR Support": "HR Team",
    "Access": "Access Management Team",
    "Storage": "Storage Team",
    "Purchase": "Procurement Team",
    "Administrative rights": "System Administration Team",
    "Internal Project": "Internal Projects Team",
    "Miscellaneous": "Service Desk Team",
}


def get_category_to_team_mapping() -> MappingProxyType[str, str]:
    """Return a read-only view of the category-to-team routing mapping."""
    return MappingProxyType(CATEGORY_TO_TEAM)


def get_supported_categories() -> tuple[str, ...]:
    """Return supported ticket categories in deterministic order."""
    return tuple(CATEGORY_TO_TEAM.keys())


def get_team_for_category(category: str) -> str | None:
    """Return the team for a category, or None when the category is unsupported."""
    return CATEGORY_TO_TEAM.get(category)


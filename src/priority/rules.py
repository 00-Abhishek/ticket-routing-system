"""Configurable keyword rules for support ticket priority assignment."""

from __future__ import annotations

from types import MappingProxyType

CRITICAL = "Critical"
HIGH = "High"
MEDIUM = "Medium"
LOW = "Low"
SUPPORTED_PRIORITIES: tuple[str, ...] = (CRITICAL, HIGH, MEDIUM, LOW)

CRITICAL_KEYWORDS: tuple[str, ...] = (
    "server down",
    "production down",
    "outage",
    "system unavailable",
    "data loss",
)

HIGH_KEYWORDS: tuple[str, ...] = (
    "cannot login",
    "access denied",
    "vpn not working",
    "email not working",
    "application unavailable",
)

MEDIUM_KEYWORDS: tuple[str, ...] = (
    "installation",
    "software request",
    "upgrade",
    "configuration",
)

LOW_KEYWORDS: tuple[str, ...] = (
    "information request",
    "documentation",
    "inquiry",
)

KEYWORD_RULES: dict[str, tuple[str, ...]] = {
    CRITICAL: CRITICAL_KEYWORDS,
    HIGH: HIGH_KEYWORDS,
    MEDIUM: MEDIUM_KEYWORDS,
    LOW: LOW_KEYWORDS,
}

KEYWORD_ALIASES: dict[str, tuple[str, ...]] = {
    "server down": (
        "server is down",
        "server went down",
        "server unavailable",
    ),
    "production down": (
        "production is down",
        "prod down",
        "prod is down",
    ),
    "cannot login": (
        "cannot log in",
        "can't login",
        "cant login",
        "unable to login",
        "unable to log in",
        "login failed",
        "log in failed",
    ),
    "email not working": (
        "mail not working",
        "outlook not working",
        "email down",
        "mailbox not working",
    ),
    "vpn not working": (
        "vpn down",
        "vpn failed",
        "unable to connect vpn",
        "unable to connect to vpn",
    ),
    "documentation": (
        "user guide",
        "guide",
        "manual",
    ),
}


def get_priority_rules() -> MappingProxyType[str, tuple[str, ...]]:
    """Return a read-only view of priority-to-keywords rules."""
    return MappingProxyType(KEYWORD_RULES)


def get_keyword_aliases() -> MappingProxyType[str, tuple[str, ...]]:
    """Return a read-only view of canonical keyword aliases."""
    return MappingProxyType(KEYWORD_ALIASES)


def get_supported_priorities() -> tuple[str, ...]:
    """Return supported priorities from highest to lowest precedence."""
    return SUPPORTED_PRIORITIES


def get_match_terms(keyword: str) -> tuple[str, ...]:
    """Return the canonical keyword and any configured aliases."""
    return (keyword, *KEYWORD_ALIASES.get(keyword, ()))

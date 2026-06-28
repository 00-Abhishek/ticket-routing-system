import pytest

from src.priority.engine import PriorityEngine, PriorityResult


def test_critical_priority_cases() -> None:
    engine = PriorityEngine()

    result = engine.assign_priority("Production server is down")

    assert result == PriorityResult(priority="Critical", matched_rule="server down")


def test_critical_precedence_over_lower_priority() -> None:
    engine = PriorityEngine()

    result = engine.assign_priority("Production down and need installation support")

    assert result.priority == "Critical"
    assert result.matched_rule == "production down"


def test_high_priority_cases_with_alias() -> None:
    engine = PriorityEngine()

    result = engine.assign_priority("Unable to login to Outlook")

    assert result == PriorityResult(priority="High", matched_rule="cannot login")


def test_high_priority_regression_preserves_canonical_rule() -> None:
    engine = PriorityEngine()

    result = engine.assign_priority(
        "I am unable to log in to the employee portal since this morning..."
    )

    assert result == PriorityResult(priority="High", matched_rule="cannot login")


def test_medium_priority_cases() -> None:
    engine = PriorityEngine()

    result = engine.assign_priority("Need installation of Visual Studio")

    assert result == PriorityResult(priority="Medium", matched_rule="installation")


def test_low_priority_cases_with_alias() -> None:
    engine = PriorityEngine()

    result = engine.assign_priority("Need user guide")

    assert result == PriorityResult(priority="Low", matched_rule="documentation")


def test_default_behavior_is_medium() -> None:
    engine = PriorityEngine()

    result = engine.assign_priority("Please create a normal support ticket")

    assert result == PriorityResult(priority="Medium", matched_rule=None)


def test_case_insensitive_matching() -> None:
    engine = PriorityEngine()

    result = engine.assign_priority("SYSTEM UNAVAILABLE for all users")

    assert result == PriorityResult(priority="Critical", matched_rule="system unavailable")


def test_priority_result_validation() -> None:
    with pytest.raises(ValueError, match="priority"):
        PriorityResult(priority="", matched_rule=None)


def test_non_string_ticket_text_raises_type_error() -> None:
    engine = PriorityEngine()

    with pytest.raises(TypeError, match="ticket_text"):
        engine.assign_priority(None)  # type: ignore[arg-type]

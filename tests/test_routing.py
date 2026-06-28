import pytest

from src.routing.router import RouteResult, TicketRouter, UnsupportedCategoryError
from src.routing.rules import CATEGORY_TO_TEAM, get_category_to_team_mapping, get_supported_categories


def test_every_category_mapping_routes_to_expected_team() -> None:
    router = TicketRouter()

    for category, expected_team in CATEGORY_TO_TEAM.items():
        result = router.route(category)

        assert result == RouteResult(category=category, assigned_team=expected_team)
        assert result.to_dict() == {
            "category": category,
            "assigned_team": expected_team,
        }


def test_unknown_category_raises_descriptive_exception() -> None:
    router = TicketRouter()

    with pytest.raises(UnsupportedCategoryError, match="Unsupported category 'Networking'"):
        router.route("Networking")


def test_blank_category_raises_descriptive_exception() -> None:
    router = TicketRouter()

    with pytest.raises(UnsupportedCategoryError, match="non-empty string"):
        router.route("   ")


def test_non_string_category_raises_descriptive_exception() -> None:
    router = TicketRouter()

    with pytest.raises(UnsupportedCategoryError, match="provided as a string"):
        router.route(None)  # type: ignore[arg-type]


def test_route_result_validation() -> None:
    with pytest.raises(ValueError, match="category"):
        RouteResult(category="", assigned_team="Hardware Team")

    with pytest.raises(ValueError, match="assigned_team"):
        RouteResult(category="Hardware", assigned_team="")


def test_mapping_helpers_are_read_only_and_complete() -> None:
    mapping = get_category_to_team_mapping()

    assert tuple(mapping.keys()) == get_supported_categories()
    with pytest.raises(TypeError):
        mapping["Other"] = "Other Team"  # type: ignore[index]


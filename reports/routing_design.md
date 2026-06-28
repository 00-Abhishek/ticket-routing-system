# Phase 6 Routing Engine Design

## Scope

Phase 6 implements deterministic routing from a predicted ticket category to a support team.

This phase does not implement:

- Priority engine
- FastAPI
- SQLite
- Streamlit
- Docker

## Architecture

```text
Predicted Category
        |
        v
TicketRouter.route(category)
        |
        v
rules.CATEGORY_TO_TEAM
        |
        v
RouteResult(category, assigned_team)
```

## Files

- `src/routing/__init__.py`
- `src/routing/rules.py`
- `src/routing/router.py`
- `tests/test_routing.py`

## Mapping Table

| Category | Assigned Team |
| --- | --- |
| Hardware | Hardware Team |
| HR Support | HR Team |
| Access | Access Management Team |
| Storage | Storage Team |
| Purchase | Procurement Team |
| Administrative rights | System Administration Team |
| Internal Project | Internal Projects Team |
| Miscellaneous | Service Desk Team |

## Routing Workflow

1. The classification model predicts a category.
2. `TicketRouter.route(category)` validates that the category is a non-empty string.
3. The router looks up the category in `CATEGORY_TO_TEAM`.
4. If the category is supported, it returns `RouteResult`.
5. If the category is unknown, it raises `UnsupportedCategoryError` with the supported category list.
6. Successful and failed routing decisions are logged.

## Business Logic

`RouteResult` is a frozen dataclass with:

- `category: str`
- `assigned_team: str`

It validates that both fields are non-empty strings and exposes `to_dict()` for future API, dashboard, or persistence layers.

## Extension Strategy

Future routing rules can extend this design without changing the API surface:

- Add new categories to `CATEGORY_TO_TEAM`.
- Move rules to JSON/YAML if non-developers need to edit routing.
- Add entity-aware routing, for example route `SOFTWARE=Oracle` to an ERP support queue.
- Add priority-aware routing in a later phase.
- Add fallback teams only after product requirements define the behavior.

Unknown categories intentionally fail fast today so model/category drift is visible during testing and demos.


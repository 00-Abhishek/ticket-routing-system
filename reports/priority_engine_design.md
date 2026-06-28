# Phase 6.5 Priority Engine Design

## Scope

Phase 6.5 implements a deterministic rule-based priority engine for IT support tickets.

This phase does not implement:

- FastAPI
- SQLite
- Streamlit
- Docker

## Architecture

```text
Ticket Text
    |
    v
PriorityEngine.assign_priority(ticket_text)
    |
    v
Normalize Text
    |
    v
Match Keyword Rules from Highest to Lowest Priority
    |
    v
PriorityResult(priority, matched_rule)
```

## Files

- `src/priority/__init__.py`
- `src/priority/rules.py`
- `src/priority/engine.py`
- `tests/test_priority.py`

## Supported Priorities

- `Critical`
- `High`
- `Medium`
- `Low`

## Keyword Rule Hierarchy

Rules are evaluated in this order:

1. `Critical`
2. `High`
3. `Medium`
4. `Low`

If no keyword matches, the engine defaults to `Medium`.

| Priority | Keywords |
| --- | --- |
| Critical | server down, production down, outage, system unavailable, data loss |
| High | cannot login, access denied, vpn not working, email not working, application unavailable |
| Medium | installation, software request, upgrade, configuration |
| Low | information request, documentation, inquiry |

## Alias Handling

Some user phrasing differs from canonical rules. The engine supports aliases while returning the canonical matched rule.

Examples:

| Input Phrase | Canonical Rule |
| --- | --- |
| unable to login | cannot login |
| cannot log in | cannot login |
| outlook not working | email not working |
| vpn down | vpn not working |
| user guide | documentation |

## Examples

| Input | Output |
| --- | --- |
| `Production server is down` | `Critical`, matched rule `server down` |
| `Unable to login to Outlook` | `High`, matched rule `cannot login` |
| `Need installation of Visual Studio` | `Medium`, matched rule `installation` |
| `Need user guide` | `Low`, matched rule `documentation` |
| `Please create a normal support ticket` | `Medium`, no matched rule |

## Error Handling And Logging

- Non-string ticket input raises `TypeError`.
- `PriorityResult` validates that priority is non-empty.
- Priority decisions are logged.
- Invalid input is logged as an error.

## Future ML-Based Priority Prediction Strategy

The rule-based engine is appropriate for the current project because the dataset labels ticket category, not ticket priority. A future ML priority model should be added only after collecting labeled priority data.

Recommended future strategy:

1. Add explicit priority labels to prediction history.
2. Store ticket text, predicted category, extracted entities, routing team, and human-confirmed priority.
3. Train a supervised classifier once enough labeled examples exist.
4. Keep these rules as fallback safety logic for critical outage keywords.
5. Evaluate priority prediction separately using macro-F1 because high-priority classes are usually imbalanced.


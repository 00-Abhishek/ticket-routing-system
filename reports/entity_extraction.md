# Phase 5 Entity Extraction Implementation

## Status

Phase 5 is complete.

Implemented a configurable spaCy rule-based NER system for IT support tickets. The extractor is intentionally rule-based because Phase 5 corpus analysis showed recurring technical terms but no labeled NER training set.

## Files

- `config/entity_patterns.json`
- `src/ner/extractor.py`
- `src/ner/__init__.py`
- `scripts/run_phase5_ner_demo.py`
- `tests/test_ner.py`

## Entity Labels

The implemented extractor supports:

- `SOFTWARE`
- `DEVICE`
- `ERROR_CODE`
- `SYSTEM`
- `LOCATION`

`SYSTEM` and `LOCATION` were added because the corpus analysis showed they are frequent and routing-relevant.

## Design

- Uses `spacy.blank("en")`, so no external language model download is required.
- Uses spaCy `EntityRuler`.
- Loads patterns from JSON configuration.
- Uses case-insensitive phrase matching.
- Uses strict regex patterns for `ERROR_CODE`.
- Lets longer phrases win over shorter overlapping phrases, such as `access card` over `card` and `meeting room` over `room`.

## Demo Command

```bash
python scripts/run_phase5_ner_demo.py
```

## Example Output

Input:

```text
Outlook fails on Windows for a remote user. Please check mailbox permissions and HTTP 500 on laptop in meeting room.
```

Expected entities:

- `Outlook` as `SOFTWARE`
- `Windows` as `SOFTWARE`
- `remote` as `LOCATION`
- `mailbox` as `SYSTEM`
- `permissions` as `SYSTEM`
- `HTTP 500` as `ERROR_CODE`
- `laptop` as `DEVICE`
- `meeting room` as `LOCATION`

## Notes

The source dataset has many generic `error` and `failed` phrases, but no meaningful strict error-code values. For that reason, `ERROR_CODE` extraction is intentionally strict and should not label generic text such as `error occurred`.


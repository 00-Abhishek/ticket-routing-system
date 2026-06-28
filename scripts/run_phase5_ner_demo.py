"""Run a small Phase 5 NER extraction demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.ner import EntityExtractor  # noqa: E402

DEFAULT_TEXT = (
    "Outlook fails on Windows for a remote user. "
    "Please check mailbox permissions and HTTP 500 on laptop in meeting room."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demo Phase 5 spaCy entity extraction.")
    parser.add_argument("--text", default=DEFAULT_TEXT, help="Ticket text to analyze.")
    parser.add_argument(
        "--patterns",
        type=Path,
        default=PROJECT_ROOT / "config" / "entity_patterns.json",
        help="Entity pattern JSON path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    extractor = EntityExtractor(pattern_path=args.patterns)
    print(json.dumps(extractor.extract_as_dicts(args.text), indent=2))


if __name__ == "__main__":
    main()


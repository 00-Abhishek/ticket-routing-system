"""Generate Phase 1 EDA artifacts for the support ticket dataset."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.preprocessing.text import normalize_ticket_series

DEFAULT_DATASET = PROJECT_ROOT / "data" / "all_tickets_processed_improved_v3.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports" / "eda"
REQUIRED_COLUMNS = ("Document", "Topic_group")
RANDOM_SEED = 42


@dataclass(frozen=True)
class DatasetProfile:
    rows: int
    columns: int
    duplicate_rows: int
    missing_documents: int
    missing_labels: int
    class_count: int
    min_class_size: int
    max_class_size: int
    imbalance_ratio: float
    avg_raw_length: float
    median_raw_length: float
    avg_clean_length: float
    median_clean_length: float
    avg_word_count: float
    median_word_count: float
    url_rows: int
    email_rows: int
    numeric_rows: int
    very_short_rows: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 1 EDA for ticket classification.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATASET, help="CSV dataset path.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_DIR, help="EDA output directory.")
    return parser.parse_args()


def validate_dataset_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}\n"
            "Place the CSV at data/all_tickets_processed_improved_v3.csv or pass --data."
        )


def load_dataset(path: Path) -> pd.DataFrame:
    validate_dataset_path(path)
    df = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    return df


def enrich_dataset(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["Document"] = enriched["Document"].fillna("")
    enriched["Topic_group"] = enriched["Topic_group"].fillna("UNKNOWN")
    enriched["clean_document"] = normalize_ticket_series(enriched["Document"])
    enriched["raw_char_length"] = enriched["Document"].astype(str).str.len()
    enriched["clean_char_length"] = enriched["clean_document"].str.len()
    enriched["word_count"] = enriched["clean_document"].str.split().str.len()
    enriched["has_url"] = enriched["Document"].astype(str).str.contains(
        r"https?://|www\.", flags=re.IGNORECASE, regex=True
    )
    enriched["has_email"] = enriched["Document"].astype(str).str.contains(
        r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b", regex=True
    )
    enriched["has_number"] = enriched["Document"].astype(str).str.contains(r"\d", regex=True)
    enriched["is_very_short"] = enriched["word_count"] < 3
    return enriched


def build_profile(df: pd.DataFrame, enriched: pd.DataFrame, class_counts: pd.Series) -> DatasetProfile:
    min_class_size = int(class_counts.min()) if not class_counts.empty else 0
    max_class_size = int(class_counts.max()) if not class_counts.empty else 0
    imbalance_ratio = round(max_class_size / min_class_size, 4) if min_class_size else 0.0
    return DatasetProfile(
        rows=int(len(df)),
        columns=int(len(df.columns)),
        duplicate_rows=int(df.duplicated().sum()),
        missing_documents=int(df["Document"].isna().sum()),
        missing_labels=int(df["Topic_group"].isna().sum()),
        class_count=int(class_counts.shape[0]),
        min_class_size=min_class_size,
        max_class_size=max_class_size,
        imbalance_ratio=imbalance_ratio,
        avg_raw_length=float(enriched["raw_char_length"].mean()),
        median_raw_length=float(enriched["raw_char_length"].median()),
        avg_clean_length=float(enriched["clean_char_length"].mean()),
        median_clean_length=float(enriched["clean_char_length"].median()),
        avg_word_count=float(enriched["word_count"].mean()),
        median_word_count=float(enriched["word_count"].median()),
        url_rows=int(enriched["has_url"].sum()),
        email_rows=int(enriched["has_email"].sum()),
        numeric_rows=int(enriched["has_number"].sum()),
        very_short_rows=int(enriched["is_very_short"].sum()),
    )


def save_class_distribution(class_counts: pd.Series, out_dir: Path) -> pd.DataFrame:
    distribution = class_counts.rename_axis("Topic_group").reset_index(name="ticket_count")
    distribution["percentage"] = (distribution["ticket_count"] / distribution["ticket_count"].sum() * 100).round(2)
    distribution.to_csv(out_dir / "class_distribution.csv", index=False)
    return distribution


def save_charts(enriched: pd.DataFrame, distribution: pd.DataFrame, out_dir: Path) -> None:
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 6))
    sns.barplot(data=distribution, x="ticket_count", y="Topic_group", color="#2563eb")
    plt.title("Support Ticket Class Distribution")
    plt.xlabel("Ticket Count")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.savefig(out_dir / "class_distribution.png", dpi=160)
    plt.close()

    plt.figure(figsize=(12, 6))
    sns.histplot(enriched["word_count"], bins=60, color="#16a34a")
    plt.title("Ticket Word Count Distribution")
    plt.xlabel("Words per Ticket")
    plt.ylabel("Ticket Count")
    plt.tight_layout()
    plt.savefig(out_dir / "ticket_word_count_distribution.png", dpi=160)
    plt.close()

    plt.figure(figsize=(12, 6))
    capped_lengths = enriched["clean_char_length"].clip(upper=enriched["clean_char_length"].quantile(0.99))
    sns.histplot(capped_lengths, bins=60, color="#9333ea")
    plt.title("Cleaned Ticket Character Length Distribution")
    plt.xlabel("Characters per Ticket, capped at 99th percentile")
    plt.ylabel("Ticket Count")
    plt.tight_layout()
    plt.savefig(out_dir / "ticket_clean_length_distribution.png", dpi=160)
    plt.close()

    noise_counts = pd.DataFrame(
        {
            "signal": ["Contains URL", "Contains Email", "Contains Number", "Very Short Text"],
            "ticket_count": [
                int(enriched["has_url"].sum()),
                int(enriched["has_email"].sum()),
                int(enriched["has_number"].sum()),
                int(enriched["is_very_short"].sum()),
            ],
        }
    )
    plt.figure(figsize=(10, 5))
    sns.barplot(data=noise_counts, x="ticket_count", y="signal", color="#f97316")
    plt.title("Potential Text Quality Signals")
    plt.xlabel("Ticket Count")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(out_dir / "text_quality_signals.png", dpi=160)
    plt.close()


def save_examples(enriched: pd.DataFrame, out_dir: Path) -> None:
    sample_size = min(5, len(enriched))
    samples = [
        group.sample(min(sample_size, len(group)), random_state=RANDOM_SEED)
        for _, group in enriched.groupby("Topic_group")
    ]
    examples = pd.concat(samples, ignore_index=True)[["Topic_group", "Document", "clean_document", "word_count"]]
    examples.to_csv(out_dir / "sample_tickets_by_class.csv", index=False)


def save_preprocessed_dataset(enriched: pd.DataFrame, out_dir: Path) -> None:
    columns = ["Document", "clean_document", "Topic_group", "raw_char_length", "clean_char_length", "word_count"]
    enriched[columns].to_csv(out_dir / "preprocessed_ticket_preview.csv", index=False)


def build_recommendations(profile: DatasetProfile) -> list[str]:
    recommendations = []
    if profile.imbalance_ratio >= 3:
        recommendations.append(
            "Class imbalance is meaningful; use stratified splits, macro-F1, weighted-F1, and class weights where supported."
        )
    else:
        recommendations.append("Class balance appears manageable; still report macro-F1 to catch minority-class weakness.")
    if profile.very_short_rows:
        recommendations.append("Very short tickets exist; keep a minimum-text validation step before model inference.")
    if profile.url_rows or profile.email_rows:
        recommendations.append("URLs and emails appear in ticket text; remove or mask them during preprocessing.")
    if profile.avg_word_count < 8:
        recommendations.append("Average ticket length is short; DistilBERT should be trained with careful validation monitoring.")
    else:
        recommendations.append("Ticket length is sufficient for contextual models; cap transformer max length after reviewing percentiles.")
    recommendations.append("Use DistilBERT as the final model and keep TF-IDF baselines for comparison.")
    return recommendations


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    headers = [str(column) for column in df.columns]
    rows = [[str(value) for value in row] for row in df.to_numpy()]
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    row_lines = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, separator, *row_lines])


def write_report(
    profile: DatasetProfile,
    distribution: pd.DataFrame,
    enriched: pd.DataFrame,
    out_dir: Path,
    dataset_path: Path,
) -> None:
    length_percentiles = enriched["word_count"].quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).round(2)
    recommendations = build_recommendations(profile)
    top_classes = dataframe_to_markdown(distribution.head(10))
    percentile_table = length_percentiles.rename("word_count").reset_index()
    percentile_table.columns = ["percentile", "word_count"]
    percentile_markdown = dataframe_to_markdown(percentile_table)

    report = f"""# Phase 1 EDA Report

## Dataset

- Path: `{dataset_path}`
- Rows: {profile.rows:,}
- Columns: {profile.columns}
- Target column: `Topic_group`
- Text column: `Document`

## Data Quality

- Duplicate rows: {profile.duplicate_rows:,}
- Missing documents: {profile.missing_documents:,}
- Missing labels: {profile.missing_labels:,}
- Rows containing URLs: {profile.url_rows:,}
- Rows containing emails: {profile.email_rows:,}
- Rows containing numbers: {profile.numeric_rows:,}
- Very short rows under 3 words: {profile.very_short_rows:,}

## Class Distribution

- Number of classes: {profile.class_count}
- Smallest class size: {profile.min_class_size:,}
- Largest class size: {profile.max_class_size:,}
- Imbalance ratio: {profile.imbalance_ratio}

{top_classes}

## Ticket Length

- Average raw character length: {profile.avg_raw_length:.2f}
- Median raw character length: {profile.median_raw_length:.2f}
- Average cleaned character length: {profile.avg_clean_length:.2f}
- Median cleaned character length: {profile.median_clean_length:.2f}
- Average word count: {profile.avg_word_count:.2f}
- Median word count: {profile.median_word_count:.2f}

{percentile_markdown}

## Preprocessing Pipeline

The preprocessing pipeline in `src/preprocessing/text.py` performs:

- Unicode normalization
- Lowercasing
- URL removal
- Email removal
- Control character normalization
- Technical-token-friendly character filtering
- Whitespace normalization

## Recommendations

{chr(10).join(f"- {item}" for item in recommendations)}

## Generated Artifacts

- `class_distribution.csv`
- `class_distribution.png`
- `ticket_word_count_distribution.png`
- `ticket_clean_length_distribution.png`
- `text_quality_signals.png`
- `sample_tickets_by_class.csv`
- `preprocessed_ticket_preview.csv`
- `dataset_profile.json`
"""
    (out_dir / "eda_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_dataset(args.data)
    enriched = enrich_dataset(df)
    class_counts = enriched["Topic_group"].value_counts()
    profile = build_profile(df, enriched, class_counts)
    distribution = save_class_distribution(class_counts, out_dir)

    save_charts(enriched, distribution, out_dir)
    save_examples(enriched, out_dir)
    save_preprocessed_dataset(enriched, out_dir)
    write_report(profile, distribution, enriched, out_dir, args.data)

    with (out_dir / "dataset_profile.json").open("w", encoding="utf-8") as file:
        json.dump(asdict(profile), file, indent=2)

    print(f"Phase 1 EDA complete. Artifacts written to: {out_dir}")


if __name__ == "__main__":
    np.random.seed(RANDOM_SEED)
    main()

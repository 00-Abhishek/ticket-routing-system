"""Train and evaluate Phase 2 TF-IDF baseline classifiers."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.classification.baselines import (  # noqa: E402
    LABEL_COLUMN,
    RANDOM_SEED,
    build_tfidf_vectorizer,
    evaluate_classifier,
    load_ticket_dataset,
    make_stratified_split,
    save_model_artifacts,
    train_logistic_regression,
    train_naive_bayes,
)

DEFAULT_DATASET = PROJECT_ROOT / "data" / "all_tickets_processed_improved_v3.csv"
DEFAULT_MODELS_DIR = PROJECT_ROOT / "models"
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "model_baselines.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Phase 2 baseline classifiers.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATASET, help="CSV dataset path.")
    parser.add_argument("--models-dir", type=Path, default=DEFAULT_MODELS_DIR, help="Model artifact directory.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Markdown report path.")
    return parser.parse_args()


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(str(value) for value in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def format_score(value: float) -> str:
    return f"{value:.4f}"


def metrics_rows(evaluations: dict[str, dict[str, object]]) -> list[list[str]]:
    rows = []
    for model_name, split_metrics in evaluations.items():
        for split_name, metrics in split_metrics.items():
            rows.append(
                [
                    model_name,
                    split_name,
                    format_score(metrics.accuracy),
                    format_score(metrics.precision_macro),
                    format_score(metrics.recall_macro),
                    format_score(metrics.f1_macro),
                    format_score(metrics.precision_weighted),
                    format_score(metrics.recall_weighted),
                    format_score(metrics.f1_weighted),
                ]
            )
    return rows


def per_class_table(metrics) -> str:
    rows = [
        [
            label,
            format_score(values["precision"]),
            format_score(values["recall"]),
            format_score(values["f1-score"]),
            values["support"],
        ]
        for label, values in metrics.per_class.items()
    ]
    return markdown_table(["Class", "Precision", "Recall", "F1 Score", "Support"], rows)


def confusion_matrix_table(labels: list[str], matrix: list[list[int]]) -> str:
    rows = [[actual_label, *row] for actual_label, row in zip(labels, matrix)]
    return markdown_table(["Actual \\ Predicted", *labels], rows)


def write_report(
    report_path: Path,
    dataset_path: Path,
    labels: list[str],
    split_sizes: dict[str, int],
    evaluations: dict[str, dict[str, object]],
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    summary = markdown_table(
        [
            "Model",
            "Split",
            "Accuracy",
            "Precision Macro",
            "Recall Macro",
            "F1 Macro",
            "Precision Weighted",
            "Recall Weighted",
            "F1 Weighted",
        ],
        metrics_rows(evaluations),
    )

    sections = [
        "# Phase 2 Baseline Model Report",
        "",
        "## Run Details",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Dataset: `{dataset_path}`",
        f"- Random seed: {RANDOM_SEED}",
        "- Split strategy: stratified 80% train, 10% validation, 10% test",
        "- Shared vectorizer: TF-IDF, unigram + bigram, max 50,000 features, sublinear TF",
        "",
        "## Split Sizes",
        "",
        markdown_table(["Split", "Rows"], [[name, count] for name, count in split_sizes.items()]),
        "",
        "## Aggregate Metrics",
        "",
        summary,
        "",
    ]

    for model_name, split_metrics in evaluations.items():
        test_metrics = split_metrics["Test"]
        sections.extend(
            [
                f"## {model_name} Test Per-Class Metrics",
                "",
                per_class_table(test_metrics),
                "",
                f"## {model_name} Test Confusion Matrix",
                "",
                confusion_matrix_table(labels, test_metrics.confusion_matrix),
                "",
            ]
        )

    sections.extend(
        [
            "## Saved Artifacts",
            "",
            "- `models/logistic_regression.pkl`",
            "- `models/tfidf_vectorizer.pkl`",
            "- `models/naive_bayes.pkl`",
            "",
        ]
    )
    report_path.write_text("\n".join(sections), encoding="utf-8")


def main() -> None:
    args = parse_args()
    df = load_ticket_dataset(args.data)
    split = make_stratified_split(df)
    labels = sorted(df[LABEL_COLUMN].unique())

    vectorizer = build_tfidf_vectorizer()
    x_train = vectorizer.fit_transform(split.x_train)
    x_validation = vectorizer.transform(split.x_validation)
    x_test = vectorizer.transform(split.x_test)

    logistic_model = train_logistic_regression(x_train, split.y_train)
    naive_bayes_model = train_naive_bayes(x_train, split.y_train)

    evaluations = {
        "TF-IDF + Logistic Regression": {
            "Validation": evaluate_classifier(logistic_model, x_validation, split.y_validation, labels),
            "Test": evaluate_classifier(logistic_model, x_test, split.y_test, labels),
        },
        "TF-IDF + Multinomial Naive Bayes": {
            "Validation": evaluate_classifier(naive_bayes_model, x_validation, split.y_validation, labels),
            "Test": evaluate_classifier(naive_bayes_model, x_test, split.y_test, labels),
        },
    }
    save_model_artifacts(vectorizer, logistic_model, naive_bayes_model, args.models_dir)
    write_report(
        report_path=args.report,
        dataset_path=args.data,
        labels=labels,
        split_sizes={
            "Train": len(split.x_train),
            "Validation": len(split.x_validation),
            "Test": len(split.x_test),
        },
        evaluations=evaluations,
    )

    metrics_json = {
        model_name: {
            split_name: {
                "accuracy": metrics.accuracy,
                "precision_macro": metrics.precision_macro,
                "recall_macro": metrics.recall_macro,
                "f1_macro": metrics.f1_macro,
                "precision_weighted": metrics.precision_weighted,
                "recall_weighted": metrics.recall_weighted,
                "f1_weighted": metrics.f1_weighted,
            }
            for split_name, metrics in split_metrics.items()
        }
        for model_name, split_metrics in evaluations.items()
    }
    print(json.dumps(metrics_json, indent=2))
    print(f"Saved models to: {args.models_dir}")
    print(f"Saved report to: {args.report}")


if __name__ == "__main__":
    main()


"""Train and evaluate the Phase 4 DistilBERT classifier."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from transformers import (  # noqa: E402
    EarlyStoppingCallback,
    DistilBertForSequenceClassification,
    DistilBertTokenizerFast,
    Trainer,
    TrainingArguments,
)

from src.classification.baselines import (  # noqa: E402
    LABEL_COLUMN,
    load_ticket_dataset,
    make_stratified_split,
)
from src.classification.distilbert import (  # noqa: E402
    MODEL_NAME,
    RANDOM_SEED,
    build_encoded_splits,
    compute_trainer_metrics,
    evaluate_predictions,
    seed_everything,
    write_label_mapping,
)

DEFAULT_DATASET = PROJECT_ROOT / "data" / "all_tickets_processed_improved_v3.csv"
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models" / "distilbert"
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "model_distilbert.md"
DEFAULT_BASELINE_REPORT = PROJECT_ROOT / "reports" / "model_baselines.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Phase 4 DistilBERT classifier.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATASET, help="CSV dataset path.")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR, help="Model output directory.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Markdown report path.")
    parser.add_argument(
        "--baseline-report",
        type=Path,
        default=DEFAULT_BASELINE_REPORT,
        help="Phase 2 baseline report path for comparison.",
    )
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=float, default=3)
    parser.add_argument("--early-stopping-patience", type=int, default=2)
    return parser.parse_args()


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(str(value) for value in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def format_score(value: float) -> str:
    return f"{value:.4f}"


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


def baseline_comparison_section(baseline_report: Path, distilbert_metrics) -> list[str]:
    rows = [
        [
            "DistilBERT base uncased",
            format_score(distilbert_metrics.accuracy),
            format_score(distilbert_metrics.f1_macro),
            format_score(distilbert_metrics.f1_weighted),
        ],
    ]
    if baseline_report.exists():
        text = baseline_report.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("| TF-IDF + Logistic Regression | Test |"):
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                rows.append([cells[0], cells[2], cells[5], cells[8]])
            if line.startswith("| TF-IDF + Multinomial Naive Bayes | Test |"):
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                rows.append([cells[0], cells[2], cells[5], cells[8]])
    return [
        "## Comparison With Phase 2 Baselines",
        "",
        markdown_table(["Model", "Test Accuracy", "Test Macro F1", "Test Weighted F1"], rows),
        "",
    ]


def write_report(
    report_path: Path,
    dataset_path: Path,
    model_dir: Path,
    labels: list[str],
    split_sizes: dict[str, int],
    validation_metrics,
    test_metrics,
    baseline_report: Path,
    max_length: int,
    batch_size: int,
    epochs: float,
    device_name: str,
    mixed_precision: bool,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    sections = [
        "# Phase 4 DistilBERT Model Report",
        "",
        "## Run Details",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Dataset: `{dataset_path}`",
        f"- Model: `{MODEL_NAME}`",
        f"- Saved model directory: `{model_dir}`",
        f"- Random seed: {RANDOM_SEED}",
        "- Split strategy: stratified 80% train, 10% validation, 10% test",
        f"- Device: {device_name}",
        f"- Mixed precision: {'enabled' if mixed_precision else 'disabled'}",
        f"- Max length: {max_length}",
        f"- Batch size: {batch_size}",
        f"- Epochs requested: {epochs:g}",
        "- Early stopping: enabled, monitored validation macro F1",
        "- Checkpointing: enabled, best validation macro F1 restored",
        "",
        "## Split Sizes",
        "",
        markdown_table(["Split", "Rows"], [[name, count] for name, count in split_sizes.items()]),
        "",
        "## Aggregate Metrics",
        "",
        markdown_table(
            [
                "Split",
                "Accuracy",
                "Precision Macro",
                "Recall Macro",
                "F1 Macro",
                "Precision Weighted",
                "Recall Weighted",
                "F1 Weighted",
            ],
            [
                [
                    "Validation",
                    format_score(validation_metrics.accuracy),
                    format_score(validation_metrics.precision_macro),
                    format_score(validation_metrics.recall_macro),
                    format_score(validation_metrics.f1_macro),
                    format_score(validation_metrics.precision_weighted),
                    format_score(validation_metrics.recall_weighted),
                    format_score(validation_metrics.f1_weighted),
                ],
                [
                    "Test",
                    format_score(test_metrics.accuracy),
                    format_score(test_metrics.precision_macro),
                    format_score(test_metrics.recall_macro),
                    format_score(test_metrics.f1_macro),
                    format_score(test_metrics.precision_weighted),
                    format_score(test_metrics.recall_weighted),
                    format_score(test_metrics.f1_weighted),
                ],
            ],
        ),
        "",
        "## Test Per-Class Metrics",
        "",
        per_class_table(test_metrics),
        "",
        "## Test Confusion Matrix",
        "",
        confusion_matrix_table(labels, test_metrics.confusion_matrix),
        "",
        *baseline_comparison_section(baseline_report, test_metrics),
        "## Saved Artifacts",
        "",
        "- `models/distilbert/`",
        "- `models/distilbert/checkpoint-*`",
        "- `models/distilbert/label_mapping.json`",
        "",
    ]
    report_path.write_text("\n".join(sections), encoding="utf-8")


def main() -> None:
    args = parse_args()
    seed_everything(RANDOM_SEED)

    df = load_ticket_dataset(args.data)
    split = make_stratified_split(df)
    encoded = build_encoded_splits(split=split, max_length=args.max_length)

    cuda_available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"
    mixed_precision = bool(cuda_available)

    model = DistilBertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(encoded.labels),
        id2label=encoded.id2label,
        label2id=encoded.label2id,
    )

    args.model_dir.mkdir(parents=True, exist_ok=True)
    steps_per_epoch = math.ceil(len(encoded.train_dataset) / args.batch_size)
    warmup_steps = int(steps_per_epoch * args.epochs * 0.1)
    training_args = TrainingArguments(
        output_dir=str(args.model_dir),
        seed=RANDOM_SEED,
        data_seed=RANDOM_SEED,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_steps=warmup_steps,
        fp16=mixed_precision,
        logging_steps=100,
        save_total_limit=2,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=encoded.train_dataset,
        eval_dataset=encoded.validation_dataset,
        compute_metrics=compute_trainer_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=args.early_stopping_patience)],
    )

    trainer.train()
    trainer.save_model(str(args.model_dir))
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "[PAD]"})
    tokenizer.save_pretrained(str(args.model_dir))
    write_label_mapping(args.model_dir, encoded.label2id, encoded.id2label)

    validation_prediction = trainer.predict(encoded.validation_dataset)
    test_prediction = trainer.predict(encoded.test_dataset)
    validation_metrics = evaluate_predictions(
        validation_prediction.predictions,
        encoded.validation_dataset.labels,
        encoded.labels,
    )
    test_metrics = evaluate_predictions(
        test_prediction.predictions,
        encoded.test_dataset.labels,
        encoded.labels,
    )

    write_report(
        report_path=args.report,
        dataset_path=args.data,
        model_dir=args.model_dir,
        labels=encoded.labels,
        split_sizes={
            "Train": len(split.x_train),
            "Validation": len(split.x_validation),
            "Test": len(split.x_test),
        },
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
        baseline_report=args.baseline_report,
        max_length=args.max_length,
        batch_size=args.batch_size,
        epochs=args.epochs,
        device_name=device_name,
        mixed_precision=mixed_precision,
    )

    print(
        json.dumps(
            {
                "validation": {
                    "accuracy": validation_metrics.accuracy,
                    "precision_macro": validation_metrics.precision_macro,
                    "recall_macro": validation_metrics.recall_macro,
                    "f1_macro": validation_metrics.f1_macro,
                    "f1_weighted": validation_metrics.f1_weighted,
                },
                "test": {
                    "accuracy": test_metrics.accuracy,
                    "precision_macro": test_metrics.precision_macro,
                    "recall_macro": test_metrics.recall_macro,
                    "f1_macro": test_metrics.f1_macro,
                    "f1_weighted": test_metrics.f1_weighted,
                },
                "device": device_name,
                "mixed_precision": mixed_precision,
            },
            indent=2,
        )
    )
    print(f"Saved DistilBERT model to: {args.model_dir}")
    print(f"Saved report to: {args.report}")


if __name__ == "__main__":
    main()

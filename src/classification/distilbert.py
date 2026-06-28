"""DistilBERT training utilities for support ticket classification."""

from __future__ import annotations

import random
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from torch.utils.data import Dataset
from transformers import DistilBertTokenizerFast, EvalPrediction, set_seed

from src.classification.baselines import DatasetSplit, ModelEvaluation

MODEL_NAME = "distilbert-base-uncased"
RANDOM_SEED = 42


@dataclass(frozen=True)
class EncodedSplits:
    """Tokenized datasets and label metadata for transformer training."""

    train_dataset: "TicketTextDataset"
    validation_dataset: "TicketTextDataset"
    test_dataset: "TicketTextDataset"
    labels: list[str]
    label2id: dict[str, int]
    id2label: dict[int, str]


class TicketTextDataset(Dataset):
    """Torch dataset wrapping tokenized ticket text and integer labels."""

    def __init__(self, encodings: dict[str, list[list[int]]], labels: list[int]) -> None:
        self.encodings = encodings
        self.labels = labels

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        item = {key: torch.tensor(value[index]) for key, value in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[index], dtype=torch.long)
        return item


def seed_everything(seed: int = RANDOM_SEED) -> None:
    """Seed Python, NumPy, PyTorch, CUDA, and Transformers."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    set_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def build_encoded_splits(
    split: DatasetSplit,
    max_length: int = 128,
    model_name: str = MODEL_NAME,
) -> EncodedSplits:
    """Tokenize stratified train, validation, and test splits."""
    labels = sorted(pd.concat([split.y_train, split.y_validation, split.y_test]).unique())
    label2id = {label: index for index, label in enumerate(labels)}
    id2label = {index: label for label, index in label2id.items()}

    tokenizer = DistilBertTokenizerFast.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "[PAD]"})

    def encode(texts: pd.Series) -> dict[str, list[list[int]]]:
        return tokenizer(
            texts.tolist(),
            truncation=True,
            padding=True,
            max_length=max_length,
        )

    return EncodedSplits(
        train_dataset=TicketTextDataset(encode(split.x_train), [label2id[label] for label in split.y_train]),
        validation_dataset=TicketTextDataset(
            encode(split.x_validation),
            [label2id[label] for label in split.y_validation],
        ),
        test_dataset=TicketTextDataset(encode(split.x_test), [label2id[label] for label in split.y_test]),
        labels=labels,
        label2id=label2id,
        id2label=id2label,
    )


def compute_trainer_metrics(prediction: EvalPrediction) -> dict[str, float]:
    """Compute metrics used by Hugging Face Trainer during validation."""
    logits = prediction.predictions
    y_pred = np.argmax(logits, axis=1)
    y_true = prediction.label_ids
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="macro",
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision),
        "recall_macro": float(recall),
        "f1_macro": float(f1),
    }


def evaluate_predictions(logits: np.ndarray, y_true: list[int], labels: list[str]) -> ModelEvaluation:
    """Evaluate DistilBERT logits with aggregate, per-class, and confusion metrics."""
    y_pred = np.argmax(logits, axis=1)
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="macro",
        zero_division=0,
    )
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0,
    )
    label_ids = list(range(len(labels)))
    report = classification_report(
        y_true,
        y_pred,
        labels=label_ids,
        target_names=labels,
        output_dict=True,
        zero_division=0,
    )
    per_class = {
        label: {
            "precision": float(report[label]["precision"]),
            "recall": float(report[label]["recall"]),
            "f1-score": float(report[label]["f1-score"]),
            "support": int(report[label]["support"]),
        }
        for label in labels
    }
    matrix = confusion_matrix(y_true, y_pred, labels=label_ids)
    return ModelEvaluation(
        accuracy=float(accuracy_score(y_true, y_pred)),
        precision_macro=float(precision_macro),
        recall_macro=float(recall_macro),
        f1_macro=float(f1_macro),
        precision_weighted=float(precision_weighted),
        recall_weighted=float(recall_weighted),
        f1_weighted=float(f1_weighted),
        per_class=per_class,
        confusion_matrix=matrix.astype(int).tolist(),
    )


def write_label_mapping(model_dir: Path, label2id: dict[str, int], id2label: dict[int, str]) -> None:
    """Save label mappings next to the trained model."""
    model_dir.mkdir(parents=True, exist_ok=True)
    mapping = {
        "label2id": label2id,
        "id2label": {str(key): value for key, value in id2label.items()},
    }
    (model_dir / "label_mapping.json").write_text(json.dumps(mapping, indent=2), encoding="utf-8")

"""Baseline TF-IDF classifiers for support ticket classification."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from src.preprocessing.text import normalize_ticket_series

RANDOM_SEED = 42
TEXT_COLUMN = "Document"
LABEL_COLUMN = "Topic_group"
REQUIRED_COLUMNS = (TEXT_COLUMN, LABEL_COLUMN)


@dataclass(frozen=True)
class DatasetSplit:
    """Stratified train, validation, and test split."""

    x_train: pd.Series
    x_validation: pd.Series
    x_test: pd.Series
    y_train: pd.Series
    y_validation: pd.Series
    y_test: pd.Series


@dataclass(frozen=True)
class ModelEvaluation:
    """Classification metrics for one split."""

    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    precision_weighted: float
    recall_weighted: float
    f1_weighted: float
    per_class: dict[str, dict[str, float]]
    confusion_matrix: list[list[int]]


def load_ticket_dataset(path: Path) -> pd.DataFrame:
    """Load and validate the support ticket dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    cleaned = df.loc[:, list(REQUIRED_COLUMNS)].dropna().copy()
    cleaned[TEXT_COLUMN] = normalize_ticket_series(cleaned[TEXT_COLUMN])
    cleaned = cleaned[cleaned[TEXT_COLUMN].str.len() > 0]
    cleaned[LABEL_COLUMN] = cleaned[LABEL_COLUMN].astype(str)
    if cleaned[LABEL_COLUMN].nunique() < 2:
        raise ValueError("At least two classes are required to train baseline classifiers.")
    return cleaned


def make_stratified_split(
    df: pd.DataFrame,
    train_size: float = 0.80,
    validation_size: float = 0.10,
    test_size: float = 0.10,
    random_state: int = RANDOM_SEED,
) -> DatasetSplit:
    """Create an 80/10/10 stratified split by default."""
    if not np.isclose(train_size + validation_size + test_size, 1.0):
        raise ValueError("train_size, validation_size, and test_size must sum to 1.0")

    x = df[TEXT_COLUMN]
    y = df[LABEL_COLUMN]
    x_train, x_temp, y_train, y_temp = train_test_split(
        x,
        y,
        train_size=train_size,
        random_state=random_state,
        stratify=y,
    )
    relative_test_size = test_size / (validation_size + test_size)
    x_validation, x_test, y_validation, y_test = train_test_split(
        x_temp,
        y_temp,
        test_size=relative_test_size,
        random_state=random_state,
        stratify=y_temp,
    )
    return DatasetSplit(
        x_train=x_train.reset_index(drop=True),
        x_validation=x_validation.reset_index(drop=True),
        x_test=x_test.reset_index(drop=True),
        y_train=y_train.reset_index(drop=True),
        y_validation=y_validation.reset_index(drop=True),
        y_test=y_test.reset_index(drop=True),
    )


def build_tfidf_vectorizer() -> TfidfVectorizer:
    """Create the shared TF-IDF vectorizer for baseline models."""
    return TfidfVectorizer(
        max_features=50_000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
    )


def train_logistic_regression(x_train, y_train) -> LogisticRegression:
    """Train a balanced logistic regression classifier."""
    model = LogisticRegression(
        C=2.0,
        class_weight="balanced",
        max_iter=1_000,
        random_state=RANDOM_SEED,
    )
    model.fit(x_train, y_train)
    return model


def train_naive_bayes(x_train, y_train) -> MultinomialNB:
    """Train a Multinomial Naive Bayes classifier."""
    model = MultinomialNB(alpha=0.5)
    model.fit(x_train, y_train)
    return model


def evaluate_classifier(model, x_features, y_true: Iterable[str], labels: list[str]) -> ModelEvaluation:
    """Evaluate a fitted classifier and return aggregate and per-class metrics."""
    y_pred = model.predict(x_features)
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
    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
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
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
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


def save_model_artifacts(
    vectorizer: TfidfVectorizer,
    logistic_model: LogisticRegression,
    naive_bayes_model: MultinomialNB,
    models_dir: Path,
) -> None:
    """Persist trained baseline models and the shared vectorizer."""
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(logistic_model, models_dir / "logistic_regression.pkl")
    joblib.dump(vectorizer, models_dir / "tfidf_vectorizer.pkl")
    joblib.dump(naive_bayes_model, models_dir / "naive_bayes.pkl")

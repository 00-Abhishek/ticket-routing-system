import unittest

import pandas as pd

from src.classification.baselines import (
    LABEL_COLUMN,
    TEXT_COLUMN,
    build_tfidf_vectorizer,
    evaluate_classifier,
    make_stratified_split,
    train_naive_bayes,
)


class BaselineTrainingTest(unittest.TestCase):
    def sample_frame(self) -> pd.DataFrame:
        rows = []
        labels = ["Hardware", "Access", "Storage"]
        for label in labels:
            for index in range(10):
                rows.append(
                    {
                        TEXT_COLUMN: f"{label.lower()} ticket example {index} needs support",
                        LABEL_COLUMN: label,
                    }
                )
        return pd.DataFrame(rows)

    def test_stratified_split_preserves_all_classes(self) -> None:
        df = self.sample_frame()

        split = make_stratified_split(df)

        self.assertEqual(len(split.x_train), 24)
        self.assertEqual(len(split.x_validation), 3)
        self.assertEqual(len(split.x_test), 3)
        self.assertEqual(set(split.y_train), {"Hardware", "Access", "Storage"})
        self.assertEqual(set(split.y_validation), {"Hardware", "Access", "Storage"})
        self.assertEqual(set(split.y_test), {"Hardware", "Access", "Storage"})

    def test_evaluate_classifier_returns_per_class_metrics(self) -> None:
        df = self.sample_frame()
        split = make_stratified_split(df)
        vectorizer = build_tfidf_vectorizer()
        x_train = vectorizer.fit_transform(split.x_train)
        x_test = vectorizer.transform(split.x_test)
        model = train_naive_bayes(x_train, split.y_train)

        metrics = evaluate_classifier(model, x_test, split.y_test, sorted(df[LABEL_COLUMN].unique()))

        self.assertGreaterEqual(metrics.accuracy, 0.0)
        self.assertEqual(set(metrics.per_class), {"Hardware", "Access", "Storage"})
        self.assertEqual(len(metrics.confusion_matrix), 3)


if __name__ == "__main__":
    unittest.main()


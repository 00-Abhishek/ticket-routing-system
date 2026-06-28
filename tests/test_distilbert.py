import unittest

import numpy as np

from src.classification.distilbert import evaluate_predictions, seed_everything


class DistilBertMetricsTest(unittest.TestCase):
    def test_evaluate_predictions_builds_per_class_metrics(self) -> None:
        labels = ["Access", "Hardware"]
        logits = np.array([[4.0, 1.0], [0.5, 3.0], [2.0, 1.0]])
        y_true = [0, 1, 1]

        metrics = evaluate_predictions(logits, y_true, labels)

        self.assertEqual(len(metrics.confusion_matrix), 2)
        self.assertEqual(set(metrics.per_class), set(labels))
        self.assertGreaterEqual(metrics.accuracy, 0.0)

    def test_seed_everything_runs(self) -> None:
        seed_everything(42)


if __name__ == "__main__":
    unittest.main()


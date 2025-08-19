"""
IMPORTANT:
- This is a shared file between OrcaLib and the Orca SDK.
- Please ensure that it does not have any dependencies on the OrcaLib code.
- Make sure to edit this file in orcalib/shared and NOT in orca_sdk, since it will be overwritten there.
"""

from typing import Literal

import numpy as np
import pytest
import sklearn.metrics

from .metrics import (
    calculate_classification_metrics,
    calculate_pr_curve,
    calculate_regression_metrics,
    calculate_roc_curve,
    softmax,
)


def test_binary_metrics():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.9, 0.8, 0.3, 0.2])

    metrics = calculate_classification_metrics(y_true, y_score)

    assert metrics.accuracy == 0.8
    assert metrics.f1_score == 0.8
    assert metrics.roc_auc is not None
    assert metrics.roc_auc > 0.8
    assert metrics.roc_auc < 1.0
    assert metrics.pr_auc is not None
    assert metrics.pr_auc > 0.8
    assert metrics.pr_auc < 1.0
    assert metrics.loss is not None
    assert metrics.loss > 0.0


def test_multiclass_metrics_with_2_classes():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([[0.9, 0.1], [0.1, 0.9], [0.2, 0.8], [0.7, 0.3], [0.8, 0.2]])

    metrics = calculate_classification_metrics(y_true, y_score)

    assert metrics.accuracy == 0.8
    assert metrics.f1_score == 0.8
    assert metrics.roc_auc is not None
    assert metrics.roc_auc > 0.8
    assert metrics.roc_auc < 1.0
    assert metrics.pr_auc is not None
    assert metrics.pr_auc > 0.8
    assert metrics.pr_auc < 1.0
    assert metrics.loss is not None
    assert metrics.loss > 0.0


@pytest.mark.parametrize(
    "average, multiclass",
    [("micro", "ovr"), ("macro", "ovr"), ("weighted", "ovr"), ("micro", "ovo"), ("macro", "ovo"), ("weighted", "ovo")],
)
def test_multiclass_metrics_with_3_classes(
    average: Literal["micro", "macro", "weighted"], multiclass: Literal["ovr", "ovo"]
):
    y_true = np.array([0, 1, 1, 0, 2])
    y_score = np.array([[0.9, 0.1, 0.0], [0.1, 0.9, 0.0], [0.2, 0.8, 0.0], [0.7, 0.3, 0.0], [0.0, 0.0, 1.0]])

    metrics = calculate_classification_metrics(y_true, y_score, average=average, multi_class=multiclass)

    assert metrics.accuracy == 1.0
    assert metrics.f1_score == 1.0
    assert metrics.roc_auc is not None
    assert metrics.roc_auc > 0.8
    assert metrics.pr_auc is None
    assert metrics.loss is not None
    assert metrics.loss > 0.0


def test_does_not_modify_logits_unless_necessary():
    logits = np.array([[0.1, 0.9], [0.2, 0.8], [0.7, 0.3], [0.8, 0.2]])
    expected_labels = [0, 1, 0, 1]
    assert calculate_classification_metrics(expected_labels, logits).loss == sklearn.metrics.log_loss(
        expected_labels, logits
    )


def test_normalizes_logits_if_necessary():
    logits = np.array([[1.2, 3.9], [1.2, 5.8], [1.2, 2.7], [1.2, 1.3]])
    expected_labels = [0, 1, 0, 1]
    assert calculate_classification_metrics(expected_labels, logits).loss == sklearn.metrics.log_loss(
        expected_labels, logits / logits.sum(axis=1, keepdims=True)
    )


def test_softmaxes_logits_if_necessary():
    logits = np.array([[-1.2, 3.9], [1.2, -5.8], [1.2, 2.7], [1.2, 1.3]])
    expected_labels = [0, 1, 0, 1]
    assert calculate_classification_metrics(expected_labels, logits).loss == sklearn.metrics.log_loss(
        expected_labels, softmax(logits)
    )


def test_precision_recall_curve():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.9, 0.8, 0.6, 0.2])

    pr_curve = calculate_pr_curve(y_true, y_score)

    assert len(pr_curve["precisions"]) == len(pr_curve["recalls"]) == len(pr_curve["thresholds"]) == 6
    assert np.allclose(pr_curve["precisions"][0], 0.6)
    assert np.allclose(pr_curve["recalls"][0], 1.0)
    assert np.allclose(pr_curve["precisions"][-1], 1.0)
    assert np.allclose(pr_curve["recalls"][-1], 0.0)

    # test that thresholds are sorted
    assert np.all(np.diff(pr_curve["thresholds"]) >= 0)


def test_roc_curve():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.9, 0.8, 0.6, 0.2])

    roc_curve = calculate_roc_curve(y_true, y_score)

    assert (
        len(roc_curve["false_positive_rates"])
        == len(roc_curve["true_positive_rates"])
        == len(roc_curve["thresholds"])
        == 6
    )
    assert roc_curve["false_positive_rates"][0] == 1.0
    assert roc_curve["true_positive_rates"][0] == 1.0
    assert roc_curve["false_positive_rates"][-1] == 0.0
    assert roc_curve["true_positive_rates"][-1] == 0.0

    # test that thresholds are sorted
    assert np.all(np.diff(roc_curve["thresholds"]) >= 0)


def test_precision_recall_curve_max_length():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.9, 0.8, 0.6, 0.2])

    pr_curve = calculate_pr_curve(y_true, y_score, max_length=5)
    assert len(pr_curve["precisions"]) == len(pr_curve["recalls"]) == len(pr_curve["thresholds"]) == 5

    assert np.allclose(pr_curve["precisions"][0], 0.6)
    assert np.allclose(pr_curve["recalls"][0], 1.0)
    assert np.allclose(pr_curve["precisions"][-1], 1.0)
    assert np.allclose(pr_curve["recalls"][-1], 0.0)

    # test that thresholds are sorted
    assert np.all(np.diff(pr_curve["thresholds"]) >= 0)


def test_roc_curve_max_length():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.9, 0.8, 0.6, 0.2])

    roc_curve = calculate_roc_curve(y_true, y_score, max_length=5)
    assert (
        len(roc_curve["false_positive_rates"])
        == len(roc_curve["true_positive_rates"])
        == len(roc_curve["thresholds"])
        == 5
    )
    assert np.allclose(roc_curve["false_positive_rates"][0], 1.0)
    assert np.allclose(roc_curve["true_positive_rates"][0], 1.0)
    assert np.allclose(roc_curve["false_positive_rates"][-1], 0.0)
    assert np.allclose(roc_curve["true_positive_rates"][-1], 0.0)

    # test that thresholds are sorted
    assert np.all(np.diff(roc_curve["thresholds"]) >= 0)


# Regression Metrics Tests


def test_perfect_regression_predictions():
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
    y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)

    metrics = calculate_regression_metrics(y_true, y_pred)

    assert metrics.mse == 0.0
    assert metrics.rmse == 0.0
    assert metrics.mae == 0.0
    assert metrics.r2 == 1.0
    assert metrics.explained_variance == 1.0
    assert metrics.loss == 0.0
    assert metrics.anomaly_score_mean is None
    assert metrics.anomaly_score_median is None
    assert metrics.anomaly_score_variance is None


def test_basic_regression_metrics():
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
    y_pred = np.array([1.1, 1.9, 3.2, 3.8, 5.1], dtype=np.float32)

    metrics = calculate_regression_metrics(y_true, y_pred)

    # Check that all metrics are reasonable
    assert metrics.mse > 0.0
    assert metrics.rmse == pytest.approx(np.sqrt(metrics.mse))
    assert metrics.mae > 0.0
    assert 0.0 <= metrics.r2 <= 1.0
    assert 0.0 <= metrics.explained_variance <= 1.0
    assert metrics.loss == metrics.mse

    # Check specific values based on the data
    expected_mse = np.mean((y_true - y_pred) ** 2)
    assert metrics.mse == pytest.approx(expected_mse)

    expected_mae = np.mean(np.abs(y_true - y_pred))
    assert metrics.mae == pytest.approx(expected_mae)


def test_regression_metrics_with_anomaly_scores():
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
    y_pred = np.array([1.1, 1.9, 3.2, 3.8, 5.1], dtype=np.float32)
    anomaly_scores = [0.1, 0.2, 0.15, 0.3, 0.25]

    metrics = calculate_regression_metrics(y_true, y_pred, anomaly_scores)

    assert metrics.anomaly_score_mean == pytest.approx(np.mean(anomaly_scores))
    assert metrics.anomaly_score_median == pytest.approx(np.median(anomaly_scores))
    assert metrics.anomaly_score_variance == pytest.approx(np.var(anomaly_scores))

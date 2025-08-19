"""
This module contains metrics for usage with the Hugging Face Trainer.

IMPORTANT:
- This is a shared file between OrcaLib and the Orca SDK.
- Please ensure that it does not have any dependencies on the OrcaLib code.
- Make sure to edit this file in orcalib/shared and NOT in orca_sdk, since it will be overwritten there.

"""

from dataclasses import dataclass
from typing import Any, Literal, TypedDict, cast

import numpy as np
import sklearn.metrics
from numpy.typing import NDArray


# we don't want to depend on scipy or torch in orca_sdk
def softmax(logits: np.ndarray, axis: int = -1) -> np.ndarray:
    shifted = logits - np.max(logits, axis=axis, keepdims=True)
    exps = np.exp(shifted)
    return exps / np.sum(exps, axis=axis, keepdims=True)


# We don't want to depend on transformers just for the eval_pred type in orca_sdk
def transform_eval_pred(eval_pred: Any) -> tuple[NDArray, NDArray[np.float32]]:
    # convert results from Trainer compute_metrics param for use in calculate_classification_metrics
    logits, references = eval_pred  # transformers.trainer_utils.EvalPrediction
    if isinstance(logits, tuple):
        logits = logits[0]
    if not isinstance(logits, np.ndarray):
        raise ValueError("Logits must be a numpy array")
    if not isinstance(references, np.ndarray):
        raise ValueError(
            "Multiple label columns found, use the `label_names` training argument to specify which one to use"
        )

    return (references, logits)


class PRCurve(TypedDict):
    thresholds: list[float]
    precisions: list[float]
    recalls: list[float]


def calculate_pr_curve(
    references: NDArray[np.int64],
    probabilities: NDArray[np.float32],
    max_length: int = 100,
) -> PRCurve:
    if probabilities.ndim == 1:
        probabilities_slice = probabilities
    elif probabilities.ndim == 2:
        probabilities_slice = probabilities[:, 1]
    else:
        raise ValueError("Probabilities must be 1 or 2 dimensional")

    if len(probabilities_slice) != len(references):
        raise ValueError("Probabilities and references must have the same length")

    precisions, recalls, thresholds = sklearn.metrics.precision_recall_curve(references, probabilities_slice)

    # Convert all arrays to float32 immediately after getting them
    precisions = precisions.astype(np.float32)
    recalls = recalls.astype(np.float32)
    thresholds = thresholds.astype(np.float32)

    # Concatenate with 0 to include the lowest threshold
    thresholds = np.concatenate(([0], thresholds))

    # Sort by threshold
    sorted_indices = np.argsort(thresholds)
    thresholds = thresholds[sorted_indices]
    precisions = precisions[sorted_indices]
    recalls = recalls[sorted_indices]

    if len(precisions) > max_length:
        new_thresholds = np.linspace(0, 1, max_length, dtype=np.float32)
        new_precisions = np.interp(new_thresholds, thresholds, precisions)
        new_recalls = np.interp(new_thresholds, thresholds, recalls)
        thresholds = new_thresholds
        precisions = new_precisions
        recalls = new_recalls

    return PRCurve(
        thresholds=cast(list[float], thresholds.tolist()),
        precisions=cast(list[float], precisions.tolist()),
        recalls=cast(list[float], recalls.tolist()),
    )


class ROCCurve(TypedDict):
    thresholds: list[float]
    false_positive_rates: list[float]
    true_positive_rates: list[float]


def calculate_roc_curve(
    references: NDArray[np.int64],
    probabilities: NDArray[np.float32],
    max_length: int = 100,
) -> ROCCurve:
    if probabilities.ndim == 1:
        probabilities_slice = probabilities
    elif probabilities.ndim == 2:
        probabilities_slice = probabilities[:, 1]
    else:
        raise ValueError("Probabilities must be 1 or 2 dimensional")

    if len(probabilities_slice) != len(references):
        raise ValueError("Probabilities and references must have the same length")

    # Convert probabilities to float32 before calling sklearn_roc_curve
    probabilities_slice = probabilities_slice.astype(np.float32)
    fpr, tpr, thresholds = sklearn.metrics.roc_curve(references, probabilities_slice)

    # Convert all arrays to float32 immediately after getting them
    fpr = fpr.astype(np.float32)
    tpr = tpr.astype(np.float32)
    thresholds = thresholds.astype(np.float32)

    # We set the first threshold to 1.0 instead of inf for reasonable values in interpolation
    thresholds[0] = 1.0

    # Sort by threshold
    sorted_indices = np.argsort(thresholds)
    thresholds = thresholds[sorted_indices]
    fpr = fpr[sorted_indices]
    tpr = tpr[sorted_indices]

    if len(fpr) > max_length:
        new_thresholds = np.linspace(0, 1, max_length, dtype=np.float32)
        new_fpr = np.interp(new_thresholds, thresholds, fpr)
        new_tpr = np.interp(new_thresholds, thresholds, tpr)
        thresholds = new_thresholds
        fpr = new_fpr
        tpr = new_tpr

    return ROCCurve(
        false_positive_rates=cast(list[float], fpr.tolist()),
        true_positive_rates=cast(list[float], tpr.tolist()),
        thresholds=cast(list[float], thresholds.tolist()),
    )


@dataclass
class ClassificationMetrics:
    f1_score: float
    """F1 score of the predictions"""

    accuracy: float
    """Accuracy of the predictions"""

    loss: float
    """Cross-entropy loss of the logits"""

    anomaly_score_mean: float | None = None
    """Mean of anomaly scores across the dataset"""

    anomaly_score_median: float | None = None
    """Median of anomaly scores across the dataset"""

    anomaly_score_variance: float | None = None
    """Variance of anomaly scores across the dataset"""

    roc_auc: float | None = None
    """Receiver operating characteristic area under the curve"""

    pr_auc: float | None = None
    """Average precision (area under the curve of the precision-recall curve)"""

    pr_curve: PRCurve | None = None
    """Precision-recall curve"""

    roc_curve: ROCCurve | None = None
    """Receiver operating characteristic curve"""

    def __repr__(self) -> str:
        return (
            "ClassificationMetrics({\n"
            + f"    accuracy: {self.accuracy:.4f},\n"
            + f"    f1_score: {self.f1_score:.4f},\n"
            + (f"    roc_auc: {self.roc_auc:.4f},\n" if self.roc_auc else "")
            + (f"    pr_auc: {self.pr_auc:.4f},\n" if self.pr_auc else "")
            + (
                f"    anomaly_score: {self.anomaly_score_mean:.4f} ± {self.anomaly_score_variance:.4f},\n"
                if self.anomaly_score_mean
                else ""
            )
            + "})"
        )


def calculate_classification_metrics(
    expected_labels: list[int] | NDArray[np.int64],
    logits: list[list[float]] | list[NDArray[np.float32]] | NDArray[np.float32],
    anomaly_scores: list[float] | None = None,
    average: Literal["micro", "macro", "weighted", "binary"] | None = None,
    multi_class: Literal["ovr", "ovo"] = "ovr",
    include_curves: bool = False,
) -> ClassificationMetrics:
    references = np.array(expected_labels)

    logits = np.array(logits)
    if logits.ndim == 1:
        if (logits > 1).any() or (logits < 0).any():
            raise ValueError("Logits must be between 0 and 1 for binary classification")
        # convert 1D probabilities (binary) to 2D logits
        logits = np.column_stack([1 - logits, logits])
        probabilities = logits  # no need to convert to probabilities
    elif logits.ndim == 2:
        if logits.shape[1] < 2:
            raise ValueError("Use a different metric function for regression tasks")
        if not (logits > 0).all():
            # convert logits to probabilities with softmax if necessary
            probabilities = softmax(logits)
        elif not np.allclose(logits.sum(-1, keepdims=True), 1.0):
            # convert logits to probabilities through normalization if necessary
            probabilities = logits / logits.sum(-1, keepdims=True)
        else:
            probabilities = logits
    else:
        raise ValueError("Logits must be 1 or 2 dimensional")

    predictions = np.argmax(probabilities, axis=-1)

    num_classes_references = len(set(references))
    num_classes_predictions = len(set(predictions))

    if average is None:
        average = "binary" if num_classes_references == 2 else "weighted"

    anomaly_score_mean = float(np.mean(anomaly_scores)) if anomaly_scores else None
    anomaly_score_median = float(np.median(anomaly_scores)) if anomaly_scores else None
    anomaly_score_variance = float(np.var(anomaly_scores)) if anomaly_scores else None

    accuracy = sklearn.metrics.accuracy_score(references, predictions)
    f1 = sklearn.metrics.f1_score(references, predictions, average=average)
    loss = sklearn.metrics.log_loss(references, probabilities)

    if num_classes_references == num_classes_predictions:
        # special case for binary classification: https://github.com/scikit-learn/scikit-learn/issues/20186
        if num_classes_references == 2:
            roc_auc = sklearn.metrics.roc_auc_score(references, logits[:, 1])
            roc_curve = calculate_roc_curve(references, logits[:, 1]) if include_curves else None
            pr_auc = sklearn.metrics.average_precision_score(references, logits[:, 1])
            pr_curve = calculate_pr_curve(references, logits[:, 1]) if include_curves else None
        else:
            roc_auc = sklearn.metrics.roc_auc_score(references, probabilities, multi_class=multi_class)
            roc_curve = None
            pr_auc = None
            pr_curve = None
    else:
        roc_auc = None
        pr_auc = None
        pr_curve = None
        roc_curve = None

    return ClassificationMetrics(
        accuracy=float(accuracy),
        f1_score=float(f1),
        loss=float(loss),
        anomaly_score_mean=anomaly_score_mean,
        anomaly_score_median=anomaly_score_median,
        anomaly_score_variance=anomaly_score_variance,
        roc_auc=float(roc_auc) if roc_auc is not None else None,
        pr_auc=float(pr_auc) if pr_auc is not None else None,
        pr_curve=pr_curve,
        roc_curve=roc_curve,
    )


@dataclass
class RegressionMetrics:
    mse: float
    """Mean squared error of the predictions"""

    rmse: float
    """Root mean squared error of the predictions"""

    mae: float
    """Mean absolute error of the predictions"""

    r2: float
    """R-squared score (coefficient of determination) of the predictions"""

    explained_variance: float
    """Explained variance score of the predictions"""

    loss: float
    """Mean squared error loss of the predictions"""

    anomaly_score_mean: float | None = None
    """Mean of anomaly scores across the dataset"""

    anomaly_score_median: float | None = None
    """Median of anomaly scores across the dataset"""

    anomaly_score_variance: float | None = None
    """Variance of anomaly scores across the dataset"""

    def __repr__(self) -> str:
        return (
            "RegressionMetrics({\n"
            + f"    mae: {self.mae:.4f},\n"
            + f"    rmse: {self.rmse:.4f},\n"
            + f"    r2: {self.r2:.4f},\n"
            + (
                f"    anomaly_score: {self.anomaly_score_mean:.4f} ± {self.anomaly_score_variance:.4f},\n"
                if self.anomaly_score_mean
                else ""
            )
            + "})"
        )


def calculate_regression_metrics(
    expected_scores: NDArray[np.float32] | list[float],
    predicted_scores: NDArray[np.float32] | list[float],
    anomaly_scores: list[float] | None = None,
) -> RegressionMetrics:
    """
    Calculate regression metrics for model evaluation.

    Params:
        references: True target values
        predictions: Predicted values from the model
        anomaly_scores: Optional anomaly scores for each prediction

    Returns:
        Comprehensive regression metrics including MSE, RMSE, MAE, R², and explained variance

    Raises:
        ValueError: If predictions and references have different lengths
    """
    references = np.array(expected_scores)
    predictions = np.array(predicted_scores)

    if len(predictions) != len(references):
        raise ValueError("Predictions and references must have the same length")

    anomaly_score_mean = float(np.mean(anomaly_scores)) if anomaly_scores else None
    anomaly_score_median = float(np.median(anomaly_scores)) if anomaly_scores else None
    anomaly_score_variance = float(np.var(anomaly_scores)) if anomaly_scores else None

    # Calculate core regression metrics
    mse = float(sklearn.metrics.mean_squared_error(references, predictions))
    rmse = float(np.sqrt(mse))
    mae = float(sklearn.metrics.mean_absolute_error(references, predictions))
    r2 = float(sklearn.metrics.r2_score(references, predictions))
    explained_var = float(sklearn.metrics.explained_variance_score(references, predictions))

    return RegressionMetrics(
        mse=mse,
        rmse=rmse,
        mae=mae,
        r2=r2,
        explained_variance=explained_var,
        loss=mse,  # For regression, loss is typically MSE
        anomaly_score_mean=anomaly_score_mean,
        anomaly_score_median=anomaly_score_median,
        anomaly_score_variance=anomaly_score_variance,
    )

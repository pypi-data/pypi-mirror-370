"""Defines functions which compute metrics."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping
from dataclasses import dataclass
from enum import Enum, auto
from functools import partial
import logging
from typing import TYPE_CHECKING, Optional, Union, cast

import numpy as np
from scipy.stats import kstest
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)

from bitfount.models.base_models import ClassifierMixIn, RegressorMixIn, _BaseModel
from bitfount.utils import delegates

if TYPE_CHECKING:
    from bitfount.types import DistributedModelProtocol

__all__: list[str] = [
    "BINARY_CLASSIFICATION_METRICS",
    "ClassificationMetric",
    "MULTICLASS_CLASSIFICATION_METRICS",
    "MULTILABEL_CLASSIFICATION_METRICS",
    "Metric",
    "MetricCollection",
    "MetricsProblem",
    "REGRESSION_METRICS",
    "SEGMENTATION_METRICS",
]

_logger = logging.getLogger(__name__)


def _binary_dice_coefficient(target: np.ndarray, pred: np.ndarray) -> float:
    """Computes the dice coefficient for a binary segmentation task.

    Dice Coefficient is 2 * the Area of Overlap (i.e. the intersection of the pixels)
    divided by the total number of pixels in both images (i.e. the union of the pixels).

    Args:
        pred: The predicted segmentation.
        target: The target segmentation.

    Returns:
        The binary dice coefficients score.
    """
    # TODO: [BIT-4450] We need to account for shapes that are different due to
    #       batches and maybe broadcast/expand the `target` array to match the
    #       `preds` array?
    # Shape must be the same, as these should be the same overall size of masks, etc
    if target.shape != pred.shape:
        raise ValueError(
            f"Array shapes for binary dice coefficients must match."
            f" Got target={target.shape}, predictions={pred.shape}"
        )

    # The masks must only have elements between 0 and 1
    for mask, mask_name in ((target, "target"), (pred, "predictions")):
        if not ((mask >= 0) & (mask <= 1)).all():
            raise ValueError(
                f"Mask must only contain elements between 0 and 1;"
                f' mask "{mask_name}" contained elements that were'
                f" outside of this range."
            )

    # Easier to work with (N,) arrays, and makes no difference to the calculations below
    y_true_f = target.flatten()
    y_pred_f = pred.flatten()

    # See: https://medium.com/the-research-nest/calculating-the-s%C3%B8rensen-dice-coefficient-a-simplified-guide-3b59a1829a82 # noqa: E501
    # for more details.
    # In the binary case (i.e. elements are 0 or 1) it is easy to see that
    # multiplying the two masks together gets their intersection, sum them to get the
    # union.
    # This can also be expanded to the "soft" label case, where they are instead
    # probabilities, and the multiplied elements give the "probabilistic overlap", etc.
    intersection: int = (y_true_f * y_pred_f).sum()
    union: int = y_true_f.sum() + y_pred_f.sum()

    # Use smoothing factor to avoid "divide by 0 issues"
    smooth = 0.0001
    return (2.0 * intersection) / (union + smooth)


def multiclass_dice_coefficients(target: np.ndarray, pred: np.ndarray) -> float:
    """Computes the dice coefficient for a multiclass segmentation task.

    Both arrays should be of shape: (Batch_size X number of classes X Height X Width).

    Args:
        pred: The predicted segmentation.
        target: The target segmentation.

    Returns:
        The multiclass dice coefficients score.
    """
    # TODO: [BIT-4450] We need to account for shapes that are different due to
    #       batches and maybe broadcast/expand the `target` array to match the
    #       `preds` array?
    n_classes = pred.shape[1]
    dice = 0.0

    for class_idx in range(1, n_classes):
        dice += _binary_dice_coefficient(target, pred[:, class_idx, :, :])

    return dice / n_classes  # taking average


def _stats_score(
    target: np.ndarray, pred: np.ndarray, n: int = 1
) -> tuple[int, int, int, int]:
    """Computes the relevant statistics between targets and predictions.

    More specifically, computes the true positive (tp), false positive(fp),
    true negative (tn) and false positive (fp) rates given the targets,
    prediction and the class.

    Args:
        target: The target value.
        pred: The predicted value.
        n: The class to compute the statistics for.

    Returns:
        A tuple containing (tp, fp, tn, fn).
    """
    cls_pred = np.argmax(pred, axis=1)
    tp = ((cls_pred == n) * (target == n)).sum()
    fp = ((cls_pred == n) * (target != n)).sum()
    tn = ((cls_pred != n) * (target != n)).sum()
    fn = ((cls_pred != n) * (target == n)).sum()
    return tp, fp, tn, fn


def dice_score(
    target: np.ndarray, pred: np.ndarray, ignore_class_0: bool = True
) -> float:
    """Computes the dice score.

    This is computed as 2*tp/2*tp+fp+fn.

    Args:
        target: The target segmentation.
        pred: The predicted segmentation.
        ignore_class_0: Whether class 0 should be excluded from the calculation.

    Returns:
        The dice score averaged over each class (i.e. "macro").
    """
    n_classes = pred.shape[1]
    # The Dice score should only be averaged over the included classes
    # See torchmetric dice() implementation for details.
    if ignore_class_0:
        avg_denom = n_classes - 1
    else:
        avg_denom = n_classes
    score = 0.0

    # Only loop from 1 if we don't care about the "background" class
    for i in range(1 if ignore_class_0 else 0, n_classes):
        tp, fp, tn, fn = _stats_score(target, pred, i)
        denom = 2 * tp + fp + fn
        if not (target == i).any():
            # no foreground class
            score_cls = 0.0
        elif np.isclose(denom, np.zeros_like(denom)).any():
            # nan result
            score_cls = 0.0
        else:
            score_cls = (2 * tp) / denom
        score += score_cls
    return score / avg_denom


def iou(target: np.ndarray, pred: np.ndarray, ignore_class_0: bool = True) -> float:
    """Computes the Intersection over union score.

    This is computed as tp/tp+fp+fn. Also known as Jaccard Index.

    Args:
        target: The target segmentation.
        pred: The predicted segmentation.
        ignore_class_0: Whether class 0 should be excluded from the averaging
            calculation. Class 0 is still used to calculate TPs, TNs, etc. from other
            classes, but the metric calculated for Class 0 is treated as 0.0 for the
            averaging.

    Returns:
        The IoU score averaged over each class (i.e. "macro").
    """
    # computed as tp/tp+fp+fn
    n_classes = pred.shape[1]
    # The Jaccard index should only be averaged over the included classes
    # See torchmetric jaccard_index() implementation for details.
    if ignore_class_0:
        avg_denom = n_classes - 1
    else:
        avg_denom = n_classes
    score = 0.0

    # Only loop from 1 if we don't care about the "background" class
    for i in range(1 if ignore_class_0 else 0, n_classes):
        tp, fp, tn, fn = _stats_score(target, pred, i)
        denom = tp + fp + fn

        # If there are only true negatives (i.e. the class is not represented in the
        # predictions at all) then we exclude this from the averaging
        # See the torchmetrics jaccard_index() implementation for details
        if np.isclose(denom, np.zeros_like(denom)).any():
            # nan result
            score_cls = 0.0
            avg_denom -= 1
        # If the current class is not in the targets at all, tp must be 0, therefore
        # tp/tp+fp+fn = 0
        elif not (target == i).any():
            # no foreground class
            score_cls = 0.0
        # Otherwise, calculate as expected
        else:
            score_cls = tp / denom
        score += score_cls

    if avg_denom != 0:
        return score / avg_denom
    else:
        return 0.0


@dataclass
class Metric:
    """A metric used for assessing ML model performance.

    Attributes:
        func: A function which computes the metric. Must take two arguments:
            y_true and y_pred and return a metric as a float.
    """

    func: Callable[[np.ndarray, np.ndarray], float]


@delegates()
@dataclass
class ClassificationMetric(Metric):
    """A classification metric used for assessing ML model performance.

    Args:
        probabilities: Whether y_pred needs to be classes or probabilities.
    """

    probabilities: bool


MULTICLASS_CLASSIFICATION_METRICS: dict[str, Metric] = {
    "AUC": ClassificationMetric(
        partial(roc_auc_score, multi_class="ovr", average="macro"), True
    ),
    "F1": ClassificationMetric(partial(f1_score, average="macro"), False),
    "Recall": ClassificationMetric(partial(recall_score, average="macro"), False),
    "Precision": ClassificationMetric(
        partial(precision_score, average="macro", zero_division=0.0),
        False,  #
    ),
    "Accuracy": ClassificationMetric(accuracy_score, False),
}

MULTILABEL_CLASSIFICATION_METRICS: dict[str, Metric] = {
    "AUC": ClassificationMetric(
        partial(roc_auc_score, multi_class="ovr", average="micro"), True
    ),
    "F1": ClassificationMetric(partial(f1_score, average="micro"), False),
    "Recall": ClassificationMetric(partial(recall_score, average="micro"), False),
    "Precision": ClassificationMetric(
        partial(precision_score, average="micro", zero_division=0.0), False
    ),
    "Accuracy": ClassificationMetric(accuracy_score, False),
}

BINARY_CLASSIFICATION_METRICS: dict[str, Metric] = {
    "AUC": ClassificationMetric(
        partial(roc_auc_score, multi_class="ovr", average="macro"), True
    ),
    "F1": ClassificationMetric(partial(f1_score, average="binary"), False),
    "Recall": ClassificationMetric(partial(recall_score, average="binary"), False),
    "Precision": ClassificationMetric(
        partial(precision_score, average="binary", zero_division=0.0), False
    ),
    "Accuracy": ClassificationMetric(accuracy_score, False),
    "BrierLoss": ClassificationMetric(brier_score_loss, True),
}

_rmse_func: Callable = lambda x, y: np.sqrt(mean_squared_error(x, y))  # noqa: E731

REGRESSION_METRICS: dict[str, Metric] = {
    "MAE": Metric(mean_absolute_error),
    "MSE": Metric(mean_squared_error),
    "RMSE": Metric(_rmse_func),
    "R2": Metric(r2_score),
    "KS": Metric(kstest),
}

SEGMENTATION_METRICS: dict[str, Metric] = {
    "IoU": Metric(iou),
    "DiceCoefficients": Metric(multiclass_dice_coefficients),
    "DiceScore": Metric(dice_score),
}


class MetricsProblem(Enum):
    """Simple wrapper for different problem types for MetricCollection."""

    BINARY_CLASSIFICATION = auto()
    MULTICLASS_CLASSIFICATION = auto()
    MULTILABEL_CLASSIFICATION = auto()
    REGRESSION = auto()
    SEGMENTATION = auto()


class MetricCollection:
    """Container class for metrics to calculate.

    Args:
        metrics: A list of metrics to calculate.
        problem: The problem type. If metrics are not specified, the problem type will
            be used to determine the metrics to calculate.

    Raises:
        ValueError: If neither one of `problem` nor `metrics` is specified.

    Attributes:
        metrics: A list of metrics to calculate.
        problem: The problem type.
        optimal_threshold: The optimal threshold to separate classes (only used for
            classification problems).
        thresholds: The thresholds to separate classes (only used for
            classification problems).
        threshold_metrics: The metrics for each threshold (only used for
            classification problems).
    """

    def __init__(
        self,
        metrics: Optional[MutableMapping[str, Metric]] = None,
        problem: Optional[MetricsProblem] = None,
    ):
        if metrics is None and problem is None:
            raise ValueError(
                "At least one of `metrics` or `problem` must be specified."
            )

        if metrics is not None:
            self.metrics = metrics
        else:
            self.metrics = self._get_metrics(cast(MetricsProblem, problem))

        self.problem = problem
        self.optimal_threshold: Optional[float] = None
        self.results: dict[str, float] = {}
        self.thresholds = np.linspace(0, 100, 201, endpoint=True) / 100
        self.threshold_metrics: Optional[Mapping[str, Iterable[float]]] = None

    @classmethod
    def create_from_model(
        cls,
        model: Union[_BaseModel, DistributedModelProtocol],
        metrics: Optional[MutableMapping[str, Metric]] = None,
    ) -> MetricCollection:
        """Creates a MetricCollection object from a _BaseModel.

        Args:
            model: A _BaseModel.
            metrics: The metrics dictionary. Defaults to None.

        Returns:
            Instance of MetricCollection.
        """
        problem: Optional[MetricsProblem] = None
        # The casts are to reassure mypy that a subclass of both _BaseModel and
        # ClassifierMixIn can exist (the ._Schema attribute causes problems)
        if isinstance(cast(ClassifierMixIn, model), ClassifierMixIn):
            classifier_model = cast(ClassifierMixIn, model)
            if classifier_model.multilabel:
                problem = MetricsProblem.MULTILABEL_CLASSIFICATION
            elif classifier_model.n_classes > 2:
                problem = MetricsProblem.MULTICLASS_CLASSIFICATION
            else:
                problem = MetricsProblem.BINARY_CLASSIFICATION
        elif isinstance(cast(RegressorMixIn, model), RegressorMixIn):
            problem = MetricsProblem.REGRESSION
        else:
            _logger.warning("Metrics problem type can't be determined. Leaving empty.")

        return cls(problem=problem, metrics=metrics)

    def compute(
        self,
        test_target: np.ndarray,
        test_preds: np.ndarray,
        metric_to_optimise: str = "F1",
        threshold: Optional[float] = None,
    ) -> dict[str, float]:
        """Compute list of metrics and save results in self.results.

        :::note

        Thresholds do not apply to multiclass problems.

        :::

        Args:
            test_target: A list of targets.
            test_preds: A list of predictions.
            metric_to_optimise: What metric to optimize in order to compute the
                optimal threshold. This will have no effect if there aren't any metrics
                to which a threshold is applied. Must be present in 'self.metrics'.
            threshold: If this argument is provided, this threshold will be
                used instead of optimising the threshold as per 'optimise'
        """
        if (
            self.problem is MetricsProblem.BINARY_CLASSIFICATION
            and np.asarray(test_preds).ndim == 2
        ):
            test_preds = np.asarray([row[1] for row in test_preds])

        if (
            self.problem is MetricsProblem.REGRESSION
            or self.problem is MetricsProblem.BINARY_CLASSIFICATION
        ):
            test_preds = np.asarray(test_preds).squeeze()
            test_target = np.asarray(test_target).squeeze()

        for metric_name, metric in self.metrics.items():
            if isinstance(metric, ClassificationMetric) and not metric.probabilities:
                test_probs_or_classes = self._get_prediction_classes(
                    test_target, test_preds, metric_to_optimise, threshold
                )
            else:
                test_probs_or_classes = test_preds
            try:
                self.results[metric_name] = cast(
                    float,
                    self._round(metric.func(test_target, test_probs_or_classes), 4),
                )
                # metric.func always returns a float, so the _round
                # function will return a float as well
            except (ValueError, IndexError):
                # This usually occurs when the targets do not have all possible classes
                self.results[metric_name] = np.inf
                _logger.warning(
                    "Unable to compute metric: " + metric_name + " setting to np.inf"
                )

        return self.results

    @staticmethod
    def _round(
        metric: Union[float, tuple[float]], num_decimal_places: int
    ) -> Union[float, tuple[float, ...]]:
        """Simply rounds metric by num_decimal_places and returns it."""
        if isinstance(metric, tuple):
            rounded_metric = tuple(round(i, num_decimal_places) for i in metric)
        elif isinstance(metric, float):
            rounded_metric = round(metric, num_decimal_places)  # type: ignore[arg-type] # reason: see below # noqa: E501
            # mypy raises the following error: Argument 1 to
            # "round" has incompatible type "float".

        return rounded_metric

    @staticmethod
    def _get_metrics(problem: MetricsProblem) -> dict[str, Metric]:
        """Returns metrics appropriate for the task, otherwise simply returns `metrics`.

        Args:
            problem: The problem type to return the appropriate metrics for.

        Returns:
            Dictionary of metrics to be computed.

        Raises:
            ValueError: If the problem type is not recognised.
        """
        if problem is MetricsProblem.REGRESSION:
            metrics = REGRESSION_METRICS
        elif problem is MetricsProblem.BINARY_CLASSIFICATION:
            metrics = BINARY_CLASSIFICATION_METRICS
        elif problem is MetricsProblem.MULTICLASS_CLASSIFICATION:
            metrics = MULTICLASS_CLASSIFICATION_METRICS
        elif problem is MetricsProblem.SEGMENTATION:
            metrics = SEGMENTATION_METRICS
        elif problem is MetricsProblem.MULTILABEL_CLASSIFICATION:
            metrics = MULTILABEL_CLASSIFICATION_METRICS
        else:
            raise ValueError("Problem type not recognised.")

        return metrics

    def _get_prediction_classes(
        self,
        test_target: np.ndarray,
        test_preds: np.ndarray,
        metric_to_optimise: str,
        threshold: Optional[float] = None,
    ) -> np.ndarray:
        """Returns test_preds as class labels.

        This is done after applying or optimising a threshold.
        """
        if (
            threshold is None
            and self.optimal_threshold is None
            and self.problem is not MetricsProblem.MULTICLASS_CLASSIFICATION
        ):
            self._optimise_threshold(test_target, test_preds, metric_to_optimise)

        return self._apply_threshold(test_preds, threshold)

    def _apply_threshold(
        self,
        preds: np.ndarray,
        threshold: Optional[float] = None,
    ) -> np.ndarray:
        """Applies a threshold to a list of predictions and returns the classes.

        For binary and multilabel problems, a threshold is computed and applied.

        For multiclass problems, it simply assumes that every prediction must
        have exactly 1 positive class and this is given to the class corresponding
        to the highest probability.
        """
        if threshold is None:
            threshold = self.optimal_threshold
        test_preds_cls: np.ndarray
        if self.problem is MetricsProblem.BINARY_CLASSIFICATION:
            test_preds_cls = np.where(preds < threshold, 0, 1)
        elif self.problem is MetricsProblem.MULTILABEL_CLASSIFICATION:
            test_preds_cls = np.asarray(
                [[0 if prob < threshold else 1 for prob in output] for output in preds]
            )
        else:
            test_preds_cls = np.array([np.argmax(output) for output in preds])
        return test_preds_cls

    def _optimise_threshold(
        self,
        test_target: np.ndarray,
        test_preds: np.ndarray,
        metric_to_optimise: str,
    ) -> None:
        """Optimise decision threshold by tuning metric_to_optimise.

        Finds the argmax of given metric by modifying the decision threshold and sets
        self.optimal_threshold

        Args:
            test_target: The targets array.
            test_preds: The predictions array.
            metric_to_optimise: The metric to optimise.

        Raises:
            ValueError: if metric_to_optimise does not exist in self.metrics
        """
        if metric_to_optimise not in self.metrics:
            raise ValueError("Chosen optimisation metric is not defined.")

        optimal_threshold = 0
        max_metric: float = 0

        # Dictionary of relevant metrics (i.e. those where a threshold is applied)
        # and the computed value for every threshold stored as a list
        threshold_metrics: dict[str, list[float]] = {}
        for m in self.metrics:
            if (
                isinstance(self.metrics[m], ClassificationMetric)
                and not cast(ClassificationMetric, self.metrics[m]).probabilities
            ):
                threshold_metrics[m] = []
        # Loop through every threshold and apply it to our predictions
        for threshold in self.thresholds:
            test_preds_cls = self._apply_threshold(test_preds, threshold)

            # Loop through every metric in threshold_metrics and compute the value
            for metric_name in threshold_metrics:
                metric = self.metrics[metric_name]
                metric_val = metric.func(test_target, test_preds_cls)

                # Store the computed value in `threshold_metrics`
                threshold_metrics[metric_name].append(metric_val)

                # Update optimal threshold if the metric is the one we are optimising
                # and if the value is better than the previous best value
                if metric_name == metric_to_optimise and metric_val > max_metric:
                    max_metric = metric_val
                    optimal_threshold = threshold

        self.optimal_threshold = optimal_threshold
        self.threshold_metrics = threshold_metrics


def _sum_var(
    test_preds_thresh: list[int],
    test_var_to_sum: list[float],
    test_var_margin: Optional[list[float]] = None,
) -> float:
    """Performs the required sum on the variable provided for every prediction."""
    cum_var: float = 0
    cum_margin: float = 0
    for index, val in enumerate(test_preds_thresh):
        if val == 1:
            cum_var += test_var_to_sum[index]
            if test_var_margin:
                cum_margin += test_var_margin[index]

    if test_var_margin:
        return cum_var / max(cum_margin, 1)

    return cum_var

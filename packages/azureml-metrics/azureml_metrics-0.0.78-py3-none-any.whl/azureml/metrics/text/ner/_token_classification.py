# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Definitions for text-ner metrics."""
import logging
from abc import abstractmethod
from typing import Any, List

from azureml.metrics.common._metric_base import Metric, ScalarMetric
from azureml.metrics.common.exceptions import MissingDependencies

_logger = logging.getLogger(__name__)


class TextNERMetric(Metric):
    """Abstract class for classification metrics."""

    MICRO_AVERAGE = 'micro'
    MACRO_AVERAGE = 'macro'
    WEIGHTED_AVERAGE = 'weighted'

    def __init__(self,
                 y_test: List[List[str]],
                 y_pred: List[List[str]]
                 ) -> None:
        """
        Initialize the classification metric class.

        :param y_test: True labels for the test set.
        :param y_pred: The model's predictions.
        """
        self._y_test = y_test
        self._y_pred = y_pred
        super().__init__()

    @abstractmethod
    def compute(self) -> Any:
        """Compute the metric."""
        ...


class Accuracy(TextNERMetric, ScalarMetric):
    """Wrapper class for accuracy."""

    def compute(self):
        """Compute the score for the metric."""
        try:
            from seqeval.metrics import accuracy_score
        except ImportError:
            safe_message = "Text packages are not available. Please run pip install azureml-metrics[text]"

            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )

        return accuracy_score(y_true=self._y_test, y_pred=self._y_pred)


class F1(TextNERMetric, ScalarMetric):
    """Wrapper class for recall."""

    def __init__(self, average_type, *args, **kwargs):
        """Initialize F1."""
        self._average_type = average_type
        super().__init__(*args, **kwargs)

    def compute(self):
        """Compute the score for the metric."""
        try:
            from seqeval.metrics import f1_score
        except ImportError:
            safe_message = "Text packages are not available. Please run pip install azureml-metrics[text]"

            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )

        return f1_score(
            y_true=self._y_test, y_pred=self._y_pred, average=self._average_type
        )


class F1Macro(F1):
    """Wrapper class for macro-averaged F1 score."""

    def __init__(self, *args, **kwargs):
        """Initialize F1Macro."""
        super().__init__(TextNERMetric.MACRO_AVERAGE, *args, **kwargs)


class F1Micro(F1):
    """Wrapper class for micro-averaged F1 score."""

    def __init__(self, *args, **kwargs):
        """Initialize F1Micro."""
        super().__init__(TextNERMetric.MICRO_AVERAGE, *args, **kwargs)


class F1Weighted(F1):
    """Wrapper class for weighted-averaged F1 score."""

    def __init__(self, *args, **kwargs):
        """Initialize F1Weighted."""
        super().__init__(TextNERMetric.WEIGHTED_AVERAGE, *args, **kwargs)


class Precision(TextNERMetric, ScalarMetric):
    """Wrapper class for precision."""

    def __init__(self, average_type, *args, **kwargs):
        """Initialize Precision."""
        self._average_type = average_type
        super().__init__(*args, **kwargs)

    def compute(self):
        """Compute the score for the metric."""
        try:
            from seqeval.metrics import precision_score
        except ImportError:
            safe_message = "Text packages are not available. Please run pip install azureml-metrics[text]"

            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )
        return precision_score(
            y_true=self._y_test, y_pred=self._y_pred, average=self._average_type
        )


class PrecisionMacro(Precision):
    """Wrapper class for macro-averaged Precision score."""

    def __init__(self, *args, **kwargs):
        """Initialize PrecisionMacro."""
        super().__init__(TextNERMetric.MACRO_AVERAGE, *args, **kwargs)


class PrecisionMicro(Precision):
    """Wrapper class for micro-averaged Precision score."""

    def __init__(self, *args, **kwargs):
        """Initialize PrecisionMicro."""
        super().__init__(TextNERMetric.MICRO_AVERAGE, *args, **kwargs)


class PrecisionWeighted(Precision):
    """Wrapper class for weighted-averaged Precision score."""

    def __init__(self, *args, **kwargs):
        """Initialize PrecisionWeighted."""
        super().__init__(TextNERMetric.WEIGHTED_AVERAGE, *args, **kwargs)


class Recall(TextNERMetric, ScalarMetric):
    """Wrapper class for recall."""

    def __init__(self, average_type, *args, **kwargs):
        """Initialize Recall."""
        self._average_type = average_type
        super().__init__(*args, **kwargs)

    def compute(self):
        """Compute the score for the metric."""
        try:
            from seqeval.metrics import recall_score
        except ImportError:
            safe_message = "Text packages are not available. Please run pip install azureml-metrics[text]"

            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )
        return recall_score(
            y_true=self._y_test, y_pred=self._y_pred, average=self._average_type
        )


class RecallMacro(Recall):
    """Wrapper class for macro-averaged recall."""

    def __init__(self, *args, **kwargs):
        """Initialize RecallMacro."""
        super().__init__(TextNERMetric.MACRO_AVERAGE, *args, **kwargs)


class RecallMicro(Recall):
    """Wrapper class for micro-averaged recall."""

    def __init__(self, *args, **kwargs):
        """Initialize RecallMicro."""
        super().__init__(TextNERMetric.MICRO_AVERAGE, *args, **kwargs)


class RecallWeighted(Recall):
    """Wrapper class for weighted-averaged recall."""

    def __init__(self, *args, **kwargs):
        """Initialize RecallWeighted."""
        super().__init__(TextNERMetric.WEIGHTED_AVERAGE, *args, **kwargs)

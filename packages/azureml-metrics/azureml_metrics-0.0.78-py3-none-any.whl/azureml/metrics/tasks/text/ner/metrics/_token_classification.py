# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Definitions for text-ner metrics."""
import logging
from abc import abstractmethod

from azureml.metrics import constants
from azureml.metrics.common._metric_base import Metric, ScalarMetric
from azureml.metrics.common.azureml_output_dao import AzureMLOutput
from azureml.metrics.common.exceptions import MissingDependencies
from azureml.metrics.tasks.text.ner.dao.azureml_ner_dao import AzureMLNerDAO

logger = logging.getLogger(__name__)


class TextNERMetric(Metric):
    """Abstract class for classification metrics."""

    MICRO_AVERAGE = 'micro'
    MACRO_AVERAGE = 'macro'
    WEIGHTED_AVERAGE = 'weighted'

    def __init__(self, metrics_data: AzureMLNerDAO) -> None:
        """
        Initialize the NER metric class.
        """
        self.metrics_data = metrics_data
        super().__init__()

    @abstractmethod
    def compute(self) -> AzureMLOutput:
        """Compute the metric."""
        ...


class Accuracy(TextNERMetric, ScalarMetric):
    """Wrapper class for accuracy."""

    def compute(self) -> AzureMLOutput:
        """Compute the score for the metric."""
        try:
            from seqeval.metrics import accuracy_score
        except ImportError:
            safe_message = "Text packages are not available. Please run pip install azureml-metrics[text]"
            raise MissingDependencies(safe_message, safe_message=safe_message)

        result = accuracy_score(y_true=self.metrics_data.y_test, y_pred=self.metrics_data.y_pred)

        output = AzureMLOutput()
        metric = constants.Metric.Accuracy
        output.add_value(metric, result)
        return output


class F1(TextNERMetric, ScalarMetric):
    """Wrapper class for recall."""

    def __init__(self, average_type, metric_name, *args, **kwargs):
        """Initialize F1."""
        self._average_type = average_type
        self._metric_name = metric_name
        super().__init__(*args, **kwargs)

    def compute(self) -> AzureMLOutput:
        """Compute the score for the metric."""
        try:
            from seqeval.metrics import f1_score
        except ImportError:
            safe_message = "Text packages are not available. Please run pip install azureml-metrics[text]"
            raise MissingDependencies(safe_message, safe_message=safe_message)

        result = f1_score(y_true=self.metrics_data.y_test, y_pred=self.metrics_data.y_pred, average=self._average_type)

        output = AzureMLOutput()
        metric = self._metric_name
        output.add_value(metric, result)
        return output


class F1Macro(F1):
    """Wrapper class for macro-averaged F1 score."""

    def __init__(self, *args, **kwargs):
        """Initialize F1Macro."""
        super().__init__(TextNERMetric.MACRO_AVERAGE, constants.Metric.F1Macro, *args, **kwargs)


class F1Micro(F1):
    """Wrapper class for micro-averaged F1 score."""

    def __init__(self, *args, **kwargs):
        """Initialize F1Micro."""
        super().__init__(TextNERMetric.MICRO_AVERAGE, constants.Metric.F1Micro, *args, **kwargs)


class F1Weighted(F1):
    """Wrapper class for weighted-averaged F1 score."""

    def __init__(self, *args, **kwargs):
        """Initialize F1Weighted."""
        super().__init__(TextNERMetric.WEIGHTED_AVERAGE, constants.Metric.F1Weighted, *args, **kwargs)


class Precision(TextNERMetric, ScalarMetric):
    """Wrapper class for precision."""

    def __init__(self, average_type, metric_name, *args, **kwargs):
        """Initialize Precision."""
        self._average_type = average_type
        self._metric_name = metric_name
        super().__init__(*args, **kwargs)

    def compute(self) -> AzureMLOutput:
        """Compute the score for the metric."""
        try:
            from seqeval.metrics import precision_score
        except ImportError:
            safe_message = "Text packages are not available. Please run pip install azureml-metrics[text]"
            raise MissingDependencies(safe_message, safe_message=safe_message)

        result = precision_score(y_true=self.metrics_data.y_test, y_pred=self.metrics_data.y_pred,
                                 average=self._average_type)

        output = AzureMLOutput()
        metric = self._metric_name
        output.add_value(metric, result)
        return output


class PrecisionMacro(Precision):
    """Wrapper class for macro-averaged Precision score."""

    def __init__(self, *args, **kwargs):
        """Initialize PrecisionMacro."""
        super().__init__(TextNERMetric.MACRO_AVERAGE, constants.Metric.PrecisionMacro, *args, **kwargs)


class PrecisionMicro(Precision):
    """Wrapper class for micro-averaged Precision score."""

    def __init__(self, *args, **kwargs):
        """Initialize PrecisionMicro."""
        super().__init__(TextNERMetric.MICRO_AVERAGE, constants.Metric.PrecisionMicro, *args, **kwargs)


class PrecisionWeighted(Precision):
    """Wrapper class for weighted-averaged Precision score."""

    def __init__(self, *args, **kwargs):
        """Initialize PrecisionWeighted."""
        super().__init__(TextNERMetric.WEIGHTED_AVERAGE, constants.Metric.PrecisionWeighted, *args, **kwargs)


class Recall(TextNERMetric, ScalarMetric):
    """Wrapper class for recall."""

    def __init__(self, average_type, metric_name, *args, **kwargs):
        """Initialize Recall."""
        self._average_type = average_type
        self._metric_name = metric_name
        super().__init__(*args, **kwargs)

    def compute(self) -> AzureMLOutput:
        """Compute the score for the metric."""
        try:
            from seqeval.metrics import recall_score
        except ImportError:
            safe_message = "Text packages are not available. Please run pip install azureml-metrics[text]"
            raise MissingDependencies(safe_message, safe_message=safe_message)

        result = recall_score(y_true=self.metrics_data.y_test, y_pred=self.metrics_data.y_pred,
                              average=self._average_type)

        output = AzureMLOutput()
        metric = self._metric_name
        output.add_value(metric, result)
        return output


class RecallMacro(Recall):
    """Wrapper class for macro-averaged recall."""

    def __init__(self, *args, **kwargs):
        """Initialize RecallMacro."""
        super().__init__(TextNERMetric.MACRO_AVERAGE, constants.Metric.RecallMacro, *args, **kwargs)


class RecallMicro(Recall):
    """Wrapper class for micro-averaged recall."""

    def __init__(self, *args, **kwargs):
        """Initialize RecallMicro."""
        super().__init__(TextNERMetric.MICRO_AVERAGE, constants.Metric.RecallMicro, *args, **kwargs)


class RecallWeighted(Recall):
    """Wrapper class for weighted-averaged recall."""

    def __init__(self, *args, **kwargs):
        """Initialize RecallWeighted."""
        super().__init__(TextNERMetric.WEIGHTED_AVERAGE, constants.Metric.RecallWeighted, *args, **kwargs)

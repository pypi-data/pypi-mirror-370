# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to a Classification task type."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, Iterator, Callable

from azureml.metrics.common import utilities
from azureml.metrics.common._logging_utils import default_log_activity, default_log_traceback
from azureml.metrics.constants import MetricExtrasConstants

logger = logging.getLogger(__name__)


class AzureMLMetrics(ABC):
    """Abstract class for AzureML metrics."""

    def __init__(self,
                 log_activity: Callable[[logging.Logger, str, Optional[str],
                                         Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
                 log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                          Optional[bool], Optional[Any]], None],
                 ):
        """
        Create the azuremlmetric base class.

        :param log_activity is a callback to log the activity with parameters
            :param logger: logger
            :param activity_name: activity name
            :param activity_type: activity type
            :param custom_dimensions: custom dimensions
        :param log_traceback is a callback to log exception traces. with parameters
            :param exception: The exception to log.
            :param logger: The logger to use.
            :param override_error_msg: The message to display that will override the current error_msg.
            :param is_critical: If is_critical, the logger will use log.critical, otherwise log.error.
            :param tb: The traceback to use for logging; if not provided, the one attached to the exception is used.
        """
        self._log_activity = log_activity if log_activity else default_log_activity
        self._log_traceback = log_traceback if log_traceback else default_log_traceback

    @abstractmethod
    def compute(self,
                y_test: Optional[Any],
                y_pred: Optional[Any] = None) -> Union[Any, Dict[str, Any]]:
        """
        Compute all metrics for classification task based on the config.

        :param y_test: Actual label values
        :param y_pred: Predicted values
        :return: Dict of computed metrics
        """
        pass

    def merge_confidence_interval_metrics(self, scored_metrics: Dict[str, Any],
                                          scored_confidence_intervals: Dict[str, Any]):
        """
        Merge the regular and confidence interval scores.

        :param scored_metrics regular scores for the task
        :param scored_confidence_intervals confidence intervals.
        """
        scored_metrics = utilities.amalgamate_scalar_non_scalar(scored_metrics)
        scored_confidence_intervals = utilities.amalgamate_scalar_non_scalar(scored_confidence_intervals)
        joined_metrics = {}  # type: Dict[str, Any]
        for metric in scored_metrics.keys():

            computed_metric = scored_metrics[metric]
            joined_metrics[metric] = computed_metric

            if metric in scored_confidence_intervals:
                ci_metric = scored_confidence_intervals[metric]  # type: Dict[str, Any]
                ci_metric[MetricExtrasConstants.VALUE] = computed_metric
                joined_metrics[MetricExtrasConstants.MetricExtrasFormat.format(metric)] = ci_metric
        return utilities.segregate_scalar_non_scalar(joined_metrics)

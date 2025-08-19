# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to a Regression task type."""

import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Iterator, Callable, Union

from azureml.metrics import constants
from azureml.metrics.common import _scoring_confidence, _scoring, utilities
from azureml.metrics.tabular.regression._dataset_binning import make_dataset_bins
from azureml.metrics.common.azureml_metrics import AzureMLMetrics


logger = logging.getLogger(__name__)


class AzureMLRegressionMetrics(AzureMLMetrics):
    """Class for AzureML regression metrics."""

    def __init__(self,
                 metrics: Optional[List[str]] = None,
                 y_max: Optional[float] = None,
                 y_min: Optional[float] = None,
                 y_std: Optional[float] = None,
                 bin_info: Optional[Dict[str, float]] = None,
                 sample_weight: Optional[np.ndarray] = None,
                 enable_metric_confidence: bool = False,
                 confidence_metrics: Optional[List[str]] = None,
                 custom_dimensions: Optional[Dict[str, Any]] = None,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None
                 ) -> None:
        """
        Given the scored data, generate metrics for regression task.

        :param metrics: Regression metrics to compute point estimates
        :param y_max: The max target value.
        :param y_min: The min target value.
        :param y_std: The standard deviation of targets value.
        :param bin_info:
            The binning information for true values. This should be calculated from make_dataset_bins. Required for
        calculating non-scalar metrics.
        :param sample_weight: Weights for the samples (Does not need
            to match sample weights on the fitted model)
        :param enable_metric_confidence: Allow regression metric calculation to include confidence intervals
            This is currently defaulted to False, and will have an azureml config setting to enable
        :param confidence_metrics: The list of metrics to compute confidence interval.
            If None, it will take the value of `metrics`
            If not None, must be a subset of `metrics`.
            metrics in this list but not in `metircs` will be ignored
        :param custom_dimensions to report the telemetry data.
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
            :param tb: The traceback to use for logging; if not provided,
                        the one attached to the exception is used.
        :return: A dictionary mapping metric name to metric score.
        """
        self.metrics = metrics if metrics else constants.Metric.REGRESSION_SET
        self.enable_metric_confidence = enable_metric_confidence
        self.bin_info = bin_info
        if confidence_metrics is None and enable_metric_confidence:
            confidence_metrics = self.metrics
        self.confidence_metrics = confidence_metrics
        self.y_max = y_max
        self.y_min = y_min
        self.y_std = y_std
        self.bin_info = bin_info
        self.sample_weight = utilities.check_and_convert_to_np(sample_weight)
        self.__custom_dimensions = custom_dimensions

        super().__init__(log_activity, log_traceback)

    def compute(self, y_test: Union[np.ndarray, pd.DataFrame, List],
                y_pred: Optional[Union[np.ndarray, pd.DataFrame, List]] = None) -> Dict[str, Dict[str, Any]]:
        """Given the scored data, generate metrics for classification task.

        The optional parameters `y_max`, `y_min`, and `y_std` should be based on the target column y from the
        full dataset.

        - `y_max` and `y_min` should be used to control the normalization of normalized metrics.
            The effect will be division by max - min.
        - `y_std` is used to estimate a sensible range for displaying non-scalar regression metrics.

        If the metric is undefined given the input data, the score will show
            as nan in the returned dictionary.

        :param y_test: The target values.
        :param y_pred: The predicted values.
        :param metrics: List of metric names for metrics to calculate.
        :param y_max: The max target value.
        :param y_min: The min target value.
        :param y_std: The standard deviation of targets value.
        :param sample_weight:
            The sample weight to be used on metrics calculation. This does not need
            to match sample weights on the fitted model.
        :param bin_info:
            The binning information for true values. This should be calculated from make_dataset_bins. Required for
            calculating non-scalar metrics.
        :param enable_metric_confidence: Allow classfication metric calculation to include confidence intervals
            This is currently defaulted to False, and will have an automl config setting to enable
        :param confidence_metrics: The list of metrics to compute confidence interval.
            If None, it will take the value of `metrics`
            If not None, must be a subset of `metrics`.
            metrics in this list but not in `metircs` will be ignored
        :return: A dictionary mapping metric name to metric score.
        """
        y_test = utilities.check_and_convert_to_np(y_test)
        y_pred = utilities.check_and_convert_to_np(y_pred)

        if self.bin_info is None:
            bin_info = make_dataset_bins(y_test.shape[0], y_test)
        else:
            bin_info = self.bin_info
        scored_metrics = _scoring._score_regression(self._log_activity, self._log_traceback,
                                                    y_test, y_pred, self.metrics,
                                                    self.y_max, self.y_min, self.y_std,
                                                    self.sample_weight, bin_info)
        scored_confidence_intervals = {}
        if self.enable_metric_confidence:
            ignored_metrics = [metric for metric in self.confidence_metrics if metric not in self.metrics]
            if ignored_metrics:
                message = "Found metrics {} in `confidence_metrics` but not in `metrics`."
                message += "These metrics will be ignored for confidence interval computation."
                message.format(ignored_metrics)
                logger.warning(message)
            confidence_metrics = [metric for metric in self.confidence_metrics if metric in self.metrics]

            with self._log_activity(
                    logger,
                    activity_name=constants.TelemetryConstants.COMPUTE_CONFIDENCE_METRICS,
                    custom_dimensions=self.__custom_dimensions
            ):
                scored_confidence_intervals = \
                    _scoring_confidence.score_confidence_intervals_regression(self._log_activity,
                                                                              self._log_traceback,
                                                                              y_test,
                                                                              y_pred,
                                                                              confidence_metrics,
                                                                              self.y_max,
                                                                              self.y_min,
                                                                              self.y_std,
                                                                              self.sample_weight)

        return self.merge_confidence_interval_metrics(scored_metrics, scored_confidence_intervals)

    @staticmethod
    def list_metrics():
        """Get the list of supported metrics.

            :return: List of supported metrics.
        """
        supported_metrics = constants.Metric.REGRESSION_SET
        return supported_metrics

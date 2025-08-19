# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to a Classification task type."""

import logging
import numpy as np
import pandas as pd
import importlib.util
from typing import Any, Dict, List, Optional, Callable, Iterator, Union

from azureml.metrics import constants
from azureml.metrics.common import _scoring_confidence, _scoring, utilities
from azureml.metrics.common.azureml_metrics import AzureMLMetrics
from azureml.metrics.common._validation import validate_multilabel_binary_format
from azureml.metrics.common.exceptions import MissingDependencies, MetricsException

logger = logging.getLogger(__name__)


class AzureMLClassificationMetrics(AzureMLMetrics):
    """Class for AzureML classification metrics."""

    def __init__(self,
                 metrics: Optional[List[str]] = None,
                 class_labels: Optional[np.ndarray] = None,
                 train_labels: Optional[np.ndarray] = None,
                 sample_weight: Optional[np.ndarray] = None,
                 y_transformer: Optional[Any] = None,
                 use_binary: bool = False,
                 enable_metric_confidence: bool = False,
                 multilabel: Optional[bool] = False,
                 positive_label: Optional[Any] = None,
                 confidence_metrics: Optional[List[str]] = None,
                 custom_dimensions: Optional[Dict[str, Any]] = None,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None
                 ) -> None:
        """
        Given the scored data, generate metrics for classification task.

        :param metrics: Classification metrics to compute point estimates
        :param class_labels: All classes found in the full dataset (includes train/valid/test sets).
            These should be transformed if using a y transformer.
        :param train_labels: Classes as seen (trained on) by the trained model. These values
            should correspond to the columns of y_pred_probs in the correct order.
        :param sample_weight: Weights for the samples (Does not need
            to match sample weights on the fitted model)
        :param y_transformer: Used to inverse transform labels from `y_test`. Required for non-scalar metrics.
        y_transformer is of type sklearn.base.TransformerMixin
        :param use_binary: Compute metrics only on the true class for binary classification.
        :param enable_metric_confidence: Allow classification metric calculation to include confidence intervals
            This is currently defaulted to False, and will have an automl config setting to enable
        :param multilabel: Indicate if it is multilabel classification.
        :param positive_label: class designed as positive class in binary classification metrics.
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
        :return: None
        """
        self.metrics = metrics if metrics else constants.Metric.CLASSIFICATION_SET_MULTILABEL \
            if multilabel else constants.Metric.CLASSIFICATION_SET_AZURE
        self.enable_metric_confidence = enable_metric_confidence
        if confidence_metrics is None and enable_metric_confidence:
            confidence_metrics = self.metrics
        self.confidence_metrics = confidence_metrics
        self.class_labels = utilities.check_and_convert_to_np(class_labels)
        self.train_labels = utilities.check_and_convert_to_np(train_labels)
        self.sample_weight = utilities.check_and_convert_to_np(sample_weight)

        if self.class_labels is None and self.train_labels is not None:
            self.class_labels = self.train_labels

        if self.train_labels is None and self.class_labels is not None:
            self.train_labels = self.class_labels

        self.y_transformer = y_transformer
        self.use_binary = use_binary
        self.positive_label = positive_label
        self.__custom_dimensions = custom_dimensions
        self.multilabel = multilabel
        super().__init__(log_activity, log_traceback)

    def compute(self, y_test: Union[np.ndarray, pd.DataFrame, List],
                y_pred: Optional[Union[np.ndarray, pd.DataFrame, List]] = None,
                y_pred_probs: Optional[Union[np.ndarray, pd.DataFrame, List]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for classification task based on the config.

        :param y_test: Actual label values
        :param y_pred: Predicted values
        :param y_pred_probs: Predicted probablity values
        :return: Dict of computed metrics

        Example for multiclass classification:
        --------------------------------------
        >>>from azureml.metrics import compute_metrics, constants
        >>>y_pred = [0, 2, 1, 3]
        >>>y_true = [0, 1, 2, 3]
        >>>compute_metrics(task_type=constants.Tasks.CLASSIFICATION, y_test=y_true,
                           y_pred=y_pred)

        Example for multilabel classification:
        --------------------------------------
        >>>from azureml.metrics import compute_metrics
        >>>y_test = np.array([[1, 1, 0],
                        [0, 1, 0],
                        [0, 1, 1],
                        [1, 0, 1]])
        >>>y_pred_proba = np.array([[0.9, 0.6, 0.4],
                                    [0.3, 0.8, 0.6],
                                    [0.1, 0.9, 0.8],
                                    [0.7, 0.1, 0.6]])
        >>>class_labels = np.array([0, 1, 2])
        >>>result = compute_metrics(task_type=constants.Tasks.CLASSIFICATION, y_test=y_test,
                                    y_pred_proba=y_pred_proba, multilabel=True)
        """
        try:
            sklearn_spec = importlib.util.find_spec("sklearn")
            if sklearn_spec is None:
                raise ImportError
            from sklearn.preprocessing import MultiLabelBinarizer
        except ImportError:
            safe_message = "Tabular packages are not available. " \
                           "Please run pip install azureml-metrics[tabular]"
            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )
        y_test = utilities.check_and_convert_to_np(y_test)
        y_pred = utilities.check_and_convert_to_np(y_pred)
        y_pred_probs = utilities.check_and_convert_to_np(y_pred_probs)

        convert_dtypes = utilities.check_for_different_dtype(y_test, y_pred)

        if convert_dtypes:
            y_test, y_pred, self.class_labels, self.train_labels = \
                utilities.convert_to_same_dtype(y_test, y_pred, self.class_labels, self.train_labels)

        if y_test is not None and y_pred is not None and self.y_transformer is None:
            if self.multilabel:
                logger.info("Multilabel is set to True, so we are calculating metrics for multilabel classification")
                if (validate_multilabel_binary_format(y_test, y_pred, y_pred_probs)):
                    if self.class_labels is None:
                        self.class_labels = np.array(range(len(y_test[0])))
                else:
                    if self.class_labels is None:
                        y_test_values = utilities.flatten_array_and_remove_duplicates(y_test)
                        y_pred_values = utilities.flatten_array_and_remove_duplicates(y_pred)
                        total_values = np.array(list(y_test_values.union(y_pred_values)))
                        self.class_labels = np.unique(total_values)

                    self.y_transformer = MultiLabelBinarizer(classes=self.class_labels)
                    self.y_transformer.fit([self.class_labels])
                    y_test = np.array(self.y_transformer.transform(y_test))
                    y_pred = np.array(self.y_transformer.transform(y_pred))

        if y_pred_probs is None and y_pred is not None and hasattr(y_pred, 'shape'):
            if not self.multilabel and y_pred.ndim > 1:
                y_pred_probs = y_pred
                y_pred = None

        if self.class_labels is None:
            if self.train_labels is not None:
                self.class_labels = self.train_labels
            else:
                try:
                    if (y_pred is not None and y_test is not None and self.y_transformer is None) \
                            and not self.multilabel:
                        combined_array = np.concatenate((y_test.flatten(), y_pred.flatten()), axis=None)
                        self.class_labels = np.array(list(np.unique(combined_array)),
                                                     dtype=combined_array.dtype)
                    elif (y_pred is None and y_test is not None) or self.multilabel:
                        if self.multilabel:
                            arr = y_pred_probs if y_pred_probs is None else y_test
                            self.class_labels = np.array(range(len(arr[0])))
                        else:
                            self.class_labels = np.array(np.unique(y_test))
                except Exception as e:
                    error_msg = "Unable to interpret class_labels from y_test or y_pred. " + \
                                "Pass class_labels as additional parameter or " + \
                                "ensure to check elements of y_test and y_pred have same datatype."
                    raise MetricsException(f"{error_msg}\nFound the exception : {e}")

        if self.train_labels is None:
            self.train_labels = self.class_labels

        if (y_pred_probs is not None) and (y_pred is not None):
            if len(self.train_labels) != len(y_pred_probs[0]):
                y_pred_probs = None
                logger.warning("Ignoring y_pred_proba as we found mismatch in length"
                               " of class labels identified from y_test, y_pred and y_pred_proba")

            elif not self.multilabel:
                try:
                    y_pred_from_probs = np.argmax(y_pred_probs, axis=1)
                    class_label_map = {key: label for key, label in enumerate(self.class_labels)}
                    y_pred_from_probs = np.array([class_label_map[key] for key in y_pred_from_probs])

                    same_prediction = (y_pred == y_pred_from_probs).all()
                    if not same_prediction:
                        y_pred_probs = None
                        logger.warning("Ignoring y_pred_proba as predictions indicated from"
                                       " y_pred_probs do not equal y_pred. Send class_labels "
                                       "in same order of y_pred_proba.")
                except Exception as e:
                    y_pred_probs = None
                    logger.warning("Ignoring y_pred_proba as we are not able to parse prediction probabilities "
                                   "because of the following exception : {}".format(e))

        scored_metrics = _scoring._score_classification(
            self._log_activity,
            self._log_traceback,
            y_test,
            y_pred,
            y_pred_probs,
            self.metrics,
            self.class_labels,
            self.train_labels,
            self.sample_weight,
            self.y_transformer,
            multilabel=self.multilabel,
            use_binary=self.use_binary,
            positive_label=self.positive_label
        )

        scored_confidence_intervals = {}
        if self.enable_metric_confidence:
            if y_pred_probs is None:
                warning_msg = "y_pred_probs is missing. Using y_pred as y_pred_probs."
                logger.info(warning_msg)
                if self.multilabel:
                    y_pred_probs = y_pred
                elif y_pred.ndim > 1:
                    y_pred_probs = y_pred
                else:
                    y_pred_probs = np.array([[1 if label == pred else 0 for label in self.class_labels]
                                            for pred in y_pred])

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
                    _scoring_confidence.score_confidence_intervals_classification(
                        self._log_activity,
                        self._log_traceback,
                        y_test,
                        y_pred_probs,
                        confidence_metrics,
                        self.class_labels,
                        self.train_labels,
                        self.sample_weight,
                        self.y_transformer,
                        self.use_binary,
                        self.multilabel,
                        self.positive_label,
                    )

        return self.merge_confidence_interval_metrics(scored_metrics, scored_confidence_intervals)

    @staticmethod
    def list_metrics(multilabel: Optional[bool] = False):
        """Get the list of supported metrics.

            :param multilabel: Accepts a boolean parameter which indicates multilabel classification.
            :return: List of supported metrics (defaults to False).
        """
        supported_metrics = []

        if multilabel:
            supported_metrics = constants.Metric.CLASSIFICATION_SET_MULTILABEL
        else:
            supported_metrics = constants.Metric.CLASSIFICATION_SET

        return supported_metrics

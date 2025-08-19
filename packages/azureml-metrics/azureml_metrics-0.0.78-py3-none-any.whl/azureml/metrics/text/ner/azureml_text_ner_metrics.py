# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to a Text Named Entity Recognition task type."""

import logging
import numpy as np

from typing import Any, Dict, List, Optional, Callable, Iterator, Union

from azureml.metrics import constants, _scoring_utilities
from azureml.metrics.common import utilities
from azureml.metrics.common._metric_base import NonScalarMetric
from azureml.metrics.common._validation import _validate_metrics_list, _check_seq2seq_list_of_list_of_str
from azureml.metrics.common.azureml_metrics import AzureMLMetrics
from azureml.metrics.common.contract import Contract

logger = logging.getLogger(__name__)


class AzureMLTextNERMetrics(AzureMLMetrics):
    """Class for AzureML text ner metrics."""

    def __init__(self,
                 metrics: Optional[List[str]] = None,
                 custom_dimensions: Optional[Dict[str, Any]] = None,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None
                 ) -> None:
        """
        Given the scored data, generate metrics for classification task.

        :param label_list: unique labels list
        :param metrics: Classification metrics to compute point estimates
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
        self.metrics = metrics if metrics else constants.Metric.NER_SET
        self.__custom_dimensions = custom_dimensions
        self.log_activity = log_activity
        self.log_traceback = log_traceback
        super().__init__(log_activity, log_traceback)

    def validate_ner(self,
                     y_test: Union[List[List[str]], np.ndarray],
                     y_pred: Union[List[List[str]], np.ndarray],) -> None:
        """
        Validate the inputs for scoring text named entity recognition

        :param y_test: Actual list of references
        :param y_pred: Actual list of predictions
        :param metrics: Metrics to compute.
        """
        reference_code = "validate_ner"
        _validate_metrics_list("Text NER", self.metrics, constants.Metric.NER_SET,
                               reference_code)

        _check_seq2seq_list_of_list_of_str(y_test, 'y_test', reference_code=reference_code)
        _check_seq2seq_list_of_list_of_str(y_pred, 'y_pred', reference_code=reference_code)

        Contract.assert_true(len(y_test) == len(y_pred), 'Number of samples in y_test and y_pred do not match',
                             log_safe=True, reference_code=reference_code, target='y_test')

        for index, (test, pred) in enumerate(zip(y_test, y_pred)):
            if len(test) != len(pred):
                logger.warning(f'Number of labels in test and pred in sample {index + 1} do not match.'
                               f' Some metrics might be skipped and not computed.')

    def log_ner_debug(self,
                      y_test: Union[List[List[str]], np.ndarray],
                      y_pred: Union[List[List[str]], np.ndarray]) -> None:
        """
        Log shapes of text-ner inputs for debugging.

        :param y_test: Actual list of references
        :param y_pred: Actual list of predictions
        """
        debug_data = {
            'y_test_length': len(y_test),
            'y_pred_length': len(y_pred),
        }

        logger.info("Text-NER metrics debug: {}".format(debug_data))

    def _score_text_ner(self,
                        y_test: Union[List[List[str]], np.ndarray],
                        y_pred: Union[List[List[str]], np.ndarray],) -> Dict[str, Union[float, Dict[str, Any]]]:
        # We are using seqeval to calculate metrics instead of sklearn for other classification problem
        # because seqeval supports evaluation at entity-level

        self.log_ner_debug(y_test, y_pred)
        self.validate_ner(y_test, y_pred)

        results = {}
        for name in self.metrics:
            if name in constants.Metric.NER_SET:
                try:
                    metric_class = _scoring_utilities.get_metric_class_text_ner(name)
                    metric = metric_class(y_test, y_pred)
                    results[name] = metric.compute()
                except MemoryError:
                    raise
                except Exception as e:
                    safe_name = _scoring_utilities.get_safe_metric_name(name)
                    logger.error("Scoring failed for NER metric {}".format(safe_name))
                    self.log_traceback(e, logger, is_critical=False)
                    if utilities.is_scalar(name):
                        results[name] = np.nan
                    else:
                        results[name] = NonScalarMetric.get_error_metric()
        return utilities.segregate_scalar_non_scalar(results)

    def compute(self,
                y_test: np.ndarray,
                y_pred: np.ndarray = None) -> Dict[str, Dict[str, Any]]:
        """
        Compute the metrics.

        :param y_test: Actual label values/label ids
        :param y_pred: Predicted values
        :return: Dict of computed metrics

        >>> from azureml.metrics import compute_metrics, constants
        >>> y_true = [['O', 'O', 'O', 'B-MISC', 'I-MISC', 'I-MISC', 'O'], ['B-PER', 'I-PER', 'O']]
        >>> y_pred = [['O', 'O', 'B-MISC', 'I-MISC', 'I-MISC', 'I-MISC', 'O'], ['B-PER', 'I-PER', 'O']]
        >>> metrics_obj = compute_metrics(task_type=constants.Tasks.TEXT_NER, y_test=y_true, y_pred=y_pred)
        """
        # added this logic for AutoML NLP as it returns result as string
        if isinstance(y_pred, str):
            prediction_str = y_pred
            y_pred = []
            predictions = prediction_str.split("\n\n")

            for prediction in predictions:
                prediction_label = prediction.split("\n")
                pred_labels = [token.split()[1] for token in prediction_label]
                y_pred.append(pred_labels)

        self.validate_ner(y_test, y_pred)
        self.log_ner_debug(y_test, y_pred)

        return self._score_text_ner(
            y_test=y_test,
            y_pred=y_pred,
        )

    @staticmethod
    def list_metrics():
        """Get the list of supported metrics.

            :return: List of supported metrics.
        """
        supported_metrics = constants.Metric.NER_SET
        return supported_metrics

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to Sequence to Sequence Translation task type."""

import logging
import numpy as np

from typing import Any, Dict, List, Optional, Callable, Iterator

from azureml.metrics import constants, _scoring_utilities
from azureml.metrics.common import utilities
from azureml.metrics.common._validation import _validate_metrics_list, _check_seq2seq_list_of_list_of_str, \
    _check_seq2seq_list_of_str, _check_seq2seq_tokenizer, _check_seq2seq_bool
from azureml.metrics.common.azureml_metrics import AzureMLMetrics
from azureml.metrics.common.contract import Contract

logger = logging.getLogger(__name__)


class AzureMLTranslationMetrics(AzureMLMetrics):
    def __init__(self,
                 metrics: Optional[List[str]] = None,
                 tokenizer: Optional[Any] = None,
                 smoothing: Optional[bool] = False,
                 use_static_script: Optional[bool] = False,
                 custom_dimensions: Optional[Dict[str, Any]] = None,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None) -> None:
        """
        Given the references (groundtruth) and hypothesis (prediction),
        generate metrics for translation task.

        :param metrics: Bleu-N metrics to compute point estimates
        :param tokenizer: function that can tokenize input data
        :params smoothing: Boolean to indicate whether to smooth out the bleu score
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
        self.metrics = metrics if metrics else constants.Metric.TRANSLATION_SET
        self.tokenizer = tokenizer
        self.smoothing = smoothing
        self.use_static_script = use_static_script
        self.__custom_dimensions = custom_dimensions
        self.log_activity = log_activity
        self.log_traceback = log_traceback
        super().__init__(log_activity, log_traceback)

    def validate_translation(self,
                             y_test: List[Any],
                             y_pred: List[str],):
        """
        Validate the inputs for translation.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        reference_code = "validate_translation"
        _validate_metrics_list("translation", self.metrics, constants.Metric.TRANSLATION_SET,
                               reference_code)

        _check_seq2seq_list_of_list_of_str(y_test, 'y_test', reference_code=reference_code)
        _check_seq2seq_list_of_str(y_pred, 'y_pred', reference_code=reference_code)
        if self.tokenizer:  # Check for valid tokenizer only if it was passed
            _check_seq2seq_tokenizer(self.tokenizer, 'tokenizer', reference_code=reference_code)
        _check_seq2seq_bool(self.smoothing, 'smoothing', reference_code=reference_code)
        _check_seq2seq_bool(self.use_static_script, 'use_static_script', reference_code=reference_code)
        Contract.assert_true(len(y_test) == len(y_pred), 'Number of samples in y_test and y_pred do not match',
                             log_safe=True, reference_code=reference_code, target='y_test')

    def log_translation_debug(self,
                              y_test: List[Any],
                              y_pred: List[str],) -> None:
        """
        Log shapes of translation inputs for debugging.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        debug_text = 'the quick brown fox jumped over the lazy dog'
        debug_data = {
            'y_test_length': len(y_test),
            'y_pred_length': len(y_pred),
            'tokenizer_example_output': ' '.join(self.tokenizer(debug_text)) if self.tokenizer else debug_text,
            'smoothing': self.smoothing,
            'use_static_script': self.use_static_script,
        }

        logger.info("Translation metrics debug: {}".format(debug_data))

    def _score_translation(
            self,
            y_test: List[Any],
            y_pred: List[str],):
        """
        Compute model evaluation metrics for a translation task.

        y_test should be a list of list of string references (even if there is only one reference)
        y_pred should be a list of string predictions
        """
        results = {}
        for name in self.metrics:
            safe_name = _scoring_utilities.get_safe_metric_name(name)
            max_ngram = constants.Metric.TRANSLATION_NGRAM_MAP[name]
            try:
                metric_class = _scoring_utilities.get_metric_class(name)
                metric = metric_class(y_test, y_pred, self.tokenizer, max_ngram, self.smoothing,
                                      self.use_static_script)
                results[name] = metric.compute()
            except MemoryError:
                raise
            except Exception as e:
                logger.error("Scoring failed for translation metric {}".format(safe_name))
                self.log_traceback(e, logger, is_critical=False)
                results[name] = np.nan
        return utilities.segregate_scalar_non_scalar(results)

    def compute(self, y_test: List[Any], y_pred: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for translation task based on the config.

        :param y_test: Actual list of list of references (Bleu supports multiple references)
        :param y_pred: Actual list of predictions
        :return: Dict of computed metrics
        """
        self.validate_translation(y_test, y_pred)
        self.log_translation_debug(y_test, y_pred)
        scored_metrics = self._score_translation(
            y_test,
            y_pred,
        )

        return scored_metrics

    @staticmethod
    def list_metrics():
        """Get the list of supported metrics.

            :return: List of supported metrics.
        """
        supported_metrics = constants.Metric.TRANSLATION_SET
        return supported_metrics

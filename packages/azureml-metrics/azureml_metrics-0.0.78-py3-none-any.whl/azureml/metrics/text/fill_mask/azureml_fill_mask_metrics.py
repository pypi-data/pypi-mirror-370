# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to Sequence to Sequence Language Modeling task type."""

import logging
from typing import Any, Dict, List, Optional, Callable, Iterator

import numpy as np
from tqdm import tqdm

from azureml.metrics import constants, _scoring_utilities
from azureml.metrics.common import utilities
from azureml.metrics.common._validation import _validate_metrics_list, _check_seq2seq_list_of_str,\
    _check_seq2seq_bool, _check_seq2seq_str, _check_seq2seq_int
from azureml.metrics.common.azureml_metrics import AzureMLMetrics
from azureml.metrics.common.contract import Contract

logger = logging.getLogger(__name__)


class AzureMLFillMaskMetrics(AzureMLMetrics):
    def __init__(self,
                 metrics: Optional[List[str]] = None,
                 model_id: Optional[str] = "gpt2",
                 batch_size: Optional[int] = 16,
                 add_start_token: Optional[bool] = True,
                 custom_dimensions: Optional[Dict[str, Any]] = None,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None) -> None:
        """
        Given the references (groundtruth) and hypothesis (prediction),
        generate metrics for Language Modeling task.

        :param metrics: Rouge metrics to compute point estimates
        :param model_id: model used for calculating Perplexity.
                         Perplexity can only be calculated for causal language models.
        :param batch_size (int): the batch size to run texts through the model. Defaults to 16.
        :param add_start_token (bool): whether to add the start token to the texts,
            so the perplexity can include the probability of the first word. Defaults to True.
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
        self.metrics = metrics if metrics else constants.Metric.FILL_MASK_SET
        self.model_id = model_id
        self.batch_size = batch_size
        self.add_start_token = add_start_token
        self.__custom_dimensions = custom_dimensions
        self.log_activity = log_activity
        self.log_traceback = log_traceback
        super().__init__(log_activity, log_traceback)

    def validate_fill_mask(self,
                           y_test: List[Any],
                           y_pred: List[str],):
        """
        Validate the inputs for QA.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        reference_code = "validate_fill_mask"
        _validate_metrics_list("Fill Masking", self.metrics, constants.Metric.FILL_MASK_SET,
                               reference_code)
        for metric in self.metrics:
            # Special set metrics do not need ground truths or y_test data
            if metric not in constants.Metric.FILL_MASK_SPECIAL_SET:
                _check_seq2seq_list_of_str(y_test, 'y_test', reference_code=reference_code)
                Contract.assert_true(len(y_test) == len(y_pred),
                                     'Number of samples in y_test and y_pred do not match',
                                     log_safe=True, reference_code=reference_code, target='y_test')

        _check_seq2seq_list_of_str(y_pred, 'y_pred', reference_code=reference_code)
        _check_seq2seq_bool(self.add_start_token, 'add_start_token', reference_code=reference_code)
        _check_seq2seq_str(self.model_id, 'model_id', reference_code=reference_code)
        _check_seq2seq_int(self.batch_size, 'batch_size', ignore_none=True, reference_code=reference_code)

    def log_fill_mask_debug(self,
                            y_test: List[Any],
                            y_pred: List[str],) -> None:
        """
        Log shapes of LM inputs for debugging.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        debug_data = {
            'y_test_length': len(y_test) if y_test is not None else 0,
            'y_pred_length': len(y_pred),
            'model_id': self.model_id,
            'batch_size': self.batch_size,
            'add_start_token': self.add_start_token,
        }

        logger.info("Fill Mask metrics debug: {}".format(debug_data))

    def _score_fill_mask(
            self,
            y_test: List[Any],
            y_pred: List[str], ):
        """
        Compute model evaluation metrics for a LM task.

        y_test should be a list of string references
        y_pred should be a list of string predictions

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        :param metrics: List of metric names for metrics to calculate.
        :param metrics: Language Modeling metrics to compute point estimates
        :param model_id: model used for calculating Perplexity.
                            Perplexity can only be calculated for causal language models.
        :param batch_size (int): the batch size to run texts through the model. Defaults to 16.
        :param add_start_token (bool): whether to add the start token to the texts,
            so the perplexity can include the probability of the first word. Defaults to True.
        """
        num_metrics = len(self.metrics)
        results = {}
        with tqdm(total=num_metrics, desc="Computing fill mask metrics") as pbar:
            for name in self.metrics:
                safe_name = _scoring_utilities.get_safe_metric_name(name)
                try:
                    metric_class = _scoring_utilities.get_metric_class(name)
                    metric = metric_class(y_test, y_pred, self.model_id,
                                          self.batch_size, self.add_start_token)
                    results[name] = metric.compute()
                except MemoryError:
                    raise
                except Exception as e:
                    logger.error("Scoring failed for Fill Mask metric {}".format(safe_name))
                    self.log_traceback(e, logger)
                    results[name] = np.nan
                finally:
                    pbar.update(1)
        return utilities.segregate_scalar_non_scalar(results)

    def compute(self, y_test: List[Any], y_pred: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for Language Modeling task based on the config.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        :return: Dict of computed metrics
        """
        self.validate_fill_mask(y_test, y_pred)
        self.log_fill_mask_debug(y_test, y_pred)
        scored_metrics = self._score_fill_mask(y_test, y_pred,)

        return scored_metrics

    @staticmethod
    def list_metrics():
        """Get the list of supported metrics.

            :return: List of supported metrics.
        """
        supported_metrics = constants.Metric.FILL_MASK_SET
        return supported_metrics

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to Sequence to Sequence Text generation task type."""

import logging
import numpy as np
from typing import Any, Dict, List, Optional, Callable, Iterator

from azureml.metrics import constants, _scoring_utilities
from azureml.metrics.common import utilities
from azureml.metrics.common._validation import _validate_metrics_list, _check_seq2seq_list_of_list_of_str, \
    _check_seq2seq_list_of_str, _check_seq2seq_tokenizer, _check_seq2seq_bool, _check_seq2seq_str, _check_seq2seq_int
from azureml.metrics.common.azureml_metrics import AzureMLMetrics
from azureml.metrics.common.contract import Contract

logger = logging.getLogger(__name__)


class AzureMLTextGenerationMetrics(AzureMLMetrics):
    def __init__(self,
                 metrics: Optional[List[str]] = None,
                 tokenizer: Optional[Any] = None,
                 smoothing: Optional[bool] = False,
                 aggregator: Optional[bool] = True,
                 stemmer: Optional[bool] = False,
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
        generate metrics for Text Generation task.

        :param metrics: Rouge and Bleu-N metrics to compute point estimates
        :param tokenizer: function that can tokenize input data
        :params smoothing: Boolean to indicate whether to smooth out the bleu score
        :params aggregator: Boolean to indicate whether to aggregate scores
        :params stemmer: Boolean to indicate whether to use Porter stemmer for word suffixes
        :param model_id: model used for calculating Perplexity.
                         Perplexity can only be calculated for causal language models.
        :param batch_size (int): the batch size to run texts through the model. Defaults to 16.
        :param add_start_token (bool): whether to add the start token to the texts,
            so the perplexity can include the probability of the first word. Defaults to True.
        :param log_activity is a callback to log the activity with parameters
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
        self.metrics = metrics if metrics else constants.Metric.TEXT_GENERATION_SET
        self.tokenizer = tokenizer
        self.smoothing = smoothing
        self.aggregator = aggregator
        self.stemmer = stemmer
        self.model_id = model_id
        self.batch_size = batch_size
        self.add_start_token = add_start_token
        self.__custom_dimensions = custom_dimensions
        self.log_activity = log_activity
        self.log_traceback = log_traceback
        super().__init__(log_activity, log_traceback)

    def validate_text_generation(self,
                                 y_test: List[Any],
                                 y_pred: List[str],):
        """
        Validate the inputs for text generation.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        reference_code = "validate_text_generation"
        _validate_metrics_list("text generation", self.metrics, constants.Metric.TEXT_GENERATION_SET,
                               reference_code)

        ignore_y_test = False
        # y_test can be None for perplexity
        if constants.Metric.FMPerplexity in self.metrics:
            ignore_y_test = True

        _check_seq2seq_list_of_list_of_str(y_test, 'y_test', ignore_none=ignore_y_test,
                                           reference_code=reference_code)
        _check_seq2seq_list_of_str(y_pred, 'y_pred', reference_code=reference_code)
        if self.tokenizer:
            _check_seq2seq_tokenizer(self.tokenizer, 'tokenizer', reference_code=reference_code)
        _check_seq2seq_bool(self.smoothing, 'smoothing', reference_code=reference_code)
        _check_seq2seq_bool(self.aggregator, 'aggregator', reference_code=reference_code)
        _check_seq2seq_bool(self.stemmer, 'stemmer', reference_code=reference_code)
        _check_seq2seq_bool(self.add_start_token, 'add_start_token', reference_code=reference_code)
        _check_seq2seq_str(self.model_id, 'model_id', reference_code=reference_code)
        _check_seq2seq_int(self.batch_size, 'batch_size', ignore_none=True, reference_code=reference_code)
        if y_test is not None:
            Contract.assert_true(len(y_test) == len(y_pred), 'Number of samples in y_test and y_pred do not match',
                                 log_safe=True, reference_code=reference_code, target='y_test')

    def log_text_generation_debug(self,
                                  y_test: List[Any],
                                  y_pred: List[str], ) -> None:
        """
        Log shapes of text generation inputs for debugging.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        debug_text = 'the quick brown fox jumped over the lazy dog'
        debug_data = {
            'y_test_length': len(y_test) if y_test is not None else 0,
            'y_pred_length': len(y_pred),
            'tokenizer_example_output': ' '.join(self.tokenizer(debug_text)) if self.tokenizer else debug_text,
            'smoothing': self.smoothing,
            'aggregator': self.aggregator,
            'stemmer': self.stemmer,
            'model_id': self.model_id,
            'batch_size': self.batch_size,
            'add_start_token': self.add_start_token,
        }

        logger.info("Text generation metrics debug: {}".format(debug_data))

    def _score_text_generation(
            self,
            y_test: List[Any],
            y_pred: List[str],):
        """
        Compute model evaluation metrics for a text generation task.

        y_test should be a list of list of string references
        y_pred should be a list of string predictions

        """
        results = {}
        for name in self.metrics:
            safe_name = _scoring_utilities.get_safe_metric_name(name)
            max_ngram = constants.Metric.TRANSLATION_NGRAM_MAP.get(name, None)
            try:
                metric_class = _scoring_utilities.get_metric_class(name)
                if max_ngram is not None:
                    metric = metric_class(y_test, y_pred, self.tokenizer, max_ngram, self.smoothing)
                elif name in constants.Metric.NONSCALAR_FILL_MASK_SET:
                    metric = metric_class(y_test, y_pred, self.model_id,
                                          self.batch_size, self.add_start_token)
                else:
                    metric = metric_class(y_test, y_pred, [name], self.tokenizer, self.aggregator, self.stemmer)
                computed_result = metric.compute()
                results[name] = computed_result.get(name, None) \
                    if isinstance(computed_result, dict) else computed_result
            except MemoryError:
                raise
            except Exception as e:
                logger.error("Scoring failed for text generation metric {}".format(safe_name))
                self.log_traceback(e, logger, is_critical=False)
                results[name] = np.nan
        return utilities.segregate_scalar_non_scalar(results)

    def compute(self, y_test: List[Any], y_pred: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for Text Generation task based on the config.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        :return: Dict of computed metrics
        """
        self.validate_text_generation(y_test, y_pred)
        self.log_text_generation_debug(y_test, y_pred)
        scored_metrics = self._score_text_generation(
            y_test,
            y_pred,
        )

        return scored_metrics

    @staticmethod
    def list_metrics():
        """Get the list of supported metrics.

            :return: List of supported metrics.
        """
        supported_metrics = constants.Metric.TEXT_GENERATION_SET
        return supported_metrics

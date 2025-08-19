# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to Sequence to Sequence Translation task type."""

import logging

from typing import Any, Dict, List, Optional, Callable, Iterator

from azureml.metrics import constants
from azureml.metrics.common._validation import _validate_metrics_list
from azureml.metrics.tasks.base.dao.azureml_dao import AzureMLDAO
from azureml.metrics.tasks.base.generator.azureml_metrics import AzureMLMetrics

logger = logging.getLogger(__name__)


class AzureMLTranslationMetrics(AzureMLMetrics):
    def __init__(self,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None,
                 **kwargs) -> None:
        """
        Initialize the translation metrics.
        """
        super().__init__(log_activity, log_traceback, **kwargs)
        self.task_type = constants.Tasks.TRANSLATION
        self.metrics = self._get_metrics() + self.custom_metrics

    def _get_metrics(self):
        metrics = list(self.kwargs.get('metrics', constants.Metric.TRANSLATION_SET))
        _validate_metrics_list("translation", metrics, constants.Metric.TRANSLATION_SET,
                               "validate_translation")
        return metrics

    def log_debug(self,
                  y_test: List[Any],
                  y_pred: List[str],
                  metrics_data: AzureMLDAO) -> None:
        """
        Log shapes of translation inputs for debugging.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        :param metrics_data
        """
        debug_text = 'the quick brown fox jumped over the lazy dog'
        debug_data = {
            'y_test_length': len(y_test),
            'y_pred_length': len(y_pred),
            'tokenizer_example_output': ' '.join(
                metrics_data.tokenizer(debug_text)) if metrics_data.tokenizer else debug_text,
            'smoothing': metrics_data.smoothing if metrics_data.smoothing else None,
        }

        logger.info("translation metrics debug: {}".format(debug_data))

    def compute(self, y_test: List[Any], y_pred: List[str], **kwargs) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for translation task based on the config.

        :param y_test: Actual list of list of references (Bleu supports multiple references)
        :param y_pred: Actual list of predictions
        :return: Dict of computed metrics
        """
        scored_metrics = self._score(
            y_test,
            y_pred,
            metrics=self.metrics
        )

        return scored_metrics.to_dict()

    @staticmethod
    def list_metrics():
        """Get the list of supported metrics.

            :return: List of supported metrics.
        """
        supported_metrics = constants.Metric.TRANSLATION_SET
        return supported_metrics

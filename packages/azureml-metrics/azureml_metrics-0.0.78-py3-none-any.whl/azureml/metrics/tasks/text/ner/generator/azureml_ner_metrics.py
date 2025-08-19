# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to NER task type."""

import logging

from typing import Any, Dict, List, Optional, Callable, Iterator

from azureml.metrics.common._validation import _validate_metrics_list
from azureml.metrics.constants import Metric, ReferenceCodes, Tasks
from azureml.metrics.tasks.text.ner.dao.azureml_ner_dao import AzureMLNerDAO
from azureml.metrics.tasks.base.generator.azureml_metrics import AzureMLMetrics

logger = logging.getLogger(__name__)


class AzureMLNerMetrics(AzureMLMetrics):
    def __init__(self,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None,
                 **kwargs) -> None:
        """
        Initialize the NER metrics.
        """
        self.task_type = Tasks.TEXT_NER
        super().__init__(log_activity, log_traceback, **kwargs)

    def _get_metrics(self):
        metrics = list(self.kwargs.get('metrics', Metric.NER_SET) or Metric.NER_SET)
        _validate_metrics_list("Text NER", metrics, Metric.NER_SET, ReferenceCodes.VALIDATE_NER)
        return metrics + self.custom_metrics

    def log_debug(self,
                  y_test: List[Any],
                  y_pred: List[List[str]],
                  metrics_data: AzureMLNerDAO) -> None:
        """
        Log shapes of text-ner inputs for debugging.

        :param y_test: Actual list of references
        :param y_pred: Actual list of predictions
        :param metrics_data
        """
        debug_data = {
            'y_test_length': len(y_test),
            'y_pred_length': len(y_pred),
        }

        logger.info("Text-NER metrics debug: {}".format(debug_data))

    def compute(self, y_test: List[Any], y_pred: List[List[str]], **kwargs) -> Dict[str, Dict[str, Any]]:
        """
        Compute the metrics.

        :param y_test: Actual label values/label ids
        :param y_pred: Predicted values
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
        supported_metrics = Metric.NER_SET
        return supported_metrics

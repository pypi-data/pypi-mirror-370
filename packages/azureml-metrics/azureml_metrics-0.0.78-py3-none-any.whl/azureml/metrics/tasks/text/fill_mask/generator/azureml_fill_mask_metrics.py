# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to Fill Mask task type."""

import logging

from typing import Any, Dict, List, Optional, Callable, Iterator

from azureml.metrics.constants import Metric, ReferenceCodes, Tasks
from azureml.metrics.common._validation import _validate_metrics_list
from azureml.metrics.tasks.text.fill_mask.dao.azureml_fill_mask_dao import AzureMLFillMaskDAO
from azureml.metrics.tasks.base.generator.azureml_metrics import AzureMLMetrics

logger = logging.getLogger(__name__)


class AzureMLFillMaskMetrics(AzureMLMetrics):
    def __init__(self,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None,
                 **kwargs) -> None:
        """
        Initialize the fill mask metrics.
        """
        self.task_type = Tasks.FILL_MASK
        super().__init__(log_activity, log_traceback, **kwargs)

    def _get_metrics(self):
        metrics = list(self.kwargs.get('metrics', Metric.FILL_MASK_SET) or Metric.FILL_MASK_SET)
        _validate_metrics_list(Tasks.FILL_MASK, metrics, Metric.FILL_MASK_SET,
                               ReferenceCodes.VALIDATE_FILL_MASK)
        return metrics + self.custom_metrics

    def log_debug(self,
                  y_test: List[Any],
                  y_pred: List[str],
                  metrics_data: AzureMLFillMaskDAO) -> None:
        """
        Log shapes of LM inputs for debugging.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        :param metrics_data
        """
        debug_data = {
            'y_test_length': len(y_test) if y_test is not None else 0,
            'y_pred_length': len(y_pred),
            'model_id': metrics_data.model_id,
            'batch_size': metrics_data.batch_size,
            'add_start_token': metrics_data.add_start_token,
        }

        logger.info("Fill Mask metrics debug: {}".format(debug_data))

    def compute(self, y_test: List[Any], y_pred: List[str], **kwargs) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for Language Modeling task based on the config.

        :param y_test: Actual list of list of references
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
        supported_metrics = Metric.FILL_MASK_SET
        return supported_metrics

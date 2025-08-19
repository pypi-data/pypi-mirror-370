# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to Sequence to Sequence Summarization task type."""
import logging

from typing import Any, Dict, Optional, Callable, Iterator

from azureml.metrics.tasks.base.generator.azureml_metrics import AzureMLMetrics

logger = logging.getLogger(__name__)


class AzureMLGenericMetrics(AzureMLMetrics):
    def __init__(self,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None,
                 **kwargs) -> None:
        """
        Initialize the summarization metrics.
        """
        super().__init__(log_activity, log_traceback, **kwargs)

    def compute(self,
                y_test: Optional[Any],
                y_pred: Optional[Any] = None,
                **kwargs) -> Dict[str, Dict[str, Any]]:
        """
        Compute all applicable metrices based on the config.

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

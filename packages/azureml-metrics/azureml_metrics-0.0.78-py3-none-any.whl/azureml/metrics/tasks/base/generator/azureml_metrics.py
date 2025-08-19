# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to a Classification task type."""
import inspect
import logging
import numpy as np

from abc import ABC, abstractmethod
from collections import defaultdict
from tqdm import tqdm
from typing import Any, Dict, Optional, Union, Iterator, Callable, List

from azureml.metrics import _scoring_utilities
from azureml.metrics.common.azureml_output_dao import AzureMLOutput
from azureml.metrics.common.exceptions import InvalidOperationException, MetricUnregisteredException
from azureml.metrics.tasks.base.dao.azureml_dao import AzureMLDAO
from azureml.metrics.common.metrics_registry import MetricsRegistry
from azureml.metrics.common import utilities
from azureml.metrics.common._logging_utils import default_log_activity, default_log_traceback
from azureml.metrics.constants import MetricExtrasConstants

logger = logging.getLogger(__name__)


class AzureMLMetrics(ABC):
    """Abstract class for AzureML metrics."""

    def __init__(self,
                 log_activity: Callable[[logging.Logger, str, Optional[str],
                                         Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
                 log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                          Optional[bool], Optional[Any]], None],
                 **kwargs
                 ):
        """
        Initialize the AzureMLMetrics object.
        """
        self._log_activity = log_activity if log_activity else default_log_activity
        self._log_traceback = log_traceback if log_traceback else default_log_traceback
        self.kwargs = kwargs
        self.custom_metrics = self.kwargs.pop('custom_metrics', []) or []
        self.metrics = list(self._get_metrics()) + self.custom_metrics

    def _get_metrics(self):
        """
        Get the metrics from the kwargs. Needs to be overridden by subclass generators for computing default metrices
        """
        metrics = self.kwargs.get('metrics', []) or []
        return metrics

    def log_debug(self,
                  y_test: List[Any],
                  y_pred: List[str],
                  metrics_data: AzureMLDAO) -> None:
        """
        Log shapes of  inputs for debugging. Should be overriden by derived classes to enhance logging experience.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        :param metrics_data : Metrics DAO object
        """
        debug_data = {
            'y_test_length': len(y_test) if y_test is not None else 0,
            'y_pred_length': len(y_pred) if y_pred is not None else 0,
        }
        logger.info("Metrics debug: {}".format(debug_data))

    @abstractmethod
    def compute(self,
                y_test: Optional[Any],
                y_pred: Optional[Any] = None,
                **kwargs) -> Union[Any, Dict[str, Any]]:
        """
        Compute all metrics for classification task based on the config.

        :param y_test: Actual label values
        :param y_pred: Predicted values
        :return: Dict of computed metrics
        """
        pass

    def merge_confidence_interval_metrics(self, scored_metrics: Dict[str, Any],
                                          scored_confidence_intervals: Dict[str, Any]):
        """
        Merge the regular and confidence interval scores.

        :param scored_metrics regular scores for the task
        :param scored_confidence_intervals confidence intervals.
        """
        scored_metrics = utilities.amalgamate_scalar_non_scalar(scored_metrics)
        scored_confidence_intervals = utilities.amalgamate_scalar_non_scalar(scored_confidence_intervals)
        joined_metrics = {}  # type: Dict[str, Any]
        for metric in scored_metrics.keys():

            computed_metric = scored_metrics[metric]
            joined_metrics[metric] = computed_metric

            if metric in scored_confidence_intervals:
                ci_metric = scored_confidence_intervals[metric]  # type: Dict[str, Any]
                ci_metric[MetricExtrasConstants.VALUE] = computed_metric
                joined_metrics[MetricExtrasConstants.MetricExtrasFormat.format(metric)] = ci_metric
        return utilities.segregate_scalar_non_scalar(joined_metrics)

    def get_daos(self, metrices, y_test=None, y_pred=None, y_pred_proba=None, **kwargs) -> Dict[AzureMLDAO, list]:
        """
        Get the unique DAO classes for the given metrics. One metric_name can have multiple DAOs based on
         data/task_type. Only one Dao should be applicable for the given (metric, data, task_type) combination.
        This method returns a dict of DAOs and the metrics that are applicable for that DAO.


        :return: Dict of dtos
        """
        result = defaultdict(list)
        for metric in metrices:
            try:
                possible_metric_data = MetricsRegistry.get_dao_classes(metric) or [AzureMLDAO]
            except MetricUnregisteredException as e:
                logger.warning("Skipping the computation of {} due to the following exception : {}".format(metric, e))
                continue
            except Exception as e:
                raise e
            metric_data_class = possible_metric_data[0]
            if len(possible_metric_data) > 1:
                metric_data_class = None
                # This solves the case when same metric name could have different implementations based on
                # y_test/y_pred type
                for dao in possible_metric_data:
                    try:
                        if metric_data_class is not None:
                            raise InvalidOperationException(
                                "Multiple DTOs applicable for the given (metric, data  additional arguments). Each "
                                "(metric, data, additional argument) combination should yield only one unique dao.")
                        metric_data_class = dao(y_test=y_test, y_pred=y_pred, y_pred_proba=y_pred_proba,
                                                **kwargs).__class__
                    except Exception as e:
                        logger.info(
                            "Skipping the computation of {} due to the following exception: {}".format(metric, e))
                        continue
                if metric_data_class is None:
                    raise InvalidOperationException("No dao suitable for the given data for metric: {}".format(metric))
            result[metric_data_class].append(metric)
        return result

    def get_metric_classes(self, daos) -> Dict[Any, Any]:
        """
        Get Metric Classes from (name, data_class).
        :return: Dict of metrics
        """
        metric_class_dao_mapping = defaultdict(list)
        for dao, metrics in daos.items():
            for metric in metrics:
                try:
                    metric_class = MetricsRegistry.get_metric_class(metric, dao)
                    metric_class_dao_mapping[(metric_class, dao)].append(metric)
                except Exception as e:
                    logger.warning(
                        "Skipping the computation of {} due to error: {}".format(metric, e))
                    continue
        return metric_class_dao_mapping

    def _score(
        self,
        y_test: List[Any],
        y_pred: List[Any],
        y_pred_proba: List[Any] = None,
        metrics=None
    ) -> AzureMLOutput:
        """
        Compute model evaluation metrics for a given list of metrics.

        This method computes the model evaluation metrics for a list of metrics provided.
        It first gets the Data Access Objects (DAOs) for the metrics and then gets the metric classes for these DAOs.
        It then computes the metrics for each metric class and updates the results.

        Parameters:
        y_test (List[Any]): The actual label values.
        y_pred (List[Any]): The predicted label values.
        y_pred_proba (List[Any], optional): The predicted probabilities. Defaults to None.
        metrics (List[str], optional): The list of metrics to compute. Defaults to None.

        Returns:
        AzureMLOutput: An object of AzureMLOutput class which contains the computed metrics.
        """
        if metrics is None:
            metrics = []
        results = AzureMLOutput()
        dao_metric_mapping = self.get_daos(metrics, y_test, y_pred)
        metric_dao_mapping = self.get_metric_classes(dao_metric_mapping)

        num_metrics = len(metrics)
        with tqdm(total=num_metrics, desc="Computing metrics") as pbar:
            for metric_data_class, metrices in metric_dao_mapping.items():
                safe_names = ', '.join([_scoring_utilities.get_safe_metric_name(name) for name in metrices])
                metric_class, data_class = metric_data_class
                metric_dict = {
                    **self.kwargs,
                    'metrics': metrices
                }
                data = data_class(y_test=y_test, y_pred=y_pred, y_pred_proba=y_pred_proba, **metric_dict)
                self.log_debug(y_test, y_pred, data)
                try:
                    if inspect.isclass(metric_class):
                        results.update(metric_class(data).compute())
                    else:
                        result = metric_class.compute(**data.kwargs)
                        # For custom prompt, this needs to be fixed
                        if isinstance(result, dict):
                            results.update(AzureMLOutput(**result))
                        else:
                            results.update(result)  # This is for Custom prompt metrics
                        # registered as custom objects
                except MemoryError:
                    raise
                except Exception as e:
                    logger.error("Scoring failed for metrics {}".format(safe_names))
                    self._log_traceback(e, logger, is_critical=False)
                    for name in metrices:
                        results.add_value(name, np.nan)
                finally:
                    pbar.update(1)
        return results

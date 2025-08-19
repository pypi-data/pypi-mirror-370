# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for computing model evaluation metrics."""
import numpy as np
import pandas as pd
import logging
import time
import uuid

from typing import Any, Dict, List, Optional, Tuple, Union
from time import gmtime, strftime

from azureml.metrics import constants
from azureml.metrics.common.azureml_custom_prompt_metric import AzureMLCustomPromptMetric
from azureml.metrics.common.exceptions import ClientException, HFEvaluateClientException, \
    MissingDependencies, DataErrorException
from azureml.metrics.common._logging_utils import default_log_activity, default_log_traceback


logger = logging.getLogger(constants.TelemetryConstants.APP_NAME)


def get_metric_task(metric: str) -> str:
    """
    Get the task for a given metric.

    :param metric: The metric to lookup.
    :return: The task type for the given metric.
    """
    if metric in constants.Metric.CLASSIFICATION_SET:
        return constants.Tasks.CLASSIFICATION
    elif metric in constants.Metric.REGRESSION_SET:
        return constants.Tasks.REGRESSION
    safe_message = "Metric {} not found".format(metric)
    raise ClientException(safe_message, target="metric_name", reference_code="utilities.get_metric_task",
                          safe_message=safe_message)


def minimize_or_maximize(metric: str,
                         task: Optional[str] = None) -> str:
    """
    Select the objective given a metric.

    Some metrics should be minimized and some should be maximized
    :param metric: the name of the metric to look up
    :return: returns one of constants.OptimizerObjectives.
    """
    if task is None:
        task = get_metric_task(metric)
    return constants.OBJECTIVES_TASK_MAP[task][metric]


def is_better(val1: float,
              val2: float,
              metric: Optional[str] = None,
              objective: Optional[str] = None) -> bool:
    """Select the best of two values given metric or objectives.

    :param val1: scalar value
    :param val2: scalar value
    :param metric: the name of the metric to look up
    :param objective: one of constants.OptimizerObjectives.
    :return: returns a boolean of if val1 is better than val2 in the situation
    """
    if objective is None:
        if metric is None:
            safe_message = "Must specific either metric or objective"
            raise ClientException(safe_message, target="metric_name", reference_code="utilities.is_better",
                                  safe_message=safe_message)
        else:
            objective = minimize_or_maximize(metric)
    if objective == constants.MAXIMIZE:
        return val1 > val2
    elif objective == constants.MINIMIZE:
        return val1 < val2
    return False


def get_all_nan(task: str) -> Dict[str, float]:
    """Create a dictionary of metrics to values for the given task.

    All metric values are set to nan initially
    :param task: one of constants.Tasks.
    :return: returns a dictionary of nans for each metric for the task.
    """
    return {m: np.nan for m in constants.METRICS_TASK_MAP[task]}


def get_metric_ranges(task: str) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Get the metric range for the task.

    :param task: Machine learning task.
    :return: Tuple with dictionaries of minimum and maximum scores.
    """
    minimums = get_min_values(task)
    maximums = get_max_values(task)
    return minimums, maximums


def get_worst_values(task: str) -> Dict[str, float]:
    """
    Get the worst possible scores for metrics of the task.

    :param task: Machine learning task.
    :return: Dictionary from metric names to the worst scores.
    """
    minimums, maximums = get_metric_ranges(task)
    task_objectives = constants.OBJECTIVES_TASK_MAP[task]

    worst_scores = dict()
    for metric_name, objective in task_objectives.items():
        if metric_name == constants.TrainingResultsType.TRAIN_TIME:
            worst_scores[metric_name] = constants.SCORE_UPPER_BOUND
            continue

        if objective == constants.MAXIMIZE:
            worst_scores[metric_name] = minimums[metric_name]
        else:
            worst_scores[metric_name] = maximums[metric_name]
    return worst_scores


def get_min_values(task: str) -> Dict[str, float]:
    """Get the minimum values for metrics for the task.

    :param task: string "classification" or "regression"
    :return: returns a dictionary of metrics with the min values.
    """
    task_ranges = constants.RANGES_TASK_MAP[task]  # type: Dict[str, Tuple[float, float]]
    return {metric_name: lower for metric_name, (lower, _) in task_ranges.items()}


def get_max_values(task: str) -> Dict[str, float]:
    """
    Get the maximum scores for metrics of the task.

    :param task: Machine learning task.
    :return: Dictionary of metrics with the maximum scores.
    """
    task_ranges = constants.RANGES_TASK_MAP[task]  # type: Dict[str, Tuple[float, float]]
    return {metric_name: upper for metric_name, (_, upper) in task_ranges.items()}


def assert_metrics_sane(scores: Dict[str, Any], task: str) -> None:
    """
    Assert that the given scores are within the valid range.

    This only checks the lower bound (upper for minimizing metrics).

    :param scores: Dictionary from metric name to metric score.
    :param task: Task name.
    """
    worst_scores = get_worst_values(task)
    objectives = constants.OBJECTIVES_TASK_MAP[task]
    for metric_name, score in scores.items():
        if not np.isscalar(score) or np.isnan(score):
            continue

        worst_value = worst_scores[metric_name]
        if objectives[metric_name] == constants.MAXIMIZE:
            if score < worst_value:
                message = "Score out of bounds for maximizing metric {}: {} < {}".format(
                    metric_name, score, worst_value)
                safe_message = "Score out of bounds for maximizing metric"
                raise ClientException(message, target="task", reference_code="utilities.assert_metrics_sane",
                                      safe_message=safe_message)

        elif objectives[metric_name] == constants.MINIMIZE:
            if score > worst_value:
                message = "Score out of bounds for minimizing metric {}: {} > {}".format(
                    metric_name, score, worst_value)
                safe_message = "Score out of bounds for minimizing metric"
                raise ClientException(message, target="task", reference_code="utilities.assert_metrics_sane",
                                      safe_message=safe_message)

        else:
            safe_message = "Cannot validate metric bounds for metrics that are not minimizing or maximizing"
            raise ClientException(safe_message, target="metric_name", reference_code="utilities.assert_metrics_sane",
                                  safe_message=safe_message)


def get_scalar_metrics(task: str) -> List[str]:
    """Get the scalar metrics supported for a given task.

    :param task: Task string, (e.g. "classification" or "regression")
    :return: List of the default metrics supported for the task
    """
    return {
        constants.Tasks.CLASSIFICATION: list(constants.Metric.SCALAR_CLASSIFICATION_SET),
        constants.Tasks.REGRESSION: list(constants.Metric.SCALAR_REGRESSION_SET),
    }[task]


def get_default_metrics(task: str) -> List[str]:
    """Get the metrics supported for a given task as a set.

    :param task: Task string, (e.g. "classification" or "regression")
    :return: List of the default metrics supported for the task
    """
    return {
        constants.Tasks.CLASSIFICATION: list(constants.Metric.CLASSIFICATION_SET
                                             - constants.Metric.UNSUPPORTED_CLASSIFICATION_TABULAR_SET),
        constants.Tasks.REGRESSION: list(constants.Metric.REGRESSION_SET),
    }[task]


def is_scalar(metric_name: str, metric_value: Any = None) -> bool:
    """
    Check whether a given metric is scalar or nonscalar.

    :param metric_name: the name of the metric found in constants.py
    :param metric_value: the value of metric computed
    :return: boolean for if the metric is scalar
    """
    if metric_name.endswith(constants.MetricExtrasConstants.MetricExtrasSuffix):
        metric_name = metric_name[:-len(constants.MetricExtrasConstants.MetricExtrasSuffix)]
    if metric_name in constants.FULL_SCALAR_SET:
        # only scalar values are expected in "metrics" and non scalar values can be in "artifacts"
        if metric_value is not None and isinstance(metric_value, List):
            return False
        return True
    # accepting pass@k metrics as scalar metrics.
    # added the condition check as 'k' value can be variable.
    elif constants.CodeGenerationConstants.CODE_GENERATION_PREFIX in metric_name:
        return True
    elif metric_name in constants.FULL_NONSCALAR_SET:
        return False
    elif metric_name in constants.FULL_CLASSWISE_SET:
        return False
    elif metric_name in [constants.ChatCompletionConstants.CONVERSATION_NUMBER,
                         constants.ChatCompletionConstants.TURN_NUMBER]:
        return False
    safe_message = "{} metric is not supported".format(metric_name)
    raise ClientException(safe_message, target="metric_name", reference_code="utilities.is_scalar",
                          safe_message=safe_message)


def is_classwise(metric_name: str) -> bool:
    """
    Check whether a given metric is a classwise metric.

    :param metric_name: the name of the metric found in constants.py
    :return: boolean for if the metric is scalar
    """
    if metric_name in constants.FULL_CLASSWISE_SET:
        return True
    else:
        return False
    safe_message = "{} metric is not supported".format(metric_name)
    raise ClientException(safe_message, target="metric_name", reference_code="utilities.is_classwise",
                          safe_message=safe_message)


def segregate_scalar_non_scalar(metrics: Dict[str, Any], task_type: str = None) -> Dict[str, Dict[str, Any]]:
    metrics_result: Dict[str, Dict[str, Any]] = {
        constants.Metric.Metrics: dict(),
        constants.Metric.Artifacts: dict()
    }
    for metric_name, metric_value in metrics.items():
        try:
            # Metrics to be aggregated
            aggregate_metric_scores(metric_name, metric_value, metrics_result, task_type)
        except Exception as e:
            logger.warning("Failed to aggregate the scores for metric : {} "
                           "with the following exception : {}".format(metric_name, e))

        if is_scalar(metric_name, metric_value):
            metrics_result[constants.Metric.Metrics][metric_name] = metric_value
        else:
            metrics_result[constants.Metric.Artifacts][metric_name] = metric_value
    return metrics_result


def aggregate_metric_scores(metric_name, metric_value, metrics_result, task_type=None):
    """Helper function to aggregate the possible artifact metrics"""
    if metric_name in constants.Metric.NONSCALAR_RAG_EVALUATION_SET and \
            task_type in [constants.Tasks.CHAT_COMPLETION, constants.Tasks.RAG_EVALUATION]:
        if isinstance(metric_value, dict):
            mean_metric_name = constants.MetricExtrasConstants.MeanExtrasFormat.format(metric_name)
            metrics_result[constants.Metric.Metrics][mean_metric_name] = np.nanmean(
                metric_value[constants.ChatCompletionConstants.SCORE_PER_CONVERSATION])
    # if task_type == constants.Tasks.CHAT_COMPLETION and isinstance(metric_value, list):
    #     if metric_value is not None and isinstance(metric_value[0], list):
    #         mean_metric_name = constants.MetricExtrasConstants.MeanExtrasFormat.format(metric_name)
    #         metrics_result[constants.Metric.Metrics][mean_metric_name] = np.nanmean(
    #             [np.nanmean(sublist) for sublist in metric_value])
    elif metric_name in constants.Metric.NON_AGGREGATED_METRICS:
        if isinstance(metric_value, list):
            first_element = metric_value[0] if metric_value else None
            if isinstance(first_element, str):  # convert list of string to list of numbers
                metric_value = [float(x) for x in metric_value if x.replace(".", "", 1).isdigit()]
            mean_metric_name = constants.MetricExtrasConstants.MeanExtrasFormat.format(metric_name)
            median_metric_name = constants.MetricExtrasConstants.MedianExtrasFormat.format(metric_name)
            metrics_result[constants.Metric.Metrics][mean_metric_name] = np.nanmean(metric_value)
            metrics_result[constants.Metric.Metrics][median_metric_name] = np.nanmedian(metric_value)
        elif isinstance(metric_value, dict):
            for key, value in metric_value.items():
                if isinstance(value, list):
                    mean_metric_name = constants.MetricExtrasConstants.MeanExtrasDictFormat.format(metric_name, key)
                    metrics_result[constants.Metric.Metrics][mean_metric_name] = np.nanmean(value)


def amalgamate_scalar_non_scalar(metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if constants.Metric.Metrics in metrics and constants.Metric.Artifacts in metrics:
        return {**metrics[constants.Metric.Metrics], **metrics[constants.Metric.Artifacts]}
    return {}


def concatenate_calculated_metrics(calculated_metrics_list: List[Dict]) -> Dict[str, Any]:
    computed_metrics = {"metrics": {}, "artifacts": {}}

    for calculated_metric in calculated_metrics_list:
        for key, value in calculated_metric.items():
            computed_metrics[key].update(value)

    return computed_metrics


def check_and_convert_to_np(arr: Optional[Union[np.ndarray, pd.DataFrame, List]]):
    if arr is not None:
        if isinstance(arr, pd.DataFrame):
            if len(arr.columns) == 1:
                return arr.iloc[:, 0].to_numpy()
            else:
                return arr.to_numpy()

        elif isinstance(arr, pd.Series):
            return arr.to_numpy()

        elif isinstance(arr, List):
            return np.array(arr)
    return arr


def check_for_different_dtype(y_test: Optional[Union[np.ndarray, pd.DataFrame, List]],
                              y_pred: Optional[Union[np.ndarray, pd.DataFrame, List]]):
    """validates y_test and y_pred datatype and returns True if they are different"""
    y_test = check_and_convert_to_np(y_test)
    y_pred = check_and_convert_to_np(y_pred)

    if ((isinstance(y_test, np.ndarray) and len(y_test) >= 1)
            and (isinstance(y_pred, np.ndarray) and len(y_pred) >= 1)):

        y_test_dtype = check_homogeneous_type(y_test)
        y_pred_dtype = check_homogeneous_type(y_pred)

        if y_test_dtype is False or y_pred_dtype is False:
            raise DataErrorException("y_test or y_pred are having mix of labels with different datatype.")

        elif y_test_dtype != y_pred_dtype and y_pred.ndim == 1:
            return True

    return False


def convert_to_same_dtype(y_test: Optional[Union[np.ndarray, pd.DataFrame, List]],
                          y_pred: Optional[Union[np.ndarray, pd.DataFrame, List]],
                          class_labels: Optional[Union[np.ndarray, List]],
                          train_labels: Optional[Union[np.ndarray, List]]):
    """converts y_test, y_pred, class_labels, train_labels to same dtype."""
    y_test = np.array([str(label) for label in y_test])
    y_pred = np.array([str(label) for label in y_pred])

    class_labels = np.array([str(label) for label in class_labels]) \
        if class_labels is not None else None
    train_labels = np.array([str(label) for label in train_labels]) \
        if train_labels is not None else None

    logger.warning("Warning: y_test and y_pred have different datatypes,"
                   + "converting both of them to string type.")

    return y_test, y_pred, class_labels, train_labels


def check_homogeneous_type(arr):
    """checks if all the values in the array of same datatype."""
    value = iter(arr)
    first_data_type = type(next(value))
    return first_data_type if all((type(x) is first_data_type) for x in value) else False


def flatten_array_and_remove_duplicates(arr):
    """flattens the array to return individual elements without duplicates."""
    arr = np.array(arr).flatten()

    values_list = []

    for row in arr:
        if isinstance(row, np.ndarray) or isinstance(row, list):
            for value in row:
                if value is not None:
                    values_list.append(value)
        elif row is not None:
            values_list.append(row)

    values = set(values_list)
    return values


def get_supported_metrics(kwargs, special_metric_set):
    metrics_list = kwargs.get("metrics", set())
    supported_metrics_list = set(metrics_list).intersection(special_metric_set)
    kwargs["metrics"] = [metric for metric in special_metric_set] \
        if len(supported_metrics_list) == 0 else supported_metrics_list
    logger.warning(f"Computing metrics for {kwargs['metrics']} as y_test is None.")


def retry(max_attempts, delay):
    def decorator_retry(func):
        def wrapper_retry(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    result = func(*args, **kwargs)
                    return result
                except MissingDependencies:
                    # safe_message = "required packages are not available in the current environment."
                    # raise MissingDependencies(
                    #     safe_message, safe_message=safe_message
                    # )
                    raise
                except Exception as e:
                    logger.warning("Failed to load metric from HuggingFace Evaluate: {}. "
                                   "Trying again in {} seconds. Remaining {} "
                                   "attempts".format(str(e), delay, max_attempts - attempts - 1))
                    attempts += 1
                    time.sleep(delay)
            safe_message = "Failed to load metric from Hugging Face Evaluate after maximum retry " \
                           "attempts. Please try again after sometime."
            raise HFEvaluateClientException(safe_message, target="metric_name", reference_code="utilities.retry",
                                            safe_message=safe_message)
        return wrapper_retry
    return decorator_retry


def check_kwargs(kwargs: Dict, task_type: constants.Tasks, task_type_args: List[str]) -> None:
    """Check for presence of any additional kwargs which are unrelated/typos.

        :param kwargs: additional/ununsed keyword arguments.
        :param task_type: Accepts an argument of type constants.Tasks for which metrics have to be computed.
            Can accept from any of the values constants.Tasks.CLASSIFICATION, constants.Tasks.REGRESSION,
            constants.Tasks.TEXT_CLASSIFICATION, constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL,
            constants.Tasks.TEXT_NER.
        :param task_type_args: keyword arguments based on task type.
    """
    if len(kwargs) > 0:
        unused_keys = list(kwargs.keys())
        warning_message = f"We have unused keyword arguments : {unused_keys}\n" + \
                          f"Applicable keyword arguments for {task_type} are {task_type_args}."

        logger.warning(warning_message)


def extract_common_kwargs(kwargs, task_type=None):
    metrics_run_id = str(uuid.uuid4())
    current_timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    # Reading common keyword arguments related to telemetry
    metrics_custom_dimensions = {
        "app_name": constants.TelemetryConstants.APP_NAME,
        "task_type": task_type,
        "azureml_metrics_run_id": metrics_run_id,
        "current_timestamp": current_timestamp,
    }

    custom_dimensions = kwargs.pop('custom_dimensions', metrics_custom_dimensions)
    # TODO: use only default_log_activity and default_log_traceback
    # log_activity = kwargs.pop('log_activity', default_log_activity)
    # log_traceback = kwargs.pop('log_traceback', default_log_traceback)
    common_args = ["custom_dimensions", "log_activity", "log_traceback"]
    return common_args, custom_dimensions, default_log_activity, default_log_traceback


def compute_custom_prompt_metrics(kwargs):
    """Helper method to compute custom prompt metrics"""
    metrics_list = kwargs.get("metrics", None)
    custom_prompt_metric_results = []

    if metrics_list is None or not isinstance(metrics_list, list):
        return {}
    elif len(metrics_list) == 0:
        return {}

    custom_prompt_metrics = [metric for metric in metrics_list if isinstance(metric, AzureMLCustomPromptMetric)]

    # remove custom prompt metrics from the metrics list
    metrics_list = [metric for metric in metrics_list if not isinstance(metric, AzureMLCustomPromptMetric)]
    kwargs["metrics"] = metrics_list

    # return empty dict if no custom prompt metrics are present
    if len(custom_prompt_metrics) == 0:
        return {}

    else:
        for metric in custom_prompt_metrics:
            current_metric_results = metric.compute(**kwargs)
            custom_prompt_metric_results.append(current_metric_results)

    return concatenate_calculated_metrics(custom_prompt_metric_results)


def format_rouge_scores(rouge_scores, name):
    """Code to remove values from the dictionary"""
    formatted_scores = []
    for outer_list in rouge_scores:
        inner_list = []
        for item in outer_list:
            inner_list.append(item[name])
        formatted_scores.append(inner_list)

    return formatted_scores

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to Sequence to Sequence Summarization task type."""

import logging

from typing import Any, Dict, Optional, Callable, Iterator

from azureml.metrics import MetricsRegistry, constants
from azureml.metrics.common.utilities import extract_common_kwargs
from azureml.metrics.common.azureml_custom_prompt_metric import AzureMLCustomPromptMetric
from azureml.metrics.tasks.base.generator.azureml_metrics import AzureMLMetrics

logger = logging.getLogger(__name__)


class AzureMLCustomPromptMetricsGenerator(AzureMLMetrics):
    def __init__(self,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None,
                 **kwargs) -> None:
        """
        Initialize the summarization metrics.
        Todo: This cusrrently doesn't support custom_metrics if the task_type is set to custom_prompt
        """
        super().__init__(log_activity, log_traceback, **kwargs)

    def _score_custom_prompt(
            self,
            **kwargs, ):
        """
        Register Custom Prompt metric and return the name of the metric
        """
        custom_metric_name = kwargs.pop("custom_metric_name",
                                        constants.DefaultValues.DEFAULT_CUSTOM_PROMPT_METRIC_NAME)
        custom_metric_description = kwargs.pop("custom_metric_description", None)
        prompt_instruction = kwargs.pop("prompt_instruction", None)
        few_shot_examples = kwargs.pop("few_shot_examples", None)
        placeholder_prompt = kwargs.pop("placeholder_prompt", None)
        user_prompt_template = kwargs.pop("user_prompt_template", None)
        input_vars = kwargs.pop("input_vars", None)
        system_prompt_template = kwargs.pop("system_prompt_template", None)

        # dataframe which contain the data required for computing custom prompt
        custom_prompt_data = kwargs.pop("custom_prompt_data", None)

        openai_api_batch_size = kwargs.pop("openai_api_batch_size", 20) if isinstance(
            kwargs.get("openai_api_batch_size", 20), int) and kwargs.get("openai_api_batch_size", 20) > 0 else 20
        use_openai_endpoint = kwargs.pop("use_openai_endpoint", False)
        openai_params = kwargs.pop("openai_params", None)
        use_chat_completion_api = kwargs.pop("use_chat_completion_api", None)

        # kwargs for llama params
        # llm_params = kwargs.pop("llm_params", None)
        # llm_api_batch_size = kwargs.pop("llm_api_batch_size", 20) \
        #     if isinstance(kwargs.get("llm_api_batch_size", 20), int) \
        #     and kwargs.get("llm_api_batch_size", 20) > 0 else 20
        if use_chat_completion_api is True:
            openai_api_batch_size = 1
        common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(
            kwargs, task_type=constants.Tasks.CUSTOM_PROMPT_METRIC)
        with log_activity(logger=logger,
                          activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                          activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(
                              constants.Tasks.CUSTOM_PROMPT_METRIC),
                          custom_dimensions=custom_dimensions):
            metrics = AzureMLCustomPromptMetric(
                metric_name=custom_metric_name,
                metric_description=custom_metric_description,
                prompt_instruction=prompt_instruction,
                few_shot_examples=few_shot_examples,
                placeholder_prompt=placeholder_prompt,
                user_prompt_template=user_prompt_template,
                input_vars=input_vars,
                system_prompt_template=system_prompt_template,
                custom_prompt_data=custom_prompt_data,
                openai_api_batch_size=openai_api_batch_size,
                use_openai_endpoint=use_openai_endpoint,
                openai_params=openai_params,
                use_chat_completion_api=use_chat_completion_api,
                **kwargs
            )
            MetricsRegistry.register(custom_metric_name, metrics)
            return custom_metric_name

    def compute(self, y_test, y_pred, **kwargs) -> Dict[str, Dict[str, Any]]:
        """
        Compute Custom Prompt metrics.

        :param y_test: Actual list of list of references (Bleu supports multiple references)
        :param y_pred: Actual list of predictions
        :return: Dict of computed metrics
        """
        metric_name = self._score_custom_prompt(
            **self.kwargs
        )
        metrices = self.metrics + [metric_name]
        scored_metrics = self._score(
            y_test,
            y_pred,
            metrics=metrices
        )
        return scored_metrics.to_dict()

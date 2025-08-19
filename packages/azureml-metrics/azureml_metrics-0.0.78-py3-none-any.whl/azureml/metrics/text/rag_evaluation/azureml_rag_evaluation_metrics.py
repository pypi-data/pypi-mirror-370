# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to RAG_EVALUATION task type."""

import logging
from typing import Any, Dict, List, Optional, Callable, Iterator

from azureml.metrics import constants
from azureml.metrics.common import _scoring
from azureml.metrics.common.azureml_metrics import AzureMLMetrics
from azureml.metrics.text.rag_evaluation._rag_utils import get_prompt_prefix

logger = logging.getLogger(__name__)


class AzureMLRagEvaluationMetrics(AzureMLMetrics):
    def __init__(self,
                 metrics: Optional[List[str]] = None,
                 openai_params: Optional[dict] = None,
                 openai_api_batch_size: Optional[int] = 20,
                 use_chat_completion_api: Optional[bool] = None,
                 llm_params: Optional[dict] = None,
                 llm_api_batch_size: Optional[int] = 20,
                 score_version: Optional[str] = "v1",
                 use_previous_conversation: Optional[bool] = False,
                 custom_dimensions: Optional[Dict[str, Any]] = None,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None) -> None:
        """
        Given the conversation history and the generated response,
        generate metrics for RAG Evaluation task.

        :param metrics: RAG Evaluation Metrics to provide the score with the help of LLMs
        :param openai_params: Dictionary containing credentials to initialize or setup LLM
        :param openai_api_batch_size: number of prompts to be batched in one API call.
        :param use_chat_completion_api: boolean flag to choose between openAI completion vs chat completion API.
        :param llm_params: Dictionary containing credentials to initialize or setup LLM
        :param llm_api_batch_size: number of prompts to be batched in one API call for LLM
        :param score_version: Version of rag evaluation metrics to be computed
        :param use_previous_conversation: boolean value to indicate if we need to use_previous_conversation
             for computing rag-evaluation metrics.
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
        self.metrics = metrics if metrics else constants.Metric.RAG_EVALUATION_SET
        self.openai_params = openai_params
        self.openai_api_batch_size = openai_api_batch_size
        self.use_chat_completion_api = use_chat_completion_api
        self.llm_params = llm_params
        self.llm_api_batch_size = llm_api_batch_size
        self.score_version = score_version
        self.use_previous_conversation = use_previous_conversation

        self.__custom_dimensions = custom_dimensions
        super().__init__(log_activity, log_traceback)

    def compute(self, y_test: List[Any], y_pred: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for Chat completion task based on the config.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        :return: Dict of computed metrics
        """
        scored_metrics = _scoring._score_rag_evaluation(
            self._log_activity,
            self._log_traceback,
            y_test,
            y_pred,
            self.metrics,
            self.openai_params,
            self.openai_api_batch_size,
            self.use_chat_completion_api,
            self.llm_params,
            self.llm_api_batch_size,
            self.score_version,
            self.use_previous_conversation
        )

        return scored_metrics

    @staticmethod
    def get_prompt_template(file_path, version, prompt_type):
        prompt_prefix = get_prompt_prefix(file_path, version, prompt_type)
        prompt_template = ''.join((prompt_prefix.strip()))
        return prompt_template

    @staticmethod
    def list_metrics():
        """Get the list of supported metrics.

            :return: List of supported metrics.
        """
        supported_metrics = constants.Metric.RAG_EVALUATION_SET
        return supported_metrics

    @staticmethod
    def list_prompts(metric_name: str) -> str:
        """
        Get the prompt template for the given metric.
        """
        version = "v1"
        if metric_name in [constants.Metric.RAG_GPTGroundedness]:
            prompt = AzureMLRagEvaluationMetrics.get_prompt_template("grounding_prompt.toml",
                                                                     version, "grounding")
        elif metric_name in [constants.Metric.RAG_GPTRetrieval]:
            prompt = AzureMLRagEvaluationMetrics.get_prompt_template("retrieval_prompt.toml",
                                                                     version, "retrieval")
        elif metric_name in [constants.Metric.RAG_GPTRelevance]:
            prompt = AzureMLRagEvaluationMetrics.get_prompt_template("generation_prompt_without_gt.toml",
                                                                     version, "generation")
        else:
            prompt = "Prompt template for {} is not available.".format(metric_name)

        return prompt

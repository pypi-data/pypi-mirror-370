# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to Sequence to Sequence Chat completion task type."""

import logging
from typing import Any, Dict, List, Optional, Callable, Iterator

from azureml.metrics import constants
from azureml.metrics.common import _scoring
from azureml.metrics.common.azureml_metrics import AzureMLMetrics

logger = logging.getLogger(__name__)


class AzureMLChatCompletionMetrics(AzureMLMetrics):
    def __init__(self,
                 metrics: Optional[List[str]] = None,
                 tokenizer: Optional[Any] = None,
                 smoothing: Optional[bool] = False,
                 aggregator: Optional[bool] = True,
                 stemmer: Optional[bool] = False,
                 use_static_script: Optional[bool] = True,
                 model_id: Optional[str] = "gpt2",
                 batch_size: Optional[int] = 16,
                 add_start_token: Optional[bool] = True,
                 openai_params: Optional[dict] = None,
                 openai_api_batch_size: Optional[int] = 20,
                 use_chat_completion_api: Optional[bool] = None,
                 llm_params: Optional[dict] = None,
                 llm_api_batch_size: Optional[int] = 20,
                 score_version: Optional[str] = "v1",
                 use_previous_conversation: Optional[bool] = False,
                 score_all_conversations: Optional[bool] = False,
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
        :param use_static_script: Boolean to indicate whether to use static script
            for computing bleu and rouge scores
        :param model_id: model used for calculating Perplexity.
                         Perplexity can only be calculated for causal language models.
        :param batch_size (int): the batch size to run texts through the model. Defaults to 16.
        :param add_start_token (bool): whether to add the start token to the texts,
            so the perplexity can include the probability of the first word. Defaults to True.
        :param openai_params: Dictionary containing credentials to initialize or setup LLM
        :param openai_api_batch_size: number of prompts to be batched in one API call.
        :param use_chat_completion_api: boolean flag to choose between openAI completion vs chat completion API.
        :param llm_params: Dictionary containing credentials to initialize or setup LLM
        :param llm_api_batch_size: number of prompts to be batched in one API call for LLM
        :param score_version: Version of rag evaluation metrics to be computed
        :param use_previous_conversation: boolean value to indicate if we need to use_previous_conversation
             for computing rag-evaluation metrics.
        :param score_all_conversations: boolean value to indicate to calculate scores for all conversations by
             by appending all assistant responses.
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
        self.metrics = metrics if metrics \
            else constants.Metric.CHAT_COMPLETION_SET if openai_params is not None \
            else constants.Metric.CHAT_COMPLETION_NONGPT_SET
        self.tokenizer = tokenizer
        self.smoothing = smoothing
        self.aggregator = aggregator
        self.stemmer = stemmer
        self.use_static_script = use_static_script
        self.model_id = model_id
        self.batch_size = batch_size
        self.add_start_token = add_start_token
        self.openai_params = openai_params
        self.openai_api_batch_size = openai_api_batch_size
        self.use_chat_completion_api = use_chat_completion_api
        self.llm_params = llm_params
        self.llm_api_batch_size = llm_api_batch_size
        self.score_version = score_version
        self.use_previous_conversation = use_previous_conversation
        self.score_all_conversations = score_all_conversations
        self.__custom_dimensions = custom_dimensions
        super().__init__(log_activity, log_traceback)

    def compute(self, y_test: List[Any], y_pred: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for Chat completion task based on the config.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        :return: Dict of computed metrics
        """
        scored_metrics = _scoring._score_chat_completion(
            self._log_activity,
            self._log_traceback,
            y_test,
            y_pred,
            self.metrics,
            self.tokenizer,
            self.smoothing,
            self.aggregator,
            self.stemmer,
            self.use_static_script,
            self.model_id,
            self.batch_size,
            self.add_start_token,
            self.openai_params,
            self.openai_api_batch_size,
            self.use_chat_completion_api,
            self.llm_params,
            self.llm_api_batch_size,
            self.score_version,
            self.use_previous_conversation,
            self.score_all_conversations,
        )

        return scored_metrics

    @staticmethod
    def list_metrics():
        """Get the list of supported metrics.

            :return: List of supported metrics.
        """
        supported_metrics = constants.Metric.CHAT_COMPLETION_SET
        return supported_metrics

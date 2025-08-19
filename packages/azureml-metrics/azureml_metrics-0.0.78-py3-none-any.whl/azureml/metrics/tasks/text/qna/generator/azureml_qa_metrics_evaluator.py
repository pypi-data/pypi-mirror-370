# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to Sequence to Sequence QA task type."""

import logging
import os
from typing import Any, Dict, List, Optional, Callable, Iterator, Union

from azureml.metrics import constants
from azureml.metrics.common._validation import _validate_metrics_list
from azureml.metrics.tasks.base.generator.azureml_metrics import AzureMLMetrics
from azureml.metrics.common.import_utilities import load_jinja2_utils
from azureml.metrics.tasks.text.qna.dao.azureml_qna_dao import AzureMLQnADAO

logger = logging.getLogger(__name__)


class AzureMLQAMetrics(AzureMLMetrics):
    def __init__(self,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None,
                 **kwargs) -> None:
        """

        """
        super().__init__(log_activity, log_traceback, **kwargs)

    def _get_metrics(self):
        metrics = list(
            self.kwargs.get('metrics', constants.Metric.QA_SET) or constants.Metric.QA_SET)
        _validate_metrics_list("QA", metrics, constants.Metric.QA_SET, "validate_qa")
        # Todo: Remove below checks and let metrics classes decide if solvable or not because if user passes just
        #  metrics list (no task type) this will not help
        if self.kwargs.get("openai_params") is None and \
                len(set(metrics).intersection(constants.Metric.QA_GPT_METRICS_SET)) > 0:
            supported_metrics = set(metrics).difference(constants.Metric.QA_GPT_METRICS_SET)
            metrics = list(supported_metrics)
            logger.warning("Skipping the computation of GPT related metrics as openai_params are not provided."
                           "Computing metrics for {}".format(metrics))
        if self.kwargs.get("llm_params") is None and \
                len(set(metrics).intersection(constants.Metric.QA_LLM_METRICS_SET)) > 0:
            supported_metrics = set(metrics).difference(constants.Metric.QA_LLM_METRICS_SET)
            metrics = list(supported_metrics)
            logger.warning("Skipping the computation of LLM related metrics as llm_params are not provided. "
                           "Computing metrics for {}".format(metrics))
        return metrics

    def log_debug(self,
                  y_test: Union[List[Any], None],
                  y_pred: List[str],
                  metrics_data: AzureMLQnADAO) -> None:
        """
        Log shapes of QA inputs for debugging.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        debug_text = 'the quick brown fox jumped over the lazy dog'
        debug_data = {
            'y_test_length': len(y_test) if y_test is not None else 0,
            'y_pred_length': len(y_pred),
            'tokenizer_example_output': ' '.join(
                metrics_data.tokenizer(debug_text)) if metrics_data.tokenizer else debug_text,
            'regexes_to_ignore': ' '.join(
                metrics_data.regexes_to_ignore) if metrics_data.regexes_to_ignore else '',
            'ignore_case': metrics_data.ignore_case,
            'ignore_punctuation': metrics_data.ignore_punctuation,
            'ignore_numbers': metrics_data.ignore_numbers,
            'lang': metrics_data.lang,
            'model_type': metrics_data.model_type,
            'idf': metrics_data.idf,
            'rescale_with_baseline': metrics_data.rescale_with_baseline,
            'questions_length': len(metrics_data.questions) if metrics_data.questions is not None else 0,
            'contexts_length': len(metrics_data.contexts) if metrics_data.contexts is not None else 0,
            'openai_api_batch_size': metrics_data.openai_api_batch_size,
            'using_openai_endpoint': metrics_data.use_openai_endpoint,
            'using_openai_api': metrics_data.openai_params is not None,
            'max_concurrent_requests': metrics_data.max_concurrent_requests,
            'use_chat_completion_api': metrics_data.use_chat_completion_api,
            'openai_embedding_engine': metrics_data.openai_embedding_engine,
            'using_llm_api': metrics_data.llm_params is not None,
            'llm_api_batch_size': metrics_data.llm_api_batch_size,
            'llm_use_chat_completion_payload': metrics_data.llm_use_chat_completion_payload,
        }

        logger.info("QA metrics debug: {}".format(debug_data))

    def compute(self, y_test: List[Any], y_pred: List[str], **kwargs) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for QA task based on the config.

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
    def get_prompt_template(file_path, **kwargs):
        """
        Given a file_path to a jinja2 template, render the template by replacing the variables in the template
        """
        Environment, FileSystemLoader = load_jinja2_utils()
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompt_templates')

        env = Environment(loader=FileSystemLoader(searchpath=template_dir), autoescape=True)

        template = env.get_template(file_path)
        return template.render(**kwargs)

    @staticmethod
    def list_metrics():
        """Get the list of supported metrics.

            :return: List of supported metrics.
        """
        supported_metrics = constants.Metric.QA_SET
        return supported_metrics

    @staticmethod
    def list_prompts(metric_name: str) -> str:
        """
        Get the prompt template for the given metric.
        """
        if metric_name in [constants.Metric.LLMSimilarity, constants.Metric.GPTSimilarity]:
            prompt = AzureMLQAMetrics.get_prompt_template("similarity_score_qa.jinja2")
        elif metric_name in [constants.Metric.LLMCoherence, constants.Metric.GPTCoherence]:
            prompt = AzureMLQAMetrics.get_prompt_template("coherence_score_qa.jinja2")
        elif metric_name in [constants.Metric.LLMRelevance, constants.Metric.GPTRelevance]:
            prompt = AzureMLQAMetrics.get_prompt_template("relevance_score_qa.jinja2")
        elif metric_name in [constants.Metric.LLMFluency, constants.Metric.GPTFluency]:
            prompt = AzureMLQAMetrics.get_prompt_template("fluency_score_qa.jinja2")
        elif metric_name in [constants.Metric.LLMGroundedness, constants.Metric.GPTGroundedness]:
            prompt = AzureMLQAMetrics.get_prompt_template("groundedness_score_qa.jinja2")
        else:
            prompt = "Prompt template for {} is not available.".format(metric_name)

        return prompt

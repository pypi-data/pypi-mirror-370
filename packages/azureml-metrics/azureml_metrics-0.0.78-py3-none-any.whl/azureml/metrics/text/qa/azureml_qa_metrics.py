# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to Sequence to Sequence QA task type."""

import logging
import os
import numpy as np
from typing import Any, Dict, List, Optional, Callable, Iterator, Union

from azureml.metrics import constants, _scoring_utilities
from azureml.metrics.common import utilities
from azureml.metrics.common._validation import _validate_metrics_list, _check_seq2seq_list_of_str, \
    _check_seq2seq_tokenizer, _check_seq2seq_bool, _check_seq2seq_list_of_list_of_str, \
    _check_seq2seq_str, _check_seq2seq_dict, _check_seq2seq_int
from azureml.metrics.common.azureml_metrics import AzureMLMetrics
from azureml.metrics.common.contract import Contract
from azureml.metrics.common.import_utilities import load_jinja2_utils

logger = logging.getLogger(__name__)


class QASplitTokenizer:
    def __call__(self, line):
        """Tokenizes an input line using split() on whitespace

        :param line: a segment to tokenize
        :return: the tokenized line
        """

        return line.split()


class AzureMLQAMetrics(AzureMLMetrics):
    def __init__(self,
                 metrics: Optional[List[str]] = None,
                 tokenizer: Optional[Any] = None,
                 regexes_to_ignore: Optional[List[str]] = None,
                 ignore_case: Optional[bool] = False,
                 ignore_punctuation: Optional[bool] = False,
                 ignore_numbers: Optional[bool] = False,
                 lang: Optional[str] = "en",
                 model_type: Optional[str] = None,
                 idf: Optional[bool] = False,
                 rescale_with_baseline: Optional[bool] = True,
                 questions: Optional[List[str]] = None,
                 contexts: Optional[List[str]] = None,
                 openai_api_batch_size: Optional[int] = 20,
                 use_openai_endpoint: Optional[bool] = False,
                 openai_params: Optional[dict] = None,
                 max_concurrent_requests: Optional[int] = None,
                 use_chat_completion_api: Optional[bool] = None,
                 openai_embedding_engine: Optional[str] = None,
                 llm_params: Optional[dict] = None,
                 llm_api_batch_size: Optional[int] = 20,
                 llm_use_chat_completion_payload: Optional[bool] = False,
                 custom_dimensions: Optional[Dict[str, Any]] = None,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None) -> None:
        """
        Given the references (groundtruth) and hypothesis (prediction),
        generate metrics for QA task.

        :param metrics: question answerng metrics to compute point estimates
        :param tokenizer: function that can tokenize input data
        :params regexes_to_ignore: List of string regular expressions to ignore
        :params ignore_case: Boolean to indicate whether to ignore case
        :params ignore_punctuation: Boolean to indicate whether to ignore punctuation
        :params ignore_numbers: Boolean to indicate whether to ignore numbers
        :params lang: String value to indicate the language of provided data.
        :param model_type: String to indicate the type of model while computing BERT score.
        :param idf: Boolean to indicate whether to use idf while computing BERT score.
        :param rescale_with_baseline: Boolean to indicate if we need to rescale BERT score.
        :param questions: Question used for the data sample used in computation of gpt-similarity metric.
        :param contexts: Context information used in Question Answering task for computing gpt-related metrics.
        :param openai_api_batch_size: number of prompts to be batched in one API call.
        :param openai_params: Dictionary containing credentials for openai API.
        :param max_concurrent_requests: maximum number of concurrent async requests to openai API.
        :param use_chat_completion_api: boolean flag to choose between openAI completion vs chat completion API.
        :param openai_embedding_engine: String to indicate the type of embedding engine to be used.
        :param llm_params: Dictionary containing api information related to any LLM.
        :param llm_api_batch_size: number of prompts to be batched in one LLM API call
        :param llm_use_chat_completion_payload: boolean flag to choose chat completion payload for LLM endpoint.
        :param custom_dimensions to report the telemetry data.
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
        self.metrics = metrics if metrics else constants.Metric.QA_SET
        self.tokenizer = tokenizer if tokenizer else QASplitTokenizer()
        self.regexes_to_ignore = regexes_to_ignore
        self.ignore_case = ignore_case
        self.ignore_punctuation = ignore_punctuation
        self.ignore_numbers = ignore_numbers
        self.lang = lang
        self.model_type = model_type
        self.idf = idf
        self.rescale_with_baseline = rescale_with_baseline
        self.questions = questions
        self.contexts = contexts
        self.openai_api_batch_size = openai_api_batch_size
        self.use_openai_endpoint = use_openai_endpoint
        self.openai_params = openai_params
        self.max_concurrent_requests = max_concurrent_requests
        self.use_chat_completion_api = use_chat_completion_api
        self.openai_embedding_engine = openai_embedding_engine
        self.llm_params = llm_params
        self.llm_api_batch_size = llm_api_batch_size
        self.llm_use_chat_completion_payload = llm_use_chat_completion_payload
        self.__custom_dimensions = custom_dimensions
        self.log_activity = log_activity
        self.log_traceback = log_traceback
        super().__init__(log_activity, log_traceback)

    def validate_qa(self,
                    y_test: Union[List[Any], None],
                    y_pred: List[str],):
        """
        Validate the inputs for QA.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        reference_code = "validate_qa"
        _validate_metrics_list("QA", self.metrics, constants.Metric.QA_SET, reference_code)
        for metric in self.metrics:
            # metrics in QA_SPECIAL_SET does not require ground_truths
            if metric not in constants.Metric.QA_SPECIAL_SET:
                _check_seq2seq_list_of_str(y_test, 'y_test', reference_code=reference_code, ignore_none=True)
                if y_test is not None:
                    Contract.assert_true(
                        len(y_test) == len(y_pred), 'Number of samples in y_test and y_pred do not match',
                        log_safe=True, reference_code=reference_code, target='y_test')

        _check_seq2seq_list_of_str(y_pred, 'y_pred', reference_code=reference_code)
        self.validate_qa_params(reference_code)

    def validate_qa_params(self, reference_code):
        if self.tokenizer:
            _check_seq2seq_tokenizer(self.tokenizer, 'tokenizer', reference_code=reference_code)
        if self.regexes_to_ignore:  # if regexes to ignore is provided, it should be a list of string
            _check_seq2seq_list_of_str(self.regexes_to_ignore, 'regexes_to_ignore', reference_code=reference_code)
        _check_seq2seq_bool(self.ignore_case, 'ignore_case', reference_code=reference_code)
        _check_seq2seq_bool(self.ignore_punctuation, 'ignore_punctuation', reference_code=reference_code)
        _check_seq2seq_bool(self.ignore_numbers, 'ignore_numbers', reference_code=reference_code)
        _check_seq2seq_str(self.lang, 'lang', ignore_none=True, reference_code=reference_code)
        _check_seq2seq_str(self.model_type, 'model_type', ignore_none=True, reference_code=reference_code)
        _check_seq2seq_bool(self.idf, 'idf', ignore_none=True, reference_code=reference_code)
        _check_seq2seq_bool(self.rescale_with_baseline, 'rescale_with_baseline', ignore_none=True,
                            reference_code=reference_code)
        _check_seq2seq_list_of_str(self.questions, 'questions', ignore_none=True, reference_code=reference_code)
        _check_seq2seq_list_of_str(self.contexts, 'contexts', ignore_none=True, reference_code=reference_code)
        _check_seq2seq_int(self.openai_api_batch_size, 'openai_api_batch_size', reference_code=reference_code)
        _check_seq2seq_bool(self.use_openai_endpoint, 'use_openai_endpoint', ignore_none=True,
                            reference_code=reference_code)
        _check_seq2seq_dict(self.openai_params, 'openai_params', ignore_none=True, reference_code=reference_code)
        _check_seq2seq_int(self.max_concurrent_requests, 'max_concurrent_requests', ignore_none=True,
                           reference_code=reference_code)
        _check_seq2seq_bool(self.use_chat_completion_api, 'use_chat_completion_api', ignore_none=True,
                            reference_code=reference_code)
        _check_seq2seq_str(self.openai_embedding_engine, 'openai_embedding_engine', ignore_none=True,
                           reference_code=reference_code)
        _check_seq2seq_dict(self.llm_params, 'llm_params', ignore_none=True, reference_code=reference_code)
        _check_seq2seq_int(self.llm_api_batch_size, 'llm_api_batch_size', ignore_none=True,
                           reference_code=reference_code)
        _check_seq2seq_bool(self.llm_use_chat_completion_payload, 'llm_use_chat_completion_payload',
                            ignore_none=True, reference_code=reference_code)

    def log_qa_debug(self,
                     y_test: Union[List[Any], None],
                     y_pred: List[str],) -> None:
        """
        Log shapes of QA inputs for debugging.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        debug_text = 'the quick brown fox jumped over the lazy dog'
        debug_data = {
            'y_test_length': len(y_test) if y_test is not None else 0,
            'y_pred_length': len(y_pred),
            'tokenizer_example_output': ' '.join(self.tokenizer(debug_text)) if self.tokenizer else debug_text,
            'regexes_to_ignore': ' '.join(self.regexes_to_ignore) if self.regexes_to_ignore else '',
            'ignore_case': self.ignore_case,
            'ignore_punctuation': self.ignore_punctuation,
            'ignore_numbers': self.ignore_numbers,
            'lang': self.lang,
            'model_type': self.model_type,
            'idf': self.idf,
            'rescale_with_baseline': self.rescale_with_baseline,
            'questions_length': len(self.questions) if self.questions is not None else 0,
            'contexts_length': len(self.contexts) if self.contexts is not None else 0,
            'openai_api_batch_size': self.openai_api_batch_size,
            'use_openai_endpoint': self.use_openai_endpoint,
            'using_openai_api': self.openai_params is not None,
            'max_concurrent_requests': self.max_concurrent_requests,
            'use_chat_completion_api': self.use_chat_completion_api,
            'openai_embedding_engine': self.openai_embedding_engine,
            'using_llm_api': self.llm_params is not None,
            'llm_api_batch_size': self.llm_api_batch_size,
            'llm_use_chat_completion_payload': self.llm_use_chat_completion_payload,
        }

        logger.info("QA metrics debug: {}".format(debug_data))

    def validate_qa_multiple_ground_truth(self,
                                          y_test: List[Any],
                                          y_pred: List[str],):
        """
        Validate the inputs for QA with multiplt ground truth.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        reference_code = "validate_qa_multiple_ground_truth"
        _validate_metrics_list("QA Multiple Ground Truth", self.metrics, constants.Metric.QA_MULTIPLE_GROUND_TRUTH_SET,
                               reference_code)
        for metric in self.metrics:
            if metric not in constants.Metric.QA_SPECIAL_SET:
                _check_seq2seq_list_of_list_of_str(y_test, 'y_test', ignore_none=True,
                                                   reference_code=reference_code)
            if y_test is not None:
                Contract.assert_true(
                    len(y_test) == len(y_pred), 'Number of samples in y_test and y_pred do not match',
                    log_safe=True, reference_code=reference_code, target='y_test')

        _check_seq2seq_list_of_str(y_pred, 'y_pred', reference_code=reference_code)
        self.validate_qa_params(reference_code=reference_code)

    def _score_qa(
            self,
            y_test: List[Any],
            y_pred: List[str],):
        """
        Compute model evaluation metrics for a QA task.

        y_test should be a list of string references
        y_pred should be a list of string predictions
        tokenizer could be any function that takes input a string, and returns a
        list of tokens

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        """
        results = {}
        for name in self.metrics:
            safe_name = _scoring_utilities.get_safe_metric_name(name)
            try:
                metric_class = _scoring_utilities.get_metric_class(name)
                if name in [constants.Metric.GPTGroundedness,
                            constants.Metric.LLMGroundedness]:
                    metric = metric_class(y_pred, self.tokenizer, self.contexts, self.openai_params,
                                          self.max_concurrent_requests,
                                          self.regexes_to_ignore, self.ignore_case, self.ignore_punctuation,
                                          self.ignore_numbers, self.lang, self.use_openai_endpoint,
                                          self.openai_api_batch_size,
                                          self.use_chat_completion_api, self.llm_params, self.llm_api_batch_size)
                else:
                    metric = metric_class(y_test, y_pred, self.tokenizer, self.regexes_to_ignore,
                                          self.ignore_case, self.ignore_punctuation, self.ignore_numbers,
                                          self.lang, self.model_type, self.idf, self.rescale_with_baseline,
                                          self.questions, self.contexts, self.use_openai_endpoint,
                                          self.openai_api_batch_size,
                                          self.openai_params, self.max_concurrent_requests,
                                          self.use_chat_completion_api, self.openai_embedding_engine,
                                          self.llm_params, self.llm_api_batch_size,
                                          self.llm_use_chat_completion_payload)
                results[name] = metric.compute()

                if name in constants.Metric.QA_GPT_STAR_METRICS_SET | constants.Metric.QA_LLM_METRICS_SET:
                    metric_results = results[name]
                    formatted_results = []
                    for result_value in metric_results:
                        try:
                            formatted_result = int(result_value)
                        except Exception:
                            formatted_result = float(np.nan)
                        formatted_results.append(formatted_result)
                    results[name] = formatted_results

            except MemoryError:
                raise
            except Exception as e:
                logger.error("Scoring failed for QA metric {}".format(safe_name))
                self.log_traceback(e, logger, is_critical=False)
                if results.get(name, None) is None:
                    if utilities.is_scalar(name):
                        results[name] = np.nan
                    else:
                        results[name] = [float(np.nan) for _ in range(len(y_pred))]
        return utilities.segregate_scalar_non_scalar(results)

    def compute(self, y_test: List[Any], y_pred: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for QA task based on the config.

        :param y_test: Actual list of list of references
        :param y_pred: Actual list of predictions
        :return: Dict of computed metrics
        """
        if self.openai_params is None:
            supported_metrics = set(self.metrics).difference(constants.Metric.QA_GPT_METRICS_SET)
            self.metrics = list(supported_metrics)
            logger.warning("GPT related metrics need openai_params to be computed. "
                           "Computing metrics for {}".format(self.metrics))

        if self.llm_params is None:
            supported_metrics = set(self.metrics).difference(constants.Metric.QA_LLM_METRICS_SET)
            self.metrics = list(supported_metrics)
            logger.warning("LLM related metrics need llm_params to be computed. "
                           "Computing metrics for {}".format(self.metrics))

        if y_test is not None and isinstance(y_test[0], list):
            # for question-answering with multiple ground truth
            self.validate_qa_multiple_ground_truth(y_test, y_pred)
        else:
            self.validate_qa(y_test, y_pred)

        self.log_qa_debug(y_test, y_pred)

        scored_metrics = self._score_qa(
            y_test,
            y_pred,
        )

        return scored_metrics

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

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AzureMLSummarizationDAO class."""
import logging
from functools import cached_property

from azureml.metrics.common._validation import _check_seq2seq_bool, _check_seq2seq_tokenizer, \
    _check_seq2seq_list_of_list_of_str, _check_seq2seq_list_of_str, _check_seq2seq_str, _check_seq2seq_int, \
    _check_seq2seq_dict
from azureml.metrics.constants import (ConcurrencyConstants, ReferenceCodes, TelemetryConstants, Metric,
                                       AggregationConstants)
from azureml.metrics.tasks.base.dao.azureml_dao import AzureMLDAO

logger = logging.getLogger(TelemetryConstants.APP_NAME)


class QASplitTokenizer:
    def __call__(self, line):
        """Tokenizes an input line using split() on whitespace

        :param line: a segment to tokenize
        :return: the tokenized line
        """

        return line.split()


class AzureMLQnADAO(AzureMLDAO):
    """Data Access Object for metrices similar to QnA"""

    def __init__(self, y_test, y_pred, **kwargs):
        """
        Initialize the AzureMLQnADAO.
        """
        super().__init__(y_test, y_pred, **kwargs)

    @property
    def reference_validation_str(self):
        """Returns reference validation string for QnA."""
        return ReferenceCodes.VALIDATE_QNA

    # def validate_if_dao_applicable(self):
    #     """
    #     Ensures that these dao gets picked only if data and kwargs are of required format
    #     Todo: Remove this if not absolutely necessary
    #     Commented out to keep this as reference if needed for some task
    #     """
    #     super().validate_if_dao_applicable()
    #     task_type = self.kwargs.get("task_type", None)
    #     supported_task_type_value = task_type in [None, constants.Tasks.QUESTION_ANSWERING, constants.Tasks.DEFAULT]
    #     Contract.assert_true(supported_task_type_value,
    #                          f"For the provided data, the metric can't be computed for {task_type}",
    #                          target=task_type,
    #                          reference_code=self.reference_validation_str)

    @cached_property
    def generated_contents(self):
        """
        Returns the generated contents
        """
        return self.y_pred

    def _prep_y_pred(self, y_pred):
        """Preprocess and validate the y_pred data"""
        _check_seq2seq_list_of_str(y_pred, 'y_pred', reference_code=self.reference_validation_str)
        return y_pred

    def _prep_y_test(self, y_test):
        """Preprocess and validate the y_test data"""
        # Check if y_test is a list of strings and convert it to a list of lists of strings
        # To support multiple ground truth answers
        is_list_of_strings = all(isinstance(x, str) for x in y_test)
        if is_list_of_strings:
            y_test = [[row] for row in y_test]
        _check_seq2seq_list_of_list_of_str(y_test, 'y_test', reference_code=self.reference_validation_str)
        return y_test

    @cached_property
    def aggregate_function(self):
        """Returns and validates the aggregate_function for the task. If not provided, returns 'average'."""
        aggregate_function = self.kwargs.get('aggregate_function', AggregationConstants.MAX)
        _check_seq2seq_str(aggregate_function, 'aggregate_function', reference_code=self.reference_validation_str)
        return aggregate_function

    @cached_property
    def aggregate_metrics(self):
        """Returns and validates the aggregate_metrics for the task. If not provided, returns None."""
        aggregate_metrics = self.kwargs.get('aggregate_metrics', [Metric.QAExactMatch, Metric.QAF1Score])
        _check_seq2seq_list_of_str(aggregate_metrics, 'aggregate_metrics', ignore_none=True,
                                   reference_code=self.reference_validation_str)
        return aggregate_metrics

    @cached_property
    def tokenizer(self):
        """Returns and validates the tokenizer for the task. If not provided, returns the default tokenizer."""
        tokenizer = self.kwargs.get('tokenizer', QASplitTokenizer())
        if tokenizer is not None:
            _check_seq2seq_tokenizer(tokenizer, 'tokenizer', reference_code=self.reference_validation_str)
        return tokenizer

    @cached_property
    def regexes_to_ignore(self):
        """Returns and validates the regexes to ignore for the task. If not provided, returns None."""
        regexes_to_ignore = self.kwargs.get('regexes_to_ignore', None)
        if regexes_to_ignore is not None:
            _check_seq2seq_list_of_str(regexes_to_ignore, 'regexes_to_ignore',
                                       reference_code=self.reference_validation_str)
        return regexes_to_ignore

    @cached_property
    def ignore_case(self):
        """Returns and validates the ignore_case for the task. If not provided, returns False."""
        ignore_case = self.kwargs.get('ignore_case', False)
        _check_seq2seq_bool(ignore_case, 'ignore_case', reference_code=self.reference_validation_str)
        return ignore_case

    @cached_property
    def ignore_punctuation(self):
        """Returns and validates the ignore_punctuation for the task. If not provided, returns False."""
        ignore_punctuation = self.kwargs.get('ignore_punctuation', False)
        _check_seq2seq_bool(ignore_punctuation, 'ignore_punctuation', reference_code=self.reference_validation_str)
        return ignore_punctuation

    @cached_property
    def ignore_numbers(self):
        """Returns and validates the ignore_numbers for the task. If not provided, returns False."""
        ignore_numbers = self.kwargs.get('ignore_numbers', False)
        _check_seq2seq_bool(ignore_numbers, 'ignore_numbers', reference_code=self.reference_validation_str)
        return ignore_numbers

    @cached_property
    def lang(self):
        """Returns and validates the lang for the task. If not provided, returns 'en'."""
        lang = self.kwargs.get('lang', "en")
        _check_seq2seq_str(lang, 'lang', ignore_none=True, reference_code=self.reference_validation_str)
        return lang

    @cached_property
    def model_type(self):
        """Returns and validates the model_type for the task. If not provided, returns None."""
        model_type = self.kwargs.get('model_type', "microsoft/deberta-large")
        _check_seq2seq_str(model_type, 'model_type', ignore_none=True, reference_code=self.reference_validation_str)
        return model_type

    @cached_property
    def idf(self):
        """Returns and validates the idf for the task. If not provided, returns False."""
        idf = self.kwargs.get('idf', False)
        _check_seq2seq_bool(idf, 'idf', ignore_none=True, reference_code=self.reference_validation_str)
        return idf

    @cached_property
    def rescale_with_baseline(self):
        """Returns and validates the rescale_with_baseline for the task. If not provided, returns True."""
        rescale_with_baseline = self.kwargs.get('rescale_with_baseline', True)
        _check_seq2seq_bool(rescale_with_baseline, 'rescale_with_baseline', ignore_none=True,
                            reference_code=self.reference_validation_str)
        return rescale_with_baseline

    @cached_property
    def questions(self):
        """Returns and validates the questions for the task. If not provided, returns None."""
        questions = self.kwargs.get('questions', None)
        _check_seq2seq_list_of_str(questions, 'questions', ignore_none=True,
                                   reference_code=self.reference_validation_str)
        return questions

    @cached_property
    def contexts(self):
        """Returns and validates the contexts for the task. If not provided, returns None."""
        contexts = self.kwargs.get('contexts', None)
        _check_seq2seq_list_of_str(contexts, 'contexts', ignore_none=True,
                                   reference_code=self.reference_validation_str)
        return contexts

    @cached_property
    def openai_api_batch_size(self):
        """Returns and validates the openai_api_batch_size for the task. If not provided, returns 1."""
        if self.use_chat_completion_api is True:
            return 1
        batch_size = self.kwargs.get('batch_size', 20)
        batch_size = batch_size if isinstance(batch_size, int) and batch_size > 0 else 20
        _check_seq2seq_int(batch_size, 'batch_size', reference_code=self.reference_validation_str)
        return batch_size

    @cached_property
    def use_openai_endpoint(self):
        """Returns and validates the use_openai_endpoint for the task. If not provided, returns False."""
        use_openai_endpoint = self.kwargs.get('use_openai_endpoint', False)
        _check_seq2seq_bool(use_openai_endpoint, 'use_openai_endpoint', ignore_none=True,
                            reference_code=self.reference_validation_str)
        return use_openai_endpoint

    @cached_property
    def openai_params(self):
        """Returns and validates the openai_params for the task. If not provided, returns None."""
        openai_params = self.kwargs.get('openai_params', None)
        _check_seq2seq_dict(openai_params, 'openai_params', ignore_none=True,
                            reference_code=self.reference_validation_str)
        return openai_params

    @cached_property
    def max_concurrent_requests(self):
        """Returns and validates the max_concurrent_requests for the task. If not provided, returns 1."""
        max_concurrent_requests = self.kwargs.get('max_concurrent_requests',
                                                  ConcurrencyConstants.MAX_CONCURRENT_REQUESTS)
        ConcurrencyConstants.MAX_CONCURRENT_REQUESTS = max_concurrent_requests
        logger.info("Setting max_concurrent_requests to {} for computing GPT based question answering metrics".format(
            ConcurrencyConstants.MAX_CONCURRENT_REQUESTS))
        _check_seq2seq_int(max_concurrent_requests, 'max_concurrent_requests', ignore_none=True,
                           reference_code=self.reference_validation_str)
        return max_concurrent_requests

    @cached_property
    def use_chat_completion_api(self):
        """Returns and validates the use_chat_completion_api for the task. If not provided, returns False."""
        use_chat_completion_api = self.kwargs.get('use_chat_completion_api', None)
        _check_seq2seq_bool(use_chat_completion_api, 'use_chat_completion_api', ignore_none=True,
                            reference_code=self.reference_validation_str)
        return use_chat_completion_api

    @cached_property
    def openai_embedding_engine(self):
        """
        Returns and validates the openai_embedding_engine for the task. If not provided, returns
        'text-embedding-ada-002'.
        """
        openai_embedding_engine = self.kwargs.get('openai_embedding_engine', "text-embedding-ada-002")
        _check_seq2seq_str(openai_embedding_engine, 'openai_embedding_engine', ignore_none=True,
                           reference_code=self.reference_validation_str)
        return openai_embedding_engine

    @cached_property
    def llm_params(self):
        """
        Returns and validates the llm_params for the task. If not provided, returns None.
        """
        llm_params = self.kwargs.get('llm_params', None)
        _check_seq2seq_dict(llm_params, 'llm_params', ignore_none=True, reference_code=self.reference_validation_str)
        return llm_params

    @cached_property
    def llm_api_batch_size(self):
        """ Returns and validates the llm_api_batch_size for the task. If not provided, returns 1."""
        llm_api_batch_size = self.kwargs.get('llm_api_batch_size', 1)
        llm_api_batch_size = llm_api_batch_size if isinstance(llm_api_batch_size,
                                                              int) and llm_api_batch_size > 0 else 1
        _check_seq2seq_int(llm_api_batch_size, 'llm_api_batch_size', ignore_none=True,
                           reference_code=self.reference_validation_str)
        return llm_api_batch_size

    @cached_property
    def llm_use_chat_completion_payload(self):
        """Returns and validates the llm_use_chat_completion_payload for the task. If not provided, returns False."""
        llm_use_chat_completion_payload = self.kwargs.get('llm_use_chat_completion_payload', False)
        _check_seq2seq_bool(llm_use_chat_completion_payload, 'llm_use_chat_completion_payload', ignore_none=True,
                            reference_code=self.reference_validation_str)
        return llm_use_chat_completion_payload


class AzureMLUnSupervisedQnADAO(AzureMLQnADAO):
    """Data Access Object for Qna type metrices which might not have y_test/ground truth answers"""

    def __init__(self, y_test, y_pred, **kwargs):
        """ Initializes the AzureMLQAPromptDAO object. """
        super().__init__(y_test, y_pred, **kwargs)

    def _prep_y_test(self, y_test):
        """Prepares the y_test for the task. If not provided, returns None."""
        return y_test


class AzureMLQAMultipleGroundTruthDAO(AzureMLQnADAO):
    """Data Access Object for Qna type metrices which might have multiple ground truth answers"""

    def __init__(self, y_test, y_pred, **kwargs):
        """ Initializes the AzureMLQAMultipleGroundTruthDAO object. """
        super().__init__(y_test, y_pred, **kwargs)

    def _prep_y_test(self, y_test):
        """Prepares the y_test for the task. If not provided, returns None."""
        _check_seq2seq_list_of_list_of_str(y_test, 'y_test', reference_code=self.reference_validation_str)
        return y_test

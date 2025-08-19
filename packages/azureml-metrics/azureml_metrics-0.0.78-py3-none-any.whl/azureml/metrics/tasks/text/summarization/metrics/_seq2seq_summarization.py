# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Definitions for Machine Translation metrics."""
import os
import importlib.util
import logging

from abc import abstractmethod
from typing import Any

from azureml.metrics.common._metric_base import Metric, ScalarMetric
from azureml.metrics.common.azureml_output_dao import AzureMLOutput
from azureml.metrics.common.utilities import retry
from azureml.metrics import constants
from azureml.metrics.common.exceptions import MissingDependencies
from azureml.metrics.tasks.text.summarization.dao.azureml_summarization_dao import AzureMLSummarizationDAO

logger = logging.getLogger(__name__)


class Seq2SeqSummarizationMetric(Metric):
    """Base class for Sequence to Sequence Translation metric"""

    def __init__(self,
                 metrics_data: AzureMLSummarizationDAO) -> None:
        """
        :param y_test: Tokenized References in the test set
        :param y_pred: Tokenized Hypothesis predicted by language model
        :param tokenizer: function that takes input a string, and returns a list of tokens
        :params aggregator: Boolean to indicate whether to aggregate scores
        :params stemmer: Boolean to indicate whether to use Porter stemmer for word suffixes
        """
        self.metrics_data = metrics_data
        super().__init__()

    @abstractmethod
    def compute(self) -> Any:
        """Compute the score for the metric"""
        ...


class Rouge(Seq2SeqSummarizationMetric, ScalarMetric):
    """Wrapper class for Rouge metric for Sequence to Sequence NLG Tasks"""

    hf_rouge = None

    def compute(self, **kwargs) -> Any:
        """Compute the score for the metric."""
        self.load_rouge()
        rouge_args = {
            'rouge_types': kwargs.get('metrics', self.metrics_data.metrics),
            'use_stemmer': self.metrics_data.stemmer,
            'use_aggregator': self.metrics_data.aggregator
        }
        if self.metrics_data.tokenizer:
            rouge_args.update({'tokenizer': self.metrics_data.tokenizer})
        y_test, y_pred = self.metrics_data.y_test, self.metrics_data.y_pred
        metrices = Rouge.hf_rouge.compute(predictions=y_pred, references=y_test,
                                          **rouge_args)
        output = AzureMLOutput()
        for metric in metrices:
            if metric in rouge_args['rouge_types']:
                output.add_value(metric, metrices[metric])
        return output

    @retry(max_attempts=constants.RetryConstants.MAX_ATTEMPTS,
           delay=constants.RetryConstants.DELAY_TIME)
    def load_rouge(self):
        try:
            import evaluate
            rougescore_spec = importlib.util.find_spec("rouge_score")

            if rougescore_spec is None:
                raise ImportError

        except ImportError:
            safe_message = "Text packages are not available. " \
                           "Please run pip install azureml-metrics[text]"
            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )
        if Rouge.hf_rouge is None:
            if self.metrics_data.use_static_script is True:
                current_file_path = os.path.abspath(__file__)
                rouge_directory_path = os.path.join(os.path.dirname(current_file_path), 'rouge')
                Rouge.hf_rouge = evaluate.load(rouge_directory_path)
                logger.info("loading rouge using static script")
            else:
                Rouge.hf_rouge = evaluate.load("rouge")
                logger.info("loading rouge using evaluate library")

    def show(self):
        """Show the metric"""
        return

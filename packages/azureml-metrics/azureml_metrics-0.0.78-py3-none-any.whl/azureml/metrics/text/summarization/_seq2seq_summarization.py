# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Definitions for Machine Translation metrics."""
import os
import importlib.util
import logging
from abc import abstractmethod
from typing import Any, List, Optional

from azureml.metrics.common._metric_base import Metric, ScalarMetric
from azureml.metrics.common.utilities import retry
from azureml.metrics import constants
from azureml.metrics.common.exceptions import MissingDependencies

logger = logging.getLogger(__name__)


class Seq2SeqSummarizationMetric(Metric):
    """Base class for Sequence to Sequence Translation metric"""

    def __init__(self,
                 y_test: List[Any],
                 y_pred: List[str],
                 metrics: List[str],
                 tokenizer: Any,
                 aggregator: bool,
                 stemmer: bool,
                 use_static_script: Optional[bool] = True) -> None:
        """
        :param y_test: Tokenized References in the test set
        :param y_pred: Tokenized Hypothesis predicted by language model
        :param tokenizer: function that takes input a string, and returns a list of tokens
        :param aggregator: Boolean to indicate whether to aggregate scores
        :param stemmer: Boolean to indicate whether to use Porter stemmer for word suffixes
        :param use_static_script: Boolean to indicate whether to use static script
            for computing rouge score
        """
        self.y_test = y_test
        self.y_pred = y_pred
        self.metrics = metrics
        self.tokenizer = tokenizer
        self.aggregator = aggregator
        self.stemmer = stemmer
        self.use_static_script = use_static_script
        super().__init__()

    @abstractmethod
    def compute(self) -> Any:
        """Compute the score for the metric"""
        ...


class Rouge(Seq2SeqSummarizationMetric, ScalarMetric):
    """Wrapper class for Rouge metric for Sequence to Sequence NLG Tasks"""

    hf_rouge = None

    def compute(self) -> Any:
        """Compute the score for the metric."""
        self.load_rouge()
        rouge_args = {
            'rouge_types': self.metrics,
            'use_stemmer': self.stemmer,
            'use_aggregator': self.aggregator
        }
        if self.tokenizer:
            rouge_args.update({'tokenizer': self.tokenizer})
        return Rouge.hf_rouge.compute(predictions=self.y_pred, references=self.y_test,
                                      **rouge_args)

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
            if self.use_static_script is True:
                current_file_path = os.path.abspath(__file__)
                rouge_directory_path = os.path.join(os.path.dirname(current_file_path), 'rouge')
                Rouge.hf_rouge = evaluate.load(rouge_directory_path)
                logger.info("loading rouge using static script")
            else:
                Rouge.hf_rouge = evaluate.load("rouge")
                logger.info("loading rouge using evaluate library")

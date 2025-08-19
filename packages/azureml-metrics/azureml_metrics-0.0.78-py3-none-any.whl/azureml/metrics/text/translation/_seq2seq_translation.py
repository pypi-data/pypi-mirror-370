# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Definitions for Machine Translation metrics."""

import os
import logging

from abc import abstractmethod
from typing import Any, List, Optional
from azureml.metrics.common._metric_base import Metric, ScalarMetric
from azureml.metrics.common.utilities import retry
from azureml.metrics import constants
from azureml.metrics.common.import_utilities import load_evaluate

logger = logging.getLogger(__name__)


class Seq2SeqTranslationMetric(Metric):
    """Base class for Sequence to Sequence Translation metric"""

    def __init__(self,
                 y_test: List[Any],
                 y_pred: List[str],
                 tokenizer: Any,
                 max_ngram: int,
                 smoothing: bool,
                 use_static_script: Optional[bool] = True) -> None:
        """
        :param y_test: Tokenized References in the test set
        :param y_pred: Tokenized Hypothesis predicted by language model
        :param tokenizer: function that takes input a string, and returns a list of tokens
        :param max_ngram: Max order of ngrams to compute Bleu
        :param smoothing: Boolean to indicate whether to smooth out the bleu score
        :param use_static_script: Boolean to indicate whether to use static script
            for computing bleu score
        """
        self.y_test = y_test
        self.y_pred = y_pred
        self.tokenizer = tokenizer
        self.max_ngram = max_ngram
        self.smoothing = smoothing
        self.use_static_script = use_static_script
        super().__init__()

    @abstractmethod
    def compute(self) -> Any:
        """Compute the score for the metric"""
        ...


class Bleu(Seq2SeqTranslationMetric, ScalarMetric):
    """Wrapper class for BLEU metric for Sequence to Sequence NLG Tasks"""

    hf_bleu = None

    def compute(self) -> Any:
        """Compute the score for the metric."""
        self.load_bleu()

        bleu_args = {
            'max_order': self.max_ngram,
            'smooth': self.smoothing
        }
        if self.tokenizer:
            bleu_args.update({'tokenizer': self.tokenizer})
        res = Bleu.hf_bleu.compute(predictions=self.y_pred, references=self.y_test, **bleu_args)
        return res['bleu']

    @retry(max_attempts=constants.RetryConstants.MAX_ATTEMPTS,
           delay=constants.RetryConstants.DELAY_TIME)
    def load_bleu(self):
        evaluate = load_evaluate()
        if Bleu.hf_bleu is None:
            if self.use_static_script is True:
                current_file_path = os.path.abspath(__file__)
                bleu_directory_path = os.path.join(os.path.dirname(current_file_path), 'bleu')
                # get the path to the static script
                Bleu.hf_bleu = evaluate.load(bleu_directory_path)
                logger.info("loading bleu using static script")
            else:
                Bleu.hf_bleu = evaluate.load("bleu")
                logger.info("loading bleu using evaluate library")

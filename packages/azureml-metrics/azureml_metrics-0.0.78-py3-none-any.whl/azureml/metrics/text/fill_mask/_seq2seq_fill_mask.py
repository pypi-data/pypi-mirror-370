# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Definitions for Language Modeling metrics."""
from abc import abstractmethod

from typing import Any, List, Optional
from azureml.metrics.common._metric_base import Metric, ScalarMetric
from azureml.metrics.common.utilities import retry
from azureml.metrics import constants
from azureml.metrics.common.exceptions import MissingDependencies

import importlib.util


class Seq2SeqFillMaskMetric(Metric):
    """Base class for Sequence to Sequence fill mask metric"""

    def __init__(
        self,
        y_test: List[Any],
        y_pred: List[str],
        model_id: Optional[str],
        batch_size: Optional[int],
        add_start_token: Optional[bool],
    ) -> None:
        """
        :param y_test: Tokenized References in the test set
        :param y_pred: Tokenized Hypothesis predicted by language model
        :param model_id: model used for calculating Perplexity.
                            Perplexity can only be calculated for causal language models.
        :param batch_size (int): the batch size to run texts through the model. Defaults to 16.
        :param add_start_token (bool): whether to add the start token to the texts,
            so the perplexity can include the probability of the first word. Defaults to True.
        """
        self.y_test = y_test
        self.y_pred = y_pred
        self.model_id = model_id
        self.batch_size = batch_size
        self.add_start_token = add_start_token
        super().__init__()

    @abstractmethod
    def compute(self) -> Any:
        """Compute the score for the metric"""
        ...


class Perplexity(Seq2SeqFillMaskMetric, ScalarMetric):
    """Perplexity metric for Sequence to Sequence Language Modeling Tasks"""

    hf_perplexity = None

    def compute(self) -> Any:
        """Compute the score for Perplexity metric"""
        self.load_perplexity()

        perplexity_args = {
            "model_id": self.model_id,
            "batch_size": self.batch_size,
            "add_start_token": self.add_start_token,
        }
        result = Perplexity.hf_perplexity.compute(
            predictions=self.y_pred, **perplexity_args
        )
        return result["perplexities"]

    @retry(max_attempts=constants.RetryConstants.MAX_ATTEMPTS,
           delay=constants.RetryConstants.DELAY_TIME)
    def load_perplexity(self):
        try:
            import evaluate
            torch_spec = importlib.util.find_spec("torch")
            transformers_spec = importlib.util.find_spec("transformers")

            if torch_spec is None or transformers_spec is None:
                raise ImportError

        except ImportError:
            safe_message = "Text packages are not available. " \
                           "Please run pip install azureml-metrics[text]"

            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )

        if Perplexity.hf_perplexity is None:
            Perplexity.hf_perplexity = evaluate.load("perplexity")

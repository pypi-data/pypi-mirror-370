# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Definitions for Language Modeling metrics."""
from abc import abstractmethod
import numpy as np

from azureml.metrics.common._metric_base import Metric, ScalarMetric
from azureml.metrics.common.azureml_output_dao import AzureMLOutput
from azureml.metrics.common.utilities import retry
from azureml.metrics import constants
from azureml.metrics.common.exceptions import MissingDependencies
from azureml.metrics.tasks.text.fill_mask.dao.azureml_fill_mask_dao import AzureMLFillMaskDAO


import importlib.util


class Seq2SeqFillMaskMetric(Metric):
    """Base class for Sequence to Sequence fill mask metric"""

    def __init__(self, metrics_data: AzureMLFillMaskDAO) -> None:
        """
        Initialize the Fill Mask metric class.
        """
        self.metrics_data = metrics_data
        super().__init__()

    @abstractmethod
    def compute(self) -> AzureMLOutput:
        """Compute the score for the metric"""
        ...


class Perplexity(Seq2SeqFillMaskMetric, ScalarMetric):
    """Perplexity metric for Sequence to Sequence Language Modeling Tasks"""

    hf_perplexity = None

    def compute(self) -> AzureMLOutput:
        """Compute the score for Perplexity metric"""
        self.load_perplexity()

        perplexity_args = {
            "model_id": self.metrics_data.model_id,
            "batch_size": self.metrics_data.batch_size,
            "add_start_token": self.metrics_data.add_start_token,
        }
        result = Perplexity.hf_perplexity.compute(
            predictions=self.metrics_data.y_pred, **perplexity_args
        )
        perplexities = result["perplexities"]
        metric = constants.Metric.FMPerplexity
        mean_metric_name = constants.MetricExtrasConstants.MeanExtrasFormat.format(metric)
        median_metric_name = constants.MetricExtrasConstants.MedianExtrasFormat.format(metric)

        output = AzureMLOutput()
        output.add_value(metric, perplexities)
        output.add_value(mean_metric_name, np.nanmean(perplexities))
        output.add_value(median_metric_name, np.nanmedian(perplexities))
        return output

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
            raise MissingDependencies(safe_message, safe_message=safe_message)

        if Perplexity.hf_perplexity is None:
            Perplexity.hf_perplexity = evaluate.load("perplexity")

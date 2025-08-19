# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics import constants
from azureml.metrics.common.metrics_registry import MetricsRegistry
from azureml.metrics.tasks.text.summarization.metrics import _seq2seq_summarization
from azureml.metrics.tasks.text.summarization.dao.azureml_summarization_dao import AzureMLSummarizationDAO


def register_summarization_metrics():
    MetricsRegistry.register(constants.Metric.SummarizationRouge1, _seq2seq_summarization.Rouge,
                             AzureMLSummarizationDAO)
    MetricsRegistry.register(constants.Metric.SummarizationRouge2, _seq2seq_summarization.Rouge,
                             AzureMLSummarizationDAO)
    MetricsRegistry.register(constants.Metric.SummarizationRougeL, _seq2seq_summarization.Rouge,
                             AzureMLSummarizationDAO)
    MetricsRegistry.register(constants.Metric.SummarizationRougeLsum, _seq2seq_summarization.Rouge,
                             AzureMLSummarizationDAO)


register_summarization_metrics()

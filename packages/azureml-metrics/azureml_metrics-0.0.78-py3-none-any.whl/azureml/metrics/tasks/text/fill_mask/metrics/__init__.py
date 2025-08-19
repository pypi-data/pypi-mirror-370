# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics.constants import Metric
from azureml.metrics.common.metrics_registry import MetricsRegistry
from azureml.metrics.tasks.text.fill_mask.metrics import _seq2seq_fill_mask
from azureml.metrics.tasks.text.fill_mask.dao.azureml_fill_mask_dao import AzureMLFillMaskDAO

MetricsRegistry.register(Metric.FMPerplexity, _seq2seq_fill_mask.Perplexity, AzureMLFillMaskDAO)

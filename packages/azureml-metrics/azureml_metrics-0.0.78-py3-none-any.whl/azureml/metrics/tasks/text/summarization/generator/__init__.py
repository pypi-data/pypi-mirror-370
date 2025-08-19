# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics import constants
from azureml.metrics.common.metrics_generator_factory import MetricsGeneratorRegistry
from azureml.metrics.tasks.text.summarization.generator.azureml_summarization_metrics import \
    AzureMLSummarizationMetrics

MetricsGeneratorRegistry.register(constants.Tasks.SUMMARIZATION, AzureMLSummarizationMetrics)

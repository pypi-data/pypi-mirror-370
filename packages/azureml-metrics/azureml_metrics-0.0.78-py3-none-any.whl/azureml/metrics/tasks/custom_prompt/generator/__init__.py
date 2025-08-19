# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics import constants
from azureml.metrics.common.metrics_generator_factory import MetricsGeneratorRegistry
from azureml.metrics.tasks.custom_prompt.generator.azureml_custom_prompt_metrics_generator import \
    AzureMLCustomPromptMetricsGenerator

MetricsGeneratorRegistry.register(constants.Tasks.CUSTOM_PROMPT_METRIC, AzureMLCustomPromptMetricsGenerator)

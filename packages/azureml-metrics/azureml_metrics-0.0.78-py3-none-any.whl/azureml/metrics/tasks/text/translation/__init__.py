# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics import constants
from azureml.metrics.common.metrics_generator_factory import MetricsGeneratorRegistry
from azureml.metrics.tasks.text.translation.azureml_translation_metrics_evaluator import \
    AzureMLTranslationMetrics

MetricsGeneratorRegistry.register(constants.Tasks.TRANSLATION, AzureMLTranslationMetrics)

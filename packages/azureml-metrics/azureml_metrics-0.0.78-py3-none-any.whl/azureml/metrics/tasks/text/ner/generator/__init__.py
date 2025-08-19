# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics import constants
from azureml.metrics.common.metrics_generator_factory import MetricsGeneratorRegistry
from azureml.metrics.tasks.text.ner.generator.azureml_ner_metrics import \
    AzureMLNerMetrics

MetricsGeneratorRegistry.register(constants.Tasks.TEXT_NER, AzureMLNerMetrics)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics import constants
from azureml.metrics.common.metrics_generator_factory import MetricsGeneratorRegistry
from azureml.metrics.tasks.generic.generator.azureml_generic_metrics import AzureMLGenericMetrics

MetricsGeneratorRegistry.register(constants.Tasks.DEFAULT, AzureMLGenericMetrics)

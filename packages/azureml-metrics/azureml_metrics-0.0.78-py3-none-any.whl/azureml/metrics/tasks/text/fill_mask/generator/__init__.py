# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics import constants
from azureml.metrics.common.metrics_generator_factory import MetricsGeneratorRegistry
from azureml.metrics.tasks.text.fill_mask.generator.azureml_fill_mask_metrics import \
    AzureMLFillMaskMetrics

MetricsGeneratorRegistry.register(constants.Tasks.FILL_MASK, AzureMLFillMaskMetrics)

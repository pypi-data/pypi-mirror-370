# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics.constants import Metric
from azureml.metrics.common.metrics_registry import MetricsRegistry
from azureml.metrics.tasks.text.ner.metrics import _token_classification
from azureml.metrics.tasks.text.ner.dao.azureml_ner_dao import AzureMLNerDAO

MetricsRegistry.register(Metric.Accuracy, _token_classification.Accuracy, AzureMLNerDAO)
MetricsRegistry.register(Metric.F1Macro, _token_classification.F1Macro, AzureMLNerDAO)
MetricsRegistry.register(Metric.F1Micro, _token_classification.F1Micro, AzureMLNerDAO)
MetricsRegistry.register(Metric.F1Weighted, _token_classification.F1Weighted, AzureMLNerDAO)
MetricsRegistry.register(Metric.PrecisionMacro, _token_classification.PrecisionMacro, AzureMLNerDAO)
MetricsRegistry.register(Metric.PrecisionMicro, _token_classification.PrecisionMicro, AzureMLNerDAO)
MetricsRegistry.register(Metric.PrecisionWeighted, _token_classification.PrecisionWeighted, AzureMLNerDAO)
MetricsRegistry.register(Metric.RecallMacro, _token_classification.RecallMacro, AzureMLNerDAO)
MetricsRegistry.register(Metric.RecallMicro, _token_classification.RecallMicro, AzureMLNerDAO)
MetricsRegistry.register(Metric.RecallWeighted, _token_classification.RecallWeighted, AzureMLNerDAO)

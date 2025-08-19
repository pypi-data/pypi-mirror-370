# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics import constants
from azureml.metrics.common.metrics_generator_factory import MetricsGeneratorRegistry
from azureml.metrics.tasks.text.qna.generator.azureml_qa_metrics_evaluator import AzureMLQAMetrics

MetricsGeneratorRegistry.register(constants.Tasks.QUESTION_ANSWERING, AzureMLQAMetrics)
MetricsGeneratorRegistry.register(constants.Tasks.QUESTION_ANSWERING_MULTIPLE_GROUND_TRUTH, AzureMLQAMetrics)

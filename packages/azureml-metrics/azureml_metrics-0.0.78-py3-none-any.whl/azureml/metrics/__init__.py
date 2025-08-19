# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains metrics computation classes for Azure Machine Learning."""
import importlib
import sys

from ._score import compute_metrics, score
from ._score import list_metrics, list_tasks, list_prompts
from azureml.metrics.common.azureml_custom_prompt_metric import AzureMLCustomPromptMetric
from azureml.metrics.common._metric_base import ScalarMetric, NonScalarMetric
from azureml.metrics.common.metrics_registry import MetricsRegistry

__all__ = [
    "compute_metrics",
    "score",
    "list_metrics",
    "list_tasks",
    "list_prompts",
    "AzureMLCustomPromptMetric",
    "MetricsRegistry",
    "ScalarMetric",
    "NonScalarMetric",
]

# TODO copy this file as part of setup in runtime package
__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: ignore

tasks_supported = [
    "custom_prompt", "generic", "base",
    "text.summarization", "text.qna", "text.translation",
    "text.fill_mask", "text.ner"
]


def import_module(module):
    try:
        importlib.import_module(module)
    except ImportError:
        pass


for task in tasks_supported:
    import_module(f"azureml.metrics.tasks.{task}.metrics")
    import_module(f"azureml.metrics.tasks.{task}.dao")
    import_module(f"azureml.metrics.tasks.{task}.generator")

# Todo: remove above code and add below code
new_metrics_supported = ["bleu"]
for metric in new_metrics_supported:
    import_module(f"azureml.metrics.metrics.{metric}")

new_tasks_supported = ["text.translation"]
for task in new_tasks_supported:
    import_module(f"azureml.metrics.tasks.{task}")

try:
    from ._version import ver as VERSION, selfver as SELFVERSION

    __version__ = VERSION
except ImportError:
    VERSION = '0.0.0+dev'
    SELFVERSION = VERSION
    __version__ = VERSION

module = sys.modules[__name__]

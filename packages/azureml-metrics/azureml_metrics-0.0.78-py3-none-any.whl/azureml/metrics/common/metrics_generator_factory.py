# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Metrics Generator Registry for Azure Machine Learning."""
from collections import defaultdict

from azureml.metrics import constants


class MetricsGeneratorRegistry:
    """
    Registry for metrics generators. Stores the mapping of task type to generator.
    Registry is a singleton and can be used to register and get generators.
    Use DefaultGenerator if no generator is found for the task type.
    """
    Registry = defaultdict(None)

    @classmethod
    def get_generator(cls, task_type):
        """Get the generator for the task type."""
        task_type = task_type if task_type is not None and task_type in cls.Registry else constants.Tasks.DEFAULT
        return cls.Registry[task_type]

    @classmethod
    def register(cls, task_type, generator):
        """Register a generator for the task type."""
        cls.Registry[task_type] = generator

    @classmethod
    def unregister(cls, task_type):
        """Unregister a generator for the task type."""
        cls.Registry.pop(task_type, None)

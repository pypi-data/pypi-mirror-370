# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Metrics Registry."""
from collections import defaultdict

from azureml.metrics.common.exceptions import MetricUnregisteredException
from azureml.metrics.tasks.base.dao.azureml_dao import AzureMLDAO


class MetricsRegistry:
    """
    Metrics Registry. Fetch metric class based on metric_name
    Or a combination of metric_name and dao_class
    """
    Registry = defaultdict(set)
    DAORegistry = defaultdict(lambda: defaultdict(None))

    @classmethod
    def get_metric_class(cls, metric_name, dao_class=None):
        """ Get metric class based on metric_name and dao_class."""
        metric_classes = cls.Registry.get(metric_name, None)
        if metric_classes is None:
            raise MetricUnregisteredException(f"Metric {metric_name} not found in registry.")
        metric_classes = list(metric_classes)
        if len(metric_classes) > 1:
            if dao_class is None:
                raise ValueError(f"Multiple metric classes found for metric {metric_name}. "
                                 f"Please provide a dao class.")
            metric_class = cls._get_metric_class_from_dao(metric_name, dao_class)
            if metric_class is None:
                raise ValueError(f"dao {dao_class} not found in registry.")
            return metric_class
        return metric_classes[0]

    @classmethod
    def _get_metric_class_from_dao(cls, metric_name, dao_class):
        """ Get metric class based on metric_name and dao_class."""
        if dao_class is None:
            return None
        return cls.DAORegistry[metric_name][dao_class]

    @classmethod
    def register(cls, metric_name, metric_class, dao_class=AzureMLDAO):
        """ Register a metric class for the metric_name."""
        cls.Registry[metric_name].add(metric_class)  # This would be for both class and object
        if isinstance(dao_class, list):
            for dao in dao_class:
                cls.DAORegistry[metric_name][dao] = metric_class
        else:
            cls.DAORegistry[metric_name][dao_class] = metric_class

    @classmethod
    def get_dao_classes(self, metric_name):
        """ Get dao classes for a metric."""
        if metric_name not in self.DAORegistry:
            raise MetricUnregisteredException(f"Metric {metric_name} not found in registry.")
        return list(self.DAORegistry[metric_name].keys())

    @classmethod
    def get_metric_names(cls):
        """ Get all metric names in the registry."""
        return cls.Registry.keys()

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DAO Output type for AzureML Metrics SDK"""
import logging
import numpy as np

from azureml.metrics import constants

logger = logging.getLogger(constants.TelemetryConstants.APP_NAME)


class AzureMLOutput:
    """ Output class to store metrics and artifacts for AzureML"""

    def __init__(self, metrics: dict = None, artifacts: dict = None):
        """
        Initialize the output object with metrics and artifacts
        :param metrics: Dictionary of metrics
        :param artifacts: Dictionary of artifacts
        """
        self.metrics = metrics or {}
        self.artifacts = artifacts or {}

    def __add__(self, other):
        """
        Merge two AzureMLOutput objects
        :param other: AzureMLOutput object
        :return: AzureMLOutput object
        """
        metrics = {**self.metrics, **other.metrics}
        artifacts = {**self.artifacts, **other.artifacts}
        return AzureMLOutput(metrics, artifacts)

    def add_value(self, key, value):
        """
        Add a key value pair to the output object
        :param key: Key
        :param value: Value
        """
        if np.isscalar(value):
            self.metrics[key] = value
        else:
            self.artifacts[key] = value

    def add_metric(self, metric_name, metric_value):
        """
        Add a metric to the output object
        """
        if np.isscalar(metric_value):
            self.metrics[metric_name] = metric_value
        else:
            # Should this throw error?
            logger.warning(f"Value for metric {metric_name} is not a scalar, use add_artifact instead")
            self.artifacts[metric_name] = metric_value

    def add_artifact(self, key, value):
        """
        Add an artifact to the output object
        :param key: Key
        :param value: Value
        """
        self.artifacts[key] = value

    def update(self, other):
        """
        Update the output object with another output object
        :param other: AzureMLOutput object
        """
        self.metrics.update(other.metrics)
        self.artifacts.update(other.artifacts)

    def __repr__(self):
        """
        String representation of the output object
        """
        return f"Metrics: {self.metrics}, Artifacts: {self.artifacts}"

    def to_dict(self):
        """
        Convert the output object to a dictionary
        """
        return {constants.Metric.Metrics: self.metrics, constants.Metric.Artifacts: self.artifacts}

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AzureML Core Run utilities."""

import os
import re

azure_core_installed = True
try:
    from azureml.core import Run
    from azureml.core.run import _OfflineRun
except ImportError:
    azure_core_installed = False


class DummyRun:
    """Dummy Run class for offline"""

    def __init__(self):
        """__init__."""
        self.id = "offline_run"


class DummyWorkspace:
    """Dummy Workspace class for offline logging."""

    def __init__(self):
        """__init__."""
        self.name = "local-ws"
        self.subscription_id = ""
        self.location = "local"
        self.resource_group = ""


class DummyExperiment:
    """Dummy Experiment class for offline logging."""

    def __init__(self):
        """__init__."""
        self.name = "offline_default_experiment"
        self.id = "1"
        self.workspace = DummyWorkspace()


class TestRun:
    """Main class containing Current Run's details."""

    def __init__(self):
        """__init__."""
        self._run = Run.get_context() if azure_core_installed else DummyRun()
        if not azure_core_installed or isinstance(self._run, _OfflineRun):
            self._experiment = DummyExperiment()
            self._workspace = self._experiment.workspace
        else:
            self._experiment = self._run.experiment
            self._workspace = self._experiment.workspace

    @property
    def run(self):
        """Azureml Run.

        Returns:
            _type_: _description_
        """
        return self._run

    @property
    def experiment(self):
        """Azureml Experiment.

        Returns:
            _type_: _description_
        """
        return self._experiment

    @property
    def region(self):
        """Azure Region.

        Returns:
            _type_: _description_
        """
        return self._workspace.location

    @property
    def subscription(self):
        """Azureml Subscription.

        Returns:
            _type_: _description_
        """
        return self._workspace.subscription_id

    @property
    def get_extra_run_info(self):
        """Get run details of the pipeline.

        Returns:
            _type_: _description_
        """
        info = {}
        if azure_core_installed and not isinstance(self._run, _OfflineRun):
            raw_json = self._run.get_details()
            info['moduleId'] = raw_json.get('properties', dict()).get('azureml.moduleid', '')
            info["moduleName"] = raw_json.get('properties', dict()).get('azureml.moduleName', 'Unknown')
        try:
            location = os.environ.get("AZUREML_SERVICE_ENDPOINT")
            location = re.compile("//(.*?)\\.").search(location).group(1)
        except Exception:
            location = os.environ.get("AZUREML_SERVICE_ENDPOINT", "")
        info["location"] = location
        return info

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base dao for Azure Machine Learning."""
import logging
import copy

from functools import cached_property

from azureml.metrics import constants
from azureml.metrics.common.contract import Contract

logger = logging.getLogger(constants.TelemetryConstants.APP_NAME)


class AzureMLDAO:
    """AzureMLDAO class. Base/Default DAO for AzureML."""

    def __init__(self, y_test=None, y_pred=None, y_pred_proba=None, **kwargs):
        """
        Initializes the AzureMLDAO class.
        """
        self.y_test = self._prep_y_test(y_test)
        self.y_pred = self._prep_y_pred(y_pred)
        self.y_pred_proba = self._prep_y_pred_proba(y_pred_proba)
        self.kwargs = kwargs  # To preserve the original kwargs; used in customPrompt
        self._dao = copy.deepcopy(kwargs)  # To avoid __getattr__ to have a recursive call
        self.validate_if_dao_applicable()

    def _prep_y_test(self, y_test):
        """
        Prepares y_test for validation. Should be overridden by derived class if needed.
        """
        return y_test

    def _prep_y_pred(self, y_pred):
        """
        Prepares y_pred for validation. Should be overridden by derived class if needed.
        """
        return y_pred

    def _prep_y_pred_proba(self, y_pred_proba):
        """
        Prepares y_pred_proba for validation. Should be overridden by derived class if needed.
        """
        return y_pred_proba

    def validate_if_dao_applicable(self):
        """
        Validates if kwargs are of correct type and data is of consistent length
        Should be called by all derived class that overrides this method
        """
        self.check_kwargs()
        if self.y_test is not None and self.y_pred is not None:
            Contract.assert_true(len(self.y_test) == len(self.y_pred),
                                 'Number of samples in y_test and y_pred do not match',
                                 log_safe=True, reference_code=self.reference_validation_str, target='y_test')

    @property
    def reference_validation_str(self):
        return ""

    @cached_property
    def metrics(self):
        """
        Returns the metrics from the kwargs
        """
        return self.kwargs.get('metrics', [])

    @cached_property
    def custom_metrics(self):
        """
        Returns the custom_metrics from the kwargs
        """
        return self.kwargs.get('custom_metrics', [])

    def __getattr__(self, item):
        """
        Returns the value of the item from the kwargs
        """
        if hasattr(self, "_dao"):
            return self._dao.get(item, None)
        return None

    def check_kwargs(self):
        """
        Validates the kwargs
        """
        logger.info(f"Initializing and validating the arguments {self.kwargs}")
        # Below doesn't include tokenizer
        properties = {arg: getattr(self, arg) for arg in dir(self) if
                      not arg.startswith('_') and not callable(getattr(self, arg))}
        logger.info("Following properties have been initialized and validated: " + str(properties))
        unused_keys = list(set(self.kwargs.keys()).difference(set(properties.keys())))
        # Adding this condition to remove task_type from unused_keys as it is not a part of the DAO
        if "task_type" in unused_keys:
            unused_keys.remove("task_type")
        if len(unused_keys) > 0:
            warning_message = f"We have unvalidated keyword arguments : {unused_keys}\n"
            logger.warning(warning_message)

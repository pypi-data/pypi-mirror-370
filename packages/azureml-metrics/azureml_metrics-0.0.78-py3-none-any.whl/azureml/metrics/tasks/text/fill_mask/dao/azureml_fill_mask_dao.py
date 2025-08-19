# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AzureMLFillMaskDAO class."""
from azureml.metrics.common._validation import _check_seq2seq_bool, _check_seq2seq_str, \
    _check_seq2seq_int, _check_seq2seq_list_of_str
from azureml.metrics.common.contract import Contract
from azureml.metrics.constants import Metric, ReferenceCodes
from azureml.metrics.tasks.base.dao.azureml_dao import AzureMLDAO
from functools import cached_property


class AzureMLFillMaskDAO(AzureMLDAO):
    """Data Access Object for metrics similar to Fill Mask."""

    @property
    def reference_validation_str(self):
        """Returns reference validation string for Fill Mask."""
        return ReferenceCodes.VALIDATE_FILL_MASK

    @cached_property
    def add_start_token(self):
        """Returns and validates the add_start_token for the task. If not provided, returns True."""
        add_start_token = self.kwargs.get('add_start_token', True)
        _check_seq2seq_bool(add_start_token, 'add_start_token', reference_code=self.reference_validation_str)
        return add_start_token

    @cached_property
    def model_id(self):
        """Returns and validates the model_id for the task. If not provided, returns default as 'gpt_2'."""
        model_id = self.kwargs.get('model_id', "gpt2")
        _check_seq2seq_str(model_id, 'model_id', reference_code=self.reference_validation_str)
        return model_id

    @cached_property
    def batch_size(self):
        """Returns and validates the batch_size for the task. If not provided, returns 16."""
        batch_size = self.kwargs.get('batch_size', 16)
        _check_seq2seq_int(batch_size, 'batch_size', ignore_none=True,
                           reference_code=self.reference_validation_str)
        return batch_size

    def _prep_y_pred(self, y_pred):
        """Preprocess and validate the y_pred data"""
        _check_seq2seq_list_of_str(y_pred, 'y_pred', reference_code=self.reference_validation_str)
        return y_pred

    def validate_if_dao_applicable(self):
        """Validates if kwargs are of correct type and data is of consistent length."""
        self.check_kwargs()
        # Special set metrics do not need ground truths or y_test data
        if len(set(self.metrics) - Metric.FILL_MASK_SPECIAL_SET) > 0:
            _check_seq2seq_list_of_str(self.y_test, 'y_test', reference_code=self.reference_validation_str)
            Contract.assert_true(len(self.y_test) == len(self.y_pred),
                                 'Number of samples in y_test and y_pred do not match',
                                 log_safe=True, reference_code=self.reference_validation_str, target='y_test')

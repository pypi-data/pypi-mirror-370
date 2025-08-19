# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AzureMLNerDAO class."""
import logging
from azureml.metrics.common._validation import _check_seq2seq_list_of_list_of_str
from azureml.metrics.constants import ReferenceCodes
from azureml.metrics.tasks.base.dao.azureml_dao import AzureMLDAO

logger = logging.getLogger(__name__)


class AzureMLNerDAO(AzureMLDAO):
    """Data Access Object for metrics similar to NER."""

    @property
    def reference_validation_str(self):
        """Returns reference validation string for NER."""
        return ReferenceCodes.VALIDATE_NER

    def _prep_y_pred(self, y_pred):
        """Preprocess and validate the y_pred data"""
        # added this logic for AutoML NLP as it returns result as string
        if isinstance(y_pred, str):
            prediction_str = y_pred
            y_pred = []
            predictions = prediction_str.split("\n\n")

            for prediction in predictions:
                prediction_label = prediction.split("\n")
                pred_labels = [token.split()[1] for token in prediction_label]
                y_pred.append(pred_labels)

        _check_seq2seq_list_of_list_of_str(y_pred, 'y_pred', reference_code=self.reference_validation_str)
        return y_pred

    def _prep_y_test(self, y_test):
        """Preprocess and validate the y_test data"""
        _check_seq2seq_list_of_list_of_str(y_test, 'y_test', reference_code=self.reference_validation_str)
        return y_test

    def validate_if_dao_applicable(self):
        """Validates if kwargs are of correct type and data is of consistent length."""
        super().validate_if_dao_applicable()

        for index, (test, pred) in enumerate(zip(self.y_test, self.y_pred)):
            if len(test) != len(pred):
                logger.warning(f'Number of labels in test and pred in sample {index + 1} do not match.'
                               f' Some metrics might be skipped and not computed.')

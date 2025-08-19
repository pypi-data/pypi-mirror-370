# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Validation for AzureML metrics."""
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any, Sequence

import numpy as np
import json

from azureml.metrics import constants
from azureml.metrics.common import utilities
from azureml.metrics.common._metric_base import NonScalarMetric
from azureml.metrics.common.contract import Contract
from azureml.metrics.common.exceptions import ValidationException
from azureml.metrics.common.reference_codes import ReferenceCodes

logger = logging.getLogger(__name__)


def validate_classification(y_test: np.ndarray,
                            y_pred: Optional[np.ndarray],
                            y_pred_probs: Optional[np.ndarray],
                            metrics: List[str],
                            class_labels: np.ndarray,
                            train_labels: np.ndarray,
                            sample_weight: Optional[np.ndarray],
                            multilabel: Optional[bool] = False) -> None:
    """
    Validate the inputs for scoring classification.

    :param y_test: Target values (Transformed if using a y transformer)
    :param y_pred: The predicted values (Transformed if using a y transformer)
    :param y_pred_probs: The predicted probabilities for all classes.
    :param metrics: Metrics to compute.
    :param class_labels: All classes found in the full dataset.
    :param train_labels: Classes as seen (trained on) by the trained model.
    :param sample_weight: Weights for the samples.
    :param multilabel: Indicate if it is multilabel classification.
    """
    _validate_metrics_list("classification", metrics, constants.Metric.CLASSIFICATION_SET,
                           ReferenceCodes._METRIC_INVALID_CLASSIFICATION_METRIC)

    pred_exists = y_pred is not None or y_pred_probs is not None
    message = "y_pred and y_pred_probs cannot be None together"
    Contract.assert_true(pred_exists, message=message, log_safe=True, reference_code='validate_classification',
                         target='y_pred/y_pred_probs')

    _check_array_type(y_test, 'y_test', reference_code='validate_classification')
    _check_array_type(y_pred, 'y_pred', ignore_none=True, reference_code='validate_classification')
    _check_array_type(y_pred_probs, 'y_pred_probs', ignore_none=True, reference_code='validate_classification')
    _check_array_type(class_labels, 'class_labels', reference_code='validate_classification')
    _check_array_type(train_labels, 'train_labels', reference_code='validate_classification')
    _check_array_type(sample_weight, 'sample_weight', ignore_none=True, reference_code='validate_classification')
    if y_pred is not None:
        _check_arrays_first_dim(y_test, y_pred, 'y_test', 'y_pred', reference_code='validate_classification')
    if y_pred_probs is not None:
        _check_arrays_first_dim(y_test, y_pred_probs, 'y_test', 'y_pred_probs',
                                reference_code='validate_classification')

    labels_type_check = {
        'class_labels': class_labels,
        'train_labels': train_labels
    }

    _check_arrays_same_type(labels_type_check, check_numeric_type=False, target='class_labels',
                            reference_code='validate_classification')

    if y_pred is not None:
        params_type_check = {
            "y_test": y_test,
            "y_pred": y_pred
        }

        _check_arrays_same_type(params_type_check, check_numeric_type=False, target='y_pred',
                                reference_code='validate_classification')

    _check_dim(class_labels, 'class_labels', 1, reference_code='validate_classification')
    _check_dim(train_labels, 'train_labels', 1, reference_code='validate_classification')
    if y_pred is not None:
        _check_dim(y_pred, 'y_pred', 1 if not multilabel else 2, reference_code='validate_classification')
    _check_dim(y_test, 'y_test', 1 if not multilabel else 2, reference_code='validate_classification')
    if y_pred_probs is not None:
        _check_dim(y_pred_probs, 'y_pred_probs', 2, reference_code='validate_classification')

    _check_array_values(class_labels, 'class_labels', reference_code='validate_classification')
    _check_array_values(train_labels, 'train_labels', reference_code='validate_classification')
    _check_array_values(y_test, 'y_test', reference_code='validate_classification')
    if y_pred is not None:
        _check_array_values(y_pred, 'y_pred', reference_code='validate_classification')
    if y_pred_probs is not None:
        _check_array_values(y_pred_probs, 'y_pred_probs', reference_code='validate_classification')
    if sample_weight is not None:
        _check_array_values(sample_weight, 'sample_weight', reference_code='validate_classification')

    # check if two preds are consistent
    if y_pred is not None and y_pred_probs is not None:
        message = "predictions indicated from y_pred_probs do not equal y_pred"
        if not multilabel:
            y_pred_from_probs = np.argmax(y_pred_probs, axis=1)

            class_label_map = {key: label for key, label in enumerate(class_labels)}
            y_pred_from_probs = np.array([class_label_map[key] for key in y_pred_from_probs])

            same_prediction = (y_pred == y_pred_from_probs).all()
            Contract.assert_true(same_prediction, message, log_safe=True, target="same_prediction",
                                 reference_code='validate_classification')

    if sample_weight is not None:
        Contract.assert_true(sample_weight.dtype.kind in set('fiu'),
                             message="Type of sample_weight must be numeric (got type {})".format(sample_weight.dtype),
                             target="sample_weight", log_safe=True, reference_code="validate_classification")

        Contract.assert_true(y_test.shape[0] == sample_weight.shape[0],
                             message="Number of samples does not match in y_test ({}) and sample_weight ({})".format(
                                 y_test.shape[0], sample_weight.shape[0]),
                             target="sample_weight", log_safe=True, reference_code="validate_classification")

    if y_pred_probs is not None:
        Contract.assert_true(train_labels.shape[0] == y_pred_probs.shape[1],
                             message="train_labels.shape[0] ({}) does not match y_pred_probs.shape[1] ({}).".format(
                                 train_labels.shape[0], y_pred_probs.shape[1]), log_safe=True,
                             reference_code="validate_classification")
    if multilabel:
        Contract.assert_true(train_labels.shape[0] == y_test.shape[1],
                             message="train_labels.shape[0] ({}) does not match y_test.shape[1] ({}).".format(
                                 train_labels.shape[0], y_test.shape[1]), log_safe=True,
                             reference_code="validate_classification")

    set_diff = np.setdiff1d(train_labels, class_labels)
    if set_diff.shape[0] != 0:
        logger.error("train_labels contains values not present in class_labels")
        message = "Labels {} found in train_labels are missing from class_labels.".format(set_diff)
        raise ValidationException(message, target="train_labels",
                                  reference_code=ReferenceCodes._METRIC_VALIDATION_EXTRANEOUS_TRAIN_LABELS,
                                  safe_message=None)

    # This validation is not relevant for multilabel as the y_test is in one-hot encoded format.
    if not multilabel:
        set_diff = np.setdiff1d(np.unique(y_test), class_labels)
        if set_diff.shape[0] != 0:
            logger.error("y_test contains values not present in class_labels")
            message = "Labels {} found in y_test are missing from class_labels.".format(set_diff)
            raise ValidationException(message, target="y_test",
                                      reference_code=ReferenceCodes._METRIC_VALIDATION_EXTRANEOUS_YTEST_LABELS,
                                      safe_message=None)


def log_classification_debug(y_test: np.ndarray,
                             y_pred: Optional[np.ndarray],
                             y_pred_probs: Optional[np.ndarray],
                             class_labels: np.ndarray,
                             train_labels: np.ndarray,
                             sample_weight: Optional[np.ndarray] = None,
                             multilabel: Optional[bool] = False) -> None:
    """
    Log shapes of classification inputs for debugging.

    :param y_test: Target values (Transformed if using a y transformer)
    :param y_pred: The predicted values (Transformed if using a y transformer)
    :param y_pred_probs: The predicted probabilities for all classes.
    :param class_labels: All classes found in the full dataset.
    :param train_labels: Classes as seen (trained on) by the trained model.
    :param sample_weight: Weights for the samples.
    :param multilabel: Indicate if it is multilabel classification.
    """

    unique_y_test = np.unique(y_test)
    debug_data = {
        'y_test_shape': y_test.shape,
        'y_pred_shape': y_pred.shape if y_pred is not None else None,
        'y_pred_probs_shape': y_pred_probs.shape if y_pred_probs is not None else None,
        'unique_y_test_shape': unique_y_test.shape,
        'class_labels_shape': class_labels.shape,
        'train_labels_shape': train_labels.shape,
        'n_missing_train': np.setdiff1d(class_labels, train_labels).shape[0],
        'n_missing_valid': np.setdiff1d(class_labels, unique_y_test).shape[0],
        'sample_weight_shape': None if sample_weight is None else sample_weight.shape
    }

    if not multilabel:
        unique_y_test = np.unique(y_test)
        debug_data.update({'unique_y_test': unique_y_test.shape,
                           'n_missing_valid': np.setdiff1d(class_labels, unique_y_test).shape[0]})
    else:
        # Log the difference in the no of labels between class_labels and y_test
        debug_data.update({'n_missing_valid': class_labels.shape[0] - y_test.shape[1]})

    logger.info("Classification metrics debug: {}".format(debug_data))


def _validate_regression_base(
        y_test: np.ndarray,
        y_pred: np.ndarray,
        metrics: List[str],
        valid_metrics: Sequence,
        task: str,
        ref_code: str) -> None:
    """
    Internal method to validate regression base inputs.

    :param y_test: Target values.
    :param y_pred: Target predictions.
    :param metrics: Metrics to compute.
    :param valid_metrics: The set of metrics available for the task.
    :param task: The task for which validation is performed.
    :param ref_code: The reference code used if the metrics contain metric not
                     in the valid_metrics.
    """
    _validate_metrics_list(task, metrics, valid_metrics, ref_code)

    _check_array_type(y_test, 'y_test', reference_code=f"validate_{task}")
    _check_array_type(y_pred, 'y_pred', reference_code=f"validate_{task}")

    _check_arrays_first_dim(y_test, y_pred, 'y_test', 'y_pred', reference_code=f"validate_{task}")
    _check_array_values(y_test, 'y_test', reference_code=f"validate_{task}")
    _check_array_values(y_pred, 'y_pred', reference_code=f"validate_{task}")


def validate_regression(y_test: np.ndarray,
                        y_pred: np.ndarray,
                        metrics: List[str]) -> None:
    """
    Validate the inputs for scoring regression.

    :param y_test: Target values.
    :param y_pred: Target predictions.
    :param metrics: Metrics to compute.
    """
    _validate_regression_base(
        y_test=y_test,
        y_pred=y_pred,
        metrics=metrics,
        valid_metrics=constants.Metric.REGRESSION_SET,
        task=constants.Tasks.REGRESSION,
        ref_code=ReferenceCodes._METRIC_INVALID_REGRESSION_METRIC)


def _log_regression_base_debug(y_test: np.ndarray,
                               y_pred: np.ndarray,
                               y_min: Optional[float],
                               y_max: Optional[float],
                               task: str,
                               sample_weight: Optional[np.ndarray] = None) -> None:
    """
    Log shapes of regression inputs for debugging.

    :param y_test: Target values.
    :param y_pred: Predicted values.
    :param y_min: Minimum target value.
    :param y_max: Maximum target value.
    :param task: The task to send the log for.
    :param sample_weight: Weights for the samples.
    """
    min_max_equal = None if None in [y_min, y_max] else y_min == y_max
    debug_data = {
        'y_test_shape': y_test.shape,
        'y_pred_shape': y_pred.shape,
        'y_test_unique_length': np.unique(y_test).shape[0],
        'y_pred_unique_length': np.unique(y_pred).shape[0],
        'y_test_has_negative': (y_test < 0).sum() > 0,
        'y_pred_has_negative': (y_pred < 0).sum() > 0,
        'min_max_equal': min_max_equal,
        'sample_weight_shape': None if sample_weight is None else sample_weight.shape
    }

    logger.info("{} metrics debug: {}".format(task.title(), debug_data))


def log_regression_debug(y_test: np.ndarray,
                         y_pred: np.ndarray,
                         y_min: Optional[float],
                         y_max: Optional[float],
                         sample_weight: Optional[np.ndarray] = None) -> None:
    """
    Log shapes of regression inputs for debugging.

    :param y_test: Target values.
    :param y_pred: Predicted values.
    :param y_min: Minimum target value.
    :param y_max: Maximum target value.
    :param sample_weight: Weights for the samples.
    """
    _log_regression_base_debug(y_test=y_test,
                               y_pred=y_pred,
                               y_min=y_min,
                               y_max=y_max,
                               task=constants.Tasks.REGRESSION,
                               sample_weight=sample_weight)


def validate_chat_completion(y_test: List[Any],
                             y_pred: List[str],
                             metrics: List[str],
                             tokenizer: Any,
                             smoothing: bool,
                             aggregator: bool,
                             stemmer: bool,
                             use_static_script: bool,
                             model_id: Optional[str],
                             batch_size: Optional[int],
                             add_start_token: Optional[bool],
                             openai_params: dict,
                             openai_api_batch_size: int,
                             use_chat_completion_api: bool,
                             llm_params: dict,
                             llm_api_batch_size: int,
                             score_version: str,
                             use_previous_conversation: bool,
                             score_all_conversations: bool, ):
    """
    Validate the inputs for chat completion.

    :param y_test: Actual list of list of references
    :param y_pred: Actual list of predictions
    :param metrics: Metrics to compute.
    :param tokenizer: function that takes input a string, and returns a list of tokens
    :param smoothing: Boolean to indicate whether to smooth out the bleu score
    :param aggregator: Boolean to indicate whether to aggregate scores
    :param stemmer: Boolean to indicate whether to use Porter stemmer for word suffixes
    :param use_static_script: Boolean to indicate whether to use static script
        for computing bleu and rouge score
    :param model_id: model used for calculating Perplexity.
        Perplexity can only be calculated for causal language models.
    :param batch_size: (int) the batch size to run texts through the model. Defaults to 16.
    :param add_start_token: (bool) whether to add the start token to the texts,
        so the perplexity can include the probability of the first word. Defaults to True.
    :param openai_params: Dictionary containing credentials to initialize or setup LLM
    :param openai_api_batch_size: number of prompts to be batched in one API call.
    :param use_chat_completion_api: boolean flag to choose between openAI completion vs chat completion API.
    :param llm_params: Dictionary containing credentials to initialize or setup LLM
    :param llm_api_batch_size: number of prompts to be batched in one API call for LLM
    :param score_version: Version of rag evaluation metrics to be computed
    :param use_previous_conversation: boolean value to indicate if we need to use_previous_conversation
             for computing rag-evaluation metrics.
    :param score_all_conversations: boolean value to indicate to calculate scores for all conversations by
             by appending all assistant responses.
    """
    reference_code = constants.ReferenceCodes.VALIDATE_CHAT_COMPLETION
    _validate_metrics_list("chat completion", metrics, constants.Metric.CHAT_COMPLETION_SET, reference_code)

    ignore_y_test = False
    # y_test can be None for perplexity
    if constants.Metric.FMPerplexity in metrics:
        ignore_y_test = True

    if tokenizer:
        _check_seq2seq_tokenizer(tokenizer, 'tokenizer', reference_code=reference_code)
    _check_seq2seq_bool(smoothing, 'smoothing', reference_code=reference_code)
    _check_seq2seq_bool(aggregator, 'aggregator', reference_code=reference_code)
    _check_seq2seq_bool(stemmer, 'stemmer', reference_code=reference_code)
    _check_seq2seq_bool(use_static_script, 'use_static_script', reference_code=reference_code)
    _check_seq2seq_bool(add_start_token, 'add_start_token', reference_code=reference_code)
    _check_seq2seq_str(model_id, 'model_id', reference_code=reference_code)
    _check_seq2seq_int(batch_size, 'batch_size', ignore_none=True, reference_code=reference_code)
    _check_seq2seq_dict(openai_params, 'openai_params', ignore_none=True, reference_code=reference_code)
    _check_seq2seq_int(openai_api_batch_size, 'openai_api_batch_size', reference_code=reference_code)
    _check_seq2seq_bool(use_chat_completion_api, 'use_chat_completion_api', ignore_none=True,
                        reference_code=reference_code)
    _check_seq2seq_dict(llm_params, 'llm_params', ignore_none=True, reference_code=reference_code)
    _check_seq2seq_int(llm_api_batch_size, 'llm_api_batch_size', reference_code=reference_code)
    _check_seq2seq_str(score_version, 'score_version', reference_code=reference_code)
    _check_seq2seq_bool(use_previous_conversation, "use_previous_conversation",
                        reference_code=reference_code)
    _check_seq2seq_bool(score_all_conversations, "score_all_conversations",
                        reference_code=reference_code)
    _check_seq2seq_list_of_list_of_str(y_test, 'y_test', ignore_none=ignore_y_test, reference_code=reference_code)
    _check_chat_conversation(y_pred, 'y_pred', reference_code=reference_code)
    if y_test is not None:
        Contract.assert_true(len(y_test) == len(y_pred), 'Number of samples in y_test and y_pred do not match',
                             log_safe=True, reference_code=reference_code, target='y_test')


def validate_rag_evaluation(y_test: List[Any],
                            y_pred: List[str],
                            metrics: List[str],
                            openai_params: dict,
                            openai_api_batch_size: int,
                            use_chat_completion_api: bool,
                            llm_params: dict,
                            llm_api_batch_size: int,
                            score_version: str,
                            use_previous_conversation: bool):
    """
    Validate the inputs for rag evaluation.

    :param y_test: multi-turn conversation for rag-evaluation metrics
    :param y_pred: multi-turn conversation for rag-evaluation metrics
    :param metrics: rag-evaluation metrics to compute.
    :param openai_params: Dictionary containing credentials to initialize or setup LLM
    :param openai_api_batch_size: number of prompts to be batched in one API call.
    :param use_chat_completion_api: boolean flag to choose between openAI completion vs chat completion API.
    :param llm_params: Dictionary containing credentials to initialize or setup LLM
    :param llm_api_batch_size: number of prompts to be batched in one API call for LLM
    :param score_version: Version of rag evaluation metrics to be computed
    :param use_previous_conversation: boolean value to indicate if we need to use_previous_conversation
             for computing rag-evaluation metrics.
    """
    reference_code = "validate_rag_evaluation"
    _validate_metrics_list("rag evaluation", metrics, constants.Metric.RAG_EVALUATION_SET, reference_code)

    _check_seq2seq_dict(openai_params, 'openai_params', ignore_none=True, reference_code=reference_code)
    _check_seq2seq_int(openai_api_batch_size, 'openai_api_batch_size', reference_code=reference_code)
    _check_seq2seq_bool(use_chat_completion_api, 'use_chat_completion_api', ignore_none=True,
                        reference_code=reference_code)
    _check_seq2seq_dict(llm_params, 'llm_params', ignore_none=True, reference_code=reference_code)
    _check_seq2seq_int(llm_api_batch_size, 'llm_api_batch_size', reference_code=reference_code)
    _check_seq2seq_str(score_version, 'score_version', reference_code=reference_code)
    _check_seq2seq_bool(use_previous_conversation, "use_previous_conversation",
                        reference_code=reference_code)
    # TODO: currently, we don't need y_test for computing rag_evaluation metrics
    _check_chat_conversation(y_pred, 'y_pred', reference_code=reference_code)


def log_rag_evaluation_debug(y_test: List[Any],
                             y_pred: List[str],
                             metrics: List[str],
                             openai_params: dict,
                             openai_api_batch_size: int,
                             use_chat_completion_api: bool,
                             llm_params: dict,
                             llm_api_batch_size: int,
                             score_version: str,
                             use_previous_conversation: bool) -> None:
    """
    Log shapes of rag evaluation inputs for debugging.

    :param y_test: multi-turn conversation for rag-evaluation metrics
    :param y_pred: multi-turn conversation for rag-evaluation metrics
    :param metrics: rag-evaluation metrics to compute.
    :param openai_params: Dictionary containing credentials to initialize or setup LLM
    :param openai_api_batch_size: number of prompts to be batched in one API call.
    :param use_chat_completion_api: boolean flag to choose between openAI completion vs chat completion API.
    :param llm_params: Dictionary containing credentials to initialize or setup LLM
    :param llm_api_batch_size: number of prompts to be batched in one API call for LLM
    :param score_version: Version of rag evaluation metrics to be computed
    :param use_previous_conversation: boolean value to indicate if we need to use_previous_conversation
             for computing rag-evaluation metrics.
    """
    debug_data = {
        'y_test_length': len(y_test) if y_test is not None else 0,
        'y_pred_length': len(y_pred),
        'metrics': metrics,
        'using_openai_api': "yes" if openai_params is not None else "no",
        'openai_api_batch_size': openai_api_batch_size,
        'use_chat_completion_api': use_chat_completion_api,
        'using_llm_deployment_api': "yes" if llm_params is not None else "no",
        'llm_api_batch_size': llm_api_batch_size,
        'score_version': score_version,
        'use_previous_conversation': use_previous_conversation,
    }

    logger.info("rag evaluation metrics debug: {}".format(debug_data))


def log_chat_completion_debug(y_test: List[Any],
                              y_pred: List[str],
                              metrics: List[str],
                              tokenizer: Any,
                              smoothing: bool,
                              aggregator: bool,
                              stemmer: bool,
                              use_static_script: bool,
                              model_id: Optional[str],
                              batch_size: Optional[int],
                              add_start_token: Optional[bool],
                              openai_params: dict,
                              openai_api_batch_size: int,
                              use_chat_completion_api: bool,
                              llm_params: dict,
                              llm_api_batch_size: int,
                              score_version: str,
                              use_previous_conversation: bool,
                              score_all_conversations: bool) -> None:
    """
    Log shapes of chat completion inputs for debugging.

    :param y_test: Actual list of list of references
    :param y_pred: Actual list of predictions
    :param metrics: rag-evaluation metrics to compute.
    :param tokenizer: function that takes input a string, and returns a list of tokens
    :param smoothing: Boolean to indicate whether to smooth out the bleu score
    :param aggregator: Boolean to indicate whether to aggregate scores
    :param stemmer: Boolean to indicate whether to use Porter stemmer for word suffixes
    :param use_static_script: Boolean to indicate whether to use static script
        for computing bleu and rouge score
    :param model_id: model used for calculating Perplexity.
        Perplexity can only be calculated for causal language models.
    :param batch_size: (int) the batch size to run texts through the model. Defaults to 16.
    :param add_start_token: (bool) whether to add the start token to the texts,
        so the perplexity can include the probability of the first word. Defaults to True.
    :param openai_params: Dictionary containing credentials to initialize or setup LLM
    :param openai_api_batch_size: number of prompts to be batched in one API call.
    :param use_chat_completion_api: boolean flag to choose between openAI completion vs chat completion API.
    :param llm_params: Dictionary containing credentials to initialize or setup LLM
    :param llm_api_batch_size: number of prompts to be batched in one API call for LLM
    :param score_version: Version of rag evaluation metrics to be computed
    :param use_previous_conversation: boolean value to indicate if we need to use_previous_conversation
             for computing rag-evaluation metrics.
    :param score_all_conversations: boolean value to indicate to calculate scores for all conversations by
             by appending all assistant responses.
    """
    debug_text = 'computing evaluation for chat-completion task'
    debug_data = {
        'y_test_length': len(y_test) if y_test is not None else 0,
        'y_pred_length': len(y_pred),
        'metrics': metrics,
        'tokenizer_example_output': ' '.join(tokenizer(debug_text)) if tokenizer else debug_text,
        'smoothing': smoothing,
        'aggregator': aggregator,
        'stemmer': stemmer,
        'use_static_script': use_static_script,
        'model_id': model_id,
        'batch_size': batch_size,
        'add_start_token': add_start_token,
        'using_openai_api': "yes" if openai_params is not None else "no",
        'openai_api_batch_size': openai_api_batch_size,
        'use_chat_completion_api': use_chat_completion_api,
        'using_llm_deployment_api': "yes" if llm_params is not None else "no",
        'llm_api_batch_size': llm_api_batch_size,
        'score_version': score_version,
        'use_previous_conversation': use_previous_conversation,
        'score_all_conversations': score_all_conversations,
    }

    logger.info("Chat completion metrics debug: {}".format(debug_data))


def validate_forecasting(y_test: np.ndarray,
                         y_pred: np.ndarray,
                         metrics: List[str]) -> None:
    """
    Validate the inputs for scoring forecasting.

    :param y_test: Target values.
    :param y_pred: Target predictions.
    :param metrics: Metrics to compute.
    """
    _validate_regression_base(
        y_test=y_test,
        y_pred=y_pred,
        metrics=metrics,
        valid_metrics=(constants.Metric.SCALAR_REGRESSION_SET | constants.Metric.FORECAST_SET),
        task=constants.Tasks.FORECASTING,
        ref_code=ReferenceCodes._METRIC_INVALID_FORECASTING_METRIC)


def log_forecasting_debug(y_test: np.ndarray,
                          y_pred: np.ndarray,
                          y_min: Optional[float],
                          y_max: Optional[float],
                          sample_weight: Optional[np.ndarray] = None) -> None:
    """
    Log shapes of regression inputs for debugging.

    :param y_test: Target values.
    :param y_pred: Predicted values.
    :param y_min: Minimum target value.
    :param y_max: Maximum target value.
    :param sample_weight: Weights for the samples.
    """
    _log_regression_base_debug(y_test=y_test,
                               y_pred=y_pred,
                               y_min=y_min,
                               y_max=y_max,
                               task=constants.Tasks.FORECASTING,
                               sample_weight=sample_weight)


def _check_arrays_first_dim(array_a: np.ndarray,
                            array_b: np.ndarray,
                            array_a_name: str,
                            array_b_name: str,
                            reference_code: str = None) -> None:
    """
    Validate that two arrays have the same shape in the first dimension.

    :array_a: First array.
    :array_b: Second array.
    :array_a_name: First array name.
    :array_b_name: Second array name.
    """
    Contract.assert_value(array_a, array_a_name, reference_code=reference_code)
    Contract.assert_value(array_b, array_b_name, reference_code=reference_code)
    message = "Number of samples does not match in {} ({}) and {} ({})".format(
        array_a_name, array_a.shape[0], array_b_name, array_b.shape[0])
    Contract.assert_true(array_a.shape[0] == array_b.shape[0], message=message, log_safe=True,
                         reference_code=reference_code, target=array_a_name)


def convert_decimal_to_float(y_test: np.ndarray) -> np.ndarray:
    """
    If the y-test array consists of elements of type decimal.Decimal,
    then convert these to float to allow for the subsequent metrics calculations.

    :param y_test: array with y_test values
    :return: y_test array converted to float, if it comprised of decimals
    """
    if y_test.dtype == object and isinstance(y_test[0], Decimal):
        y_test = y_test.astype(float)
    return y_test


def _validate_metrics_list(task_type, metrics, default_metrics, ref_code):
    """
    Validate metrics list helper for task type.

    :param task_type: Tasks for which metrics have to be verified.
    :param metrics: Metrics to check.
    :param default_metrics: Default metrics list.
    """
    extra_metrics = []
    for metric in list(metrics):
        if metric not in default_metrics:
            extra_metrics += [metric]
            metrics.remove(metric)
    Contract.assert_true(
        len(metrics) > 0,
        "No valid metrics passed for {}. Invalid metrics passed: {}. Choose among the metrics: {} ".format(
            task_type, ', '.join(extra_metrics), ', '.join(default_metrics)),
        target="metric", reference_code=ref_code
    )
    if len(extra_metrics) > 0:
        logger.warning("Ignoring invalid metrics passed for {}: {}.".format(task_type, ', '.join(extra_metrics)))

    return metrics


def _check_array_values(arr: np.ndarray,
                        name: str,
                        validate_type: bool = True,
                        reference_code: str = None) -> None:
    """
    Check the array for correct types and reasonable values.

    :param arr: Array to check.
    :param name: Array name.
    :param validate_type: Whether to validate the array type.
    """
    # Convert object types
    if arr.dtype == object:
        if isinstance(arr[0], (int, float)):
            arr = arr.astype(float)
        elif isinstance(arr[0], str):
            arr = arr.astype(str)

    if arr.dtype.kind in set('bcfiu'):
        message = "Elements of {} cannot be {}"
        Contract.assert_true(~np.isnan(arr).any(), message=message.format(name, 'NaN'), log_safe=True,
                             reference_code=reference_code, target=name)
        Contract.assert_true(np.isfinite(arr).all(), message=message.format(name, 'infinite'), log_safe=True,
                             reference_code=reference_code, target=name)
    elif np.issubdtype(arr.dtype, np.str_):
        pass
    else:
        if validate_type:
            message = ("{} should have numeric or string type, found type {}. "
                       "Elements have type {}. Please consider multilabel flag is "
                       "set appropriately.").format(name, arr.dtype, type(arr[0]))
            Contract.assert_true(False, message=message, log_safe=True, reference_code=reference_code, target=name)


def _check_array_type(arr: Any, name: str, ignore_none: bool = False, reference_code: str = None) -> None:
    """
    Check that the input is a numpy array.

    :param arr: Array object to validate.
    :param name: Name of array to use in error message.
    :param validate_none: Whether to validate the array as None-type.
    """
    if ignore_none and arr is None:
        return

    Contract.assert_value(arr, name, reference_code=reference_code)

    try:
        arr.dtype
    except AttributeError:
        message = "Argument {} must be a numpy array, not {}".format(name, type(arr))
        Contract.assert_true(False, message=message, log_safe=True, reference_code=reference_code, target=name)


def _check_arrays_same_type(array_dict: Dict[str, np.ndarray], check_numeric_type: bool = True,
                            reference_code: str = None, target: str = None) -> None:
    """
    Check that multiple arrays have the same types.

    :param array_dict: Dictionary from array name to array.
    :param check_numeric_type: whether to compare numeric arrays
    """
    items = list(array_dict.items())
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            i_type, j_type = items[i][1].dtype, items[j][1].dtype
            i_name, j_name = items[i][0], items[j][0]

            # Handle equivalent types like int32/int64 integers, U1/U2 strings
            if check_numeric_type:
                # check if two numeric types are equivalent types
                if np.issubdtype(i_type, np.integer) and np.issubdtype(j_type, np.integer):
                    continue
                if np.issubdtype(i_type, np.floating) and np.issubdtype(j_type, np.floating):
                    continue
            else:
                # if they are both numeric, then continue
                if np.issubdtype(i_type, np.number) and np.issubdtype(j_type, np.number):
                    continue
            if np.issubdtype(i_type, np.str_) and np.issubdtype(j_type, np.str_):
                continue

            # Handle all other types
            Contract.assert_true(i_type == j_type,
                                 message="{} ({}) does not have the same type as {} ({})".format(
                                     i_name, i_type, j_name, j_type),
                                 log_safe=True, target=target, reference_code=reference_code)


def _check_dim(arr: np.ndarray,
               name: str,
               n_dim: int,
               reference_code: str) -> None:
    """
    Check the number of dimensions for the given array.

    :param arr: Array to check.
    :param name: Array name.
    :param n_dim: Expected number of dimensions.
    """
    Contract.assert_true(arr.ndim == n_dim, message="{} must be an ndarray with {} dimensions, found {}".format(
        name, n_dim, arr.ndim), target=name, log_safe=True, reference_code=reference_code)


def _check_seq2seq_list_of_list_of_str(refs: Any, name: str, ignore_none: bool = False,
                                       reference_code: str = None) -> None:
    """
    :param refs: References to validate.
    :param name: Name of references to use in error message.
    :param ignore_none: Whether to validate references as None-type.
    """
    if ignore_none and refs is None:
        return

    Contract.assert_value(refs, name, reference_code=reference_code)
    Contract.assert_true(isinstance(refs, list), message="{} must be a list".format(name),
                         target=name, log_safe=True, reference_code=reference_code)

    for ref in refs:
        _check_seq2seq_list_of_str(ref, name + '_value', reference_code=reference_code)


def _check_seq2seq_list_of_str(preds: Any, name: str, ignore_none: bool = False, reference_code: str = None) -> None:
    """
    :param preds: Predictions to validate.
    :param name: Name of predictions to use in error message.
    :param ignore_none: Whether to validate predictions as None-type.
    """

    if ignore_none and preds is None:
        return

    Contract.assert_value(preds, name, reference_code=reference_code)
    Contract.assert_true(isinstance(preds, list), message="{} must be a list".format(name),
                         target=name, log_safe=True, reference_code=reference_code)
    convert_to_str = False if reference_code == constants.ReferenceCodes.VALIDATE_CHAT_COMPLETION else True
    for idx in range(len(preds)):
        preds[idx] = _check_seq2seq_str(preds[idx], name + '_value', reference_code=reference_code,
                                        convert_to_str=convert_to_str)


def _check_seq2seq_list_of_int(preds: Any, name: str, ignore_none: bool = False, reference_code: str = None) -> None:
    """
    :param preds: Predictions to validate.
    :param name: Name of predictions to use in error message.
    :param ignore_none: Whether to validate predictions as None-type.
    """

    if ignore_none and preds is None:
        return

    Contract.assert_value(preds, name, reference_code=reference_code)
    Contract.assert_true(isinstance(preds, list), message="{} must be a list".format(name),
                         target=name, log_safe=True, reference_code=reference_code)

    for value in preds:
        _check_seq2seq_int(value, name + '_value', reference_code=reference_code)


def _check_seq2seq_str(obj: Any, name: str, ignore_none: bool = False, reference_code: str = None,
                       convert_to_str: bool = False) -> Optional[str]:
    """
    :param obj: Object to validate as string.
    :param name: Name of predictions to use in error message.
    :param ignore_none: Whether to validate predictions as None-type.
    """
    if ignore_none and obj is None:
        return

    Contract.assert_value(obj, name, reference_code=reference_code)
    if not convert_to_str:
        Contract.assert_true(isinstance(obj, str), message="{} must be a string".format(name),
                             target=name, log_safe=True, reference_code=reference_code)

    if not isinstance(obj, str):
        try:
            logger.warning("{} must be a string. Trying to convert {} to str.".format(name, type(obj)))
            obj = str(obj)
        except Exception:
            Contract.assert_true(False, message="{} must be a string".format(name),
                                 target=name, log_safe=True, reference_code=reference_code)
    return obj


def _check_seq2seq_int(obj: Any, name: str, ignore_none: bool = False, reference_code: str = None) -> None:
    """
    :param obj: Object to validate as int.
    :param name: Name of object to use in error message.
    :param ignore_none: Whether to validate object as None-type.
    """
    if ignore_none and obj is None:
        return

    Contract.assert_value(obj, name, reference_code=reference_code)
    Contract.assert_true(isinstance(obj, int), message="{} must be a integer".format(name),
                         target=name, log_safe=True, reference_code=reference_code)


def _check_seq2seq_dict(obj: Any, name: str, ignore_none: bool = False, reference_code: str = None) -> None:
    """
    :param obj: Object to validate as dict.
    :param name: Name of predictions to use in error message.
    :param ignore_none: Whether to validate predictions as None-type.
    """
    if ignore_none and obj is None:
        return

    Contract.assert_value(obj, name, reference_code=reference_code)
    Contract.assert_true(isinstance(obj, dict), message="{} must be a dict".format(name),
                         target=name, log_safe=True, reference_code=reference_code)


def _check_seq2seq_bool(obj: Any, name: str, ignore_none: bool = False, reference_code: str = None) -> None:
    """
    :param obj: Object to validate as bool.
    :param name: Name of predictions to use in error message.
    :param ignore_none: Whether to validate predictions as None-type.
    """
    if ignore_none and obj is None:
        return

    Contract.assert_true(isinstance(obj, bool), message="{} must be of bool type".format(name),
                         target=name, log_safe=True, reference_code=reference_code)


def _check_seq2seq_tokenizer(obj: Any, name: str, ignore_none: bool = False, reference_code: str = None) -> None:
    """
    :param obj: Object to validate as tokenizer.
    :param name: Name of tokenizer to use in error message.
    :param ignore_none: Whether to validate tokenizer as None-type.
    """
    Contract.assert_true(hasattr(obj, '__call__'), message="{} must be callable".format(name),
                         target=name, log_safe=True, reference_code=reference_code)

    # TBD: Is this check necessary? Will it work for all tokenizers?
    # Check if tokenizer returns list of tokens for a simple text
    text = 'the quick brown fox jumped over the lazy dog'
    tokens = obj(text)
    _check_seq2seq_list_of_str(tokens, name + '_output', reference_code=reference_code)


def _check_rag_conversation(obj: Any, name: str, ignore_none: bool = False, reference_code: str = None) -> None:
    """
    :param obj: Object to validate as string.
    :param name: Name of predictions to use in error message.
    :param ignore_none: Whether to validate predictions as None-type.
    """
    if ignore_none and obj is None:
        return

    Contract.assert_true(isinstance(obj, list), message="{} must be a list".format(name),
                         target=name, log_safe=True, reference_code=reference_code)

    for conversation_num, conversation in enumerate(obj):
        Contract.assert_true(isinstance(conversation, list),
                             message="every conversation must be a list. please check "
                                     "conversation_number: {}".format(conversation_num + 1),
                             target=name, log_safe=True, reference_code=reference_code)
        for turn_num, turn in enumerate(conversation):
            Contract.assert_true(isinstance(turn, dict),
                                 message="each turn in the conversation must be a dict. please check "
                                         "turn_number: {} in conversation_number: {}".format(turn_num + 1,
                                                                                             conversation_num + 1),
                                 target=name, log_safe=True, reference_code=reference_code)

            Contract.assert_true('user' in turn and 'assistant' in turn and 'retrieved_documents' in turn,
                                 message="please ensure to have user, assistant, retrieved_documents keys "
                                         "in each turn of the conversation.",
                                 target=name, log_safe=True, reference_code=reference_code)

            Contract.assert_true(isinstance(turn['user'], dict) and isinstance(turn['assistant'], dict),
                                 message="please ensure to have values of user, assistant as a dict. please check "
                                         "turn_number: {} in conversation_number: {}".format(turn_num + 1,
                                                                                             conversation_num + 1),
                                 target=name, log_safe=True, reference_code=reference_code)

            try:
                json.loads(turn['retrieved_documents'])
            except Exception:
                Contract.assert_true(False,
                                     message="failed to parse retrieved documents as json. please check "
                                             "turn_number: {} in conversation_number: {}".format(turn_num + 1,
                                                                                                 conversation_num + 1),
                                     target=name, log_safe=True, reference_code=reference_code)


def _check_chat_conversation(obj: Any, name: str, ignore_none: bool = False, reference_code: str = None) -> None:
    """
    :param obj: Object to validate as string.
    :param name: Name of predictions to use in error message.
    :param ignore_none: Whether to validate predictions as None-type.
    """
    if ignore_none and obj is None:
        return

    Contract.assert_true(isinstance(obj, list), message="{} must be a list".format(name),
                         target=name, log_safe=True, reference_code=reference_code)

    for conversation_num, conversation in enumerate(obj):
        Contract.assert_true(isinstance(conversation, list) or isinstance(conversation, dict),
                             message="every conversation must be a list or dictionary. please check "
                                     "conversation_number: {}".format(conversation_num + 1),
                             target=name, log_safe=True, reference_code=reference_code)
        # llama format
        if isinstance(conversation, list):
            for turn_num, turn in enumerate(conversation):
                Contract.assert_true(isinstance(turn, dict),
                                     message="each turn in the conversation must be a dict. please check "
                                             "turn_number: {} in conversation_number: {}"
                                     .format(turn_num + 1, conversation_num + 1),
                                     target=name,
                                     log_safe=True,
                                     reference_code=reference_code)

                Contract.assert_true('role' in turn and 'content' in turn,
                                     message="please ensure to have role, content keys "
                                             "in each turn of the conversation.",
                                     target=name, log_safe=True, reference_code=reference_code)

                Contract.assert_true(isinstance(turn['role'], str) and isinstance(turn['content'], str),
                                     message="please ensure to have values of user, assistant as string. please check "
                                             "turn_number: {} in conversation_number: {}"
                                     .format(turn_num + 1, conversation_num + 1),
                                     target=name,
                                     log_safe=True,
                                     reference_code=reference_code)

                Contract.assert_true(turn["role"] in [constants.ChatCompletionConstants.USER_PERSONA,
                                                      constants.ChatCompletionConstants.ASSISTANT_PERSONA,
                                                      constants.ChatCompletionConstants.SYSTEM_PERSONA],
                                     message="please ensure to have any of the following roles : '{}', '{}', '{}' in "
                                             "conversation. please check turn_number: {} in "
                                             "conversation_number: {}"
                                     .format(constants.ChatCompletionConstants.USER_PERSONA,
                                             constants.ChatCompletionConstants.ASSISTANT_PERSONA,
                                             constants.ChatCompletionConstants.SYSTEM_PERSONA,
                                             turn_num + 1, conversation_num + 1),
                                     target=name, log_safe=True, reference_code=reference_code)
        else:  # openai format
            Contract.assert_true("conversation" in conversation,
                                 message="if json format, must have conversation field",
                                 target=name, log_safe=True, reference_code=reference_code)
            Contract.assert_true("meta_data" in conversation,
                                 message="if json format, must have meta_data field",
                                 target=name, log_safe=True, reference_code=reference_code)


def format_1d(arr: np.ndarray,
              name: str) -> np.ndarray:
    """
    Format an array as 1d if possible.

    :param arr: The array to reshape.
    :param name: Name of the array to reshape.
    :return: Array of shape (x,).
    """
    _check_array_type(arr, name, reference_code='format_1d')

    if arr.ndim == 2 and (arr.shape[0] == 1 or arr.shape[1] == 1):
        arr = np.ravel(arr)
    return arr


def log_failed_splits(scores, metric):
    """
    Log if a metric could not be computed for some splits.

    :scores: The scores over all splits for one metric.
    :metric: Name of the metric.
    """
    n_splits = len(scores)

    failed_splits = []
    for score_index, score in enumerate(scores):
        if utilities.is_scalar(metric):
            if np.isnan(score):
                failed_splits.append(score_index)
        else:
            if NonScalarMetric.is_error_metric(score):
                failed_splits.append(score_index)
    n_failures = len(failed_splits)
    failed_splits_str = ', '.join([str(idx) for idx in failed_splits])

    if n_failures > 0:
        warn_args = metric, n_failures, n_splits, failed_splits_str
        warn_msg = "Could not compute {} for {}/{} validation splits: {}"
        logger.warning(warn_msg.format(*warn_args))


def validate_multilabel_binary_format(y_test, y_pred, y_pred_proba):
    """Validates if multi label input is in binary or one hot encoded format."""
    y_test_values = y_test.flatten()
    y_pred_values = y_pred.flatten()

    for test_val, pred_val in zip(y_test_values, y_pred_values):
        test_val, pred_val = str(test_val), str(pred_val)
        if test_val not in ("0", "1") or pred_val not in ("0", "1"):
            return False

    if y_pred_proba is not None:
        return y_test.shape == y_pred.shape == y_pred_proba.shape

    return y_test.shape == y_pred.shape

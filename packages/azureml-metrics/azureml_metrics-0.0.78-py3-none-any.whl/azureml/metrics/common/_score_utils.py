# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility files for compute_metrics"""
import numpy as np
import logging

from azureml.metrics import constants
from azureml.metrics.text.classification.azureml_classification_metrics import AzureMLClassificationMetrics
from azureml.metrics.text.fill_mask.azureml_fill_mask_metrics import AzureMLFillMaskMetrics
from azureml.metrics.tabular.forecasting.azureml_forecasting_metrics import AzureMLForecastingMetrics
from azureml.metrics.vision.od_is_eval.azureml_od_is_metrics import AzureMLODISMetrics, AzureMLODMetrics, \
    AzureMLISMetrics
from azureml.metrics.vision.generation_eval.azureml_image_generation_metrics import AzureMLImageGenerationMetrics
from azureml.metrics.vision.track_eval.azureml_mot_metrics import AzureMlMOTODMetrics
from azureml.metrics.text.qa.azureml_qa_metrics import AzureMLQAMetrics
from azureml.metrics.tabular.regression.azureml_regression_metrics import AzureMLRegressionMetrics
from azureml.metrics.text.summarization.azureml_summarization_metrics import AzureMLSummarizationMetrics
from azureml.metrics.text.text_generation.azureml_text_generation_metrics import AzureMLTextGenerationMetrics
from azureml.metrics.text.chat_completion.azureml_chat_completion_metrics import AzureMLChatCompletionMetrics
from azureml.metrics.text.rag_evaluation.azureml_rag_evaluation_metrics import AzureMLRagEvaluationMetrics
from azureml.metrics.text.ner.azureml_text_ner_metrics import AzureMLTextNERMetrics
from azureml.metrics.text.translation.azureml_translation_metrics import AzureMLTranslationMetrics
from azureml.metrics.text.code_generation.azureml_code_generation import AzureMLCodeGenerationMetrics
from azureml.metrics.common.azureml_custom_prompt_metric import AzureMLCustomPromptMetric
from azureml.metrics.common.utilities import extract_common_kwargs, check_kwargs
from azureml.metrics.common.exceptions import InvalidValueException, MetricsException
from azureml.metrics.constants import Tasks

logger = logging.getLogger(constants.TelemetryConstants.APP_NAME)


def compute_metrics_classification(task_type, y_test, y_pred, y_pred_proba, kwargs):
    metrics_list = kwargs.pop('metrics', None)
    class_labels = kwargs.pop('class_labels', None)
    train_labels = kwargs.pop('train_labels', None)
    sample_weight = kwargs.pop('sample_weight', None)
    y_transformer = kwargs.pop('y_transformer', None)
    use_binary = kwargs.pop('use_binary', False)
    enable_metric_confidence = kwargs.pop('enable_metric_confidence', False)
    multilabel = kwargs.pop('multilabel', False)
    positive_label = kwargs.pop('positive_label', None)
    confidence_metrics = kwargs.pop('confidence_metrics', None)
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    multilabel_tasks = [constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL,
                        constants.Tasks.IMAGE_CLASSIFICATION_MULTILABEL,
                        constants.Tasks.IMAGE_MULTI_LABEL_CLASSIFICATION]
    if task_type in multilabel_tasks:
        multilabel = True
    classification_kwargs = ["metrics", "class_labels", "train_labels", "sample_weight",
                             "y_transformer", "use_binary", "enable_metric_confidence",
                             "multilabel", "positive_label", "confidence_metrics"]
    check_kwargs(kwargs, task_type, classification_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLClassificationMetrics(
            metrics=metrics_list,
            class_labels=class_labels,
            train_labels=train_labels,
            sample_weight=sample_weight,
            y_transformer=y_transformer,
            use_binary=use_binary,
            enable_metric_confidence=enable_metric_confidence,
            multilabel=multilabel,
            positive_label=positive_label,
            confidence_metrics=confidence_metrics,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred, y_pred_probs=y_pred_proba)
        return computed_metrics


def compute_metrics_regression(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop("metrics", None)
    y_max = kwargs.pop("y_max", None)
    y_min = kwargs.pop("y_min", None)
    y_std = kwargs.pop("y_std", None)
    bin_info = kwargs.pop("bin_info", None)
    sample_weight = kwargs.pop("sample_weight", None)
    enable_metric_confidence = kwargs.pop("enable_metric_confidence", False)
    confidence_metrics = kwargs.pop("confidence_metrics", None)
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    regression_kwargs = ["metrics", "y_max", "y_min", "y_std",
                         "bin_info", "sample_weight", "enable_metric_confidence",
                         "confidence_metrics"]
    check_kwargs(kwargs, task_type, regression_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLRegressionMetrics(
            metrics=metrics_list,
            y_max=y_max,
            y_min=y_min,
            y_std=y_std,
            bin_info=bin_info,
            sample_weight=sample_weight,
            enable_metric_confidence=enable_metric_confidence,
            confidence_metrics=confidence_metrics,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_translation(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop('metrics', None)
    tokenizer = kwargs.pop('tokenizer', None)
    smoothing = kwargs.pop('smoothing', False)

    use_static_script = kwargs.pop('use_static_script', True)
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    translation_kwargs = ['metrics', 'tokenizer', 'smoothing']
    check_kwargs(kwargs, task_type, translation_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLTranslationMetrics(
            metrics=metrics_list,
            tokenizer=tokenizer,
            smoothing=smoothing,
            use_static_script=use_static_script,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_ner(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop('metrics', None)
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    ner_kwargs = ["metrics"]
    check_kwargs(kwargs, task_type, ner_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLTextNERMetrics(
            metrics=metrics_list,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_summarization(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop('metrics', None)
    tokenizer = kwargs.pop('tokenizer', None)
    aggregator = kwargs.pop('aggregator', True)
    stemmer = kwargs.pop('stemmer', False)
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    summarization_kwargs = ['metrics', 'tokenizer', 'aggregator', 'stemmer']
    check_kwargs(kwargs, task_type, summarization_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLSummarizationMetrics(
            metrics=metrics_list,
            tokenizer=tokenizer,
            aggregator=aggregator,
            stemmer=stemmer,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_qa(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop('metrics', None)
    tokenizer = kwargs.pop('tokenizer', None)
    regexes_to_ignore = kwargs.pop('regexes_to_ignore', None)
    ignore_case = kwargs.pop('ignore_case', False)
    ignore_punctuation = kwargs.pop('ignore_punctuation', False)
    ignore_numbers = kwargs.pop('ignore_numbers', False)
    # kwargs for BERT Score
    lang = kwargs.pop("lang", "en")
    model_type = kwargs.pop("model_type", "microsoft/deberta-large")
    idf = kwargs.pop("idf", False)
    rescale_with_baseline = kwargs.pop("rescale_with_baseline", True)
    # kwargs for gpt-similarity metric
    questions = kwargs.pop("questions", None)
    contexts = kwargs.pop("contexts", None)
    openai_api_batch_size = kwargs.pop("openai_api_batch_size", 20) \
        if isinstance(kwargs.get("openai_api_batch_size", 20), int) \
        and kwargs.get("openai_api_batch_size", 20) > 0 else 20
    use_openai_endpoint = kwargs.pop("use_openai_endpoint", False)
    openai_params = kwargs.pop("openai_params", None)
    max_concurrent_requests = kwargs.pop("max_concurrent_requests",
                                         constants.ConcurrencyConstants.MAX_CONCURRENT_REQUESTS)
    use_chat_completion_api = kwargs.pop("use_chat_completion_api", None)
    # kwargs for ada cosine similarity
    openai_embedding_engine = kwargs.pop("openai_embedding_engine", "text-embedding-ada-002")
    # kwargs for llama params
    llm_params = kwargs.pop("llm_params", None)
    llm_api_batch_size = kwargs.pop("llm_api_batch_size", 1) \
        if isinstance(kwargs.get("llm_api_batch_size", 1), int) \
        and kwargs.get("llm_api_batch_size", 1) > 0 else 1
    llm_use_chat_completion_payload = kwargs.pop("llm_use_chat_completion_payload", False)
    if use_chat_completion_api is True:
        openai_api_batch_size = 1

    # keyword argument for maximum number of concurrent requests
    max_concurrent_requests = kwargs.pop("max_concurrent_requests",
                                         constants.ConcurrencyConstants.MAX_CONCURRENT_REQUESTS)
    constants.ConcurrencyConstants.MAX_CONCURRENT_REQUESTS = max_concurrent_requests
    logger.info("Setting max_concurrent_requests to {} for computing GPT based question answering metrics".format(
        constants.ConcurrencyConstants.MAX_CONCURRENT_REQUESTS))

    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    qa_kwargs = ['metrics', 'tokenizer', 'regexes_to_ignore', 'ignore_case',
                 'ignore_punctuation', 'ignore_numbers', 'lang', 'model_type',
                 'questions', 'openai_params', 'idf', 'rescale_with_baseline',
                 'contexts', "openai_api_batch_size", "use_chat_completion_api",
                 "openai_embedding_engine", "llm_params", "llm_api_batch_size",
                 "llm_use_chat_completion_payload", "max_concurrent_requests"]
    check_kwargs(kwargs, task_type, qa_kwargs)

    if metrics_list is None:
        if task_type == Tasks.QUESTION_ANSWERING:
            metrics_list = constants.Metric.QA_SET
        elif task_type == Tasks.QUESTION_ANSWERING_MULTIPLE_GROUND_TRUTH:
            metrics_list = constants.Metric.QA_MULTIPLE_GROUND_TRUTH_SET

    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLQAMetrics(
            metrics=metrics_list,
            tokenizer=tokenizer,
            regexes_to_ignore=regexes_to_ignore,
            ignore_case=ignore_case,
            ignore_punctuation=ignore_punctuation,
            ignore_numbers=ignore_numbers,
            lang=lang,
            model_type=model_type,
            idf=idf,
            rescale_with_baseline=rescale_with_baseline,
            questions=questions,
            contexts=contexts,
            openai_api_batch_size=openai_api_batch_size,
            use_openai_endpoint=use_openai_endpoint,
            openai_params=openai_params,
            max_concurrent_requests=max_concurrent_requests,
            use_chat_completion_api=use_chat_completion_api,
            openai_embedding_engine=openai_embedding_engine,
            llm_params=llm_params,
            llm_api_batch_size=llm_api_batch_size,
            llm_use_chat_completion_payload=llm_use_chat_completion_payload,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_custom_prompt(task_type, y_test, y_pred, kwargs):
    custom_metric_name = kwargs.pop("custom_metric_name",
                                    constants.DefaultValues.DEFAULT_CUSTOM_PROMPT_METRIC_NAME)
    custom_metric_description = kwargs.pop("custom_metric_description", None)
    prompt_instruction = kwargs.pop("prompt_instruction", None)
    few_shot_examples = kwargs.pop("few_shot_examples", None)
    placeholder_prompt = kwargs.pop("placeholder_prompt", None)
    user_prompt_template = kwargs.pop("user_prompt_template", None)
    input_vars = kwargs.pop("input_vars", None)
    system_prompt_template = kwargs.pop("system_prompt_template", None)

    # dataframe which contain the data required for computing custom prompt
    custom_prompt_data = kwargs.pop("custom_prompt_data", None)

    openai_api_batch_size = kwargs.pop("openai_api_batch_size", 20) \
        if isinstance(kwargs.get("openai_api_batch_size", 20), int) \
        and kwargs.get("openai_api_batch_size", 20) > 0 else 20
    use_openai_endpoint = kwargs.pop("use_openai_endpoint", False)
    openai_params = kwargs.pop("openai_params", None)
    use_chat_completion_api = kwargs.pop("use_chat_completion_api", None)

    # kwargs for llama params
    # llm_params = kwargs.pop("llm_params", None)
    # llm_api_batch_size = kwargs.pop("llm_api_batch_size", 20) \
    #     if isinstance(kwargs.get("llm_api_batch_size", 20), int) \
    #     and kwargs.get("llm_api_batch_size", 20) > 0 else 20
    if use_chat_completion_api is True:
        openai_api_batch_size = 1
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLCustomPromptMetric(
            metric_name=custom_metric_name,
            metric_description=custom_metric_description,
            prompt_instruction=prompt_instruction,
            few_shot_examples=few_shot_examples,
            placeholder_prompt=placeholder_prompt,
            user_prompt_template=user_prompt_template,
            input_vars=input_vars,
            system_prompt_template=system_prompt_template,
            custom_prompt_data=custom_prompt_data,
            openai_api_batch_size=openai_api_batch_size,
            use_openai_endpoint=use_openai_endpoint,
            openai_params=openai_params,
            use_chat_completion_api=use_chat_completion_api,
            **kwargs
        )
        computed_metrics = metrics.compute()
        return computed_metrics


def compute_metrics_fill_mask(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop("metrics", None)
    # perplexity keyword arguments
    # using gpt2 as default model_id
    model_id = kwargs.pop("model_id", "gpt2")
    batch_size = kwargs.pop("batch_size", 16)
    add_start_token = kwargs.pop("add_start_token", True)
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    lm_kwargs = ["metrics", "model_id", "batch_size", "add_start_token"]
    check_kwargs(kwargs, task_type, lm_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLFillMaskMetrics(
            metrics=metrics_list,
            model_id=model_id,
            batch_size=batch_size,
            add_start_token=add_start_token,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_text_generation(task_type, y_test, y_pred, kwargs):
    sub_task = kwargs.pop('sub_task', None)

    if sub_task == constants.SubTaskType.TEXT_GENERATION_SUBTASK_CODE:
        return compute_metrics_code_generation(task_type, y_test, y_pred, kwargs)

    metrics_list = kwargs.pop("metrics", None)
    # bleu keyword arguments
    tokenizer = kwargs.pop('tokenizer', None)
    smoothing = kwargs.pop('smoothing', False)
    # rouge keyword arguments
    aggregator = kwargs.pop('aggregator', True)
    stemmer = kwargs.pop('stemmer', False)
    # perplexity keyword arguments
    # using gpt2 as default model_id
    model_id = kwargs.pop("model_id", "gpt2")
    batch_size = kwargs.pop("batch_size", 16)
    add_start_token = kwargs.pop("add_start_token", True)
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    text_generation_kwargs = ["metrics", "tokenizer", "smoothing",
                              "aggregator", "stemmer", "model_id", "batch_size",
                              "add_start_token"]
    check_kwargs(kwargs, task_type, text_generation_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLTextGenerationMetrics(
            metrics=metrics_list,
            tokenizer=tokenizer,
            smoothing=smoothing,
            aggregator=aggregator,
            stemmer=stemmer,
            model_id=model_id,
            batch_size=batch_size,
            add_start_token=add_start_token,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_chat_completion(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop("metrics", None)
    # bleu keyword arguments
    tokenizer = kwargs.pop('tokenizer', None)
    smoothing = kwargs.pop('smoothing', False)
    # rouge keyword arguments
    aggregator = kwargs.pop('aggregator', True)
    stemmer = kwargs.pop('stemmer', False)
    use_static_script = kwargs.pop('use_static_script', True)
    # perplexity keyword arguments
    # using gpt2 as default model_id
    model_id = kwargs.pop("model_id", "gpt2")
    batch_size = kwargs.pop("batch_size", 16)
    add_start_token = kwargs.pop("add_start_token", True)
    # keyword arguments for rag based metrics
    openai_params = kwargs.pop("openai_params", None)
    openai_api_batch_size = kwargs.pop("openai_api_batch_size", 20) \
        if isinstance(kwargs.get("openai_api_batch_size", 20), int) \
        and kwargs.get("openai_api_batch_size", 20) > 0 else 20
    use_chat_completion_api = kwargs.pop("use_chat_completion_api", None)
    # kwargs for llama params
    llm_params = kwargs.pop("llm_params", None)
    llm_api_batch_size = kwargs.pop("llm_api_batch_size", 20) \
        if isinstance(kwargs.get("llm_api_batch_size", 20), int) \
        and kwargs.get("llm_api_batch_size", 20) > 0 else 20
    # score_version -- propagated as input to get_generation_score method
    score_version = kwargs.pop("score_version", "v1")
    use_previous_conversation = kwargs.pop("use_previous_conversation", False)
    score_all_conversations = kwargs.pop("score_all_conversations", False)

    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    chat_completion_kwargs = ["metrics", "tokenizer", "smoothing",
                              "aggregator", "stemmer", "model_id", "batch_size",
                              "add_start_token", "openai_params", "openai_api_batch_size",
                              "use_chat_completion_api", "llm_params", "llm_api_batch_size",
                              "score_version", "use_previous_conversation", "score_all_conversations"]
    check_kwargs(kwargs, task_type, chat_completion_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLChatCompletionMetrics(
            metrics=metrics_list,
            tokenizer=tokenizer,
            smoothing=smoothing,
            aggregator=aggregator,
            stemmer=stemmer,
            use_static_script=use_static_script,
            model_id=model_id,
            batch_size=batch_size,
            add_start_token=add_start_token,
            openai_params=openai_params,
            openai_api_batch_size=openai_api_batch_size,
            use_chat_completion_api=use_chat_completion_api,
            llm_params=llm_params,
            llm_api_batch_size=llm_api_batch_size,
            score_version=score_version,
            use_previous_conversation=use_previous_conversation,
            score_all_conversations=score_all_conversations,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_rag_evaluation(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop("metrics", None)
    # propagated directly as input to setup_llm or init_llm methods
    # evaluation_llm = setup_llm(API_BASE, API_VERSION, MODEL_KEY, is_chat=True)
    openai_params = kwargs.pop("openai_params", None)
    openai_api_batch_size = kwargs.pop("openai_api_batch_size", 20) \
        if isinstance(kwargs.get("openai_api_batch_size", 20), int) \
        and kwargs.get("openai_api_batch_size", 20) > 0 else 20
    use_chat_completion_api = kwargs.pop("use_chat_completion_api", None)
    # kwargs for llama params
    llm_params = kwargs.pop("llm_params", None)
    llm_api_batch_size = kwargs.pop("llm_api_batch_size", 20) \
        if isinstance(kwargs.get("llm_api_batch_size", 20), int) \
        and kwargs.get("llm_api_batch_size", 20) > 0 else 20
    # score_version -- propagated as input to get_generation_score method
    score_version = kwargs.pop("score_version", "v1")
    use_previous_conversation = kwargs.pop("use_previous_conversation", False)

    # max number of threads to use for parallelizing the evaluation
    max_threads = kwargs.pop("max_threads", constants.ChatCompletionConstants.MAX_THREADS_PER_METRIC)
    constants.ChatCompletionConstants.MAX_THREADS_PER_METRIC = max_threads
    logger.info("Setting max_threads to {} for computing rag evaluation based metrics".format(
        constants.ChatCompletionConstants.MAX_THREADS_PER_METRIC))

    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    rag_evaluation_kwargs = ["metrics", "openai_params", "openai_api_batch_size", "use_chat_completion_api",
                             "llm_params", "llm_api_batch_size", "score_version", "use_previous_conversation",
                             "max_threads"]
    check_kwargs(kwargs, task_type, rag_evaluation_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLRagEvaluationMetrics(
            metrics=metrics_list,
            openai_params=openai_params,
            openai_api_batch_size=openai_api_batch_size,
            use_chat_completion_api=use_chat_completion_api,
            llm_params=llm_params,
            llm_api_batch_size=llm_api_batch_size,
            score_version=score_version,
            use_previous_conversation=use_previous_conversation,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_forecasting(task_type, y_test, y_pred, kwargs):
    # Parameters common with regression task
    metrics_list = kwargs.pop('metrics', None)
    sample_weight = kwargs.pop("sample_weight", None)
    X_train = kwargs.pop("X_train", None)
    y_train = kwargs.pop("y_train", None)
    y_std = kwargs.pop("y_std", None)
    # Forecasting-specific parameters
    time_series_id_column_names = kwargs.pop("time_series_id_column_names", None)
    aggregation_method = kwargs.pop("aggregation_method", np.mean)
    time_column_name = kwargs.pop("time_column_name", None)
    X_test = kwargs.pop("X_test", None)
    y_min_dict = kwargs.pop("y_min_dict", None)
    y_max_dict = kwargs.pop("y_max_dict", None)
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    forecasting_kwargs = ["metrics", "sample_weight",
                          "X_train", "X_test", "y_train", "y_std",
                          "time_series_id_column_names",
                          "aggregation_method", "time_column_name", "y_min_dict",
                          "y_max_dict"]
    check_kwargs(kwargs, task_type, forecasting_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLForecastingMetrics(
            metrics=metrics_list,
            sample_weight=sample_weight,
            X_train=X_train,
            y_train=y_train,
            y_std=y_std,
            time_series_id_column_names=time_series_id_column_names,
            time_column_name=time_column_name,
            aggregation_method=aggregation_method,
            custom_dimensions=custom_dimensions,
            y_min_dict=y_min_dict,
            y_max_dict=y_max_dict,
            log_activity=log_activity,
            log_traceback=log_traceback)
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred, X_test=X_test)
        return computed_metrics


def compute_metrics_image_od_is(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop("metrics", None)
    task_is_detection = task_type == constants.Tasks.IMAGE_OBJECT_DETECTION
    num_classes = kwargs.pop("num_classes", None)
    iou_threshold = kwargs.pop("iou_threshold", None)
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    if num_classes is None:
        raise MetricsException("The number of classes must be specified for {} tasks.".format(task_type))
    # Extract the additional image-related argument required for object detection / instance segmentation.
    image_meta_info = kwargs.pop("image_meta_info", None)
    if image_meta_info is None:
        raise MetricsException("The image meta information must be specified for {} tasks.".format(task_type))
    od_is_kwargs = ["metrics", "num_classes", "iou_threshold", "image_meta_info"]
    check_kwargs(kwargs, task_type, od_is_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLODISMetrics(
            task_is_detection=task_is_detection,
            num_classes=num_classes,
            iou_threshold=iou_threshold,
            metrics=metrics_list,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred, image_meta_info=image_meta_info)
        return computed_metrics


def compute_metrics_image_generation(task_type, y_test, y_pred, kwargs):
    _, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)

    with log_activity(
        logger=logger,
        activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
        activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
        custom_dimensions=custom_dimensions
    ):
        metrics = AzureMLImageGenerationMetrics(log_activity=log_activity, log_traceback=log_traceback)
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_code_generation(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop('metrics', None)
    # pass@k metric keyword arguments
    test_cases = kwargs.pop('test_cases', None)
    allow_code_eval = kwargs.pop('allow_code_eval', True)
    no_of_candidates = kwargs.pop('no_of_candidates', [1, 10, 100])
    num_workers = kwargs.pop('num_workers', 4)
    timeout = kwargs.pop('timeout', 3)
    dataset = kwargs.pop('dataset', None)

    # bleu keyword arguments
    tokenizer = kwargs.pop('tokenizer', None)
    smoothing = kwargs.pop('smoothing', False)
    # rouge keyword arguments
    aggregator = kwargs.pop('aggregator', True)
    stemmer = kwargs.pop('stemmer', False)

    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    code_evaluation_kwargs = ['metrics', 'allow_code_eval', 'no_of_candidates', 'num_workers'
                              'timeout', 'dataset', 'tokenizer', 'smoothing', 'aggregator', 'stemmer']
    check_kwargs(kwargs, task_type, code_evaluation_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMLCodeGenerationMetrics(
            metrics=metrics_list,
            test_cases=test_cases,
            allow_code_eval=allow_code_eval,
            no_of_candidates=no_of_candidates,
            num_workers=num_workers,
            timeout=timeout,
            dataset=dataset,
            tokenizer=tokenizer,
            smoothing=smoothing,
            aggregator=aggregator,
            stemmer=stemmer,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
        return computed_metrics


def compute_metrics_video_mot(task_type, y_test, y_pred, kwargs):
    metrics_list = kwargs.pop("metrics", None)
    num_classes = kwargs.pop("num_classes", None)
    iou_threshold = kwargs.pop("iou_threshold", None)
    common_args, custom_dimensions, log_activity, log_traceback = extract_common_kwargs(kwargs, task_type=task_type)
    if num_classes is None:
        raise InvalidValueException("The number of classes must be specified for {} tasks.".format(task_type))
    # Extract the additional image-related argument required for object detection / instance segmentation.
    image_meta_info = kwargs.pop("image_meta_info", None)
    if image_meta_info is None:
        raise InvalidValueException("The image meta information must be specified for {} tasks.".format(task_type))
    mot_kwargs = ["metrics", "num_classes", "iou_threshold", "image_meta_info"]
    check_kwargs(kwargs, task_type, mot_kwargs)
    with log_activity(logger=logger,
                      activity_type=constants.TelemetryConstants.COMPUTE_METRICS_NAME,
                      activity_name=constants.TelemetryConstants.COMPUTE_METRICS_TASK_SUFFIX.format(task_type),
                      custom_dimensions=custom_dimensions):
        metrics = AzureMlMOTODMetrics(
            num_classes=num_classes,
            iou_threshold=iou_threshold,
            metrics=metrics_list,
            log_activity=log_activity,
            log_traceback=log_traceback,
            custom_dimensions=custom_dimensions,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred, image_meta_info=image_meta_info)
        return computed_metrics


def get_supported_metrics(task_type):
    task_options = {
        constants.Tasks.CLASSIFICATION: AzureMLClassificationMetrics,
        constants.Tasks.REGRESSION: AzureMLRegressionMetrics,
        constants.Tasks.TEXT_CLASSIFICATION: AzureMLClassificationMetrics,
        constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL: AzureMLClassificationMetrics,
        constants.Tasks.TEXT_NER: AzureMLTextNERMetrics,
        constants.Tasks.TRANSLATION: AzureMLTranslationMetrics,
        constants.Tasks.SUMMARIZATION: AzureMLSummarizationMetrics,
        constants.Tasks.QUESTION_ANSWERING: AzureMLQAMetrics,
        constants.Tasks.QUESTION_ANSWERING_MULTIPLE_GROUND_TRUTH: AzureMLQAMetrics,
        constants.Tasks.FILL_MASK: AzureMLFillMaskMetrics,
        constants.Tasks.TEXT_GENERATION: AzureMLTextGenerationMetrics,
        constants.Tasks.CHAT_COMPLETION: AzureMLChatCompletionMetrics,
        constants.Tasks.RAG_EVALUATION: AzureMLRagEvaluationMetrics,
        constants.Tasks.CODE_GENERATION: AzureMLCodeGenerationMetrics,
        constants.Tasks.IMAGE_OBJECT_DETECTION: AzureMLODMetrics,
        constants.Tasks.IMAGE_INSTANCE_SEGMENTATION: AzureMLISMetrics,
        constants.Tasks.FORECASTING: AzureMLForecastingMetrics,
        constants.Tasks.IMAGE_CLASSIFICATION: AzureMLClassificationMetrics,
        constants.Tasks.IMAGE_CLASSIFICATION_MULTILABEL: AzureMLClassificationMetrics,
        constants.Tasks.IMAGE_MULTI_LABEL_CLASSIFICATION: AzureMLClassificationMetrics,
        constants.Tasks.VIDEO_MULTI_OBJECT_TRACKING: AzureMlMOTODMetrics,
    }
    if task_type is None:
        result = task_options
    else:
        result = task_options.get(task_type, None)
    return result


def get_supported_prompts(task_type):
    """
    Returns the metrics class corresponding to the given task type.

    Parameters:
    task_type (str): The type of task for which the metrics class is required.

    Returns:
    class: The metrics class corresponding to the given task type, or None if the task type is not supported.
    """
    task_options = {
        constants.Tasks.QUESTION_ANSWERING: AzureMLQAMetrics,
        constants.Tasks.CHAT_COMPLETION: AzureMLRagEvaluationMetrics,
        constants.Tasks.RAG_EVALUATION: AzureMLRagEvaluationMetrics,
    }
    result = task_options.get(task_type, None)
    return result

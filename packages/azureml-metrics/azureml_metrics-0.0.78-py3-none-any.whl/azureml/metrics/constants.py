# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Metrics constants."""
import sys
from enum import Enum

import numpy as np

import pkg_resources


class TrainingResultsType:
    """Defines potential results from runners class."""

    # Metrics
    TRAIN_METRICS = "train"
    VALIDATION_METRICS = "validation"
    TEST_METRICS = "test"
    TRAIN_FROM_FULL_METRICS = "train from full"
    TEST_FROM_FULL_METRICS = "test from full"
    CV_METRICS = "CV"
    CV_MEAN_METRICS = "CV mean"

    # Other useful things
    TRAIN_TIME = "train time"
    FIT_TIME = "fit_time"
    PREDICT_TIME = "predict_time"
    BLOB_TIME = "blob_time"
    ALL_TIME = {TRAIN_TIME, FIT_TIME, PREDICT_TIME}
    TRAIN_PERCENT = "train_percent"
    MODELS = "models"

    # Status:
    TRAIN_VALIDATE_STATUS = "train validate status"
    TRAIN_FULL_STATUS = "train full status"
    CV_STATUS = "CV status"


class MetricExtrasConstants:
    """Define internal values of Confidence Intervals."""

    UPPER_95_PERCENTILE = "upper_ci_95"
    LOWER_95_PERCENTILE = "lower_ci_95"
    VALUE = "value"

    # Confidence Interval metric metric_name format
    MetricExtrasSuffix = "_extras"
    MetricExtrasFormat = "{}" + MetricExtrasSuffix

    # Aggregation logic extra suffix
    MeanExtrasPrefix = "mean_"
    MeanExtrasFormat = MeanExtrasPrefix + "{}"
    MeanExtrasDictFormat = MeanExtrasPrefix + "{}_{}"

    MedianExtrasPrefix = "median_"
    MedianExtrasFormat = MedianExtrasPrefix + "{}"

    # Custom prompt metric metric_name suffix
    CustomPromptMetricSuffix = "{}" + "_custom_prompt_metric"


class RetryConstants:
    """Define constants to be used in retry logic."""

    MAX_ATTEMPTS = 3
    DELAY_TIME = 10


class Metric:
    """Defines all metrics supported by classification and regression."""

    # Scalar & non scalar segregation key constants
    Metrics = "metrics"  # Scalar
    Artifacts = "artifacts"  # Non-Scalar

    # Classification
    AUCBinary = "AUC_binary"
    AUCMacro = "AUC_macro"
    AUCMicro = "AUC_micro"
    AUCWeighted = "AUC_weighted"
    Accuracy = "accuracy"
    WeightedAccuracy = "weighted_accuracy"
    BalancedAccuracy = "balanced_accuracy"
    NormMacroRecall = "norm_macro_recall"
    LogLoss = "log_loss"
    F1Binary = "f1_score_binary"
    F1Micro = "f1_score_micro"
    F1Macro = "f1_score_macro"
    F1Weighted = "f1_score_weighted"
    PrecisionBinary = "precision_score_binary"
    PrecisionMicro = "precision_score_micro"
    PrecisionMacro = "precision_score_macro"
    PrecisionWeighted = "precision_score_weighted"
    RecallBinary = "recall_score_binary"
    RecallMicro = "recall_score_micro"
    RecallMacro = "recall_score_macro"
    RecallWeighted = "recall_score_weighted"
    AvgPrecisionBinary = "average_precision_score_binary"
    AvgPrecisionMicro = "average_precision_score_micro"
    AvgPrecisionMacro = "average_precision_score_macro"
    AvgPrecisionWeighted = "average_precision_score_weighted"
    AccuracyTable = "accuracy_table"
    ConfusionMatrix = "confusion_matrix"
    MatthewsCorrelation = "matthews_correlation"
    ClassificationReport = "classification_report"

    # Multilabel classification
    IOU = "iou"
    IOUMicro = "iou_micro"
    IOUMacro = "iou_macro"
    IOUWeighted = "iou_weighted"

    # classwise metrics
    PrecisionClasswise = "precision_score_classwise"
    RecallClasswise = "recall_score_classwise"
    F1Classwise = "f1_score_classwise"
    AUCClasswise = "AUC_classwise"
    AvgPrecisionClasswise = "average_precision_score_classwise"
    IOUClasswise = "iou_classwise"

    # Regression
    ExplainedVariance = "explained_variance"
    R2Score = "r2_score"
    Spearman = "spearman_correlation"
    MAPE = "mean_absolute_percentage_error"
    SMAPE = "symmetric_mean_absolute_percentage_error"
    MeanAbsError = "mean_absolute_error"
    MedianAbsError = "median_absolute_error"
    RMSE = "root_mean_squared_error"
    RMSLE = "root_mean_squared_log_error"
    NormMeanAbsError = "normalized_mean_absolute_error"
    NormMedianAbsError = "normalized_median_absolute_error"
    NormRMSE = "normalized_root_mean_squared_error"
    NormRMSLE = "normalized_root_mean_squared_log_error"
    Residuals = "residuals"
    PredictedTrue = "predicted_true"

    # Forecast
    ForecastMAPE = "forecast_mean_absolute_percentage_error"
    ForecastSMAPE = "forecast_symmetric_mean_absolute_percentage_error"
    ForecastResiduals = "forecast_residuals"
    ForecastTable = "forecast_table"
    ForecastTsIDDistributionTable = "forecast_time_series_id_distribution_table"

    # Sequence to Sequence Metrics
    # Seq2Seq Translation
    TranslationBleu_1 = "bleu_1"
    TranslationBleu_2 = "bleu_2"
    TranslationBleu_3 = "bleu_3"
    TranslationBleu_4 = "bleu_4"

    # Seq2Seq Summarization
    SummarizationRouge1 = "rouge1"
    SummarizationRouge2 = "rouge2"
    SummarizationRougeL = "rougeL"
    SummarizationRougeLsum = "rougeLsum"

    # QA
    QAExactMatch = "exact_match"
    QAF1Score = "f1_score"
    # QA multiple ground truth
    QAMacroAveragedF1 = "macro_averaged_f1"
    QAMacroAveragedExactMatch = "macro_averaged_exact_match"

    # Text Similarity metrics for Question Answering
    AdaSimilarity = "ada_similarity"
    BERTScore = "bertscore"
    GPTSimilarity = "gpt_similarity"
    GPTCoherence = "gpt_coherence"
    GPTRelevance = "gpt_relevance"
    GPTGroundedness = "gpt_groundedness"
    GPTFluency = "gpt_fluency"
    # LLM based metrics for Question Answering
    LLMSimilarity = "llm_similarity"
    LLMCoherence = "llm_coherence"
    LLMRelevance = "llm_relevance"
    LLMGroundedness = "llm_groundedness"
    LLMFluency = "llm_fluency"

    # RAG Evaluation metrics
    RAG_GPTGroundedness = "gpt_groundedness"
    RAG_GPTRelevance = "gpt_relevance"
    RAG_GPTRetrieval = "gpt_retrieval_score"

    # Chat Completion metrics
    ConversationGroundingScore = "conversation_groundedness_score"

    # Code Generation metrics
    CodeGenerationPassRateScore = "code_eval"  # Pass@k

    # Fill Masking Metrics
    FMPerplexity = "perplexity"

    # Image object detection and instance segmentation
    MEAN_AVERAGE_PRECISION = "mean_average_precision"
    AVERAGE_PRECISION = "average_precision"
    PRECISION = "precision"
    RECALL = "recall"
    PER_LABEL_METRICS = "per_label_metrics"
    IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS = "image_level_binary_classsifier_metrics"
    CONFUSION_MATRICES_PER_SCORE_THRESHOLD = "confusion_matrices_per_score_threshold"

    # Image generation
    FID = "fid"

    # Video object tracking
    IDF1 = "IDF1"
    MOTA = "MOTA"
    MOTP = "MOTP"
    IDSW = "IDSw"
    FP = "FP"  # False Positive
    FN = "FN"  # False Negative
    FM = "FM"  # False Match
    ML = "ML"  # Mostly Lost
    MT = "MT"  # Mostly Tracked
    PT = "PT"  # Partially Tracked
    TRACKING_PRECISION = "Tracking_Precision"
    TRACKING_RECALL = "Tracking_Recall"

    SCALAR_CLASSIFICATION_SET = {
        AUCBinary,
        AUCMacro,
        AUCMicro,
        AUCWeighted,
        Accuracy,
        WeightedAccuracy,
        NormMacroRecall,
        BalancedAccuracy,
        LogLoss,
        F1Binary,
        F1Micro,
        F1Macro,
        F1Weighted,
        PrecisionBinary,
        PrecisionMicro,
        PrecisionMacro,
        PrecisionWeighted,
        RecallBinary,
        RecallMicro,
        RecallMacro,
        RecallWeighted,
        AvgPrecisionBinary,
        AvgPrecisionMicro,
        AvgPrecisionMacro,
        AvgPrecisionWeighted,
        MatthewsCorrelation,
    }

    IOU_CLASSIFICATION_SET_MULTILABEL = {
        IOU,
        IOUMacro,
        IOUMicro,
        IOUWeighted,
    }

    SCALAR_CLASSIFICATION_BINARY_SET = {
        AUCBinary,
        F1Binary,
        PrecisionBinary,
        RecallBinary,
        AvgPrecisionBinary,
    }

    SCALAR_CLASSIFICATION_SET_MULTILABEL = {
        AUCMacro,
        AUCMicro,
        AUCWeighted,
        Accuracy,
        NormMacroRecall,
        BalancedAccuracy,
        LogLoss,
        F1Micro,
        F1Macro,
        F1Weighted,
        PrecisionMicro,
        PrecisionMacro,
        PrecisionWeighted,
        RecallMicro,
        RecallMacro,
        RecallWeighted,
        AvgPrecisionMicro,
        AvgPrecisionMacro,
        AvgPrecisionWeighted,
    }

    CLASSIFICATION_PROB_REQUIRED_SET = {
        AUCBinary,
        AUCMacro,
        AUCMicro,
        AUCWeighted,
        AvgPrecisionBinary,
        AvgPrecisionMacro,
        AvgPrecisionMicro,
        AvgPrecisionWeighted,
        LogLoss,
        AccuracyTable,
        NormMacroRecall,
    }

    NONSCALAR_CLASSIFICATION_SET = {
        AccuracyTable,
        ConfusionMatrix,
        ClassificationReport,
    }

    NONSCALAR_CLASSIFICATION_SET_MULTILABEL = {AccuracyTable, ConfusionMatrix}

    CLASSIFICATION_BINARY_SET = {
        AUCBinary,
        F1Binary,
        PrecisionBinary,
        RecallBinary,
        AvgPrecisionBinary,
    }

    CLASSIFICATION_CLASSWISE_SET = {
        PrecisionClasswise,
        RecallClasswise,
        F1Classwise,
        IOUClasswise,
        AvgPrecisionClasswise,
        AUCClasswise,
    }

    CLASSIFICATION_SET = (
        SCALAR_CLASSIFICATION_SET
        | NONSCALAR_CLASSIFICATION_SET
        | CLASSIFICATION_CLASSWISE_SET
        | IOU_CLASSIFICATION_SET_MULTILABEL
    )
    # classification set for the azuremlclassification file
    CLASSIFICATION_SET_AZURE = (
        SCALAR_CLASSIFICATION_SET | NONSCALAR_CLASSIFICATION_SET_MULTILABEL
    )

    CLASSIFICATION_SET_MULTILABEL = (
        SCALAR_CLASSIFICATION_SET_MULTILABEL
        | NONSCALAR_CLASSIFICATION_SET_MULTILABEL
        | IOU_CLASSIFICATION_SET_MULTILABEL
        | SCALAR_CLASSIFICATION_BINARY_SET
    )

    CLASSIFICATION_PRIMARY_SET = {
        Accuracy,
        AUCWeighted,
        NormMacroRecall,
        AvgPrecisionWeighted,
        PrecisionWeighted,
    }

    CLASSIFICATION_BALANCED_SET = {
        # this is for metrics where we would recommend using class_weights
        BalancedAccuracy,
        AUCMacro,
        NormMacroRecall,
        AvgPrecisionMacro,
        PrecisionMacro,
        F1Macro,
        RecallMacro,
    }

    UNSUPPORTED_CLASSIFICATION_TABULAR_SET = (
        CLASSIFICATION_CLASSWISE_SET
        | IOU_CLASSIFICATION_SET_MULTILABEL
        | {ClassificationReport}
    )

    TEXT_CLASSIFICATION_SET = {
        Accuracy,
        AUCWeighted,
        PrecisionMicro,
        PrecisionWeighted,
    }

    TEXT_CLASSIFICATION_MULTILABEL_SET = {
        Accuracy,
        F1Macro,
        F1Micro,
    }

    SCALAR_REGRESSION_SET = {
        ExplainedVariance,
        R2Score,
        Spearman,
        MAPE,
        MeanAbsError,
        MedianAbsError,
        RMSE,
        RMSLE,
        NormMeanAbsError,
        NormMedianAbsError,
        NormRMSE,
        NormRMSLE,
    }

    NONSCALAR_REGRESSION_SET = {Residuals, PredictedTrue}

    REGRESSION_SET = SCALAR_REGRESSION_SET | NONSCALAR_REGRESSION_SET

    REGRESSION_NORMALIZED_SET = {
        NormMeanAbsError,
        NormMedianAbsError,
        NormRMSE,
        NormRMSLE,
    }

    REGRESSION_PRIMARY_SET = {Spearman, NormRMSE, R2Score, NormMeanAbsError}

    IMAGE_CLASSIFICATION_PRIMARY_SET = {Accuracy}

    IMAGE_CLASSIFICATION_MULTILABEL_PRIMARY_SET = {IOU}

    IMAGE_OBJECT_DETECTION_PRIMARY_SET = {MEAN_AVERAGE_PRECISION}

    SCALAR_IMAGE_OBJECT_DETECTION_SET = {MEAN_AVERAGE_PRECISION, RECALL, PRECISION}
    NONSCALAR_IMAGE_OBJECT_DETECTION_SET = {
        IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS,
        CONFUSION_MATRICES_PER_SCORE_THRESHOLD,
        PER_LABEL_METRICS,
    }

    IMAGE_OBJECT_DETECTION_SET = (
        SCALAR_IMAGE_OBJECT_DETECTION_SET | NONSCALAR_IMAGE_OBJECT_DETECTION_SET
    )
    IMAGE_OBJECT_DETECTION_CLASSWISE_SET = {PER_LABEL_METRICS}

    SCALAR_IMAGE_INSTANCE_SEGMENTATION_SET = {MEAN_AVERAGE_PRECISION, RECALL, PRECISION}
    IMAGE_INSTANCE_SEGMENTATION_CLASSWISE_SET = {PER_LABEL_METRICS}

    IMAGE_INSTANCE_SEGMENTATION_SET = (
        SCALAR_IMAGE_INSTANCE_SEGMENTATION_SET
        | IMAGE_INSTANCE_SEGMENTATION_CLASSWISE_SET
    )

    SCALAR_IMAGE_GENERATION_SET = {FID}
    NONSCALAR_IMAGE_GENERATION_SET = set()

    IMAGE_GENERATION_SET = (
        SCALAR_IMAGE_GENERATION_SET | NONSCALAR_IMAGE_GENERATION_SET
    )

    SCALAR_VIDEO_MULTI_OBJECT_TRACKING_SET = {
        MOTA,
        MOTP,
        IDF1,
        PRECISION,
        RECALL,
        TRACKING_PRECISION,
        TRACKING_RECALL,
        IDSW,
        FP,
        FN,
        FM,
        ML,
        MT,
        PT,
    }

    NONSCALAR_VIDEO_MULTI_OBJECT_TRACKING_SET = set()

    VIDEO_MULTI_OBJECT_TRACKING_SET = (
        SCALAR_VIDEO_MULTI_OBJECT_TRACKING_SET
        | NONSCALAR_VIDEO_MULTI_OBJECT_TRACKING_SET
    )

    SAMPLE_WEIGHTS_UNSUPPORTED_SET = {
        WeightedAccuracy,
        Spearman,
        MedianAbsError,
        NormMedianAbsError,
    }

    TEXT_CLASSIFICATION_PRIMARY_SET = {Accuracy, AUCWeighted, PrecisionWeighted}

    TEXT_CLASSIFICATION_MULTILABEL_PRIMARY_SET = {Accuracy}

    TEXT_NER_PRIMARY_SET = {Accuracy}

    NER_SET = {
        Accuracy,
        F1Macro,
        F1Micro,
        F1Weighted,
        PrecisionMicro,
        PrecisionMacro,
        PrecisionWeighted,
        RecallMicro,
        RecallMacro,
        RecallWeighted,
    }

    NONSCALAR_FORECAST_SET = {
        ForecastMAPE,
        ForecastResiduals,
        ForecastTable,
        ForecastTsIDDistributionTable,
    }

    FORECAST_SET = NONSCALAR_FORECAST_SET

    # The set of non scalar metrics allowed even if the
    # training set was not provided.
    FORECASTING_NONSCALAR_SET_NO_TRAINING = {ForecastTsIDDistributionTable}

    # Metrics set for Sequence to Sequence Tasks
    SCALAR_TRANSLATION_SET = {
        TranslationBleu_1,
        TranslationBleu_2,
        TranslationBleu_3,
        TranslationBleu_4,
    }

    TRANSLATION_SET = SCALAR_TRANSLATION_SET

    TRANSLATION_NGRAM_MAP = {
        TranslationBleu_1: 1,
        TranslationBleu_2: 2,
        TranslationBleu_3: 3,
        TranslationBleu_4: 4,
    }

    SCALAR_SUMMARIZATION_SET = {
        SummarizationRouge1,
        SummarizationRouge2,
        SummarizationRougeL,
        SummarizationRougeLsum,
    }

    SUMMARIZATION_SET = SCALAR_SUMMARIZATION_SET

    SCALAR_QA_SET = set()

    NONSCALAR_QA_SET = {
        QAExactMatch,
        QAF1Score,
        BERTScore,
        AdaSimilarity,
        GPTSimilarity,
        GPTCoherence,
        GPTGroundedness,
        GPTFluency,
        GPTRelevance,
        LLMSimilarity,
        LLMCoherence,
        LLMGroundedness,
        LLMFluency,
        LLMRelevance,
    }

    SCALAR_CODE_GENERATION_SET = {CodeGenerationPassRateScore}

    QA_SET = SCALAR_QA_SET | NONSCALAR_QA_SET

    # QA metrics that don't need groundtruths.
    QA_SPECIAL_SET = {
        GPTCoherence,
        GPTGroundedness,
        GPTFluency,
        GPTRelevance,
        LLMCoherence,
        LLMGroundedness,
        LLMFluency,
        LLMRelevance,
    }

    QA_GPT_METRICS_SET = {
        GPTCoherence,
        GPTGroundedness,
        GPTFluency,
        GPTRelevance,
        GPTSimilarity,
        AdaSimilarity,
    }

    QA_GPT_STAR_METRICS_SET = {
        GPTCoherence,
        GPTGroundedness,
        GPTFluency,
        GPTRelevance,
        GPTSimilarity,
    }
    QA_LLM_METRICS_SET = {
        LLMCoherence,
        LLMGroundedness,
        LLMFluency,
        LLMRelevance,
        LLMSimilarity,
    }

    # QA metrics with multiple ground truths
    SCALAR_QA_MULTIPLE_GROUND_TRUTH_SET = {QAMacroAveragedF1, QAMacroAveragedExactMatch}
    NON_SCALAR_QA_MULTIPLE_GROUND_TRUTH_SET = set()
    QA_MULTIPLE_GROUND_TRUTH_SET = (
        SCALAR_QA_MULTIPLE_GROUND_TRUTH_SET | NON_SCALAR_QA_MULTIPLE_GROUND_TRUTH_SET
        | QA_GPT_STAR_METRICS_SET | QA_LLM_METRICS_SET
    )

    # Fill Masking Metrics
    SCALAR_FILL_MASK_SET = set()
    NONSCALAR_FILL_MASK_SET = {FMPerplexity}

    # Fill Masking metrics that do not need groundtruths
    FILL_MASK_SPECIAL_SET = {FMPerplexity}

    FILL_MASK_SET = SCALAR_FILL_MASK_SET | NONSCALAR_FILL_MASK_SET

    # Text generation metrics
    SCALAR_TEXT_GENERATION_SET = SCALAR_SUMMARIZATION_SET | SCALAR_TRANSLATION_SET
    NONSCALAR_TEXT_GENERATION_SET = NONSCALAR_FILL_MASK_SET
    TEXT_GENERATION_SET = SCALAR_TEXT_GENERATION_SET | NONSCALAR_TEXT_GENERATION_SET

    # Code Generation Metrics
    CODE_GENERATION_SET = SCALAR_CODE_GENERATION_SET | SCALAR_TEXT_GENERATION_SET
    CODE_GENERATION_SPECIAL_SET = {CodeGenerationPassRateScore}

    # RAG evaluation metrics
    NONSCALAR_RAG_EVALUATION_SET = {
        RAG_GPTGroundedness,
        RAG_GPTRelevance,
        RAG_GPTRetrieval,
    }
    RAG_EVALUATION_SET = NONSCALAR_RAG_EVALUATION_SET

    # Chat completion metrics
    CONVERSATION_RAI_SET = {ConversationGroundingScore}
    # TODO: Enable F1 Score and Exact Match metrics for chat completion
    SCALAR_CHAT_COMPLETION_SET = SCALAR_TEXT_GENERATION_SET
    NONSCALAR_CHAT_COMPLETION_SET = (
        NONSCALAR_FILL_MASK_SET | CONVERSATION_RAI_SET | NONSCALAR_RAG_EVALUATION_SET
    )
    CHAT_COMPLETION_SET = NONSCALAR_CHAT_COMPLETION_SET | SCALAR_CHAT_COMPLETION_SET
    CHAT_COMPLETION_NONGPT_SET = SCALAR_CHAT_COMPLETION_SET | NONSCALAR_FILL_MASK_SET
    # Chat Completion metrics that doesn't need ground-truths
    CHAT_COMPLETION_SPECIAL_SET = {FMPerplexity, ConversationGroundingScore}

    SCALAR_SEQ2SEQ_SET = (
        SCALAR_TRANSLATION_SET
        | SCALAR_SUMMARIZATION_SET
        | SCALAR_QA_SET
        | SCALAR_FILL_MASK_SET
        | SCALAR_TEXT_GENERATION_SET
        | SCALAR_CHAT_COMPLETION_SET
    )

    FULL_SET = CLASSIFICATION_SET | REGRESSION_SET | IMAGE_OBJECT_DETECTION_SET
    NONSCALAR_FULL_SET = (
        NONSCALAR_CLASSIFICATION_SET
        | NONSCALAR_REGRESSION_SET
        | NONSCALAR_QA_SET
        | NONSCALAR_RAG_EVALUATION_SET
        | NONSCALAR_TEXT_GENERATION_SET
        | NONSCALAR_CHAT_COMPLETION_SET
    )
    SCALAR_FULL_SET = (
        SCALAR_CLASSIFICATION_SET
        | SCALAR_REGRESSION_SET
        | SCALAR_QA_MULTIPLE_GROUND_TRUTH_SET
        | SCALAR_SEQ2SEQ_SET
    )

    SCALAR_FULL_SET_TIME = SCALAR_FULL_SET | TrainingResultsType.ALL_TIME

    # Metrics that need to be aggregated
    NON_AGGREGATED_METRICS = (
        {FMPerplexity, BERTScore, QAExactMatch, QAF1Score}
        | QA_GPT_METRICS_SET
        | QA_LLM_METRICS_SET
        | SCALAR_TEXT_GENERATION_SET
    )


class Tasks:
    """Defines types of machine learning tasks supported by automated ML."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    FORECASTING = "forecasting"

    # Sequence to Sequence Tasks
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    DEFAULT = "default"
    QUESTION_ANSWERING = "qa"
    QUESTION_ANSWERING_MULTIPLE_GROUND_TRUTH = "qa_multiple_ground_truth"
    FILL_MASK = "fill-mask"
    TEXT_GENERATION = "text-generation"

    # Chat Completion task type
    CHAT_COMPLETION = "chat-completion"

    # RAG Evaluation task type
    RAG_EVALUATION = "rag-evaluation"

    # Code Generation
    CODE_GENERATION = "code-generation"

    IMAGE_CLASSIFICATION = "image-classification"
    IMAGE_CLASSIFICATION_MULTILABEL = "image-classification-multilabel"
    IMAGE_MULTI_LABEL_CLASSIFICATION = (
        "image-multi-labeling"  # for temporary backward-compatibility
    )
    IMAGE_OBJECT_DETECTION = "image-object-detection"
    IMAGE_INSTANCE_SEGMENTATION = "image-instance-segmentation"
    _ALL_IMAGE_CLASSIFICATION = [
        IMAGE_CLASSIFICATION,
        IMAGE_CLASSIFICATION_MULTILABEL,
        IMAGE_MULTI_LABEL_CLASSIFICATION,
    ]
    # Custom prompt metric
    CUSTOM_PROMPT_METRIC = "custom-prompt-metric"

    IMAGE_CLASSIFICATION = 'image-classification'
    IMAGE_CLASSIFICATION_MULTILABEL = 'image-classification-multilabel'
    IMAGE_MULTI_LABEL_CLASSIFICATION = 'image-multi-labeling'  # for temporary backward-compatibility
    IMAGE_OBJECT_DETECTION = 'image-object-detection'
    IMAGE_INSTANCE_SEGMENTATION = 'image-instance-segmentation'
    IMAGE_GENERATION = "image-generation"
    _ALL_IMAGE_CLASSIFICATION = [IMAGE_CLASSIFICATION, IMAGE_CLASSIFICATION_MULTILABEL,
                                 IMAGE_MULTI_LABEL_CLASSIFICATION]

    _ALL_IMAGE_OBJECT_DETECTION = [IMAGE_OBJECT_DETECTION, IMAGE_INSTANCE_SEGMENTATION]
    _ALL_IMAGE = [
        IMAGE_CLASSIFICATION,
        IMAGE_CLASSIFICATION_MULTILABEL,
        IMAGE_MULTI_LABEL_CLASSIFICATION,
        IMAGE_OBJECT_DETECTION,
        IMAGE_INSTANCE_SEGMENTATION,
        IMAGE_GENERATION,
    ]
    VIDEO_MULTI_OBJECT_TRACKING = "video-multi-object-tracking"

    TEXT_CLASSIFICATION = "text-classification"
    TEXT_CLASSIFICATION_MULTILABEL = "text-classification-multilabel"
    TEXT_NER = "text-ner"

    _ALL_CLASSIFICATION_TASKS = [
        CLASSIFICATION,
        TEXT_CLASSIFICATION,
        TEXT_CLASSIFICATION_MULTILABEL,
        IMAGE_CLASSIFICATION,
        IMAGE_CLASSIFICATION_MULTILABEL,
        IMAGE_MULTI_LABEL_CLASSIFICATION,
    ]

    _ALL_TEXT = [TEXT_CLASSIFICATION, TEXT_CLASSIFICATION_MULTILABEL, TEXT_NER]
    _ALL_DNN = _ALL_IMAGE + _ALL_TEXT
    _ALL = _ALL_IMAGE + _ALL_TEXT


class ImageTask(Enum):
    """Available Image task types."""

    IMAGE_CLASSIFICATION = Tasks.IMAGE_CLASSIFICATION
    IMAGE_CLASSIFICATION_MULTILABEL = Tasks.IMAGE_CLASSIFICATION_MULTILABEL
    IMAGE_OBJECT_DETECTION = Tasks.IMAGE_OBJECT_DETECTION
    IMAGE_INSTANCE_SEGMENTATION = Tasks.IMAGE_INSTANCE_SEGMENTATION
    IMAGE_GENERATION = Tasks.IMAGE_GENERATION
    VIDEO_MULTI_OBJECT_TRACKING = Tasks.VIDEO_MULTI_OBJECT_TRACKING


class SubTaskType:
    """Available Sub-task types of Main tasks."""

    TEXT_GENERATION_SUBTASK_CODE = "code"


# All tasks
TASK_TYPES = {
    # Tabular task types
    Tasks.CLASSIFICATION,
    Tasks.REGRESSION,
    Tasks.FORECASTING,
    # Image/vision task types
    Tasks.IMAGE_CLASSIFICATION,
    Tasks.IMAGE_CLASSIFICATION_MULTILABEL,
    Tasks.IMAGE_MULTI_LABEL_CLASSIFICATION,
    Tasks.IMAGE_OBJECT_DETECTION,
    Tasks.IMAGE_INSTANCE_SEGMENTATION,
    Tasks.IMAGE_GENERATION,
    # Text task types
    Tasks.TEXT_CLASSIFICATION,
    Tasks.TEXT_CLASSIFICATION_MULTILABEL,
    Tasks.TEXT_NER,
    Tasks.TRANSLATION,
    Tasks.SUMMARIZATION,
    Tasks.QUESTION_ANSWERING,
    Tasks.QUESTION_ANSWERING_MULTIPLE_GROUND_TRUTH,
    Tasks.FILL_MASK,
    Tasks.TEXT_GENERATION,
    Tasks.CHAT_COMPLETION,
    Tasks.RAG_EVALUATION,
    Tasks.CODE_GENERATION,
    Tasks.CUSTOM_PROMPT_METRIC,
}

# All Metrics
FULL_SET = (
    Metric.CLASSIFICATION_SET
    | Metric.REGRESSION_SET
    | Metric.IMAGE_OBJECT_DETECTION_SET
    | Metric.IMAGE_INSTANCE_SEGMENTATION_SET
    | Metric.FORECAST_SET
    | Metric.TRANSLATION_SET
    | Metric.SUMMARIZATION_SET
    | Metric.QA_SET
    | Metric.FILL_MASK_SET
    | Metric.TEXT_GENERATION_SET
    | Metric.CHAT_COMPLETION_SET
    | Metric.RAG_EVALUATION_SET
    | Metric.CODE_GENERATION_SET
)

FULL_CLASSWISE_SET = (
    Metric.CLASSIFICATION_CLASSWISE_SET
    | Metric.IMAGE_OBJECT_DETECTION_CLASSWISE_SET
    | Metric.IMAGE_INSTANCE_SEGMENTATION_CLASSWISE_SET
)

FULL_NONSCALAR_SET = (
    Metric.NONSCALAR_CLASSIFICATION_SET
    | Metric.NONSCALAR_REGRESSION_SET
    | Metric.NONSCALAR_FILL_MASK_SET
    | Metric.NONSCALAR_FORECAST_SET
    | Metric.NONSCALAR_IMAGE_OBJECT_DETECTION_SET
    | Metric.NONSCALAR_IMAGE_GENERATION_SET
    | Metric.NONSCALAR_VIDEO_MULTI_OBJECT_TRACKING_SET
    | Metric.NONSCALAR_QA_SET
    | Metric.NONSCALAR_RAG_EVALUATION_SET
    | Metric.CONVERSATION_RAI_SET
)

FULL_SCALAR_SET = (
    Metric.SCALAR_CLASSIFICATION_SET
    | Metric.SCALAR_REGRESSION_SET
    | Metric.SCALAR_QA_SET
    | Metric.SCALAR_QA_MULTIPLE_GROUND_TRUTH_SET
    | Metric.SCALAR_CODE_GENERATION_SET
    | Metric.SCALAR_IMAGE_OBJECT_DETECTION_SET
    | Metric.SCALAR_IMAGE_GENERATION_SET
    | Metric.SCALAR_IMAGE_INSTANCE_SEGMENTATION_SET
    | Metric.SCALAR_VIDEO_MULTI_OBJECT_TRACKING_SET
    | Metric.SCALAR_SEQ2SEQ_SET  # TODO: has repeat values
    | Metric.IOU_CLASSIFICATION_SET_MULTILABEL
)

METRICS_TASK_MAP = {
    Tasks.CLASSIFICATION: Metric.CLASSIFICATION_SET,
    Tasks.REGRESSION: Metric.REGRESSION_SET,
    Tasks.FORECASTING: Metric.FORECAST_SET,
    Tasks.IMAGE_CLASSIFICATION: Metric.IMAGE_CLASSIFICATION_PRIMARY_SET,
    # why are 2 tasks mapping to the same metric functions - for backward compatibility @vision,
    Tasks.IMAGE_CLASSIFICATION_MULTILABEL: Metric.IMAGE_CLASSIFICATION_MULTILABEL_PRIMARY_SET,
    Tasks.IMAGE_MULTI_LABEL_CLASSIFICATION: Metric.IMAGE_CLASSIFICATION_MULTILABEL_PRIMARY_SET,
    Tasks.IMAGE_OBJECT_DETECTION: Metric.IMAGE_OBJECT_DETECTION_SET,
    Tasks.IMAGE_INSTANCE_SEGMENTATION: Metric.IMAGE_INSTANCE_SEGMENTATION_SET,
    Tasks.IMAGE_GENERATION: Metric.IMAGE_GENERATION_SET,
    Tasks.TEXT_CLASSIFICATION: Metric.TEXT_CLASSIFICATION_SET,
    Tasks.TEXT_CLASSIFICATION_MULTILABEL: Metric.TEXT_CLASSIFICATION_MULTILABEL_SET,
    Tasks.TEXT_NER: Metric.NER_SET,
    Tasks.TRANSLATION: Metric.TRANSLATION_SET,
    Tasks.SUMMARIZATION: Metric.SUMMARIZATION_SET,
    Tasks.QUESTION_ANSWERING: Metric.QA_SET,
    Tasks.QUESTION_ANSWERING_MULTIPLE_GROUND_TRUTH: Metric.QA_MULTIPLE_GROUND_TRUTH_SET,
    Tasks.FILL_MASK: Metric.FILL_MASK_SET,
    Tasks.TEXT_GENERATION: Metric.TEXT_GENERATION_SET,
    Tasks.CHAT_COMPLETION: Metric.CHAT_COMPLETION_SET,
    Tasks.RAG_EVALUATION: Metric.RAG_EVALUATION_SET,
    Tasks.CODE_GENERATION: Metric.CODE_GENERATION_SET,
    Tasks.VIDEO_MULTI_OBJECT_TRACKING: Metric.VIDEO_MULTI_OBJECT_TRACKING_SET,
}

SAMPLE_WEIGHTS_UNSUPPORTED_SET = {
    Metric.Spearman,
    Metric.WeightedAccuracy,
    Metric.MedianAbsError,
    Metric.NormMedianAbsError,
}

# Schema Types

# These types will be removed when the artifact-backed
# metrics are defined with protobuf
# Do not use these constants except in artifact-backed metrics
SCHEMA_TYPE_ACCURACY_TABLE = "accuracy_table"
SCHEMA_TYPE_FORECAST_HORIZON_TABLE = "forecast_horizon_table"
SCHEMA_TYPE_CONFUSION_MATRIX = "confusion_matrix"
SCHEMA_TYPE_CLASSIFICATION_REPORT = "classification_report"
SCHEMA_TYPE_RESIDUALS = "residuals"
SCHEMA_TYPE_PREDICTIONS = "predictions"
SCHEMA_TYPE_MAPE = "mape_table"
SCHEMA_TYPE_DISTRIBUTION_TABLE = "forecast_time_series_id_distribution_table"

# Ranges

SCORE_UPPER_BOUND = sys.float_info.max

MULTILABEL_PREDICTION_THRESHOLD = 0.5

CLASSIFICATION_RANGES = {
    Metric.Accuracy: (0.0, 1.0),
    Metric.WeightedAccuracy: (0.0, 1.0),
    Metric.NormMacroRecall: (0.0, 1.0),
    Metric.BalancedAccuracy: (0.0, 1.0),
    Metric.LogLoss: (0.0, SCORE_UPPER_BOUND),
    Metric.AUCBinary: (0.0, 1.0),
    Metric.AUCMacro: (0.0, 1.0),
    Metric.AUCMicro: (0.0, 1.0),
    Metric.AUCWeighted: (0.0, 1.0),
    Metric.F1Binary: (0.0, 1.0),
    Metric.F1Macro: (0.0, 1.0),
    Metric.F1Micro: (0.0, 1.0),
    Metric.F1Weighted: (0.0, 1.0),
    Metric.PrecisionBinary: (0.0, 1.0),
    Metric.PrecisionMacro: (0.0, 1.0),
    Metric.PrecisionMicro: (0.0, 1.0),
    Metric.PrecisionWeighted: (0.0, 1.0),
    Metric.RecallBinary: (0.0, 1.0),
    Metric.RecallMacro: (0.0, 1.0),
    Metric.RecallMicro: (0.0, 1.0),
    Metric.RecallWeighted: (0.0, 1.0),
    Metric.AvgPrecisionBinary: (0.0, 1.0),
    Metric.AvgPrecisionMacro: (0.0, 1.0),
    Metric.AvgPrecisionMicro: (0.0, 1.0),
    Metric.AvgPrecisionWeighted: (0.0, 1.0),
    Metric.AccuracyTable: (np.nan, np.nan),
    Metric.ConfusionMatrix: (np.nan, np.nan),
    Metric.MatthewsCorrelation: (-1.0, 1.0),
    Metric.IOU: (0.0, 1.0),
    Metric.IOUMicro: (0.0, 1.0),
    Metric.IOUMacro: (0.0, 1.0),
    Metric.IOUWeighted: (0.0, 1.0),
    Metric.ClassificationReport: (np.nan, np.nan),
    Metric.PrecisionClasswise: (np.nan, np.nan),
    Metric.RecallClasswise: (np.nan, np.nan),
    Metric.F1Classwise: (np.nan, np.nan),
    Metric.IOUClasswise: (np.nan, np.nan),
    Metric.AvgPrecisionClasswise: (np.nan, np.nan),
    Metric.AUCClasswise: (np.nan, np.nan),
}

REGRESSION_RANGES = {
    Metric.ExplainedVariance: (-SCORE_UPPER_BOUND, 1.0),
    Metric.R2Score: (-1.0, 1.0),  # Clipped at -1 for Miro
    Metric.Spearman: (-1.0, 1.0),
    Metric.MeanAbsError: (0.0, SCORE_UPPER_BOUND),
    Metric.NormMeanAbsError: (0.0, 1),  # Intentionally clipped at 1 for Miro
    Metric.MedianAbsError: (0.0, SCORE_UPPER_BOUND),
    Metric.NormMedianAbsError: (0.0, 1),  # Intentionally clipped at 1 for Miro
    Metric.RMSE: (0.0, SCORE_UPPER_BOUND),
    Metric.NormRMSE: (0.0, 1),  # Intentionally clipped at 1 for Miro
    Metric.RMSLE: (0.0, SCORE_UPPER_BOUND),
    Metric.NormRMSLE: (0.0, 1),  # Intentionally clipped at 1 for Miro
    Metric.MAPE: (0.0, SCORE_UPPER_BOUND),
    Metric.Residuals: (np.nan, np.nan),
    Metric.PredictedTrue: (np.nan, np.nan),
}

RANGES_TASK_MAP = {
    Tasks.CLASSIFICATION: CLASSIFICATION_RANGES,
    Tasks.REGRESSION: REGRESSION_RANGES,
}

# Objectives

MAXIMIZE = "maximize"
MINIMIZE = "minimize"
NA = "NA"

OBJECTIVES = {MAXIMIZE, MINIMIZE, NA}

CLASSIFICATION_OBJECTIVES = {
    Metric.Accuracy: MAXIMIZE,
    Metric.WeightedAccuracy: MAXIMIZE,
    Metric.NormMacroRecall: MAXIMIZE,
    Metric.BalancedAccuracy: MAXIMIZE,
    Metric.LogLoss: MINIMIZE,
    Metric.AUCBinary: MAXIMIZE,
    Metric.AUCMacro: MAXIMIZE,
    Metric.AUCMicro: MAXIMIZE,
    Metric.AUCWeighted: MAXIMIZE,
    Metric.F1Binary: MAXIMIZE,
    Metric.F1Macro: MAXIMIZE,
    Metric.F1Micro: MAXIMIZE,
    Metric.F1Weighted: MAXIMIZE,
    Metric.PrecisionBinary: MAXIMIZE,
    Metric.PrecisionMacro: MAXIMIZE,
    Metric.PrecisionMicro: MAXIMIZE,
    Metric.PrecisionWeighted: MAXIMIZE,
    Metric.RecallBinary: MAXIMIZE,
    Metric.RecallMacro: MAXIMIZE,
    Metric.RecallMicro: MAXIMIZE,
    Metric.RecallWeighted: MAXIMIZE,
    Metric.AvgPrecisionBinary: MAXIMIZE,
    Metric.AvgPrecisionMacro: MAXIMIZE,
    Metric.AvgPrecisionMicro: MAXIMIZE,
    Metric.AvgPrecisionWeighted: MAXIMIZE,
    Metric.AccuracyTable: NA,
    Metric.ConfusionMatrix: NA,
    TrainingResultsType.TRAIN_TIME: MINIMIZE,
    Metric.MatthewsCorrelation: MAXIMIZE,
    Metric.IOU: MAXIMIZE,
    Metric.IOUMicro: MAXIMIZE,
    Metric.IOUMacro: MAXIMIZE,
    Metric.IOUWeighted: MAXIMIZE,
    Metric.ClassificationReport: NA,
    Metric.PrecisionClasswise: NA,
    Metric.RecallClasswise: NA,
    Metric.F1Classwise: NA,
    Metric.IOUClasswise: NA,
    Metric.AvgPrecisionClasswise: NA,
    Metric.AUCClasswise: NA,
}

REGRESSION_OBJECTIVES = {
    Metric.ExplainedVariance: MAXIMIZE,
    Metric.R2Score: MAXIMIZE,
    Metric.Spearman: MAXIMIZE,
    Metric.MeanAbsError: MINIMIZE,
    Metric.NormMeanAbsError: MINIMIZE,
    Metric.MedianAbsError: MINIMIZE,
    Metric.NormMedianAbsError: MINIMIZE,
    Metric.RMSE: MINIMIZE,
    Metric.NormRMSE: MINIMIZE,
    Metric.RMSLE: MINIMIZE,
    Metric.NormRMSLE: MINIMIZE,
    Metric.MAPE: MINIMIZE,
    Metric.Residuals: NA,
    Metric.PredictedTrue: NA,
    TrainingResultsType.TRAIN_TIME: MINIMIZE,
}

# Note: using the same objectives as regression as both of them are having same metrics
FORECASTING_OBJECTIVES = REGRESSION_OBJECTIVES

IMAGE_CLASSIFICATION_OBJECTIVES = {
    Metric.Accuracy: MAXIMIZE,
}

IMAGE_CLASSIFICATION_MULTILABEL_OBJECTIVES = {
    Metric.IOU: MAXIMIZE,
}

IMAGE_OBJECT_DETECTION_OBJECTIVES = {
    Metric.MEAN_AVERAGE_PRECISION: MAXIMIZE,
}

IMAGE_GENERATION_OBJECTIVES = {
    Metric.FID: MAXIMIZE,
}

TEXT_CLASSIFICATION_OBJECTIVES = {
    Metric.Accuracy: MAXIMIZE,
    Metric.AUCWeighted: MAXIMIZE,
    Metric.PrecisionMicro: MAXIMIZE,
    Metric.PrecisionWeighted: MAXIMIZE,
}

TEXT_CLASSIFICATION_MULTILABEL_OBJECTIVES = {
    Metric.Accuracy: MAXIMIZE,
    Metric.F1Macro: MAXIMIZE,
    Metric.F1Micro: MAXIMIZE,
}

TEXT_NER_OBJECTIVES = {
    Metric.Accuracy: MAXIMIZE,
    Metric.F1Micro: MAXIMIZE,
    Metric.PrecisionMicro: MAXIMIZE,
    Metric.RecallMicro: MAXIMIZE,
}

TRANSLATION_OBJECTIVES = {
    Metric.TranslationBleu_1: MAXIMIZE,
    Metric.TranslationBleu_2: MAXIMIZE,
    Metric.TranslationBleu_3: MAXIMIZE,
    Metric.TranslationBleu_4: MAXIMIZE,
}

SUMMARIZATION_OBJECTIVES = {
    Metric.SummarizationRouge1: MAXIMIZE,
    Metric.SummarizationRouge2: MAXIMIZE,
    Metric.SummarizationRougeL: MAXIMIZE,
    Metric.SummarizationRougeLsum: MAXIMIZE,
}

QUESTION_ANSWERING_OBJECTIVES = {
    Metric.QAExactMatch: MAXIMIZE,
    Metric.QAF1Score: MAXIMIZE,
    Metric.BERTScore: MAXIMIZE,
    Metric.GPTSimilarity: MAXIMIZE,
    Metric.GPTCoherence: MAXIMIZE,
    Metric.GPTGroundedness: MAXIMIZE,
    Metric.GPTFluency: MAXIMIZE,
    Metric.GPTRelevance: MAXIMIZE,
    Metric.LLMSimilarity: MAXIMIZE,
    Metric.LLMCoherence: MAXIMIZE,
    Metric.LLMGroundedness: MAXIMIZE,
    Metric.LLMFluency: MAXIMIZE,
    Metric.LLMRelevance: MAXIMIZE,
}

QUESTION_ANSWERING_MULTIPLE_GROUND_TRUTH_OBJECTIVES = {
    Metric.QAMacroAveragedExactMatch: MAXIMIZE,
    Metric.QAMacroAveragedF1: MAXIMIZE,
}

FILL_MASK_OBJECTIVES = {
    Metric.FMPerplexity: MINIMIZE,
}

TEXT_GENERATION_OBJECTIVES = {
    Metric.SummarizationRouge1: MAXIMIZE,
    Metric.SummarizationRouge2: MAXIMIZE,
    Metric.SummarizationRougeL: MAXIMIZE,
    Metric.SummarizationRougeLsum: MAXIMIZE,
    Metric.TranslationBleu_1: MAXIMIZE,
    Metric.TranslationBleu_2: MAXIMIZE,
    Metric.TranslationBleu_3: MAXIMIZE,
    Metric.TranslationBleu_4: MAXIMIZE,
}

CHAT_COMPLETION_OBJECTIVES = {
    Metric.SummarizationRouge1: MAXIMIZE,
    Metric.SummarizationRouge2: MAXIMIZE,
    Metric.SummarizationRougeL: MAXIMIZE,
    Metric.SummarizationRougeLsum: MAXIMIZE,
    Metric.TranslationBleu_1: MAXIMIZE,
    Metric.TranslationBleu_2: MAXIMIZE,
    Metric.TranslationBleu_3: MAXIMIZE,
    Metric.TranslationBleu_4: MAXIMIZE,
    Metric.QAExactMatch: MAXIMIZE,
    Metric.QAF1Score: MAXIMIZE,
}

RAG_EVALUATION_OBJECTIVES = {
    Metric.RAG_GPTGroundedness: MAXIMIZE,
    Metric.RAG_GPTRelevance: MAXIMIZE,
    Metric.RAG_GPTRetrieval: MAXIMIZE,
}

CODE_GENERATION_OBJECTIVES = {Metric.CodeGenerationPassRateScore: MAXIMIZE}

FULL_OBJECTIVES = {
    **CLASSIFICATION_OBJECTIVES,
    **REGRESSION_OBJECTIVES,
    **FORECASTING_OBJECTIVES,
    **IMAGE_CLASSIFICATION_OBJECTIVES,
    **IMAGE_CLASSIFICATION_MULTILABEL_OBJECTIVES,
    **IMAGE_OBJECT_DETECTION_OBJECTIVES,
    **TEXT_CLASSIFICATION_MULTILABEL_OBJECTIVES,
    **TEXT_CLASSIFICATION_OBJECTIVES,
    **TEXT_NER_OBJECTIVES,
    **TRANSLATION_OBJECTIVES,
    **SUMMARIZATION_OBJECTIVES,
    **QUESTION_ANSWERING_OBJECTIVES,
    **QUESTION_ANSWERING_MULTIPLE_GROUND_TRUTH_OBJECTIVES,
    **FILL_MASK_OBJECTIVES,
    **TEXT_GENERATION_OBJECTIVES,
    **CHAT_COMPLETION_OBJECTIVES,
    **RAG_EVALUATION_OBJECTIVES,
    **CODE_GENERATION_OBJECTIVES,
}

OBJECTIVES_TASK_MAP = {
    Tasks.CLASSIFICATION: CLASSIFICATION_OBJECTIVES,
    Tasks.REGRESSION: REGRESSION_OBJECTIVES,
    Tasks.FORECASTING: FORECASTING_OBJECTIVES,
    Tasks.IMAGE_CLASSIFICATION: IMAGE_CLASSIFICATION_OBJECTIVES,
    Tasks.IMAGE_CLASSIFICATION_MULTILABEL: IMAGE_CLASSIFICATION_MULTILABEL_OBJECTIVES,
    Tasks.IMAGE_MULTI_LABEL_CLASSIFICATION: IMAGE_CLASSIFICATION_MULTILABEL_OBJECTIVES,
    Tasks.IMAGE_OBJECT_DETECTION: IMAGE_OBJECT_DETECTION_OBJECTIVES,
    Tasks.IMAGE_INSTANCE_SEGMENTATION: IMAGE_OBJECT_DETECTION_OBJECTIVES,
    Tasks.IMAGE_GENERATION: IMAGE_GENERATION_OBJECTIVES,
    Tasks.TEXT_CLASSIFICATION: TEXT_CLASSIFICATION_OBJECTIVES,
    Tasks.TEXT_CLASSIFICATION_MULTILABEL: TEXT_CLASSIFICATION_MULTILABEL_OBJECTIVES,
    Tasks.TEXT_NER: TEXT_NER_OBJECTIVES,
    Tasks.TRANSLATION: TRANSLATION_OBJECTIVES,
    Tasks.SUMMARIZATION: SUMMARIZATION_OBJECTIVES,
    Tasks.QUESTION_ANSWERING: QUESTION_ANSWERING_OBJECTIVES,
    Tasks.QUESTION_ANSWERING_MULTIPLE_GROUND_TRUTH: QUESTION_ANSWERING_MULTIPLE_GROUND_TRUTH_OBJECTIVES,
    Tasks.FILL_MASK: FILL_MASK_OBJECTIVES,
    Tasks.TEXT_GENERATION: TEXT_GENERATION_OBJECTIVES,
    Tasks.CHAT_COMPLETION: CHAT_COMPLETION_OBJECTIVES,
    Tasks.RAG_EVALUATION: RAG_EVALUATION_OBJECTIVES,
    Tasks.CODE_GENERATION: CODE_GENERATION_OBJECTIVES,
}

# Pipeline constants

DEFAULT_PIPELINE_SCORE = float("NaN")

# Metric restrictions

MINIMUM_METRIC_NAME_LENGTH = 3  # This is an arbitrary limit for validation.
MAXIMUM_METRIC_NAME_LENGTH = (
    50  # Check Run History restrictions before extending this limit.
)


class ExceptionTypes:
    """AzureML Exception Types."""

    User = "User"
    System = "System"
    Service = "Service"
    Unclassified = "Unclassified"
    All = {User, System, Service, Unclassified}


class TelemetryConstants:
    """Define telemetry constants."""

    COMPONENT_NAME = "automl"

    # Spans that are shared across different child run types
    # Formatting for span name: <Component_Name>.<Span_Name> e.g. automl.Training
    SPAN_FORMATTING = "{}.{}"
    # RunInitialization: Initialize common variables across remote wrappers
    RUN_INITIALIZATION = "RunInitialization"
    RUN_INITIALIZATION_USER_FACING = "Initializing AutoML run"
    # DataFetch: Setup and Featurization data fetching
    DATA_PREPARATION = "DataPrep"
    DATA_PREPARATION_USER_FACING = "Preparing input data"
    # LoadCachedData: Training and Model Explain load data from cache
    LOAD_CACHED_DATA = "LoadCachedData"
    LOAD_CACHED_DATA_USER_FACING = "Loading cached data"

    # Spans specific to Setup Run
    FEATURIZATION_STRATEGY = "FeaturizationStrategy"
    FEATURIZATION_STRATEGY_USER_FACING = "Deciding featurization actions"
    DATA_VALIDATION = "DataValidation"
    DATA_VALIDATION_USER_FACING = "Validating input data"

    # Spans specific to Featurization
    FEATURIZATION = "Featurization"
    FEATURIZATION_USER_FACING = "Featurizing data"

    # Spans specific to Training
    LOAD_ONNX_CONVERTER = "LoadOnnxConverter"
    LOAD_ONNX_CONVERTER_USER_FACING = "Loading ONNX converter"
    RUN_TRAINING = "RunE2ETraining"
    RUN_TRAINING_USER_FACING = "Running E2E training"
    TRAINING = "Training"
    TRAINING_USER_FACING = "Training model"
    VALIDATION = "Validation"
    VALIDATION_USER_FACING = "Validating model quality"
    METRIC_AND_SAVE_MODEL_NAME = "SaveModelArtifacts"
    METRIC_AND_SAVE_MODEL_USER_FACING = "Uploading run output metadata"
    ONNX_CONVERSION = "OnnxConversion"
    ONNX_CONVERSION_USER_FACING = "Converting to ONNX model"
    LOG_METRICS = "LogMetrics"
    LOG_METRICS_USER_FACING = "Logging run metrics"

    # Spans specific to Training
    BATCH_TRAINING = "BatchTraining"
    BATCH_TRAINING_USER_FACING = "Training model in batch"

    # Spans specific to Model Explain
    MODEL_EXPLANATION = "ModelExplanation"
    MODEL_EXPLANATION_USER_FACING = "Running model explainability"

    # Local Managed
    ScriptRunFinalizing = "ScriptRunFinalizing"
    ScriptRunStarting = "ScriptRunStarting"

    # Spans specific to Confidence Interval
    COMPUTE_CONFIDENCE_METRICS = "ComputeConfidenceMetrics"
    BOOTSTRAP_STEPS = "BootstrapSteps"

    # TODO: refactor / organize below and use compatible telemetry constants for activity logger and RH tracing
    AZUREML_METRICS_DISABLE_LOGGING = "AZUREML_METRICS_DISABLE_LOGGING"
    APP_NAME = "azureml-metrics"
    DEFAULT_VERSION = pkg_resources.get_distribution("azureml-metrics").version
    LOGGER_NAME = "azureml_metrics_package"
    NON_PII_MESSAGE = '[Hidden as it may contain PII]'
    TRUTHY = ['true', '1', 'yes', 'y', 't', True]
    LOGGING_FMT = '%(asctime)s [{}] [{}] [%(module)s] %(funcName)s +%(lineno)s: %(levelname)-8s ' + \
                  '[%(process)d] %(message)s \n'

    COMPUTE_METRICS_NAME = "ComputeMetrics"
    COMPUTE_METRICS_TASK_SUFFIX = "compute_metrics-{}"
    LIST_METRICS_NAME = "ListMetrics"
    LIST_METRICS_TASK_SUFFIX = "list_metrics-{}"

    LIST_TASKS_NAME = "ListTasks"
    LIST_PROMPTS = "ListPrompts"

    DOWNLOAD_ENSEMBLING_MODELS = "DownloadEnsemblingModels"
    DOWNLOAD_MODEL = "DownloadModel"
    FAILURE = "Failure"
    FIT_ITERATION_NAME = "FitIteration"
    GET_BEST_CHILD = "GetBestChild"
    GET_CHILDREN = "GetChildren"
    GET_OUTPUT = "GetOutput"
    GET_PIPELINE_NAME = "GetPipeline"
    OUTPUT_NAME = "Output"
    PACKAGES_CHECK = "PackagesCheck"
    PRE_PROCESS_NAME = "PreProcess"
    PREDICT_NAME = "Predict"
    REGISTER_MODEL = "RegisterModel"
    REMOTE_INFERENCE = "RemoteInference"
    RUN_CV_MEAN_NAME = "RunCVMean"
    RUN_CV_NAME = "RunCV"
    RUN_ENSEMBLING_NAME = "RunEnsembling"
    RUN_NAME = "Run"
    RUN_PIPELINE_NAME = "RunPipeline"
    RUN_TRAIN_FULL_NAME = "TrainFull"
    RUN_TRAIN_VALID_NAME = "TrainValid"
    SUCCESS = "Success"
    TIME_FIT_ENSEMBLE_NAME = "TimeFitEnsemble"
    TIME_FIT_INPUT = "TimeFitInput"
    TIME_FIT_NAME = "TimeFit"


class ReferenceCodes:
    """Reference codes for errors."""

    VALIDATE_NER = "validate_ner"
    VALIDATE_FILL_MASK = "validate_fill_mask"
    VALIDATE_QNA = "validate_qa"
    VALIDATE_SUMMARIZATION = "validate_summarization"
    VALIDATE_TRANSLATION = "validate_translation"
    VALIDATE_CHAT_COMPLETION = "validate_chat_completion"


class _TimeSeriesInternal:
    """Define the time series constants"""

    DUMMY_GRAIN_COLUMN = "_automl_dummy_grain_col"
    DUMMY_TARGET_COLUMN = "_automl_target_col"
    HORIZON_NAME = "horizon_origin"
    FORECAST_ORIGIN_COLUMN_NAME = "_automl_forecast_origin"


class ChatCompletionConstants:
    """Define chatcompletion metric constants"""

    CONVERSATION_NUMBER = "conversation_number"
    TURN_NUMBER = "turn_number"
    # rag_evaluation constants
    SCORE_PER_TURN = "score_per_turn"
    SCORE_PER_CONVERSATION = "score_per_conversation"
    REASON = "reason"
    # chat completion persona strings
    USER_PERSONA = "user"
    ASSISTANT_PERSONA = "assistant"
    SYSTEM_PERSONA = "system"
    # default response in case of error for RAG based metrics
    DEFAULT_GPT_SCORE = float("nan")
    DEFAULT_GPT_REASON = ""
    MAX_THREADS_PER_METRIC = 6
    # retry constants
    MAX_RETRIES = 6
    DELAY_FACTOR = 4
    MAX_DELAY = 10


class AggregationConstants:
    MAX = "max"
    MIN = "min"
    MEAN = "mean"
    MEDIAN = "median"


class CodeGenerationConstants:
    """constants needed for code generation metrics"""

    CODE_GENERATION_PREFIX = "pass@"


class ConcurrencyConstants:
    """constants needed for concurrency tasks"""
    MAX_CONCURRENT_REQUESTS = 4


class DefaultValues:
    # hardcoded custom system prompt for all gpt-star metrics
    DEFAULT_SYSTEM_PROMPT = "You are an AI assistant. You will be given the definition of an " \
                            "evaluation metric for assessing the quality of an answer in a " \
                            "question-answering task. Your job is to compute an accurate evaluation " \
                            "score using the provided evaluation metric."
    DEFAULT_CUSTOM_PROMPT_METRIC_NAME = "custom_prompt_metric"
    DEFAULT_OPENAI_SEED = 123
    DEFAULT_MAX_TOKENS_CUSTOM_METRIC = 1
    DEFAULT_GPT_MODEL = "gpt-35-turbo"

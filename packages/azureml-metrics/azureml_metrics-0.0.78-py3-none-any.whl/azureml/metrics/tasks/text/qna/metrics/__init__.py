# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics import constants
from azureml.metrics.common.metrics_registry import MetricsRegistry
from azureml.metrics.tasks.text.qna.dao.azureml_qna_dao import AzureMLQnADAO, AzureMLUnSupervisedQnADAO, \
    AzureMLQAMultipleGroundTruthDAO
from azureml.metrics.tasks.text.qna.metrics import _seq2seq_qa, _seq2seq_qa_multiple_ground_truth


def register_qa_metrics():
    MetricsRegistry.register(constants.Metric.QAExactMatch, _seq2seq_qa.ExactMatch, AzureMLQnADAO)
    MetricsRegistry.register(constants.Metric.QAF1Score, _seq2seq_qa.F1Score, AzureMLQnADAO)
    MetricsRegistry.register(constants.Metric.BERTScore, _seq2seq_qa.BERTScore, AzureMLQnADAO)
    MetricsRegistry.register(constants.Metric.AdaSimilarity, _seq2seq_qa.AdaSimilarity,
                             [AzureMLQnADAO, AzureMLQAMultipleGroundTruthDAO])
    MetricsRegistry.register(constants.Metric.GPTSimilarity, _seq2seq_qa.GPTSimilarity,
                             [AzureMLQnADAO, AzureMLQAMultipleGroundTruthDAO])
    MetricsRegistry.register(constants.Metric.LLMSimilarity, _seq2seq_qa.LLMSimilarity,
                             [AzureMLQnADAO, AzureMLQAMultipleGroundTruthDAO])
    # GPT/LLM-{Coherence, Groundedness, Fluency, Relevance} can be applied to both supervised and unsupervised QnA
    MetricsRegistry.register(constants.Metric.GPTCoherence, _seq2seq_qa.GPTCoherence,
                             [AzureMLQnADAO, AzureMLUnSupervisedQnADAO])
    MetricsRegistry.register(constants.Metric.GPTGroundedness, _seq2seq_qa.GPTGroundedness,
                             [AzureMLQnADAO, AzureMLUnSupervisedQnADAO])
    MetricsRegistry.register(constants.Metric.GPTFluency, _seq2seq_qa.GPTFluency,
                             [AzureMLQnADAO, AzureMLUnSupervisedQnADAO])
    MetricsRegistry.register(constants.Metric.GPTRelevance, _seq2seq_qa.GPTRelevance,
                             [AzureMLQnADAO, AzureMLUnSupervisedQnADAO])

    MetricsRegistry.register(constants.Metric.LLMCoherence, _seq2seq_qa.LLMCoherence,
                             [AzureMLQnADAO, AzureMLUnSupervisedQnADAO])
    MetricsRegistry.register(constants.Metric.LLMGroundedness, _seq2seq_qa.LLMGroundedness,
                             [AzureMLQnADAO, AzureMLUnSupervisedQnADAO])
    MetricsRegistry.register(constants.Metric.LLMFluency, _seq2seq_qa.LLMFluency,
                             [AzureMLQnADAO, AzureMLUnSupervisedQnADAO])
    MetricsRegistry.register(constants.Metric.LLMRelevance, _seq2seq_qa.LLMRelevance,
                             [AzureMLQnADAO, AzureMLUnSupervisedQnADAO])
    MetricsRegistry.register(constants.Metric.QAMacroAveragedExactMatch,
                             _seq2seq_qa_multiple_ground_truth.MacroAveragedExactMatch,
                             AzureMLQAMultipleGroundTruthDAO)
    MetricsRegistry.register(constants.Metric.QAMacroAveragedF1, _seq2seq_qa_multiple_ground_truth.MacroAveragedF1,
                             AzureMLQAMultipleGroundTruthDAO)


register_qa_metrics()

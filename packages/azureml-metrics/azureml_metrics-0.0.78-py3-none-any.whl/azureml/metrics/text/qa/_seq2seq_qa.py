# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Source for BERT Score: https://github.com/huggingface/evaluate/blob/main/metrics/bertscore/bertscore.py
# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Definitions for Question/Answering metrics."""
import os
import re
import sys
import asyncio
import string
import logging
import importlib.util
import numpy as np

from abc import abstractmethod
from collections import Counter
from typing import Any, List, Optional
from numpy.linalg import norm

from azureml.metrics.common._metric_base import Metric, ScalarMetric, NonScalarMetric
from azureml.metrics import constants
from azureml.metrics.common.import_utilities import load_evaluate,\
    load_openai_embeddings_utils, load_jinja2_utils, load_nest_asyncio
from azureml.metrics.common.utilities import retry
from azureml.metrics.common.exceptions import MissingDependencies

logger = logging.getLogger(__name__)


class Seq2SeqQAMetric(Metric):
    """Base class for Sequence to Sequence Question Answering metric"""
    ASYNC_BATCH_SIZE = 40

    def __init__(self,
                 y_test: List[Any],
                 y_pred: List[str],
                 tokenizer: Any,
                 regexes_to_ignore: List[str],
                 ignore_case: bool,
                 ignore_punctuation: bool,
                 ignore_numbers: bool,
                 lang: Optional[str] = "en",
                 model_type: Optional[str] = None,
                 idf: Optional[bool] = False,
                 rescale_with_baseline: Optional[bool] = True,
                 questions: Optional[List[str]] = None,
                 contexts: Optional[List[str]] = None,
                 use_openai_endpoint: Optional[bool] = False,
                 openai_api_batch_size: Optional[int] = 20,
                 openai_params: Optional[dict] = None,
                 max_concurrent_requests: Optional[int] = None,
                 use_chat_completion_api: Optional[bool] = None,
                 openai_embedding_engine: Optional[str] = None,
                 llm_params: Optional[dict] = None,
                 llm_api_batch_size: Optional[int] = 20,
                 llm_use_chat_completion_payload: Optional[bool] = False) -> None:
        """
        :param y_test: Tokenized References in the test set
        :param y_pred: Tokenized Hypothesis predicted by language model
        :param tokenizer: function that takes input a string, and returns a list of tokens
        :params regexes_to_ignore: List of string regular expressions to ignore
        :params ignore_case: Boolean to indicate whether to ignore case
        :params ignore_punctuation: Boolean to indicate whether to ignore punctuation
        :params ignore_numbers: Boolean to indicate whether to ignore numbers
        :params lang: String value to indicate the language of provided data.
        :param model_type: String to indicate the type of model while computing BERT score.
        :param idf: Boolean to indicate whether to use idf while computing BERT score.
        :param rescale_with_baseline: Boolean to indicate if we need to rescale BERT score.
        :param questions: Question used for the data sample used in computation of gpt-similarity metric.
        :param contexts: Context information used in Question Answering task for computing gpt-related metrics.
        :param openai_api_batch_size: number of prompts to be batched in one API call.
        :param openai_params: Dictionary contating credentials for openai API.
        :param use_chat_completion_api: boolean flag to choose between openAI completion vs chat completion API.
        :param openai_embedding_engine: String value to indicate the type of embedding engine to be used.
        """
        try:
            from azureml.metrics.common.llm_connector._openai_connector import OpenAIConnector
            from azureml.metrics.common.llm_connector._llm_url_connector import LLMUrlConnector
        except ImportError:
            safe_message = "Relevant GPT Star metrics packages are not available. " \
                           "Please run pip install azureml-metrics[prompt-flow]"
            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )

        self.y_test = y_test
        self.y_pred = y_pred
        self.tokenizer = tokenizer
        self.regexes_to_ignore = regexes_to_ignore
        self.ignore_case = ignore_case
        self.ignore_punctuation = ignore_punctuation
        self.ignore_numbers = ignore_numbers
        self.lang = lang
        self.model_type = model_type
        self.idf = idf
        self.rescale_with_baseline = rescale_with_baseline
        self.questions = questions
        self.contexts = contexts
        self.use_openai_endpoint = use_openai_endpoint
        self.openai_api_batch_size = openai_api_batch_size
        self.openai_params = openai_params
        self.max_concurrent_requests = max_concurrent_requests
        self.use_chat_completion_api = use_chat_completion_api
        self.openai_embedding_engine = openai_embedding_engine
        self.llm_params = llm_params
        self.llm_api_batch_size = llm_api_batch_size
        self.llm_use_chat_completion_payload = llm_use_chat_completion_payload
        self.openai_connector = OpenAIConnector(self.openai_params, self.openai_api_batch_size,
                                                self.use_chat_completion_api,
                                                max_concurrent_requests=self.max_concurrent_requests,
                                                use_openai_endpoint=self.use_openai_endpoint)
        self.llm_connector = LLMUrlConnector(self.llm_params, self.llm_api_batch_size,
                                             self.llm_use_chat_completion_payload)
        self.system_prompt = Seq2SeqQAMetric.get_prompt_template(file_path="system_prompt_qa.jinja2")
        # setting the logger level for urllib3 library to WARNING
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        super().__init__()

    @abstractmethod
    def compute(self) -> Any:
        """Compute the score for the metric"""
        ...

    """
    Function is same as normalize_answer(s) with name changed to normalize_text(self, text)
    Modified from
    https://github.com/huggingface/evaluate/blob/main/metrics/squad_v2/compute_score.py
    """

    @staticmethod
    def normalize_text(text) -> str:
        """Lower text and remove punctuation, articles and extra whitespace."""

        def remove_articles(text):
            return re.sub(r"\b(a|an|the)\b", " ", text)

        def white_space_fix(text):
            return " ".join(text.split())

        def remove_punc(text):
            exclude = set(string.punctuation)
            return "".join(ch for ch in text if ch not in exclude)

        def lower(text):
            return text.lower()

        return white_space_fix(remove_articles(remove_punc(lower(text))))

    def _compute_async_gpt_metric(self, prompt_list, system_prompt=None):
        nest_asyncio = load_nest_asyncio()
        prompt_batch_list = self.openai_connector.get_prompt_batches(prompt_list)

        nest_asyncio.apply()
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        results = []
        if system_prompt is None:
            system_prompt = self.system_prompt
        # Splitting the prompt_batch_list into smaller batches of size ASYNC_BATCH_SIZE
        for index in range(0, len(prompt_batch_list), Seq2SeqQAMetric.ASYNC_BATCH_SIZE):
            logger.debug("Processing data rows from {} to {} postion".format(index,
                                                                             index + Seq2SeqQAMetric.ASYNC_BATCH_SIZE))
            async_prompt_batch = prompt_batch_list[index:index + Seq2SeqQAMetric.ASYNC_BATCH_SIZE]
            async_prompt_batch_results = asyncio.run(self.openai_connector.get_async_prediction(
                prompt_batch_list=async_prompt_batch, system_prompt=system_prompt))
            results.extend(async_prompt_batch_results)

        # results = asyncio.run(self.openai_connector.get_async_prediction(prompt_batch_list=prompt_batch_list,
        #                                                                  system_prompt=self.system_prompt))
        return results

    def metric_max_over_references(self, metric_fn, prediction, references) -> Any:
        scores_for_references = []
        for reference in references:
            score = metric_fn(self, reference, prediction)
            scores_for_references.append(score)

        return max(scores_for_references)

    def metric_aggregation_over_references(self, metric_fn, prediction, references, aggregation="max") -> Any:
        scores_for_references = []
        for reference in references:
            score = metric_fn(self, reference, prediction)
            scores_for_references.append(score)

        if aggregation == "max":
            aggregated_score = max(scores_for_references)
        elif aggregation == "min":
            aggregated_score = min(scores_for_references)
        elif aggregation == "mean":
            aggregated_score = np.mean(scores_for_references)
        elif aggregation == "median":
            aggregated_score = np.median(scores_for_references)
        else:
            logger.info("Invalid aggregation method. Please choose from ['max', 'min', 'mean', 'median']."
                        " Applying max aggregation.")
            aggregated_score = max(scores_for_references)

        return aggregated_score

    def check_kwargs(self, metric_key: str) -> Any:
        """Compute the score for GPT Star metrics"""

        if metric_key in [constants.Metric.GPTGroundedness, constants.Metric.GPTRelevance,
                          constants.Metric.LLMGroundedness, constants.Metric.LLMRelevance]:
            if self.contexts is None:
                logger.warning("{} metric is not applicable as it needs question and context "
                               "for every example.".format(metric_key))
                return "nan"

        if metric_key in [constants.Metric.GPTRelevance, constants.Metric.LLMRelevance,
                          constants.Metric.GPTFluency, constants.Metric.LLMFluency,
                          constants.Metric.GPTCoherence, constants.Metric.LLMCoherence,
                          constants.Metric.GPTSimilarity, constants.Metric.LLMSimilarity]:
            if self.questions is None:
                logger.warning("{} metric is not applicable as it needs question "
                               "for every example.".format(metric_key))
                return "nan"

        if metric_key in [constants.Metric.GPTSimilarity, constants.Metric.LLMSimilarity]:
            if self.y_test is None:
                logger.warning("{} metric is not applicable as it needs ground truth "
                               "for every example.".format(metric_key))
                return "nan"

        # TODO : remove logit bias when we add explanation.
        # so that it returns values between 1 and 5
        if isinstance(self.openai_params, dict):
            self.openai_params["logit_bias"] = {16: 100, 17: 100, 18: 100, 19: 100, 20: 100}

    @staticmethod
    def get_prompt_template(file_path, **kwargs):
        """
        Given a file_path to a jinja2 template, render the template by replacing the variables in the template
        """
        Environment, FileSystemLoader = load_jinja2_utils()
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompt_templates')

        env = Environment(loader=FileSystemLoader(searchpath=template_dir), autoescape=True)

        template = env.get_template(file_path)
        return template.render(**kwargs)


class ExactMatch(Seq2SeqQAMetric, ScalarMetric):
    """ExactMatch metric for Sequence to Sequence Question Answering Tasks"""

    def exact_match_score(self, reference, prediction) -> Any:
        return self.normalize_text(reference) == self.normalize_text(prediction)

    def compute(self) -> Any:
        """Compute the score for ExactMatch metric"""
        if self.regexes_to_ignore is not None:
            for s in self.regexes_to_ignore:
                self.y_pred = np.array([re.sub(s, "", x) for x in self.y_pred])
                self.y_test = np.array([re.sub(s, "", x) for x in self.y_test])
        else:
            self.y_pred = np.asarray(self.y_pred)
            self.y_test = np.asarray(self.y_test)

        if self.ignore_case:
            self.y_pred = np.char.lower(self.y_pred)
            self.y_test = np.char.lower(self.y_test)

        if self.ignore_punctuation:
            repl_table = string.punctuation.maketrans("", "", string.punctuation)
            self.y_pred = np.char.translate(self.y_pred, table=repl_table)
            self.y_test = np.char.translate(self.y_test, table=repl_table)

        if self.ignore_numbers:
            repl_table = string.digits.maketrans("", "", string.digits)
            self.y_pred = np.char.translate(self.y_pred, table=repl_table)
            self.y_test = np.char.translate(self.y_test, table=repl_table)

        score_list = self.y_pred == self.y_test

        return score_list.tolist()


class F1Score(Seq2SeqQAMetric, ScalarMetric):
    """F1 score metric for Sequence to Sequence Question Answering Tasks"""

    """
    Function is similar to compute_f1(a_gold, a_pred) with modifications
    Modified from
    https://github.com/huggingface/evaluate/blob/main/metrics/squad_v2/compute_score.py
    """

    def f1_score(self, reference, prediction) -> Any:
        """Calculate F1 metric"""
        prediction_tokens = self.normalize_text(prediction)
        reference_tokens = self.normalize_text(reference)
        prediction_tokens = self.tokenizer(prediction_tokens)
        reference_tokens = self.tokenizer(reference_tokens)

        common = Counter(prediction_tokens) & Counter(reference_tokens)
        num_same = sum(common.values())
        if num_same == 0:
            return 0
        precision = 1.0 * num_same / len(prediction_tokens)
        recall = 1.0 * num_same / len(reference_tokens)
        f1 = (2 * precision * recall) / (precision + recall)
        return f1

    def compute(self) -> Any:
        """Compute the score for F1 score metric"""

        f1_score_list = []

        for reference, prediction in zip(self.y_test, self.y_pred):
            f1_score_list.append(self.f1_score(reference, prediction))

        return f1_score_list


class BERTScore(Seq2SeqQAMetric, ScalarMetric):
    """BERTScore metric for comparison of similarity between ground truths and predictions"""

    hf_bertscore = None

    def compute(self) -> Any:
        """Compute the score for BERT Score metric"""
        self.load_bertscore()

        if self.model_type is None:
            result = BERTScore.hf_bertscore.compute(predictions=self.y_pred, references=self.y_test,
                                                    lang=self.lang, idf=self.idf,
                                                    rescale_with_baseline=self.rescale_with_baseline)
        else:
            result = BERTScore.hf_bertscore.compute(predictions=self.y_pred, references=self.y_test,
                                                    lang=self.lang, model_type=self.model_type,
                                                    idf=self.idf,
                                                    rescale_with_baseline=self.rescale_with_baseline)
        return result

    @retry(max_attempts=constants.RetryConstants.MAX_ATTEMPTS,
           delay=constants.RetryConstants.DELAY_TIME)
    def load_bertscore(self):
        try:
            import evaluate
            bertscore_spec = importlib.util.find_spec("bert_score")
            torch_spec = importlib.util.find_spec("torch")
            transformers_spec = importlib.util.find_spec("transformers")

            if torch_spec is None or transformers_spec is None \
                    or bertscore_spec is None:
                raise ImportError

        except ImportError:
            safe_message = "bert-score packages are not available. " \
                           "Please run pip install azureml-metrics[bert-score]"

            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )
        if BERTScore.hf_bertscore is None:
            BERTScore.hf_bertscore = evaluate.load("bertscore")


class LLMSimilarity(Seq2SeqQAMetric, NonScalarMetric):
    """LLMSimilarity metric for comparison of similarity between ground truths and predictions"""

    def compute(self) -> Any:
        """Compute the score for GPT Similarity metric"""
        # _similarity_utils = load_similarity_utils()
        if self.check_kwargs(constants.Metric.LLMSimilarity) == "nan":
            return [float(np.nan) for _ in range(len(self.y_pred))]

        prompt_list = []
        # validation for presence of y_test and y_pred happens in compute_metrics() method.

        for question, ground_truth, prediction in zip(self.questions, self.y_test, self.y_pred):
            if isinstance(ground_truth, list):
                ground_truth = ground_truth[0]
                logger.info("Considering the first ground truth to compute LLM Similarity.")
            prompt = Seq2SeqQAMetric.get_prompt_template(
                file_path="similarity_score_qa.jinja2",
                question=question, ground_truth=ground_truth, prediction=prediction)
            prompt_list.append(prompt)

        # results = _similarity_utils.get_llm_prediction(prompt_list=prompt_list, llm_params=self.llm_params,
        #                                                llm_batch_size=self.llm_api_batch_size)
        results = self.llm_connector.get_llm_prediction(prompt_list=prompt_list)

        logger.debug("llm similarity results : {}".format(results))
        return results


class GPTSimilarity(Seq2SeqQAMetric, ScalarMetric):
    """GPTSimilarity metric for comparison of similarity between ground truths and predictions"""

    def compute(self) -> Any:
        """Compute the score for GPT Similarity metric"""
        logger.debug("Computing gpt similarity metric")
        if self.check_kwargs(constants.Metric.GPTSimilarity) == "nan":
            return [float(np.nan) for _ in range(len(self.y_pred))]

        prompt_list = []
        # validation for presence of y_test and y_pred happens in compute_metrics() method.
        for question, ground_truth, prediction in zip(self.questions, self.y_test, self.y_pred):
            if isinstance(ground_truth, list):
                ground_truth = ground_truth[0]
                logger.info("Considering the first ground truth to compute GPT Similarity.")
            prompt = Seq2SeqQAMetric.get_prompt_template(
                file_path="similarity_score_qa.jinja2",
                question=question, ground_truth=ground_truth, prediction=prediction)

            prompt_list.append(prompt)

        results = self._compute_async_gpt_metric(prompt_list)

        logger.debug("gpt similarity results : {}".format(results))
        return results


class LLMCoherence(Seq2SeqQAMetric, NonScalarMetric):
    """LLMCoherence metric for comparison of coherence between ground truths and predictions"""

    def compute(self) -> Any:
        """compute the score for GPTCoherence metric"""
        if self.check_kwargs(constants.Metric.LLMCoherence) == "nan":
            return [float(np.nan) for _ in range(len(self.y_pred))]

        prompt_list = []

        for question, prediction in zip(self.questions, self.y_pred):
            prompt = Seq2SeqQAMetric.get_prompt_template(
                file_path="coherence_score_qa.jinja2",
                question=question, prediction=prediction)
            prompt_list.append(prompt)

        results = self.llm_connector.get_llm_prediction(prompt_list=prompt_list)

        logger.debug("llm coherence results : {}".format(results))
        return results


class GPTCoherence(Seq2SeqQAMetric, ScalarMetric):
    """GPTCoherence metric for comparison of coherence between ground truths and predictions"""

    def compute(self) -> Any:
        """compute the score for GPTCoherence metric"""
        logger.debug("Computing gpt coherence metric")
        if self.check_kwargs(constants.Metric.GPTCoherence) == "nan":
            return [float(np.nan) for _ in range(len(self.y_pred))]

        prompt_list = []

        for question, prediction in zip(self.questions, self.y_pred):
            prompt = Seq2SeqQAMetric.get_prompt_template(
                file_path="coherence_score_qa.jinja2",
                question=question, prediction=prediction)
            prompt_list.append(prompt)

        system_prompt = Seq2SeqQAMetric.get_prompt_template(file_path="system_prompt_coherence_qa.jinja2")
        results = self._compute_async_gpt_metric(prompt_list, system_prompt)

        logger.debug("gpt coherence results : {}".format(results))
        return results


class LLMRelevance(Seq2SeqQAMetric, NonScalarMetric):
    """LLMRelevance metric for comparison of coherence between ground truths and predictions"""

    def compute(self) -> Any:
        """compute the score for GPTRelevance metric"""
        # _similarity_utils = load_similarity_utils()
        if self.check_kwargs(constants.Metric.LLMRelevance) == "nan":
            return [float(np.nan) for _ in range(len(self.y_pred))]

        prompt_list = []

        for context, question, prediction in zip(self.contexts, self.questions, self.y_pred):
            prompt = Seq2SeqQAMetric.get_prompt_template(
                file_path="relevance_score_qa.jinja2",
                context=context, question=question, prediction=prediction)
            prompt_list.append(prompt)

        # results = _similarity_utils.get_llm_prediction(prompt_list=prompt_list, llm_params=self.llm_params,
        #                                                llm_batch_size=self.llm_api_batch_size)
        results = self.llm_connector.get_llm_prediction(prompt_list=prompt_list)

        logger.debug("llm relevance results : {}".format(results))
        return results


class GPTRelevance(Seq2SeqQAMetric, ScalarMetric):
    """GPTRelevance metric for comparison of coherence between ground truths and predictions"""

    def compute(self) -> Any:
        """compute the score for GPTRelevance metric"""
        logger.debug("Computing gpt relevance metric")
        if self.check_kwargs(constants.Metric.GPTRelevance) == "nan":
            return [float(np.nan) for _ in range(len(self.y_pred))]

        prompt_list = []

        for context, question, prediction in zip(self.contexts, self.questions, self.y_pred):
            prompt = Seq2SeqQAMetric.get_prompt_template(
                file_path="relevance_score_qa.jinja2",
                context=context, question=question, prediction=prediction)
            prompt_list.append(prompt)

        results = self._compute_async_gpt_metric(prompt_list)

        logger.debug("gpt relevance results : {}".format(results))
        return results


class LLMFluency(Seq2SeqQAMetric, ScalarMetric):
    """LLMFluency metric for comparison of coherence between ground truths and predictions"""

    def compute(self) -> Any:
        """compute the score for GPTFluency metric"""
        # _similarity_utils = load_similarity_utils()
        if self.check_kwargs(constants.Metric.LLMFluency) == "nan":
            return [float(np.nan) for _ in range(len(self.y_pred))]

        prompt_list = []

        for question, prediction in zip(self.questions, self.y_pred):
            prompt = Seq2SeqQAMetric.get_prompt_template(
                file_path="fluency_score_qa.jinja2",
                question=question, prediction=prediction)
            prompt_list.append(prompt)

        # results = _similarity_utils.get_llm_prediction(prompt_list=prompt_list, llm_params=self.llm_params,
        #                                                llm_batch_size=self.llm_api_batch_size)
        results = self.llm_connector.get_llm_prediction(prompt_list=prompt_list)

        logger.debug("llm fluency results : {}".format(results))
        return results


class GPTFluency(Seq2SeqQAMetric, ScalarMetric):
    """GPTFluency metric for comparison of coherence between ground truths and predictions"""

    def compute(self) -> Any:
        """compute the score for GPTFluency metric"""
        logger.debug("Computing gpt fluency metric")
        if self.check_kwargs(constants.Metric.GPTFluency) == "nan":
            return [float(np.nan) for _ in range(len(self.y_pred))]

        prompt_list = []

        for question, prediction in zip(self.questions, self.y_pred):
            prompt = Seq2SeqQAMetric.get_prompt_template(
                file_path="fluency_score_qa.jinja2",
                question=question, prediction=prediction)
            prompt_list.append(prompt)

        results = self._compute_async_gpt_metric(prompt_list)

        logger.debug("gpt fluency results : {}".format(results))
        return results


class SquadV2(Seq2SeqQAMetric, ScalarMetric):
    """Squad_v2 metrics for Question Answering Tasks"""

    hf_squadv2 = None

    def compute(self) -> Any:
        """Compute score for Squad_v2 metrics"""
        # We will lazy load hf_squadv2 to avoid loading it in non seg2seq tasks
        self.load_squadv2()

        squad_v2_args = {"predictions": self.y_pred, "references": self.y_test}
        res = SquadV2.hf_squadv2.compute(
            predictions=self.y_pred, references=self.y_test, **squad_v2_args
        )

        return res

    @retry(max_attempts=constants.RetryConstants.MAX_ATTEMPTS,
           delay=constants.RetryConstants.DELAY_TIME)
    def load_squadv2(self):
        evaluate = load_evaluate()
        if SquadV2.hf_squadv2 is None:
            SquadV2.hf_squadv2 = evaluate.load("squad_v2")


class AdaSimilarity(Seq2SeqQAMetric, ScalarMetric):
    """Ada Similiarity for Question Answering Tasks"""

    def compute(self) -> Any:
        get_embedding = load_openai_embeddings_utils(self.openai_params, self.use_openai_endpoint)

        try:
            import openai
        except ImportError:
            safe_message = "openai package is not available. Please run pip " \
                           "install azureml-metrics[ada-similarity]"
            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )

        if self.openai_embedding_engine is None:
            embedding_model = "text-embedding-ada-002"
        else:
            embedding_model = self.openai_embedding_engine

        logger.info("Setting openai embedding engine to {}".format(embedding_model))
        result = []
        try:
            for a, b in zip(self.y_pred, self.y_test):
                if openai.__version__ < "1.0.0":
                    y_test_embedding = get_embedding(b, engine=embedding_model, **self.openai_params)
                    y_pred_embedding = get_embedding(a, engine=embedding_model, **self.openai_params)
                else:
                    y_test_embedding = get_embedding(b, model=embedding_model)
                    y_pred_embedding = get_embedding(a, model=embedding_model)

                result.append(np.dot(y_pred_embedding, y_test_embedding)
                              / (norm(y_pred_embedding) * norm(y_test_embedding)))
        except Exception as e:
            predicted_result = e.__class__.__name__
            logger.warning("Using the engine {} for computing ada similarity. "
                           "Please ensure to have valid deployment for {} model".format(embedding_model,
                                                                                        embedding_model))
            logger.warning("Could not compute metric because of the following exception : {}".format(str(e)))
            result = [str(predicted_result).lower() for _ in range(len(self.y_pred))]

        return result

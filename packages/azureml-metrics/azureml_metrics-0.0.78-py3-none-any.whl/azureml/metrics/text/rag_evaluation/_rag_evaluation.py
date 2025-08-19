# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Definitions for RAG Evaluation metrics."""
import os
import re
import random
import time
import logging
import numpy as np

from abc import abstractmethod
from typing import Any, List, Optional, Dict
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

from azureml.metrics import constants
from azureml.metrics.common._metric_base import Metric, NonScalarMetric
from azureml.metrics.common.templates.prompt_template import ChatPromptTemplate, StringPromptTemplate
from azureml.metrics.common.import_utilities import load_prompt_crafter, load_rag_init_functions,\
    load_llm_retry_function, load_openai_rate_limit_error
from azureml.metrics.text.rag_evaluation._rag_utils import Speaker, get_prompt_prefix


logger = logging.getLogger(__name__)


class RagEvaluationMetric(Metric):
    """Base class for RAG Evaluation metric"""

    # Retry constants
    max_retries = constants.ChatCompletionConstants.MAX_RETRIES
    delay_factor = constants.ChatCompletionConstants.DELAY_FACTOR
    max_delay = constants.ChatCompletionConstants.MAX_DELAY
    max_threads_per_metric = constants.ChatCompletionConstants.MAX_THREADS_PER_METRIC

    def __init__(self,
                 y_test: List[Any],
                 y_pred: dict,
                 openai_params: dict,
                 openai_api_batch_size: Optional[int] = 20,
                 use_chat_completion_api: Optional[bool] = None,
                 llm_params: Optional[dict] = None,
                 llm_api_batch_size: Optional[int] = 20,
                 score_version: Optional[str] = "v1",
                 use_previous_conversation: Optional[bool] = False) -> None:
        """
        :param y_test: Tokenized References in the test set
        :param y_pred: Tokenized Hypothesis predicted by language model
        :param openai_params: Dictionary containing credentials to initialize or setup openai API
        :param openai_api_batch_size: number of prompts to be batched in one API call.
        :param use_chat_completion_api: boolean flag to choose between openAI completion vs chat completion API.
        :param llm_params: Dictionary containing credentials to initialize or setup LLM
        :param llm_api_batch_size: number of prompts to be batched in one API call for LLM
        :param score_version: Version of rag evaluation metrics to be computed
        :param use_previous_conversation: boolean value to indicate if we need to use_previous_conversation
             for computing rag-evaluation metrics.
        """
        self.y_test = y_test
        self.y_pred = y_pred
        self.openai_params = openai_params
        self.openai_api_batch_size = openai_api_batch_size
        self.use_chat_completion_api = use_chat_completion_api
        self.llm_params = llm_params
        self.llm_api_batch_size = llm_api_batch_size
        self.score_version = score_version
        self.use_previous_conversation = use_previous_conversation
        self.quality_score_prefix = "<start quality score>"
        self.quality_score_suffix = "<end quality score>"
        self.quality_score_reasoning_prefix = "<start quality score reasoning>"
        self.quality_score_reasoning_suffix = "<end quality score reasoning>"
        self.reference_answer_suffix = "<end reference answer>"

        self.generation_prompt_prefix = get_prompt_prefix(
            "generation_prompt_without_gt.toml", "v1", "generation")
        self.retrieval_prompt_prefix = get_prompt_prefix(
            "retrieval_prompt.toml", "v1", "retrieval"
        )
        self.grounding_prompt_prefix = get_prompt_prefix(
            "grounding_prompt.toml", "v1", "grounding"
        )

        self._conversation_history = []
        self._domain = ""

        self.llm = self.extract_openai_params()
        # setting the logger level for urllib3 library to WARNING
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        super().__init__()

    def extract_openai_params(self):
        setup_llm, is_chat_completion_api = load_rag_init_functions()

        if self.openai_params is not None and isinstance(self.openai_params, dict):
            api_base = self.openai_params.get("api_base",
                                              self.openai_params.get("azure_endpoint",
                                                                     self.openai_params.get("base_url", None)))
            api_version = self.openai_params.get("api_version", None)
            api_key = self.openai_params.get("api_key", None)
            deployment_id = self.openai_params.get("deployment_id", self.openai_params.get("model", None))
            if deployment_id is None:
                deployment_id = self.openai_params.get("model", "gpt-35-turbo")
                logger.info("Using gpt-35-turbo for openai deployment_id as "
                            "model or deployment_id is not provided in openai_params")
            if api_base is None or api_version is None or api_key is None:
                return None
            else:
                if self.use_chat_completion_api is None:
                    if is_chat_completion_api(deployment_id):
                        self.use_chat_completion_api = True
                        logger.debug("Using chat completion API to evaluate scores")
                    else:
                        self.use_chat_completion_api = False
                        logger.debug("Using completion API to evaluate scores")

                return setup_llm(api_base, api_version,
                                 deployment_id, api_key,
                                 self.use_chat_completion_api)
        else:
            return None

    @abstractmethod
    def compute(self) -> Any:
        """Compute the score for the metric"""
        ...

    @staticmethod
    def aggregate(
            scores: List[Any]
    ) -> float:
        """
        Fold several scores from a computed metric together. For now,
        it is a list of list of strings, but the inside list has len 1

        :param scores: List of List of str, response from openai
        :return: Aggregated score.
        """
        int_scores = []
        for score in scores:
            try:
                int_scores.append(int(score[0]))
            except ValueError:
                int_scores.append(np.nan)

        if np.isnan(int_scores).sum() == len(int_scores):
            logger.error("Score aggregation failed with all non-integer scores")
            return float(np.nan)
        return float(np.nanmean(int_scores))

    @property
    def conversation_history(self):
        return str({"conversation_history": self._conversation_history})

    def add_to_conversation_history(self, turn: Dict[str, str]):
        self._conversation_history.append(turn)

    def reset_conversation_history(self):
        self._conversation_history = []

    @conversation_history.setter
    def conversation_history(self, value: List[str]):
        self._conversation_history = value

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value: str):
        self._domain = value

    @staticmethod
    def validate_quality_score(quality_score):
        """
        Set the score to default value if it is invalid or out of range.
        (i.e. not an integer or not in range of 1 to 5)
        :param quality_score: int, quality score
        :return: int, quality score
        """
        # If the score is not an integer or not in range of 1 to 5 set it to default value
        if not isinstance(quality_score, int) or quality_score < 1 or quality_score > 5:
            quality_score = constants.ChatCompletionConstants.DEFAULT_GPT_SCORE
        return quality_score

    def update_prompt_prefix(self, version: str, prompt_type: str):

        if prompt_type.lower() == "generation_with_gt":
            self.generation_prompt_prefix = get_prompt_prefix(
                "generation_prompt_with_gt.toml", version, "generation")
        elif prompt_type.lower() == "generation_without_gt":
            self.generation_prompt_prefix = get_prompt_prefix(
                "generation_prompt_without_gt.toml", version, "generation")
        elif prompt_type.lower() == "retrieval":
            self.retrieval_prompt_prefix = get_prompt_prefix(
                "retrieval_prompt.toml", version, "retrieval")
        elif prompt_type.lower() == "grounding":
            self.grounding_prompt_prefix = get_prompt_prefix(
                "grounding_prompt.toml", version, "grounding")
        elif prompt_type.lower() == "generation_prompt_sbs":
            self.generation_prompt_prefix = get_prompt_prefix(
                "generation_prompt_sbs.toml", version, "generation")
        else:
            raise ValueError(
                "Type must be one of generation, retrieval, or grounding")

    # TODO: check if this can be staticmethod
    def extract_result_from_output(self, output: str, result_prefix: str, result_suffix: str):
        if output.find(result_prefix) != -1 and output.find(result_suffix) != -1:
            result_start_index = output.find(
                result_prefix) + len(result_prefix)
            result_end_index = output.find(result_suffix)
            return output[result_start_index:result_end_index]
        else:
            return constants.ChatCompletionConstants.DEFAULT_GPT_REASON

    def extract_quality_score(self, output: str, quality_score_prefix: str, quality_score_suffix: str):
        quality_score_str = self.extract_result_from_output(
            output, quality_score_prefix, quality_score_suffix)
        numbers_found = re.findall(r"(\d+\.*\d*)\/", quality_score_str)
        if len(numbers_found) != 0:
            quality_score = int(float(numbers_found[0].replace("'", "")))
        else:
            quality_score = constants.ChatCompletionConstants.DEFAULT_GPT_SCORE
        return quality_score

    def extract_quality_reasoning(self, output: str,
                                  quality_score_reasoning_prefix: str,
                                  quality_score_reasoning_suffix: str):
        quality_reasoning = self.extract_result_from_output(
            output, quality_score_reasoning_prefix, quality_score_reasoning_suffix)
        return quality_reasoning

    def extract_reference_answer(self, output: str, reference_answer_suffix: str):
        if output.find(reference_answer_suffix) == -1:
            return ''
        else:
            reference_answer = output[0:output.find(reference_answer_suffix)]
            return reference_answer


class GenerationScore(RagEvaluationMetric, NonScalarMetric):
    """RAG_GPTRelevance metric for rag evaluation"""
    retry_with_exponential_backoff = load_llm_retry_function()

    @retry_with_exponential_backoff(max_retries=RagEvaluationMetric.max_retries,
                                    delay_factor=RagEvaluationMetric.delay_factor,
                                    max_delay=RagEvaluationMetric.max_delay)
    def get_generation_score(self,
                             question: str,
                             documents: str,
                             completion: str,
                             groundtruth_answer: str = "",
                             version: str = "v1",
                             has_ground_truth: bool = False):
        """
        question: str, question asked by user
        documents: str, retrieved documents
        completion: str, response generated by the model
        groundtruth_answer: str, ground truth answer, default is empty string
        version: str, version of the prompt template, default is v1
        has_ground_truth: bool, whether the ground truth answer is provided, default is False
        """
        conversation_history = ""
        domain = self._domain
        if has_ground_truth:
            if version == "v1":
                self.update_prompt_prefix("v1", "generation_with_gt")
                # TODO: please check how use_chat_completion_api needs to be set
                if self.use_chat_completion_api:
                    idx_start = self.generation_prompt_prefix.find("[system](#instructions)") \
                        + len("[system](#instructions)")
                    idx_end = self.generation_prompt_prefix.find("<|im_end|>")
                    prompt_prefix = self.generation_prompt_prefix[idx_start:idx_end]
                    prompt_template = [{"role": "system", "content": prompt_prefix},
                                       {"role": "user", "content": "#question\n{question}"},
                                       {"role": "user", "content": "#ground truth answer\n{groundtruth_answer}"},
                                       {"role": "user", "content": "#answer\n{completion}"},
                                       ]
                    prompt = ChatPromptTemplate(prompt_template_list=prompt_template, input_var_names=[
                        'prompt_prefix', 'question', 'completion', 'groundtruth_answer'], stop_strings=["<|im_end|>"])

                else:
                    prompt_template = ''.join((
                        self.generation_prompt_prefix.strip(),
                        '\n<|im_start|>user\n[user](#question)\n',
                        """{}""".format(question),
                        '\n<|im_end|>\n<|im_start|>user\n[user](#ground truth answer)\n"""',
                        """{}""".format(groundtruth_answer),
                        '\n<|im_end|>\n<|im_start|>user\n[user](#answer)\n"""',
                        """{}""".format(completion),
                        '\n[assistant](#evaluation result)\n'
                    ))
                    prompt = StringPromptTemplate(prompt_template_str=prompt_template,
                                                  input_var_names=['prompt_prefix', 'question', 'completion',
                                                                   'groundtruth_answer'],
                                                  stop_strings=["<|im_end|>"])
                llm_input = {
                    'prompt_prefix': self.generation_prompt_prefix.strip(),
                    'question': question.strip(),
                    'completion': completion.strip(),
                    'groundtruth_answer': groundtruth_answer.strip()
                }
            else:
                raise ValueError("Invalid version parameter. Version must be v1.")
        else:
            if version == "v1":
                conversation_history = self.conversation_history
                self.update_prompt_prefix("v1", "generation_without_gt")
                self.generation_prompt_prefix = self.generation_prompt_prefix.replace(
                    "{DOMAIN}", domain)
                if self.use_chat_completion_api:
                    idx_start = self.generation_prompt_prefix.find("[system](#instructions)") +\
                        len("[system](#instructions)")
                    idx_end = self.generation_prompt_prefix.find("<|im_end|>")
                    prompt_prefix = self.generation_prompt_prefix[idx_start:idx_end]
                    prompt_template = [{"role": "system", "content": prompt_prefix},
                                       {"role": "user", "content": "#conversation history\n{conversation_history}"},
                                       {"role": "user", "content": "#question\n{question}"},
                                       {"role": "user", "content": "#retrieved documents\n{documents}"},
                                       {"role": "user", "content": "#completion\n{completion}"},
                                       ]
                    prompt = ChatPromptTemplate(prompt_template_list=prompt_template,
                                                input_var_names=['prompt_prefix', 'question', 'completion',
                                                                 'conversation_history', 'documents'],
                                                stop_strings=["<|im_end|>"])

                else:
                    logger.debug("Using ChatML to evaluate generation score")
                    prompt_prefix = self.generation_prompt_prefix.strip()
                    conversation_history = conversation_history.strip()
                    prompt_template = ''.join((
                        prompt_prefix,
                        '\n<|im_start|>user\n[user](#conversation history)\n',
                        """{}""".format(conversation_history),
                        '\n<|im_end|>\n<|im_start|>user\n[user](#question)\n',
                        """{}""".format(question),
                        '\n<|im_end|>\n<|im_start|>user\n[user](#fetched documents)\n',
                        """{}""".format(documents),
                        '\n<|im_end|>\n<|im_start|>user\n[user](#provided response)\n',
                        """{}""".format(completion),
                        '\n<|im_end|>\n<|im_start|>assitant\n[assistant](#evaluation result)\n'
                        '<start reference answer>"""',
                    ))
                    prompt = StringPromptTemplate(prompt_template_str=prompt_template,
                                                  input_var_names=['prompt_prefix', 'question', 'completion',
                                                                   'conversation_history', 'documents'],
                                                  stop_strings=["<|im_end|>"])
                llm_input = {
                    'prompt_prefix': prompt_prefix,
                    'question': question.strip(),
                    'completion': completion.strip(),
                    'conversation_history': conversation_history,
                    'documents': documents.strip()}
            else:
                raise ValueError("Invalid version parameter. Version must be v1.")

        # TODO: check if we need llm abstraction
        if self.llm is None:
            logger.warning("rag evaluation metrics need openai_params to be computed")
            return float("nan"), ""

        LLMPromptCrafter = load_prompt_crafter()

        crafter = LLMPromptCrafter(prompt, self.llm)
        RateLimitError = load_openai_rate_limit_error()

        try:
            # TODO: parallelize this apply method
            llm_output = crafter.apply(llm_input)
        except RateLimitError:
            RagEvaluationMetric.max_threads_per_metric = max(1, RagEvaluationMetric.max_threads_per_metric - 1)
            logger.warning("Rate limit error, reducing the number of threads per metric to {}".format(
                RagEvaluationMetric.max_threads_per_metric))
            raise
        except Exception as e:
            logger.warning("Computing gpt based metrics failed with the exception : {}".format(str(e)))
            raise

        output = llm_output['response']
        quality_score = constants.ChatCompletionConstants.DEFAULT_GPT_SCORE
        quality_reasoning = constants.ChatCompletionConstants.DEFAULT_GPT_REASON
        # TODO: we have added the and condition in line 344
        # if conversation_history != "":
        if conversation_history != "" and self.quality_score_prefix in output \
                and self.quality_score_suffix in output:
            quality_score = self.extract_quality_score(
                output, self.quality_score_prefix, self.quality_score_suffix)
            quality_reasoning = self.extract_quality_reasoning(
                output, self.quality_score_reasoning_prefix, self.quality_score_reasoning_suffix)
            # TODO: do we need reference_answer?
            # reference_answer = self.extract_reference_answer(
            #     output, self.reference_answer_suffix)
            return quality_score, quality_reasoning
        else:
            for sent in output.split('\n'):
                sent = sent.strip()
                if re.match(r"\s*(<)?Quality score:", sent) or re.match(r"\s*(<)?quality score", sent.lower()):
                    numbers_found = re.findall(r"(\d+\.*\d*)\/", sent)
                    if len(numbers_found) == 0:
                        continue
                    quality_score = int(
                        float(numbers_found[0].replace("'", "")))
                elif len(re.findall(r"quality score.*?(\d+(\.\d+)?)\/\d+", output)) > 0:
                    matches = re.findall(r"quality score.*?(\d+(\.\d+)?)\/\d+", output)
                    scores = [float(match[0]) for match in matches]
                    quality_score = int(scores[0])

            quality_score = RagEvaluationMetric.validate_quality_score(quality_score)

            for sent in output.split('\n'):
                sent = sent.strip()
                if re.match(r"\s*(<)?Quality score reasoning:", sent) or \
                        re.match(r"\s*(<)?quality score reasoning", sent.lower()):
                    quality_reasoning += sent.strip()
                    break
            return quality_score, quality_reasoning

    def compute(self) -> Any:
        """Compute the score for RAG_GPTRelevance metric"""

        num_conversations = len(self.y_pred["model_result"])
        default_score = constants.ChatCompletionConstants.DEFAULT_GPT_SCORE

        score_per_turn = constants.ChatCompletionConstants.SCORE_PER_TURN
        score_per_conversation = constants.ChatCompletionConstants.SCORE_PER_CONVERSATION
        reason = constants.ChatCompletionConstants.REASON

        generation_score_dict = {
            score_per_turn: [[default_score] for _ in range(num_conversations)],
            score_per_conversation: [float("nan") for _ in range(num_conversations)],
            reason: [[""] for _ in range(num_conversations)]
        }

        executors_map = {}
        with tqdm(total=num_conversations, desc="Computing gpt relevance score") as pbar:

            with ThreadPoolExecutor(max_workers=int(os.environ.get(
                    "MAX_THREADS_PER_METRIC", RagEvaluationMetric.max_threads_per_metric))) as thread_pool:
                # iterating over multiple conversations
                for index, (conv_question, conv_model_result, conv_retrieved_documents, conv_ground_truth) \
                        in enumerate(zip(self.y_pred["question"], self.y_pred["model_result"],
                                         self.y_pred["retrieved_documents"], self.y_pred["ground_truth"])):
                    # add random delay between 10 ms to 100 ms
                    delay = random.uniform(0.01, 0.1)
                    time.sleep(delay)
                    executors_map[index] = thread_pool.submit(
                        self._compute_conversation, conv_question, conv_model_result, conv_retrieved_documents,
                        conv_ground_truth
                    )

                for index, task in executors_map.items():
                    score_dict = task.result()
                    generation_score_dict[score_per_turn][index] = score_dict[score_per_turn]
                    generation_score_dict[score_per_conversation][index] = score_dict[score_per_conversation]
                    generation_score_dict[reason][index] = score_dict[reason]
                    pbar.update(1)

        return generation_score_dict

    def _compute_conversation(self, conv_question, conv_model_result, conv_retrieved_documents, conv_ground_truth):
        # reset the history after one conversation
        self.reset_conversation_history()
        generation_score_per_conversation = []
        generation_reason_per_conversation = []
        # iterating turn by turn over a single conversation
        for question, model_result, retrieved_documents, ground_truth in zip(conv_question,
                                                                             conv_model_result,
                                                                             conv_retrieved_documents,
                                                                             conv_ground_truth):
            generation_score, generation_reason = self.get_generation_score(question, retrieved_documents,
                                                                            model_result, ground_truth,
                                                                            version=self.score_version)

            generation_score_per_conversation.append(generation_score)
            generation_reason_per_conversation.append(generation_reason)

            if self.use_previous_conversation:
                # add this turn to chat history
                logger.debug("adding previous turns to conversation history")
                self.add_to_conversation_history({Speaker.USER.value: question,
                                                  Speaker.BOT.value: model_result})
        score_dict = {
            "score_per_turn": generation_score_per_conversation,
            "score_per_conversation": np.nanmean(generation_score_per_conversation),
            "reason": generation_reason_per_conversation
        }

        return score_dict


class RetrievalScore(RagEvaluationMetric, NonScalarMetric):
    """RAG_GPTRetrieval metric for rag evaluation"""
    retry_with_exponential_backoff = load_llm_retry_function()

    @retry_with_exponential_backoff(max_retries=RagEvaluationMetric.max_retries,
                                    delay_factor=RagEvaluationMetric.delay_factor,
                                    max_delay=RagEvaluationMetric.max_delay)
    def get_retrieval_score(self, question: str, fetched_doc: str, version: str = "v1"):
        """
        retrieval metrics
        @param question: user raw query
        @param fetched_doc: casted string type of retrieved document dictionary,
          including id, title, content, meta, etc.
        @param version: version for retrieval metric
        """
        if version == "v1":
            prompt_template = self.create_prompt_template(fetched_doc, question)
            if self.use_chat_completion_api:
                prompt = ChatPromptTemplate(input_var_names=[], prompt_template_list=[
                    {"role": "user", "content": prompt_template}], stop_strings=["<|im_end|>"]
                )
            else:
                prompt = StringPromptTemplate(input_var_names=[], prompt_template_str=prompt_template,
                                              stop_strings=["<|im_end|>"])

            llm_input = {}
            if self.llm is None:
                logger.warning("rag evaluation metrics need openai_params to be computed")
                return float("nan"), ""
            LLMPromptCrafter = load_prompt_crafter()
            crafter = LLMPromptCrafter(prompt, self.llm)
            RateLimitError = load_openai_rate_limit_error()
            try:
                # TODO: parallelize this apply method
                llm_output = crafter.apply(llm_input)
            except RateLimitError:
                RagEvaluationMetric.max_threads_per_metric = max(1, RagEvaluationMetric.max_threads_per_metric - 1)
                logger.warning("Rate limit error, reducing the number of threads per metric to {}".format(
                    RagEvaluationMetric.max_threads_per_metric))
                raise
            except Exception as e:
                logger.warning("Computing gpt based metrics failed with the exception : {}".format(str(e)))
                raise
            output = llm_output['response']
            return self.post_process_results(output)
        else:
            logger.warning("current version only support retrieval v1, please check the version you set")
            return float("nan"), ""

    def create_prompt_template(self, fetched_doc, question):
        self.update_prompt_prefix("v1", "retrieval")
        self.retrieval_prompt_prefix = self.retrieval_prompt_prefix.replace("{{ history }}",
                                                                            self.conversation_history)
        self.retrieval_prompt_prefix = self.retrieval_prompt_prefix.replace("{{ query }}", question.strip())
        self.retrieval_prompt_prefix = self.retrieval_prompt_prefix.replace("{{ FullBody }}", fetched_doc.strip())
        prompt_template = ''.join((self.retrieval_prompt_prefix.strip()))
        return prompt_template

    def post_process_results(self, raw_output):
        try:
            pattern = re.compile(r"quality score:\s*(\d+)\/\d|<quality score:>\s*(\d+)\/\d"
                                 r"|<quality score>:\s*(\d+)\/\d")
            numbers_found = re.findall(pattern, raw_output.lower())

            score = constants.ChatCompletionConstants.DEFAULT_GPT_SCORE

            if len(numbers_found) > 0:
                for number in numbers_found[0]:
                    if isinstance(number, str) and number.isdigit():
                        score = int(number)
                        break

            # validate the generated quality score
            score = RagEvaluationMetric.validate_quality_score(score)
        except Exception as e:
            score = constants.ChatCompletionConstants.DEFAULT_GPT_SCORE
            logger.warning("parsing score error with the following exception : "
                           "{}, retrieval score set to nan".format(e))
        return score, raw_output

    def compute(self) -> Any:
        """Compute the score for RAG_GPTRetrieval metric"""

        num_conversations = len(self.y_pred["model_result"])
        default_score = constants.ChatCompletionConstants.DEFAULT_GPT_SCORE

        score_per_turn = constants.ChatCompletionConstants.SCORE_PER_TURN
        score_per_conversation = constants.ChatCompletionConstants.SCORE_PER_CONVERSATION
        reason = constants.ChatCompletionConstants.REASON

        retrieval_score_dict = {
            score_per_turn: [[default_score] for _ in range(num_conversations)],
            score_per_conversation: [float("nan") for _ in range(num_conversations)],
            reason: [[""] for _ in range(num_conversations)]
        }

        executors_map = {}
        with tqdm(total=num_conversations, desc="Computing gpt retrieval score") as pbar:
            with ThreadPoolExecutor(max_workers=int(os.environ.get(
                    "MAX_THREADS_PER_METRIC", RagEvaluationMetric.max_threads_per_metric))) as thread_pool:
                # iterating over multiple conversations
                for index, (conv_question, conv_model_result, conv_retrieved_documents) \
                        in enumerate(zip(self.y_pred["question"], self.y_pred["model_result"],
                                         self.y_pred["retrieved_documents"])):
                    # add random delay between 10 ms to 100 ms
                    delay = random.uniform(0.01, 0.1)
                    time.sleep(delay)
                    executors_map[index] = thread_pool.submit(
                        self._compute_conversation, conv_question, conv_model_result, conv_retrieved_documents,
                    )

                for index, task in executors_map.items():
                    score_dict = task.result()
                    retrieval_score_dict[score_per_turn][index] = score_dict[score_per_turn]
                    retrieval_score_dict[score_per_conversation][index] = score_dict[score_per_conversation]
                    retrieval_score_dict[reason][index] = score_dict[reason]
                    pbar.update(1)

        return retrieval_score_dict

    def _compute_conversation(self, conv_question, conv_model_result, conv_retrieved_documents):
        # reset the history after one conversation
        self.reset_conversation_history()
        retrieval_score_per_conversation = []
        retrieval_reason_per_conversation = []
        # iterating turn by turn over a single conversation
        for question, model_result, retrieved_documents in zip(conv_question,
                                                               conv_model_result,
                                                               conv_retrieved_documents):
            retrieval_score, retrieval_reason = self.get_retrieval_score(question, retrieved_documents,
                                                                         version=self.score_version)

            retrieval_score_per_conversation.append(retrieval_score)
            retrieval_reason_per_conversation.append(retrieval_reason)

            if self.use_previous_conversation:
                # add this turn to chat history
                logger.debug("adding previous turns to conversation history")
                self.add_to_conversation_history({Speaker.USER.value: question,
                                                  Speaker.BOT.value: model_result})
        score_dict = {
            "score_per_turn": retrieval_score_per_conversation,
            "score_per_conversation": np.nanmean(retrieval_score_per_conversation),
            "reason": retrieval_reason_per_conversation
        }

        return score_dict


class GroundingScore(RagEvaluationMetric, NonScalarMetric):
    """RAG_GPTGroundedness metric for rag evaluation"""
    retry_with_exponential_backoff = load_llm_retry_function()

    @retry_with_exponential_backoff(max_retries=RagEvaluationMetric.max_retries,
                                    delay_factor=RagEvaluationMetric.delay_factor,
                                    max_delay=RagEvaluationMetric.max_delay)
    def get_grounding_score(self, question: str, fetched_doc: str, completion: str, version: str = "v0"):
        """generates QnA pairs from a list of documents
        :param model_name: metric_name of the model to use
        :param temperature: temperature of the model
        :param prompt_version: version of the prompt to use
        :param documents: list of documents to generate QnA pairs from
        :return: list of QnA pairs
        """
        if version == "v1":
            prompt_template = self.create_prompt_template(completion, fetched_doc, question)
            if self.use_chat_completion_api:
                prompt = ChatPromptTemplate(input_var_names=[],
                                            prompt_template_list=[{"role": "user", "content": prompt_template}],
                                            stop_strings=["<|im_end|>"])
            else:
                prompt = StringPromptTemplate(input_var_names=[],
                                              prompt_template_str=prompt_template,
                                              stop_strings=["<|im_end|>"])
            llm_input = {}
            if self.llm is None:
                logger.warning("rag evaluation metrics need openai_params to be computed")
                return float("nan"), ""
            LLMPromptCrafter = load_prompt_crafter()
            crafter = LLMPromptCrafter(prompt, self.llm)
            RateLimitError = load_openai_rate_limit_error()
            try:
                # TODO: parallelize this apply method
                llm_output = crafter.apply(llm_input)
            except RateLimitError:
                RagEvaluationMetric.max_threads_per_metric = max(1, RagEvaluationMetric.max_threads_per_metric - 1)
                logger.warning("Rate limit error, reducing the number of threads per metric to {}".format(
                    RagEvaluationMetric.max_threads_per_metric))
                raise
            except Exception as e:
                logger.warning("Computing gpt based metrics failed with the exception : {}".format(str(e)))
                raise
            raw_output = llm_output['response']

            return self.post_process_results(raw_output)
        else:
            raise ValueError("Invalid version parameter. Current grounding score version must be v1.")

    def create_prompt_template(self, completion, fetched_doc, question):
        self.update_prompt_prefix("v1", "grounding")
        self.grounding_prompt_prefix = self.grounding_prompt_prefix.replace("{{ history }}",
                                                                            self.conversation_history)
        self.grounding_prompt_prefix = self.grounding_prompt_prefix.replace("{{ query }}", question.strip())
        self.grounding_prompt_prefix = self.grounding_prompt_prefix.replace("{{ FullBody }}", fetched_doc.strip())
        self.grounding_prompt_prefix = self.grounding_prompt_prefix.replace("{{ reply }}", completion.strip())
        prompt_template = ''.join((self.grounding_prompt_prefix.strip()))
        return prompt_template

    def post_process_results(self, raw_output):
        try:
            pattern = re.compile(r"quality score:\s*(\d+)\/\d|<quality score:>\s*(\d+)\/\d"
                                 r"|<quality score>:\s*(\d+)\/\d")
            numbers_found = re.findall(pattern, raw_output.lower())

            score = constants.ChatCompletionConstants.DEFAULT_GPT_SCORE
            if len(numbers_found) > 0:
                for number in numbers_found[0]:
                    if isinstance(number, str) and number.isdigit():
                        score = int(number)
                        break

            # validate the generated quality score
            score = RagEvaluationMetric.validate_quality_score(score)

        except Exception as e:
            score = constants.ChatCompletionConstants.DEFAULT_GPT_SCORE
            logger.warning("parsing score error with the following exception : "
                           "{}, grounding score set to nan".format(e))
        return score, raw_output

    def compute(self) -> Any:
        """Compute the score for RAG_GPTGroundedness metric"""

        num_conversations = len(self.y_pred["model_result"])
        default_score = constants.ChatCompletionConstants.DEFAULT_GPT_SCORE

        score_per_turn = constants.ChatCompletionConstants.SCORE_PER_TURN
        score_per_conversation = constants.ChatCompletionConstants.SCORE_PER_CONVERSATION
        reason = constants.ChatCompletionConstants.REASON

        grounding_score_dict = {
            score_per_turn: [[default_score] for _ in range(num_conversations)],
            score_per_conversation: [float("nan") for _ in range(num_conversations)],
            reason: [[""] for _ in range(num_conversations)]
        }

        executors_map = {}
        with tqdm(total=num_conversations, desc="Computing gpt groundedness score") as pbar:
            with ThreadPoolExecutor(max_workers=int(os.environ.get(
                    "MAX_THREADS_PER_METRIC", RagEvaluationMetric.max_threads_per_metric))) as thread_pool:
                # iterating over multiple conversations
                for index, (conv_question, conv_model_result, conv_retrieved_documents) \
                        in enumerate(zip(self.y_pred["question"], self.y_pred["model_result"],
                                         self.y_pred["retrieved_documents"])):
                    # add random delay between 10 ms to 100 ms
                    delay = random.uniform(0.01, 0.1)
                    time.sleep(delay)
                    executors_map[index] = thread_pool.submit(
                        self._compute_conversation, conv_question, conv_model_result, conv_retrieved_documents,
                    )

                for index, task in executors_map.items():
                    score_dict = task.result()
                    grounding_score_dict[score_per_turn][index] = score_dict[score_per_turn]
                    grounding_score_dict[score_per_conversation][index] = score_dict[score_per_conversation]
                    grounding_score_dict[reason][index] = score_dict[reason]
                    pbar.update(1)

        return grounding_score_dict

    def _compute_conversation(self, conv_question, conv_model_result, conv_retrieved_documents):
        # reset the history after one conversation
        self.reset_conversation_history()
        grounding_score_per_conversation = []
        grounding_reason_per_conversation = []
        # iterating turn by turn over a single conversation
        for question, model_result, retrieved_documents in zip(conv_question,
                                                               conv_model_result,
                                                               conv_retrieved_documents):
            grounding_score, grounding_reason = self.get_grounding_score(question,
                                                                         retrieved_documents,
                                                                         model_result,
                                                                         version=self.score_version)

            grounding_score_per_conversation.append(grounding_score)
            grounding_reason_per_conversation.append(grounding_reason)

            if self.use_previous_conversation:
                # add this turn to chat history
                logger.debug("adding previous turns to conversation history")
                self.add_to_conversation_history({Speaker.USER.value: question,
                                                  Speaker.BOT.value: model_result})
        score_dict = {
            "score_per_turn": grounding_score_per_conversation,
            "score_per_conversation": np.nanmean(grounding_score_per_conversation),
            "reason": grounding_reason_per_conversation
        }

        return score_dict

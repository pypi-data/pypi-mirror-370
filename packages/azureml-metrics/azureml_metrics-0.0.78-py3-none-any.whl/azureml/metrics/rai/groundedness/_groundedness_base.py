# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
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


"""Definitions for Groundedness metrics."""
import logging
import numpy as np
import asyncio
import sys

from typing import Any, List, Optional, Dict

from azureml.metrics.common._metric_base import Metric
from azureml.metrics.common.exceptions import MissingDependencies
from azureml.metrics import constants
from azureml.metrics.common.import_utilities import load_nest_asyncio

logger = logging.getLogger(__name__)


class GroundednessBase(Metric):
    """GPTGroundedness metric for comparison of generated content vs. context"""

    def __init__(self,
                 generated_contents: List[str],
                 tokenizer: Any,
                 contexts: List[str],
                 openai_params: dict,
                 max_concurrent_requests: Optional[int] = constants.ConcurrencyConstants.MAX_CONCURRENT_REQUESTS,
                 regexes_to_ignore: Optional[List[str]] = None,
                 ignore_case: bool = False,
                 ignore_punctuation: bool = False,
                 ignore_numbers: bool = False,
                 lang: Optional[str] = "en",
                 use_openai_endpoint: Optional[bool] = False,
                 openai_api_batch_size: Optional[int] = 20,
                 use_chat_completion_api: Optional[bool] = None,
                 llm_params: Optional[dict] = None,
                 llm_api_batch_size: Optional[int] = 20,
                 ) -> None:
        """
        :param generated_contents: list of generated contents to evaluate groundedness
        :param tokenizer: function that takes input a string, and returns a list of tokens
        :params regexes_to_ignore: List of string regular expressions to ignore
        :params ignore_case: Boolean to indicate whether to ignore case
        :params ignore_punctuation: Boolean to indicate whether to ignore punctuation
        :params ignore_numbers: Boolean to indicate whether to ignore numbers
        :param contexts: list of contexts against which to evaluate groundedness
        :param openai_params: Dictionary contating credentials for openai API.
        :params lang: String value to indicate the language of provided data.
        :param openai_api_batch_size: number of prompts to be batched in one API call.
        :param use_chat_completion_api: boolean flag to choose between openAI completion vs chat completion API.
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
        self.tokenizer = tokenizer
        self.regexes_to_ignore = regexes_to_ignore
        self.ignore_case = ignore_case
        self.ignore_punctuation = ignore_punctuation
        self.ignore_numbers = ignore_numbers
        self.lang = lang
        # y_pred is being referred as generated_contents
        self.generated_contents = generated_contents
        self.contexts = contexts
        self.use_openai_endpoint = use_openai_endpoint
        self.openai_api_batch_size = openai_api_batch_size
        self.openai_params = openai_params
        self.max_concurrent_requests = max_concurrent_requests
        self.use_chat_completion_api = use_chat_completion_api
        self.llm_params = llm_params
        self.llm_api_batch_size = llm_api_batch_size
        self.openai_connector = OpenAIConnector(openai_params, openai_api_batch_size,
                                                use_chat_completion_api,
                                                max_concurrent_requests=max_concurrent_requests,
                                                use_openai_endpoint=self.use_openai_endpoint)
        self.llm_url_connector = LLMUrlConnector(llm_params, llm_api_batch_size)

        self.system_prompt = self.get_system_prompt()
        super().__init__()

    def get_system_prompt(self) -> str:
        """this is a default system prompt, can be overwritten by child classes"""
        system_prompt = "You are an AI assistant. You will be given the definition of an " \
            "evaluation metric for assessing the quality of an answer in a " \
            "question-answering task. Your job is to compute an accurate evaluation " \
            "score using the provided evaluation metric."
        return system_prompt

    # in the future child class can overwrite post process function
    def post_process(self, raw_results) -> List[str]:
        results = []
        for result in raw_results:
            if isinstance(result, str):
                results.append(result.strip().lower())
            elif isinstance(result, list):
                results.append(result[0].strip().lower())
            else:
                results.append(result)
        return results

    def check_kwargs(self, metric_name: str) -> Any:
        if metric_name == constants.Metric.GPTGroundedness:
            if self.openai_params is None:
                logger.error("OpenAI params not provided.")
                return "nan"
            if self.generated_contents is None:
                logger.error("Generated contents not provided.")
                return "nan"
            if self.contexts is None:
                logger.error("Contexts not provided.")
                return "nan"
        elif metric_name == constants.Metric.LLMGroundedness:
            if self.llm_params is None:
                logger.error("LLM params not provided.")
                return "nan"
            if self.generated_contents is None:
                logger.error("Generated contents not provided.")
                return "nan"
            if self.contexts is None:
                logger.error("Contexts not provided.")
                return "nan"

    def compute(self) -> Any:
        """compute the score for GPTGroundedness metric"""
        ...

    def get_formatting_reminder(self) -> str:
        reminder = "Reminder: The return values for each task should be correctly formatted as an integer " \
            "between 1 and 5. Do not repeat the context and question.\n"
        return reminder

    def construct_user_prompts(self, context: str, gen_content: str) -> str:
        instruction = \
            "You will be presented with a CONTEXT and an ANSWER about that CONTEXT. " \
            "You need to decide whether the ANSWER is entailed by the CONTEXT by choosing one of" \
            " the following rating:\n" \
            "1. 5: The ANSWER follows logically from the information contained in the CONTEXT.\n" \
            "2. 1: The ANSWER is logically false from the information contained in the CONTEXT.\n" \
            "3. an integer score between 1 and 5 and if such integer score does not exist, " \
            "use 1: It is not possible to determine whether the ANSWER is true or false without " \
            "further information. " \
            "Read the passage of information thoroughly and select the correct " \
            "answer from the three answer labels. " \
            "Read the CONTEXT thoroughly to ensure you know what the CONTEXT entails. " \
            "Note the ANSWER is generated by a computer system, it can contain certain symbols, " \
            "which should not be a negative factor in the evaluation.\n"

        examples = \
            "Independent Examples:\n" \
            "## Example Task #1 Input:\n" \
            """{"CONTEXT": "The Academy Awards, also known as the Oscars are awards for """ \
            "artistic and technical merit for the film industry. " \
            "They are presented annually by the Academy of Motion Picture Arts and Sciences, " \
            "in recognition of excellence in cinematic achievements as assessed by the Academy's " \
            "voting membership. " \
            "The Academy Awards are regarded by many as the most prestigious, significant " \
            "awards in the entertainment " \
            """industry in the United States and worldwide.", """ \
            """"QUESTION": "", "ANSWER": "Oscar is presented every other two years"}\n""" \
            "## Example Task #1 Output:\n" \
            "1\n" \
            "## Example Task #2 Input:\n" \
            """{"CONTEXT": "The Academy Awards, also known as the Oscars are awards for """ \
            "artistic and technical merit for the film industry. " \
            "They are presented annually by the Academy of Motion Picture Arts and Sciences, " \
            "in recognition of excellence in cinematic achievements as assessed by the Academy's " \
            "voting membership. " \
            "The Academy Awards are regarded by many as the most prestigious, significant awards in the " \
            "entertainment " \
            """industry in the United States and worldwide.", """ \
            """"QUESTION": "", "ANSWER": "Oscar is very important awards in the entertainment industry in the """ \
            """United States. And it's also significant worldwide"}\n""" \
            "## Example Task #2 Output:\n" \
            "5\n" \
            "## Example Task #3 Input:\n" \
            """{"CONTEXT": "In Quebec, an allophone is a resident, usually an immigrant, whose mother tongue """\
            """or home language is neither French nor English.", """ \
            """"QUESTION": "", "ANSWER": "In Quebec, an allophone is a resident, usually an""" \
            " immigrant, whose mother " \
            """tongue or home language is not French."}\n""" \
            "## Example Task #3 Output:\n" \
            "5\n" \
            "## Example Task #4 Input:\n" \
            """{"CONTEXT": "Some are reported as not having been wanted at all.", "QUESTION": "", """ \
            """"ANSWER": "All are reported as being completely and fully wanted."}\n""" \
            "## Example Task #4 Output:\n" \
            "1\n"

        reminder = self.get_formatting_reminder()

        actual_task = \
            "## Actual Task Input:\n" \
            '{{"CONTEXT": {}, "QUESTION": "", "ANSWER": {}}}\n'.format(context, gen_content)

        output_prompt = "Actual Task Output:"

        prompt = instruction + examples + actual_task + reminder + output_prompt
        return prompt

    def construct_full_prompts(self, user_prompt_list) -> List[List[Dict[str, str]]]:
        """ this can be overwritten by child classes that want more flexibility,
        e.g. with different names for few shot examples"""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        result = []
        for user_prompt in user_prompt_list:
            result.append(messages + [{"role": "user", "content": user_prompt}])
        return result

    def _compute_async_gpt_metric(self, prompt_list):
        nest_asyncio = load_nest_asyncio()
        prompt_batch_list = self.openai_connector.get_prompt_batches(prompt_list)

        nest_asyncio.apply()
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        results = asyncio.run(self.openai_connector.get_async_prediction(prompt_batch_list=prompt_batch_list,
                                                                         system_prompt=self.system_prompt))
        return results

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

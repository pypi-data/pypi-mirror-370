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

"""Definitions for Groundedness conversation metrics."""
import logging
import numpy as np

from typing import Any, List, Optional
from azureml.metrics.common._metric_base import NonScalarMetric
from azureml.metrics.rai.groundedness._groundedness_base import GroundednessBase
from azureml.metrics import constants

logger = logging.getLogger(__name__)


class GroundednessConversation(GroundednessBase, NonScalarMetric):
    """Groundedness metric for conversation"""

    def __init__(self,
                 generated_contents: List[str],
                 tokenizer: Any,
                 contexts: List[str],
                 persona_name: List[str],
                 openai_params: dict,
                 lang: Optional[str] = "en",
                 openai_api_batch_size: Optional[int] = 20,
                 ) -> None:

        super().__init__(generated_contents=generated_contents,
                         tokenizer=tokenizer,
                         contexts=contexts,
                         openai_params=openai_params,
                         lang=lang,
                         openai_api_batch_size=openai_api_batch_size)
        self.persona_name = persona_name

    def construct_user_prompts(self, context: str, gen_content: str, persona_name: str) -> List[str]:
        instruction = \
            "You will be presented with a context and a multiturn conversation. " \
            """You need to decide whether the responses by assistant (prefixed by "(Assistant):") """ \
            "in the conversation is based on the context, or derived from it with common sense. Please " \
            """evaluate only the answer by the assistant, prefixed by "(Assistant):". You do not need to """ \
            f"evaluate the human's response prefixed by \"({persona_name})\":. Please choose the following rating:\n" \
            "5: The responses by the assistant all follow logically from the information contained in the context, " \
            "or can be derived from the context with common sense.]\n" \
            "1: The responses by the assistant contain information that is logically false from the information " \
            "contained in the context.\n" \
            "an integer score between 1 and 5 and if such integer score does not exists, use 1: " \
            "It is not possible to determine whether the responses by the assistant is true or false without " \
            "further information.\n" \
            "Read the passage of information thoroughly and select the correct answer from the three options above. " \
            "Read the context thoroughly to ensure you know what the context entails. Pay close " \
            "attention to any fact " \
            "not mentioned in the context. If such information occurs at any point of the conversation, it is not " \
            "completely grounded and needs to receive a score less than 5. Keep this " \
            "in mind as you go through the conversation.\n"

        reminder = self.get_formatting_reminder()

        actual_task = \
            "## Actual Task Input:\n" \
            '{{"context": {}, "conversation": {}}}\n'.format(context, gen_content)

        output_prompt = "Actual Task Output:"

        prompt = instruction + actual_task + reminder + output_prompt
        return [prompt]

    def get_system_prompt(self) -> str:
        conversation_system_prompt = "You are an AI assistant. You will be given the definition of an " \
            "evaluation metric for assessing the quality of the output of an assistant (prefixed by " \
            """ "(Assistant):"). """ \
            "Your job is to compute an accurate evaluation score using the provided evaluation metric."
        return conversation_system_prompt

    def compute(self) -> Any:
        """compute the score for GPTGroundedness metric"""
        if self.check_kwargs(constants.Metric.ConversationGroundingScore) == "nan":
            return [float(np.nan) for _ in range(len(self.generated_contents))]

        prompt_list = []

        for context, generated_content, persona_name in zip(self.contexts,
                                                            self.generated_contents,
                                                            self.persona_name):
            prompts = self.construct_full_prompts(self.construct_user_prompts(context,
                                                                              generated_content,
                                                                              persona_name))
            prompt_list.append(prompts)

        # results_raw = self.openai_connector.get_openai_response_all_instances(prompt_list)

        results_raw = self._compute_async_gpt_metric(prompt_list)
        logger.debug("gpt groundedness results : {}".format(results_raw))

        # post process
        results = self.post_process(results_raw)
        return results

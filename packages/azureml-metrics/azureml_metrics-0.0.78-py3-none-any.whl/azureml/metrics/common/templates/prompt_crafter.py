# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Store basic crafter that can be used to define new crafter or can be easily combined using Pipelines
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union

from azureml.metrics.common.exceptions import MissingDependencies, MetricsException

try:
    from azureml.metrics.common.llm_connector._llm import LLM
    from azureml.metrics.common.templates.prompt_template import StringPromptTemplate, \
        ChatPromptTemplate
except ImportError:
    safe_message = "Relevant RAG Evaluation packages are not available. " \
                   "Please run pip install azureml-metrics[rag-evaluation]"
    raise MissingDependencies(
        safe_message, safe_message=safe_message
    )


class AbstractPromptCrafter(ABC):
    @abstractmethod
    def apply(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Apply transformation to input variable to return output varaible values"""

    @abstractmethod
    async def async_apply(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Async interface to apply transformation to input variable to return output varaible values"""


class LLMPromptCrafter(AbstractPromptCrafter):
    """Prompt crafter that uses a LLM call to generate output variables
    """

    def __init__(
        self,
        prompt_to_execute: Union[StringPromptTemplate, ChatPromptTemplate],
        llm: LLM,
        generation_output_key: str = "response",
    ):
        """

        :param prompt_to_execute: A string prompt that is used by LLM to generate a response one all variables are set
        :param llm: LLM model used for generation
        :param generation_output_key: Name of the variable that stores the output of the LLM crafter.
            Defaults to 'response'
        """
        self.generation_output_key = generation_output_key
        self.prompt = prompt_to_execute
        self.llm = llm
        self.llm.update_stop_string(self.prompt.stop_strings)

    def reset_prompt(self, new_prompt: StringPromptTemplate):
        self.prompt = new_prompt

    def _apply_llm_preprocess(self, input_vars: Dict[str, Any]) -> Union[str, List]:
        self.prompt.set_input_vars(input_vars)
        if self.prompt.is_prompt_complete():
            this_prompt = self.prompt.get_prompt()
            return this_prompt
        else:
            raise MetricsException(
                f"Cannot execute incomplete prompt."
                f"Please provide all variables for prompt: {self.prompt.get_input_vars()}"
            )

    async def async_apply(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Execute prompt template using the input vars
        :return: Generated text from LLM with var_name as self.generation_output_key
        """
        this_prompt = self._apply_llm_preprocess(input_vars)
        generation = await self.llm.async_generate(this_prompt)
        return {self.generation_output_key: generation}

    def apply(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        this_prompt = self._apply_llm_preprocess(input_vars)
        generation = self.llm.generate(this_prompt)
        return {self.generation_output_key: generation}

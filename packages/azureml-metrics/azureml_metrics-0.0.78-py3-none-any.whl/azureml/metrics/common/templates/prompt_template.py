# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base template class for prompt templates

This module contains the base class for prompt templates. All prompt templates should inherit from this class.

Classes:
    AbstractPromptTemplate: Base class for prompt templates
    StringPromptTemplate: Prompt template that stores prompt as a string with expected varaibles
    that can be defined later
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Any, Union
import logging
from copy import deepcopy

from azureml.metrics.common.exceptions import MetricsException


class AbstractPromptTemplate(ABC):
    """Class to encapsulate prompts and varaibles needed to fully form that prompt.
    We expect to use prompt crafters to iteratively define variables needed to complete the prompt.
    """

    @abstractmethod
    def get_input_vars(self) -> Dict[str, str]:
        """return variables expected to be filled to form this prompt"""

    @abstractmethod
    def set_input_vars(self, input_vars: Dict[str, Any]):
        """return variables expected to be filled to form this prompt"""

    @abstractmethod
    def is_prompt_complete(self) -> bool:
        """Check if all the variables needed to complete the prompt have been defined"""

    @abstractmethod
    def get_prompt(self) -> Union[str, Dict]:
        """output prompt as a string after putting in all variables"""


class BasePromptTemplate(AbstractPromptTemplate):
    """Prompt template that stores prompt as a string with expected varaibles that can be defined later
    Note: Current template does not support arbitrary f-string like code execution. Just variable subsituition.
    Delayed execution is impossible without security issues of eval.
    """

    def __init__(self, input_var_names: List[str], prompt_template_str: str = "", prompt_template_list: List = [],
                 var_definitions: Optional[Dict[str, str]] = None, stop_strings: Optional[List[str]] = None):
        """

        :param prompt_template_str: String that will act as final prompt with variables formatted as '{var_name}'
        within the prompt template
        :param prompt_template_list: List that will act as final prompt with variables formatted as '{var_name}'
        within the prompt template
        :param input_var_names: Name of the variables that are expected to fully form the prompt. Please
        specifiy all '{var_name}'
        :param var_definitions: (Optional) Define what is epxected in the var name to make the template readable
        :param stop_strings: (Optional) List of strings that will stop the prompt. If any of these strings are present
        in the prompt, the prompt will be stopped.
        """
        self.template = prompt_template_str or prompt_template_list
        self.input_var_names = set(input_var_names)
        self.input_vars = {}
        self.intermediate_vars = {}

        # optional parameter that can be used to store explaination of what is expected in that varaible
        self.var_definitions = var_definitions
        self.stop_strings = stop_strings if stop_strings else []

    def get_input_vars(self) -> Dict[str, str]:
        return self.input_vars

    def set_input_vars(self, input_vars: Dict[str, Any]):
        """
        Set input variables expected by the prompt. Can be partial set-up.
        If there are extra variables, they will be saved in intermeduate vars
        :param input_vars: set of variable to be set in the prompt in form of a dict ({'var_name':'var_value'})
        """
        relevant_vars = {k: v for k, v in input_vars.items()
                         if k in self.input_var_names}
        if len(relevant_vars) > 0:
            check_str_types = all(
                [isinstance(v, str) for k, v in relevant_vars.items()] + [True])  # added true for empty input vars
            if not check_str_types:
                non_str_types = [
                    (k, "Current Type:{}".format(type(v))) for k, v in relevant_vars.items() if type(v) != str]
                if non_str_types != [("conversation", "Current Type:<class \'list\'>")]:
                    raise MetricsException(
                        "Please provide string types for input vars:{}".format(non_str_types))
            self.input_vars = {**self.input_vars, **relevant_vars}

        self.intermediate_vars = {**self.intermediate_vars, **input_vars}

    def get_unset_vars(self) -> Set[str]:
        """
        :return: names of variables still not set in the prompt
        """
        return self.input_var_names.difference(self.input_vars.keys())

    def is_prompt_complete(self):
        vars_left_to_set = self.get_unset_vars()
        if len(vars_left_to_set) == 0:
            return True
        else:
            logging.info(
                "Following variables are still not set: {}".format(vars_left_to_set))
            return False

    def get_intermediate_vars(self):
        return self.intermediate_vars

    def safe_replacement(self, key: str, value: str, template: str) -> str:
        replace_key = "{" + key + "}"
        replace_value = value

        return template.replace(replace_key, replace_value)


class StringPromptTemplate(BasePromptTemplate):
    def get_prompt(self) -> str:
        """
        Form the prompt from template using the existing set variables.
        If variables are unset, their templating is preserved
        """
        if not isinstance(self.template, str):
            raise MetricsException("Prompt template is not a string when using StringPromptTemplate")
        this_template = deepcopy(self.template)
        curr_unset_vars = list(self.get_unset_vars())
        for this_var in curr_unset_vars:
            this_template = this_template.replace(
                "{" + this_var + "}", "<" + this_var + ">")

        for key, value in self.input_vars.items():
            this_template = self.safe_replacement(key, value, template=this_template)
        pre_prompt = this_template
        for this_var in curr_unset_vars:
            pre_prompt = pre_prompt.replace(
                "<" + this_var + ">", "{" + this_var + "}")
        return pre_prompt


class ChatPromptTemplate(BasePromptTemplate):
    def _is_chat_turns(self, value) -> bool:
        if not isinstance(value, list):
            return False
        for turn in value:
            if not isinstance(turn, dict):
                return False
            if "role" not in turn or "content" not in turn:
                return False
        return True

    def get_prompt(self) -> List:
        """
        Form the prompt from template using the existing set variables.
        If variables are unset, their templating is preserved
        """
        if not isinstance(self.template, list):
            raise MetricsException("Prompt template is not a list when using ChatPromptTemplate")
        this_template = deepcopy(self.template)
        curr_unset_vars = list(self.get_unset_vars())

        conversation_idx = -1
        conversation_content = []

        for idx, turn in enumerate(this_template):
            if not isinstance(turn, dict):
                raise MetricsException("Prompt template is not a list of dict when using ChatPromptTemplate")
            message = turn["content"]
            for this_var in curr_unset_vars:
                message = message.replace(
                    "{" + this_var + "}", "<" + this_var + ">")
            for key, value in self.input_vars.items():
                if self._is_chat_turns(value):
                    if turn["role"] == "conversation" and turn["content"] == "{" + key + "}":
                        conversation_idx = idx
                        conversation_content = value
                else:
                    message = self.safe_replacement(key, value, template=message)
            turn["content"] = message
            this_template[idx] = turn

        if conversation_idx != -1:
            this_template = this_template[:conversation_idx] + conversation_content + \
                this_template[conversation_idx + 1:]

        pre_prompt = this_template
        for idx, turn in enumerate(pre_prompt):
            for this_var in curr_unset_vars:
                message = turn["content"]
                turn["content"] = message.replace(
                    "<" + this_var + ">", "{" + this_var + "}")
                pre_prompt[idx] = turn
        return pre_prompt

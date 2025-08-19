# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utils for RAG Evaluation metrics."""
import importlib.resources
import logging

from enum import Enum
from typing import Optional
from azureml.metrics.common.import_utilities import load_toml_lib

logger = logging.getLogger(__name__)


class PromptDelimiter:
    conversation: str = "<Conversation>"
    endOfTokens: str = "<|im_end|>"
    startOfAnswer: str = "<Generated Answer>"
    documentationStart: str = "<DocumentationStart>"
    documentationEnd: str = "<DocumentationEnd>"
    documentation: str = "<Documentation>"
    docDelimiter: str = "<DOC>\n"
    promptStart: str = "<|im_start|>"
    promptEnd: str = "<|im_end|>"
    promptSeparator: str = "<|im_sep|>"
    promptSystem: str = "[system]"
    promptUser: str = "user"
    promptAssistant: str = "assistant"
    currentMessageIntent: str = "Current Message Intent"


class Speaker(Enum):
    USER = PromptDelimiter.promptUser
    BOT = PromptDelimiter.promptAssistant


def load_toml(prompt_file: str = "sbs_prompt.toml",
              source_module: Optional[str] = "azureml.metrics.text.rag_evaluation.prompt_templates") -> dict:
    # source_module: Optional[str] = "rag_evaluation.prompt_templates") -> dict:
    toml = load_toml_lib()
    try:
        with importlib.resources.open_text(source_module, prompt_file, encoding="ISO-8859-1") as f:
            return toml.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"toml file loading error,double check this: {prompt_file}")


def get_prompt_prefix(filename: str,
                      version: str = "",
                      purpose: str = "retrieval",
                      keyword: str = "prefix"):
    """
    get prompt prefix

    :param filename: filename of the toml file
    :param version: version of the prompt - no version by default
    :param purpose: purpose of the prompt - "retrieval" or "generation"
    :param keyword: indicates if prefix to be used
    :return: prompt prefix and prompt template
    """
    prompt_dict = load_toml(filename)

    # use version control if there are more than one version of the prompt
    try:
        if version != "":
            prefix = prompt_dict[purpose][version][keyword] if keyword in prompt_dict[purpose][version] else ""
        else:
            prefix = prompt_dict[purpose][keyword] if keyword in prompt_dict[purpose] else ""
    except KeyError:
        raise KeyError(
            f"please check if keywords: {purpose}, prefix, examples(optional), {version} exist your toml file")
    prompt_prefix = prefix

    if prompt_prefix == "":
        raise ValueError(
            "prompt prefix is empty, we need the key word 'retrieval', 'prefix', 'examples(optional)' "
            "in the toml file")

    return prompt_prefix

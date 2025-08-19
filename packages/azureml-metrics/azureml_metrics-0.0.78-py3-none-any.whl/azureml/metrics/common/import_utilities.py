# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for importing required dependencies."""
import copy

from azureml.metrics.common.exceptions import MissingDependencies, ValidationException


def load_sklearn():
    try:
        import sklearn
        import sklearn.metrics
    except ImportError:
        safe_message = "Tabular packages are not available. " \
                       "Please run pip install azureml-metrics[tabular]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return sklearn


def load_evaluate():
    try:
        import evaluate
    except ImportError:
        safe_message = "evaluate package is not available. Please run pip install azureml-metrics[evaluate]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return evaluate


def load_openai_embeddings_utils(openai_params, use_openai_endpoint=False):
    try:
        import openai
        import os

        openai_v1_kwargs = copy.deepcopy(openai_params)

        if openai.__version__ < "1.0.0":
            from openai.embeddings_utils import get_embedding
        else:
            if use_openai_endpoint is True:
                from openai import OpenAI

                client = OpenAI(
                    api_key=openai_v1_kwargs.pop("api_key", os.getenv("OPENAI_API_KEY"))
                )

            else:
                from openai import AzureOpenAI

                client = AzureOpenAI(
                    azure_endpoint=openai_v1_kwargs.pop("azure_endpoint",
                                                        openai_params.pop("base_url",
                                                                          os.getenv("AZURE_OPENAI_ENDPOINT"))),
                    api_key=openai_v1_kwargs.pop("api_key", os.getenv("AZURE_OPENAI_KEY")),
                    api_version=openai_v1_kwargs.pop("api_version", os.getenv("AZURE_OPENAI_VERSION")),
                )

            # TODO: openAI > "1.0.0" doesn't support get_embedding method
            def get_embedding(text, model="text-embedding-ada-002"):
                return client.embeddings.create(input=[text], model=model).data[0].embedding

    except ImportError:
        safe_message = "openai.embedding_utils package is not available. Please run pip " \
                       "install azureml-metrics[ada-similarity]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return get_embedding


def load_similarity_utils():
    try:
        from azureml.metrics.text.qa import _similarity_utils

    except ImportError:
        safe_message = "Relevant GPT Star metrics packages are not available. " \
                       "Please run pip install azureml-metrics[prompt-flow]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return _similarity_utils


def load_llm_retry_function():
    try:
        from azureml.metrics.common.llm_connector.llm_utils import retry_with_exponential_backoff
    except ImportError:
        safe_message = "Relevant Evaluation packages are not available. " \
                       "Please run pip install azureml-metrics[prompt-flow]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return retry_with_exponential_backoff


def load_openai_rate_limit_error():
    try:
        import openai
        if openai.__version__ < "1.0.0":
            from openai.error import RateLimitError
        else:
            from openai import RateLimitError

    except ImportError:
        safe_message = "Relevant Evaluation packages are not available. " \
                       "Please run pip install azureml-metrics[prompt-flow]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return RateLimitError


def load_jinja2_utils():
    try:
        from jinja2 import Environment, FileSystemLoader

    except ImportError:
        safe_message = "Relevant GPT Star metrics packages are not available. " \
                       "Please run pip install azureml-metrics[prompt-flow]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return Environment, FileSystemLoader


def load_jinja2_template():
    try:
        from jinja2 import Template

    except ImportError:
        safe_message = "Relevant GPT Star metrics packages are not available. " \
                       "Please run pip install azureml-metrics[prompt-flow]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return Template


def load_nest_asyncio():
    try:
        import nest_asyncio

    except ImportError:
        safe_message = "Relevant GPT Star metrics packages are not available. " \
                       "Please run pip install azureml-metrics[prompt-flow]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return nest_asyncio


def load_toml_lib():
    try:
        import toml
    except ImportError:
        safe_message = "Relevant RAG Evaluation packages are not available. " \
                       "Please run pip install azureml-metrics[rag-evaluation]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return toml


def load_prompt_crafter():
    try:
        from azureml.metrics.common.templates.prompt_crafter import LLMPromptCrafter
    except ImportError:
        safe_message = "Relevant RAG Evaluation packages are not available. " \
                       "Please run pip install azureml-metrics[rag-evaluation]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return LLMPromptCrafter


def load_rag_init_functions():
    try:
        from azureml.metrics.common.llm_connector._llm import setup_llm, is_chat_completion_api
    except ImportError:
        safe_message = "Relevant RAG Evaluation packages are not available. " \
                       "Please run pip install azureml-metrics[rag-evaluation]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )
    return setup_llm, is_chat_completion_api


def load_mmtrack_eval_mot():
    """Load mmtrack package for evaluation."""
    try:
        from mmtrack.core.evaluation.eval_mot import eval_mot
        return eval_mot
    except ImportError:
        msg = "mmtrack package import failed, the package is not installed. \
               mmtrack is in need in video multi-object-tracking scenario, \
               and it's going to be installed in azureml-acft-image-components. \
               please install mmtrack==0.14.0"
        return ValidationException(msg, safe_message=msg)


def load_image_generation_utilities():
    """Load Image from PIL, torch, center_crop from torchvision and fid from cleanfid."""

    try:
        import torch
        from PIL import Image
        from torchvision.transforms.functional import center_crop
        from cleanfid import fid
    except ImportError:
        safe_message = "Image generation evaluation packages not installed. " \
                       "Please run pip install torchvision==0.14.1 clean-fid==0.1.35 ."
        raise MissingDependencies(safe_message, safe_message=safe_message)

    return torch, Image, center_crop, fid

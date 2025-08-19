# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pandas as pd
import time
import threading
import functools
import logging
import asyncio
from random import random

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field

from azureml.metrics.common.exceptions import OAIClientContentFilterException, MissingDependencies
from azureml.metrics import constants

try:
    import openai
    if openai.__version__ < "1.0.0":
        from openai.error import RateLimitError, APIConnectionError, AuthenticationError
    else:
        from openai import RateLimitError, APIConnectionError, AuthenticationError
    from requests.exceptions import HTTPError
except ImportError:
    safe_message = "Relevant Evaluation packages are not available. " \
                   "Please run pip install azureml-metrics[prompt-flow]"
    raise MissingDependencies(
        safe_message, safe_message=safe_message
    )

logger = logging.getLogger(constants.TelemetryConstants.APP_NAME)


class LLMState:
    """Maintain the state of LLM usage"""

    def __init__(self):
        self.total_token_usage = 0
        self.prompt_token_usage = 0
        self.completion_token = 0

    def update(self, total_token_usage=0, prompt_token_usage=0, completion_token=0):
        self.total_token_usage += total_token_usage
        self.prompt_token_usage += prompt_token_usage
        self.completion_token += completion_token

    def __str__(self):
        return f"LLMState(total_token_usage={self.total_token_usage}, " \
               f"prompt_token_usage={self.prompt_token_usage}, completion_token={self.completion_token})"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise KeyError(f'Invalid key: {key}')


@dataclass
class OAIGenerationConfig:
    """Class to hold OAI config. Used to instantiate GPTEndpoint

    Members:
        model: str - model to use for chatbot
        temperature: float - temperature to use for chatbot
        top_p: float - top_p to use for chatbot
        max_tokens: int - max_tokens to use for chatbot
        stop: Optional[List[str]] - stop to use for chatbot
    """
    # TODO: check if we need to use different default model
    model: str = "chatgpt"
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 1000
    stop: Optional[List[str]] = field(default_factory=list)
    is_streaming: bool = False

    try:
        import openai
        if openai.__version__ >= "1.0.0":
            seed: int = constants.DefaultValues.DEFAULT_OPENAI_SEED
    except Exception:
        raise


def handle_finish_reason(response: Dict[str, Any], llm_state: Optional[LLMState]) -> Optional[str]:
    if 'finish_reason' not in response["choices"][0]:
        return None
    finish_reason = response["choices"][0]['finish_reason']
    if not finish_reason:
        return None
    if finish_reason == 'content_filter':
        raise OAIClientContentFilterException()
    # calculate tokens if not a content filter error and llm state is available
    if 'usage' in response:
        usage = response['usage']
        if usage and 'total_tokens' in usage and llm_state:
            llm_state.update(
                total_token_usage=usage['total_tokens'],
                prompt_token_usage=usage['prompt_tokens'],
                completion_token=usage['completion_tokens']
            )
    if finish_reason == 'length':
        # TODO: check if we need to return an exception here
        return 'stop'  # raise LengthFinishException()
    elif finish_reason == 'stop':
        return 'stop'


def conversation_metric_aggregation(report_df: pd.DataFrame):
    conversation_avg_scores = report_df.mean().round(2)
    return conversation_avg_scores


def retry_with_exponential_backoff(max_retries: int = 10,
                                   delay_factor: float = 2.0,
                                   max_delay: float = 300.0,
                                   jitter: bool = True,
                                   verbose: bool = False):

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if retries == max_retries:
                        logger.warning("Computation of GPT Evaluation metrics failed with the following "
                                       "exception :\n {}".format(e))
                        raise e

                    sleep_time = _openai_error_handling(e, retries)

                    # sleeping for sleep_time seconds
                    time.sleep(sleep_time)

                    if verbose:
                        logger.warning(f"Woke Up {threading.get_ident()}")
                    retries += 1

        def _openai_error_handling(e, retries):
            sleep_time = delay_factor ** retries
            if jitter:
                sleep_time = sleep_time * (0.5 + random())  # Add random jitter
            sleep_time = min(sleep_time, max_delay)
            # fail fast without retry for AuthenticationError and APIConnectionError
            if isinstance(e, AuthenticationError) or isinstance(e, APIConnectionError)\
                    or isinstance(e, TypeError):
                logger.warning("Computation of GPT Evaluation metrics for {} failed with the following "
                               "exception :\n {}".format(func, e))
                raise e
            if isinstance(e, RateLimitError):
                retry_after_in_header = None
                retry_after_in_header_response = None
                retry_after = 0

                if hasattr(e, "headers"):
                    retry_after_in_header = e.headers.get("Retry-After", None)
                if hasattr(e, "response") and hasattr(e.response, "headers"):
                    retry_after_in_header_response = e.response.headers.get("Retry-After", None)

                if hasattr(e, "error") and getattr(e.error, "type", None) == "insufficient_quota":
                    logger.warning(
                        "Insufficient quota for computing GPT Evaluation metrics."
                        " Please choose the deployment with higher quota.")
                    raise e
                elif retry_after_in_header is not None:
                    retry_after = float(retry_after_in_header)

                elif retry_after_in_header_response is not None:
                    retry_after = float(retry_after_in_header_response)

                elif "Please retry after" in str(e):
                    retry_after = int(str(e).split('Please retry after ')[1].split(' second')[0]) + 1

                sleep_time = retry_after + sleep_time * (0.5 + random())
                if verbose:
                    logger.warning(
                        "Encountered RateLimitError for {} and retrying after {} seconds".format(func,
                                                                                                 sleep_time))
                    logger.warning(
                        "Attempting retry number {} after {} seconds".format(retries, round(sleep_time, 2)))
            if isinstance(e, HTTPError):
                if e.response.status_code == 429:
                    retry_after = float(e.response.headers.get("Retry-After", sleep_time))
                    sleep_time = retry_after + sleep_time * (0.5 + random())
                    if verbose:
                        logger.warning("Attempting retry number {} after {} seconds".format(retries, round(
                            sleep_time, 2)))
            if verbose:
                logger.warning(f"Sleeping now {threading.get_ident()}")
            return sleep_time
        return wrapper

    return decorator


def async_retry_with_exponential_backoff(max_retries: int = 10,
                                         delay_factor: float = 2.0,
                                         max_delay: float = 300.0,
                                         jitter: bool = True,
                                         verbose: bool = True):

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if retries == max_retries:
                        logger.warning("Computation of GPT Evaluation metrics failed with the following "
                                       "exception :\n {}".format(e))
                        raise e

                    sleep_time = _openai_error_handling(e, retries)

                    if verbose:
                        logger.warning("Thread {} sleeping now for {} seconds".format(threading.get_ident(),
                                                                                      sleep_time))

                    # sleeping for sleep_time seconds
                    await asyncio.sleep(sleep_time)

                    if verbose:
                        logger.warning("Thread {} woke up".format(threading.get_ident()))
                    retries += 1

        def _openai_error_handling(e, retries):
            sleep_time = delay_factor ** retries
            if jitter:
                sleep_time = sleep_time * (0.5 + random())  # Add random jitter
            sleep_time = min(sleep_time, max_delay)
            # fail fast without retry for AuthenticationError and APIConnectionError
            if isinstance(e, AuthenticationError) or isinstance(e, APIConnectionError) \
                    or isinstance(e, TypeError):
                logger.warning("Computation of GPT Evaluation metrics for {} failed with the following "
                               "exception :\n {}".format(func, e))
                raise e
            if isinstance(e, RateLimitError):
                retry_after_in_header = None
                retry_after_in_header_response = None
                retry_after = 0

                if hasattr(e, "headers"):
                    retry_after_in_header = e.headers.get("Retry-After", None)
                if hasattr(e, "response") and hasattr(e.response, "headers"):
                    retry_after_in_header_response = e.response.headers.get("Retry-After", None)

                if hasattr(e, "error") and getattr(e.error, "type", None) == "insufficient_quota":
                    logger.warning(
                        "Insufficient quota for computing GPT Evaluation metrics."
                        " Please choose the deployment with higher quota.")
                    raise e
                elif retry_after_in_header is not None:
                    retry_after = float(retry_after_in_header)

                elif retry_after_in_header_response is not None:
                    retry_after = float(retry_after_in_header_response)

                elif "Please retry after" in str(e):
                    retry_after = int(str(e).split('Please retry after ')[1].split(' second')[0]) + 1

                sleep_time = retry_after + sleep_time * (0.5 + random())
                if verbose:
                    logger.warning(
                        "Encountered RateLimitError for {} and retrying after {} seconds".format(func,
                                                                                                 sleep_time))
                    logger.warning(
                        "Attempting retry number {} after {} seconds".format(retries, round(sleep_time, 2)))
            if isinstance(e, HTTPError):
                if e.response.status_code == 429:
                    retry_after = float(e.response.headers.get("Retry-After", sleep_time))
                    sleep_time = retry_after + sleep_time * (0.5 + random())
                    if verbose:
                        logger.warning("Attempting retry number {} after {} seconds".format(retries, round(
                            sleep_time, 2)))

            if verbose:
                logger.warning(
                    "Encountered exception {} for {} and retrying after {} seconds".format(str(e), func,
                                                                                           sleep_time))
                logger.warning(
                    "Attempting retry number {} after {} seconds".format(retries, round(sleep_time, 2)))

            return sleep_time
        return wrapper

    return decorator
